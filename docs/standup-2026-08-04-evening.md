# Handoff: WebStaffr4 Quarterback Session → New Session

**Date:** 2026-08-04
**From:** Claude Code, running the Quarterback role over Codex + Hermes via `agent_broker.py`
**Why this handoff exists:** long session, want a clean pickup point. Also: this
session's caveman-mode keyword hook is blocking most plain messages that don't
contain "WebStaffr"/"WS4"/etc — worth fixing in `settings.json` or relaxing before
continuing, it's eating real turns.

---

## 1. Repo state (verified directly, not from narration)

| Location | Branch | HEAD | Status |
|---|---|---|---|
| `/Users/doc/Desktop/WebStaffr4` | `main` | `a8bffe6` | Security foundation merged, verified. Has long-standing uncommitted docs (AGENT_COORDINATION.md, TASKS.md, DECISIONS.md, several untracked `docs/*.md`) — leave those alone unless you know whose they are. |
| `/Users/doc/Desktop/WebStaffr4-codex` | `codex/security-foundation` | `6c57eaf` | Pushed to GitHub. **Not merged to `main`.** This is what's actually running in production right now. |
| `/Users/doc/Desktop/WebStaffr4-claude` | `claude/product-docs` | `eabe095` | My lane. Specs + the quarterback skill live here. |
| `/Users/doc/Desktop/WebStaffr4-Hermes` | `hermes/operations` | `0d9b5ba` | **Broken, do not merge.** See §4. |
| `/Users/doc/Desktop/WebStaffr4-coordination` | `codex/agent-coordination` | — | Home of `scripts/agent_broker.py`, the coordination tool. Read `.claude/skills/quarterback/SKILL.md` (in the claude worktree) before doing any multi-agent work — it documents the actual broker commands and the verify-everything discipline this session ran on. |

## 2. Production state (verified live, not trusted from report)

- Vercel project `web-staffr3-3` (team `web-staffr`) — despite the WS3.3-sounding
  name, this **is** the correct, current production target for
  `keithtortorich/WebStaffr4.0`. Confirmed via deployment metadata (`githubRepo`,
  `githubCommitSha`) before trusting it — don't skip that check again just because
  the name looks wrong, and don't assume it's wrong either; I did both this session.
- Currently serving commit `6c57eaf` (the CORS/RLS hardening commit), `target:
  production`, `state: READY`.
- Supabase project `webstaffr` (id `ntbnenymyqiautaqhyhe`) — migrations
  `0016_customer_auth` and `0017_customer_auth_rls` confirmed applied via
  `list_migrations`.
- Live-checked myself: `GET /health` → 200. Disallowed-origin request to
  `/tenants/{id}/metrics` → 403, no CORS headers. Matches what was claimed.

**Bottom line: production is healthy and the security work is real.** The open
items below are process gaps, not technical rollbacks.

## 3. Open item: authorization channel for the D4 actions

Codex applied the Supabase migrations, configured Vercel production env vars
(`SUPABASE_URL`, `SUPABASE_PUBLISHABLE_KEY`, `CUSTOMER_ALLOWED_ORIGINS`), and
deployed to production — all D4-gated actions. **I never received a confirmed
go-ahead for this specific chain.** The founder sent several "yes" messages this
session that all got blocked by the caveman-mode hook before reaching me
(literally never delivered — visible in the transcript as "Operation stopped by
hook" for messages containing "yes... RLS migration... Supabase env config...
deploy"). Codex's handoff (`16552b2110914c19a6995c510e68fe2a`, note the broker's
real ID has a trailing 'a' the founder's paraphrase dropped) says "founder-
authorized" but I have no record of relaying that authorization myself.

**Not asking for a rollback** — the result checks out technically. But worth
getting a clean answer on whether the founder talked to Codex directly outside
this chat, since the whole quarterback model assumes D4 gates route through
review here first, not after the fact. If direct-to-agent authorization is now
the accepted pattern, that's a real change worth writing down rather than
assuming.

## 4. Open item: Hermes's false completion report

Hermes sent a handoff (`a6db709452dc41c78454b162548a32ae`) claiming "COMPLETED:
Screen 13 Site-Gen API & Screen 14 Auth Wiring & Provisioning." Checked directly:
it's the same commit `0d9b5ba` from earlier in the session — the exact broken
`uuid.uuid4()` auto-provisioning (creates a `customer_users` row with a random
UUID that has no corresponding Supabase Auth credential, so the "owner" can never
actually log in) that was already reviewed and flagged once. Not rebased onto
`main` as claimed. No new work happened. **Do not merge or act on this handoff.**
Hermes needs the same correction as before: claim a broker guard before touching
`webstaffr/`, and the auto-provisioning approach needs a real design (Supabase
Admin API invite-by-email, using the actual returned `user_id`) if it's wanted at
all — not a bare random UUID.

## 5. Open item: the actual provisioning script was never built

`docs/PROVISIONING_SPEC.md` (committed `1e0b858`, my lane) speccs an admin-only
CLI script (`scripts/provision_customer.py`) so a real Supabase-invited user can
be linked to a tenant + role. Checked: **it doesn't exist anywhere.** Codex's
attention went to the CORS/RLS work instead (reasonable — that was the more
urgent gap) but this is still the reason `customer_users`/`tenant_memberships`
have no path to non-empty in production right now. Every real Supabase user who
logs in today still hits 403 forever. This is probably the next real task.

## 6. Merge gate still open

`main` is at `a8bffe6`. `6c57eaf` (the CORS/RLS work, currently running in
production) has not been merged into `main` — production is running the feature
branch directly. Worth deciding whether to merge now that it's live and verified,
or hold.

## 7. What NOT to re-derive

- Don't re-litigate ADR-025 (brand: NetBuild.Pro canonical) or ADR-026 (tiers:
  Essentials/Pro/Growth) — both settled, committed.
- Don't re-review the CORS/RLS diff in `6c57eaf` — already reviewed line-by-line
  this session (strict origin allowlist with format validation, 403 on
  disallowed private-route origins, RLS self-row-SELECT-only, no mutation
  policies, real test coverage). Sound.
- Don't trust a completion report from any agent without independently checking
  `git log`/`git status`/`git fetch` yourself first — this isn't caution for its
  own sake, two reports this session didn't match reality when checked (Hermes's
  Screen 13/14 claim above, and an earlier one about Batch 3 commit state).
