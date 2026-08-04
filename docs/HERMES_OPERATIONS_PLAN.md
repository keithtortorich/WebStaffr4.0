# Hermes Autonomous Operations Plan

**Status:** Proposed for founder approval before execution
**Date:** 2026-08-04
**Depth:** D3, multi-session operations/automation architecture
**Owner:** Hermes executes; Codex approves anything touching production code or infra; Claude approves customer-facing behavior.

## Why this doc exists

The "three-agent execution split" doc (`menage a trois.md`, Desktop) assigns Hermes an autonomous-operations role: converting procedures into skills, running account provisioning, continuous monitoring, QA at scale, monthly optimization reports, and continuous learning. No matching in-repo plan existed before today. This scopes it against what actually exists, so Hermes isn't asked to operate infrastructure that isn't built yet.

## Verified current state (checked before writing this)

- **No production monitoring exists yet.** `health_check.py` is a 9-check suite run manually/on-demand (per TASKS.md health check log, latest run 2026-08-01). There is no scheduled/automatic execution, no alerting, no uptime checks. Hermes's Phase 3 (continuous monitoring) has nothing to plug into until Codex's plan (`CODEX_SECURITY_EXECUTION_PLAN.md` Batch 5 — "reliability foundation and production operations," monitoring/alerts/uptime) ships. **Hermes's monitoring phase is sequenced behind Codex Batch 5, not parallel to it.**
- **CI is not authoritative yet.** TASKS.md and Codex's plan both confirm: one GitHub Actions workflow exists, runs pytest, but lacks lint/type/secret-scan/dependency-scan and does not block deployment. Hermes's "post-deployment smoke tests" and "safe rollback procedures" (source doc Phase 5) depend on Codex's Batch 4 (authoritative CI/deployment gate) existing first.
- **The onboarding smoketest skill that already exists is stale.** TASKS.md 2026-08-04: `webstaffr-onboarding-smoketest`'s `scripts/smoketest.py` checks for WS3.3's `backend/main.py` layout, doesn't recognize WS4.0's `webstaffr/app.py`. A workaround was run manually (TestClient → POST /intake → GET /sites/{tenant}/web, passed). **This is the closest existing thing to Hermes's Phase 2 (account provisioning checks) — it needs a repo-detection fix before Hermes can rely on it, not a from-scratch replacement.**
- **No customer accounts exist yet to provision or monitor.** Angel is built but MVP has not shipped to a real paying tenant (per `AGENT_TEAM_PLAN.md` Phase 0: "Angel end-to-end live for a real tenant" is still the exit condition, gated on GHL/Retell paid credentials — a founder decision tracked as pending). Hermes's Phase 2 (account provisioning) and Phase 5 (monthly optimization) have no real accounts to run against until then.
- **No skills registry for Hermes-authored procedures exists in this repo.** The skills referenced in CLAUDE.md and this session (webstaffr-analyze, webstaffr-go, etc.) live in the plugin/skill directory, not as versioned artifacts Hermes itself authors and updates. Phase 1 (convert procedures into reusable skills) needs a decision on where those live and how they're versioned before Hermes starts writing them.

## Execution sequence

### Phase 0: Sequencing gate (new — not in the source doc, added because of what's verified above)

Hermes cannot productively start Phases 2-5 of the source doc until:
1. MVP ships to at least one real tenant (Angel live end-to-end) — founder-gated on paid vendor credentials.
2. Codex's Batch 4 (CI/deployment gate) and Batch 5 (monitoring/alerting/rollback) exist to operate.

What Hermes *can* start now, independent of those gates:

### Phase 1: Convert existing procedures into reusable skills (can start now)

Start with what's already been done manually and is repeatable, rather than the full 16-item list in the source doc:
- Fix and adopt the onboarding smoketest (repo-detection fix for `webstaffr/app.py`, per the logged TASKS.md gap) as the first real Hermes skill.
- Formalize the 5-skill site audit pattern already run manually 2026-08-01 (design-critique, accessibility-review, design-system, governance-linter, research-synthesis) into a repeatable Hermes procedure.
- Each skill follows the source doc's required shape (trigger, inputs, steps, guardrails, success conditions, recovery steps, escalation conditions, structured output, version, metrics) — this shape is sound and adopted as-is.

Remaining skills in the source doc's Phase 1 list (Retell testing, GHL sync testing, Stripe webhook testing, domain/SSL verification, incident escalation, monthly optimization, data export, cancellation) are written as skills only once there's a real integration or account to test against — writing them earlier means testing against nothing, which produces false-positive "passing" skills.

### Phase 2: Account provisioning (blocked on Phase 0 gate)

Adopt the source doc's 15-step provisioning checklist as-is once there's a real tenant flow to run it against. No changes needed to the checklist itself — it's sound and matches the repo's actual intake → site → Angel → GHL flow.

### Phase 3: Continuous monitoring (blocked on Codex Batch 5)

Adopt the source doc's monitoring list and autonomy boundaries (may retry/diagnose/escalate; may not spend money, change schemas, deploy unreviewed code, issue refunds) as-is — the boundaries are correctly conservative and don't need founder revision. Implementation blocked on Codex building the monitoring hooks Hermes would read from.

### Phase 4: QA at scale (blocked on Phase 0 gate — needs real transcripts/traffic)

Adopt as-is once real call/chat volume exists to sample from.

### Phase 5: Monthly optimization (blocked on Phase 0 gate — needs real accounts)

Adopt as-is; source doc's ownership split (Claude approves customer-facing recommendations, Codex implements code changes) matches the ownership table already in `menage a trois.md` and is correct.

### Phase 6: Continuous learning (starts naturally once Phase 1 skills exist)

Adopt as-is — this is a process discipline (record trigger/cause/resolution, update skill draft, add regression scenario, route defects to Codex or Claude) that applies as soon as any Hermes skill exists and fails once.

## Completion standard

This plan is complete when Phase 1's two starter skills (fixed onboarding smoketest, formalized site-audit procedure) exist, are versioned, and have run successfully at least once. Phases 2-5 remain blocked and logged as blocked — not attempted — until their stated gates clear.

## What this plan does not do

- Does not stand up monitoring, alerting, or CI gating itself — that's Codex's Batch 4/5, this plan only sequences Hermes's dependency on it.
- Does not provision real customer accounts — none exist yet.
- Does not change the autonomy boundaries in the source doc (may/may not act autonomously) — those are adopted verbatim as sound.

## Required approval to begin

Approve Phase 1 only (the two starter skills). Phases 2-6 activate automatically once their stated gates (MVP live, Codex Batch 4/5 shipped) clear — no separate approval needed at that point, since the source doc's procedures are already reviewed and adopted here.
