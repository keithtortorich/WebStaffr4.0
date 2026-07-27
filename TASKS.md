# TASKS.md — WebStaffr 4.0

## Session Handoff (2026-07-28, landing page governance + dead form)

**Fixed in `webstaffr/landing_router.py` (local only, not committed):**
- `<title>` read "WebStaffr — AI Staff for Home Services". Two governance breaches in
  the single most public string on the site: "AI" in customer-facing copy, and an
  em-dash. Now "WebStaffr | 24/7 Receptionist for Home Services", which uses the
  product framing already on the page.
- Five other em-dashes removed from customer-facing copy (H1, "See It Live" heading,
  the ladder/house line, the "Everything else" line, the investor PDF string).
- **Dead lead-capture form fixed.** The "Get Your Free Website" form had no `action`,
  no `method`, and no submit handler. It promised a site in 48 hours and silently
  discarded every submission. It now has a submit handler that opens a prefilled email
  to the contact address, plus a visible status line. Interim, not final: `/intake`
  requires twelve fields, two of which (`lead_routing`, `approver`) are internal-only
  and can never appear on a public form, so this three-field form has no endpoint it
  can legitimately post to yet.
- Contact email and phone were duplicated across three places and had drifted. Now
  defined once as `_CONTACT_EMAIL` / `_CONTACT_PHONE` / `_CONTACT_PHONE_TEL` and
  substituted into the HTML by `_render_landing_page()`.

**Left alone deliberately:**
- "It's not software. It's not AI. It's not a chatbot." reads as an "AI" breach but is
  canonical, MESSAGING_CANONICAL.md line 50, founder-authored, and disclaims AI rather
  than positioning as it. Founder's call, not an engineering fix.

**Resolved this session:**
- **Contact email.** Founder confirmed mail goes to `keithtortorich@gmail.com`, not to
  any mailbox on webstaff.com or webstaffr.com. The old `keith@webstaff.com` was dead.
  Updated in `landing_router.py` (via `_CONTACT_EMAIL`, so it covers the investor JSON,
  the investor modal, and the lead form), INVESTOR_EMAIL_FINAL.md, and
  POST_DEPLOY_VERIFICATION.md.

**Pending founder decision:**
- **Which domain is the live site?** Still unsettled and now independent of email.
  INVESTOR_EMAIL_FINAL.md and POST_DEPLOY_VERIFICATION.md say `webstaff.com`;
  LINK_MANIFEST.md and docs/SITE_WEAVER_SEO_BLUEPRINT.md say `webstaffr.com`. Investor
  materials currently point at three `https://webstaff.com` URLs. If that domain is not
  the one being deployed, those links are dead in a document already sent to investors.
- **Personal Gmail as the public and investor contact.** Works, and it is the founder's
  call, but a Gmail address on investor materials reads differently from a domain
  address, and it cannot be reassigned to staff later without changing every published
  document. Worth revisiting once the domain question above is settled, since the fix
  is then a forwarding alias rather than a rewrite. Not blocking anything.
- **What is the public intake contract?** Either the landing form stays a short lead
  capture that hands off to a longer onboarding form, or `/intake` grows a public
  subset with the internal fields set server-side. That decision blocks the real
  endpoint and is a customer-experience call.

**Verified:** Python syntax passes; template renders with zero unsubstituted tokens,
zero em-dashes, zero bad brand spellings, zero emoji. No landing page tests exist
(`tests/` has none for this router) so this is static verification only, not a test run.

## Session Handoff (2026-07-28, Sam worker complete)

**Sam — Sales Consultant AI worker (MVP implementation complete, 2026-07-28):**
- **Purpose:** Generate quotes, handle objections, drive quote-to-booking conversion. Target: 50% of quotes sent automatically within 24h of lead intake, quote-to-booking conversion tracked per industry.
- **Architecture:** Sibling worker to Angel and Leo, same composition-root pattern, dependency injection, tenant isolation. Three endpoints:
  - `POST /quotes/generate` (server-to-server): accepts lead data (contact_id, name, email, service scope, industry, urgency), pulls pricing from trade presets, generates estimate range with caveats, stores quote record, sends via GHL email (if configured), returns quote_id
  - `GET /quotes/{quote_id}` (server-to-server): fetch quote by ID (tenant-scoped), returns full quote data including status, timestamps, appointment link
  - `POST /quotes/{quote_id}/accept` (server-to-server): accept quote, create appointment via Angel's existing booking logic, link to quote, returns appointment_id
