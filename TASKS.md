# TASKS.md — WebStaffr 4.0

## Completed

- **Clean rebuild from WS3.3.** Carried forward only proven, running code (~95 files) into a
  new repo with fresh git history. WS3.3 (and WS3.0 before it) remain untouched on GitHub as
  archives. See `docs/DECISIONS.md` ADR-012 through ADR-016 for the full rationale of each
  structural change below.
- **Composition root split.** `webstaffr/app.py` is now the single place that assembles the
  FastAPI app; Angel's own endpoints (`/chat`, `/book`, `/webhooks/ghl`) moved into
  `create_angel_router()` in `workers/angel/router.py`. Verified: 170/170 tests passing
  immediately after the split, before any further changes.
- **Unused workflow engine left behind.** `workflow.py`, `execution.py`, `executor.py`,
  `repository.py` and their dedicated tests are not part of this repo -- verified via
  full-repo grep that nothing in the live product's HTTP surface ever called them. Also
  removed the dead `db.py` special-casing that existed only to serve that engine
  (`_LASTROWID_PK["execution_records"]`, the `INSERT OR REPLACE INTO workflow_definitions`
  Postgres-dialect translation, and its dedicated test class).
- **Integration packages consolidated.** `integrations/social_media/`'s
  `SocialMediaMount`/`SocialMediaIntent` dataclasses now live only in `client.py` (`sync.py`
  imports them). `integrations/workflow_graph/` collapsed from three layers to one --
  `sync.py` and `repository.py` deleted, their logic folded into `client.py`. Verified safe
  in every import order (tested `sync`-first, `client`-first, and package-first imports
  directly).
- **Migrations renumbered, engine tables dropped from the SQLite baseline.** New
  `0001_tenants.sql` through `0007_execution_nodes.sql` replace the old `0001-0008` set (no
  `workflow_definitions`/`execution_records`, no numbering gap). Verified: a fresh migrate()
  produces exactly the 9 expected application tables, with the two dropped-engine tables
  confirmed absent.
- **Two new Postgres migrations written** (`postgres_manual/0007_social_media.sql`,
  `0008_execution_nodes.sql`) closing a real gap: `social_media_mounts`/`social_media_intents`
  and `execution_nodes` previously had no Postgres DDL and no RLS at all. **Not yet applied**
  to the live database -- see Pending.
- **`health_check.py` reworked** to smoke-test the actual live product surface (imports,
  fresh-migrate table assertions, app boot + full `/chat`/`/book`/`/webhooks/ghl` round trip,
  intake round-trip with cross-tenant isolation check, site-data never-leak assertion, CORS
  scoping, rate-limit trip, prompt asset load) instead of the removed workflow engine.
  8/8 checks HEALTHY.
