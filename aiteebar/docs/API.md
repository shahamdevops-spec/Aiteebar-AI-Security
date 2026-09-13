# API Reference

Base URL: `http://localhost:8000`
Interactive docs: `/docs` (Swagger) · `/redoc`

54 endpoints. **11 require a bearer token; the other 43 do not.** The `Auth`
column below is authoritative — it was generated from the live OpenAPI schema,
not written by hand. That so many read paths are open is a real gap, covered in
[SECURITY.md](SECURITY.md).

Copy-pasteable requests for every endpoint: [API_EXAMPLES.md](API_EXAMPLES.md).

---

## Conventions

**Authentication.** Send `Authorization: Bearer <token>` from
`POST /api/v1/auth/login`. Tokens are HS256 and expire after 24 hours. A
missing or bad token returns **401**, not 403.

**Errors.** Failures return:

```json
{ "error": { "code": "INTERNAL_SERVER_ERROR", "message": "...", "status": 500,
             "timestamp": "2026-09-13T12:00:00+00:00" } }
```

Pydantic validation failures return **422** with a `details` array naming the
offending fields.

| Status | Meaning |
|---|---|
| 200 / 201 / 204 | Success |
| 401 | Missing, malformed, or expired token |
| 403 | Authenticated but insufficient role (admin-only routes) |
| 404 | No such resource |
| 422 | Request body or query failed validation |
| 500 | Unhandled server error |

**Enums.**

| Enum | Values |
|---|---|
| Severity | `INFO` `LOW` `MEDIUM` `HIGH` `CRITICAL` |
| Risk level | `LOW` `MEDIUM` `HIGH` `CRITICAL` |
| Policy action | `ALLOW` `WARN` `REQUIRE_APPROVAL` `BLOCK` |
| Action taken | `ALLOWED` `WARNED` `APPROVAL_REQUIRED` `BLOCKED` |
| Detection method | `policy_engine` `dlp` `threat_detection` `manual` `other` |
| Alert status | `open` `acknowledged` `resolved` `false_positive` |
| Event type | `agent_tool_connection` `data_access` `dlp_detection` `risk_threshold_exceeded` `policy_violation` `external_communication` `threat_detected` `block_action_taken` |

---

## Authentication — `/api/v1/auth`

| Method | Path | Auth | Purpose |
|---|---|---|---|
| POST | `/register` | — | Create an account. Always assigned the `viewer` role |
| POST | `/login` | — | Exchange credentials for a JWT |
| GET | `/me` | ✅ | Current user from the token |

`POST /login` returns `{ access_token, token_type, user: {...} }`. Wrong
credentials give 401; an inactive account gives 403.

---

## Security events — `/api/events`

| Method | Path | Auth | Purpose |
|---|---|---|---|
| POST | `` | ✅ | Log an event. **Auto-generates an alert at or above the severity threshold** |
| GET | `` | — | List events. `event_type` `severity` `agent_id` `days` `skip` `limit` |
| GET | `/types` | — | The event-type vocabulary |
| GET | `/{event_id}` | — | One event |

`POST` returns `{ event, alert_generated, alert_id }`. When `alert_generated`
is true, alert creation and delivery already happened in that same request.
A non-existent `agent_id` or `application_id` returns 404.

---

## SOC alerts — `/api/alerts`

| Method | Path | Auth | Purpose |
|---|---|---|---|
| POST | `` | ✅ | Raise an alert directly |
| GET | `` | — | List. `severity` `status` `agent_id` `days` `skip` `limit` |
| GET | `/export` | — | Batch SIEM JSON. `severity` `status` `days` `limit` |
| GET | `/{alert_id}` | — | One alert, full record |
| GET | `/{alert_id}/siem` | — | One alert in SIEM shape |
| PATCH | `/{alert_id}/status` | ✅ | Acknowledge / resolve / mark false positive |
| POST | `/{alert_id}/deliver` | ✅ | Re-send after a collector outage |

