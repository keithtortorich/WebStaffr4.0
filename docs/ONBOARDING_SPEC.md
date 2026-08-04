# Onboarding Experience Specification — Phase 2

**Status:** Specification only (no UI implementation yet)  
**Date:** 2026-08-04  
**Owner:** Claude (spec). Codex validates technical feasibility per section.  
**Source:** INTAKE_FORM_PHASE2_CANONICAL.md, intake.py (IntakeSubmission dataclass)  
**Deliverable:** Define every screen from initial landing through final site launch.

---

## Overview

The onboarding experience guides a business from awareness (landing page) through intake (9-section form) to site generation and Angel deployment. This spec reconciles the intake form schema (INTAKE_FORM_PHASE2_CANONICAL.md) against the actual fields in `intake.py` — no hypothetical new fields.

**Flow:**
1. Landing page — 3-field lead capture
2. Lead triage → route to intake wizard
3. Intake wizard — 9 sections, ~40 fields
4. Submission review → confirmation
5. Site generation → launch approval
6. Angel deployment → live

---

## Screen 1: Landing Page — Lead Capture

**Purpose:** Minimal entry point; capture contact + business name to initiate intake.  
**Placement:** Public landing page (e.g., `webstaffr.com/start`)  
**Template:** Simple form card, no multi-step wizards yet.

| Field | Intake Field | Type | Required | Label | Explanation | Validation | Default | Error Message | Consuming Worker |
|-------|--------------|------|----------|-------|-------------|-----------|---------|----------------|------------------|
| Business name | `biz_name` | string | ✓ | "Business name" | "Legal name of your business (used for your site URL)" | Non-empty string, < 100 chars | None | "Business name required" | Tenant ID generation |
| Phone | `phone` | string | ✓ | "Business phone" | "Your primary contact number (for lead routing)" | Non-empty string, accepts any format | None | "Phone number required" | Lead routing, Angel call target |
| Email | `email` | string | ✓ | "Email address" | "Primary contact email (we'll send confirmations here)" | Valid email format | None | "Valid email required" | Lead routing, access/recovery |

**Submit action:** `POST /intake` with `biz_name`, `phone`, `email` → redirects to Screen 2 (Industry selection).

**UX notes:**
- Single form card, no accordion/tabs
- Submit button disabled until all three fields filled
- Phone: accept any format (no validation beyond non-empty)
- Email: use browser native `type=email` validation

---

## Screen 2: Industry & Service Area (Conditional)

**Purpose:** Classify the business; fetch industry-specific hints. Route to intake wizard if new, or dashboard if returning.

| Field | Intake Field | Type | Required | Label | Explanation | Validation | Default | Error Message | Consuming Worker |
|-------|--------------|------|----------|-------|-------------|-----------|---------|----------------|------------------|
| Industry | `industry` | string (select) | ✓ | "What industry are you in?" | "Select your trade. We'll provide industry-specific tips." | Must be in `VALID_INDUSTRIES` or "Other" | None | "Please select an industry" | Trade presets, site copy templates |
| Service area | `service_area` | string | ✓ | "Service area" | "Geographic scope where you operate (e.g., 'Tampa metro', 'statewide')" | Non-empty string, free text | None | "Service area required" | Site copy, local SEO |

**API calls:**
- Load `GET /intake/presets` on page load → populate industry dropdown
- On industry change, call `GET /intake/presets/{industry}` → display industry hints below select

**UX notes:**
- Dropdown populated from `GET /intake/presets` response (canonical list: HVAC, Plumber, Electrician, Roofing, Water Damage Restoration, Garage Door Repair, Pest Control, Landscaping, Tree Service, Cleaning Services, Other)
- Hints displayed below select (FSM software suggestions, trade notes)
- Service area is free text, not a select — no preset list

**Submit action:** Validate; if valid, proceed to Screen 3 (Business Basics section).

---

## Screen 3: Business Basics — Section 1

**Purpose:** Core business identity.

