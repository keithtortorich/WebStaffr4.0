"""Server-side rendering of customer/tenant sites -- the free, in-repo
alternative to Lovable's Site Weaver (see docs/SITE_RENDERER_PLAN.md for
the full decision record).

Consumes the same public projection GET /sites/{tenant_id} already
returns (build_public_site_data()) -- this module adds no new fields and
therefore cannot leak anything that projection doesn't already expose.
Pure functions only; no DB access lives here. The router
(site_render_router.py) owns the DB round trip and passes the resulting
dict in.

Follows docs/SITE_WEAVER_SEO_BLUEPRINT.md's page architecture, on-page
element patterns, and schema markup -- except the blueprint's Review
schema example, which hardcodes a fabricated rating/review as
boilerplate. This module renders AggregateRating/Review JSON-LD only
from real rating_value/review_count/testimonials fields already present
in the public projection, and omits that block entirely otherwise --
per CLAUDE.md's no-fabrication invariant (see the flag recorded at the
top of the blueprint doc).
"""

from __future__ import annotations

import re
from typing import Optional

from .trade_presets import normalize_industry

_SLUG_PATTERN = re.compile(r"[^a-z0-9]+")

# schema.org has dedicated LocalBusiness subtypes for HVAC/Plumber/
# Electrician/Roofing (all children of the real schema.org
# HomeAndConstructionBusiness type). None of this list's other trades
# have a dedicated schema.org subtype -- rather than invent one (e.g. a
# fabricated "PestControlBusiness" or "TreeServiceBusiness" isn't a real
# schema.org type), they use the real parent type,
# HomeAndConstructionBusiness, directly. Keyed off intake's own
# normalized industry set (trade_presets.SUPPORTED_INDUSTRIES) so this
# never drifts from what the intake form treats as canonical -- adding a
# new industry there means adding one line here.
_SCHEMA_TYPE_BY_INDUSTRY: dict[str, str] = {
    "HVAC": "HVACBusiness",
    "Plumber": "Plumber",
    "Electrician": "Electrician",
    "Roofing": "RoofingContractor",
    "Water Damage Restoration": "HomeAndConstructionBusiness",
    "Garage Door Repair": "HomeAndConstructionBusiness",
    "Pest Control": "HomeAndConstructionBusiness",
    "Landscaping": "HomeAndConstructionBusiness",
    "Tree Service": "HomeAndConstructionBusiness",
    "Cleaning Services": "HomeAndConstructionBusiness",
    "Other": "LocalBusiness",
}


def slugify(text: str) -> str:
    """URL-safe slug for a service name or similar short label. Dash-joined
    per the SEO blueprint's URL convention (intake's own sanitize_slug()
    uses underscores for tenant_id -- a different namespace with a
    different constraint, not reused here on purpose)."""
    slug = _SLUG_PATTERN.sub("-", text.strip().lower()).strip("-")
    return slug or "service"


def schema_business_type(industry: str) -> str:
    """schema.org type for the LocalBusiness JSON-LD block."""
    return _SCHEMA_TYPE_BY_INDUSTRY.get(normalize_industry(industry), "LocalBusiness")


def service_pages(site_data: dict) -> list[dict]:
    """One {name, slug} entry per service in the public site data, in
    submission order. De-duplicates slugs (two differently-worded services
    that happen to slugify to the same string) with a numeric suffix, so no
    two services on one tenant's site collide on URL."""
    seen: dict[str, int] = {}
    pages = []
    for name in site_data.get("services", []):
        base_slug = slugify(name)
        count = seen.get(base_slug, 0)
        seen[base_slug] = count + 1
        slug = base_slug if count == 0 else f"{base_slug}-{count + 1}"
        pages.append({"name": name, "slug": slug})
    return pages


def find_service(site_data: dict, slug: str) -> Optional[dict]:
    """The one service page whose slug matches, or None -- turning that
    into a 404 is the router's job, not this module's."""
    for page in service_pages(site_data):
        if page["slug"] == slug:
            return page
    return None


def has_real_reviews(site_data: dict) -> bool:
    """True only when real rating/review data is present in the public
    projection -- gates the AggregateRating/Review JSON-LD block and the
    /reviews page. This only ever looks at what build_public_site_data()
    actually returned for a real submission, so it can never be true from
    placeholder or example data."""
    return bool(site_data.get("rating_value") and site_data.get("review_count"))


def page_title(site_data: dict, service_name: Optional[str] = None) -> str:
    """`[Service] in [Service Area] | [Business Name]` pattern from the SEO
    blueprint's title-tag convention. Falls back to an industry-based
    homepage title when no specific service is given."""
    biz_name = site_data["biz_name"]
    area = site_data.get("service_area", "")
    if service_name:
        suffix = f" in {area}" if area else ""
        return f"{service_name}{suffix} | {biz_name}"
    industry = site_data.get("industry", "")
    suffix = f" in {area}" if area else ""
    return f"{industry} Services{suffix} | {biz_name}" if industry else biz_name


