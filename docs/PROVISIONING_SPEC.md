# Customer Provisioning — Admin-Only Path (Design Note)

**Status:** Spec for Codex implementation  
**Date:** 2026-08-04  
**Depth:** D3 — no precedent, new surface  
**Owner:** Claude (spec). Codex builds and owns the resulting script/tooling.  
**Blocks:** Screen 14 (owner dashboard) — see `docs/ONBOARDING_SPEC.md`  
**Related:** `webstaffr/customer_auth.py`, `webstaffr/migrations/0014_customer_auth.sql` / `postgres_manual/0016_customer_auth.sql`

---

## Problem

`customer_auth.py`'s `start_session()` reads `customer_users` and `authorize()` reads
`tenant_memberships` — both tables exist (merged commit `a8bffe6`) but nothing in the
codebase writes to them outside tests. A real Supabase-authenticated user hits
`start_session()` today and gets 403 (`user is None`), unconditionally, forever —
there is no path from "business owner signs up" to "business owner can see their
dashboard."

## Scope for this pass

**Admin-only. No self-serve signup, no public API route, no email-invite automation.**
Ops manually invites via the Supabase Dashboard; this spec covers only the step after
that — linking a real Supabase Auth user to a tenant with a role.

Building a self-serve invite flow (owner invites their own dispatcher from inside the
dashboard) is real future work, but it depends on Screen 14 existing first, which
depends on this. Not in scope here — flagged as out of scope explicitly so it's not
half-built.

## Design

**A CLI script, not an HTTP endpoint.** No new authenticated route, no new auth model
to secure it, no attack surface added to the public API. Whoever runs it already has
shell access to production — the same trust boundary as running a migration by hand.

```
python scripts/provision_customer.py \
  --tenant-id <tenant_id> \
  --supabase-user-id <uuid, from Supabase Dashboard after inviting the user> \
  --role owner|manager|dispatcher|viewer
```

**Steps the script performs, in order:**

1. Validate `tenant_id` exists in `tenants` (reuse `Tenant` validation from `tenant.py`,
   same as every other tenant-scoped write in this codebase — don't invent a second
   validation path).
2. Validate `--supabase-user-id` is a well-formed UUID. The script does not call the
   Supabase Admin API to verify the user actually exists — ops is expected to have just
   created them via the Dashboard. (First failure mode: `authorize()` will 403 on a
   nonexistent user just like it does today. Cheap to detect, not worth the extra
   Admin API dependency for an admin-only script.)
3. `INSERT INTO customer_users (user_id, status) VALUES (?, 'active') ON CONFLICT DO
   NOTHING` — idempotent, safe to re-run if the same person is added to a second
   tenant later.
4. `INSERT INTO tenant_memberships (tenant_id, user_id, role, status, created_by)
   VALUES (?, ?, ?, 'active', NULL)`. `created_by` is `NULL` — see note below, don't
   invent a value for it.
5. Print a confirmation line with tenant_id, user_id, role. No silent success.

**Idempotency:** re-running with the same tenant_id + user_id + role should not error.
Use `ON CONFLICT (tenant_id, user_id) DO UPDATE SET role = excluded.role, status =
'active'` on the membership insert, so the same script also serves as "reactivate a
suspended membership" or "change someone's role" without a second tool.

## `created_by` — deliberately left NULL

`tenant_memberships.created_by REFERENCES customer_users(user_id)` — it's a foreign
key into the same table, meaning it can only point at another *customer*, not at
whichever ops person ran the script (ops staff don't have `customer_users` rows; they
aren't customers). Two options considered:

- Add a free-text `provisioned_by` column for an ops identifier — schema change, more
  scope than this pass needs.
- Leave `created_by` NULL for admin-provisioned rows, matching the schema's existing
  nullable FK, and rely on shell/deploy logs for who-did-it audit trail.

Going with the second. If ops-attribution on membership rows becomes a real
requirement later, that's a schema change + its own spec, not a workaround bolted
onto this script.

## What this does NOT do

- No self-serve signup UI or route.
- No email invite automation (Supabase Admin API `inviteUserByEmail` or equivalent) —
  ops uses the Dashboard directly for that step.
- No bulk import / CSV provisioning — one tenant-user-role triple per invocation.
- No role change history — `tenant_memberships.updated_at` shows *when* it last
  changed, not what it changed from. Acceptable for an admin-only tool; revisit if
  this becomes customer-facing.
- Does not touch `customer_sessions` or `customer_audit_events` — those are populated
  by `customer_auth.py` at actual login/authorize time, not at provisioning time.

## Verification (Codex should confirm before calling this done)

- Script run twice with identical args does not error and does not create a duplicate
  `tenant_memberships` row (composite PK `(tenant_id, user_id)` already enforces this
  at the DB level — confirm the `ON CONFLICT` clause matches).
- Script run with a `--tenant-id` that fails `Tenant` validation exits non-zero with a
  clear message, does not partially insert.
- After running the script, a real `POST /auth/session` + `GET /tenants/{tenant_id}/metrics`
  round-trip with that user's Supabase-issued Bearer token succeeds (this is the actual
  acceptance test — the unit-level DB inserts are necessary but not sufficient).

## Also in this handoff: CORS wildcard comment

Separate from provisioning, but bundled into the same Codex pass per the founder's
sequencing: `webstaffr/app.py:92`'s `_CORS_SCOPED_PREFIXES` wildcards
`Access-Control-Allow-Origin: *` on `/tenants/*`. Safe today because auth is
Bearer-token, not cookie-based — add a comment at that line pinning the assumption
("wildcard is safe only because these routes use Authorization header, not cookies —
revisit this if session handling ever moves to cookies") so nobody removes the
constraint unknowingly later.

---

**Document owner:** Claude  
**Next review:** After Codex implements — Claude verifies the acceptance test above
before this is marked resolved in TASKS.md.