- **Data model:** New migration `0008_quotes.sql` (SQLite) and Postgres equivalent:
  - `quotes` table: id (uuid PK), tenant_id (FK), contact_id (GHL), contact name/email, service_scope (free-text), industry, estimated_range_low/high (no hardcoded specifics, always ranges), caveat (disclaimer "subject to site inspection"), status (pending/sent/accepted/declined), email_template (HTML body), timestamps (created/sent/accepted/declined), appointment_id (FK when accepted), declined_reason
  - Indexes on (tenant_id, status), (tenant_id, contact_id), (tenant_id, created_at DESC)
- **Code:**
  - `docs/WORKERS_SAM_DESIGN.md`: full architecture spec (triggering events, quote generation flow, pricing logic, objection handling, booking flow, API contract, protocols, database schema, error handling, testing strategy, constraints, out-of-scope items)
  - `webstaffr/workers/sam/__init__.py`, `protocol.py`: GHLQuoteClient protocol (send_quote_email, log_quote_note), TradePresetAccessor, ObjectionHandler, Null implementations
  - `webstaffr/workers/sam/pricing.py`: PricingEngine class with preset ranges for all supported trades (HVAC, Plumber, Electrician, Roofing, Water Damage, Garage Door, Pest Control, Landscaping, Tree Service, Cleaning). generate_estimate() extracts service keywords from scope, looks up trade-specific ranges, applies urgency multiplier (routine 1.0x, urgent 1.2x, emergency 1.5x), location premium (MVP: 1.0x placeholder), rounds to nearest $50, includes caveat text. Returns PricingEstimate with range and services_identified. Never fabricates: unknown services return 0-0 "contact for quote" fallback.
  - `webstaffr/workers/sam/objections.py`: ObjectionLibrary with per-trade objection responses (cost, timeline, warranty, availability, trust). Professional, educational tone — never pushy. Industry-specific responses (e.g. AC warranty differences from plumbing) with fallback to defaults. No promises; references "team will discuss" and "site visit". Context-aware personalization for business_name and services_mentioned.
  - `webstaffr/workers/sam/quote_repository.py`: Quote persistence layer (pattern: raw SQL, tenant scoped). Methods: create_quote(), get_quote(), update_quote_sent(), update_quote_accepted(), update_quote_declined(), list_quotes_by_contact(), list_quotes_by_tenant_status(). All queries use `?` placeholders, DB_ERRORS wrapping, StorageError exceptions.
  - `webstaffr/workers/sam/client.py`: GoHighLevelQuoteClient wraps existing GHLClient, adds send_quote_email() and log_quote_note(). ghl_quote_client_from_env() factory returns None if env vars missing (fallback to NullGHLQuoteClient pattern).
  - `webstaffr/workers/sam/router.py`: FastAPI router with 3 POST/GET endpoints. Validates input, resolves Tenant, calls pricing/objection layers, persists to DB, sends email via GHL (if configured), returns JSON. Error handling: invalid tenant → 400, missing/invalid fields → 400, GHL down → quote saved locally (email_sent: false), DB down → 503. Rate limiting: not wired yet (post-MVP).
  - `tests/test_sam_pricing.py`: 12+ unit tests (known/unknown services, urgency multipliers, multi-service parsing, range validation, all trades, caveat text)
  - `tests/test_sam_objections.py`: 10+ unit tests (default/industry-specific responses, objection types, educational tone, caveats, never empty)
  - `tests/test_sam_router.py`: 20+ integration tests (quote generation, pricing correctness, unknown service fallback, urgency effects, DB persistence, GET retrieval, tenant isolation, quote acceptance/appointment creation, no-fabrication validation)
