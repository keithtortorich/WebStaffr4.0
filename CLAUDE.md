# CLAUDE.md : WebStaffr 4.0 Operating Rules

## Why this repo exists
A clean rebuild of WebStaffr 3.3, carrying forward only the code that's actually proven and actually running -- the Angel AI-employee backend -- restructured around a real composition root instead of one buried inside a single worker's package. WS3.3 (and WS3.0 before it) stay intact on GitHub as archives; nothing was deleted, only left behind. See `docs/DECISIONS.md` for what changed and why.

## Founder's Role
Founder is not a coder. Do not assume technical background to evaluate implementation tradeoffs. When multiple sound approaches exist, pick the one that best fits this repo's architecture, maintainability, security, and simplicity : don't present options for the founder to choose between. Escalate only for: product vision, business priorities, budget, legal/compliance, vendor selection, or material cost/schedule impact. Otherwise, decide and act.

## MVP Scope
Full flow: intake → generated customer site → Angel widget embedded and working, plus live voice via Retell.
- Frontend/site generation: delegated to Lovable (MCP). Iterate customer sites there, not token-by-token here.
- This repo's scope: backend logic : Angel (voice, GHL, booking), tenant isolation, attribution, integration bridges (social media, workflow graph, ServiceTitan), tests.
- Out of scope until MVP ships: the other AI-employee roles (Marketing Coordinator -- see `docs/MARKETING_COORDINATOR_PLAN.md`), workflow builder UI, ops dashboard, billing/tier logic, ServiceTitan/Jobber sync going live (code exists, wiring it live is post-MVP).

## Process
Claude-only. No multi-agent coordination protocol, no ownership-header comments on files. Short, single-purpose turns. Decisions get made once, logged, executed : not re-litigated. One task per turn; side-issues discovered mid-task get logged in TASKS.md, not fixed inline, unless trivially in-path.

## Self-Approval Scope
Self-approvable, no need to ask: any reversible local-only change (code edits, tests, docs, refactors), improvements following best practices (auth, rate limits, error handling, security scoping), anything that keeps tests passing and health check HEALTHY.

Requires explicit founder approval first: git push or any deploy, new dependency (package or SaaS vendor), architecture/data-model/DB schema changes, anything touching credentials/secrets/production systems/Lovable/Vercel/Supabase, high-ambiguity decisions with material cost or live-behavior impact.

When acting: summarize clearly, e.g. "Completed X. Tests: N/N passing. Health: HEALTHY. Ready for push?"

## Engineering Invariants
- Persistence: raw SQL via `webstaffr/db.py`'s `get_connection()`, `?` placeholders, `DB_ERRORS` for error wrapping. No ORM, ever. `migrate()` is a no-op under Postgres : schema is managed in Supabase out-of-band via `webstaffr/migrations/postgres_manual/`.
- Integrations: `Protocol` interface + `Null*` safe default + real implementation raising a `*NotConfiguredError` at construction when credentials are absent. Dependencies injected via constructor.
- Every query is tenant-scoped. `tenant_id` is public, never treated as a credential.
- CORS is per-path: browser-facing routes only (`/chat`, `/intake*`, `/sites/*`, `/tenants/*`). Server-to-server routes (`/book`, `/webhooks/ghl`, `/retell/*`, `/integrations/*`, `/workflow-graph/*`) carry no CORS headers.
- Hosting is Vercel serverless : nothing may assume a persistent process or a held-open connection.
- No fabrication: never generate placeholder ratings, reviews, testimonials, or credentials. Omit missing sections rather than inventing filler. Any change to the public site-data projection (`site_data.py`) re-checks the never-leak list (internal-only fields: `lead_routing`, `approver`, `competitors`, `license_number`).
- Secrets: never asked for in chat. Set via Vercel env var (Sensitive) or a gitignored `.env`, verified with a pass/fail script that never echoes the value. New env var → update `CREDENTIALS.md` and `README.md` both.
- Composition root: `webstaffr/app.py`'s `create_app()` is the one place that assembles the FastAPI app. A new AI-employee worker adds its own router there, as a sibling to Angel's -- never nested inside `workers/angel/`.

## Token-Efficiency Rules
- Orientation: read TASKS.md only. Full doc set only when reconciling.
- Tests: run on code changes, skip on doc-only commits.
- Diffs: `git diff --stat` first, deep-read only implicated files.
- Third-party claims (Lovable agent, vendor docs): verify independently before trusting a "fixed" report.
- No subagents unless the founder asks for one.

## CLAUDE.md Hygiene
TASKS.md is the single source of truth for live status. This file records durable rules and invariants only -- no session addenda accumulate here; when a decision is made, it goes in `docs/DECISIONS.md` as a dated ADR instead.

## Security Baseline
- No secrets, credentials, or tokens committed at any point, including comments, examples, or fixtures.
- No new dependency (package or vendor) added without explicit approval tied to that specific choice.

## Git Mechanics
This sandbox's shell cannot write git objects for a repo mounted this way : commit/push via Desktop Commander on the founder's actual Mac. Stage specific files only, never `git add -A`.
