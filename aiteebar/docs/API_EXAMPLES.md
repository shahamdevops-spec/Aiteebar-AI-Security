# API Examples

Copy-pasteable requests. **Every example here was executed against a running
server and returned the status shown.** If one fails for you, the server state
differs — it is not a typo in the doc.

- Base URL: `http://localhost:8000`
- Reference: [API.md](API.md)

> **Windows note.** `curl.exe` on Windows does not accept single-quoted JSON.
> Every example below uses `-d @file.json`, which works identically in bash,
> PowerShell, and cmd. Inline-quoted variants are given for bash only.

---

## 1. Get a token

```bash
cat > login.json <<'EOF'
{"email":"admin@aiteebar.ai","password":"Demo@123"}
EOF

curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d @login.json
```

→ **200**

```json
{ "access_token": "eyJhbGciOiJIUzI1NiIs...", "token_type": "bearer",
  "user": { "id": "e9f79629-...", "email": "admin@aiteebar.ai", "role": "admin" } }
```

Keep it in a variable:

```bash
# bash
TOKEN=$(curl -s -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" -d @login.json | jq -r .access_token)
```

```powershell
# PowerShell
$r = Invoke-RestMethod -Uri http://localhost:8000/api/v1/auth/login -Method POST `
     -ContentType application/json -Body '{"email":"admin@aiteebar.ai","password":"Demo@123"}'
$TOKEN = $r.access_token
```

Verify it:

```bash
curl http://localhost:8000/api/v1/auth/me -H "Authorization: Bearer $TOKEN"   # 200
curl http://localhost:8000/api/v1/auth/me                                     # 401
```

---

## 2. DLP

### Ad-hoc scan — returns results, writes nothing

```bash
cat > dlp.json <<'EOF'
{"text":"Customer CNIC 35201-1234567-1 and IBAN PK36ABNA0000001234567890"}
EOF

curl -X POST http://localhost:8000/api/dlp/scan \
  -H "Content-Type: application/json" -d @dlp.json
```

→ **200**

```json
{ "success": true, "scan_id": "scan_1789301234567", "text_length": 63,
  "total_detections": 2,
  "severity_breakdown": { "CRITICAL": 1, "HIGH": 1 },
  "data_types_found": ["CNIC", "IBAN"],
  "detections": [
    { "data_type": "CNIC", "confidence": 95.0, "severity": "CRITICAL",
      "matched_content": "35201-1234567-1", "position": 14 }
  ],
  "processing_time_ms": 0.42 }
```

### Attributed scan — persists DLP events

Add `agent_id`. Without it nothing is stored, because `dlp_events.agent_id` is
NOT NULL.

```bash
cat > dlp_agent.json <<'EOF'
{"agent_id":"<AGENT_UUID>","source":"customer_export",
 "text":"Customer CNIC 35201-1234567-1 and IBAN PK36ABNA0000001234567890"}
EOF

curl -X POST http://localhost:8000/api/dlp/scan \
  -H "Content-Type: application/json" -d @dlp_agent.json     # 200
```

Then read them back:

```bash
curl "http://localhost:8000/api/dlp/events?limit=5"          # 200
curl "http://localhost:8000/api/dlp/report?days=7"           # 200
```

---

## 3. Policies

### List and inspect

```bash
curl http://localhost:8000/api/policies                      # 200
curl http://localhost:8000/api/policies/statistics           # 200
```

→ statistics

```json
{ "total_policies": 3, "enabled_policies": 3, "total_executions": 0,
  "executions_by_action": { "ALLOW": 0, "WARN": 0, "REQUIRE_APPROVAL": 0, "BLOCK": 0 } }
```

### Create (admin only)

```bash
cat > policy.json <<'EOF'
{
  "name": "Block Confidential Data Exfiltration",
  "description": "CNIC must not leave for an external destination",
  "condition": {
    "entity_type": "agent",
    "logic": "AND",
    "triggers": [
      { "field": "data_type",   "operator": "equals",   "value": "CNIC" },
      { "field": "destination", "operator": "contains", "value": "external" }
    ]
  },
  "action": "BLOCK",
  "priority": 20,
  "enabled": true
}
EOF

