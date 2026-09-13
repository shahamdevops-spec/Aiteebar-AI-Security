# Demo Walkthrough

A 15-minute guided demo. Every command and screen here has been run against a
live build, and the outputs shown are real.

**Read this first:** there are two "attack" demos.

| | What it is | Use it for |
|---|---|---|
| **Act 5 — Real attack chain** | Genuinely runs DLP, policy evaluation, event logging, alert generation, and SIEM export. Writes real rows | **The demo you want.** Everything shown is the product working |
| **Act 6 — Scripted simulation** | `POST /api/simulation/attack-sequence`. Eleven hardcoded steps with fixed numbers. Calls no engine and writes nothing | A visual narrative only. Do not present it as live detection |

Act 5 is more impressive precisely because it is real.

---

## Before you start

Both servers running ([SETUP_GUIDE.md](SETUP_GUIDE.md)):

```bash
curl http://localhost:8000/health     # {"status":"healthy",...}
curl http://localhost:3000            # HTML
```

Seeded:

```bash
cd backend
python scripts/seed_users.py
python scripts/seed_policies.py
```

Credentials — same password for all three:

| Role | Email | Password |
|---|---|---|
| **Admin** | `admin@aiteebar.ai` | `Demo@123` |
| Analyst | `analyst@aiteebar.ai` | `Demo@123` |
| Viewer | `viewer@aiteebar.ai` | `Demo@123` |

Use **admin** — policy creation needs it.

Keep a terminal beside the browser. Half the story is in the API responses.

---

## Act 1 — Sign in · 1 min

1. Open **http://localhost:3000**
2. Click **Sign In**
3. Under *Demo Credentials*, click the **Admin** card

> 📸 **Capture:** the login screen with the three demo cards.

You land on the dashboard. Talking point: three roles exist and the platform is
role-aware — policy writes are admin-only, which you will see enforced in Act 4.

---

## Act 2 — Dashboard · 2 min

The landing page shows headline counts:

```bash
curl http://localhost:8000/api/v1/dashboard/metrics \
  -H "Authorization: Bearer $TOKEN"
```

```json
{ "total_applications": 46, "total_agents": 8, "mcp_connections": 0,
  "high_risk_applications": 6, "critical_agents": 1,
  "sensitive_data_events": 0, "blocked_actions": 0 }
```

> 📸 **Capture:** the dashboard with metric cards and the sidebar.

**Say:** this is the inventory problem. 46 AI applications, 8 agents, 6 rated
high risk. Most organisations cannot answer "which AI tools are in use and what
can they reach" — that is what this catalogs.

**Note:** `sensitive_data_events` and `blocked_actions` read zero on a fresh
install. They become non-zero during Act 5. Pointing that out up front makes
the change meaningful later.

---

## Act 3 — DLP detection · 3 min

The engine is deterministic regex matching — no model call, so the same input
always produces the same verdict.

Navigate to **DLP Violations**, or run it directly:

```bash
cat > scan.json <<'EOF'
{"text":"Customer record: Ali Ahmed, CNIC 35201-1234567-1, IBAN PK36ABNA0000001234567890, card 4111111111111111, ali@example.com"}
EOF

curl -X POST http://localhost:8000/api/dlp/scan \
  -H "Content-Type: application/json" -d @scan.json
```

```json
{ "success": true, "total_detections": 4,
  "severity_breakdown": { "CRITICAL": 2, "HIGH": 1, "MEDIUM": 1 },
  "data_types_found": ["CNIC", "IBAN", "CREDIT_CARD", "EMAIL"],
  "processing_time_ms": 0.42 }
```

> 📸 **Capture:** the DLP page with detections listed by severity.

**Points worth making:**

- **Sub-millisecond.** Fast enough to sit inline on every agent call.
- **Confidence, not just match.** Each hit is scored; anything under 50 is
  discarded. Text near `CONFIDENTIAL` scores higher, obvious test data like
  `test@` scores lower.
- **`ali@example.com` scores lowest** — the engine recognises example-domain
  addresses and de-rates them. That is the false-positive control, and it is
  why the output is usable as a policy input.

