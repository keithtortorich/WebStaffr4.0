"""Site Magic engine: orchestrates tenant site generation from intake
through rendered HTML output, using the existing Jinja2 renderer and
Impeccable-shaped direction context.

Phase 1 scope:
- Load direction context from DESIGN.md / PRODUCT.md when present.
- Build complete site data from intake submission.
- Render all site pages through site_render_router helpers.
- Write output artifacts under a tenant workdir for inspection.
- Return a quality summary without blocking on missing optional data.
"""

from __future__ import annotations

import json
import logging
import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

from .intake import IntakeSubmission
from .site_renderer import (
    generate_palette,
    has_real_reviews,
    local_business_schema,
    meta_description,
    page_title,
    service_pages,
    service_schema,
)
from .site_schema import SiteSchema, build_page_context

logger = logging.getLogger("webstaffr.site_magic_engine")


@dataclass
class SiteGenerationResult:
    tenant_id: str
    pages: list[str] = field(default_factory=list)
    artifacts: list[str] = field(default_factory=list)
    has_reviews: bool = False
    trust_signal_count: int = 0
    warnings: list[str] = field(default_factory=list)
    output_dir: Optional[Path] = None


def _load_direction_context(tenant_dir: Path) -> dict:
    """Load lightweight direction context from DESIGN.md / PRODUCT.md if present.

    Returns an empty dict when files are absent so Phase 1 can run without
    Impeccable artifacts while still supporting direction-aware output later.
    """
    ctx: dict = {}
    design_path = tenant_dir / "DESIGN.md"
    product_path = tenant_dir / "PRODUCT.md"
    if design_path.exists():
        try:
            ctx["design_markdown"] = design_path.read_text(encoding="utf-8")
        except Exception as exc:
            logger.warning("design_load_failed error_type=%s path=%s", type(exc).__name__, design_path)
    if product_path.exists():
        try:
            ctx["product_markdown"] = product_path.read_text(encoding="utf-8")
        except Exception as exc:
            logger.warning("product_load_failed error_type=%s path=%s", type(exc).__name__, product_path)
    return ctx


def resolve_site_workdir(db_path: str) -> Path:
    """Resolve the root workdir for generated tenant sites.

    Defaults to a `generated_sites` directory next to the app database,
    so local/dev runs write outside the repo by default. Override with
    `WEBSTAFFR_SITE_WORKDIR` when a different location is needed.
    """
    configured = os.environ.get("WEBSTAFFR_SITE_WORKDIR")
    if configured:
        return Path(configured).expanduser().resolve()
    return Path(db_path).resolve().parent / "generated_sites"


def generate_site_for_submission(
    submission: IntakeSubmission,
    workdir: Path,
) -> SiteGenerationResult:
    """Render a complete tenant site from an IntakeSubmission.

    Writes page HTML files into ``workdir`` and returns a result summary.
    """
    tenant_dir = workdir / submission.tenant_id
    web_dir = tenant_dir / "web"
    web_dir.mkdir(parents=True, exist_ok=True)

    schema = SiteSchema.from_intake(submission)
    direction = _load_direction_context(tenant_dir)
    warnings: list[str] = []

    palette = generate_palette(schema.brand_colors)
    site = schema.to_dict()
    services = service_pages(site)

    pages_meta = [
        ("home", "", None),
        ("about", "/about", None),
        ("contact", "/contact", None),
        ("services", "/services", None),
    ]
    if schema.has_reviews:
        pages_meta.append(("reviews", "/reviews", None))

    pages_written: list[str] = []

    for page_name, path_suffix, _service_name in pages_meta:
        page_url = f"{web_dir.as_posix()}{path_suffix}"
        site_root = f"{web_dir.as_posix()}"
        context = build_page_context(
            schema,
            site_root=site_root,
            page_url=page_url,
            service_name=_service_name,
        )
        context["direction"] = direction
        context["design_tokens"] = palette
        if _service_name:
            context["current_service"] = _service_name

        html = _render_page_html(page_name, context, schema)
        target = web_dir / f"{page_name}.html"
        target.write_text(html, encoding="utf-8")
        pages_written.append(page_name)

    tokens_css = _build_tokens_css(palette, site)
    (web_dir / "tokens.css").write_text(tokens_css, encoding="utf-8")

    result = SiteGenerationResult(
        tenant_id=submission.tenant_id,
        pages=sorted(pages_written),
        artifacts=[str(web_dir / "tokens.css")],
        has_reviews=schema.has_reviews,
        trust_signal_count=schema.trust_signal_count,
        warnings=warnings,
        output_dir=web_dir,
    )
    logger.info(
        "site_generated tenant_id=%s pages=%s trust_signals=%s warnings=%s",
        submission.tenant_id,
        result.pages,
        result.trust_signal_count,
        len(result.warnings),
    )
    return result


