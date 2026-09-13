# Aiteebar AI Security

A security platform for AI agents. It inventories the AI applications in use,
watches what their agents do, detects sensitive data leaving the organisation,
scores risk, enforces policy, and raises SOC alerts.

**Status: MVP.** It runs end to end and every feature described here has been
exercised against a live server. It is not production software — see
[KNOWN_LIMITATIONS.md](docs/KNOWN_LIMITATIONS.md) before you rely on it.

---

## What it does

| Capability | What it actually does |
|---|---|
| **Application catalog** | Inventory of AI applications with six-dimension risk scoring |
| **DLP engine** | Regex detection of 10 sensitive data types with confidence scoring. Deterministic — no LLM in the detection path |
| **Threat detection** | Six rules over agent activity: exfiltration, unauthorised tool use, abnormal behaviour, credential exposure, prompt injection, dangerous tool invocation |
| **Risk scoring** | Seven weighted factors producing an explainable 0-100 score with per-factor contributions |
| **Policy engine** | Conditional rules with AND/OR logic and eight operators, resolving to ALLOW / WARN / REQUIRE_APPROVAL / BLOCK |
| **SOC alerting** | SIEM-shaped alerts auto-generated from CRITICAL events, with webhook and email delivery |

---

## Quick start

Prerequisites: **Python 3.11+**, **Node.js 18+**.

```bash
# 1. Backend
cd backend
pip install -r requirements-dev.txt
python scripts/seed_users.py
python scripts/seed_policies.py
python -m uvicorn app.main:app --reload
```

```bash
# 2. Frontend, in a second terminal
cd frontend
npm install
npm run dev
```

Open **http://localhost:3000** and sign in with a demo account.

| Role | Email | Password |
|---|---|---|
| Admin | `admin@aiteebar.ai` | `Demo@123` |
| Analyst | `analyst@aiteebar.ai` | `Demo@123` |
| Viewer | `viewer@aiteebar.ai` | `Demo@123` |

> These are seeded demo accounts for local use. They are not suitable for any
> shared or internet-reachable deployment.

Interactive API docs: **http://localhost:8000/docs**

Full instructions, including troubleshooting, are in
[SETUP_GUIDE.md](docs/SETUP_GUIDE.md).

---

## Documentation

| Document | Read it when |
|---|---|
| [SETUP_GUIDE.md](docs/SETUP_GUIDE.md) | Installing from scratch |
| [DEMO_WALKTHROUGH.md](docs/DEMO_WALKTHROUGH.md) | Demonstrating the platform |
| [ARCHITECTURE.md](docs/ARCHITECTURE.md) | Understanding how it fits together |
| [API.md](docs/API.md) | Looking up an endpoint |
| [API_EXAMPLES.md](docs/API_EXAMPLES.md) | You want a copy-pasteable request |
| [DATABASE.md](docs/DATABASE.md) | Working with the schema |
| [SECURITY.md](docs/SECURITY.md) | Assessing it for deployment |
| [KNOWN_LIMITATIONS.md](docs/KNOWN_LIMITATIONS.md) | **Before trusting any output** |
| [PRODUCTION_ROADMAP.md](docs/PRODUCTION_ROADMAP.md) | Planning the path to production |
| [DEVELOPER_GUIDE.md](docs/DEVELOPER_GUIDE.md) | Contributing code |

Component deep-dives: [DLP_ENGINE.md](docs/DLP_ENGINE.md) ·
[THREAT_DETECTION.md](docs/THREAT_DETECTION.md) ·
[RISK_SCORING.md](docs/RISK_SCORING.md)

---

## Layout

```
aiteebar/
├── backend/
│   ├── app/
│   │   ├── main.py          FastAPI app, middleware, router registration
│   │   ├── models.py        SQLAlchemy ORM, 14 tables
│   │   ├── security.py      bcrypt hashing, JWT issue and decode
│   │   ├── routers/         HTTP layer, one module per domain
│   │   ├── schemas/         Pydantic request and response models
│   │   └── services/        Engines: dlp, threat_detection, risk, policies,
│   │                        alerting, simulation
│   └── scripts/             seed_users, seed_policies, seed_agents
└── frontend/
    ├── app/                 Next.js App Router pages
    ├── components/          Shared UI
    └── lib/                 API client, auth helpers, constants
```

## Stack

Backend: FastAPI · SQLAlchemy 2 · Pydantic v2 · SQLite (dev) / PostgreSQL (target) · python-jose · bcrypt
Frontend: Next.js 14 · React 18 · TypeScript · Tailwind · axios

---

## Two things to know up front

1. **Most endpoints are unauthenticated.** 43 of 54 require no token, including
   every read path and `POST /api/dlp/scan`. See
   [SECURITY.md](docs/SECURITY.md).
2. **The attack simulation is scripted.** `POST /api/simulation/attack-sequence`
   replays a fixed narrative; it does not run the detection engines and writes
   nothing to the database. See
   [KNOWN_LIMITATIONS.md](docs/KNOWN_LIMITATIONS.md).