curl -X POST http://localhost:8000/api/policies \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d @policy.json
```

→ **201**. Without the token → **401**. With a non-admin token → **403**.

### Test a rule before trusting it

```bash
cat > sample.json <<'EOF'
{"data_type":"CNIC","destination":"external-api.com"}
EOF

curl -X POST http://localhost:8000/api/policies/<POLICY_ID>/test \
  -H "Content-Type: application/json" -d @sample.json
```

→ **200**

```json
{ "policy_id": "...", "matched": true, "action": "BLOCK",
  "reasoning": "All 2 triggers matched" }
```

Change `destination` to `internal-db` and `matched` becomes `false` — the
cheapest way to confirm a rule does what you think.

### Update and delete

```bash
cat > bump.json <<'EOF'
{"priority":15}
EOF

curl -X PUT http://localhost:8000/api/policies/<POLICY_ID> \
  -H "Content-Type: application/json" -H "Authorization: Bearer $TOKEN" \
  -d @bump.json                                              # 200

curl -X DELETE http://localhost:8000/api/policies/<POLICY_ID> \
  -H "Authorization: Bearer $TOKEN"                          # 204

curl "http://localhost:8000/api/policies/<POLICY_ID>/executions"   # 200
```

---

## 4. Events and alerting

### Log a CRITICAL event — this auto-generates an alert

```bash
cat > event.json <<'EOF'
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
  -H "Authorization: Bearer $TOKEN" -d @event.json
```

→ **201**

```json
{ "event": { "id": "45a0a906-...", "event_type": "policy_violation",
             "severity": "CRITICAL", "risk_score": 94.0,
             "action_taken": "BLOCKED", "status": "open" },
  "alert_generated": true,
  "alert_id": "89f3d733-dece-457c-844b-11ac5f5a037d" }
```

Send the same body with `"severity": "MEDIUM"` and `alert_generated` is
`false` — below the threshold, no alert. That threshold is
`ALERT_AUTO_GENERATE_SEVERITY`.

Add `agent_id` and `application_id` to tie the alert to a real agent; the
snapshot fields then populate. A non-existent id returns **404**.

### Read alerts

```bash
curl "http://localhost:8000/api/alerts?severity=CRITICAL"    # 200
curl "http://localhost:8000/api/alerts?status=open&days=7"   # 200
curl http://localhost:8000/api/events/types                  # 200
```

### SIEM export

```bash
curl "http://localhost:8000/api/alerts/export?severity=CRITICAL"     # 200
curl "http://localhost:8000/api/alerts/<ALERT_ID>/siem"              # 200
```

→ export

```json
{ "exported_at": "2026-09-13T12:30:00", "count": 1,
  "alerts": [ { "alert_id": "...", "severity": "CRITICAL",
                "title": "AI Agent Data Exfiltration Attempt",
                "data_type": "CNIC", "destination": "external-api.com",
                "risk_score": 94.0, "action_taken": "BLOCKED",
                "source": "policy_engine", "events": ["..."] } ] }
```

Ship to a collector:

```bash
curl -s "http://localhost:8000/api/alerts/export?severity=CRITICAL" \
  | jq -c '.alerts[]' \
  | while read -r a; do
      curl -s -X POST "$SIEM_URL" -H "Content-Type: application/json" -d "$a"
    done
```

### Triage

```bash
cat > ack.json <<'EOF'
{"status":"acknowledged"}
EOF

curl -X PATCH http://localhost:8000/api/alerts/<ALERT_ID>/status \
  -H "Content-Type: application/json" -H "Authorization: Bearer $TOKEN" \
  -d @ack.json                                               # 200
```

`status` accepts `open`, `acknowledged`, `resolved`, `false_positive`. Anything
other than `open` stamps `acknowledged_by` and `acknowledged_at`.

### Re-deliver after a collector outage

```bash
curl -X POST http://localhost:8000/api/alerts/<ALERT_ID>/deliver \
  -H "Authorization: Bearer $TOKEN"                          # 200