| Field | Intake Field | Type | Required | Label | Explanation | Validation | Default | Error Message | Consuming Worker |
|-------|--------------|------|----------|-------|-------------|-----------|---------|----------------|------------------|
| Years in business | `years_in_biz` | integer | ✗ | "Years in business" | "Optional. Helps with credibility signals on your site." | Integer ≥ 0, or empty | None | "Must be a whole number" | Site copy credibility, Angel context |
| Emergency service? | `emergency_service` | radio (yes/no) | ✗ | "Do you offer emergency service?" | "Shows a badge on your site if yes" | "yes" or "no" or empty | None | N/A | Site display, Angel escalation |

**UX notes:**
- Years in business: HTML5 `type=number`, min=0, optional
- Emergency service: two radio buttons (yes/no), initially unchecked
- These are *optional* — do not block submission if skipped

---

## Screen 4: Current Web Presence — Section 2

**Purpose:** Understand existing digital footprint.

| Field | Intake Field | Type | Required | Label | Explanation | Validation | Default | Error Message | Consuming Worker |
|-------|--------------|------|----------|-------|-------------|-----------|---------|----------------|------------------|
| Have a website? | `has_site` | radio (yes/no) | ✗ | "Do you have an existing website?" | "Helps us understand your current setup" | "yes" or "no" or empty | None | N/A | Site generation, migration planning |
| Website URL | `site_url` | string | ✗ (conditional) | "Website URL" | "Link to your current site" | Valid URL format | None | "Enter a valid URL" | Competitive analysis, design reference |
| Website platform | `site_platform` | select | ✗ (conditional) | "Which platform?" | "Wix, Squarespace, WordPress, custom, or other" | Must be in preset list or empty | None | N/A | Integration planning |
| Website issues | `site_issues` | textarea | ✗ | "Any issues with your current site?" | "E.g., slow, outdated, no lead form — helps us improve your new site" | Free text, any length | None | N/A | Site spec prioritization |
| Google Business Profile? | `has_gbp` | radio (yes/no) | ✗ | "Do you have a Google Business Profile?" | "Essential for local search" | "yes" or "no" or empty | None | N/A | SEO, citation building |
| GBP URL | `gbp_url` | string | ✗ (conditional) | "Google Business Profile link" | "Link to your GBP profile" | Valid URL format | None | "Enter a valid URL" | Citation sync, review monitoring |
| Google reviews link | `google_review_link` | string | ✗ | "Google reviews link" | "Direct link to your reviews section" | Valid URL format | None | "Enter a valid URL" | Review display, social proof |

**Conditional logic:**
- `website_url` and `website_platform` only required if `has_site = "yes"`
- `gbp_url` only required if `has_gbp = "yes"`

**UX notes:**
- `has_site`, `has_gbp` are two radio buttons each
- `site_platform` dropdown: Wix, Squarespace, WordPress, custom, other
- All URL fields: use HTML5 `type=url` for browser-native validation
- `site_issues` textarea: 5 rows, optional

---

## Screen 5: Brand — Section 3

**Purpose:** Visual identity and design direction.

| Field | Intake Field | Type | Required | Label | Explanation | Validation | Default | Error Message | Consuming Worker |
|-------|--------------|------|----------|-------|-------------|-----------|---------|----------------|------------------|
| Have a logo? | `has_logo` | radio (yes/no) | ✗ | "Do you have a business logo?" | "We can integrate it into your new site" | "yes" or "no" or empty | None | N/A | Site design, branding |
| Brand colors | `brand_colors` | string | ✗ | "Brand colors" | "E.g., 'navy and gold', hex codes, or color names" | Free text, any length | None | N/A | Site design, Lovable context |
| Brand words | `brand_words` | string | ✗ | "Words that describe your brand" | "E.g., 'professional', 'friendly', 'bold' — helps set the tone" | Free text, any length | None | N/A | Site copy tone, design direction |
| Design inspiration sites | `inspo_sites` | textarea | ✗ | "Design inspiration" | "URLs of competitor or reference sites you like" | Free text URLs, one per line | None | N/A | Design reference, creative brief |

