# PRODUCT_LOCK.md — NetBuild.Pro Locked Product Definition

**Status:** Founder-approved 2026-08-04
**Depth:** D3 output (product/UX plan Phase 1)
**Supersedes:** Nothing — this is the first doc to state ICP, trades, and fair-use in one place.
**Cited by:** `docs/CLAUDE_PRODUCT_UX_PLAN.md` Phases 2-6. Do not re-decide any item below in a later doc — cite this one.

## Flagship product

NetBuild.Pro installs and manages a contractor's website, AI receptionist, booking, lead follow-up, reviews, and performance reporting.

## Ideal customer profile

Small team, 2-15 employees. Has some admin/dispatch capacity already, but no dedicated after-hours or overflow call handling — that gap is what Angel fills. Not a solo operator (too price-sensitive, no existing process to plug into) and not an established business with 15+ employees and its own office staff (NetBuild.Pro augments, doesn't replace, existing admin at that size — different sales motion, out of scope for current copy/onboarding).

## Supported trades

**No hard trade restriction in the product.** `webstaffr/intake.py`'s `industry` field is free text, not a constrained enum — the architecture is trade-agnostic by design. Confirmed proven, not just theoretical, on two trades: HVAC and plumbing (both have dedicated demo templates in the repo — `demo-templates/01-hvac-desert-cooling.html`, `demo-templates/02-plumbing-rivera.html`). No other trade has been built out or demoed.

**How to talk about this honestly:** Site copy and sales materials should not claim NetBuild.Pro is built specifically for any one trade, and should not claim broad multi-trade proof it doesn't have yet. Safe framing: "built for home-service businesses" (trade-agnostic claim, true), with HVAC and plumbing as the concrete, demonstrable examples when specificity helps (case studies, demo links). Do not name electrical, roofing, or general contracting as supported until a demo or live tenant exists in that trade — nothing in the repo backs that claim today.

## Included services (per flagship product line)

- Managed website (site_renderer.py, Jinja2-rendered, per-tenant)
- AI receptionist — chat + voice (Angel: Retell voice, GHL integration, booking)
- Lead qualification and booking
- Missed-call text-back and follow-up
- Review requests
- CRM and calendar integration
- Performance dashboard (spec-only as of this doc — see `CLAUDE_PRODUCT_UX_PLAN.md` Phase 3; not yet built)
- Monthly optimization pass

## Excluded services (out of scope until MVP ships, per CLAUDE.md)

- Other AI-employee roles beyond Angel/Sam/Rita/Leo (Reputation Manager, Marketing Coordinator, Growth Manager, Front Office Manager — proposed in `AGENT_TEAM_PLAN.md`, none built)
- Workflow builder UI
- Ops dashboard
- Billing/tier logic enforcement
- Live ServiceTitan/Jobber sync (code exists, not wired live)

**Copy rule:** No product copy, onboarding screen, or sales material may describe an excluded/unbuilt capability as available. This is a restatement of the no-fabrication rule already in `CLAUDE.md` and `NETBUILD_GOVERNANCE.md` — not a new rule, just scoped to this list.

## Fair-use boundaries

Two categories apply caps; nothing else does yet:

1. **Call/conversation volume caps per tier.** Each tier (Essentials/Pro/Growth) has a monthly call-and-chat volume ceiling before overage pricing or an upgrade prompt applies. **Open:** exact numeric caps per tier are not yet set — that's a pricing-model detail, not a product-scope one, and belongs in Phase 6 (Offer and sales materials) working against ADR-026's tier table, not in this doc.
2. **Site/content update frequency limits.** Monthly optimization pass is included per tier. On-demand major site rebuilds, off-cycle redesigns, or ad hoc content overhauls beyond the monthly pass are not included — treated as a scoped add-on or out-of-cycle request, not unlimited-included work.

No caps apply to anything else (e.g., number of leads booked, number of reviews requested) — those scale with the customer's own business volume and are the value being sold, not a cost to be limited.

## Tier reference (do not restate elsewhere — cite ADR-026)

| Tier | Price | Old name (retired) |
|---|---|---|
| Essentials | $497/mo | Office Staff |
| Pro | $2,497/mo | Business Manager |
| Growth | $5,000+/mo custom | White-Glove |

## Brand name reference (do not restate elsewhere — cite ADR-025)

NetBuild.Pro is canonical everywhere customer-facing, in all docs, and in all internal references going forward. The Python package name `webstaffr` and internal code identifiers are the one exception — not customer-visible, not renamed, no product value in touching it.

## What this doc does not do

- Does not set numeric call/conversation caps per tier — Phase 6's job, working against real usage data once available.
- Does not claim any trade beyond HVAC/plumbing is supported — correct this doc, not the copy, if a new trade gets a real demo or live tenant.
- Does not unblock Phases 2-6 automatically — each still gets its own founder review per `CLAUDE_PRODUCT_UX_PLAN.md`'s "Required approval to begin" section. This doc closes Phase 1 only.
