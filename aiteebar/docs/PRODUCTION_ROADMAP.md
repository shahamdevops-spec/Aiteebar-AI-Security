# Production Roadmap

Sequenced path from MVP to production. Ordered by dependency and risk, not by
appeal — the unglamorous items come first because everything else sits on them.

Effort is rough: **S** ≈ days, **M** ≈ 1-2 weeks, **L** ≈ a month or more.

---

## Phase 0 — Stop the bleeding · ~1 week

Cheap changes that remove the sharpest edges. Do these before showing the
platform to anyone outside the team.

| # | Item | Effort |
|---|---|---|
| 0.1 | **Refuse to start on a default secret.** Validate `JWT_SECRET_KEY` at startup and exit when `ENVIRONMENT != development` and it is unchanged | S |
| 0.2 | **Authenticate by default.** Apply `Depends(get_current_user)` at router level, then open specific routes deliberately. Closes 43 open endpoints | S |
| 0.3 | **Remove `*` from `allowed_hosts`** and drive it from config | S |
| 0.4 | **Rate-limit login and `/api/dlp/scan`.** The config keys already exist | S |
| 0.5 | **Adopt Alembic.** Baseline the current schema, then never edit a table by hand again. Blocks every later phase | M |
| 0.6 | **Drop the orphan `policy_actions` table** in that first migration | S |
| 0.7 | **Stop cascading deletes onto `policy_executions`.** Soft-delete policies instead | S |

**Exit criteria:** no unauthenticated write path, no default secret accepted,
schema changes are versioned.

---

## Phase 1 — Make it trustworthy · ~3 weeks

Nothing above Phase 1 is safe to build on until the tests and the database are
real.

| # | Item | Effort |
|---|---|---|
| 1.1 | **Get the test suite running in CI.** Files exist under `backend/tests/` and are stale. Fix them, add coverage for auth, policy evaluation, and alert generation, wire to GitHub Actions on every PR | M |
| 1.2 | **Move to PostgreSQL.** Expect breakage — Postgres enforces foreign keys and rejects the enum-versus-integer comparisons SQLite tolerates. That is the point | M |
| 1.3 | **Structured logging.** `python-json-logger` is installed and unused. Add request IDs that survive across services | S |
| 1.4 | **Health checks that mean something.** `/health` should verify the DB can be written to, not just connected to | S |
| 1.5 | **Error tracking.** Sentry or equivalent. The CORS-stripped-500 problem made browser errors invisible; catch them server-side | S |
| 1.6 | **Retention and redaction for `dlp_events.matched_context`.** It currently stores plaintext fragments of detected sensitive data forever | M |

**Exit criteria:** CI green on every PR, running on Postgres, errors visible
without reading a terminal.

---

## Phase 2 — Close the product gap · ~6 weeks

The two things that make the story true rather than aspirational.

### 2.1 — An enforcement point · L

**The most important item on this roadmap.** Today the policy engine evaluates
and records; nothing sits between an agent and a tool to stop a call.
`action_taken: "BLOCKED"` is an assertion by the caller, not something the
platform did.

Options, cheapest first:

1. **SDK/middleware** the agent runtime calls before each tool invocation.
   Easy, but relies on cooperation
2. **Proxy** in front of the MCP transport. Enforces without cooperation, adds
   a network hop and a failure mode
3. **Sidecar** per agent. Strongest isolation, heaviest to operate

Whichever is chosen, decide the fail mode explicitly: **fail-closed** (deny on
outage — safe, can halt the business) or **fail-open** (allow on outage — never
blocks work, useless exactly when it is attacked). That decision belongs to
whoever owns the risk, not to engineering.

### 2.2 — Real activity ingestion · L

The threat rules work but need a `context` dict nobody builds. Requires an
agent-activity collector producing correlated DLP events and network
connections with timestamps. Without it,
`SensitiveDataExfiltrationRule` can never fire from live data.

### 2.3 — Rebuild the simulation on real engines · M

Replace the hardcoded narrative with one that actually calls DLP, risk, threat
detection, and policy, and writes real rows. Same endpoint, same output shape —
but the numbers become computed and the dashboard moves afterwards. Also serves
as a live integration test of the whole chain.

### 2.4 — SOC alert console · M

Alerts are fully functional over the API and invisible in the product. Needs a
queue view, severity and status filters, a detail pane, and triage actions. The
API is done; this is frontend only.

---

## Phase 3 — Operate at scale · ~4 weeks

| # | Item | Effort |
|---|---|---|
| 3.1 | **Move threat history out of process memory.** `ThreatDetectionEngine.threat_history` is a capped in-memory list — lost on restart, wrong across workers | M |
| 3.2 | **Cursor pagination.** Offset pagination degrades badly; alert export caps at 5,000 with no way to backfill fully | S |
| 3.3 | **Link table for alert↔event.** `alerts.event_ids` as JSON cannot answer "which alerts reference this event" without a scan | S |
| 3.4 | **Async delivery.** Webhook and email are inline in the request. A slow collector currently slows event ingestion | M |
| 3.5 | **Cache policy evaluation.** Every call loads all enabled policies | S |
| 3.6 | **Multi-worker deployment** behind a real ASGI setup, once 3.1 makes it safe | S |

---

## Phase 4 — Enterprise readiness · ~8 weeks

| # | Item | Effort |
|---|---|---|
| 4.1 | **SSO** — SAML/OIDC. Local accounts do not survive procurement | L |
| 4.2 | **Multi-tenancy** — tenant isolation at the data layer. Retrofitting this later is painful, so decide early whether you need it | L |
| 4.3 | **Administrative audit log** — who changed which policy, when, from where | M |
| 4.4 | **Token revocation** — logout, refresh rotation, a blocklist. `create_refresh_token()` already exists with no endpoint | M |
| 4.5 | **Granular RBAC** — three hardcoded roles will not survive contact with a real org chart | M |
| 4.6 | **Native SIEM integrations** — Splunk HEC, Sentinel, Chronicle. The generic webhook covers most cases; named integrations sell | M |
| 4.7 | **Compliance mapping** — SOC 2 / ISO 27001 evidence generation | L |

---

## Explicitly not planned

Worth stating so nobody assumes them.

| Not doing | Why |
|---|---|
| **ML-based DLP** | Determinism is the feature. A policy input that gives different answers on the same text is not enforceable. Revisit only as an additive signal, never replacing regex |
| **Agent behaviour prediction** | No training data, and a false positive that suspends a production agent is more expensive than a miss |
| **Auto-remediation** | Do not build automatic response before the enforcement point (2.1) is proven and trusted |
| **Mobile app** | A SOC console is a desktop tool |

---

## Sequencing

```
Phase 0  ████                          secrets, auth, migrations
Phase 1      ████████                  CI, Postgres, observability
Phase 2          ████████████████      enforcement, ingestion, console
Phase 3                  ████████      scale
Phase 4                      ████████████  enterprise
```

Phases 0 and 1 are strictly sequential — everything depends on migrations and a
working test suite. Phase 2's three tracks can run in parallel with separate
owners. Phase 4 is demand-driven; do not start it before a customer asks.

---

## If you only do three things

1. **Phase 0.2** — authenticate by default. One change closes 43 open endpoints
2. **Phase 0.5** — Alembic. Without it every later schema change is a data-loss
   event
3. **Phase 2.1** — an enforcement point. Until it exists, this is a monitoring
   tool that describes itself as a prevention tool, and that gap will be found
   by a customer rather than by you