**UX notes:**
- `has_logo` radio: yes/no, initially unchecked
- `brand_colors`, `brand_words`: text input, optional
- `inspo_sites` textarea: 3 rows, free text (URLs on separate lines, not validated as URLs)

---

## Screen 6: Positioning — Section 4

**Purpose:** Differentiation and messaging.

| Field | Intake Field | Type | Required | Label | Explanation | Validation | Default | Error Message | Consuming Worker |
|-------|--------------|------|----------|-------|-------------|-----------|---------|----------------|------------------|
| Tagline | `tagline` | string | ✓ | "Your tagline" | "One-liner for your homepage hero section (e.g., 'Emergency plumbing, same-day response')" | Non-empty string, < 150 chars | None | "Tagline required" | Site hero copy, Angel greeting |
| Differentiator | `differentiator` | string | ✓ | "What makes you different?" | "Why should customers choose you? (e.g., 'Family-owned, 20 years, 100% satisfaction guarantee')" | Non-empty string, < 300 chars | None | "Differentiator required" | Site positioning copy, Angel context |
| Competitors | `competitors` | textarea | ✗ | "Named competitors" | "Who do you compete against? (Informational only)" | Free text, any length | None | N/A | Competitive analysis, site copy |
| Brand tone | `tone` | select | ✗ | "Brand tone" | "How should your site sound? Professional, friendly, authoritative, casual" | Must be in preset list or empty | None | N/A | Site copy generation, Angel voice |

**Preset values for `tone` select:**
- Professional
- Friendly
- Authoritative
- Casual

**UX notes:**
- `tagline`: text input, single line, max 150 chars, required
- `differentiator`: textarea, 3 rows, required
- `competitors`: textarea, 2 rows, optional
- `tone` select: 4 preset options, initially unselected

---

## Screen 7: Services & Licensing — Section 5

**Purpose:** Service offerings and regulatory compliance.

| Field | Intake Field | Type | Required | Label | Explanation | Validation | Default | Error Message | Consuming Worker |
|-------|--------------|------|----------|-------|-------------|-----------|---------|----------------|------------------|
| Services offered | `services` | textarea (multi-line list) | ✓ | "What services do you offer?" | "List your main service offerings (one per line, e.g., 'Emergency repair', 'Maintenance')" | Non-empty list, ≥ 1 item | None | "At least one service required" | Site services section, Angel knowledge |
| Show pricing on site? | `pricing_shown` | radio (yes/no) | ✗ | "Display pricing on your site?" | "If yes, we'll add a pricing section" | "yes" or "no" or empty | None | N/A | Site pricing section |
| Promotions | `promos` | string | ✗ | "Active promotions" | "Any current offers or seasonal promotions (e.g., '15% off winterization')" | Free text, any length | None | N/A | Site promo section, Angel upsell |
| License number | `license_number` | string | ✓ | "License number" | "Your professional license ID (stored securely, never displayed publicly)" | Non-empty string | None | "License number required" | Compliance, internal audit only |

**UX notes:**
- `services`: textarea showing 4 rows, user enters one service per line, split on newlines
- `pricing_shown`: radio yes/no, optional
- `promos`: text input, single line, optional
- `license_number`: text input, single line, required (not shown on public site per site_data.py)

---

## Screen 8: Proof & Credibility — Section 6

**Purpose:** Social proof; no fabrication.

| Field | Intake Field | Type | Required | Label | Explanation | Validation | Default | Error Message | Consuming Worker |
|-------|--------------|------|----------|-------|-------------|-----------|---------|----------------|------------------|
| Star rating | `rating_value` | number | ✗ | "Average rating" | "E.g., 4.8 (only shown if you also have ≥3 reviews)" | 1.0–5.0 float | None | "Rating must be between 1 and 5" | Site star display (gated on review_count) |
| Number of reviews | `review_count` | integer | ✗ | "Number of reviews" | "Must be ≥3 for rating to display on your site" | Integer ≥ 0 or empty | None | "Must be a whole number" | Site star display gate, social proof |
| Certifications | `certifications` | textarea | ✗ | "Certifications" | "E.g., 'EPA certified', 'GAF Master Elite', 'ISSA member'" | Free text, any length | None | N/A | Site trust signals, Angel context |
| Before/after photos? | `has_before_after` | radio (yes/no) | ✗ | "Do you have before/after project photos?" | "We can showcase them on your site" | "yes" or "no" or empty | None | N/A | Site project gallery |
| Testimonials | `testimonials` | textarea | ✗ | "Customer testimonials" | "One or more customer quotes (can span multiple lines)" | Free text, any length | None | N/A | Site testimonial section |