def meta_description(site_data: dict, service_name: Optional[str] = None) -> str:
    """Meta description built only from real intake fields (tagline,
    differentiator) -- never invented copy. Truncated to a conventional
    ~155 chars so search engines don't cut it off mid-word."""
    biz_name = site_data["biz_name"]
    area = site_data.get("service_area", "")
    parts = [biz_name]
    if service_name:
        parts.append(f"provides {service_name.lower()}" + (f" in {area}" if area else ""))
    else:
        tagline = site_data.get("tagline")
        if tagline:
            parts.append(tagline)
    differentiator = site_data.get("differentiator")
    if differentiator:
        parts.append(differentiator)
    text = ". ".join(p.strip().rstrip(".") for p in parts if p) + "."
    if len(text) > 155:
        text = text[:152].rsplit(" ", 1)[0] + "..."
    return text


def local_business_schema(site_data: dict, page_url: str) -> dict:
    """LocalBusiness (or trade-specific subtype) JSON-LD, built only from
    fields intake actually collects. Deliberately leaner than the SEO
    blueprint's example: this repo's intake form has no street address,
    lat/long, opening-hours, or logo-image fields, so `address`/`geo`/
    `openingHours`/`image` are omitted rather than invented -- the
    no-fabrication invariant applies to schema markup exactly as it does
    to visible copy. `areaServed` uses the freeform `service_area` string
    as a Place name rather than assuming it parses to one City."""
    schema: dict = {
        "@context": "https://schema.org",
        "@type": schema_business_type(site_data.get("industry", "")),
        "name": site_data["biz_name"],
        "url": page_url,
        "telephone": site_data["phone"],
        "email": site_data["email"],
    }
    description = site_data.get("tagline") or site_data.get("differentiator")
    if description:
        schema["description"] = description
    area = site_data.get("service_area")
    if area:
        schema["areaServed"] = {"@type": "Place", "name": area}
    same_as = [
        url for url in (site_data.get("facebook_url"), site_data.get("instagram_url")) if url
    ]
    if same_as:
        schema["sameAs"] = same_as
    if has_real_reviews(site_data):
        schema["aggregateRating"] = {
            "@type": "AggregateRating",
            "ratingValue": site_data["rating_value"],
            "reviewCount": site_data["review_count"],
            "bestRating": 5,
            "worstRating": 1,
        }
    return schema


def service_schema(site_data: dict, service_name: str, page_url: str) -> dict:
    """Service JSON-LD for one service page. No `offers`/price block --
    `pricing_shown` is a yes/no intake flag, not an actual price, and
    inventing one would violate the no-fabrication invariant."""
    schema: dict = {
        "@context": "https://schema.org",
        "@type": "Service",
        "serviceType": service_name,
        "provider": {
            "@type": schema_business_type(site_data.get("industry", "")),
            "name": site_data["biz_name"],
        },
        "url": page_url,
    }
    area = site_data.get("service_area")
    if area:
        schema["areaServed"] = {"@type": "Place", "name": area}
    schema["description"] = meta_description(site_data, service_name)
    return schema


def build_page_context(
    site_data: dict, site_root: str, page_url: str, service_name: Optional[str] = None
) -> dict:
    """Everything a template needs for one page: the raw public site data,
    derived SEO fields (title, meta description, schema type, the
    service-page list, the reviews gate), and the JSON-LD schema dict(s)
    for that specific page. Templates never compute SEO strings or build
    schema themselves -- that logic stays here, in one tested place.

    `site_root` is this tenant's site root (e.g.
    `https://host/sites/{tenant_id}/web`, no trailing slash) -- what nav
    links and the widget's `data-api-base` are built from. `page_url` is
    the full URL of the specific page being rendered -- used for the
    canonical tag and each schema object's own `.url`. Both are supplied
    by the router from the live request; this module stays a pure
    function of its inputs and never guesses its own deployed host.

    No FAQPage schema: the SEO blueprint's FAQ example uses invented
    question/answer copy, and intake collects no structured Q&A content
    to back a real one -- adding fabricated FAQ schema was considered and
    deliberately not built, rather than silently generating filler.
    Same reasoning for individual `Review` objects: `testimonials` is a
    single free-text field with no author/date, so it renders as visible
    page copy only, never as invented structured Review entries."""
    return {
        "site": site_data,
        "title": page_title(site_data, service_name),
        "meta_description": meta_description(site_data, service_name),
        "schema_type": schema_business_type(site_data.get("industry", "")),
        "services": service_pages(site_data),
        "has_reviews": has_real_reviews(site_data),
        "current_service": service_name,
        "site_root": site_root,
        "page_url": page_url,
        "local_business_schema": local_business_schema(site_data, page_url),
        "service_schema": (
            service_schema(site_data, service_name, page_url) if service_name else None
        ),
    }
