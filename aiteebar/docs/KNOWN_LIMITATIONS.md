# Known Limitations

What this MVP does not do. Written plainly so nobody discovers it during a
demo or, worse, after relying on it.

Everything here is verified against the current build, not speculative.

---

## Things that look finished but are not

### The attack simulation is scripted

`POST /api/simulation/attack-sequence` streams eleven steps ending in
"BLOCKED — Risk 94/100". It looks like a live pipeline. It is not.

- Risk scores, threat rules, and the blocking policy are **hardcoded literals**
- It does **not** call the DLP, risk, threat, or policy engines
- It writes **nothing** — no `security_events`, no `dlp_events`, no `alerts`
- Nothing else in the platform changes as a result

It calls `DLPDetector` once and discards the result. Treat it as a storyboard.
[DEMO_WALKTHROUGH.md](DEMO_WALKTHROUGH.md) Act 5 gives a real chain that
exercises the engines end to end.

### "Real-time" is polling

No WebSockets, no SSE to the browser. Pages fetch once on mount. The dashboard
updates when you reload it. The only streaming anywhere is the simulation's
NDJSON response.

### The frontend covers a fraction of the API

54 endpoints; the UI reaches a handful. There is **no SOC alert console** —
alerts are fully functional over the API and invisible in the product. Same for
events, SIEM export, and policy execution history.

Pages exist as stubs for agents, MCP tools, events, graph, settings, and risk —
several render placeholder content.

### React Query is installed and unused

`@tanstack/react-query` is in `package.json`. Every page uses bare `useEffect` +
`axios`. No caching, no deduplication, no background refetch.

---

## Detection

### DLP is regex-only

Deterministic and fast, which is the right trade for a policy input. But:

- **Format-bound.** A CNIC written `35201 1234567 1` instead of
  `35201-1234567-1` is missed
- **No semantics.** "the customer's national ID is on file" is invisible
- **No images, PDFs, or attachments** — text only
- **No custom patterns.** Adding a data type means editing `patterns.py`
- **Confidence weights are hand-tuned**, not calibrated against a labelled
  corpus. Treat the numbers as ordinal, not probabilities

### Threat rules need context nobody supplies

The six rules work — but only against a fully populated `context` dict.
Nothing in the platform assembles that automatically from live agent activity.
Today you must construct it yourself and call `/api/threats/detect`.

`SensitiveDataExfiltrationRule` needs correlated DLP events and network
connections with timestamps inside a five-minute window. There is no collector
producing them.

### Risk scoring is uncalibrated

Weights (25/25/20/15/10/5) are reasonable but arbitrary — no empirical basis.
The bands (80+ CRITICAL, 60+ HIGH) are equally arbitrary. Scores are useful for
**ranking** entities against each other, not as absolute measures. "Agent A is
riskier than Agent B" is supported; "Agent A is 78% risky" is not.

### Policy evaluation is first-match-wins

Evaluation stops at the **first** matching policy by ascending priority. A
`WARN` at priority 10 shadows a `BLOCK` at priority 20 — the stricter rule never
runs. There is no conflict detection and nothing warns you when you create an
overlapping policy.

### Nothing enforces policies automatically

The engine evaluates and records. **No enforcement point exists.** Nothing sits
between an agent and a tool to actually block a call. `action_taken: "BLOCKED"`
means a caller asserted it, not that the platform prevented anything.

This is the single biggest gap between the product's story and what it does.

---

## Data and operations

### No migrations

Alembic is installed and configured; there are zero migrations.
`create_all()` adds missing tables and will not alter an existing one. Changing
a column means deleting the database. Fine locally, unacceptable with real
data.

### `policy_actions` is an orphan table

Left behind by a model rename. Nothing maps to it. Superseded by
`policy_executions`. Safe to `DROP`.

### Deleting a policy destroys its audit trail

`ON DELETE CASCADE` on `policy_executions.policy_id`. Removing a policy erases
every record of what it blocked and why.

### Alert-to-event links are not queryable

`alerts.event_ids` is a JSON array. You can go alert → events, but "which
alerts reference this event" needs a scan. A link table is required at scale.

### SQLite hides bugs PostgreSQL would catch

Foreign keys are not enforced by default, and enum-versus-integer comparisons
silently return wrong rows instead of raising. A `risk_level >= 65` bug lived
in the dashboard for exactly this reason. Expect breakage on first switch to
Postgres — it is the schema getting stricter, not regressing.

### No retention or archival

Events, alerts, DLP detections, and threat detections accumulate forever. The
DLP table stores fragments of the sensitive data it detected, unencrypted, with
no expiry.

---

## Security

Detailed in [SECURITY.md](SECURITY.md). The headline items:

- **43 of 54 endpoints need no authentication**, including every read path
- **`POST /api/dlp/scan` is an open, unauthenticated data sink** that accepts
  100 KB per request and can attribute fabricated detections to any agent
- **Default JWT secret ships in config** — the app starts without complaint and
  admin tokens can be forged
- **`allowed_hosts` contains `*`**, disabling Host validation
- **Rate limiting is configured and unimplemented**
- **No token revocation** — a leaked token is valid for 24 hours

None is hard to fix. All are currently open.

---

## Scale

Untested beyond demo volumes. Known ceilings:

| Area | Limit |
|---|---|
| DLP | Ten regex passes per scan, single-threaded, 100 KB cap |
| Threat history | In-memory list capped at 10,000, **lost on restart** |
| Policy evaluation | Loads every enabled policy per call, no cache |
| Listings | Offset pagination — degrades on large tables |
| Alert export | Capped at 5,000; no cursor for a full backfill |
| Concurrency | Single uvicorn worker by default |

`ThreatDetectionEngine.threat_history` living in process memory means threat
summaries reset every restart and are wrong across multiple workers.

---

## Quality

- **Tests do not run.** `backend/tests/` has files for DLP, threats, and risk
  scoring, but there is no CI and they were not part of any change verified
  here. Assume they are stale.
- **No CI/CD.** No automated build, test, lint, or deploy.
- **Inconsistent auth style.** Some routers use `get_current_user` inline,
  others import helpers from `app/dependencies.py`.
- **Two API versioning schemes.** Auth and dashboard are `/api/v1/...`;
  everything else is `/api/...`.
- **A doubled path segment.** Resolve is
  `/api/threats/threats/{id}/resolve` — router prefix plus route both say
  `threats`. Left alone to avoid breaking callers.
- **Deprecation warnings on startup.** `applications.py` uses FastAPI's
  removed-in-future `regex=` instead of `pattern=`.

---

## Honest positioning

**Good for:** demonstrating the concept, validating the data model, exercising
detection logic against sample data, as a base to build on.

**Not ready for:** production traffic, real customer data, compliance evidence,
anything internet-reachable, or any claim that it prevents exfiltration — it
observes and records, it does not intercept.

Sequenced plan to close these: [PRODUCTION_ROADMAP.md](PRODUCTION_ROADMAP.md).