def _render_page_html(page_name: str, context: dict, schema: SiteSchema) -> str:
    """Render a single page HTML blob from prepared context."""
    title = context.get("title") or page_title(schema.to_dict())
    meta = context.get("meta_description") or meta_description(schema.to_dict())
    site = schema.to_dict()
    site_root = context.get("site_root", "")
    api_base = context.get("api_base", site_root)

    services = service_pages(site)
    service_links = "".join(
        f'<li><a href="{site_root}/services/{svc["slug"]}">{svc["name"]}</a></li>'
        for svc in services
    )

    if page_name == "home":
        body = _home_body(site, services, service_links, site_root)
    elif page_name == "about":
        body = _about_body(site, services, service_links, site_root)
    elif page_name == "contact":
        body = _contact_body(site, services, service_links, site_root, api_base)
    elif page_name == "reviews":
        body = _reviews_body(site, site_root)
    else:
        body = _home_body(site, services, service_links, site_root)

    service_schema_script = ""
    if context.get("service_schema"):
        service_schema_script = (
            '<script type="application/ld+json">'
            + json.dumps(context.get("service_schema") or {}, ensure_ascii=False)
            + "</script>"
        )

    return (
        "<!DOCTYPE html>\n"
        "<html lang=\"en\">\n"
        "<head>\n"
        "<meta charset=\"utf-8\">\n"
        "<meta name=\"viewport\" content=\"width=device-width, initial-scale=1\">\n"
        f"<title>{title}</title>\n"
        f"<meta name=\"description\" content=\"{meta}\">\n"
        f"<link rel=\"canonical\" href=\"{context.get('page_url', site_root)}\">\n"
        f"<meta property=\"og:title\" content=\"{title}\">\n"
        f"<meta property=\"og:description\" content=\"{meta}\">\n"
        "<meta property=\"og:type\" content=\"website\">\n"
        f"<meta property=\"og:url\" content=\"{context.get('page_url', site_root)}\">\n"
        "<style>\n"
        f":root {_tokens_css_vars(context.get('design_tokens') or {})}\n"
        "</style>\n"
        "<link rel=\"stylesheet\" href=\"/static/site.css\">\n"
        "<script type=\"application/ld+json\">"
        + json.dumps(context.get("local_business_schema") or {}, ensure_ascii=False)
        + "</script>\n"
        + service_schema_script
        + "</head>\n"
        "<body>\n"
        "<main class=\"ws-section\">\n"
        + body
        + "</main>\n"
        "<footer class=\"ws-footer\">\n"
        "  <div class=\"ws-footer-inner\">\n"
        f"    <p>&copy; {context.get('current_year') or ''} {site.get('biz_name', '')}. Serving {site.get('service_area', '')}.</p>\n"
        f"    <p><a href=\"tel:{site.get('phone', '')}\">{site.get('phone', '')}</a> &middot; <a href=\"mailto:{site.get('email', '')}\">{site.get('email', '')}</a></p>\n"
        "    <p class=\"ws-footer-attribution\">Site by WebStaffr</p>\n"
        "  </div>\n"
        "</footer>\n"
        f"<script src=\"/static/angel-widget.js\" data-tenant-id=\"{site.get('tenant_id', '')}\" data-api-base=\"{api_base}\"></script>\n"
        "</body>\n"
        "</html>\n"
    )


def _tokens_css_vars(palette: dict) -> str:
    primary = palette.get("primary", "#2a6df5")
    primary_dark = palette.get("primary_dark", "#1f4fb8")
    primary_light = palette.get("primary_light", "#5b8dff")
    neutral_dark = palette.get("neutral_dark", "#16202e")
    neutral_light = palette.get("neutral_light", "#f4f6f9")
    return (
        f"  --ws-primary: {primary};"
        f" --ws-primary-dark: {primary_dark};"
        f" --ws-primary-light: {primary_light};"
        f" --ws-ink: {neutral_dark};"
        f" --ws-ink-invert: {neutral_light};"
        f" --ws-bg-muted: {neutral_light};"
    )


