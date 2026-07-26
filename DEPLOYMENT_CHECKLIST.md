# Deployment Checklist

**Owner:** Founder (approval gate before any push to production)

**Status:** CUT OVER COMPLETE (2026-07-26; independently verified 2026-07-27). Vercel project
`web-staffr3-3` builds from `WebStaffr4.0@681870d`; both Postgres migrations applied with RLS
verified; live smoke test passed. **Correction to the env-var assumption below:** the six
application credentials (`GROK_API_KEY`, `GHL_API_KEY`, `GHL_LOCATION_ID`,
`RETELL_WEBHOOK_SECRET`, `GHL_WEBHOOK_SECRET`, `BOOK_API_KEY`) were never actually set on this
Vercel project -- only `DATABASE_URL` was. Setting them is the remaining pre-MVP step; see
`TASKS.md`.

---

## Repository Readiness

- [x] **Tests passing**: 169/169 tests passing in a fresh, isolated Python 3.12 venv.
- [x] **Health check**: 8/8 checks HEALTHY (imports, migrations produce expected tables,
      app boots and serves a full chat/book/webhook round trip, intake round-trip with
      tenant isolation, site-data never leaks internal fields, CORS scoped correctly,
      rate limit trips, Angel prompt loads).
- [x] **Tenant isolation verified**: every query scoped by `tenant_id`; auth on `/book`,
      `/webhooks/ghl`, `/retell/*`, `/integrations/*`, `/workflow-graph/*`.
- [x] **Database migrations**: `0001-0007` (SQLite) apply cleanly; the two dropped-engine
      tables confirmed absent from a fresh schema.
- [x] **Angel worker**: code-complete, unit-tested.
- [x] **GHL integration**: implemented (create/update/cancel appointments, retries, error logging).
- [x] **Retell voice wiring**: code-complete, unit-tested, webhook signature verification implemented.
- [x] **Env var reference**: documented (`CREDENTIALS.md`).
- [x] **Git hygiene**: no secrets committed.
- [ ] **Secrets manager configured**: Vercel project not yet re-pointed at this repo (see below).

---

## Cutover Steps (this repo is a rebuild of WS3.3, already live at web-staffr3-3.vercel.app)

**This is a re-point, not a first launch.** The existing Vercel project and its env vars
(`GROK_API_KEY`, `GHL_API_KEY`, `GHL_LOCATION_ID`, `RETELL_WEBHOOK_SECRET`,
`GHL_WEBHOOK_SECRET`, `BOOK_API_KEY`, `DATABASE_URL`) already exist and stay with the Vercel
project through a repo swap -- they do not need to be re-entered.

1. **[Founder, production DB change]** Apply the two new Postgres migrations to the live
   Supabase project, in order:
   - `webstaffr/migrations/postgres_manual/0007_social_media.sql`
   - `webstaffr/migrations/postgres_manual/0008_execution_nodes.sql`

   Via the Supabase SQL editor, the Supabase CLI, or the Supabase MCP's `apply_migration`.
   **Must happen before step 3** -- without this, `/integrations/*` and `/workflow-graph/*`
   500 against the live Postgres backend, and the two tables would exist with no RLS if
   created implicitly some other way.

2. **[Founder]** Verify: re-run Supabase's advisor check (or query `pg_tables`/`pg_policies`
   directly) to confirm RLS default-deny now covers `social_media_mounts`,
   `social_media_intents`, and `execution_nodes` -- same pattern as every other table.

3. **[Founder]** Re-point the Vercel project's connected repository from WS3.3 to this repo
   (`WebStaffr4`). Vercel project settings → Git → change repository. Env vars persist with
   the project.

4. **[Agent, post-deploy]** Smoke test against the live URL once the new deploy is up:
   - `GET /health` → `200 {"status":"ok"}`
   - `POST /chat` with a real tenant → `200`, response carries
     `Access-Control-Allow-Origin`
   - `GET /sites/{a_real_tenant_id}` → response contains no `lead_routing`, `approver`,
     `competitors`, or `license_number` keys
   - `POST /book` with no `X-API-Key` → `401`, response carries **no** CORS headers
   - A malformed Retell signature on `/retell/webhook` → rejected

5. **[Founder]** Eyeball-check: open a real generated customer site (Lovable-hosted), confirm
   the Angel widget loads and a chat round-trip works end to end against the newly
   re-pointed backend.

6. **[Founder]** Once stable, update WS3.3's own `README.md` to point at this repo, and
   consider tagging WS3.3's final commit as `archive/final`.

---

## Post-Cutover Monitoring (first 30 days)

- [ ] **Inbound call volume**: at least 1 call/day from genuine inquiries.
- [ ] **Answer rate**: 100% of calls answered by Angel (no failures/timeouts).
- [ ] **Booking accuracy**: >90% of bookings correctly captured (name, phone, time, service).
- [ ] **GHL sync success**: 100% of booked appointments synced without error.
- [ ] **Error logs**: no unhandled exceptions; the `_db_connection_failed` logging added to
      the four connection-boundary functions (`site_router.py`, `intake_router.py`,
      `attribution_router.py`, `workers/angel/router.py`) means a DB-layer failure now shows
      up in Vercel logs with an exception type -- check for it, don't assume silence means health.
- [ ] **First renewal decision**: by day 28, customer decides to renew or cancel.

---

## Rollback Triggers

If any of the following occur post-cutover, re-point the Vercel project back to WS3.3
(the archive repo, still fully intact) rather than trying to hot-fix forward under pressure:

1. More than 10% of inbound calls fail to connect or timeout.
2. Any call data (names, phone numbers) appears in logs or public output.
3. GHL sync fails for 3+ consecutive bookings.
4. `/sites/{tenant_id}` starts returning internal-only fields (never-leak list regression).
5. Error rate >1% on any endpoint (monitored via Vercel logs).

---

## Definition of "MVP Validated"

Unchanged from WS3.3: validated when at least 1 paying customer is live and answering calls,
at least 1 inbound call has been successfully answered and booked, and the customer renews
after their first billing cycle. All other metrics are operational -- retention is the
success signal.

---

**Last Updated:** at WebStaffr 4.0 rebuild completion.
**Next Review:** before running step 1 above (the production DB change).