The SIEM payload is the canonical wire format — identical for webhook delivery,
`/export`, and `/{id}/siem`:

```json
{
  "alert_id": "32d758a0-b614-4546-b451-2c82d5ec8bc0",
  "timestamp": "2026-09-13T11:55:16",
  "severity": "CRITICAL",
  "title": "AI Agent Data Exfiltration Attempt",
  "description": "DataBot-v3 triggered a CRITICAL severity event ...",
  "agent":       { "id": "...", "name": "DataBot-v3", "owner": "analytics-team",
                   "environment": "production", "status": "active",
                   "risk_score": 78.0, "risk_level": "HIGH",
                   "connected_tools": ["CustomerDatabase", "HTTPClient"] },
  "application": { "id": "...", "name": "AcmeGPT", "vendor": "Acme AI",
                   "category": "assistant", "risk_score": 65.0,
                   "risk_level": "HIGH" },
  "data_type": "CNIC",
  "destination": "external-api.com",
  "risk_score": 94.0,
  "action_taken": "BLOCKED",
  "source": "policy_engine",
  "events": ["45a0a906-...", "7c2c5a31-..."]
}
```

`agent` and `application` are snapshots taken when the alert was generated, not
live joins — they stay populated after the underlying rows change or are
deleted.

---

## Policies — `/api/policies`

| Method | Path | Auth | Purpose |
|---|---|---|---|
| POST | `` | ✅ admin | Create |
| GET | `` | — | List, ascending priority. `enabled_only` `skip` `limit` |
| GET | `/statistics` | — | Counts and executions by action |
| GET | `/{policy_id}` | — | One policy |
| PUT | `/{policy_id}` | ✅ admin | Update. All fields optional |
| DELETE | `/{policy_id}` | ✅ admin | Delete. Returns 204 |
| GET | `/{policy_id}/executions` | — | Audit trail for this policy |
| POST | `/{policy_id}/test` | — | Evaluate against a sample event without saving |

Write operations require the **admin** role; an analyst or viewer token gets
403.

Condition shape:

```json
{
  "entity_type": "agent",
  "logic": "AND",
  "triggers": [
    { "field": "data_type",   "operator": "equals",   "value": "CNIC" },
    { "field": "destination", "operator": "contains", "value": "external" }
  ]
}
```

Operators: `equals` `contains` `starts_with` `ends_with` `in` `greater_than`
`less_than` `regex`. `in` takes a comma-separated `value`. All string
comparisons are case-insensitive.

Evaluation is **first-match-wins by ascending priority** — a lower-priority
number wins even if a higher number carries a stricter action.

`/test` is the cheap way to validate a rule before enabling it:

```json
{ "policy_id": "...", "matched": true, "action": "BLOCK",
  "reasoning": "All 2 triggers matched" }
```

---

## DLP — `/api/dlp`

| Method | Path | Auth | Purpose |
|---|---|---|---|
| POST | `/scan` | — | Scan text for sensitive data |
| POST | `/scan-agent/{agent_id}` | — | Scan attributed to an agent |
| GET | `/events` | — | Detections. `limit` `offset` `agent_id` `severity` `data_type` `days` |
| GET | `/report` | — | Aggregate report. `days` `agent_id` |

`POST /scan` takes `{ text, source?, scan_id?, agent_id? }`. **Supplying
`agent_id` persists the detections as DLP events; omitting it returns results
without writing anything.** `DLPEvent.agent_id` is NOT NULL, so an unattributed
scan cannot be stored.

Detected types: `CNIC` `IBAN` `EMAIL` `PHONE` `API_KEY` `PASSWORD`
`CREDIT_CARD` `SSN` `PASSPORT` `HEALTH_RECORD`. Matches scoring below 50
confidence are discarded.

⚠️ This endpoint is unauthenticated and accepts up to 100,000 characters.

---

## Threats — `/api/threats`

