# DECISIONS.md

Architectural decisions actually made in this codebase's history, with
real reasoning and real consequences -- not a hypothetical ADR template.
ADR-001 through ADR-011 carry forward from WS3.3 because the decisions
and their reasoning still apply to this repo's code. ADR-012 onward cover
the WebStaffr 4.0 rebuild itself.

New decisions belong at the bottom, dated, in the same format. Don't
rewrite history here -- if a decision is later reversed, add a new entry
that says so and link back to the one it reverses.

---

## ADR-001: Raw SQL over an ORM

**Decision**: Every repository and route handler is written against a
`sqlite3.Connection`-shaped interface using raw SQL (`?` placeholders),
with a hand-written translation shim (`db.py`) making the identical SQL
text work against Postgres too. No SQLAlchemy, no ORM, anywhere.

**Why**: An ORM would need its own dialect-abstraction layer anyway to
support both SQLite (dev/test) and Postgres (production) -- writing the
translation shim once, by hand, in one file (`db.py`), is simpler than
adopting a general-purpose ORM and configuring it for the same
dual-backend requirement.

**Consequences**: SQL is visible and auditable at every call site, at the
cost of writing dialect-aware code by hand instead of relying on a
library to handle it. `db.py`'s shim is deliberately narrow -- it
translates only the specific SQL patterns this codebase actually uses
(`INSERT OR IGNORE`, `PRAGMA`, `RETURNING`-injection for lastrowid
emulation), not general SQLite-to-Postgres translation. Adding a new
query pattern that needs dialect translation means updating `db.py`, not
just writing the query.

## ADR-002: Protocol + Null-object + real-implementation for every integration

**Decision**: Every external dependency (voice/AI backend, CRM, webhook
signature verification, shared-secret auth) is defined as a `Protocol`,
with a `Null*` implementation that's always safe to construct and a real
implementation that raises a `*NotConfiguredError` at construction time
if credentials are missing.

**Why**: The app needs to run safely with zero credentials configured --
for local dev, for CI, and for any tenant that hasn't been fully set up
yet. A pattern where "missing credential" means "silent no-op" or
"fabricated success" was rejected in favor of one where it means either
"safe, deterministic default behavior" (the Null object) or "loud failure
at startup" (the real implementation refusing to construct) -- never a
silent partial failure discovered later at request time.

**Consequences**: Adding a new integration means adding all three parts,
not just a client class. Tests exercise the real implementation's logic
by passing an explicit fake credential and mocking only the actual
network call -- no test in this suite makes a real network call, and none
are conditionally skipped based on whether real credentials are present
in the environment.

## ADR-003: `tenant_id` is public, never a credential

**Decision**: `tenant_id` appears in URLs (`/sites/{tenant_id}`,
`/tenants/{tenant_id}/...`) and is treated as a public routing identifier,
never as proof of authorization on its own.

**Why**: `/book` and `/webhooks/ghl` originally had no authentication
beyond accepting whatever `tenant_id` was passed in the request -- a
guessable or enumerable `tenant_id` would let anyone book appointments or
trigger webhook handling for any tenant. Fixed by adding shared-secret
auth (`X-API-Key` / `X-Webhook-Secret` headers) on top, without ever
making `tenant_id` itself secret -- the fix was "add a real credential,"
not "make the identifier harder to guess."

**Consequences**: Any new endpoint that accepts a `tenant_id` and
performs a write or exposes non-public data must be evaluated for whether
it needs its own auth, the same way `/book` and `/webhooks/ghl` needed it
added after the fact. `attribution_router.py`'s write path avoided this
problem entirely by not exposing a public write endpoint in the first
place (see ADR-007).

## ADR-004: CORS is scoped per-path, not app-wide

**Decision**: A custom `ScopedCORSMiddleware` adds CORS headers only to
browser-facing routes (`/chat`, `/intake*`, `/sites/*`, `/tenants/*`).
Server-to-server routes (`/book`, `/webhooks/ghl`, `/retell/*`,
`/integrations/*`, `/workflow-graph/*`) carry no CORS headers at all.

