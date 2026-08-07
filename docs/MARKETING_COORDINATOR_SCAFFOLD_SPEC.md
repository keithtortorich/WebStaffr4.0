# Marketing Coordinator — Corrected Scaffold Spec

**Status: plan only, post-MVP gated (same gate as `docs/MARKETING_COORDINATOR_PLAN.md`).**
This is a *corrected* version of the scaffold the Session Standup claimed to have built.
The standup code does not exist in the repo and, as written, would not run and had two
cross-tenant security defects. This spec is grounded in the repo's actual conventions
(verified: `webstaffr/` package, sync `db.get_connection`, `?` placeholders, `tenants`
is identifier-only, tier has no column, `execution_nodes`/`intake_submissions` real schemas,
`SharedSecretVerifier` Protocol + Null + `*_from_env` pattern).

No code in this doc should be written until the MVP gate clears and D4 vendor sign-off lands.

---

## 1. Conventions this spec obeys (verified)

- Package is `webstaffr`, not `netbuild`. Place new module at `webstaffr/workers/marketing_coordinator/`.
- DB is **sync** `conn = get_connection(db_path)` (sqlite3/psycopg2-adapted). `conn.execute(sql, params)`
  with `?` placeholders; `.fetchone()/.fetchall()/.lastrowid`; `.commit()/.close()`. No asyncpg, no `$1`, no `fetchrow`.
- Migrations are numbered SQLite-dialect `.sql` under `webstaffr/migrations/`. Current max is `0014_customer_auth.sql`.
  Next free numbers: **`0015_*`, `0016_*`**. (No `UUID`/`gen_random_uuid()`; use `TEXT`/`INTEGER`.)
