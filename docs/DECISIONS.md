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

**Last updated:** 2026-08-01
