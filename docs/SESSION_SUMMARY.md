# Session Summary — 2026-08-04

(Note: this file previously held a 2026-08-03 summary, carried over when this
worktree was cut from the canonical repo today. That content is preserved in
TASKS.md's session history; this file follows the repo's per-session
convention of reflecting only the most recent session.)

## Completed

- **ADR-025:** NetBuild.Pro locked as sole canonical brand name everywhere; Python package name `webstaffr` frozen (not customer-facing, avoids import breakage).
- **ADR-026:** Essentials/Pro/Growth locked as canonical tier names, 1:1 mapped to retired pricing vocabulary — Essentials=Office Staff ($497), Pro=Business Manager ($2,497), Growth=White-Glove ($5,000+). ADR-024 amended: portal ships in **Pro** tier.
- Scoped two previously-unscoped agent lanes from the "three-agent execution split" doc (`~/Desktop/menage a trois.md`), both grounded in verified repo state, not aspiration:
  - `docs/CLAUDE_PRODUCT_UX_PLAN.md` — Phase 1 (lock the product) mostly resolved by ADR-025/026; one item still open (ICP, included/excluded services, supported trades, fair-use boundaries — founder input needed, not started).
  - `docs/HERMES_OPERATIONS_PLAN.md` — Phase 1 starter skills approved (fix stale onboarding-smoketest repo detection, formalize the 5-skill site-audit pattern); Phases 2-6 gated on MVP going live + Codex Batch 4/5.
- Reconciled Codex's `CODEX_SECURITY_EXECUTION_PLAN.md`; founder approved Batch 1 (fail-closed auth boundary) in Codex's isolated lane.
- **Caught and corrected a live lane violation:** Hermes was editing `webstaffr/landing_router.py`, inside Codex's declared ownership, while building its own git-coordination-safety skill. Founder directed Hermes to stop and hand off; Hermes confirmed and is holding. Wrote `docs/HERMES_SKILL_CORRECTION_2026-08-04.md` (not editing Hermes's skill file directly) flagging the skill's stale Claude-ownership entry and the deeper gap: preflight checks disk state, not lane ownership.
- Established Claude's own isolated worktree per Codex's addendum requirement: `/Users/doc/Desktop/WebStaffr4-claude`, branch `claude/product-docs`. Commits: `318dde8`, `ecc0c13`.

## Changed

- `docs/DECISIONS.md`: ADR-025, ADR-026 added; ADR-024 amended in place.
- `TASKS.md`: session log entries for brand lock, tier lock, Batch 1 approval, Hermes lane-violation catch.
- New: `docs/CLAUDE_PRODUCT_UX_PLAN.md`, `docs/HERMES_OPERATIONS_PLAN.md`, `docs/HERMES_SKILL_CORRECTION_2026-08-04.md`.
- Addendum appended to `~/Desktop/menage a trois.md` (source doc, untouched otherwise).

## Blockers

- **Claude Phase 1, item 4** (ICP, included/excluded services, supported trades, fair-use boundaries) — founder input required, not started.
- **Hermes** — holding on canonical-tree writes pending: (a) applying the ownership-table correction to its own skill file, (b) confirming `landing_router.py` final disposition with Codex.
- **Coordination broker** — founder proposed a shared real-time broker (heartbeat, file-ownership claims, atomic locking, stale-claim expiry, single preflight command, founder-readable status) to replace prose-based relay coordination. Codex requested explicit confirmation ("Approve the local coordination broker") — **not given in this session.** Observed via `git worktree list` at session end: Codex already created `/Users/doc/Desktop/WebStaffr4-coordination` on branch `codex/agent-coordination`, ahead of confirmed approval. Flag at next session start; don't treat as quietly approved.

## Next (priority order)

1. Confirm (or hold) approval for Codex's coordination-broker work — already started in an isolated lane, no push/deploy, but the explicit go-ahead wasn't given before it began.
2. Hermes applies its skill correction and closes out `landing_router.py` with Codex.
3. Founder input on Claude Phase 1 item 4 (ICP/services/trades/fair-use) to unblock Phase 2 (onboarding spec).
4. Once the broker exists: migrate coordination off prose/chat-relay onto whatever protocol it defines — all three lanes use the same commands, not separate interpretations.

## Decisions this session

- ADR-025, ADR-026 (founder D2, recorded in DECISIONS.md).
- Codex Batch 1 approved (founder D4, security fix, isolated lane).
- Claude worktree path/branch approved (founder D3) — confirmed as `claude/product-docs` when Codex proposed a different branch name (`product-ux`); kept the already-built, already-approved name.
- Hermes lane-violation resolution: stop, hand off, correct ownership table (founder directive, immediate).

## Assumptions to carry forward

- Canonical repo: `/Users/doc/Desktop/WebStaffr4`. Worktrees alongside it: `-claude` (mine), `-codex` (Codex's Batch 1), `-coordination` (Codex's broker work, unconfirmed).
- `AGENT_COORDINATION.md` + Codex's addendum + Hermes's git-coordination-safety skill are three separate, partially-overlapping coordination docs. No single authoritative source yet — the gap the proposed broker would close.
- Five files seen modified mid-session (`agency_router.py`, `SALES TOOL.html`, `landing_page_hormozi_voss.html`, two SKILL.md files) were reverted/discarded by end of session, origin never attributed. Closed as non-issue, not resolved-with-explanation.

## Files updated

`docs/DECISIONS.md`, `TASKS.md`, `docs/CLAUDE_PRODUCT_UX_PLAN.md`, `docs/HERMES_OPERATIONS_PLAN.md`, `docs/HERMES_SKILL_CORRECTION_2026-08-04.md`, `~/Desktop/menage a trois.md` (addendum only).
