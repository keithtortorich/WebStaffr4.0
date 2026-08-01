# Marketing Coordinator — Publishing API Options Addendum

**Status:** research + recommendation only. No implementation.  
**Date:** 2026-07-27  
**Parent plan:** `docs/MARKETING_COORDINATOR_PLAN.md`  
**Scope:** how a unified social publishing API can strengthen and expedite Phase 2 (organic execution) and feed Phase 3 measurement, without changing the strategy brain, approval gate, or WebStaffr/SMMM seam.

This addendum does not re-litigate the combination thesis (GTM skill + SMMM + WebStaffr). It only addresses the highest-risk, highest-effort piece of Phase 2: owning and maintaining native platform adapters.

---

## Why this matters for the plan

Phase 2 done-criteria today:

> Approved variants → schedule → publish via adapters → visible in calendar; trace on both sides; one approved post reaches a test platform account with a full trace.

SMMM already has:

- Approval state machine (structurally enforced)
- Post version history
- Calendar / scheduling
- Celery workers
- `execution_nodes` on both sides
- Nine platform adapters under `backend/app/social/platforms/` (facebook, instagram, linkedin, x, threads, tiktok, pinterest, youtube, google_business)

The adapters are the long-tail risk: OAuth, token refresh, media specs, rate limits, and platform policy changes per network. A unified publishing API collapses that surface into one client, one set of credentials, and vendor-maintained compliance.

**What a vendor must not own**

- Strategy / positioning / copy generation (GTM stages 1–3)
- Approval state machine or immutable post history
- WebStaffr intake, attribution, or client comms channel
- No-fabrication / never-leak rules
- Tenant/org identity models (mount remains the only binding)

Vendor receives only already-approved content and returns post IDs, status, and (ideally) analytics.

---

## D2 platform set (must cover)

From the parent plan (founder decision D2):

| Priority | Platforms |
|---|---|
| Core (launch) | Facebook, Instagram, LinkedIn, **Google Business Profile** |
| Available per-client | X, TikTok, Pinterest, Threads, YouTube |

Any recommended vendor must cover the core set, including Google Business Profile.

---

## Shortlist (researched 2026-07-27)

### Tier 1 — best fit for this architecture

| Vendor | Platforms (approx.) | Pricing model | Entry cost | Why it fits |
|---|---|---|---|---|
| **Upload-Post** | 12–22 (majors + GBP, Reddit, Discord, Telegram, etc.) | Free tier + low flat plans | Free (10 uploads/mo) → ~$16/mo | Purest publish + schedule + analytics API. Explicit GBP. Free tier for spikes. Does not push its own AI writer into the strategy path. Strong SDKs, webhooks, MCP. |
| **Zernio** (ex-Late) | 15 (majors + GBP, WhatsApp, Discord, Telegram, Snapchat, Reddit) | Pay-per-connected-account (graduated) | Free for first 2 accounts; then $6 → $3 → $1/account/mo | Widest coverage + full social layer (comments/DMs/ads). Strong MCP. Everything included. Watch per-account cost as client × platform count grows. |
| **Outstand** | 10–11 majors | Base + per-post | ~$19/mo incl. 3k posts, then ~$0.005–0.007/post; unlimited accounts | Clean usage-based pricing. Unlimited accounts. Good for early/spiky volume. Confirm GBP in spike. |

### Tier 2 — viable but secondary

| Vendor | Notes |
|---|---|
| **Blotato** | $29/mo flat, 9 platforms, strong AI content + MCP. Better if you also want their repurposing/visual engine later. Less ideal as a pure publish layer (strategy stays in GTM/SMMM). |
| **RobinReach** | Strong MCP + human calendar UX. More full social-management product than thin backend dependency. |
| **Ayrshare** | Most mature multi-tenant API (13+, includes GBP). Starts $149/mo per-profile. Only justified if Tier 1 fails reliability or multi-tenant needs. |
| **bundle.social** | Flat org plans, unlimited accounts, solid depth. Higher entry ($100/mo Pro) than Upload-Post/Outstand. |

### Explicitly out of scope for Phase 2 replacement

Native platform APIs (Meta Graph, TikTok Content Posting, LinkedIn, etc.) — they reintroduce the exact maintenance burden this addendum is trying to remove. Self-hosted open-source schedulers (e.g. Postiz self-host) partially defeat the purpose unless ops ownership is deliberately accepted.

---

## Platform coverage vs D2

