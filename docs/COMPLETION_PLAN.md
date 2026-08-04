# COMPLETION_PLAN.md : WebStaffr 4.0 to Full Product

**Status:** Plan only. No code changes. Drafted 2026-08-04 against verified repo state. Revised 2026-08-04 with founder decisions (see Section 0a).
**Supersedes:** nothing. Sequences `docs/AGENT_TEAM_PLAN.md`, `docs/MARKETING_COORDINATOR_PLAN.md`, and the unwritten dashboard work into one ordered path.

---

## 0a. Founder decisions locked 2026-08-04

**1. Automatic response, not approval-first.** Rita's review responses and Sam's quotes send automatically. The customer can intervene, override, and configure — they do not pre-approve each send. This is the product promise: staff that works, not a queue that waits.

**2. The portal is Business Manager tier ($2,497).** Office Staff ($497) does not include the portal.

**What these two decisions change downstream:**

| Consequence | Where it lands |
|---|---|
| TCPA/DNC review moves from "review before Phase 1 outbound" to **hard blocker on any send** | Phase 1 |
| Auto-sent review responses need content guardrails, not a human backstop | Phase 1 |
| Negative reviews must escalate to a human rather than auto-respond | Phase 1 |
| Office Staff tenants need a non-portal proof-of-value surface | Phase 1 |
| Portal needs tier gating, which needs the plan-name drift resolved | Phase 3 |
| Portal becomes the primary upgrade lever, so it needs a preview path for $497 tenants | Phase 3 |

Each is expanded in the phase it affects.

---

## 0. Correction to TASKS.md before anything else

TASKS.md is stale on the most important point. It describes Rita, Leo, and Sam as "not started." They are built, tested, and registered as sibling routers in `create_app()`:

| Worker | Role | Files | Routes | Tests |
|---|---|---|---|---|
| Angel | Receptionist | `workers/angel/` | `/chat`, `/book`, `/webhooks/ghl`, `/retell/*`, `/webhooks/stripe` | `test_angel.py`, `test_router.py`, `test_retell_router.py`, `test_stripe_webhook.py` |
| Leo | Lead Coordinator | `workers/leo/` | `/webhooks/ghl/lead`, `/leo/score` | `test_leo_router.py`, `test_leo_scoring.py` |
| Rita | Reputation Manager | `workers/rita/` | `/webhooks/ghl/job_completed`, `/workers/rita/draft-response` | `test_rita_router.py` |
| Sam | Sales Consultant | `workers/sam/` | `/quotes/generate`, `/quotes/{id}`, `/quotes/{id}/accept` | `test_sam_router.py`, `test_sam_pricing.py`, `test_sam_objections.py` |

Phases 1 through 3 of `AGENT_TEAM_PLAN.md` are substantially **code complete**. What they are not is **live** — every one of them is a `Null*` no-op until GHL and Retell credentials exist. The remaining work is far less "build the agents" than the docs imply, and far more "turn them on, prove them, and give the customer a place to see them working."

That reframes the whole plan. The bottleneck is not engineering capacity. It is three founder gates and one missing foundation.

---

## 1. The one thing that blocks every dashboard

`webstaffr/migrations/0001_tenants.sql` is one column: `tenant_id TEXT PRIMARY KEY`.

There is no user table, no login, no session, no password, no role. Grep for auth in `webstaffr/` returns only shared-secret verifiers for server-to-server webhooks. `tenant_id` is explicitly documented as public and never a credential.

Every dashboard in this plan — customer-facing, internal ops, billing — needs a human to log in and be bound to a tenant. That identity layer does not exist and cannot be faked with `tenant_id`. **Nothing dashboard-shaped can ship until it is built.** It is the single highest-leverage unbuilt thing in the repo, and it is D3 (new surface, no precedent, touches auth and schema, irreversible once customers have accounts).

This is why the dashboard phases sit where they do below, and why Phase 4 exists at all.

---

## 2. Gap inventory (verified, not assumed)

**Agents — of the nine roles in `AGENT_TEAM_PLAN.md`:**

- Built and registered: Angel, Leo, Rita, Sam (4)
- Effectively absorbed by infrastructure: Website Ops (`health_check.py` + Vercel/Supabase)
- Partially built: Growth Manager (`seo_content_pipeline.py` + site renderer schema exist; GBP/listings sync does not)
- Planned only: Marketing Coordinator (`MARKETING_COORDINATOR_PLAN.md`, gated on D4 vendor)
- Not started: Service Advisor (Angel prompt extension, no new worker), Front Office Manager (orchestration, by design last)