| Method | Path | Auth | Purpose |
|---|---|---|---|
| POST | `/detect` | — | Run all six rules. Query params `agent_id` `user_input` |
| GET | `/events` | — | Detections. `limit` `offset` `agent_id` `severity` `threat_type` `days` |
| GET | `/summary` | — | Counts and trend. `days` |
| GET | `/agent/{agent_id}/score` | — | Aggregate threat score for one agent |
| POST | `/threats/{threat_id}/resolve` | — | Mark resolved |

⚠️ The resolve path really is `/api/threats/threats/{id}/resolve` — the router
prefix and the route both contain `threats`. Left as-is to avoid breaking
callers; noted in [KNOWN_LIMITATIONS.md](KNOWN_LIMITATIONS.md).

---

## Risk — `/api/risk`

| Method | Path | Auth | Purpose |
|---|---|---|---|
| GET | `/score` | — | Multi-factor score. **`entity_type` and `entity_id` required** |
| GET | `/summary` | — | Aggregate. **`entity_type` required**; `days` |
| GET | `/metrics` | — | Counts by level across applications |
| GET | `/compare` | — | Compare two entities |
| GET | `/recommendations/{entity_id}` | — | Suggested controls. `entity_type` |
| GET | `/applications/{application_id}` | — | Six-dimension assessment |
| GET | `/by-level/{risk_level}` | — | Applications at one level. `limit` |

`/score` and `/summary` return **422** without their required query
parameters — a bare `GET /api/risk/summary` will fail.

---

## Applications — `/api/applications`

| Method | Path | Auth | Purpose |
|---|---|---|---|
| GET | `` | — | Catalog. `category` `risk_level` `search` `sort_by` `sort_order` `limit` `offset` |
| GET | `/categories` | — | Categories with counts |
| GET | `/search` | — | Search. `q` `limit` |
| GET | `/{application_id}` | — | One application |

`sort_by` accepts `name` or `risk_score`; `sort_order` accepts `asc` or `desc`.

---

## Dashboard — `/api/v1/dashboard`

All require a token.

| Method | Path | Purpose |
|---|---|---|
| GET | `/metrics` | Headline counts |
| GET | `/risk-distribution` | Applications banded by risk score |
| GET | `/top-risky-applications` | `limit` |
| GET | `/top-risky-agents` | `limit` |
| GET | `/recent-events` | `limit` |
| GET | `/recent-activity` | `limit` |
| GET | `/application-categories` | Category breakdown |

---

## Simulation — `/api/simulation`

| Method | Path | Auth | Purpose |
|---|---|---|---|
| POST | `/attack-sequence` | ✅ | Stream a scripted attack narrative (NDJSON) |
| GET | `/scenarios` | ✅ | Available scenarios |

⚠️ **Scripted, not real.** The eleven steps and their risk scores are
hardcoded. It does not call the DLP, risk, threat, or policy engines, and
writes nothing to the database — so nothing else in the platform changes as a
result. Treat it as a presentation aid.

---

## MITRE ATLAS — `/api/atlas`

| Method | Path | Auth | Purpose |
|---|---|---|---|
| GET | `` | — | Version, counts, headline coverage |
| GET | `/tactics` | — | Tactics in matrix order with per-tactic counts |
| GET | `/matrix` | — | Full matrix with a `detected` flag on every technique |
| GET | `/coverage` | — | Per-tactic covered and uncovered counts |
| GET | `/mappings` | — | Every detection-to-technique claim, with rationale |
| GET | `/techniques` | — | All techniques. `tactic` `detected_only` |
| GET | `/techniques/{id}` | — | One technique and what detects it. 404 on unknown id |

Alerts carry their techniques as `mitre_atlas` in the SIEM payload. Full
detail, including the coverage breakdown and how to refresh the reference
data: [MITRE_ATLAS.md](MITRE_ATLAS.md).

---

## Health

| Method | Path | Purpose |
|---|---|---|
| GET | `/health` | Service and database status. 503 when the DB is unreachable |
| GET | `/health/db` | Database connectivity only |
| GET | `/` | Service metadata and doc links |
