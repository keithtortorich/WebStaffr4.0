"""WebStaffr Agency Site — company marketing site, not customer sites.

Served at GET /agency/* using Jinja2 templates with the new brand palette
(teal + gold + copper). Copy from WEBSTAFFR_AGENCY_SITE_COPY_HORMOZI_VOSS.md.
Design from WEBSTAFFR_AGENCY_SITE_DESIGN_DIRECTION.md.
"""

from __future__ import annotations

import os
from fastapi import APIRouter
from fastapi.responses import HTMLResponse
from jinja2 import Environment, FileSystemLoader

agency_router = APIRouter(tags=["agency"])

def _get_jinja_env():
    """Lazily load Jinja2 environment on first use."""
    template_dir = os.path.join(os.path.dirname(__file__), "templates", "agency")
    return Environment(
        loader=FileSystemLoader(template_dir),
        autoescape=True,
    )


@agency_router.get("/agency", response_class=HTMLResponse)
@agency_router.get("/agency/", response_class=HTMLResponse)
async def agency_home():
    """Serve the agency home page."""
    jinja_env = _get_jinja_env()
    template = jinja_env.get_template("home.html")
    return HTMLResponse(content=template.render())


@agency_router.get("/agency/how-it-works", response_class=HTMLResponse)
async def agency_how_it_works():
    """Serve the 'How It Works' page."""
    jinja_env = _get_jinja_env()
    template = jinja_env.get_template("how_it_works.html")
    return HTMLResponse(content=template.render())


@agency_router.get("/agency/pricing", response_class=HTMLResponse)
async def agency_pricing():
    """Serve the pricing page."""
    jinja_env = _get_jinja_env()
    template = jinja_env.get_template("pricing.html")
    return HTMLResponse(content=template.render())


@agency_router.get("/agency/faq", response_class=HTMLResponse)
async def agency_faq():
    """Serve the FAQ page."""
    jinja_env = _get_jinja_env()
    template = jinja_env.get_template("faq.html")
    return HTMLResponse(content=template.render())


@agency_router.get("/agency/about", response_class=HTMLResponse)
async def agency_about():
    """Serve the About page."""
    jinja_env = _get_jinja_env()
    template = jinja_env.get_template("about.html")
    return HTMLResponse(content=template.render())


@agency_router.get("/agency/contact", response_class=HTMLResponse)
async def agency_contact():
    """Serve the Contact page."""
    jinja_env = _get_jinja_env()
    template = jinja_env.get_template("contact.html")
    return HTMLResponse(content=template.render())