**Why**: FastAPI's built-in `CORSMiddleware` with `allow_origins=["*"]`
applied app-wide would mean `/book` and `/webhooks/ghl`, not just the
intentionally-public `/chat`, were callable cross-origin from any
website -- broader than intended.

**Consequences**: Any new route needs an explicit decision about whether
it belongs in `_CORS_SCOPED_PATHS`/`_CORS_SCOPED_PREFIXES` (defined in
`webstaffr/app.py`) -- the default for a new route is *no* CORS headers,
which is safe-by-default for server-to-server endpoints but must be
deliberately added for anything a browser widget needs to call directly.

## ADR-005: No fabricated content, ever ("perfect-site principle")

**Decision**: The public site-data projection (`site_data.py`) omits a
field entirely when its underlying data is absent, rather than
substituting a placeholder, a default rating, a fake testimonial, or any
other invented content.

**Why**: A data-integrity standard that caught real bugs previously: a
lead-capture form silently posting to a dead route, and hardcoded fake
testimonials rendered on every generated customer site regardless of
whether the business actually had any. The principle -- never fabricate,
omit instead -- became a standing rule.

**Consequences**: Every change to `build_public_site_data()`'s field set
must re-check which fields are internal-only (see DATABASE.md's
`intake_submissions` table) -- getting this wrong is a privacy leak, not
just a display bug. `competitors` and `license_number` were both caught
leaking into the public response historically (see ADR-006).

## ADR-006: `license_number` removed from public site data

**Decision**: `license_number` is collected at intake (required field)
but never included in `GET /sites/{tenant_id}`'s response.

**Why**: A founder decision, not a technical necessity -- contractor
license numbers are a common trust signal on real trade-business
websites, but Supabase's own security advisor had already flagged the
`license_number` column as sensitive at the database layer. Given that
signal, the founder chose not to carry the exposure forward to the
application layer too, even though nothing technically required removing
it.

**Consequences**: If a future business need calls for showing license
numbers publicly again, that's a new founder decision to make explicitly,
not a default to silently restore.

## ADR-007: Attribution events are written in-process, not via a public endpoint

**Decision**: `call_events` rows are written only by code that already
holds an open, tenant-resolved database connection (`intake_router.py`,
`retell_router.py`) -- there is no `POST /events` or similar public
ingestion endpoint.

**Why**: Given this repo's own history with `/book` and `/webhooks/ghl`
needing shared-secret auth bolted on after the fact (ADR-003), the
attribution feature avoided repeating that pattern by not adding a new
unauthenticated write surface in the first place.

**Consequences**: Any future integration that wants to log a call event
from outside this codebase (e.g. a different telephony provider) needs a
real design decision about how it authenticates -- there is no existing
endpoint to simply reuse.

## ADR-008: Retell over native Grok Voice for telephony

**Decision**: Live phone-call voice is built on Retell AI (webhook +
function-call integration), not xAI's native Grok Voice Agent API, even
though Grok is already the vendor used for text chat.

**Why**: Native Grok Voice's SIP integration requires this application's
own backend to hold a live WebSocket connection open for the full
duration of every call -- incompatible with Vercel serverless hosting
without standing up a second, always-on service just for voice. Retell
hosts that persistent connection on its own infrastructure instead.
Retell was chosen over Vapi specifically because it bundles telephony (no
separate Twilio-style account needed) and has less operational overhead
for a small team.

**Consequences**: Any future voice-related decision needs to account for
the serverless hosting constraint first -- a vendor that requires a
persistent connection held by *this* backend is disqualified by
construction, not by preference.

## ADR-009: Rate limiting via a DB-backed fixed-window counter, not in-memory or Redis