**Dashboards — none exist.** No login, no tenant portal, no ops console, no billing UI. Zero lines written. Three distinct products are hiding under the word "dashboard":

1. **Customer portal** — the tenant logs in, sees their leads, calls, quotes, reviews, bookings, and site. This is the retention surface. Without it, a customer paying $497/mo has no evidence they are getting value.
2. **Internal ops console** — you log in, see all tenants, health, error rates, credential status, usage. This is how you run the business at more than ~5 customers.
3. **Billing** — plan, invoices, usage, upgrade path. Stripe webhook exists and is fixed; nothing renders it.

**Infrastructure gaps behind all of the above:** identity/auth, a per-tenant activity/event stream to actually display, and a usage metering path if tiers are ever usage-bound.

---

## 3. Sequencing principle

Order is set by three rules, applied in this priority:

1. **Prove revenue before building for scale.** One paying tenant running end-to-end teaches more than any amount of pre-built surface. Everything before that is speculation.
2. **Unblock gates early.** Founder decisions have lead time and block whole phases. They go first even when the code they unblock comes later.
3. **Build foundations once, at the last responsible moment.** Auth is a foundation. Build it when the first dashboard needs it, not before, and never twice.

The plan therefore front-loads *turning on what is already built*, then builds identity, then dashboards, then the remaining agents.

---

## 4. The phases

### Phase 0 — Ship the MVP live (Weeks 1–2)

**Goal:** one real tenant goes intake → generated site → Angel answering → booked job in GHL. Nothing new is built.

| Work | Depth | Gate |
|---|---|---|
| Set `GHL_API_KEY`, `GHL_LOCATION_ID`, `GHL_WEBHOOK_SECRET`, `RETELL_WEBHOOK_SECRET` | D4 | Founder — paid vendors |
| Commit the 20+ uncommitted files sitting in the working tree | D4 | Founder — push approval |
| Run `webstaffr-onboarding-smoketest`, verify Retell voice path end-to-end | D1 | none |
| Fix trust bar dead divs; restyle `service/about/contact.html` to home's visual language | D1 | none |
| Resolve payment vendor (Stripe vs Orion) — Stripe webhook is already written, tested, and secure | D4 | Founder |

**Exit:** one paying-tier flow works, verified against a live tenant, not a fixture.

**Note on the working tree:** there are 11 modified and 15 untracked files uncommitted right now, including `site_schema.py`, `seo_content_pipeline.py`, and two new test files. That is a meaningful body of unshipped work and a growing merge risk. Clearing it is the first move of Phase 0.

---

### Phase 1 — Prove the built agents against a live tenant (Weeks 2–4)

**Goal:** Leo, Rita, and Sam stop being `Null*` no-ops.

Each is already coded to the invariants (Protocol + `Null*` + `*NotConfiguredError`, tenant-scoped queries, no CORS on server-to-server). Turning them on is configuration plus verification, not construction.

| Work | Depth |
|---|---|
| GHL workflows for Leo: instant acknowledgment, follow-up sequences, reminders | D2 |
| **TCPA/DNC compliance review — hard gate, nothing sends until cleared** | **D4 — legal** |
| Rita live: job-completion trigger → review request → auto-sent response | D2 |
| **Auto-send guardrails** (see below) | D2 |
| Sam live: auto-sent quotes from trade presets against a real tenant's pricing | D2 |
| Per-tenant metrics recorded for each (this becomes dashboard data) | D2 |
| Weekly value-proof email for Office Staff tenants (no portal at $497) | D2 |

**Auto-send is the decision that raises the stakes of this phase.** With approval-first, a bad draft is caught by the customer. With automatic send, a bad draft is a published review response under the customer's business name. The engineering work that makes this safe:

- **Never fabricate.** Existing invariant, now load-bearing. Auto-responses may not invent remedies, discounts, timelines, or facts not in the tenant record.
- **Negative reviews escalate, they do not auto-respond.** A 1- or 2-star review routes to a human with a suggested draft. Auto-responding to an angry customer with generated text is the single most likely way this feature produces a public incident.
- **Kill switch per tenant, per worker.** A customer must be able to stop auto-send instantly without a support ticket.
- **Every auto-send is logged as a reversible event** with what was sent, when, and on what trigger.
- **Rate ceilings.** A webhook loop that fires 400 review requests at one customer list is a plausible failure, not a paranoid one.