Ad-hoc scans return results without storing anything. Add `"agent_id"` to
attribute and persist them.

---

## Act 4 — Policies · 3 min

Go to **Policies**. Three seeded rules, ascending priority:

| Priority | Action | Rule |
|---|---|---|
| 10 | `BLOCK` | CNIC **and** external destination |
| 50 | `WARN` | Database tool **and** EXECUTE |
| 60 | `REQUIRE_APPROVAL` | API tool **and** external call |

> 📸 **Capture:** the policies list showing all three with colour-coded action
> badges and their conditions.

### Build one live

Click **+ Create Policy**:

- **Name:** `Block Passport Data to Third Parties`
- **Action:** `Block`
- **Conditions** (Match ALL):
  - `data_type` · `equals` · `PASSPORT`
  - click **+ Condition** → `destination` · `contains` · `third-party`
- **Priority:** `15`

Save. It appears in the list, sorted between the 10 and 50 policies.

> 📸 **Capture:** the rule builder with two conditions filled in.

### Prove it works before trusting it

```bash
cat > sample.json <<'EOF'
{"data_type":"CNIC","destination":"external-api.com"}
EOF

curl -X POST http://localhost:8000/api/policies/<POLICY_ID>/test \
  -H "Content-Type: application/json" -d @sample.json
```

```json
{ "matched": true, "action": "BLOCK", "reasoning": "All 2 triggers matched" }
```

Change `destination` to `internal-db` and `matched` flips to `false`.

**Say:** you can test a rule against a hypothetical event before enabling it.
That is the difference between a policy engine and a config file.

### Show enforcement

Sign out, sign in as **Viewer**, and try to create a policy → **403**. The role
model is enforced server-side, not hidden in the UI.

---

## Act 5 — The real attack chain · 4 min

**This is the centrepiece.** A CRITICAL event enters the platform and comes out
the other side as a SIEM-ready alert. Every step is real.

Get an admin token:

```bash
TOKEN=$(curl -s -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@aiteebar.ai","password":"Demo@123"}' | jq -r .access_token)
```

### Step 1 — the agent reads sensitive data

```bash
curl -X POST http://localhost:8000/api/dlp/scan \
  -H "Content-Type: application/json" -d @scan.json
```

CNIC and IBAN detected, CRITICAL.

### Step 2 — that read heads for an external destination

```bash
cat > attack.json <<'EOF'
{
  "event_type": "policy_violation",
  "severity": "CRITICAL",
  "data_type": "CNIC",
  "source": "customer_records",
  "destination": "external-api.com",
  "detection_method": "policy_engine",
  "risk_score": 94,
  "action_taken": "BLOCKED"
}
EOF

curl -X POST http://localhost:8000/api/events \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" -d @attack.json
```

### Step 3 — watch the alert appear in the same response

```json
{ "event": { "id": "45a0a906-...", "severity": "CRITICAL",
             "action_taken": "BLOCKED", "status": "open" },
  "alert_generated": true,
  "alert_id": "89f3d733-dece-457c-844b-11ac5f5a037d" }
```

**`alert_generated: true` is the moment to point at.** The alert was created,
titled, described, and pushed to every enabled delivery channel inside that
one request. Nothing polled, nothing was scheduled.

### Step 4 — prove the threshold is real

Re-run with `"severity": "MEDIUM"`:

```json
{ "alert_generated": false, "alert_id": null }
```

Same event, below threshold, no alert. The platform is not alerting on
everything — it is applying a rule you control
(`ALERT_AUTO_GENERATE_SEVERITY`).

### Step 5 — the SIEM payload

```bash
curl "http://localhost:8000/api/alerts/export?severity=CRITICAL" | jq
```

```json
{ "alert_id": "...", "severity": "CRITICAL",
  "title": "AI Agent Data Exfiltration Attempt",
  "description": "DataBot-v3 triggered a CRITICAL severity event under
                  application 'AcmeGPT' involving CNIC data from
                  customer_records to destination 'external-api.com'.
                  Detected by policy_engine with a risk score of 94/100.
                  Action taken: BLOCKED.",
  "agent":       { "name": "DataBot-v3", "owner": "analytics-team",
                   "environment": "production", "risk_level": "HIGH" },
  "application": { "name": "AcmeGPT", "vendor": "Acme AI" },
  "data_type": "CNIC", "destination": "external-api.com",
  "risk_score": 94.0, "action_taken": "BLOCKED",
  "source": "policy_engine", "events": ["45a0a906-..."] }
```