- **Integration:** GHLClient protocol already exists in Angel; Sam extends it with send_quote_email() and log_quote_note() via GoHighLevelQuoteClient wrapper. Wired Sam router into `webstaffr/app.py` as sibling to Angel, Leo, Rita; uses existing ghl_client from app factory; db_path passed through; reuses Tenant validation and error patterns. Quote acceptance calls Angel.book_appointment() in-process.
- **Error resilience:** GHL unavailable → quote saved locally with email_sent=false, no network retry (post-MVP); pricing data missing → return (0,0) "contact for quote"; invalid tenant → 400; quote not found → 404. All queries tenant-scoped.
- **MVP scope:** Quote generation with trade-specific ranges, email send, objection responses with templates, booking flow to appointment. NOT included: quote expiry enforcement, multi-language templates, dynamic pricing from historical costs, A/B testing quote formats, Marketing Coordinator follow-up sequences, TCPA/DNC compliance, quote assignment to sales reps, performance tracking/dashboards.
- **No fabrication:** Ranges come from trade_presets.py only (market research-based, not fabricated). Caveats always present. Objection responses use real business name/services where available, generic fallback if not. Pricing never shows specific numbers without trade/service backing.
- **All constraints satisfied:** No new dependencies (stdlib only). Tenant isolation enforced. POST routes carry no CORS headers. GHL unavailable → graceful fallback. Null defaults for unconfigured GHL. Protocol-based design. All tests pass syntax check. Design doc complete.
- **Not yet tested in sandbox** (venv mount restriction), **not yet committed/pushed** (awaiting founder approval per CLAUDE.md). Syntax validation: PASS (all modules, tests, migration). Ready for `pytest` and health check after push.

## Session Handoff (2026-07-28, Leo worker complete)

**Leo — Lead Coordinator AI worker (MVP implementation complete, 2026-07-28):**
- **Purpose:** Instant follow-up on every lead within 2 minutes. Receives leads from GoHighLevel webhook, scores with AOKAI 100-point rubric, routes to call-led (SMS) or email-led nurture, stores for tracking.
- **Architecture:** Sibling worker to Angel, same composition-root pattern, dependency injection, tenant isolation. Two endpoints:
  - `POST /webhooks/ghl/lead` (server-to-server, GHL → Leo): validates webhook secret, scores lead, determines tier, sends first-touch SMS or email via GHL, stores in `webstaffr_leads` table, returns score/tier/sync_status
  - `POST /leo/score` (internal test endpoint): accepts lead signals, returns AOKAI breakdown
- **Data model:** New migration `0008_leo_leads.sql` (SQLite) and `postgres_manual/0009_leo_leads.sql` (Postgres with RLS):
  - `webstaffr_leads` table: lead_id (PK), tenant_id (FK), GHL contact data, AOKAI score breakdown (accessibility/business_size/digital_maturity/revenue_potential/buying_signals), tier, first_touch_channel, first_touch_sent_at, sync_status, ghl_error, audit timestamps
- **Code:**
  - `docs/WORKERS_LEO_DESIGN.md`: full architecture spec (triggering events, data flow, AOKAI rubric, tier routing, API contract, database schema, testing strategy, open items)
  - `webstaffr/workers/leo/__init__.py`, `protocol.py`: GHLMessagingClient protocol (send_sms, send_email)
  - `webstaffr/workers/leo/scoring.py`: AOKAI 100-point rubric implementation (35 points Accessibility: phone/owner/text/email; 20 Business Size: employees/vehicles/hiring/locations; 20 Digital Maturity: website/booking/CRM/DIY; 15 Revenue Potential: industry-based; 10 Buying Signals: office hiring/reviews/financing/service history). Tier assignment: 1 (85-100 call-led), 2 (70-84 call-led), 3 (55-69 email-led), 4 (<55 skip).
  - `webstaffr/workers/leo/router.py`: HTTP endpoints, payload validation (LeadWebhookEvent), AOKAI calculation, lead storage, first-touch SMS/email templates (industry-aware, no fabrication), rate limiting, tenant isolation, error handling
  - `tests/test_leo_scoring.py`: 60+ unit tests (all categories, score ranges, tier assignment, industry mapping, edge cases)
  - `tests/test_leo_router.py`: 20+ integration tests (webhook round-trip, lead storage, SMS/email routing, tier thresholds, tenant isolation, rate limiting, error responses, GHL sync failure handling)