**Office Staff proof-of-value.** Portal is now $2,497-only, so $497 tenants have no window into their staff working. A weekly summary email — calls answered, leads captured, jobs booked — is the substitute, and it doubles as the upgrade pitch. Cheap to build on the same `activity_events` data.

**Exit:** every lead acknowledged under 2 minutes; review request within 24h of job completion; quote turnaround same-day; zero auto-sends that violate the never-fabricate rule; negative reviews escalating, not auto-answering.

**Design note that matters later:** Phase 1 is where you decide what an "event" is. Every dashboard renders a per-tenant activity stream — call answered, lead scored, quote sent, review requested, job booked. If each worker writes those events to one shared, tenant-scoped `activity_events` table now, the dashboards become a read query. If it is deferred, dashboards become an archaeology project across five schemas. **Recommendation: define `activity_events` in Phase 1, not Phase 3.** D3, schema change, founder approval on the migration.

---

### Phase 2 — Identity and access (Weeks 4–6) — **D3, the foundation**

**Goal:** a human can log in and be bound to a tenant with a role.

| Work | Depth |
|---|---|
| ADR in `docs/DECISIONS.md`: auth approach, session model, role model | D3 |
| `users` + `tenant_members` tables, roles: owner / staff / webstaffr_admin | D3 — schema, founder approval |
| Login, logout, password reset, session middleware | D3 |
| Route protection: every dashboard route tenant-scoped by session, not by URL parameter | D3 |
| Auth vendor decision if not rolling own | **D4 — vendor** |

**The critical invariant:** today `tenant_id` arrives in the request and is trusted because every caller is either a webhook with a shared secret or a public site read. The moment a browser session exists, `tenant_id` from a request parameter becomes an authorization bypass. Dashboard routes must derive tenant from the session and never from user input. This is the one place in this plan where a five-line mistake is unrecoverable in production.

**Recommendation on build-vs-buy:** you have Auth0 skills installed and a founder who is not a coder maintaining this. Rolling your own password storage, reset flows, and session invalidation is the kind of thing that looks cheap in week one and is a liability in year one. **Recommend a managed provider.** That is a D4 vendor call with a real monthly cost, so it is yours — but the engineering recommendation is unambiguous.

**Exit:** a tenant owner logs in and sees a page that is provably theirs and provably not anyone else's, with a test that asserts cross-tenant access returns 403.

---

### Phase 3 — Customer portal (Weeks 6–9)

**Goal:** the retention surface and the upgrade lever. A Business Manager customer opens this and sees their staff working.

Built on Phase 1's `activity_events` and Phase 2's session. Jinja2 server-rendered, matching the existing `site_renderer.py` stack — no new frontend framework, no new dependency.

**Gated to Business Manager tier.** Two things follow from that:

- **Tier gating needs the plan-name drift resolved first.** `intake.py` accepts `essentials / pro / growth`; the tier this portal belongs to is called Business Manager in every pricing document. There is no mapping between the two vocabularies. A tier check cannot be written against a name that does not exist in the code. **This is now a Phase 3 prerequisite, not a backlog item** (logged in TASKS.md 2026-08-04).
- **Office Staff tenants need a preview, not a locked door.** The portal is the reason to pay 5x more. A $497 tenant should see the overview screen with their real numbers and the deeper screens visibly gated — not a 403. That is a conversion surface, not a paywall.

| Screen | Content | Tier | Depth |
|---|---|---|---|
| Overview | Calls answered, leads captured, bookings, quotes out, reviews requested — this week vs last | Preview at $497, full at $2,497 | D2 |
| Activity | Live per-tenant event stream | Business Manager | D2 |
| Leads | Leo's captures with AOKAI score, status, source attribution | Business Manager | D2 |
| Quotes | Sam's auto-sent quotes, status, accept/decline, override | Business Manager | D2 |
| Reviews | Rita's requests and auto-sent responses, escalation queue for negative reviews, per-worker kill switch | Business Manager | D2 |
| Site | Preview, request-a-change, custom domain status | Business Manager | D2 |
| Settings | Business info, hours, services, auto-send controls, notification preferences | Business Manager | D2 |

**The Reviews and Quotes screens change shape under the automatic decision.** They are no longer approval queues. They are audit trails plus controls: what went out, when, and the switches to stop or amend it. The escalation queue for negative reviews is the one place a human still acts before anything sends.

**Exit:** a Business Manager customer can answer "what did WebStaffr do for me this week" without contacting you, and an Office Staff customer can see exactly what they are missing.

---

### Phase 4 — Internal ops console + billing (Weeks 9–12)