- Auth for **server-to-server** endpoints: `SharedSecretVerifier.verify(x_api_key)` via `X-API-Key` header
  (same as `social_media_router` and Leo's `/leo/score`). Auth for **inbound webhooks**: a dedicated
  webhook-secret verifier via `X-Webhook-Secret` (same as Leo's `/webhooks/ghl/lead`).
- `Tenant` is identifier-only. There is **no `tier` column** anywhere. Business Manager gating needs a new source (see §6).
- `execution_nodes` real columns: `node_id, tenant_id, workflow_instance_id, type, status, payload_ref,
  parent_node_id, created_at, completed_at, failure_reason`; PK `(tenant_id, workflow_instance_id, node_id)`.
- `intake_submissions` holds `phone`/`email` (not `tenants`). `submission_id INTEGER PRIMARY KEY AUTOINCREMENT`.
- Attribution reality: no `attributed_jobs` table. Booked jobs = `call_events` where `event_type='appointment_booked'`.
  Revenue is `ESTIMATED_VALUE_PER_APPOINTMENT = 250.0` (estimate, labeled). See `webstaffr/attribution.py`.

---

## 2. Files to create

| File | Purpose |
| :--- | :--- |
| `webstaffr/migrations/0015_comms_queue.sql` | Outbound/inbound message queue (tenant-scoped). |
| `webstaffr/migrations/0016_tenant_entitlements.sql` | Tier source for Business Manager gating. |
| `webstaffr/workers/marketing_coordinator/protocol.py` | `CommsProvider` (send) + `CommsWebhookVerifier` (verify) Protocols, `Null*`, `*NotConfiguredError`. |
| `webstaffr/workers/marketing_coordinator/router.py` | `create_marketing_coordinator_router(...)` factory. Auth-bound endpoints. |
| `webstaffr/workers/marketing_coordinator/attribution.py` | Weekly ROAS report over `call_events`, `unavailable` markers. |
| `webstaffr/intake.py` (edit) | `normalize_phone_e164` field_validator; new GTM fields optional. |
| `webstaffr/app.py` (edit) | `include_router(create_marketing_coordinator_router(...))`. |

---

## 3. Migrations (corrected numbering + dialect)

```sql
-- 0015_comms_queue.sql
CREATE TABLE IF NOT EXISTS comms_queue (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    tenant_id TEXT NOT NULL REFERENCES tenants(tenant_id),
    submission_id INTEGER REFERENCES intake_submissions(submission_id),
    channel TEXT NOT NULL,            -- 'email' | 'sms'
    direction TEXT NOT NULL,           -- 'outbound' | 'inbound'
    to_address TEXT NOT NULL,
    from_address TEXT,
    subject TEXT,
    body TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'queued',  -- queued|sent|delivered|failed|received|triage
    created_at TEXT NOT NULL,
    sent_at TEXT
);
CREATE INDEX IF NOT EXISTS idx_comms_queue_tenant ON comms_queue(tenant_id);
```

```sql
-- 0016_tenant_entitlements.sql  (tier source — does not exist in schema today)
CREATE TABLE IF NOT EXISTS tenant_entitlements (
    tenant_id TEXT PRIMARY KEY REFERENCES tenants(tenant_id),
    tier TEXT NOT NULL DEFAULT 'office_staff',  -- 'office_staff' | 'business_manager'
    updated_at TEXT NOT NULL
);
```

---

## 4. `protocol.py` (split send vs verify, match repo pattern)

```python
from __future__ import annotations
from typing import Optional, Protocol

class CommsNotConfiguredError(Exception):
    pass

class CommsProvider(Protocol):
    def send_outbound(self, tenant_id: str, channel: str, to_address: str,
                      subject: Optional[str], body: str) -> dict: ...

class CommsWebhookVerifier(Protocol):           # mirrors ghl_webhook_verifier_from_env
    def verify(self, provided: Optional[str], raw_body: Optional[bytes] = None) -> bool: ...

class NullComms:
    def send_outbound(self, *a, **k) -> dict:
        raise CommsNotConfiguredError("Comms provider not configured. Message queued.")
```

---

## 5. `router.py` — auth-bound, correct schemas (skeleton)

Factory signature mirrors `create_leo_router`:
`create_marketing_coordinator_router(db_path, comms_client, comms_webhook_verifier, internal_api_verifier)`.

- **Kickoff / status / weekly-report** (server-to-server): gate on `internal_api_verifier.verify(x_api_key)`.
  `tenant_id` arrives in body but is a *trusted internal* caller; every SQL query still filters by `tenant_id` (never-leak).
- **Inbound `/webhooks/comms/re-interview`**: gate on `comms_webhook_verifier.verify(x_webhook_secret)`.
  `tenant_id` is **derived**, never trusted from body (see §7).
- **Tier gate** (`require_business_manager`): `SELECT tier FROM tenant_entitlements WHERE tenant_id=?`;
  raise 403 unless `'business_manager'`. (Not `tenants.tier` — that column does not exist.)

Execution trace insert uses real columns:
```python
conn.execute(
    "INSERT INTO execution_nodes (node_id, tenant_id, workflow_instance_id, type, status, created_at) "
    "VALUES (?, ?, ?, 'kickoff', 'started', ?)",
    (node_id, tenant_id, workflow_instance_id, _now_iso()),
)
```

---

## 6. Tier source decision (open item, D2/D4-adjacent)

No `tier` column exists. This spec adds `tenant_entitlements` (0016). Alternative: extend `tenants`
(against its "identifier only" design) — rejected. Billing/tier definition itself is Phase 4; this spec
only reads the tier for gating. Confirm at build start.

---

## 7. Inbound sender matching (corrected table)

Match against `intake_submissions`, normalizing both sides to E.164:
```python
from_addr_norm = normalize_phone_e164(from_address)  # sms; lowercased email for email
row = conn.execute(
    "SELECT tenant_id, submission_id FROM intake_submissions WHERE tenant_id=? AND (phone=? OR email=?)",
    (tenant_id, from_addr_norm, from_addr_norm),
).fetchone()
```
Unrecognized → insert `comms_queue` row with `status='triage'`, never guessed into a tenant.

---

## 8. `attribution.py` (corrected tables, estimate-labeled)

```python
booked = conn.execute(
    "SELECT COUNT(*) AS n FROM call_events WHERE tenant_id=? AND event_type='appointment_booked' "
    "AND created_at >= ? AND created_at <= ?", (tenant_id, start, end)).fetchone()["n"]
est_revenue = booked * ESTIMATED_VALUE_PER_APPOINTMENT   # labeled estimate, not measured
```
Ad spend comes from SMMM bridge (stubbed). If `ad_spend <= 0`: `roas = "N/A (no ad spend recorded)"`.
Every missing metric returns `"unavailable"`. No invented numbers.

---

## 9. Risk-review closures (from the plan)

- **Dead-pipeline reconciliation**: add `stalled_workflows(tenant_id)` query — `execution_nodes` with
  `status='started'` and `created_at` older than N minutes → returned as a flagged list (no silent hang).
- **AI cost cap**: enforced on the SMMM side (Phase 1), not netbuild.pro. Spec notes it as a hard
  requirement before Phase 1 ships; netbuild.pro only emits the `workflow_instance_id` to trace against.

---

## 10. What this spec deliberately does NOT do

- No live SearXNG research, no SMMM pipeline (Phase 1, SMMM repo).
- No paid-ads APIs (Phase 4).
- No real Twilio/Postmark wiring — only the `Protocol`/`Null*`/`*NotConfiguredError` seam + `NullComms` default.
- No comms sending until D4 vendor sign-off. `NullComms` raises; messages stay queued.

*End of corrected scaffold spec.*