**Gating logic:**
- Star rating only renders on public site if `rating_value` is present AND `review_count` ≥ 3
- Testimonials section omitted if empty (no placeholder)

**UX notes:**
- `rating_value`: HTML5 number input, step=0.1, min=1, max=5, optional
- `review_count`: HTML5 number input, min=0, optional
- `certifications`: textarea, 2 rows, optional
- `has_before_after`: radio yes/no, optional
- `testimonials`: textarea, 4 rows, optional

---

## Screen 9: Social & Integrations — Section 7

**Purpose:** Digital presence and tooling.

| Field | Intake Field | Type | Required | Label | Explanation | Validation | Default | Error Message | Consuming Worker |
|-------|--------------|------|----------|-------|-------------|-----------|---------|----------------|------------------|
| Facebook | `facebook_url` | string | ✗ | "Facebook page link" | "Link to your Facebook business page" | Valid URL format or empty | None | "Enter a valid URL" | Site social links |
| Instagram | `instagram_url` | string | ✗ | "Instagram profile link" | "Link to your Instagram business profile" | Valid URL format or empty | None | "Enter a valid URL" | Site social links |
| Field Service Management system | `fsm_system` | select | ✗ | "What FSM software do you use?" | "ServiceTitan, Housecall Pro, Jobber, or other — helps us understand your workflow" | Preset list or empty | None | N/A | Integration planning, Angel context |
| Public booking available? | `booking_system` | radio (yes/no) | ✗ | "Does your FSM have public booking?" | "Can customers book appointments via your site?" | "yes" or "no" or empty | None | N/A | Site booking feature, integration planning |

**Preset values for `fsm_system` select:**
- ServiceTitan
- Housecall Pro
- Jobber
- Other
- (blank/unselected)

**UX notes:**
- `facebook_url`, `instagram_url`: text input with `type=url`, optional
- `fsm_system`: dropdown, optional
- `booking_system`: radio yes/no, optional

---

## Screen 10: Workforce & Plan Selection — Section 8

**Purpose:** Pricing tier and lead routing (internal-only fields).

| Field | Intake Field | Type | Required | Label | Explanation | Validation | Default | Error Message | Consuming Worker |
|-------|--------------|------|----------|-------|-------------|-----------|---------|----------------|------------------|
| Tier | `plan` | select | ✓ | "Which NetBuild.Pro tier?" | "Essentials ($497/mo), Pro ($2,497/mo), or Growth ($5,000+/mo) — see pricing page for details" | Must be "essentials", "pro", or "growth" | None | "Please select a tier" | Billing, site feature gates, Angel package |
| Lead routing | `lead_routing` | string | ✓ | **Internal only** | "GHL location ID or internal routing rules for this tenant (never exposed to customer)" | Non-empty string | None | "Lead routing required" | GHL webhook config, internal ops |
| Timeline | `timeline` | select | ✗ | "When do you want to launch?" | "ASAP, 2-4 weeks, 1-2 months, or planning phase — helps us prioritize support" | Preset values or empty | None | N/A | Support prioritization, site readiness |
| Approver | `approver` | string | ✓ | **Internal only** | "Name and email of person approving this submission (e.g., 'Keith Tortorich <keith@webstaffr.com>')" | Non-empty string | None | "Approver required" | Audit trail, internal record |

**Preset values for `timeline` select:**
- ASAP
- 2–4 weeks
- 1–2 months
- Planning phase
- (blank/unselected)

**UX notes:**
- `plan` dropdown: show pricing for each tier on selection
- `lead_routing` and `approver`: label as internal-only in UI or hide from public forms (only shown in internal intake flow)
- `timeline` select: optional, for internal prioritization only