> 📸 **Capture:** this JSON in the terminal. It is the most convincing artefact
> in the demo.

**Points worth making:**

- **The title was synthesised**, not copied from a field. Data type plus
  external destination on a policy violation is what makes it an
  *exfiltration attempt* rather than a generic event.
- **`agent` and `application` are snapshots**, not live joins. Delete the agent
  and this alert still reads correctly in six months.
- **This is the wire format** — identical for webhook delivery and export, so
  backfill and live streaming share one schema.

### Step 6 — triage

```bash
curl -X PATCH http://localhost:8000/api/alerts/<ALERT_ID>/status \
  -H "Content-Type: application/json" -H "Authorization: Bearer $TOKEN" \
  -d '{"status":"acknowledged"}'
```

`acknowledged_by` and `acknowledged_at` are stamped from the token.

### Step 7 — the dashboard moved

Reload the dashboard. `sensitive_data_events` has increased from the Act 3
scan. The numbers you called out in Act 2 changed because of what you just did.

---

## Act 6 — The scripted simulation · 1 min

⚠️ **Be straight about what this is.** It streams eleven hardcoded steps. It
does not call the DLP, risk, threat, or policy engines and writes nothing to
the database.

```bash
curl -N -X POST http://localhost:8000/api/simulation/attack-sequence \
  -H "Authorization: Bearer $TOKEN"
```

NDJSON, one step per line, ending:

```json
{"step":8,"action":"Action Execution - REQUEST BLOCKED","status":"blocked","risk_score":94.0}
{"step":11,"action":"Simulation Complete - Attack Prevented","risk_score":94.0}
```

Or visit **http://localhost:3000/simulation** and click **Start Attack
Simulation**.

**How to frame it:** "this is the storyboard of the flow — the working version
is what we just did in Act 5." Presenting it as live detection will not survive
the first question about where the data went.

---

## Talk track

| Beat | Point |
|---|---|
| Dashboard | You cannot govern AI tools you cannot see |
| DLP | Deterministic and sub-millisecond — fast enough to sit inline |
| Policies | Rules are testable before they are trusted |
| Real chain | Detection to SIEM-ready alert in one request |
| Threshold | Controlled alerting, not alert spam |
| Snapshots | Alerts stay readable after the world moves on |

---

## Screenshots

Images are not committed to the repository. Capture these six and drop them in
`docs/images/`:

| File | Screen |
|---|---|
| `01-login.png` | Login with the three demo cards |
| `02-dashboard.png` | Dashboard metric cards |
| `03-dlp.png` | DLP detections by severity |
| `04-policies.png` | Policy list with action badges |
| `05-rule-builder.png` | Create form with two conditions |
| `06-siem-payload.png` | Terminal showing the exported alert JSON |

Then reference them at the 📸 markers above:

```markdown
![Dashboard](images/02-dashboard.png)
```

For a GIF of Act 4, [ScreenToGif](https://www.screentogif.com/) (Windows) or
[Kap](https://getkap.co/) (macOS) work well. Keep it under 10 seconds —
opening the form, adding a condition, saving.

---

## If something goes wrong mid-demo

| Symptom | Fix |
|---|---|
| Login fails | `python scripts/seed_users.py` — resets in place |
| No policies listed | `python scripts/seed_policies.py` |
| 401 on a curl | Token expired (24h). Re-run the login command |
| 403 creating a policy | You are signed in as analyst or viewer |
| `alert_generated: false` unexpectedly | Severity is below `ALERT_AUTO_GENERATE_SEVERITY` |
| Blank page / `ERR_FAILED` | Backend 500. The real error is in the backend terminal |

Full list: [SETUP_GUIDE.md](SETUP_GUIDE.md#troubleshooting).
