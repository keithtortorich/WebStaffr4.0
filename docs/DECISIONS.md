# Architecture Decisions

## [ADR-001] Brand Color Customization for Rendered Sites

**Date:** 2026-08-01  
**Status:** Approved  
**Affects:** `site_data.py` (public projection), `site_render_router.py` (rendering), `site.css` (template)  
**Effort:** D3 (implementation 2-3 days)

### Problem

All customer sites render with a hardcoded blue palette (#2a6df5 primary, #101826 header). The intake form collects `brand_colors` (primary hex from business logo/brand), but this field is intentionally excluded from the public projection (internal use only).

- **User expectation:** Sites should reflect the business's brand colors.
- **Current reality:** All sites look identical in palette.
- **Tradeoff:** Adding brand_colors to the projection expands attack surface; omitting it keeps the projection minimal.

### Decision

**Expose `brand_colors` to the public projection and inject a dynamic palette at render time.**

1. Add `brand_colors` (nullable hex string) to `build_public_site_data()` output.
2. In `site_render_router.py`, generate a 5-color palette from the brand primary (primary, darker, lighter, neutrals).
3. Inject palette as CSS custom properties into an inline `<style>` block on every page.
4. Validate contrast ratios; log warnings if AA fails, but render anyway (don't block).
5. Test: contrast edge cases, mobile rendering, XSS prevention.

### Rationale

**Why expose it:**
- Direct customer-facing content (not internal ops data).
- Hex color string is low-risk (#rrggbb, no code injection).
- Personalization benefit outweighs minimal risk.

**Why inject dynamically:**
- Stateless rendering (no per-tenant CSS files).
- Fits Vercel serverless model.
- Contrast validation at render time catches bad brand choices.

**Why deterministic algorithm:**
- One primary → automatic palette (HSL-based darkening/lightening).
- Zero designer cost per tenant.
- Fallback to default if brand_colors is null.

### Implementation Stages

**Stage 1:** Add `brand_colors` to public projection + hex validation  
**Stage 2:** Palette generation function (primary → 5-color dict via HSL)  
**Stage 3:** Contrast validation (warn, don't block)  
**Stage 4:** Template injection (CSS vars in `<style>` block)  
**Stage 5:** Tests + docs  

### Trade-offs

| Choice | Benefit | Risk | Mitigation |
|--------|---------|------|-----------|
| Expose brand_colors | Personalization | Slight surface expansion | Hex validation only |
| Deterministic palette | No cost, consistent | May not match intent | Log warnings, manual override in phase 3 |
| Warn on contrast fail | Respects business choice | Poor contrast rendering | Log prominently, email founder weekly |

### Rollout

1. Ship stages 1-4 together.
2. Feature flag: `ENABLE_BRAND_COLORS=true` env var (off by default).
3. Verify on preview deploy with test tenants.
4. Flip to default-on after verification.
5. Monitor contrast warnings weekly.

### Rollback

- Client: override CSS vars in console.
- Server: set `brand_colors = null` for tenant (revert to default).
- Kill switch: `ENABLE_BRAND_COLORS=false` (all sites → default palette).

### Questions for Founder

1. **Contrast enforcement:** Block sites with contrast < 4.5:1, or warn + render?  
   *Current plan: Warn + render.*
2. **Premium design:** Hand-tuned palettes for premium tiers?  
   *Current plan: All deterministic, premium override in phase 3.*

---

## [ADR-002] Custom Domains for Rendered Sites (Phase 2)

**Date:** 2026-08-01  
**Status:** Approved  
**Affects:** `tenants` table, `app.py` (middleware), `site_render_router.py` (documentation)  
**Effort:** D2 (implemented in 1 session)

### Problem

Tenants want to serve sites at custom domains (e.g., `desertcooling.com`) instead of the default `/sites/{tenant_id}/web` path. Presently, all sites live under WebStaffr's path structure with no custom domain support.

### Decision

**Add a `custom_domain` column to tenants and implement path-rewriting middleware to transparently route custom domains to the internal path-based handler.**

### Implementation

1. **Database:** Add `custom_domain` (nullable TEXT, non-unique) column to tenants table.
2. **Resolver:** `resolve_tenant_from_host()` function queries custom_domain column, handles port stripping and case normalization.
3. **Middleware:** `CustomDomainMiddleware` intercepts all requests, checks Host header, resolves tenant_id, rewrites path before FastAPI routing.
   - Custom domain request: `desertcooling.com/about` → internally routed as `/sites/{tenant_id}/web/about`
   - Path-based request: unchanged, routes normally.
   - Non-matching Host: passthrough (no-op).
4. **Routes:** Reuse existing path-based handlers; no route duplication.

### Why Middleware vs Duplicate Routes

- **Avoids routing conflicts:** Identical paths can't have multiple handlers in FastAPI.
- **Centralizes logic:** One place to manage custom domain resolution.
- **Reuses handlers:** Existing path-based rendering pipeline unchanged.
- **Transparent:** Tenant code sees no difference; all routing logic in middleware.

### Trade-offs

| Choice | Benefit | Risk | Mitigation |
|--------|---------|------|-----------|
| Middleware-based | Clean routing, no duplication | Harder to debug | Log Host header and rewritten path on dispatch |
| Nullable column (no unique constraint) | Avoid SQLite migration issues | Application must prevent duplicates | Single query per request (negligible cost) |
| Host header lookup | Automatic domain → tenant resolution | Port parsing complexity | Handle `:` stripping, lowercase normalization |

### Testing

- 12 new unit tests for middleware path rewriting, resolution, isolation.
- All 381 existing tests still pass (zero regressions).
- Tests cover: empty hosts, port stripping, subpaths (services, sitemap, robots), passthrough, state tracking.

### Rollout

1. Ship with brand colors (ADR-001).
2. Feature flag optional (`ENABLE_CUSTOM_DOMAINS=true` env var, off by default).
3. Verify on preview with test tenant pointing to custom domain via DNS.
4. Flip to default-on after validation.

### Rollback

- Remove `custom_domain` value for tenant (revert to path-based).
- Kill switch: stop including `CustomDomainMiddleware` in app.py.

### Future (Phase 3+)

- SSL provisioning for custom domains (Let's Encrypt via Vercel, zero-trust model).
- CNAME validation endpoint (/domain-verification/{token}).
- Dashboard UI for domain management (intake redesign).

---

## [ADR-003] Premium Design Variations (Phase 3)

**Date:** 2026-08-01  
**Status:** Backlog

Design variations (modern, minimal, bold) from Silex/Mobirise mockups.

**Defer until founder provides design direction.**

---

## [ADR-021] WebStaffr Brand Color Doctrine (Locked)

**Date:** 2026-08-03
**Status:** Approved (founder-locked)
**Affects:** `WEBSTAFFR_GOVERNANCE.md` (Visual Identity), Site Magic's default direction, all future WebStaffr-owned marketing surfaces
**Effort:** D1 (doc update, no code change)

### Problem

`WEBSTAFFR_GOVERNANCE.md`'s Visual Identity section (last updated 2026-07-18) specified an approximate two-color logo treatment (gray/gold split, deep blue `#1f4d78` unified) with no defined marketing-site palette. The founder has since built and approved a full landing page (`webstaffr-standalone.html`) with a complete four-color system, dark mode, and a refined logo treatment. That page is now the reference implementation for WebStaffr's own brand identity, and is the basis Site Magic's generator should draw its default direction from.

### Decision

**Lock the following as WebStaffr's canonical color doctrine, superseding the prior approximate values:**

| Token | Hex | Role |
|---|---|---|
| Navy | `#000080` | Primary brand color. Headlines, primary text, unified-logo mark, primary CTA on light backgrounds, hero gradient base. |
| Royal Blue | `#4169E1` | Secondary accent. Links, secondary CTAs, icon accents, focus/interactive states. |
| Orange | `#FF6600` | Highlight/energy accent. Primary CTA fill, "Staffr" wordmark color (both logo variants), focus-visible outline color. |
| Gray | `#E0E0E0` | Neutral surface. Page background, card fills, muted section backgrounds. |

**Supporting tones (extracted from the locked implementation, not independently chosen):**
- Navy scale (light-to-dark UI depth, all four used across surfaces/dark mode): `#000080` -> `#000066` -> `#00005A` -> `#000055` -> `#000040`. Footer: `#00004D`.
- Orange tint (icon backgrounds, light mode): `#FFE0CC`.
- Royal blue pressed state: `#2E4FC9`.
- Muted body text: `#5d6880` (light), standard slate grays in dark mode.
- Success/error states use standard semantic colors (emerald/red), not brand colors -- these were never part of brand identity and stay unchanged.

**Logo (Garamond Bold Italic, one size larger than surrounding text):**
- Split (default, light backgrounds): "Web" `#999999`, "Staffr" `#FF6600`.
- Dark (on navy backgrounds): "Web" `#cccccc`, "Staffr" `#FF6600`.
- Unified (monochrome contexts): both words `#000080`.

This corrects two values in the prior doctrine: "Staffr" moves from gold `#bf9000` to orange `#FF6600`, and the unified variant moves from deep blue `#1f4d78` to navy `#000080`. The gray split color (`#999999`) is unchanged.

**Typography:** Garamond (logo only, italic bold) + Manrope (all UI text, weights 400-800).

### Rationale

The founder built and explicitly locked this palette by reviewing the finished landing page, not by picking hex values in the abstract -- the doctrine here is a transcription of an approved artifact, not a new design decision made by Claude. Recording it as an ADR (rather than only updating the governance doc) preserves the "why" for whoever builds Site Magic's default direction: the palette isn't arbitrary, it's traceable to one approved reference implementation.

### Consequences

- `WEBSTAFFR_GOVERNANCE.md`'s Visual Identity section is updated to match (this ADR is the record of why).
- Site Magic's direction engine, when generating a default/fallback direction (no per-tenant brand override), should treat this four-color system as WebStaffr's own house style -- distinct from the dynamic per-tenant `brand_colors` palette system in `DESIGN.md`, which remains customer-brand-driven and unaffected by this decision.
- Any future WebStaffr-owned marketing surface (investor site, agency site, this landing page) should be checked against this table rather than eyeballed.

### Known gap (logged, not fixed here)

`ADR-020` (em-dash governance rule, 2026-07-30) is referenced in `TASKS.md` and `CLAUDE.md` but was never written into this file. Backfilling it is a separate, trivial doc task -- flagged in `TASKS.md`, not done inline here to keep this ADR scoped to the color decision.

---

**Last updated:** 2026-08-03
