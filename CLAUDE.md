# CLAUDE.md : WebStaffr 4.0 Operating Rules

## Why this repo exists
A clean rebuild of WebStaffr 3.3, carrying forward only the code that's actually proven and actually running -- the Angel AI-employee backend -- restructured around a real composition root instead of one buried inside a single worker's package. WS3.3 (and WS3.0 before it) stay intact on GitHub as archives; nothing was deleted, only left behind. See `docs/DECISIONS.md` for what changed and why.

## Founder's Role
Founder is not a coder. Do not assume technical background to evaluate implementation tradeoffs. When multiple sound approaches exist, pick the one that best fits this repo's architecture, maintainability, security, and simplicity : don't present options for the founder to choose between. Escalate only for: product vision, business priorities, budget, legal/compliance, vendor selection, or material cost/schedule impact. Otherwise, decide and act.

## MVP Scope
Full flow: intake → generated customer site → Angel widget embedded and working, plus live voice via Retell.
- Frontend/site generation: in-repo Jinja2 renderer (site_renderer.py). Customer sites render at `/sites/{tenant_id}/web`.
- This repo's scope: backend logic : Angel (voice, GHL, booking), tenant isolation, attribution, integration bridges (social media, workflow graph, ServiceTitan), tests.
- Out of scope until MVP ships: the other AI-employee roles (Marketing Coordinator -- see `docs/MARKETING_COORDINATOR_PLAN.md`), workflow builder UI, ops dashboard, billing/tier logic, ServiceTitan/Jobber sync going live (code exists, wiring it live is post-MVP).
- Brand/naming governance for all customer-facing and marketing surfaces (site copy, investor materials) is set by the founder's brand source docs, not by this repo. Company name is always **WebStaffr** (capital W, capital S) -- never "WebStaff" or other variants. Never say "AI" in customer-facing copy; no emojis in brand-facing assets. Check against the actual source doc before trusting any older cached ruleset -- see TASKS.md's 2026-07-27 entries for a case where a stale captured ruleset cited governance docs that don't exist in this repo. **Resolved 2026-07-30:** founder confirmed the Google Drive "Webstaffr4" folder's docs (WEBSTAFFR_GOVERNANCE.md, WebStaffr_Training_Manual_real, and siblings) are the newest canonical sources. WEBSTAFFR_GOVERNANCE.md is explicit and unconditional: no em-dashes anywhere in WebStaffr copy, internal or external, no exceptions. That supersedes the Brand Principles Handbook PDF's looser (no-ban) treatment wherever the two conflict. See `docs/DECISIONS.md` ADR-020.

## Process
Claude-only. No multi-agent coordination protocol, no ownership-header comments on files. Short, single-purpose turns. Decisions get made once, logged, executed : not re-litigated. One task per turn; side-issues discovered mid-task get logged in TASKS.md, not fixed inline, unless trivially in-path.

## Capability Check
Runs before every response, ahead of the scope call. Any sentence that starts "can you open", "go to", "run this in your terminal", "navigate to", "check the dashboard for", or "paste me the contents of" is a claim that no available tool reaches that thing. Verify the claim before writing the sentence : it is usually false, and the founder cannot catch the error from his side because he can't see which tools were available.

Ladder, stop at the first rung that works:
1. **A dedicated MCP for that exact service.** Supabase (project settings, connection strings, keys, logs, SQL, advisors), Vercel (deployments, build logs, runtime logs, runtime errors), GitHub, Netlify, Drive. If unsure one exists, search the MCP registry before concluding it doesn't.
2. **Desktop Commander.** Real shell and real filesystem on the founder's Mac : file reads/writes anywhere, ripgrep at scale, git operations including the pushes a sandbox structurally cannot do, persistent shells, long-running processes, SSH. If the next thing you were going to type is a command for him to paste, run it here instead.
3. **Browser tools (Claude in Chrome).** Anything that would otherwise be "log into the dashboard and click around" : Vercel logs, Supabase settings, GitHub, GHL, Retell, Netlify. Uses his real logged-in session.
4. **Computer use.** Native macOS apps and cross-app work nothing else reaches. Fallback, not a first move.
5. **The sandbox shell.** Isolated compute that doesn't touch his machine.

Only after all five come up empty is asking him legitimate : credentials only he holds, an OAuth flow, a paid action, a session nothing is logged into. When you do ask, give the exact command or click path in one move, say what you'll do with the result, and if a connectable tool would remove the ask entirely, name it in one line.

An approval gate is about authority, not mechanics. "Ready to push?" is a legitimate ask. "Can you run git push for me" is not : Desktop Commander does it the moment he says yes.

**Local-empty is not empty, and check the mounted folder first.** A filesystem search that finds nothing means the thing isn't where you looked, not that it doesn't exist. Before searching at all, check the folder already mounted into the session and the file already in context : that is where the current repo usually is. See ADR-019.

## Self-Approval Scope
Self-approvable, no need to ask: any reversible local-only change (code edits, tests, docs, refactors), improvements following best practices (auth, rate limits, error handling, security scoping), anything that keeps tests passing and health check HEALTHY.

Requires explicit founder approval first: git push or any deploy, new dependency (package or SaaS vendor), architecture/data-model/DB schema changes, anything touching credentials/secrets/production systems/Vercel/Supabase, high-ambiguity decisions with material cost or live-behavior impact.

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
- Third-party claims (vendor docs): verify independently before trusting a "fixed" report.
- Subagents: on by default for work that is parallel, broad-and-searchable, fresh-eyes review (an agent that didn't write the diff reviews it better), or long and grinding. Spawn and report what was delegated; don't ask permission each time. Supersedes the earlier "no subagents unless asked" rule, per the founder's 2026-07-28 direction. Don't delegate work needing the full conversation thread, single-file work, or anything with an approval gate mid-task : a subagent can't wait for a yes.

## CLAUDE.md Hygiene
TASKS.md is the single source of truth for live status. This file records durable rules and invariants only -- no session addenda accumulate here; when a decision is made, it goes in `docs/DECISIONS.md` as a dated ADR instead.

## Security Baseline
- No secrets, credentials, or tokens committed at any point, including comments, examples, or fixtures.
- No new dependency (package or vendor) added without explicit approval tied to that specific choice.

## Git Mechanics
This sandbox's shell cannot write git objects for a repo mounted this way : commit/push via Desktop Commander on the founder's actual Mac. Stage specific files only, never `git add -A`.
