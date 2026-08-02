"""WebStaffr Agency Site — company marketing site, not customer sites.

Served at GET /agency/* using Jinja2 templates with the new brand palette
(teal + gold + copper). Copy from WEBSTAFFR_AGENCY_SITE_COPY_HORMOZI_VOSS.md.
Design from WEBSTAFFR_AGENCY_SITE_DESIGN_DIRECTION.md.

Vercel-safe: Template content is pre-compiled at import time, not loaded from
disk at request time. This avoids filesystem path resolution issues on serverless.
"""

from __future__ import annotations

import os
from fastapi import APIRouter
from fastapi.responses import HTMLResponse
from jinja2 import Environment, DictLoader

agency_router = APIRouter(tags=["agency"])


def _load_template_content(filename: str) -> str:
    """Load template content from disk at import time (module load)."""
    template_dir = os.path.join(os.path.dirname(__file__), "templates", "agency")
    with open(os.path.join(template_dir, filename), "r", encoding="utf-8") as f:
        return f.read()


# Pre-compile templates at import time using DictLoader.
# This avoids Vercel filesystem path issues at request time.
_TEMPLATES = {
    "base.html": _load_template_content("base.html"),
    "home.html": _load_template_content("home.html"),
    "how_it_works.html": _load_template_content("how_it_works.html"),
    "pricing.html": _load_template_content("pricing.html"),
    "faq.html": _load_template_content("faq.html"),
    "about.html": _load_template_content("about.html"),
    "contact.html": _load_template_content("contact.html"),
}

_jinja_env = Environment(
    loader=DictLoader(_TEMPLATES),
    autoescape=True,
)


@agency_router.get("/agency", response_class=HTMLResponse)
@agency_router.get("/agency/", response_class=HTMLResponse)
async def agency_home():
    """Serve the agency home page."""
    template = _jinja_env.get_template("home.html")
    return HTMLResponse(content=template.render())


@agency_router.get("/agency/how-it-works", response_class=HTMLResponse)
async def agency_how_it_works():
    """Serve the 'How It Works' page."""
    template = _jinja_env.get_template("how_it_works.html")
    return HTMLResponse(content=template.render())


@agency_router.get("/agency/pricing", response_class=HTMLResponse)
async def agency_pricing():
    """Serve the pricing page."""
    template = _jinja_env.get_template("pricing.html")
    return HTMLResponse(content=template.render())


@agency_router.get("/agency/faq", response_class=HTMLResponse)
async def agency_faq():
    """Serve the FAQ page."""
    template = _jinja_env.get_template("faq.html")
    return HTMLResponse(content=template.render())


@agency_router.get("/agency/about", response_class=HTMLResponse)
async def agency_about():
    """Serve the About page."""
    template = _jinja_env.get_template("about.html")
    return HTMLResponse(content=template.render())


@agency_router.get("/agency/contact", response_class=HTMLResponse)
async def agency_contact():
    """Serve the Contact page."""
    template = _jinja_env.get_template("contact.html")
    return HTMLResponse(content=template.render())
