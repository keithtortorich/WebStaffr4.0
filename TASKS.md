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

- **WebStaffr Agency Site (Lovable, new project, 2026-07-27).** Reviewed a stack of loose
  frontend/marketing files handed off outside this repo (`WS4 TBR/` folder plus uploaded docs):
  an old React/Vite `frontend/` scaffold, an `intake.html` prototype, several marketing-site
  HTML mockups, and strategy/brand reference docs. All Python/servicetitan files in that stash
  were byte-identical to what's already in this repo -- no code integration needed there.
  The frontend scaffold and intake prototype are **not wired to this backend's real routes**
  (`intake.html` posts to a nonexistent `/api/leads`; the React scaffold displays
  `site.license_number`, a field `site_data.py` deliberately never sends) -- flagged, not fixed,
  since frontend is Lovable's domain per this repo's MVP Scope section, not this repo's to patch.
  Ran this project's `governance-compliance-linter` skill against the WebStaffr agency
  marketing-site HTML using a ruleset derived from the founder's actual Brand Handbook PDF
  (uploaded this session -- supersedes the skill's stale captured ruleset, which cited a
  `docs/governance/DOC1.1_writing_editorial.md` that does not exist anywhere in this repo or
  its lineage). Confirmed rules: company name is always **WebStaffr** (the handbook's own
  cover-page logo violated this -- "WebStaff" -- a real finding, not a false positive); never
  say "AI" in customer-facing copy; no emojis in brand-facing assets. The em-dash "ban" cited
  by the old ruleset does not appear anywhere in the real handbook and was dropped rather than
  enforced. Fixed all naming/AI/emoji violations in the reference HTML, then created a **new**
  Lovable project, "WebStaffr Agency Site" (`https://lovable.dev/projects/6c33e383-76ed-4398-ae38-8428d80d06da`),
  separate from the existing "Site Weaver" project -- Site Weaver renders customer/tenant sites
  from `/sites/{tenant_id}`; this new project is the company's own public marketing site and
  has no tenant_id logic, so folding it into Site Weaver would have muddied that project's scope.
  Lovable's `create_project` call returned a client-side timeout but the project completed
  server-side (confirmed via `list_projects`) -- **not yet visually verified** against the
  brand rules in the actual rendered preview; per this repo's rule to independently verify
  agent "done" claims, review the Lovable editor/preview before treating this as finished.

- **WebStaffr Agency Site: live preview independently verified (2026-07-27).** Pulled the full
  rendered page text from the live preview URL
  (`id-preview--6c33e383-76ed-4398-ae38-8428d80d06da.lovable.app`) via Chrome tools, not just a
  screenshot -- confirmed this is a real, working build (status `completed`, `agentFinished: true`),
  closing the open verification item from the entry above.
  **Clean:** WebStaffr spelling correct everywhere (nav, footer, copyright); no "AI"/"chatbot"/
  "software"/"platform" language describing the product anywhere on the page (uses "Angel" /
  "recurring office staff" / "receptionist" throughout, matching brand rules); no emoji characters,
  only the approved thin ✦ glyph and star-rating glyphs.
  **3 issues found, none fixed yet (see Pending -- blocked on Lovable credits):**
  1. Three em-dashes in body copy (hero paragraph, chat-orb "YES -- APPLY NOW" button, "Why
     WebStaffr" section) -- violates the no-em-dash rule (present in both the Brand Handbook
     finding and the separate Governance Manual excerpt provided 2026-07-27).
  2. The 11 demo-gallery industry cards (Luna Salon, Rivera Plumbing, Rodriguez Law, etc.) and 3
     testimonial quotes in the Proof section show specific fabricated-looking stats (review
     counts, star ratings, named businesses) presented as if real, with nothing marking them as
     illustrative -- this is the same category of problem this repo's own no-fabrication
     invariant exists to prevent, just surfaced on the marketing site rather than in
     `site_data.py`.
  3. Live pricing section shows three tiers ($97/mo "Site", $497/mo "Site + Office Staff", custom
     "Full Front Office") that don't match the official Governance Manual pricing (Office Staff
     $497/mo, Business Manager $2,497/mo, White-Glove $5,000+/mo custom) -- pricing has drifted
     from source of truth on this specific Lovable project.
  A single consolidated fix instruction for all three issues was drafted and sent to the Lovable
  agent, but the send failed: **workspace is out of Lovable credits** (API error, not a
  founder-decision block). See Pending.

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

- **WebStaffr Agency Site (Lovable): 3 fixes queued, blocked on Lovable credits (2026-07-27).**
  Consolidated instruction ready to send the moment credits are added at
  `lovable.dev/settings/billing`: (1) remove 3 em-dashes from body copy, (2) label the demo-gallery
  cards and testimonials as illustrative examples rather than implying real customers, (3) correct
  the live pricing tiers to match the Governance Manual ($497/$2,497/$5,000+ instead of the
  currently-shown $97/$497/custom). Not a founder-decision block -- purely an account-credits
  issue; resend the same instruction once resolved.
- **Two governance source documents disagree on the em-dash rule (2026-07-27, unresolved).**
  The founder's Brand Principles Handbook PDF (verified earlier session) uses em-dashes freely in
  its own body copy with no stated ban anywhere in its 19 pages. A separate "WebStaffr Governance
  Manual" excerpt (provided 2026-07-27, used as source of truth for the new
  `webstaffr-website-copy` skill and all website copy work below) explicitly states "no
  em-dashes anywhere in WebStaffr copy, internal or external... This applies to marketing, sales
  materials, investor decks, internal documentation, everything." Per founder direction, the
  Governance Manual's no-em-dash rule has been followed for all copy produced this session (the
  new website copy doc, and the Lovable fix instruction above). The two source documents still
  conflict and haven't been reconciled -- flagged, not resolved.
- **New WebStaffr website copy produced and a reusable skill created (2026-07-27, outside this
  repo).** Full production-ready website copy (Home, Pricing, How It Works, Industries, About,
  FAQ, Contact, nav, footer, CTAs, forms, microcopy) was written following the Governance Manual,
  using verified statistics only (Invoca 2026's 27% unanswered-call figure and the MIT/Oldroyd
  speed-to-lead study both held up on independent search; a claimed "85% of voicemail callers
  never call back" BIA/Kelsey stat and a claimed HVAC-specific "34% answer rate" did not, on two
  separate rounds of independent verification, and were deliberately left out of the copy). A
  packaged `webstaffr-website-copy` skill was also built to standardize this for future copy
  requests. Both live outside this repo (Cowork outputs/skill library), not committed here --
  noting for context since they used this repo's Brand Handbook findings as partial input.
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
