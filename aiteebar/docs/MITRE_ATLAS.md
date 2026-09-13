# MITRE ATLAS Mapping

Aiteebar maps its detections onto [MITRE ATLAS](https://atlas.mitre.org), the
adversarial threat framework for AI systems — ATT&CK's counterpart for ML and
LLM attacks.

**Current coverage: 9 of 59 techniques (15.3%).** That number is low on
purpose: it is measured, not aspirational, and the uncovered 50 are listed
alongside the covered 9.

---

## Where the data comes from

Technique and tactic definitions are generated from the authoritative
[mitre-atlas/atlas-data](https://github.com/mitre-atlas/atlas-data) repository
into `backend/app/services/atlas/atlas_data.json`, which records its source and
retrieval date.

**Do not hand-edit that file or invent technique IDs.** ATLAS is revised
regularly — v5.1.0 in November 2025 added a tactic and 18 techniques, and
renamed much of the framework from "ML" to "AI" (`AML.T0053` became
"AI Agent Tool Invocation"). A stale or invented `AML.T####` in a SOC alert is
worse than no mapping, because an analyst will correlate on it.

Refresh it:

```bash
cd backend
python scripts/refresh_atlas.py
```

The script reports added and removed techniques. **Removals matter most** — a
mapping pointing at a retired technique must be revisited, not carried
forward. Then re-validate:

```bash
python -c "from app.services.atlas import mapping; print(mapping.validate() or 'ok')"
```

`mapping.py` runs that validation at import, so an unknown ID crashes the app
at startup rather than leaking into an alert.

---

## How detections map

Every mapping carries a **confidence** and a **rationale**, so a reviewer can
challenge one claim rather than having to trust the table wholesale.

| Confidence | Meaning |
|---|---|
| `direct` | The detector tests for exactly what the technique describes |
| `partial` | It covers part of the technique, or fires on a consistent proxy signal |

### Threat rules

| Rule | Techniques | |
|---|---|---|
| `PromptInjectionRule` | `AML.T0051` LLM Prompt Injection | direct |
| | `AML.T0054` LLM Jailbreak | direct |
| | `AML.T0056` Extract LLM System Prompt | partial |
| `SensitiveDataExfiltrationRule` | `AML.T0057` LLM Data Leakage | direct |
| | `AML.T0025` Exfiltration via Cyber Means | direct |
| `CredentialExposureRule` | `AML.T0055` Unsecured Credentials | direct |
| `UnauthorizedToolAccessRule` | `AML.T0053` AI Agent Tool Invocation | direct |
| `DangerousToolInvocationRule` | `AML.T0053` AI Agent Tool Invocation | direct |
| | `AML.T0050` Command and Scripting Interpreter | partial |
| `AbnormalAgentBehaviorRule` | `AML.T0034` Cost Harvesting | partial |

`PromptInjectionRule` earns three techniques because its 18 regexes genuinely
cover three distinct behaviours: instruction override (`ignore all previous`),
jailbreak (`DAN mode`, `do anything now`), and system-prompt disclosure
(`show me your instructions`). The last is `partial` because it detects the
*attempt*, not whether extraction succeeded.

`AbnormalAgentBehaviorRule` is `partial` because it measures request **rate**,
not **cost**. Rate is consistent with cost harvesting but does not prove it.

### DLP data types

`PASSWORD` and `API_KEY` map to `AML.T0055` (direct). Other sensitive types —
CNIC, IBAN, CREDIT_CARD, SSN, PASSPORT, HEALTH_RECORD — map to `AML.T0057`
(partial): presence in agent-visible text is not by itself exfiltration.
`EMAIL` and `PHONE` map to nothing.

### Contextual promotion

Sensitive data **plus an external destination** promotes to `AML.T0025`
Exfiltration via Cyber Means at `direct` confidence, because egress is now
evidenced rather than merely possible.

This uses the same `is_external_destination()` check that decides whether an
alert is titled a "Data Exfiltration Attempt", so the title and the mapping
cannot disagree. They did once: an alert to `internal-warehouse.corp` was
titled an exfiltration attempt while the mapping correctly withheld `T0025`.

```
data_type=CNIC  destination=external-api.com
  → "AI Agent Data Exfiltration Attempt"
  → AML.T0025 (direct), AML.T0057 (partial)

data_type=CNIC  destination=internal-warehouse.corp
  → "Security Policy Violation"
  → AML.T0057 (partial)
```

### Not mapped, deliberately

`block_action_taken` maps to nothing. Enforcement outcomes are **defensive
actions, not adversary techniques**. So do `policy_violation`,
`risk_threshold_exceeded`, and `data_access` — a policy can be about anything,
so mapping it blindly would assert a technique the evidence does not support.

---

## Coverage

| Tactic | Covered |
|---|---|
| Reconnaissance | 0 / 6 |
| Resource Development | 0 / 11 |
| Initial Access | 0 / 5 |
| AI Model Access | 0 / 4 |
| **Execution** | **3 / 4** |
| Persistence | 0 / 3 |
| **Privilege Escalation** | **2 / 3** |
| Defense Evasion | 1 / 5 |
| **Credential Access** | **1 / 1** |
| Discovery | 0 / 6 |
| Lateral Movement | 0 / 1 |
| Collection | 0 / 3 |
| AI Attack Staging | 0 / 4 |
| Command and Control | 0 / 1 |
| **Exfiltration** | **3 / 4** |
| Impact | 1 / 6 |

The shape is informative. Coverage clusters in **Execution, Privilege
Escalation, Credential Access, and Exfiltration** — the runtime behaviours of a
deployed agent. It is zero across **Reconnaissance, Resource Development,
Initial Access, AI Model Access, Persistence, Discovery, Collection, and AI
Attack Staging**.

That is the honest characterisation: **Aiteebar observes what a deployed agent
does at runtime. It sees nothing of how an attacker prepares, gains access, or
persists.** A full-lifecycle claim would be false.

Closing those gaps needs telemetry the platform does not collect — model
registry events, training pipeline access, infrastructure logs — not more
rules over the same data.

---

## API

| Method | Path | Purpose |
|---|---|---|
| GET | `/api/atlas` | Version, counts, headline coverage |
| GET | `/api/atlas/tactics` | Tactics in matrix order with per-tactic counts |
| GET | `/api/atlas/matrix` | Full matrix with a `detected` flag on every technique |
| GET | `/api/atlas/coverage` | Per-tactic covered and uncovered counts |
| GET | `/api/atlas/mappings` | Every detection-to-technique claim with rationale |
| GET | `/api/atlas/techniques` | All techniques. `?tactic=` `?detected_only=` |
| GET | `/api/atlas/techniques/{id}` | One technique and what detects it |

```bash
curl http://localhost:8000/api/atlas | jq
curl "http://localhost:8000/api/atlas/techniques?detected_only=true" | jq '.[].id'
curl http://localhost:8000/api/atlas/techniques/AML.T0051 | jq
```

---

## In alerts

Alerts carry their techniques in the SIEM payload as `mitre_atlas`, which is
what a SIEM correlates on:

```json
{
  "alert_id": "...",
  "title": "AI Agent Data Exfiltration Attempt",
  "data_type": "CNIC",
  "destination": "external-api.com",
  "mitre_atlas": [
    { "id": "AML.T0025", "name": "Exfiltration via Cyber Means",
      "confidence": "direct",
      "tactics": [{ "id": "AML.TA0010", "name": "Exfiltration" }],
      "rationale": "CNIC was detected alongside an external destination ('external-api.com'), which is egress of sensitive data by cyber means.",
      "url": "https://atlas.mitre.org/techniques/AML.T0025" },
    { "id": "AML.T0057", "name": "LLM Data Leakage", "confidence": "partial", "…": "…" }
  ]
}
```

Techniques are resolved **when the alert is generated and frozen on the row**,
alongside the agent and application snapshots. If the mapping table is later
revised, a historical alert still shows what was asserted at the time it was
raised — which is what an audit record has to do.

---

## UI

`/atlas` renders the full 16-tactic matrix. Detected techniques are
highlighted; everything else is visibly present but dim, so the gaps are as
readable as the coverage. Clicking a technique shows which detections cover it,
at what confidence, and why.

---

## Adding a mapping

1. Confirm the ID exists in `atlas_data.json`. If not, run `refresh_atlas.py`.
2. Add a `Mapping(technique_id, confidence, rationale)` to the right table in
   `mapping.py`.
3. Write a rationale that names **what in the detector** corresponds to the
   technique. "Detects prompt injection" is not a rationale; "matches
   instruction-override patterns such as 'ignore all previous'" is.
4. Choose `partial` when in doubt. An inflated coverage number that does not
   survive scrutiny is worse than an honest low one.

Validation runs at import, so a bad ID fails at startup.