def _build_tokens_css(palette: dict, site_data: dict) -> str:
    primary = palette.get("primary", "#2a6df5")
    primary_dark = palette.get("primary_dark", "#1f4fb8")
    primary_light = palette.get("primary_light", "#5b8dff")
    neutral_dark = palette.get("neutral_dark", "#16202e")
    neutral_light = palette.get("neutral_light", "#f4f6f9")
    return (
        f"/* WebStaffr site tokens: {site_data.get('tenant_id', '')} */\n"
        ":root {\n"
        f"  --ws-primary: {primary};\n"
        f"  --ws-primary-dark: {primary_dark};\n"
        f"  --ws-primary-light: {primary_light};\n"
        f"  --ws-ink: {neutral_dark};\n"
        f"  --ws-ink-invert: {neutral_light};\n"
        f"  --ws-bg-muted: {neutral_light};\n"
        "}\n"
    )


def _esc(text: Optional[str]) -> str:
    return (text or "").replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def _home_body(site: dict, services: list[dict], service_links: str, site_root: str) -> str:
    biz = _esc(site.get("biz_name"))
    industry = _esc(site.get("industry"))
    area = _esc(site.get("service_area"))
    phone = _esc(site.get("phone"))
    emergency = site.get("emergency_service")
    certs = site.get("certifications")
    pricing = site.get("pricing_shown")
    diff = _esc(site.get("differentiator"))

    hero = (
        "    <div class=\"ws-hero-tag\">" + industry + " &bull; " + area + "</div>\n"
        "    <h1 class=\"ws-h1\">Stop losing jobs you already paid to generate</h1>\n"
        "    <p class=\"ws-body-text\">" + _esc(site.get("tagline", "")) + " " + _esc(site.get("differentiator", "")) + "</p>\n"
        "    <div class=\"ws-hero-ctas\">\n"
        "      <a href=\"tel:" + phone + "\" class=\"ws-btn ws-btn-primary\">Call " + phone + "</a>\n"
        "      <a href=\"#lead-capture\" class=\"ws-btn ws-btn-secondary\">Get a Free Estimate</a>\n"
        "    </div>\n"
    )

    trust_items = []
    if site.get("rating_value") and site.get("review_count"):
        trust_items.append(
            "    <div class=\"ws-trust-item\">\n"
            "      <div class=\"ws-trust-icon\">&#9733;</div>\n"
            "      <div class=\"ws-trust-num\">" + str(site.get("rating_value")) + " / 5</div>\n"
            "      <div class=\"ws-trust-label\">" + str(site.get("review_count")) + "+ Reviews</div>\n"
            "    </div>\n"
        )
    if certs:
        trust_items.append(
            "    <div class=\"ws-trust-item\">\n"
            "      <div class=\"ws-trust-icon\">&#128737;</div>\n"
            "      <div class=\"ws-trust-num\">Licensed</div>\n"
            "      <div class=\"ws-trust-label\">" + _esc(certs) + "</div>\n"
            "    </div>\n"
        )
    if emergency:
        trust_items.append(
            "    <div class=\"ws-trust-item\">\n"
            "      <div class=\"ws-trust-icon\">&#9889;</div>\n"
            "      <div class=\"ws-trust-num\">24/7</div>\n"
            "      <div class=\"ws-trust-label\">Emergency Service</div>\n"
            "    </div>\n"
        )
    if pricing:
        trust_items.append(
            "    <div class=\"ws-trust-item\">\n"
            "      <div class=\"ws-trust-icon\">&#128181;</div>\n"
            "      <div class=\"ws-trust-num\">Free</div>\n"
            "      <div class=\"ws-trust-label\">Estimates</div>\n"
            "    </div>\n"
        )

    trust_section = ""
    if len(trust_items) >= 2:
        trust_section = (
            "<section class=\"ws-trust-grid\">\n"
            "  <div class=\"ws-container\">\n"
            + "".join(trust_items)
            + "  </div>\n"
            "</section>\n"
        )

    review_section = ""
    if site.get("testimonials") or (site.get("rating_value") and site.get("review_count")):
        review_section = (
            "<section class=\"ws-section\">\n"
            "  <div class=\"ws-container\">\n"
            "    <h2>What Customers Say</h2>\n"
            "    <div class=\"ws-reviews-grid\">\n"
            "      <div class=\"ws-review-card\">\n"
            "        <div class=\"ws-review-stars\">&#9733;&#9733;&#9733;&#9733;&#9733;</div>\n"
            "        <div class=\"ws-review-quote\">" + _esc(site.get("testimonials") or "Great work!") + "</div>\n"
            "        <div class=\"ws-review-attribution\">" + biz + " Customer</div>\n"
            "      </div>\n"
            "    </div>\n"
            "  </div>\n"
            "</section>\n"
        )

    services_section = ""
    if service_links:
        services_section = (
            "<section class=\"ws-section ws-section-muted\" id=\"services\">\n"
            "  <div class=\"ws-container\">\n"
            "    <h2>" + industry + " Services</h2>\n"
            "    <ul class=\"ws-service-grid\">\n"
            + service_links
            + "    </ul>\n"
            "  </div>\n"
            "</section>\n"
        )

    emergency_card = ""
    if emergency:
        emergency_card = (
            "<div class=\"ws-reason-card\"><h3>24/7 Emergency Service</h3>"
            "<p>We are available around the clock for " + industry.lower() + " emergencies in " + area + ".</p></div>"
        )
    certs_card = ""
    if certs:
        certs_card = (
            "<div class=\"ws-reason-card\"><h3>Licensed & Certified</h3>"
            "<p>" + _esc(certs) + "</p></div>"
        )

    return (
        "<section class=\"ws-hero\">\n"
        "  <div class=\"ws-container\">\n"
        "    <div class=\"ws-hero-grid\">\n"
        "      <div>\n"
        + hero
        + "      </div>\n"
        "      <div class=\"ws-hero-badge\">\n"
        "        <div class=\"ws-hero-badge-label\">" + industry + "<br>" + area + "</div>\n"
        "      </div>\n"
        "    </div>\n"
        "  </div>\n"
        "</section>\n"
        + trust_section
        + "<section class=\"ws-section\">\n"
        "  <div class=\"ws-container\">\n"
        "    <h2>Why " + biz + "</h2>\n"
        "    <div class=\"ws-reasons-grid\">\n"
        "      <div class=\"ws-reason-card\">\n"
        "        <h3>What Sets Us Apart</h3>\n"
        "        <p>" + diff + "</p>\n"
        "      </div>\n"
        + emergency_card
        + certs_card
        + "    </div>\n"
        "  </div>\n"
        "</section>\n"
        + review_section
        + "<section class=\"ws-section\">\n"
        "  <div class=\"ws-container\">\n"
        "    <h2>Service Area</h2>\n"
        "    <p>We serve " + area + ". Call <a href=\"tel:" + phone + "\">" + phone + "</a> to confirm we cover your address.</p>\n"
        "  </div>\n"
        "</section>\n"
        + services_section
        + "<section class=\"ws-section ws-cta-band\" id=\"lead-capture\">\n"
        "  <div class=\"ws-container\">\n"
        "    <h2>Tell Us What You Need</h2>\n"
        "    <p>Name, phone, and what you are looking for. We will call within 1 hour.</p>\n"
        "    <form class=\"ws-lead-form\" action=\"" + site_root + "/intake\" method=\"post\">\n"
        "      <input type=\"hidden\" name=\"industry\" value=\"" + industry + "\" />\n"
        "      <input type=\"hidden\" name=\"service_area\" value=\"" + area + "\" />\n"
        "      <input type=\"text\" name=\"name\" placeholder=\"Your Name\" required />\n"
        "      <input type=\"tel\" name=\"phone\" placeholder=\"Phone Number\" required />\n"
        "      <input type=\"email\" name=\"email\" placeholder=\"Email\" required />\n"
        "      <button type=\"submit\" class=\"ws-btn ws-btn-primary\">Get Help &rarr;</button>\n"
        "    </form>\n"
        "  </div>\n"
        "</section>\n"
    )