**Decision**: `/chat` and `/webhooks/ghl` are rate-limited using a
counter table (`rate_limit_counters`) in the existing database, not an
in-process dict and not a dedicated cache/store like Redis or Upstash.

**Why**: Given the serverless hosting model, an in-memory counter would
only be enforced within a single warm function instance -- Vercel's
multiple and cold-started instances would each keep their own counter,
giving no real ceiling on total request volume in production. A
DB-backed counter is correctly shared across every instance without
introducing a new external vendor relationship. A fixed-window
(not sliding-window/token-bucket) algorithm was chosen for simplicity,
accepting that a client could send up to roughly 2x the nominal limit
right at a window boundary.

**Consequences**: The counter table has no automated pruning yet -- a
known, accepted gap, not an oversight.

## ADR-010: Lovable is the canonical frontend

**Decision**: Customer-site generation and the Angel widget embed happen
in a Lovable-hosted project ("Site Weaver"). This repo does not carry a
`frontend/` directory.

**Why**: Lovable already had the Angel widget embedded and verified
working end-to-end against real backend data. Maintaining a second,
locally-built frontend for the same MVP flow would have doubled the
maintenance surface for no product benefit.

**Consequences**: Any new customer-facing site UI work happens in the
Lovable project, not in this repo.

## ADR-011: Attribution was prioritized over an immediate vertical launch

**Decision**: Call-attribution/tracking infrastructure (`tracking_numbers`,
`call_events`, `attribution_router.py`) was built before an immediate
single-vertical launch push.

**Why**: A "pays for itself" money-back guarantee -- part of the intended
go-to-market pitch -- needs proof-of-performance data behind it before
the guarantee is made, not retrofitted after customers are already being
told about it.

**Consequences**: `estimated_value_usd` in the metrics response is
explicitly labeled a placeholder (`appointments_booked × $250`), not a
measured figure -- treat it as provisional until real conversion data
replaces the placeholder multiplier.

---

## ADR-012: WebStaffr 4.0 -- clean rebuild carrying only proven, running code

**Decision**: Rebuilt as a new repository rather than continuing to
restructure WS3.3 in place. WS3.3 (and WS3.0 before it) remain intact on
GitHub as archives -- nothing was deleted from them, only left out of the
new repo.

**Why**: WS3.3's tracked repo had grown to 517 files, 82% of which were
two merged-in reference folders (the prior `WebStaffr 3.0/` repo and the
separate `social-media-marketing-machine` product) unrelated to what this
repo actually runs. The real product was ~95 files / ~8.7k lines,
carrying real rot alongside it: an orphaned workflow engine nothing
called, duplicated dataclasses across two integration packages, a
501-line app factory buried inside one AI worker's own package, and
SQLite/Postgres migration drift with two tables that had no Postgres DDL
or RLS at all. A rebuild let all of this be addressed as one coherent
pass instead of a series of patches to a repo whose size made even
locating the actual product surface non-obvious.

**Consequences**: Every file in this repo was deliberately carried
forward, not defaulted into existence by history. New work that wants to
reuse something from the archive repos is a deliberate decision to bring
it over, not an assumption it's already here.

## ADR-013: Unused workflow engine left behind

**Decision**: `workflow.py`, `execution.py`, `executor.py`, `repository.py`
(a `Tenant`/`WorkflowDefinition`/`WorkflowExecutor` engine, plus their
dedicated tests) are not part of this repo.

**Why**: Verified before removal, not assumed: nothing in the live
product's HTTP surface ever constructed or ran a `WorkflowExecutor` --
the only callers were the engine's own tests and the previous
`health_check.py`. It was fully tested code with zero production callers,
carrying real maintenance weight (two `workflow_definitions`/
`execution_records` tables in every migration baseline, a hardcoded
Postgres-dialect special case in `db.py`) for a feature the app never
actually exercised.

