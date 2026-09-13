# Developer Guide

How to work on this codebase without repeating mistakes already made here.

Environment setup: [SETUP_GUIDE.md](SETUP_GUIDE.md).
System design: [ARCHITECTURE.md](ARCHITECTURE.md).

---

## Layout

```
backend/app/
├── main.py          app, middleware, exception handlers, router registration
├── config.py        pydantic-settings; every env var is declared here
├── database.py      engine, SessionLocal, get_db
├── models.py        all 14 ORM models and every enum
├── security.py      bcrypt hashing, JWT issue/decode, get_current_user
├── dependencies.py  require_admin / require_analyst helpers
├── routers/         HTTP only
├── schemas/         Pydantic request/response models
└── services/        the engines
```

**The rule that matters: `services/` never imports FastAPI.** Engines take
plain dicts and return plain objects. Routers handle HTTP; services handle
logic. That separation is what lets you test an engine without a server — see
[Testing](#testing).

---

## Adding an endpoint

1. **Schemas** in `schemas/<domain>.py`. Import enums from `app.models` rather
   than redefining them — duplicated enums drift.
2. **Logic** in `services/<domain>/`, framework-free.
3. **Router** in `routers/<domain>.py` — validate, authorise, delegate.
4. **Register** in `main.py`: add to the import and call `include_router`.

### Route ordering will bite you

FastAPI matches in declaration order. A literal path declared after a
parameterised sibling is unreachable:

```python
@router.get("/{policy_id}")     # captures everything
@router.get("/statistics")      # never reached — "statistics" becomes an id
```

Correct:

```python
# Declared before /{policy_id} so the literal path is not captured as an ID.
@router.get("/statistics")
@router.get("/{policy_id}")
```

This has shipped twice. `/api/policies/statistics` 404'd for a whole release.
Leave the comment when you fix one.

### `get_current_user` returns a dict

It decodes the JWT and hands back the **claims**, not a `User` row:

```python
current_user.get("role")    # correct
current_user.get("sub")     # user id
current_user.role           # AttributeError -> 500
current_user.id             # AttributeError -> 500
```

Annotate it `current_user: dict`. Annotating it `User` is what made the mistake
look right. `app/dependencies.py` has `require_admin` / `require_analyst`
helpers that read it correctly — prefer them over inline checks.

### Pydantic models are not dicts

```python
policy_data.condition.get("triggers")   # AttributeError on a BaseModel
policy_data.condition.triggers          # correct
```

And when writing a Pydantic model into a JSON column, dump it first:

```python
condition=policy_data.condition.model_dump()   # correct
condition=policy_data.condition                # not serializable
```

Both forms shipped and 500'd every create and update.

### Response models must match column types

```python
last_assessed: Optional[str]        # column is DateTime -> 422 on every populated row
last_assessed: Optional[datetime]   # correct
```

Pydantic v2 will not coerce `datetime` to `str`. One mismatched field 500s the
whole list endpoint.

---

## Adding a threat rule

Subclass `ThreatRule` in `services/threat_detection/rules.py`:

```python
class MyRule(ThreatRule):
    def evaluate(self, context: Dict[str, Any]) -> RuleResult:
        if not context.get("thing_i_need"):
            return RuleResult(self.rule_name, False, 0.0, "LOW",
                              "Not applicable", {}, datetime.utcnow())
        return RuleResult(self.rule_name, True, 75.0,
                          self._get_risk_severity(75.0),
                          "Explain what fired and why",
                          {"evidence": "..."}, datetime.utcnow())
```

Register it in `ThreatDetectionEngine._initialize_default_rules`.

Two requirements: return `triggered=False` rather than raising when the context
is missing what you need, and make `explanation` a sentence a SOC analyst can
act on. `evidence` must be JSON-serializable — enums need `.value`.

## Adding a DLP pattern

Add to `PATTERNS` in `services/dlp/patterns.py` with a compiled regex,
severity, and base confidence. Add the type to the `DataType` enum in
`app/models.py` too, or persisting a detection will fail.

Anchor patterns tightly. A loose regex produces false positives that feed
policy decisions, and a policy that fires on noise gets switched off.

## Adding a policy operator

Add a branch in `PolicyEngine._evaluate_trigger` and a matching entry in the
frontend's `OPERATORS` array in `app/policies/page.tsx`. **Both** — the UI
offers what it lists, and the backend accepts what it implements. A mismatch is
invisible until a rule silently never matches.

---

## Frontend

### Use the shared API client

```typescript
import { api } from '@/lib/api'
await api.get('/policies')      // baseURL + JWT injection + 401 handling
```

Never call `axios` directly. `lib/api.ts` injects the bearer token and, on a
401, clears it and redirects to `/login`. Raw `axios` bypasses both and sends
unauthenticated requests to a hardcoded host.

### The app is dark-mode only

`app/layout.tsx` hardcodes `className="dark"` on `<html>` with a `bg-slate-900`
body. Building a page with `bg-gray-50` and `text-gray-*` yields white-on-white
text and grey slabs where cards should be. Shared components like `Card` are
dark-only and have no light variant.

### Check component props

`PageHeader` takes `description`, not `subtitle`. React silently drops unknown
props, so a typo here loses content with no error. Read the component before
using it.

---

## Testing

`backend/tests/` contains files for DLP, threats, and risk scoring. **There is
no CI and they are likely stale** — verify before trusting them.

```bash
cd backend
pytest tests/ -v
```

Because services are framework-free, the valuable tests need no HTTP:

```python
from app.services.dlp import DLPDetector

def test_detects_cnic():
    hits = DLPDetector().detect_sensitive_data("CNIC 35201-1234567-1")
    assert any(h.data_type.value == "CNIC" for h in hits)
```

### Verify against a running server before claiming it works

Type checks and unit tests confirm code correctness, not feature correctness.
Three endpoints in this codebase returned 500 while looking entirely fine in
review. Before saying a change works:

```bash
curl -s -o /dev/null -w "%{http_code}\n" http://localhost:8000/api/your-endpoint
```

For UI changes, load the page and use the feature. "It compiles" is not
"it works".

---

## Commits

Describe what changed and why, especially the non-obvious why:

```
fix: repair login, which was broken by two stacked bugs

1. passlib could not initialise. It probes for an old bcrypt bug by hashing
   a deliberately >72-byte secret at import, which bcrypt 4.1+ rejects.

2. The demo credentials never matched between constants.ts and
   seed_users.py, so the demo buttons could not have worked at any point.

Verified: existing hashes still verify, login returns 200, bad password 401.
```

**Do not describe intent as if it were outcome.** A commit here once claimed a
"condition rule builder" that was never written — the button had no `onClick`.
If you did not run it, do not claim it.

---

## Before opening a PR

- [ ] Backend starts clean: `python -m uvicorn app.main:app --reload`
- [ ] Endpoints you touched return expected status codes via curl
- [ ] UI changes loaded in a browser and actually used
- [ ] No new unauthenticated write paths
- [ ] Literal routes declared before parameterised siblings
- [ ] Schema change? Note it — there are no migrations yet
- [ ] `__pycache__` and `test.db` not staged

---

## Gotchas worth knowing

**CORS is stripped from 500s.** The bare-`Exception` handler runs in
`ServerErrorMiddleware`, outside `CORSMiddleware`, so a crash reaches the
browser as an opaque `net::ERR_FAILED` with no message. `main.py` re-attaches
the headers. If you add another top-level handler, do the same — otherwise
browser debugging becomes guesswork.

**SQLite hides bugs.** Foreign keys are not enforced and enum-versus-integer
comparisons return wrong rows instead of raising. `AIApplication.risk_level >= 65`
compared an enum label to a number and silently returned nonsense for months.
Filter numerically on `risk_score`; `risk_level` is a label.

**`.gitignore` misses nested `__pycache__`.** The pattern is
`backend/__pycache__/`, which matches only the top level, so
`backend/app/__pycache__/` is tracked. Check `git status` before `git add .`.

**`Decimal`, not `float`.** `NUMERIC` columns read back as `Decimal`.
`json.dumps` raises on them. Cast with `float()` when building dicts by hand;
Pydantic response models handle it for you.

**Enums need `.value` for JSON.** `DataType.CNIC` is not a string to
`json.dumps`, and `detection.data_type == "CNIC"` is always `False`.