- **Integration:** Extended GHLClient protocol and both implementations (NullGHLClient and GoHighLevelClient in `webstaffr/workers/angel/ghl.py`) with send_sms() and send_email() methods. Wired Leo router into `webstaffr/app.py` as sibling to Angel; reuses ghl_webhook_verifier for signature verification; uses existing rate_limit.py counter.
- **Error resilience:** GHL API unreachable → lead stored locally with sync_status="pending_sync" and ghl_error captured for retry (post-MVP background job). Invalid tenant/event_type → 400. Bad/missing webhook secret → 401. Rate limit exceeded → 429. DB error → 503.
- **MVP scope:** Receives leads, scores, stores, sends first touch only (SMS for Tier 1-2, email for Tier 3). Full 7-touch (Tier 1-2) and 5-touch (Tier 3) sequences are post-MVP. No deduplication, lead sourcing, Retell cold-calling, performance tracking, manual review escalation, or compliance (TCPA/DNC) wired yet.
- **No fabrication:** AOKAI scores use real lead data only, never default/assumed values. Email/SMS templates use real business name, contact name where available, fallback to generic copy.
- **Not yet tested in sandbox** (venv mount restriction), **not yet committed/pushed** (awaiting founder approval per CLAUDE.md). Code ready for `pytest` and health check after push.

## Session Handoff (2026-07-28, Rita worker complete)

**Rita — Reputation Manager AI worker (MVP complete, pending tests/health check):**
- **Status:** All code written. Tests written. Composition root wired. Ready for `pytest` and health check verification.

## Session Handoff (2026-07-28, earlier updates)

**`sales-crm.html` merged with founder-supplied mobile sales tool (uncommitted, local only):**
- Founder uploaded "WS sales-tool-new 2.html" (a mobile-first rep tool) and directed a merge, with the new tool as the base. Result replaces `sales-crm.html` in full: the new tool's mobile shell (navy/gold, 520px, scrollable tabs) now hosts 8 tabs — Revenue (missed-call calculator with per-trade job-value presets and live loss meter), Leads (ported from old CRM: AOKAI 100-point rubric, 48h escalation with distinct Reviewed state, referral logging), Pitch (personalized generator: 6 templates filled from business/owner/trade/city, copy-to-clipboard), Objections (8, accordion), ROI (human receptionist vs. WebStaffr + commission calculator), Tracker (one-tap call outcomes, CSV export), Referral kit, Notes.
- Governance fixes applied to the uploaded tool's content before merge: "WebStaff" → WebStaffr throughout; all "AI receptionist / AI staff" wording removed from customer-facing pitch/objection copy; em-dashes and emojis removed; XSS-escaping and event delegation carried over from the 2026-07-27 CRM rebuild.
- **Pricing corrected per founder (2026-07-28):** uploaded tool's $197/$497/$997 tiers were old pricing; replaced with Governance Manual tiers — Office Staff $497/mo, Business Manager $2,497/mo (White-Glove $5,000+/mo is custom-quoted, excluded from fixed-price calculators). **Commission rate 20% founder-confirmed 2026-07-28.**
- Referral rewards card keeps the $430 reconciled max with the visible note; `referral.md` reconciliation still pending founder review (unchanged open item).
- Verified this session: JS syntax check clean (node --check), zero emoji, zero em-dashes, no bad brand spelling, no "AI" mentions, no old prices — automated checks only, not yet opened in a live browser by a human. localStorage keys: `webstaffr_sales_data` (leads/notes/referrals, preserved from old CRM so existing data survives) and `webstaffr_calls` (new call tracker).
- One retained unverified stat: "slow sites lose 53% of mobile visitors" (Google/SOASTA-derived claim, in the bad-site email and website objection). Not one of the previously debunked 85%/78% stats, but not independently verified in this repo either — flag for the next copy audit.

## Session Handoff (2026-07-27)

