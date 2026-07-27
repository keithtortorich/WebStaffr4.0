"""FastAPI router serving rendered HTML customer/tenant sites -- the
in-repo, Jinja2-based replacement for Lovable's Site Weaver as the
*generation* mechanism (see docs/SITE_RENDERER_PLAN.md for the full
decision record). GET /sites/{tenant_id} (site_router.py) keeps returning
JSON unchanged; this router adds HTML pages alongside it at
/sites/{tenant_id}/web and below.

Mounted into the main app via create_app().include_router(site_render_router),
sibling to site_router, same composition-root rule as every other worker.
"""

from __future__ import annotations

import json
import logging
from datetime import datetime, timezone
from pathlib import Path

from fastapi import APIRouter, HTTPException, Request, Response
from fastapi.templating import Jinja2Templates
from markupsafe import Markup

from .db import DB_ERRORS, get_connection
from .intake import IntakeRepository
from .site_data import build_public_site_data
from .site_renderer import build_page_context, find_service, has_real_reviews
from .tenant import InvalidTenantError, Tenant

logger = logging.getLogger("webstaffr.site_render_router")

site_render_router = APIRouter()

_TEMPLATES_DIR = Path(__file__).parent / "templates"
_STATIC_SITE_CSS = Path(__file__).parent / "templates" / "site" / "static" / "site.css"
_STATIC_WIDGET_JS = Path(__file__).parent / "workers" / "angel" / "widget" / "angel-widget.js"


def _tojson_script(value) -> Markup:
    """JSON for embedding inside a <script type="application/ld+json">
    block. Escapes characters that would otherwise let attacker-controlled
    string content (e.g. a business's own tagline or testimonials text)
    break out of the script context -- same escaping Flask's `tojson`
    filter applies, reimplemented here since Starlette's Jinja2Templates
    doesn't ship it."""
    return Markup(
        json.dumps(value)
        .replace("<", "\\u003c")
        .replace(">", "\\u003e")
        .replace("&", "\\u0026")
        .replace("'", "\\u0027")
    )


templates = Jinja2Templates(directory=str(_TEMPLATES_DIR))
templates.env.filters["tojson_script"] = _tojson_script


def _get_connection(request: Request):
    """Same pattern as site_router.py's _get_connection() -- 503 on a
    DB-layer failure, never a raw psycopg2/sqlite3 exception (or its
    connection-string-bearing message) reaching the client."""
    try:
        return get_connection(request.app.state.db_path)
    except DB_ERRORS as exc:
        logger.error("site_render_db_connection_failed error_type=%s", type(exc).__name__)
        raise HTTPException(status_code=503, detail="Site data temporarily unavailable") from exc


def _load_site_data(tenant_id: str, request: Request) -> dict:
    """Tenant validation + latest-submission load + the same public
    projection GET /sites/{tenant_id} returns as JSON. 404 either way
    (invalid tenant_id vs. no submission yet) -- no information leakage
    about which tenant_ids are valid, same as site_router.py."""
    try:
        Tenant(tenant_id=tenant_id)
    except InvalidTenantError as exc:
        raise HTTPException(status_code=404, detail="No site found for this tenant") from exc

    conn = _get_connection(request)
    try:
        submission = IntakeRepository(conn).load_latest_for_tenant(tenant_id)
    finally:
        conn.close()

    if submission is None:
        raise HTTPException(status_code=404, detail="No site found for this tenant")

    return build_public_site_data(submission)


def _site_root(request: Request, tenant_id: str) -> str:
    return f"{str(request.base_url).rstrip('/')}/sites/{tenant_id}/web"


def _render(request: Request, template_name: str, site_data: dict, tenant_id: str, *, path: str = "", service_name=None) -> Response:
    site_root = _site_root(request, tenant_id)
    context = build_page_context(
        site_data,
        site_root=site_root,
        page_url=f"{site_root}{path}",
        service_name=service_name,
    )
    context["current_year"] = datetime.now(timezone.utc).year
    context["api_base"] = str(request.base_url).rstrip("/")
    return templates.TemplateResponse(request, f"site/{template_name}", context)


@site_render_router.get("/sites/{tenant_id}/web")
def render_home(tenant_id: str, request: Request) -> Response:
    site_data = _load_site_data(tenant_id, request)
    return _render(request, "home.html", site_data, tenant_id)


@site_render_router.get("/sites/{tenant_id}/web/about")
def render_about(tenant_id: str, request: Request) -> Response:
    site_data = _load_site_data(tenant_id, request)
    return _render(request, "about.html", site_data, tenant_id, path="/about")


@site_render_router.get("/sites/{tenant_id}/web/contact")
def render_contact(tenant_id: str, request: Request) -> Response:
    site_data = _load_site_data(tenant_id, request)
    return _render(request, "contact.html", site_data, tenant_id, path="/contact")


@site_render_router.get("/sites/{tenant_id}/web/reviews")
def render_reviews(tenant_id: str, request: Request) -> Response:
    site_data = _load_site_data(tenant_id, request)
    if not has_real_reviews(site_data):
        # No real rating/review data on file -- the page simply doesn't
        # exist rather than rendering an empty or fabricated reviews page.
        raise HTTPException(status_code=404, detail="No reviews on file for this tenant")
    return _render(request, "reviews.html", site_data, tenant_id, path="/reviews")


@site_render_router.get("/sites/{tenant_id}/web/services/{service_slug}")
def render_service(tenant_id: str, service_slug: str, request: Request) -> Response:
    site_data = _load_site_data(tenant_id, request)
    service = find_service(site_data, service_slug)
    if service is None:
        raise HTTPException(status_code=404, detail="No such service for this tenant")
    return _render(
        request,
        "service.html",
        site_data,
        tenant_id,
        path=f"/services/{service_slug}",
        service_name=service["name"],
    )


@site_render_router.get("/sites/{tenant_id}/web/sitemap.xml")
def render_sitemap(tenant_id: str, request: Request) -> Response:
    site_data = _load_site_data(tenant_id, request)
    site_root = _site_root(request, tenant_id)
    context = build_page_context(site_data, site_root=site_root, page_url=site_root)
    body = templates.get_template("site/sitemap.xml").render(context)
    return Response(content=body, media_type="application/xml")


@site_render_router.get("/sites/{tenant_id}/web/robots.txt")
def render_robots(tenant_id: str, request: Request) -> Response:
    site_data = _load_site_data(tenant_id, request)
    site_root = _site_root(request, tenant_id)
    context = build_page_context(site_data, site_root=site_root, page_url=site_root)
    body = templates.get_template("site/robots.txt").render(context)
    return Response(content=body, media_type="text/plain")


# Static assets shared by every tenant's rendered site. Explicit routes
# (rather than a StaticFiles mount) keep this dependency-minimal -- no
# aiofiles requirement, no extra directory-traversal surface to reason
# about, and both files are small enough that reading them fresh per
# request costs nothing measurable on Vercel's serverless model.
@site_render_router.get("/static/site.css")
def static_site_css() -> Response:
    return Response(content=_STATIC_SITE_CSS.read_text(), media_type="text/css")


@site_render_router.get("/static/angel-widget.js")
def static_angel_widget_js() -> Response:
    return Response(content=_STATIC_WIDGET_JS.read_text(), media_type="application/javascript")