---

## Screen 11: Content & SEO — Section 9

**Purpose:** Additional pages and optimization.

| Field | Intake Field | Type | Required | Label | Explanation | Validation | Default | Error Message | Consuming Worker |
|-------|--------------|------|----------|-------|-------------|-----------|---------|----------------|------------------|
| Asset status | `assets_status` | radio | ✗ | "Do you have photos/video assets?" | "Have photos, need photos, or will provide later — helps us plan your site launch" | "have photos/video" \| "need photos/video" \| "will provide later" \| empty | None | N/A | Site design, content planning |
| Target keywords | `keywords` | textarea | ✗ | "Target keywords" | "Keywords you want to rank for (e.g., 'emergency plumbing Phoenix', 'HVAC repair Tampa')" | Free text, any length | None | N/A | SEO optimization, site copy, Angel knowledge |
| Extra pages | `extra_pages` | textarea | ✗ | "Additional pages" | "Pages beyond standard Home/Services/About/Contact (e.g., 'Blog', 'Financing options', 'Warranty', 'FAQ')" | Free text, one per line | None | N/A | Site architecture, content roadmap |
| Additional notes | `notes` | textarea | ✗ | "Anything else?" | "Catch-all for anything not covered above" | Free text, any length | None | N/A | Support context, site spec |

**UX notes:**
- `asset_status`: radio group with 3 options, optional
- `keywords`: textarea, 2 rows, optional
- `extra_pages`: textarea, 2 rows, optional (one per line)
- `notes`: textarea, 4 rows, optional

---

## Screen 12: Review & Submission

**Purpose:** Confirm data before sending.

**Content:**
- Summary of all 9 sections (collapsible)
- Links to edit each section
- "Review my information" heading
- Checkbox: "I confirm this information is accurate"
- Submit button (disabled until checkbox checked)
- Cancel button (exits without saving)

**Submit action:**
- POST `/intake` with full payload from all 9 sections
- On 201 Created: redirect to Screen 13 (Confirmation)
- On 400 Bad Request: show error summary, highlight problem fields
- On 503 Service Unavailable: show "Please try again" message with retry button

**UX notes:**
- Use collapsible sections for each of the 9 intake sections — one per section
- Each collapsible has an "Edit" link that returns to that screen
- Validation summary at top if 400 error
- No PII (email, phone, license number) shown in full form view — show masked (first/last chars only)

---

## Screen 13: Confirmation & Site Generation

**Purpose:** Confirm submission; show site URL; begin generation.

**Content:**
- Success message: "Your submission received!"
- Submission ID (for support reference)
- Tenant ID (for site URL)
- Site URL: `webstaffr.com/sites/{tenant_id}/web` (clickable link)
- Status: "Your site is being generated..." (spinner)
- "Angel widget is being deployed..."
- Estimated time: "Usually ready in 5–10 minutes"

**What happens in background:**
1. Tenant created in `webstaffr_tenants` (if new)
2. Tracking number assigned in `webstaffr_tracking_numbers`
3. Site data cached in `webstaffr_sites` (optional)
4. Site generated via `site_renderer.py` (Jinja2)
5. Angel deployed (Retell widget embedded)
6. Lead routing configured (GHL webhook)

**UX notes:**
- Show submission_id and tenant_id so user can reference support
- Site link clickable once generation completes
- Polling UI: check `/sites/{tenant_id}/web` status every 2 seconds
- Timeout: if generation takes >10 min, show "Contact support" message
- No email sent yet (Phase 2+ feature)

---

## Screen 14: Site Launch

**Purpose:** Customer can see their live site.

**Content:**
- Heading: "Your NetBuild.Pro site is live!"
- Live site iframe or full-page link
- "Customize your site" button → directs to Lovable site editor (if owner authenticated)
- "Call Angel demo" button → triggers Retell widget
- "Go to owner dashboard" button → directs to `/dashboard/{tenant_id}` (requires auth from Codex Batch 3)

