# Security

Aiteebar is a security product, which sets a higher bar for its own posture
than for an ordinary MVP. This document states honestly where it currently
stands.

**Summary: suitable for local evaluation only.** Do not expose this to a
network you do not control, and do not point it at production data.

---

## Open findings

Ordered by severity. Each is real and reproducible on the current build.

### 1. Most endpoints require no authentication — HIGH

**43 of 54 endpoints accept unauthenticated requests**, including every read
path:

```bash
# no token, all return 200
curl http://localhost:8000/api/policies
curl http://localhost:8000/api/alerts?severity=CRITICAL
curl http://localhost:8000/api/events
curl http://localhost:8000/api/dlp/events
curl http://localhost:8000/api/threats/events
curl http://localhost:8000/api/risk/metrics
```

Anyone who can reach the port can read your entire security posture: which
agents are risky, what sensitive data was detected, which policies exist and
therefore what is *not* covered. For an attacker that is a map of the gaps.

Only writes are protected, and inconsistently — `POST /api/policies` requires
admin, while `POST /api/policies/{id}/test` requires nothing.

**Fix:** apply `Depends(get_current_user)` at the router level, then open
specific routes deliberately.

### 2. `POST /api/dlp/scan` is an unauthenticated data sink — HIGH

Open to anyone, accepts up to 100,000 characters per request, and with an
`agent_id` writes rows to `dlp_events`. Three consequences:

- Unauthenticated storage growth
- CPU burn — ten regex passes over 100 KB, repeatable at will
- An attacker can attribute fabricated DLP detections to any agent they can
  name, poisoning risk scores and triggering false alerts

**Fix:** require auth, rate-limit, and verify the caller may act for that
`agent_id`.

### 3. Default secrets ship in config — HIGH

```python
jwt_secret_key: str = Field(default="change-me-in-production-32-chars-min", ...)
encryption_key: str = Field(default="your-encryption-key-32-chars-long", ...)
```

If `JWT_SECRET_KEY` is unset the app starts anyway with a publicly known
secret, and anyone can forge an admin token:

```python
jwt.encode({"sub": "x", "role": "admin", "exp": ...},
           "change-me-in-production-32-chars-min", algorithm="HS256")
```

**Fix:** refuse to start when `ENVIRONMENT != development` and the secret is
still the default.

### 4. `TrustedHostMiddleware` allows every host — MEDIUM

```python
allowed_hosts=["localhost", "127.0.0.1", "*"]
```

The `*` makes the other two meaningless and disables Host-header validation
entirely.

**Fix:** drive from config; never include `*` outside development.

### 5. DLP events store the data they detected — MEDIUM

`dlp_events.matched_context` holds a window of the original text, so the table
that records "we found a CNIC" **contains the CNIC**. It is unencrypted, has no
retention policy, and is readable through an unauthenticated endpoint (finding
1).

**Fix:** store a redacted or hashed form, encrypt at rest, add retention, and
gate the read path.

### 6. Deleting a policy destroys its audit trail — MEDIUM

`policy_executions.policy_id` is `ON DELETE CASCADE`, so `DELETE
/api/policies/{id}` silently erases every record of decisions that policy made.
An admin can remove the evidence of what was blocked and why — the opposite of
what an audit trail is for.

**Fix:** soft-delete policies, or make the FK `SET NULL` and denormalise the
policy name onto the execution row.

### 7. No rate limiting — MEDIUM

`rate_limit_requests`, `rate_limit_window_seconds`, and `rate_limit_burst`
exist in config and **nothing reads them**. Login is unthrottled, so password
guessing is limited only by bcrypt's cost.

### 8. No token revocation — MEDIUM

Tokens are stateless with a 24-hour lifetime. There is no logout, no
blocklist, no rotation. A leaked token is valid until it expires and cannot be
recalled. `create_refresh_token()` exists but no endpoint calls it.

### 9. Passwords silently truncate at 72 bytes — LOW

bcrypt only considers the first 72 bytes. `security.py` truncates explicitly
rather than raising, so a user with a 100-character passphrase is
authenticated on its first 72 bytes without being told. This matches the
previous passlib behaviour and keeps existing hashes valid, but it is
surprising.

### 10. Demo credentials are in the repository — LOW

`admin@aiteebar.ai` / `Demo@123` appears in `seed_users.py`,
`frontend/lib/constants.ts`, and the docs, and the login page renders
one-click buttons for them. Intentional for a demo; unacceptable anywhere
reachable. The seed script must not run outside development.

### 11. No administrative audit log — LOW

Policy creation, edits, and deletes are not recorded. `policies.created_by`
holds the author, but there is no trail of who changed or removed what.

---

## What is done correctly

Not everything is a gap.

**Password storage.** bcrypt at 12 rounds with per-password salts, called
directly rather than through the unmaintained passlib. Verification failures
return `False` rather than raising, so a malformed stored hash is an auth
failure rather than a 500.

**No user enumeration at login.** Wrong email and wrong password both return
the same 401 with the same message.

**SQL injection.** All queries go through the SQLAlchemy ORM with bound
parameters. No string-built SQL anywhere in the codebase.

**Deterministic DLP.** Detection is regex-based with no model call, so the
same input always yields the same verdict. Nothing in the detection path can be
talked out of its decision by crafted text — which matters for a component that
feeds policy enforcement.

**Alert integrity.** Agent and application state is snapshotted into the alert
row, so a SOC record stays readable after the referenced entities change or are
deleted.

**Secrets are not logged.** The request logger records method, path, client,
and duration — never bodies or headers, so tokens and scanned text stay out of
the logs.

**CORS is a real allowlist.** Explicit origins with credentials enabled, not
`*`. `.env` is gitignored.

---

## Hardening before any shared deployment

Minimum bar, in order:

1. Set `JWT_SECRET_KEY` to 32+ random bytes and make the app refuse to start on
   the default outside development
2. Require authentication by default; open routes case by case
3. Remove `*` from `allowed_hosts`
4. Enforce the rate limits that are already configured
5. Serve over TLS only
6. Delete or disable the demo accounts; block `seed_users.py` outside
   development
7. Move to PostgreSQL with encryption at rest
8. Add retention and redaction for `dlp_events.matched_context`
9. Stop cascading deletes onto `policy_executions`

Items 1-3 are single-line changes. See
[PRODUCTION_ROADMAP.md](PRODUCTION_ROADMAP.md) for sequencing.

---

## Reporting a vulnerability

This is pre-production software with the known gaps above. If you find
something not listed here, open a private security advisory on the repository
rather than a public issue.