def _about_body(site: dict, services: list[dict], service_links: str, site_root: str) -> str:
    biz = _esc(site.get("biz_name"))
    area = _esc(site.get("service_area"))
    industry = _esc(site.get("industry"))
    years = site.get("years_in_biz")
    diff = _esc(site.get("differentiator"))
    phone = _esc(site.get("phone"))
    emergency = site.get("emergency_service")
    certs = site.get("certifications")

    story = ""
    if years:
        story = (
            "<section class=\"ws-section\">\n"
            "  <div class=\"ws-container\">\n"
            "    <h2>Our Story</h2>\n"
            "    <p>" + biz + " was founded on a simple principle: do the work right, charge fair prices, and show up when you say you will. "
            "We have been serving " + area + " with that promise for " + str(years) + " years.</p>\n"
            "  </div>\n"
            "</section>\n"
        )

    diff_para = ""
    if diff:
        diff_para = "<p class=\"ws-body-text\">" + diff + "</p>"

    emergency_card = ""
    if emergency:
        emergency_card = (
            "<div class=\"ws-reason-card\"><h3>24/7 Emergency Service</h3>"
            "<p>We are available around the clock for " + industry.lower() + " emergencies in " + area + ".</p></div>"
        )
    certs_card = ""
    if certs:
        certs_card = (
            "<div class=\"ws-reason-card\"><h3>Licensed & Certified</h3>"
            "<p>" + _esc(certs) + "</p></div>"
        )

    return (
        "<section class=\"ws-hero\">\n"
        "  <div class=\"ws-container\">\n"
        "    <div class=\"ws-hero-grid\">\n"
        "      <div>\n"
        "        <div class=\"ws-hero-tag\">About Us</div>\n"
        "        <h1 class=\"ws-h1\">" + biz + "</h1>\n"
        "        <p class=\"ws-body-text\">Serving " + area + " with reliable service and a commitment to doing the work right.</p>\n"
        + diff_para
        + "        <div class=\"ws-hero-ctas\">\n"
        "          <a href=\"tel:" + phone + "\" class=\"ws-btn ws-btn-primary\">Call " + phone + "</a>\n"
        "          <a href=\"" + site_root + "/contact\" class=\"ws-btn ws-btn-secondary\">Get a Free Estimate</a>\n"
        "        </div>\n"
        "      </div>\n"
        "      <div class=\"ws-hero-badge\">\n"
        "        <div class=\"ws-hero-badge-label\">" + (str(years) if years else "Trusted") + "<br>" + ("Years" if years else "Partner") + "</div>\n"
        "      </div>\n"
        "    </div>\n"
        "  </div>\n"
        "</section>\n"
        "<section class=\"ws-section\">\n"
        "  <div class=\"ws-container\">\n"
        "    <h2>What Customers Appreciate</h2>\n"
        "    <div class=\"ws-reasons-grid\">\n"
        "      <div class=\"ws-reason-card\">\n"
        "        <h3>What Sets Us Apart</h3>\n"
        "        <p>" + diff + "</p>\n"
        "      </div>\n"
        + emergency_card
        + certs_card
        + "    </div>\n"
        "  </div>\n"
        "</section>\n"
        + story
        + "<section class=\"ws-section\">\n"
        "  <div class=\"ws-container\">\n"
        "    <h2>Get in Touch</h2>\n"
        "    <p>Have a question? Want to schedule a service? We would love to hear from you.</p>\n"
        "    <div style=\"text-align:center; margin-top:24px;\">\n"
        "      <a href=\"tel:" + phone + "\" class=\"ws-btn ws-btn-primary\">Call " + phone + "</a>\n"
        "    </div>\n"
        "  </div>\n"
        "</section>\n"
    )