**Pushed to origin/main, verified live (189/189 tests, 9/9 health checks, this session):**
- `643d4c6` Narrowed supported industries to the priority trade list.
- `daa906f` Added the in-repo server-side site renderer (Jinja2 templates, SEO/schema, tests).
- `edb0d75` Rewrote the landing page, wired 11 working links.
- `c990e24` **Fixed no-fabrication violations in `home.html`** found during this session's review: a hardcoded "5,000+ Jobs Done" stat, a `years_in_biz or 15` fake-default, a trust bar that fabricated "4.9 stars / 100+ reviews" for tenants with zero real reviews, unconditional trust badges, and a fabricated second review card. All now gate on real `site_data` fields. Also added an objection-handling "Common Questions" (MFAQ) section, plain copy not schema.org markup, gated on real intake fields only.
- `ce87ed7` Doc updates (README, TASKS.md).
- `f0c5b44` Added `referral.md` (new Referral Program, founder-approved as its own source of truth — no prior governance doc for it). **One open item still unresolved:** the "Max per referral: $560+" figure doesn't reconcile against the stated upfront ($100) + recurring ($180) + retention ($150) = $430; flagged in the doc, not fixed, since the right fix depends on which component was meant to carry the extra multiplier.
- Also caught and stripped mid-session: the landing page draft had reintroduced the "85% of voicemail callers never call back" stat (BIA/Kelsey), which had already failed independent verification twice earlier the same day and was deliberately excluded from the real website copy. Removed from all 3 occurrences before push.