**Goal:** you can run 50 tenants without opening a database client.

| Work | Depth |
|---|---|
| Tenant list: status, plan, health, last activity, credential state | D2 |
| Per-tenant drill-down reusing Phase 3's views under admin role | D2 |
| Error and integration health surface (which tenants have a broken GHL sync, right now) | D2 |
| Onboarding queue: intake submissions awaiting site generation or credentials | D2 |
| Billing: plan, invoices, upgrade path, wired to the existing Stripe webhook | D3 — money |
| Usage metering if any tier is usage-bound | D3 |

**Exit:** onboarding a new tenant is a workflow in the console, not a session with Claude.

---

### Phase 5 — Remaining agents (Weeks 12–20)

Deliberately last. Every one of these is worth more once there is a portal to display it in and paying customers to inform it.

**5a. Service Advisor (Weeks 12–13, D2).** No new worker — an Angel prompt and intent extension: per-trade pre-diagnosis questions feeding the booking payload, urgency detection, escalation. Cheapest remaining agent by a wide margin, and it improves every booking Angel already makes.

**5b. Growth Manager completion (Weeks 13–15, D2).** `seo_content_pipeline.py` and the renderer's schema work are built. Remaining: Google Business Profile and listings sync, per-tenant SEO reporting into the portal. Note the pipeline's own rule — vendor keyword/SERP data is an injected concern, so this needs a data source decision (**D4 — vendor**).

**5c. Marketing Coordinator (Weeks 15–19, D3).** Execute `MARKETING_COORDINATOR_PLAN.md` as written. Gated on the D4 SMS/email vendor decision (recommendation on file: Twilio + Postmark, unsigned since 2026-07-27) and the SearXNG research layer. The social bridge (`social_media_mounts`, `execution_nodes`) is already built and tested on this side.

**5d. Front Office Manager (Weeks 19–20, D3).** Orchestration across workers in the composition root — handoffs, escalation routing, per-tenant reporting. This is the White-Glove tier's backbone and is correctly built last, once there are five workers worth orchestrating and a portal to report into.

---

## 5. Critical path, compressed

```
Credentials (D4) ──▶ Phase 0 live MVP ──▶ Phase 1 agents proven
                                              │
                                              ├──▶ activity_events schema (D3)
                                              │
Auth vendor (D4) ──▶ Phase 2 identity ────────┴──▶ Phase 3 portal ──▶ Phase 4 ops+billing
                                                                          │
Legal: TCPA/DNC (D4) ──▶ Leo outbound                                     │
SMS/email vendor (D4) ────────────────────────────────────────────────────┴──▶ Phase 5c Marketing
```

Roughly 20 weeks end to end, assuming founder gates clear without stalling. The gates, not the code, are the schedule risk — three of the five have been open for over a week already.

---

## 6. Founder decisions this plan needs

Ordered by how much they block:

**Still open:**

1. **GHL + Retell credentials** — blocks Phase 0, therefore everything. Open since 2026-07-28.
2. **Payment vendor: Stripe or Orion** — Stripe integration is already written, tested, and its signature bug fixed. Choosing Orion discards working code.
3. **TCPA/DNC compliance review** — now a hard gate on all Phase 1 outbound, given the automatic-send decision. Legal, not engineering.
4. **Auth: managed provider or roll our own** — blocks Phase 2, therefore every dashboard. Engineering recommendation is managed.
5. **Tier naming** — `essentials / pro / growth` in code vs Office Staff / Business Manager / White-Glove in pricing. Blocks Phase 3 tier gating. Product call, then a rename or mapping.
6. **SMS/email vendor** — blocks Phase 5c only. Recommendation on file since 2026-07-27.

**Resolved:**

- ~~Push approval for the working tree~~ — approved 2026-08-04.
- ~~Approval-first vs automatic~~ — **automatic**, 2026-08-04.
- ~~Which tier includes the portal~~ — **Business Manager ($2,497)**, 2026-08-04.

Everything else in this document is self-approvable engineering inside existing invariants.

---

## 7. What this plan deliberately does not do

- **No new frontend framework.** Dashboards are Jinja2 on the existing stack. A React SPA would be a new dependency, a new build step, and a second way to render pages in a repo that already renders pages well.
- **No ORM.** Unchanged invariant.
- **No rebuild of what works.** Angel, Leo, Rita, and Sam are not touched except to turn on and instrument.
- **No parallel phases.** One phase at a time, reviewed and approved before the next — per CLAUDE.md's working rule. The week ranges assume sequential execution.
