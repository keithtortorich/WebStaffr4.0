"""NetBuild.Pro agency site, separate from generated customer sites.

Served at GET /agency/* using Jinja2 templates with the new brand palette
(teal + gold + copper). Copy from WEBSTAFFR_AGENCY_SITE_COPY_HORMOZI_VOSS.md.
Design from WEBSTAFFR_AGENCY_SITE_DESIGN_DIRECTION.md.

Vercel-safe: Zero filesystem I/O. All templates, CSS, and JS are hardcoded.
"""

from __future__ import annotations

from fastapi import APIRouter
from fastapi.responses import HTMLResponse
from jinja2 import Environment, DictLoader

agency_router = APIRouter(tags=["agency"])

# Embedded templates, with no filesystem dependency.
_TEMPLATES = {
    "base.html": '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta name="description" content="NetBuild.Pro builds customer websites and activates Angel call handling for home service contractors.">
    <title>{% block page_title %}NetBuild.Pro | Websites and call handling for contractors{% endblock %}</title>
    <style>
    :root {
        --ws-primary-teal: #1a4d5e;
        --ws-gold: #d4a574;
        --ws-copper: #c85a3a;
        --ws-cream: #f5f1e8;
        --ws-dark-slate: #2a3a42;
        --ws-light-gray: #f0f0f0;
        --ws-border: #e2e6ec;
    }
    * { margin: 0; padding: 0; box-sizing: border-box; }
    body { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; line-height: 1.6; color: #333; background: #fff; }

    .ws-utility-bar { background: var(--ws-primary-teal); color: white; padding: 8px 0; font-size: 0.875rem; }
    .ws-utility-bar-inner { max-width: 1200px; margin: 0 auto; padding: 0 20px; display: flex; justify-content: flex-end; gap: 40px; align-items: center; }
    .ws-utility-phone { display: flex; gap: 8px; align-items: center; }
    .ws-utility-item-accent { font-weight: 700; color: var(--ws-gold); }

    .ws-header { background: white; border-bottom: 1px solid var(--ws-border); position: sticky; top: 0; z-index: 100; }
    .ws-header-inner { max-width: 1200px; margin: 0 auto; padding: 16px 20px; display: flex; justify-content: space-between; align-items: center; }
    .ws-brand { display: flex; gap: 12px; align-items: center; font-weight: 700; font-size: 1.25rem; color: var(--ws-primary-teal); }
    .ws-logo { width: 32px; height: 32px; }
    .ws-brand-text { font-weight: 700; }
    .ws-nav { display: flex; gap: 32px; }
    .ws-nav-link { color: #666; text-decoration: none; font-size: 0.95rem; transition: color 0.2s; }
    .ws-nav-link:hover { color: var(--ws-copper); }
    .ws-nav-cta { background: var(--ws-copper); color: white; padding: 10px 20px; border-radius: 4px; text-decoration: none; font-size: 0.95rem; font-weight: 600; transition: background 0.2s; }
    .ws-nav-cta:hover { background: #b04a2a; }

    .ws-main { min-height: calc(100vh - 300px); }
    .ws-section-inner { max-width: 1200px; margin: 0 auto; padding: 60px 20px; }
    .ws-section-heading { font-size: 2.5rem; font-weight: 700; color: var(--ws-primary-teal); margin-bottom: 24px; }

    .ws-btn { display: inline-block; padding: 12px 24px; border-radius: 4px; text-decoration: none; font-weight: 600; cursor: pointer; border: none; font-size: 1rem; transition: all 0.2s; }
    .ws-btn-primary { background: var(--ws-copper); color: white; }
    .ws-btn-primary:hover { background: #b04a2a; }

    .ws-footer { background: var(--ws-dark-slate); color: white; padding: 60px 20px 24px; }
    .ws-footer-inner { max-width: 1200px; margin: 0 auto; display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 40px; margin-bottom: 40px; }
    .ws-footer-heading { font-size: 1.125rem; font-weight: 700; margin-bottom: 12px; }
    .ws-footer-subheading { font-size: 0.95rem; font-weight: 600; margin-bottom: 12px; }
    .ws-footer-text { font-size: 0.9rem; line-height: 1.6; color: rgba(255,255,255,0.8); }
    .ws-footer-links { list-style: none; }
    .ws-footer-links a { color: rgba(255,255,255,0.8); text-decoration: none; font-size: 0.9rem; }
    .ws-footer-links a:hover { color: var(--ws-gold); }
    .ws-footer-bottom { border-top: 1px solid rgba(255,255,255,0.1); padding-top: 20px; text-align: center; }
    .ws-footer-copyright { font-size: 0.8rem; color: rgba(255,255,255,0.6); }

    @media (max-width: 768px) {
        .ws-nav { display: none; }
        .ws-section-heading { font-size: 2rem; }
    }
    </style>
</head>
<body>
    <div class="ws-utility-bar">
        <div class="ws-utility-bar-inner">
            <div class="ws-utility-phone">(888) 302-8368</div>
            <div class="ws-utility-item"><span class="ws-utility-item-accent">Built for</span> Home Services</div>
        </div>
    </div>

    <header class="ws-header">
        <div class="ws-header-inner">
            <div class="ws-brand">
                <svg width="24" height="24" viewBox="0 0 100 100" fill="none" xmlns="http://www.w3.org/2000/svg" class="ws-logo">
                    <rect x="10" y="10" width="30" height="30" fill="#1a4d5e" rx="4"/>
                    <rect x="50" y="10" width="30" height="30" fill="#d4a574" rx="4"/>
                    <rect x="10" y="50" width="30" height="30" fill="#d4a574" rx="4"/>
                    <rect x="50" y="50" width="30" height="30" fill="#1a4d5e" rx="4"/>
                </svg>
                <span class="ws-brand-text">NetBuild.Pro</span>
            </div>
            <nav class="ws-nav">
                <a href="/agency" class="ws-nav-link">Home</a>
                <a href="/agency/how-it-works" class="ws-nav-link">How It Works</a>
                <a href="/agency/pricing" class="ws-nav-link">Pricing</a>
                <a href="/agency/faq" class="ws-nav-link">FAQ</a>
                <a href="/agency/about" class="ws-nav-link">About</a>
            </nav>
            <a href="/agency/contact" class="ws-nav-cta">Get Started</a>
        </div>
    </header>

    <main class="ws-main">
        {% block content %}{% endblock %}
    </main>

    <footer class="ws-footer">
        <div class="ws-footer-inner">
            <div><h3 class="ws-footer-heading">NetBuild.Pro</h3><p class="ws-footer-text">Customer websites and call handling for home service businesses.</p></div>
            <div><h4 class="ws-footer-subheading">Product</h4><ul class="ws-footer-links"><li><a href="/agency/how-it-works">How It Works</a></li><li><a href="/agency/pricing">Pricing</a></li></ul></div>
            <div><h4 class="ws-footer-subheading">Company</h4><ul class="ws-footer-links"><li><a href="/agency/about">About</a></li><li><a href="/agency/contact">Contact</a></li></ul></div>
            <div><h4 class="ws-footer-subheading">Contact</h4><p class="ws-footer-text"><a href="mailto:keithtortorich@gmail.com">keithtortorich@gmail.com</a><br>(888) 302-8368</p></div>
        </div>
        <p class="ws-footer-copyright">&copy; 2026 NetBuild.Pro. All rights reserved.</p>
    </footer>
</body>
</html>''',

    "home.html": '''{% extends "base.html" %}
{% block page_title %}Capture more customer requests | NetBuild.Pro{% endblock %}
{% block content %}
<section class="ws-section-inner">
    <h1 class="ws-section-heading">Turn customer interest into service requests.</h1>
    <p style="font-size: 1.125rem; color: #666; margin-bottom: 40px; max-width: 600px;">NetBuild.Pro gives home service businesses a customer-ready website, lead capture, and Angel call handling after each integration is verified.</p>
    <a href="/start" class="ws-btn ws-btn-primary">Start Your Intake</a>

    <div style="margin-top: 60px; padding: 40px; background: var(--ws-cream); border-radius: 8px;">
        <p style="font-size: 0.95rem; color: #666; margin-bottom: 16px;"><strong>The workflow:</strong> complete intake, review your generated site, then activate the approved call-handling and CRM integrations.</p>
        <p style="font-size: 0.95rem; color: #666;">Every captured request keeps its tenant and source attribution.</p>
    </div>
</section>
{% endblock %}''',

    "pricing.html": '''{% extends "base.html" %}
{% block page_title %}Pricing | NetBuild.Pro{% endblock %}
{% block content %}
<section class="ws-section-inner">
    <h1 class="ws-section-heading">Simple pricing. No surprises.</h1>
    <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 24px; margin-top: 40px;">
        <div style="padding: 24px; border: 2px solid var(--ws-copper); border-radius: 8px; background: var(--ws-cream);">
            <h3 style="font-size: 1.125rem; font-weight: 700; margin-bottom: 8px;">Essentials</h3>
            <p style="font-size: 2rem; font-weight: 700; color: var(--ws-copper); margin-bottom: 16px;">$497<span style="font-size: 0.875rem;">/month</span></p>
        </div>
        <div style="padding: 24px; border: 2px solid var(--ws-border); border-radius: 8px;">
            <h3 style="font-size: 1.125rem; font-weight: 700; margin-bottom: 8px;">Pro</h3>
            <p style="font-size: 2rem; font-weight: 700; color: var(--ws-primary-teal); margin-bottom: 16px;">$2,497<span style="font-size: 0.875rem;">/month</span></p>
        </div>
        <div style="padding: 24px; border: 2px solid var(--ws-border); border-radius: 8px;">
            <h3 style="font-size: 1.125rem; font-weight: 700; margin-bottom: 8px;">Growth</h3>
            <p style="font-size: 2rem; font-weight: 700; color: var(--ws-primary-teal); margin-bottom: 16px;">Custom</p>
            <p style="font-size: 0.9rem; color: #666;">$5,000+ per month</p>
        </div>
    </div>
</section>
{% endblock %}''',

    "how_it_works.html": '''{% extends "base.html" %}
{% block page_title %}How It Works | NetBuild.Pro{% endblock %}
{% block content %}
<section class="ws-section-inner">
    <h1 class="ws-section-heading">Three Steps</h1>
    <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 40px; margin-top: 40px;">
        <div>
            <div style="width: 48px; height: 48px; background: var(--ws-copper); color: white; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-weight: 700; font-size: 1.5rem; margin-bottom: 16px;">1</div>
            <h3 style="font-size: 1.25rem; font-weight: 700; margin-bottom: 12px;">Complete intake</h3>
            <p style="color: #666;">Tell us about your business, services, and customer-facing details.</p>
        </div>
        <div>
            <div style="width: 48px; height: 48px; background: var(--ws-copper); color: white; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-weight: 700; font-size: 1.5rem; margin-bottom: 16px;">2</div>
            <h3 style="font-size: 1.25rem; font-weight: 700; margin-bottom: 12px;">Review your site</h3>
            <p style="color: #666;">NetBuild.Pro generates the site and embeds the Angel customer-contact widget.</p>
        </div>
        <div>
            <div style="width: 48px; height: 48px; background: var(--ws-copper); color: white; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-weight: 700; font-size: 1.5rem; margin-bottom: 16px;">3</div>
            <h3 style="font-size: 1.25rem; font-weight: 700; margin-bottom: 12px;">Activate integrations</h3>
            <p style="color: #666;">Call handling, CRM routing, and booking go live after each configured integration passes verification.</p>
        </div>
    </div>
</section>
{% endblock %}''',

    "faq.html": '''{% extends "base.html" %}
{% block page_title %}Common Questions | NetBuild.Pro{% endblock %}
{% block content %}
<section class="ws-section-inner">
    <h1 class="ws-section-heading">Common Questions</h1>
    <div style="max-width: 700px; margin: 40px auto;">
        <details style="margin-bottom: 16px; padding: 16px; border: 1px solid var(--ws-border); border-radius: 4px;">
            <summary style="cursor: pointer; font-weight: 600;">How does Angel know my service?</summary>
            <p style="margin-top: 12px; color: #666;">Your approved intake supplies Angel with the business and service details used during customer conversations.</p>
        </details>
        <details style="margin-bottom: 16px; padding: 16px; border: 1px solid var(--ws-border); border-radius: 4px;">
            <summary style="cursor: pointer; font-weight: 600;">Can I cancel anytime?</summary>
            <p style="margin-top: 12px; color: #666;">Current terms are reviewed with you before activation. Contact support for account changes.</p>
        </details>
        <details style="margin-bottom: 16px; padding: 16px; border: 1px solid var(--ws-border); border-radius: 4px;">
            <summary style="cursor: pointer; font-weight: 600;">Does Angel use real voice?</summary>
            <p style="margin-top: 12px; color: #666;">Angel uses the configured voice provider. The live voice path is activated only after provider verification.</p>
        </details>
    </div>
</section>
{% endblock %}''',

    "about.html": '''{% extends "base.html" %}
{% block page_title %}About NetBuild.Pro{% endblock %}
{% block content %}
<section class="ws-section-inner">
    <h1 class="ws-section-heading">Built for home service businesses</h1>
    <p style="font-size: 1.125rem; color: #666; max-width: 700px; line-height: 1.8;">NetBuild.Pro combines a customer-ready website with tenant-scoped lead capture and Angel call handling. Integrations are activated only after they are configured and verified for the customer.</p>
</section>
{% endblock %}''',

    "contact.html": '''{% extends "base.html" %}
{% block page_title %}Get Started with NetBuild.Pro | Contact{% endblock %}
{% block content %}
<section class="ws-section-inner">
    <h1 class="ws-section-heading">Start with your business intake.</h1>
    <div style="max-width: 600px; margin: 40px auto; background: white; border: 2px solid #1a4d5e; border-radius: 8px; padding: 40px; box-shadow: 0 4px 12px rgba(26, 77, 94, 0.1); text-align: center;">
        <p style="margin: 0 0 24px 0; font-size: 1.1rem; color: #666;">Provide the business details needed to generate your reviewable customer site.</p>
        <a href="/start" class="ws-btn ws-btn-primary">Open Intake</a>
        <p style="margin-top: 24px; font-size: 0.9rem; color: #666;">Questions? Email keithtortorich@gmail.com or call (888) 302-8368.</p>
    </div>
</section>
{% endblock %}''',
}

_jinja_env = Environment(loader=DictLoader(_TEMPLATES), autoescape=True)


@agency_router.get("/agency", response_class=HTMLResponse)
@agency_router.get("/agency/", response_class=HTMLResponse)
async def agency_home():
    template = _jinja_env.get_template("home.html")
    return HTMLResponse(content=template.render())


@agency_router.get("/agency/how-it-works", response_class=HTMLResponse)
async def agency_how_it_works():
    template = _jinja_env.get_template("how_it_works.html")
    return HTMLResponse(content=template.render())


@agency_router.get("/agency/pricing", response_class=HTMLResponse)
async def agency_pricing():
    template = _jinja_env.get_template("pricing.html")
    return HTMLResponse(content=template.render())


@agency_router.get("/agency/faq", response_class=HTMLResponse)
async def agency_faq():
    template = _jinja_env.get_template("faq.html")
    return HTMLResponse(content=template.render())


@agency_router.get("/agency/about", response_class=HTMLResponse)
async def agency_about():
    template = _jinja_env.get_template("about.html")
    return HTMLResponse(content=template.render())


@agency_router.get("/agency/contact", response_class=HTMLResponse)
async def agency_contact():
    template = _jinja_env.get_template("contact.html")
    return HTMLResponse(content=template.render())