**Not committed — sitting as untracked reference material, founder review pending:**
- `docs/POSITIONING_AUDIT_PROTOCOL.md` — a prospecting research protocol (review sentiment, website/social audit, competitor mapping, positioning logic) for a future outbound sales tool. Not code, not wired to anything.
- `docs/LEAD_ENGINE.md` (2026-07-27) — **merged, current reference**, superseding both `docs/LEAD_ENGINE_ARCHITECTURE.md` and `docs/LEAD_ENGINE_PHOENIX_INTEGRATION.md` (both left in place, verbatim, with a superseded banner pointing here). Consolidation: one outreach sequence (call-led for AOKAI tiers 1-2, email-led nurture for tier 3, replacing two overlapping sequences), AOKAI as the sole scoring rubric, GoHighLevel as the sole CRM (HubSpot Free dropped as a duplicate), stack re-baselined GHL-native per `CLAUDE.md` (Twilio/MessageBird/Instantly/SmartLead/Privyr/Zapier/Streamlit-Tableau demoted from "the stack" to "escalation options, each needing its own approval"), cutting new-vendor approvals needed from 7+ down to 2 (a lead-sourcing vendor, and Retell AI's new outbound-calling use). All epistemic flags from both source docs carried forward (AOKAI "documented but unexecuted," the unverified compiled spreadsheet, founder time commitment) plus one new one: neither source doc addressed TCPA/DNC-registry compliance for automated cold calls and SMS — flagged as required before any outbound runs, not resolved.
- `sales-crm.html` (rebuilt 2026-07-27) — this is WebStaffr's own internal lead machine (not the Marketing Coordinator, which stays out of MVP scope). Rebuilt in place, same look and no new dependencies, still `localStorage`-only and not wired to this repo's backend. Fixes: logo corrected from "WebStaff" to WebStaffr; all emoji removed; debunked 85%/78% stats replaced with the one verified stat (Invoca 2026, 27% unanswered calls) already used in the real website copy; em-dashes removed from copy that leaves the tool via copy-to-clipboard; referral "Max" figure changed from the unreconciled "$560+" to $430 (the value `referral.md` itself derives by arithmetic), with a visible note pending the founder's reconciliation call on that doc. The AOKAI scorer was a placeholder simulation (hardcoded values, only ever scored the most-recent lead) — replaced with a real per-lead 100-point checklist matching `docs/LEAD_ENGINE.md`'s rubric exactly, tier badge shown per lead. Escalation logic bug fixed: "Mark Reviewed" previously mislabeled escalated leads as "Contacted" with no actual contact; now a distinct "Reviewed" state, and the 48-hour clock anchors on last real contact (or creation if never contacted) instead of always creation. Also fixed: unescaped user input (lead names/notes) rendered directly into the DOM, now escaped; inline `onclick` handlers replaced with event delegation. Verified this session: JS syntax check clean, zero emoji, zero em-dashes, no bad brand spelling, all via automated grep/node checks — not yet opened in a live browser by a human.
- Also present, untouched, not reviewed this session (unclear provenance, likely from a separate tool/session): `DEMO-TEMPLATES-INDEX.md`, `DEPLOYMENT_SUMMARY.md`, `INVESTOR_EMAIL.md`, `INVESTOR_EMAIL_LIVE.md`, `INVESTOR_UPDATE_2026-07-27.md`, `MARKETING_COORDINATOR_PUBLISHING_API_OPTIONS.md`, `POST_DEPLOY_VERIFICATION.md`, `PUSH_COMMANDS.sh`, `WebStaffr 3 Consolidated Master Document (v1.md`, `demo-templates/`. None of these are wired into backend code (the landing page's demo links route through the site renderer, not the static `demo-templates/` files).

**Repo state at handoff:** `main` in sync with `origin/main` at `f0c5b44`. Working tree has no modified tracked files, only the untracked items listed above.

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

- **Supported industries narrowed to WebStaffr's priority trade list (2026-07-27, founder
  direction).** `webstaffr/trade_presets.py`'s `SUPPORTED_INDUSTRIES` replaced: kept
  HVAC/Plumber/Electrician/Roofing, dropped Contractor/Restaurant/Med Spa/Dentist/Salon
  (off-strategy), added Water Damage Restoration, Garage Door Repair, Pest Control,
  Landscaping, Tree Service, Cleaning Services -- the founder's ranked list of trades where
  speed-to-lead most directly determines revenue. "Other" stays as the always-available
  fallback (`normalize_industry()` behavior unchanged, so intake still never hard-fails on an
  unlisted business type). Added illustrative `TRADE_HINTS`/`TRADE_SOFTWARE` entries for all
  6 new trades, matching the existing style (Phoenix-themed placeholder copy, real
  vertical-specific FSM software names -- PestPac/FieldRoutes for pest control,
  Aspire/LMN for landscaping, Arborgold/SingleOps for tree service, ZenMaid/Launch27 for
  cleaning, Xactimate/DASH/Encircle for restoration). Added aliases (Restoration,
  Garage Door, Exterminator, Lawn Care, Tree Trimming, House Cleaning, etc.) so common
  synonyms resolve to the right canonical key.
  `webstaffr/site_renderer.py`'s `_SCHEMA_TYPE_BY_INDUSTRY` updated to match: the 6 new
  trades have no dedicated schema.org LocalBusiness subtype, so they use the real parent
  type `HomeAndConstructionBusiness` rather than inventing one (no-fabrication invariant
  applied to schema markup, not just visible copy).
  Verified (this sandbox): 183/183 tests passing, 9/9 health checks HEALTHY, plus a manual
  end-to-end check (new industry preset, alias resolution, and JSON-LD schema type all
  correct on a real intake -> render round trip for Pest Control). Not yet pushed -- same
  push mechanics note as the site-renderer entry above (Desktop Commander, founder's Mac).

- **In-repo customer site renderer: built (2026-07-27), not yet pushed.** Per
  `docs/SITE_RENDERER_PLAN.md`'s build sequence, all steps complete:
  `webstaffr/site_renderer.py` (pure SEO/schema helper functions), `webstaffr/templates/site/`
  (Jinja2 templates for home/service/about/reviews/contact + sitemap.xml/robots.txt + shared
  CSS), `webstaffr/site_render_router.py` (GET routes at `/sites/{tenant_id}/web` and below,
  plus `/static/site.css` and `/static/angel-widget.js` -- the latter wasn't served by this
  backend at all before this change, only referenced in a comment), wired into
  `create_app()`. `jinja2==3.1.6` + `markupsafe==3.0.3` added to `requirements.txt`.
  20 new tests in `tests/test_site_render_router.py` covering rendered-page round trips,
  never-leak (HTML, not just JSON), no-fabrication (no aggregateRating/FAQPage schema
  without real data backing it, no forbidden brand copy), tenant isolation, and 404 handling.
  `health_check.py` gained a 9th check (`rendered_site_smoke_test`). Two real adaptations
  from the SEO blueprint, both documented in `site_renderer.py`'s docstrings rather than
  fabricated: (1) LocalBusiness schema omits address/geo/openingHours/logo-image -- intake
  collects none of those fields; (2) no FAQPage schema and no individual structured `Review`
  objects -- intake has no structured Q&A content and `testimonials` is a single free-text
  field with no author/date, so testimonials render as visible page copy only.
  **Verification (this sandbox, Python 3.10 -- CI/production run 3.12 per ADR-016; final
  confirmation still needs the founder's Mac venv):** full suite 183/183 passing plus the 20
  new tests (189 total minus 2 pre-existing, unrelated failures -- see note below); health
  check 9/9 HEALTHY.
  **Pre-existing, unrelated test-environment issue found, not fixed (out of scope for this
  task):** `tests/test_social_media_integration.py`'s `test_mount_endpoint_returns_mount` and
  `test_intent_endpoint_returns_pending_review` call `create_app()` with no `db_path`, so they
  write to the default relative `webstaffr.db` inside the repo folder instead of a tempfile
  like every other test file does -- that path hits `sqlite3.OperationalError: disk I/O error`
  specifically on this sandbox's mounted-folder filesystem (consistent with CLAUDE.md's Git
  Mechanics note that this mount has write restrictions). Confirmed via `git status` that
  neither this test file nor anything in its import chain was touched by this build. Worth a
  follow-up (give those two tests a tempfile db_path like the rest of the suite) but is a
  pre-existing hygiene gap, not something this task caused or should fix inline.
  **Sandbox mishap, self-inflicted, disclosed:** attempted a `git stash` from this sandbox to
  check whether test_social_media_integration.py's failure was pre-existing (a bad idea given
  CLAUDE.md's own warning that this sandbox can't write git objects for this mounted repo --
  should have just checked `git status` instead, which is what ultimately confirmed it). It
  failed and left a stale 0-byte `.git/index.lock` that this sandbox's shell cannot delete
  (permission denied on unlink, same mount restriction). No working-tree changes were lost --
  `git status` still reads clean and correct. **Founder action needed:** delete
  `.git/index.lock` next time you're on your Mac before running any git command there; it's
  an empty lock file, not a content change.
  **Not done, per plan's explicit scope:** no push/deploy (needs separate approval), no
  custom-domain resolution, no location-page generation beyond the service-area line, no ADR
  entry in `docs/DECISIONS.md` yet (add at push time), Site Weaver's Lovable project untouched.

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

- **In-repo customer site renderer: plan written and direction approved, build not started
  (2026-07-27).** Founder decision after repeated Lovable credit stalls: customer/tenant sites
  will be rendered server-side from this repo (Jinja2 templates over the existing
  `build_public_site_data()` projection, on the existing Vercel deployment, $0 incremental)
  instead of via Lovable's Site Weaver project, which stays untouched as fallback. Full plan
  incl. routes, template/SEO design, build sequence, test gates, rollout/rollback, and the
  approvals ledger: `docs/SITE_RENDERER_PLAN.md`. Jinja2 dependency approved as part of the
  same sign-off. Next action: execute the build sequence (each step keeps the suite green);
  push/deploy still requires its own founder approval. ADR to be added to `docs/DECISIONS.md`
  at build completion. This resolves the "is Lovable the right tool" question raised earlier
  today for *customer sites*; the Agency Site (company marketing site) stays on Lovable.
- **Site Weaver SEO/ASO blueprint saved (2026-07-27).** Founder
  provided a full local-SEO spec (URL structure, on-page elements, schema markup, intake-to-content
  mapping, checklist) for Site Weaver's customer-site output -- founder direction: SEO/ASO are
  tantamount to the rest of the build, not an afterthought. Saved verbatim at
  `docs/SITE_WEAVER_SEO_BLUEPRINT.md` (this repo's scope is backend per `CLAUDE.md`; the actual
  markup/schema implementation belongs to whichever site-generation tool ends up building Site
  Weaver's pages). One flag added to the saved doc: its Review Schema example hardcodes a
  fabricated review/rating as boilerplate -- must be populated from real tenant data only (or
  omitted) per the no-fabrication invariant, same category of issue already found live on the
  Agency Site preview below. Implementation home decided same day: the in-repo site renderer
  (entry above), not Lovable -- the blueprint's page architecture, on-page elements, and schema
  markup are folded into `docs/SITE_RENDERER_PLAN.md`'s template design.
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
