# Architecture

How Aiteebar is put together, and why.

---

## Shape

Three tiers, no message broker, no cache. Everything is synchronous request/response.

```
┌──────────────────────────────────────────────────────────────┐
│  Next.js 14 (App Router)          localhost:3000             │
│  lib/api.ts  ── axios client, injects JWT from localStorage  │
└───────────────────────────┬──────────────────────────────────┘
                            │ HTTP + JSON
┌───────────────────────────▼──────────────────────────────────┐
│  FastAPI                          localhost:8000             │
│                                                              │
│  middleware   request logging → trusted host → CORS          │
│  routers/     HTTP only: validate, authorise, delegate       │
│  services/    the engines. No FastAPI imports.               │
│  models.py    SQLAlchemy ORM                                 │
└───────────────────────────┬──────────────────────────────────┘
                            │
                    SQLite (dev) / PostgreSQL (target)
```

The rule that matters: **`services/` never imports FastAPI**. Engines take
plain dicts and return plain objects, so they can be unit-tested and called
from a script without an HTTP server. Routers own HTTP concerns; services own
logic.

---

## The engines

### DLP — `services/dlp/`

`patterns.py` holds compiled regexes for ten data types, each with a severity
and a base confidence. `detector.py` walks them, skips overlapping matches,
and scores each hit.

Confidence starts at the pattern's base and is adjusted by context: longer
matches score higher, text near `CONFIDENTIAL` / `SECRET` / `RESTRICTED` gains
10 points, and obvious test data (`test@`, `example@`) loses 20. Anything below
50 is discarded. Results sort CRITICAL-first.

Detection is **deterministic**. No model call, so the same input always yields
the same output — which is what makes it usable as a policy input.

### Threat detection — `services/threat_detection/`

Six rules, each a class with `evaluate(context) -> RuleResult`. The engine runs
all six and collects those that fired, sorted by severity.

| Rule | Fires when |
|---|---|
| `SensitiveDataExfiltrationRule` | A DLP hit and an external connection within a 5-minute window |
| `UnauthorizedToolAccessRule` | A tool is called that is not in the agent's allowed list |
| `AbnormalAgentBehaviorRule` | Request-rate spike, >3 data types in <30s, or a suspicious tool sequence |
| `CredentialExposureRule` | DLP detects PASSWORD, API_KEY, or AWS_SECRET |
| `PromptInjectionRule` | Input matches any of 18 injection patterns |
| `DangerousToolInvocationRule` | A destructive operation is invoked |

Rules are independent — one throwing does not stop the others. Adding a rule is
subclassing `ThreatRule` and appending it.

### Risk scoring — `services/risk/`

`calculator.py` computes each factor; `engine.py` weights and combines them.

| Factor | Weight |
|---|---|
| Application risk | 25% |
| Data sensitivity | 25% |
| Agent privilege | 20% |
| Tool permissions | 15% |
| Destination risk | 10% |
| Behaviour anomaly | 5% |

Weights sum to exactly 1.0. Every factor returns its value, its weight, its
weighted contribution, and a sentence explaining itself, so a score can always
be decomposed into why. That explainability is the point — an unexplainable
risk number is not actionable.

### Policy — `services/policies/`

A policy is a JSON condition plus an action. Conditions hold triggers
(`field`, `operator`, `value`) combined with AND or OR. Eight operators:
`equals`, `contains`, `starts_with`, `ends_with`, `in`, `greater_than`,
`less_than`, `regex`.

Evaluation walks enabled policies **in ascending priority order and stops at
the first match** — first-match-wins, not most-severe-wins. A policy at
priority 10 shadows one at 50 even if the second is stricter. Every match is
written to `policy_executions` with the reasoning.

### Alerting — `services/alerting/`

`generator.py` turns a security event into an alert when severity meets the
threshold (`ALERT_AUTO_GENERATE_SEVERITY`, default CRITICAL). `notifier.py`
delivers over webhook and email.