| Platform | Upload-Post | Zernio | Outstand | Plan priority |
|---|---|---|---|---|
| Facebook | Yes | Yes | Yes | Core |
| Instagram | Yes | Yes | Yes | Core |
| LinkedIn | Yes | Yes | Yes | Core |
| Google Business Profile | Yes | Yes | Confirm in spike | Core |
| X | Yes | Yes | Yes | Optional |
| TikTok | Yes | Yes | Yes | Optional |
| Pinterest | Yes | Yes | Yes | Optional |
| Threads | Yes | Yes | Yes | Optional |
| YouTube | Yes | Yes | Yes | Optional |

---

## Evaluation scorecard

Score 0–5 after the spike. Weights reflect Marketing Coordinator priorities.

| Dimension (weight) | Upload-Post | Zernio | Outstand |
|---|---|---|---|
| Platform coverage for D2 set (20%) | | | |
| Publish + schedule reliability (20%) | | | |
| Analytics usable for Phase 3 (15%) | | | |
| Multi-tenant cost model (15%) | | | |
| Developer friction — API/SDK/MCP (10%) | | | |
| Google Business Profile support (10%) | | | |
| Ops / compliance burden transferred to vendor (10%) | | | |
| **Weighted total** | | | |

**Decision rule:** reject any vendor scoring < 3.5 on platform coverage or publish reliability. Then choose highest total that also clears founder dependency sign-off (CLAUDE.md security baseline).

---

## Spike checklist (1–2 days, throwaway accounts only)

1. Sign up (prefer free tier). Generate API key. Confirm no production credentials enter the repo or chat.
2. Connect test accounts for at least: Facebook Page, Instagram, LinkedIn, Google Business Profile. Optionally X + TikTok.
3. From a local script (or temporary SMMM Celery task):
   - Schedule a text + image post to ≥ 3 platforms.
   - Immediately publish to 1 platform.
   - Capture returned post IDs / status payloads.
4. Failure path: invalid media or disconnected account must return a clear error (never silent success).
5. Pull analytics for a live post. Record schema (views, likes, comments, reach, etc.).
6. Confirm webhook or reliable polling for publish completion — must be able to drive an `execution_nodes` update.
7. Cost projection: 10 Business Manager clients × avg 4 platforms × 12 posts/month.
8. Document: OAuth connect ownership (who hosts the redirect?), token storage model, rate-limit headers, any pressure to use vendor AI writing (reject if it would bypass no-fabrication rules).
9. Disconnect test accounts / delete test data. Fill scorecard.
10. Founder decision: proceed / reject / try next. **No production wiring until explicit sign-off.**

**Recommended spike order:** Upload-Post → Zernio → Outstand. Only then Ayrshare if the first three fail.

---

## Recommended integration shape

```
WebStaffr (tenant, intake, attribution, approval routing)
        │
        │  existing mount / intent bridge
        ▼
SMMM (campaigns, posts, ApprovalStateMachine, execution_nodes, Celery)
        │
        │  single Protocol client (feature-flagged)
        ▼
Vendor (Upload-Post / Zernio / Outstand / …)
        │
        └── publishes + returns post IDs / status / analytics
```

- Identity models stay separate (existing INTEGRATION_PLAN.md seam).
- Tenant/org scoping stays at the SMMM repository layer (known landmine — never look up publish work by primary key alone).
- Vendor credentials behind `Protocol` + `Null*` + `*NotConfiguredError` (same pattern as every other integration in both repos).
- Feature flag: `PUBLISH_BACKEND=native|vendor_x` so native adapters remain reversible until founder sign-off on permanent removal.

---

## Concrete task list — replace adapters with Vendor X

### Phase A — Thin client (no behavior change)

1. Add vendor package under SMMM (e.g. `backend/app/social/vendors/` or parallel to existing integrations).
2. Define `SocialPublisher(Protocol)` matching what current adapters already expose, e.g.:
   - `publish(post, platform_accounts, schedule_at=None) -> PublishResult`
   - `get_status(job_id) -> Status`
   - `get_analytics(post_ref) -> AnalyticsSnapshot` (Phase 3)
3. Implement `NullSocialPublisher` and `VendorXClient` (real client raises `*NotConfiguredError` when credentials absent).
4. Env: `VENDOR_X_API_KEY` (+ base URL if needed). Document; never commit.
5. Unit tests with mocked HTTP only. No live network calls in CI.

### Phase B — Wire into existing publish path

6. Locate current flow: `backend/app/workers/tasks/publish_tasks.py` + `backend/app/social/platforms/`.
7. Feature flag `PUBLISH_BACKEND=native|vendor_x`.
8. When `vendor_x`:
   - Map SMMM approved `Post` + version + platform accounts → vendor payload.
   - Call `VendorXClient.publish`.
   - Write `execution_nodes`: `publish_requested`, `publish_succeeded` / `publish_failed` (correct parentage, tenant/org scoped).
