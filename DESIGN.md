# WebStaffr Design System

## Visual Language
- **Hero-first layout**: Bold headline, value prop, CTA above the fold
- **Trust bar**: Rating, certifications, emergency service, free estimates (show only if ≥2 signals)
- **Icon set**: Inline SVG, 14–56px, single-color (primary on background)
- **Color palette**: Primary brand hex (dynamic from intake), neutral grays, semantic reds for errors

## Typography
- **Headlines (h1, h2, h3)**: sans-serif, bold, 1.2–1.4 line-height
- **Body**: sans-serif, 16px, 1.5 line-height, max-width 600px
- **UI labels**: sans-serif, 12–14px, caps optional, 0.05em letter-spacing

## Spacing
- **Sections**: 48–64px vertical rhythm
- **Cards**: 16px internal padding, 8–12px gap between items
- **CTA buttons**: 48px min height, 16–20px horizontal padding

## Content Gates
- **Trust bar**: Show only if `trust_signal_count >= 2` (rating + reviews + certs + emergency + pricing)
- **Reviews section**: Show only if `has_reviews` (rating_value AND review_count both present)
- **Service pages**: Render only services in the submitted list, never invent

## Schema (from site_schema.py)
**Required**: tenant_id, biz_name, phone, email, industry, service_area, tagline, differentiator, services, plan
**Optional (always present, may be None)**: brand_colors, years_in_biz, emergency_service, rating_value, review_count, certifications, testimonials, facebook_url, instagram_url, keywords, pricing_shown, promos, tone, gbp_url, google_review_link, has_before_after

## Computed Properties
- `trust_signal_count` — Integer; gates trust bar
- `has_reviews` — Boolean; gates reviews section and /reviews page
- `service_pages` — List of (name, slug) tuples
- `palette` — Color dict for CSS variable injection
- `show_trust_bar` — Boolean; true if trust_signal_count >= 2

## Anti-Patterns (Never)
- Fabricated ratings or reviews
- Missing optional fields in context (use None instead)
- Business logic in templates (compute in Python)
- CORS headers on server-to-server routes
- Tenant data leakage across tenant_id boundaries