Two decisions worth calling out:

- **Entity state is snapshotted into the alert row.** `agent_id` and
  `application_id` are `ON DELETE SET NULL`, so without a copy an alert becomes
  unreadable once the agent is deleted. A SOC record read months later must
  still make sense.
- **Delivery never raises.** A collector outage must not lose the alert. Both
  channels record their own outcome and the alert is stored regardless.

### Simulation — `services/simulation/`

⚠️ Scripted narrative, not a real pipeline. It streams eleven fixed steps and
does not invoke the engines above or write any rows. See
[KNOWN_LIMITATIONS.md](KNOWN_LIMITATIONS.md).

---

## Request path

A CRITICAL event posted to `/api/events`:

```
POST /api/events
  ↓ HTTPBearer dependency → decode JWT → claims dict
  ↓ Pydantic validates SecurityEventCreate
  ↓ router checks agent_id / application_id exist → 404 if not
  ↓ INSERT security_events
  ↓ AlertGenerator.generate_from_event
       severity >= threshold?  no → return, no alert
                               yes ↓
       load agent + application, snapshot them
       synthesise title and description
       INSERT alerts
  ↓ AlertNotifier.dispatch → webhook, email (both off by default)
  ↓ 201 { event, alert_generated, alert_id }
```

---

## Authentication

JWT bearer tokens, HS256, 24-hour expiry. `get_current_user` decodes the token
and **returns the claims as a plain dict** — `sub`, `email`, `role` — not a
`User` row. It does not hit the database.

```python
current_user.get("role")   # correct
current_user.role          # AttributeError
```

That distinction has caused real 500s in this codebase. `app/dependencies.py`
provides `require_admin` / `require_analyst` helpers that read it correctly.

Passwords use bcrypt directly at 12 rounds. passlib was removed: version 1.7.4
probes for an old bcrypt bug by hashing a deliberately >72-byte secret at
import, which bcrypt 4.1+ rejects, breaking every hash and verify.

---

## Middleware order

Registered innermost-first, so execution is outside-in:

```
ServerErrorMiddleware   ← holds the bare-Exception handler
  request logging
    TrustedHost
      CORS
        routes
```

`ServerErrorMiddleware` sits **outside** CORS, so a 500 would reach the browser
without CORS headers and surface as an opaque `net::ERR_FAILED` rather than the
error body. `main.py`'s exception handler therefore re-attaches the CORS
headers itself. Without that, every backend crash looks like a network failure
in the UI.

---

## Route ordering

FastAPI matches in declaration order, so literal paths must precede
parameterised siblings:

```python
@router.get("/statistics")      # must come first
@router.get("/{policy_id}")     # otherwise this captures "statistics"
```

This has bitten `/api/policies/statistics` and `/api/alerts/export`. Both are
now ordered correctly and carry a comment saying why.

---

## Frontend

Next.js App Router. Pages are client components (`'use client'`) that fetch on
mount — no SSR data loading, no React Query despite it being installed.

All requests go through `lib/api.ts`, which injects the bearer token and, on a
401, clears the token and redirects to `/login`. **Using raw `axios` bypasses
both** and produces requests with no credentials.

The app is dark-mode only: `app/layout.tsx` hardcodes `className="dark"` on
`<html>` with a `bg-slate-900` body. Pages that assume a light background
render unreadably.

---

## Deliberate omissions

| Not present | Why |
|---|---|
| Message queue | Every operation is fast and synchronous at this scale |
| Cache | No measured hot path yet |
| Migrations | Alembic is installed but unused; `create_all` at startup |
| WebSockets | "Real-time" is client polling |
| Rate limiting | Config keys exist; nothing enforces them |
| Refresh tokens | `create_refresh_token` exists with no endpoint |

Several are prerequisites for production. See
[PRODUCTION_ROADMAP.md](PRODUCTION_ROADMAP.md).