**Consequences**: The engine is not gone, only not carried -- it remains
intact and tested in the WS3.3 archive repo, recoverable in full the day
a real feature needs multi-step workflow orchestration. `db.py`'s
Postgres shim also dropped `_LASTROWID_PK["execution_records"]` and the
`INSERT OR REPLACE INTO workflow_definitions` translation, since both
were dead code with the engine gone (verified via full-repo grep before
removal, and by the passing test suite after).

## ADR-014: Composition root moved to `webstaffr/app.py`

**Decision**: `create_app()` -- the FastAPI app factory, middleware, and
every router's wiring -- moved from `webstaffr/workers/angel/router.py`
into a new `webstaffr/app.py`. Angel's own endpoints (`/chat`, `/book`,
`/webhooks/ghl`) stay in `workers/angel/router.py`, now exposed as
`create_angel_router()`.

**Why**: With one AI-employee worker (Angel), a 501-line file doing both
"assemble the whole app" and "handle Angel's three endpoints" was
awkward but not actively harmful. With a second worker (Marketing
Coordinator) planned, that shape would have meant either editing Angel's
own module to add a second worker's router, or duplicating app-assembly
logic per worker -- neither is right. Splitting now, while there's only
one worker to migrate, is far cheaper than splitting later with two.

**Consequences**: A future worker adds its own `webstaffr/workers/<name>/`
package with its own `create_<name>_router()`, and `app.py` gains one new
`app.include_router(...)` line -- it never needs to touch another
worker's module. See `docs/ARCHITECTURE.md`'s composition-root section.

## ADR-015: Integration packages consolidated to one persistence layer each

**Decision**: `integrations/social_media/` keeps its `SocialMediaMount`/
`SocialMediaIntent` dataclasses in `client.py` only (`sync.py` imports
them rather than redefining). `integrations/workflow_graph/` collapsed
from three layers (`client.py` wrapping `sync.py`'s functions, plus a
`repository.py` wrapping the same four operations a second time) down to
one (`client.py`, functions and the `WorkflowGraphClient` wrapper
together); `sync.py` and `repository.py` were deleted.

**Why**: Both packages had accumulated duplicate dataclass definitions
and, in `workflow_graph`'s case, a third layer (`repository.py`) with no
caller other than its own tests. Neither served the "thin seam over the
real product" purpose the packages' own docstrings describe.

**Consequences**: `workflow_graph_router.py`'s import of `client.py`
didn't need to change at all -- it already imported the winning
definitions. `tests/test_workflow_graph.py` re-points its imports at
`client.py`; one test class (`TestInsertOrReplaceWorkflowDefinitionsRewrite`
in `test_db_pg_shim.py`) was removed along with ADR-013's dead code
rather than updated, since the SQL pattern it tested no longer exists
anywhere in this codebase.

## ADR-016: No `pyproject.toml`, `requirements.txt` is the sole dependency source

**Decision**: This repo has no `pyproject.toml` at all. `requirements.txt`
and `requirements-dev.txt` are the only place dependencies are declared;
`pytest.ini` covers test discovery config.

**Why**: A `pyproject.toml` with only a `[tool.vercel]`/`[tool.pytest]`
table was tried previously and failed Vercel's build -- `uv` requires a
full `[project]` table once `pyproject.toml` exists at all, and a full
`[project].dependencies` table duplicates `requirements.txt` as a second
source of truth. That duplication caused a real bug in the prior repo:
`pyproject.toml`'s pinned versions drifted out of sync with
`requirements.txt` (which is what Vercel and CI both actually installed
from), so the file everyone assumed was authoritative wasn't the one
actually governing the deployed app.

**Consequences**: Do not reintroduce `pyproject.toml`, even a minimal or
tool-only one -- it reintroduces exactly the failure mode this decision
closes. Dependency version bumps (e.g. via Dependabot) only need to touch
`requirements.txt`.

---

## ADR-017: Public lead-capture form posts to a mail draft, not to `/intake`

**Date**: 2026-07-28

