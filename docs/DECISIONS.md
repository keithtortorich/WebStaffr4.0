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
**Status:** Proposed  
**Effort:** D2 (1-2 days)

Allows `desertcooling.com` → custom domain instead of `/sites/{tenant_id}/web`.

**Approach:**
- Add `custom_domain` (nullable) column to tenants.
- FastAPI middleware: Host header → tenant lookup.
- Vercel: multiple domains (already supported, zero cost).
- Existing routes work unchanged at domain root.

**Rollout:** After brand colors verified. Low risk, additive.

---

## [ADR-003] Premium Design Variations (Phase 3)

**Date:** 2026-08-01  
**Status:** Backlog

Design variations (modern, minimal, bold) from Silex/Mobirise mockups.

**Defer until founder provides design direction.**

---

**Last updated:** 2026-08-01