```

→ `{ "alert_id": "...", "results": { "webhook": "disabled", "email": "disabled" } }`

`disabled` is expected until you set `ALERT_WEBHOOK_ENABLED` or
`ALERT_EMAIL_ENABLED`.

### Raise an alert directly

```bash
cat > alert.json <<'EOF'
{"severity":"HIGH","title":"Manual Alert","description":"Raised by an analyst",
 "risk_score":70,"action_taken":"WARNED","source":"manual","event_ids":[]}
EOF

curl -X POST http://localhost:8000/api/alerts \
  -H "Content-Type: application/json" -H "Authorization: Bearer $TOKEN" \
  -d @alert.json                                             # 201
```

---

## 5. Threats

```bash
curl -X POST "http://localhost:8000/api/threats/detect?agent_id=<AGENT_UUID>&user_input=ignore%20all%20previous%20instructions"   # 200
curl "http://localhost:8000/api/threats/summary?days=7"      # 200
curl "http://localhost:8000/api/threats/events?limit=5"      # 200
curl "http://localhost:8000/api/threats/agent/<AGENT_UUID>/score"   # 200
```

`/detect` takes `agent_id` and `user_input` as **query parameters**, not a JSON
body.

---

## 6. Risk

```bash
curl http://localhost:8000/api/risk/metrics                          # 200
curl "http://localhost:8000/api/risk/summary?entity_type=agent"      # 200
curl "http://localhost:8000/api/risk/score?entity_type=agent&entity_id=<UUID>"  # 200
curl "http://localhost:8000/api/risk/by-level/CRITICAL?limit=10"     # 200
curl "http://localhost:8000/api/risk/applications/<APP_ID>"          # 200
```

⚠️ `entity_type` is **required** on `/summary` and `/score`. Omitting it
returns **422**, not a default:

```bash
curl http://localhost:8000/api/risk/summary                          # 422
```

---

## 7. Applications

```bash
curl "http://localhost:8000/api/applications?limit=5"                    # 200
curl "http://localhost:8000/api/applications?sort_by=risk_score&sort_order=desc&limit=10"  # 200
curl "http://localhost:8000/api/applications?risk_level=HIGH"            # 200
curl "http://localhost:8000/api/applications/search?q=chat&limit=5"      # 200
curl http://localhost:8000/api/applications/categories                   # 200
```

---

## 8. Dashboard (token required)

```bash
curl http://localhost:8000/api/v1/dashboard/metrics -H "Authorization: Bearer $TOKEN"
```

→ **200**

```json
{ "total_applications": 46, "total_agents": 8, "mcp_connections": 0,
  "high_risk_applications": 6, "critical_agents": 1,
  "sensitive_data_events": 0, "blocked_actions": 0 }
```

```bash
curl http://localhost:8000/api/v1/dashboard/risk-distribution -H "Authorization: Bearer $TOKEN"
```

→ `{ "low": 0, "medium": 14, "high": 32, "critical": 0 }`

---

## 9. Health

```bash
curl http://localhost:8000/health          # 200, or 503 if the DB is down
curl http://localhost:8000/health/db       # 200
```

---

## Postman

Import `http://localhost:8000/openapi.json` — File → Import → Link. That
generates a collection from the live schema, so it never drifts from the code.

Then:
1. Collection → Variables → add `baseUrl` = `http://localhost:8000`
2. Collection → Authorization → Bearer Token → `{{token}}`
3. On the login request, Scripts → Post-response:

```javascript
pm.collectionVariables.set("token", pm.response.json().access_token);
```

Run login once; every authenticated request then works.

---

## Troubleshooting

| Symptom | Cause |
|---|---|
| **401** on a write | No token, or expired (24h lifetime). Log in again |
| **403** on a policy write | Token is valid but the role is not `admin` |
| **422** with `field required` | A required query parameter is missing — usually `entity_type` |
| **404** posting an event | `agent_id` or `application_id` does not exist |
| `net::ERR_FAILED` in a browser | A 500 whose CORS headers were stripped. Check the server log for the real error |
| Curl rejects your JSON | Windows `curl.exe` will not take single-quoted bodies. Use `-d @file.json` |