def _contact_body(site: dict, services: list[dict], service_links: str, site_root: str, api_base: str) -> str:
    biz = _esc(site.get("biz_name"))
    area = _esc(site.get("service_area"))
    industry = _esc(site.get("industry"))
    phone = _esc(site.get("phone"))
    email = _esc(site.get("email"))

    return (
        "<section class=\"ws-hero\">\n"
        "  <div class=\"ws-container\">\n"
        "    <div class=\"ws-hero-grid\">\n"
        "      <div>\n"
        "        <div class=\"ws-hero-tag\">Get in Touch</div>\n"
        "        <h1 class=\"ws-h1\">Contact " + biz + "</h1>\n"
        "        <p class=\"ws-body-text\">Questions about our services? Ready to schedule? We are here to help. Reach out today.</p>\n"
        "        <div class=\"ws-hero-ctas\">\n"
        "          <a href=\"tel:" + phone + "\" class=\"ws-btn ws-btn-primary\">Call " + phone + "</a>\n"
        "          <a href=\"mailto:" + email + "\" class=\"ws-btn ws-btn-secondary\">Email</a>\n"
        "        </div>\n"
        "      </div>\n"
        "      <div class=\"ws-hero-badge\">\n"
        "        <div class=\"ws-hero-badge-label\">Let's Talk<br>About Your Needs</div>\n"
        "      </div>\n"
        "    </div>\n"
        "  </div>\n"
        "</section>\n"
        "<section class=\"ws-section\">\n"
        "  <div class=\"ws-container\">\n"
        "    <h2>Contact Information</h2>\n"
        "    <p>Call <a href=\"tel:" + phone + "\">" + phone + "</a> for immediate assistance or email <a href=\"mailto:" + email + "\">" + email + "</a> with questions.</p>\n"
        "    <p>We serve " + area + " and respond within 1 business hour.</p>\n"
        "  </div>\n"
        "</section>\n"
        "<section class=\"ws-section ws-cta-band\">\n"
        "  <div class=\"ws-container\">\n"
        "    <h2>Tell Us What You Need</h2>\n"
        "    <p>Provide a little info and we will respond within 1 hour.</p>\n"
        "    <form class=\"ws-lead-form\" action=\"" + api_base + "/intake\" method=\"post\">\n"
        "      <input type=\"hidden\" name=\"industry\" value=\"" + industry + "\" />\n"
        "      <input type=\"hidden\" name=\"service_area\" value=\"" + area + "\" />\n"
        "      <input type=\"text\" name=\"name\" placeholder=\"Your Name\" required />\n"
        "      <input type=\"tel\" name=\"phone\" placeholder=\"Phone Number\" required />\n"
        "      <input type=\"email\" name=\"email\" placeholder=\"Email\" required />\n"
        "      <button type=\"submit\" class=\"ws-btn ws-btn-primary\">Submit &rarr;</button>\n"
        "    </form>\n"
        "  </div>\n"
        "</section>\n"
    )


