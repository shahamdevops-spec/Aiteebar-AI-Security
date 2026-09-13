# Database

14 tables. Defined in `backend/app/models.py` via SQLAlchemy 2 declarative
ORM. This document was generated from a live `inspect(engine)` run, so it
matches what the code actually creates.

- **Development:** SQLite at `backend/test.db`
- **Target:** PostgreSQL via `DATABASE_URL`
- **Creation:** `Base.metadata.create_all()` on startup. **No migrations** —
  see [Schema changes](#schema-changes).

---

## Conventions

| | |
|---|---|
| Primary keys | `VARCHAR(36)`, application-generated UUID4 strings, not DB sequences |
| Timestamps | `created_at` / `updated_at`, `DateTime(timezone=True)`, default `func.now()` |
| Scores | `NUMERIC(5,2)`, constrained `0..100`. Read back as `Decimal` — cast to `float` before arithmetic or JSON |
| Enums | `SQLEnum` over Python `str, Enum` classes. Stored as the **name string** |
| Flexible data | `JSON` columns for shapes that vary per row |

> **Decimal trap.** `risk_score` returns `Decimal`, not `float`. `json.dumps`
> will raise on it. Pydantic response models coerce automatically; manual
> dict-building does not.

---

## Relationships

```
users ──< policies ──< policy_executions >── security_events
  │                                              │
  └──< alerts.acknowledged_by                    │
                                                 │
ai_applications ──< ai_agents ──< mcp_tools ─────┤
       │                │            │           │
       │                ├──< agent_activity      │
       │                ├──< dlp_events          │
       │                ├──< threat_detections   │
       │                └──< risk_assessments    │
       │                                         │
       └─────────────< alerts ───────────────────┘

destinations   (standalone, no FKs)
```

Delete behaviour matters:

| Relationship | On delete | Consequence |
|---|---|---|
| `ai_applications` → `ai_agents` | CASCADE | Deleting an app removes its agents |
| `ai_agents` → `mcp_tools`, `agent_activity`, `dlp_events` | CASCADE | Deleting an agent removes its history |
| `ai_agents` → `security_events`, `alerts` | SET NULL | Events and alerts **survive** agent deletion |
| `policies` → `policy_executions` | CASCADE | Deleting a policy destroys its audit trail |
| `users` → `policies` | RESTRICT | A user who authored a policy cannot be deleted |

The SET NULL on `alerts` is why alerts carry `agent_snapshot` and
`application_snapshot` — without them an alert becomes unreadable once its
agent is gone. **The CASCADE on `policy_executions` is a real problem**:
deleting a policy silently erases the record of every decision it ever made.
See [KNOWN_LIMITATIONS.md](KNOWN_LIMITATIONS.md).

---

## Tables

### `users` (9)

| Column | Type | Notes |
|---|---|---|
| `id` | VARCHAR(36) | PK |
| `email` | VARCHAR(255) | NOT NULL, unique, indexed |
| `password_hash` | VARCHAR(255) | NOT NULL. bcrypt `$2b$12$...`, 60 chars |
| `name` | VARCHAR(255) | NOT NULL |
| `role` | enum | `admin` · `analyst` · `viewer` |
| `is_active` | BOOLEAN | Inactive accounts get 403 at login |
| `last_login_at` | DATETIME | Declared but never written |

### `ai_applications` (23)

Catalog of AI applications. Beyond `risk_score` / `risk_level`, six dimension
scores: `privacy_score`, `security_score`, `data_handling_score`,
`enterprise_control_score`, `integration_score`, `permission_score`.

Also `mcp_support`, `api_available`, `data_residency`, `is_demo`,
`last_assessed`, plus `enterprise_controls` and `authentication` as JSON.

> `risk_level` is an enum **label**, `risk_score` is the 0-100 number. Filter
> numerically on `risk_score`. Comparing `risk_level` to an integer does not
> error on SQLite — it silently returns wrong rows. That bug shipped in the
> dashboard.

### `ai_agents` (13)

| Column | Type | Notes |
|---|---|---|
| `application_id` | VARCHAR(36) | NOT NULL → `ai_applications.id` CASCADE |
| `name`, `owner`, `environment` | VARCHAR | |
| `risk_score` / `risk_level` | NUMERIC / enum | |
| `connected_tools` | JSON | Array of tool names |
| `data_access` | JSON | `{"types": ["CNIC", "IBAN"]}` — read by the risk calculator |
| `status` | enum | `active` · `inactive` · `suspended`. **No `critical` member** |

### `mcp_tools` (11)

Tools attached to an agent. `permissions` is a JSON array; `data_sensitivity`
reuses the `RiskLevel` enum and drives tool-permission risk.

### `agent_activity` (10)

Action log. `action_type` is `CONNECT` · `READ` · `WRITE` · `EXECUTE` ·
`EXTERNAL_CALL`; `status` is `pending` · `executed` · `blocked`. Free-form
detail lives in `agent_metadata` (named to avoid SQLAlchemy's reserved
`metadata`).

### `dlp_events` (10)

| Column | Type | Notes |
|---|---|---|
| `agent_id` | VARCHAR(36) | **NOT NULL** → `ai_agents.id` CASCADE |
| `data_type` | enum | CNIC · IBAN · EMAIL · PHONE · API_KEY · PASSWORD · CREDIT_CARD · SSN · PASSPORT · HEALTH_RECORD · OTHER |
| `confidence` | NUMERIC(5,2) | 0-100 |
| `severity` | enum | |
| `matched_context` | TEXT | Surrounding text, truncated to 200 chars |

`agent_id` being NOT NULL is why `POST /api/dlp/scan` only persists when the
caller supplies one.

> `matched_context` stores a window of the original text, so **this table
> holds fragments of the sensitive data it detected**. Treat it as sensitive.

### `security_events` (15)

The spine. `event_type` is a free-form `VARCHAR(100)` validated against
`SecurityEventType` at the API boundary only — writing directly to the DB
bypasses that. `agent_id`, `application_id`, `tool_id` are all nullable
SET NULL.

### `alerts` (22)

| Column | Type | Notes |
|---|---|---|
| `severity`, `title`, `description` | | NOT NULL |
| `agent_snapshot` | JSON | Copy of agent state at generation time |
| `application_snapshot` | JSON | Copy of application state |
| `event_ids` | JSON | Correlated `security_events.id` values |
| `source` | enum | Which subsystem raised it |
| `status` | enum | `open` · `acknowledged` · `resolved` · `false_positive` |
| `delivery_status` | enum | `not_attempted` · `delivered` · `failed` · `disabled` |
| `delivery_error` | TEXT | Populated on failure |

`event_ids` is a JSON array, **not** a join table — you cannot query "which
alerts reference this event" with a normal join. At MVP volume that is fine;
at scale it needs a link table.

### `policies` (10)

`condition` is JSON:

```json
{ "entity_type": "agent", "logic": "AND",
  "triggers": [{ "field": "...", "operator": "...", "value": "..." }] }
```

Schemaless by design — new operators need no migration. The cost is that a
malformed condition is only caught at evaluation time. `priority` is ascending
(lower wins) and indexed with `enabled`.

### `policy_executions` (8)

Audit row per policy match: `action_taken`, `matched_conditions` (JSON),
`reasoning` (TEXT), `executed_at`.

### `threat_detections` (14)

Rule output. `evidence` and `affected_resources` are JSON; `resolved` is a
boolean flag.

### `risk_assessments` (13)

Point-in-time snapshots with `dimensions`, `key_concerns`, and
`recommended_controls` as JSON. A CHECK constraint enforces that the
`entity_type` matches whichever of `application_id` / `agent_id` / `tool_id`
is populated.

### `destinations` (8)

External endpoints with `is_internal` and a risk score. **No foreign keys
anywhere** — nothing references it yet.

### `policy_actions` (6) — orphan

⚠️ Left behind when the `PolicyAction` model was renamed to `PolicyExecution`.
No ORM model maps to it and no code reads or writes it. Superseded by
`policy_executions`. Safe to drop:

```sql
DROP TABLE policy_actions;
```

---

## Indexes

Beyond primary keys and foreign keys:

| Table | Index |
|---|---|
| `ai_applications` | `risk_score DESC` |
| `security_events` | `risk_score DESC`, `created_at DESC` |
| `threat_detections` | `severity DESC`, `risk_score DESC`, `created_at DESC` |
| `alerts` | `(severity, status)`, `timestamp DESC` |
| `policies` | `(enabled DESC, priority ASC)` |
| `policy_executions` | `executed_at DESC` |
| `dlp_events` | `confidence DESC` |

These target the common access patterns: newest-first listing and
severity filtering. The `policies` composite matches the engine's exact query —
enabled rows in ascending priority.

---

## Schema changes

Alembic is in `requirements.txt` and `alembic.ini` exists, but **there are no
migrations**. `create_all()` creates missing tables and does nothing to
existing ones — it will not add a column, change a type, or drop anything.

So today, changing a column means recreating the database:

```bash
# destroys all local data
rm backend/test.db
python backend/scripts/seed_users.py
python backend/scripts/seed_policies.py
```

That is acceptable for local development and unacceptable for anything with
real data. Adopting Alembic is the first item in
[PRODUCTION_ROADMAP.md](PRODUCTION_ROADMAP.md).

---

## Seeding

| Script | Creates |
|---|---|
| `scripts/seed_users.py` | Three demo accounts. **Idempotent** — resets existing demo users in place, leaves others untouched |
| `scripts/seed_policies.py` | Three example policies. Skips by name if present |
| `scripts/seed_agents.py` | Sample agents and tools |

---

## PostgreSQL

Point `DATABASE_URL` at Postgres and restart:

```bash
DATABASE_URL=postgresql://user:pass@localhost:5432/aiteebar
```

The models are portable — `String`, `Numeric`, `Boolean`, `DateTime`, and
SQLAlchemy's generic `JSON` all map cleanly. Expect two behaviour changes:

- **Enum comparisons get stricter.** Postgres will reject comparisons SQLite
  silently allows, which may surface latent bugs of the `risk_level >= 65`
  kind rather than returning wrong rows.
- **Foreign keys are enforced.** SQLite does not enforce them by default
  unless `PRAGMA foreign_keys=ON`. Orphan rows tolerated in dev will fail.

Both changes are improvements, but expect breakage on first switch.