9. ApprovalStateMachine and post version history remain untouched — vendor only ever sees approved content.
10. Org/tenant scoping enforced at repository layer (binding landmine from HANDOFF.md).

### Phase C — Schedule, status, analytics

11. Map SMMM calendar/schedule entries to vendor schedule API **or** keep SMMM as scheduler and only hand “publish now” to the vendor (prefer the latter initially — less surface area).
12. Celery task or webhook handler: vendor status → update `execution_nodes` + `publish_job`.
13. Phase 3: pull analytics → normalize into existing analytics snapshot model (DB dedup constraint stays). Missing metrics marked explicitly “unavailable”, never invented.

### Phase D — Cleanup and gates

14. Success gate: one real tenant post has full trace (approve → schedule → live on ≥ 1 platform).
15. Native adapters for covered platforms remain in tree behind the flag until founder signs off on permanent deprecation.
16. Update landmines / HANDOFF notes: “publish path goes through Vendor X; org filter still mandatory.”
17. If vendor is usage-based (Outstand) or per-account (Zernio), add a simple per-tenant or per-run counter / alarm (addresses the parent plan’s “no cost ceiling on the AI layer” risk class).

### Explicitly out of scope for this replacement

- GTM strategy pipeline / intake mapper / research module / copy variants
- Approval workflow
- WebStaffr intake, attribution, two-way client comms (D4)
- Paid-ads platform APIs (Phase 4)
- Any path that lets the vendor invent social proof or emit never-leak fields

---

## Cost and multi-tenant notes

| Vendor | Early (≤ 5 clients, ~20 accounts) | Scale (20 clients × 4 platforms = 80 accounts) |
|---|---|---|
| Upload-Post | Free → low tens $/mo | Still modest flat plans |
| Zernio | Free → ~$100/mo range | Graduated; can climb if every client connects many platforms |
| Outstand | ~$19 + low per-post | Predictable if post volume is known; unlimited accounts |
| Ayrshare | $149+ | Per-profile; becomes expensive fast |

Projection at spike time is mandatory before founder sign-off. Prefer vendors whose cost does not scale linearly with “number of client platform connections” unless volume discounts are clear.

---

## Alignment with parent plan risks

| Parent-plan risk | How this addendum helps or interacts |
|---|---|
| Phase 1 before Phase 2 risk-ordering | Vendor publish path makes Phase 2 validation cheaper, supporting the already-noted option to stand Phase 2 up first with placeholder strategy content. |
| No cost ceiling | Usage- or account-based vendors require an explicit counter/alarm (task D.17). |
| Dead pipeline / trace desync | Vendor webhooks or status polling must write `execution_nodes`; reconciliation still required (parent risk remains). |
| Tenant/org scoping landmine | Unchanged — still enforced at SMMM repository layer. |
| Incomplete questionnaire | Unrelated; still needs an explicit decision in the parent plan. |

---

## Founder decisions required before any production wiring

1. **Approve spike** on Upload-Post (and optionally Zernio) using throwaway accounts only.
2. **New dependency sign-off** for the chosen vendor (CLAUDE.md security baseline — same bar as D1 SearXNG and D4 Twilio/Postmark).
3. **Confirm Google Business Profile** support is real and sufficient for the D2 launch set.
4. **Accept cost model** for projected Business Manager client count.
5. **Decide** whether SMMM remains the scheduler (preferred initially) or defers scheduling entirely to the vendor.

Until these clear, native adapters remain the only publish path. No Marketing Coordinator publish code changes production behavior.

---

## What this addendum deliberately does not do

- Does not implement anything.
- Does not choose the final vendor (spike + founder sign-off required).
- Does not alter Phase 0–4 sequencing beyond making Phase 2 cheaper to validate.
- Does not merge identity models or move strategy into the vendor.
- Does not relax no-fabrication, never-leak, or approval-gate rules.

---

## Sources (research snapshot 2026-07-27)

Primary: product sites and docs for Upload-Post, Zernio, Outstand, Blotato, RobinReach, Ayrshare, bundle.social.  
Secondary: independent 2026 comparisons (platform counts, pricing models, MCP presence).  
Figures and platform lists should be re-verified at spike time — the category moves quickly.

---

*End of addendum. Carry forward into `docs/` alongside `MARKETING_COORDINATOR_PLAN.md`. Update parent plan’s Phase 2 sequencing note and risk review only after a vendor is signed off and the first end-to-end publish trace succeeds.*