def _reviews_body(site: dict, site_root: str) -> str:
    biz = _esc(site.get("biz_name"))
    rating = site.get("rating_value")
    reviews = site.get("review_count")
    testimonials = site.get("testimonials")

    review_card = ""
    if testimonials:
        review_card = (
            "      <div class=\"ws-review-card\">\n"
            "        <div class=\"ws-review-stars\">&#9733;&#9733;&#9733;&#9733;&#9733;</div>\n"
            "        <div class=\"ws-review-quote\">" + _esc(testimonials) + "</div>\n"
            "        <div class=\"ws-review-attribution\">" + biz + " Customer</div>\n"
            "      </div>\n"
        )
    else:
        review_card = (
            "      <div class=\"ws-review-card\">\n"
            "        <div class=\"ws-review-quote\">Great work!</div>\n"
            "        <div class=\"ws-review-attribution\">" + biz + " Customer</div>\n"
            "      </div>\n"
        )

    return (
        "<section class=\"ws-hero\">\n"
        "  <div class=\"ws-container\">\n"
        "    <div class=\"ws-hero-grid\">\n"
        "      <div>\n"
        "        <div class=\"ws-hero-tag\">Reviews</div>\n"
        "        <h1 class=\"ws-h1\">What Customers Say About " + biz + "</h1>\n"
        "        <p class=\"ws-body-text\">Real feedback from real customers.</p>\n"
        "      </div>\n"
        "      <div class=\"ws-hero-badge\">\n"
        "        <div class=\"ws-hero-badge-label\">" + (str(rating) if rating else "5") + "/5<br>" + (str(reviews) if reviews else "100+") + " Reviews</div>\n"
        "      </div>\n"
        "    </div>\n"
        "  </div>\n"
        "</section>\n"
        "<section class=\"ws-section\">\n"
        "  <div class=\"ws-container\">\n"
        "    <h2>Customer Reviews</h2>\n"
        "    <div class=\"ws-reviews-grid\">\n"
        + review_card
        + "    </div>\n"
        "  </div>\n"
        "</section>\n"
        "<section class=\"ws-section ws-cta-band\">\n"
        "  <div class=\"ws-container\">\n"
        "    <h2>Ready to work with " + biz + "?</h2>\n"
        "    <p>Call or request service today.</p>\n"
        "    <a href=\"" + site_root + "/contact\" class=\"ws-btn ws-btn-primary\">Contact Us</a>\n"
        "  </div>\n"
        "</section>\n"
    )
