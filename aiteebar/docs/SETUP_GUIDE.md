# Setup Guide

From a clean machine to a running platform. Troubleshooting at the bottom
covers problems actually hit on this codebase, not hypothetical ones.

---

## Requirements

| | Version | Check |
|---|---|---|
| Python | 3.11+ | `python --version` |
| Node.js | 18+ | `node --version` |
| npm | 9+ | `npm --version` |
| Git | any | `git --version` |

Windows, macOS, and Linux all work. Windows commands are given where they
differ.

> **Python 3.13+ users:** use `requirements-dev.txt`, not `requirements.txt`.
> See [Troubleshooting](#pip-install-fails-building-a-wheel).

---

## 1. Clone

```bash
git clone https://github.com/shahamdevops-spec/Aiteebar-AI-Security.git
cd Aiteebar-AI-Security/aiteebar
```

---

## 2. Backend

### Virtual environment (recommended)

```bash
cd backend
python -m venv venv
```

```bash
source venv/bin/activate      # macOS / Linux
venv\Scripts\activate         # Windows
```

### Dependencies

```bash
pip install -r requirements-dev.txt
```

`requirements-dev.txt` is the right choice for local work. It omits
`psycopg2-binary` (only needed for PostgreSQL, and it compiles from source on
newer Pythons) and the docs/linting extras.

If a package tries to compile, force pre-built wheels:

```bash
pip install --only-binary :all: -r requirements-dev.txt
```

### Configuration

The defaults in `app/config.py` run out of the box on SQLite. To customise:

```bash
cp ../.env.example .env
```

Settings you are most likely to touch:

| Variable | Default | Notes |
|---|---|---|
| `DATABASE_URL` | SQLite at `backend/test.db` | Point at PostgreSQL for a real DB |
| `JWT_SECRET_KEY` | a placeholder | **Must be changed for anything shared** |
| `ENVIRONMENT` | `development` | |
| `CORS_ORIGINS` | `http://localhost:3000,http://localhost:3001` | Add your frontend origin |
| `ALERT_AUTO_GENERATE_SEVERITY` | `CRITICAL` | Severity at which events raise alerts |
| `ALERT_WEBHOOK_ENABLED` | `false` | |
| `ALERT_EMAIL_ENABLED` | `false` | |

### Seed data

Tables are created automatically on first start. Populate them:

```bash
python scripts/seed_users.py       # three demo accounts
python scripts/seed_policies.py    # three example policies
python scripts/seed_agents.py      # sample agents and tools (optional)
```

`seed_users.py` is idempotent — re-run it any time to reset the demo accounts.
It only touches those three and leaves other users alone.

### Run

```bash
python -m uvicorn app.main:app --reload
```

Expected output:

```
INFO:     Uvicorn running on http://127.0.0.1:8000
INFO:     Application startup complete.
```

Verify:

```bash
curl http://localhost:8000/health
```

```json
{"status":"healthy","service":"aiteebar-api","components":{"database":"healthy"}}
```

Two `FastAPIDeprecationWarning` lines about `regex` on startup are expected and
harmless.

---

## 3. Frontend

In a second terminal:

```bash
cd frontend
npm install
```

Create `frontend/.env.local`:

```bash
NEXT_PUBLIC_API_URL=http://localhost:8000/api
```

**The `/api` suffix is required.** `lib/api.ts` appends paths like `/policies`
to this value; without it every request 404s.

```bash
npm run dev
```

Open **http://localhost:3000**.

---

## 4. Sign in

| Role | Email | Password | Can |
|---|---|---|---|
| Admin | `admin@aiteebar.ai` | `Demo@123` | Everything, including policy writes |
| Analyst | `analyst@aiteebar.ai` | `Demo@123` | Read, triage alerts |
| Viewer | `viewer@aiteebar.ai` | `Demo@123` | Read only |

The login page has one-click buttons for each. You should land on the
dashboard.

Next: [DEMO_WALKTHROUGH.md](DEMO_WALKTHROUGH.md).

---

## 5. Verify the install

```bash
curl http://localhost:8000/health                      # healthy
curl http://localhost:8000/api/policies                # 3 seeded policies
curl http://localhost:8000/api/events/types            # 8 event types
```

Signed-in check:

```bash
TOKEN=$(curl -s -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@aiteebar.ai","password":"Demo@123"}' | jq -r .access_token)

curl http://localhost:8000/api/v1/dashboard/metrics -H "Authorization: Bearer $TOKEN"
```

All four succeeding means backend, database, seeding, and auth are working.

---

## Windows helper scripts

In the repo root:

| Script | Does |
|---|---|
| `start-fresh.bat` | Kills existing processes, starts backend and frontend, seeds users |
| `start-backend.bat` | Backend only |
| `start-frontend.bat` | Frontend only |
| `close-all.bat` | Force-closes Node, Python, cmd, PowerShell |
| `kill-cmd.bat` | Force-closes stuck cmd windows |
| `control-panel.bat` | Interactive menu for the above |

These use `taskkill /F` and will terminate **every** Node and Python process on
the machine, not only this project's. Do not run them while other work is
open.

---

## PostgreSQL (optional)

```bash
pip install psycopg2-binary
createdb aiteebar
export DATABASE_URL=postgresql://user:pass@localhost:5432/aiteebar
python -m uvicorn app.main:app --reload
```

Tables are created on startup. Re-run the seed scripts against the new
database. Expect stricter enum and foreign-key behaviour than SQLite — see
[DATABASE.md](DATABASE.md#postgresql).

---

## Troubleshooting

### `pip install` fails building a wheel

On Python 3.13+, `psycopg2-binary`, `pydantic-core`, `aiohttp`, and `orjson`
have no pre-built wheels and fall back to compiling, which needs a C toolchain
and can fail outright.

```bash
pip install -r requirements-dev.txt                       # omits psycopg2
pip install --only-binary :all: -r requirements-dev.txt   # never compile
```

### `ModuleNotFoundError: No module named 'app'`

Run uvicorn from `backend/`, not the repo root:

```bash
cd backend && python -m uvicorn app.main:app --reload
```

### Login fails with "Invalid email or password"

Re-seed — it resets the demo accounts in place:

```bash
cd backend && python scripts/seed_users.py
```

If it still fails, the frontend and backend disagree on the password. They must
match:

- `backend/scripts/seed_users.py` → `DEMO_USERS`
- `frontend/lib/constants.ts` → `DEMO_CREDENTIALS`

A silent drift between those two files is exactly what broke login previously.

### Login returns 500

Almost certainly a bcrypt/passlib conflict. This build calls `bcrypt` directly
and passlib should not be installed:

```bash
pip uninstall passlib
pip install "bcrypt>=4.1"
```

### Frontend 404s on `_next/static/*`

A stale or partial Next.js build.

```bash
cd frontend
rm -rf .next        # Windows: rmdir /s /q .next
npm run dev
```

### Frontend starts on port 3001

Port 3000 was already taken and Next.js fell back. Either use 3001, or free
3000:

```bash
npx kill-port 3000              # macOS / Linux
netstat -ano | findstr :3000    # Windows, then: taskkill /F /PID <pid>
```

If you use 3001, add it to `CORS_ORIGINS`.

### Browser shows `net::ERR_FAILED` on an API call

A backend 500 whose CORS headers were stripped. The browser hides the real
error. Check the backend terminal for the traceback — that is where the actual
cause is.

### API returns 422

A required query parameter is missing. Most often `entity_type` on
`/api/risk/summary` and `/api/risk/score`. The response body names the field.

### Port 8000 already in use

```bash
python -m uvicorn app.main:app --reload --port 8001
```

Then update `frontend/.env.local` to match.

### Reset everything

```bash
cd backend
rm test.db                      # Windows: del test.db
python scripts/seed_users.py
python scripts/seed_policies.py
```

Destroys all local data and rebuilds the schema from the models.
