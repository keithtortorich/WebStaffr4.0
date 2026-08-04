# NetBuild.Pro — Product Context for Impeccable

## Product Vision
NetBuild.Pro is an AI-employee platform that answers every customer service call for home service businesses (plumbing, HVAC, electrical, etc). The AI (Angel) responds to inbound calls in real time, qualifies leads, books appointments, and integrates with existing workflows (GHL, ServiceTitan, Retell voice).

## Core Flow (MVP)
1. **Intake** — Business submits a 9-section form (business basics, positioning, services, credibility, social, workforce plan, content/SEO)
2. **Site Generation** — NetBuild.Pro renders a professional customer-facing website from the intake data
3. **Angel Widget** — Embedded on the site, answers calls using the business's own voice and knowledge
4. **Live Voice** — Retell AI handles real-time call synthesis

## Current Scope (MVP)
- Intake → Site generation → Angel answering → Live voice via Retell
- Site rendering via Jinja2 templates (site_renderer.py)
- No multi-agent orchestration, no workflow builder UI, no billing/tier logic (Phase 2+)

## Design Principles
- **No fabrication**: Never invent ratings, reviews, or credentials. Omit sections rather than fill with placeholders.
- **Tenant isolation**: Every query scoped by `tenant_id`. Internal data (lead_routing, approver) never exposed.
- **Schema clarity**: All fields defined upfront. No missing keys. All optionals present (None if absent).
- **Fail-safe defaults**: Missing data becomes None, never invented content.
- **Single responsibility**: Each module owns one thing. Templates display; Python computes.

## Audience
Home service business owners (40-70 years old, tech-skeptical, time-poor). They want calls answered, not UI features.

## Success Metric
All inbound calls answered by Angel. No missed leads.
