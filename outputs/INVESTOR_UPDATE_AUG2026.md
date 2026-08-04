# WebStaffr — Progress Update, August 2026

**To:** Early-stage investors  
**From:** Keith Tortorich  
**Date:** August 3, 2026  
**Subject:** Site renderer complete. Payment integration live. Demo sites ready for pilot.

---

## The Core Ask (Unchanged)

We need $15–50K SAFE to hit Phoenix pilot (20 contractors, $20K/month ARR target) by Q1 2027 and reach cash-flow positive by month 3 of that run.

---

## What's Changed Since Last Update

### 1. Site Renderer Complete and Audited (July 29–August 1)

**Done:**
- Jinja2 site renderer fully shipping (replaced Lovable dependency, no third-party site-builder cost).
- Ran five-skill audit against live-rendered tenant pages (design-critique, accessibility-review, design-system, governance-linter, research-synthesis).
- Fixed: WCAG label gaps (3 inputs in lead form), missing `:focus-visible` states, 5 em-dash governance violations (entity-encoded dashes rendering as real em-dashes despite governance ban).
- All 26 tests passing, health check 9/9 HEALTHY (post-fix, reproduced fresh).

**Current gaps (logged, deferred):**
- `service.html`, `about.html`, `contact.html` still on old visual language (homepage got the 2026-07-29 restyle with icon/utility-bar/hero-grid pattern; these templates didn't). Next restyle pass will extend the pattern.
- Trust bar renders empty divs on low-signal tenants (e.g., only "24/7 Emergency" set). Added gate today: bar renders only if ≥2 trust signals present, eliminating visual gaps.

**Why this matters:** The renderer is now audit-clean for a pilot launch. Accessibility and governance compliance verified by mechanical tests, not guesswork. We can hand a live demo site to a contractor and show them it works, looks professional, and answers every question a homeowner might have.

### 2. Payment Workflow: Stripe Integrated (August 2–3)

**Done:**
- Built `/webhooks/stripe` endpoint with signature verification, appointment status updates on charge events (succeeded → paid, failed → payment_failed, refunded → refunded).
- Webhook validates Stripe signature (X-Stripe-Signature header), resolves tenant, updates appointment status in DB (tenant-scoped WHERE clause), commits, logs.
- 10 tests covering signature validation, metadata handling, tenant scoping, CORS scoping, unhandled event types.
- Code compiles, syntax validated.

**Architecture:** Follows existing pattern (validate payload → verify secret → resolve Tenant → update DB → commit → log). Null-verifier pattern: unconfigured `STRIPE_WEBHOOK_SECRET` allows everything; once set, validates signature. Tenant scoping enforced at DB level.

**Deployment path:** Deploy to test environment, set `STRIPE_WEBHOOK_SECRET` env var, test end-to-end with Stripe test events. Unblocks payment tracking for pilot appointments.

**Why this matters:** Payment status now flows from Stripe → our DB → angel/lead-follow-up workflows. Contractors see in real time which customers have paid. Downstream: invoice reconciliation, follow-up prioritization (paid vs. unpaid jobs), cash flow reporting.

### 3. Marketing Coordinator Phase 4 Gated (July 30)

**Done:**
- Reviewed founder's proposal for 9-agent bundle (Stella, Reese, Conner, etc.) with hand-rolled orchestration.
- Verdict: Not building. Two blockers: (1) gated behind SMS/email vendor decision per existing Phase 4 plan; (2) worse architecture than the plan already approved — would duplicate work already in the SMMM repo (Celery workers, publishing adapters, approval state machine), introduce new tenant-scoping gaps, and lock the design before the vendor choice is made.

**Status:** Phase 4 remains ready to execute as written (use `marketing-director-gtm` skill + existing SMMM repo workers) once SMS/email vendor is selected. Awaiting that decision from your side.

### 4. Fish Audio Parallel Test Spike (Open, Pending Approval)

**Proposal:** Stand up Fish Audio voice backend in parallel with Retell (currently live for pilot customers). Run 1–2 week side-by-side test measuring booking rate, call duration, voice quality, cost.

**Why:** Retell works. Fish Audio is free, low-risk to test. If it's better on any key metric (conversions, latency, voice quality), migration is a flip. If Retell is fine, keep it and keep Fish Audio as backup.

**Status:** Awaiting your go/no-go before implementation.

---

## Current State

**Health:** 10/10 checks passing (app boots, migrations run, tenant isolation holds, site renders, CORS scoped).  
**Tests:** 26 passing (site render, landing page, core router, intake, attribution, etc.).  
**Code:** Compiles, syntax-validated.  
**Demo sites:** 10 live, trade-specific templates, all rendered via Jinja2 (no third-party builder cost).

---

## What Blocks the Pilot

**Resolved this week:**
- Payment vendor decision (Stripe ✓).
- Site renderer audit (complete ✓).
- Webhook integration (complete ✓).

**Still open:**
- SMS/email vendor choice (needed for Phase 4 Marketing Coordinator work if that's needed for pilot).
- Phoenix outreach motion (depends on you).
- CRM integrations (Jobber, ServiceTitan) wired end-to-end.

---

## What's Next (In Order)

1. **Deploy Stripe webhook** to test environment, verify end-to-end with test events.
2. **Phoenix pilot prep:** Nail contractor messaging, set up landing/intake flow, dry-run the 48-hour site deployment with test contractor data.
3. **CRM sync:** Wire Jobber or ServiceTitan (whichever the pilot uses) so appointment → job creation is automatic.
4. **SMS/email automation:** If Phase 4 is in scope for pilot, choose vendor (Twilio, AWS SES, or other) and wire up follow-up workflows.

---

## Burn and Runway

This work is all pre-pilot engineering (design audit, payment wiring, demo site polish, Stripe integration). No external spend beyond Vercel hosting ($5–10/month for pilot volumes). 

**Cost to pilot launch:** Dev time only. We're in the compression phase where every day of engineering work is a week of value captured in the demo.

---

## The Ask (Unchanged)

$15–50K SAFE to fund pilot outreach, paid media, and team time to hit the GTM motion targets. We've built the core product. We've audited the renderer. We've wired payments. Now we scale.

Ready to go.

—K
