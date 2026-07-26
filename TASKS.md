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

## In Progress

(none)

## Pending

- **Founder: run the two new Postgres migrations** (`postgres_manual/0007_social_media.sql`,
  `0008_execution_nodes.sql`) against the live Supabase project before cutover -- production DB
  change, requires explicit approval per `CLAUDE.md`. See `DEPLOYMENT_CHECKLIST.md`.
- **Founder: re-point the Vercel project** from WS3.3 to this repo. Env vars persist with the
  project; see `DEPLOYMENT_CHECKLIST.md`.
- **Post-cutover smoke test** against the live URL once re-pointed: `/health`, `/chat` (200 +
  CORS), `/sites/{tenant}` (no never-leak fields), `/book` (401 + no CORS without a key),
  Retell bad-signature rejection, and a founder eyeball-check of the Lovable site's chat
  widget end to end.
- **ServiceTitan socket workflow format** -- open design decision, needed before the next
  ServiceTitan integration pass (post-MVP).
- **D4 (SMS/email vendor)** for the Marketing Coordinator's two-way client comms channel --
  explicitly left open by the founder; see `docs/MARKETING_COORDINATOR_PLAN.md`.
- **Retell signature format is `[Unverified]`** against a real Retell-signed request -- see
  `docs/SECURITY.md`.
- **Dormant `postgres_manual/0009_drop_engine_tables.sql`** -- not run at cutover; revisit
  after this repo has run in production for at least a week with no regressions.

## Blocked

(none carried forward from WS3.3 as of this rebuild -- the prior `/sites/{tenant_id}` 503
investigation and its Supabase credential-retrieval blocker were WS3.3-specific operational
issues, not code defects in what was carried into this repo. Re-verify against this repo's
own deploy once cutover happens, rather than assuming resolved.)