**UX notes:**
- Site is now publicly accessible at `webstaffr.com/sites/{tenant_id}/web`
- Angel widget is live and listening for inbound calls/chat
- Owner can customize via Lovable link
- Dashboard is gated behind Bearer token auth (Codex implementation)

---

## Form Structure & UX Patterns

### Multi-step vs. Single-page

**Recommendation:** Single-page form with collapsible sections per screen design above.

**Rationale:**
- 9 sections span ~40 fields — too much for one scroll, too many steps for a wizard
- Collapsible sections let users skip optional sections without feeling forced
- Progress bar shows sections completed
- Save-and-resume not required for Phase 2; Phase 2+ can add

### Validation

**Client-side (instant feedback):**
- Required fields: `type=email`, `type=url`, `type=number`, `required` attribute
- Conditional fields: show/hide based on preceding field values
- Inline error messages below each field

**Server-side (before POST):**
- All validation rules in `intake.py` `validate_intake_payload()`
- Return 400 with field-level error list
- Frontend maps error list to form fields for highlighting

### Accessibility

- Form labels: `<label for="field-id">` paired to inputs
- Required fields: mark with `*` and aria-required=true
- Error messages: role=alert, aria-live=polite
- Keyboard navigation: tab through all fields, submit with Enter
- ARIA landmarks: `<fieldset>` for each section

### Mobile / Responsive

- Form should stack vertically on small screens
- Inputs: full-width on mobile, ~80% width on desktop
- Collapsible sections: always usable on mobile (tap to expand)
- Buttons: full-width on mobile, auto-width on desktop

---

## Data Flow Summary

```
Landing (Screen 1)
  ↓ biz_name, phone, email
  ↓
Industry & Area (Screen 2)
  ↓ industry, service_area
  ↓
Intake Form (Screens 3–11)
  ↓ all 9 sections' fields
  ↓
Review & Submit (Screen 12)
  ↓ POST /intake
  ↓ [validation in intake_router.py + intake.py]
  ↓
Confirmation (Screen 13)
  ↓ [tenant creation, site generation, Angel deployment]
  ↓
Site Launch (Screen 14)
  ↓ live site at /sites/{tenant_id}/web
```

---

## Codex Feasibility Notes (for review)

**Screens 1–2 (Landing & Industry):**
- Requires `GET /intake/presets` and `GET /intake/presets/{industry}` endpoints in `intake_router.py` ✓ (exists per INTAKE_FORM_PHASE2_CANONICAL.md)

**Screens 3–12 (Intake Form):**
- Form submission: `POST /intake` ✓ (exists in `intake_router.py`)
- Validation: all rules in `intake.py` `validate_intake_payload()` ✓
- Database: `intake.py` IntakeRepository handles persistence ✓

**Screen 13 (Confirmation):**
- Requires polling status of site generation (no current status API — consider adding `/intake/{submission_id}/status` for phase 2+)

**Screen 14 (Site Launch):**
- Requires owner dashboard routes (Codex Batch 3 implementing GET `/tenants/{tenant_id}/dashboard` and related endpoints)
- Angel widget: Retell integration (assumed working; confirm scope with team)

---

## Open Questions for Founder Review

1. **Landing-to-intake flow:** Should lead capture (Screen 1) happen on a public marketing page, or is the intake form behind a gate? (Current spec assumes public entry.)
2. **Save-and-resume:** Should users be able to save mid-form and resume later? (Current spec: no; Phase 2+ feature.)
3. **Form layout:** Single-page scrollable form with collapsibles, or multi-step wizard? (Recommend single-page for ~40 fields.)
4. **Site readiness:** What triggers Screen 14 (Site Launch)? Immediately after submission, or after manual review? (Current spec: immediate.)
5. **Lovable integration:** Should "Customize your site" link live on Screen 14, or only in owner dashboard? (Recommend both.)
6. **Email confirmations:** No email sequence in Phase 2 spec; add in Phase 3+?

---

**Document owner:** Claude  
**Last updated:** 2026-08-04  
**Next review:** After founder approval + Codex feasibility check