**Decision**: The "Get Your Free Website" form on the landing page submits by
opening a prefilled mail draft to the public contact address, rather than
POSTing to a backend endpoint. This is explicitly interim.

**Why**: The form collects three fields. `/intake` requires twelve, two of
which (`lead_routing`, `approver`) are internal-only and on the never-leak
list, so they can never appear on a public form. There is therefore no
existing endpoint the form can legitimately post to. The alternatives were
each worse: building a new public `POST /leads` endpoint plus a table means a
schema change and new production surface for a page that CLAUDE.md already
delegates to Lovable and that is labelled placeholder HTML in the source, so
the code would be thrown away; and leaving the form as it was meant it kept
promising a website in 48 hours while silently discarding every submission,
which is worse than having no form.

**Consequences**: Mail-draft submission depends on the visitor having a mail
client configured, so some submissions will be lost. That is a known and
accepted downgrade from a real endpoint, and a large upgrade from the previous
behaviour of losing all of them. Replace this with a real POST once the public
intake contract is decided. That decision is the founder's: either the landing
form stays a short lead capture that hands off to a longer onboarding form, or
`/intake` grows a public subset with the internal fields set server-side.

---

## ADR-018: Subagents are on by default, amending CLAUDE.md's token-efficiency rule

**Date**: 2026-07-28

**Decision**: Claude evaluates on every task whether to delegate to a subagent,
and spawns one when the work fits, reporting the delegation rather than asking
permission first. This amends the CLAUDE.md rule "No subagents unless the
founder asks for one."

**Why**: Founder request, made explicitly this session. The original rule was
written as a token-efficiency measure, on the assumption that subagents are an
escalation. For wide work they are the opposite: parallel agents keep the main
context small, and a fresh agent that did not write the code is a materially
better reviewer than the one that did.

**Consequences**: Delegate for parallel work, broad searches, review by fresh
eyes, and long grinding tasks. Do not delegate when the task needs the full
conversation thread, when it is a single file, or when a founder approval gate
sits in the middle, since a subagent cannot wait for a yes. The judgement is
encoded in the `engineering-director` skill; if that skill is removed, this ADR
still governs.


---

## ADR-019: Capability Check runs before every response

**Date**: 2026-07-28

**Decision**: Before writing any instruction that sends the founder to a
terminal, a directory, or a dashboard, Claude works down a five-rung ladder
first : dedicated MCP for that service, Desktop Commander, browser tools,
computer use, sandbox shell. Only when all five come up empty is the ask
legitimate. The rule is now a section in CLAUDE.md so it loads on every
orientation pass, and is mirrored in `~/.claude/CLAUDE.md` and the
`engineering-director` skill.

**Why**: Founder request, made explicitly this session in response to being
repeatedly asked to do mechanical lookups by hand. The cost is asymmetric and
invisible to him: he can tell when a design is wrong, but he cannot tell that a
working tool was sitting there unused. Two concrete precedents. The WS3.3
`/sites/{tenant_id}` 503 investigation lost two sessions to retrieving
`DATABASE_URL` out of the Vercel UI while the Supabase MCP (keys, logs,
advisors, direct SQL) and Vercel MCP (runtime logs, runtime errors) were
connected the whole time. And in the session that produced this ADR, Claude ran
a filesystem search for "webstaffr4", got no hits, and reported that no 4.0
repo existed : while this repo was the mounted session folder and this very
CLAUDE.md was already in context. Both failures share a shape: concluding
absence from one narrow check.

**Consequences**: Two clauses carry most of the weight. An approval gate is
about authority, not mechanics : "ready to push?" is a legitimate ask, "run git
push for me" is not, because Desktop Commander does it on the yes. And
local-empty is not empty : check the mounted folder and the context already
loaded before searching, and check the remote before reporting that something
does not exist. Asking the founder to confirm what could be verified directly
is offloading, not diligence; a long manual workaround written out in prose is
a tell that the ladder was skipped.