- **CI standardized on Python 3.12** (Vercel's runtime), matching the local dev venv used for
  all verification this session.
- **`pyproject.toml` removed entirely.** `requirements.txt`/`requirements-dev.txt` are now
  the sole dependency source (`pytest.ini` covers test config) -- closes the version-drift bug
  where `pyproject.toml`'s pins had gone stale against what Vercel/CI actually installed. See
  `docs/DECISIONS.md` ADR-016.
- **Dangling doc references cleaned up.** Every citation of `CODE_REVIEW.md`, `STRATEGY.md`,
  `TIER_A_ROADMAP.md`, and `RETAINED_GRAPH_MODEL.md` (files that don't exist in this repo)
  removed from source comments, docstrings, and one customer-facing API response field
  (`attribution.py`'s `estimated_value_note` no longer names internal doc files).
- **Fresh doc set written** (not copy-pasted): `CLAUDE.md`, `README.md`, `PROJECT.md`,
  `CREDENTIALS.md`, `docs/ARCHITECTURE.md`, `docs/API.md`, `docs/DATABASE.md`,
  `docs/SECURITY.md`, `docs/DECISIONS.md`, `docs/MARKETING_COORDINATOR_PLAN.md` (moved from
  root, paths/migration numbers updated), `DEPLOYMENT_CHECKLIST.md`.
- **Final verification**: full suite green in a fresh, isolated Python 3.12 venv, health
  check HEALTHY, before the initial commit.
- **Production cutover complete (2026-07-26, verified live 2026-07-27).** The two Postgres
  migrations (`0007_social_media.sql`, `0008_execution_nodes.sql`) are applied to the live
  Supabase project -- all 11 public tables confirmed with RLS enabled, default-deny
  (0 policies), verified via direct `pg_tables`/`pg_policies` query. Vercel project
  `web-staffr3-3` now builds from `keithtortorich/WebStaffr4.0` commit `681870d` --
  confirmed via the deployment's own git metadata, not assumed. Latest production deploy
  READY at `web-staffr3-3.vercel.app`.
- **Post-cutover smoke test passed (2026-07-27, live URL).** `/health` 200; `/sites/{tenant}`
  200 with zero never-leak fields (`lead_routing`/`approver`/`competitors`/`license_number`
  all absent); `/book` carries no CORS headers; `/chat` 200 with graceful NullVoiceBackend
  fallback reply (GROK_API_KEY unset -- expected, see Pending).

## In Progress

(none)

- **Founder eyeball-check passed (2026-07-27, Site Weaver Lovable preview).** Loaded the live
  tenant site for `webstaffr_e2e_verification_co_d07dc1d1`: hero, tagline, industry/location
  badge, call/email CTAs all rendered correctly from the live backend. Angel widget loaded and
  gave a real, on-topic Grok reply to "Do you offer emergency plumbing service?" -- confirmed
  full round trip, not a Null/fallback response.
  **Bug found and fixed en route:** Site Weaver's Lovable project had a stale runtime secret
  `API_BASE_URL` pointing at `web-staffr3-0-snowy.vercel.app` (WS3.0's dead deployment,
  503) that shadowed the already-correct `.env` value. `.env` was fixed via the Lovable
  agent; the runtime secret required the founder to update directly in Lovable's Project
  Settings -> Secrets (blocked from being changed programmatically, correctly, per this
  repo's credential-handling rules). Both now point at `web-staffr3-3.vercel.app`.

- **6 of 7 open Dependabot PRs reviewed and merged (2026-07-27).** All CI-green, no conflicts:
  `actions/setup-python` 6->7 (#1), `actions/checkout` 6->7 (#2), `pytest` 8.4.2->9.1.1 (#3),
  `fastapi` 0.139.2->0.140.0 (#6), `anyio` 4.12.1->4.14.2 (#7), `uvicorn` 0.39.0->0.51.0 (#5)
  -- the last being the biggest version jump and the piece most tied to the Vercel-serverless
  invariant, merged only after confirming CI (which boots the app and round-trips
  `/chat`/`/book`/`/webhooks/ghl`) passed clean. **#4 (`pydantic-core` 2.46.4->2.47.0) left
  open, correctly** -- CI fails with a real pip dependency conflict: `pydantic` 2.13.4 pins
  `pydantic-core==2.46.4`, so bumping the sub-dependency alone is unresolvable. Not a repo bug;
  waiting on Dependabot/upstream to bump `pydantic` itself before this is mergeable.

## Pending

- **Set remaining production credentials on the Vercel project** -- all tied to paid vendors,
  deliberately deferred by founder decision (2026-07-27: no new spend or timed trials yet):
  `GHL_API_KEY` + `GHL_LOCATION_ID` (GHL subscription), `GHL_WEBHOOK_SECRET` (free, but
  generate it when the GHL account exists so it can be pasted into both sides in one sitting
  -- Vercel Sensitive vars can't be read back), `RETELL_WEBHOOK_SECRET` (Retell account).
  Until set: GHL sync is a no-op and both webhook routes fail open (Null verifiers) -- safe,
  by design. Set (verified live 2026-07-27): `GROK_API_KEY` (`/chat` returns real Grok
  replies), `BOOK_API_KEY` (`/book` now 401s unauthenticated callers -- fail-open closed).
- **Founder decision: disposition of `WebStaffr 3.0/` and `social-media-marketing-machine/`
  subfolders** inside the WS3.3 archive repo (leave as-is vs. prune).
- **ServiceTitan socket workflow format** -- open design decision, needed before the next
  ServiceTitan integration pass (post-MVP).
- **D4 (SMS/email vendor)** for the Marketing Coordinator's two-way client comms channel --
  explicitly left open by the founder; see `docs/MARKETING_COORDINATOR_PLAN.md`.
- **Retell signature format is `[Unverified]`** against a real Retell-signed request -- see
  `docs/SECURITY.md`.
- **Dormant `postgres_manual/0009_drop_engine_tables.sql`** -- not run at cutover; revisit
  after this repo has run in production for at least a week with no regressions.

## Blocked

(none -- the prior `/sites/{tenant_id}` 503 was diagnosed post-cutover as a `DATABASE_URL`
hostname transcription error (`.co` vs the correct `aws-1-ap-south-1.pooler.supabase.com`),
fixed and verified live 2026-07-27: `/sites/{tenant}` returns 200 with correct data.)
