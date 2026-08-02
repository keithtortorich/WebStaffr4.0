"""WebStaffr Agency Site — company marketing site, not customer sites.

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

# Embedded templates — no filesystem dependency.
_TEMPLATES = {
    "base.html": '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta name="description" content="WebStaffr: 24/7 recurring office staff for home service contractors. Angel answers every call. One flat rate.">
    <title>{% block page_title %}WebStaffr | 24/7 Recurring Office Staff for Contractors{% endblock %}</title>
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
            <div class="ws-utility-item"><span class="ws-utility-item-accent">24/7</span> Live Support</div>
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
                <span class="ws-brand-text">WebStaffr</span>
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
            <div><h3 class="ws-footer-heading">WebStaffr</h3><p class="ws-footer-text">24/7 recurring office staff.</p></div>
            <div><h4 class="ws-footer-subheading">Product</h4><ul class="ws-footer-links"><li><a href="/agency/how-it-works">How It Works</a></li><li><a href="/agency/pricing">Pricing</a></li></ul></div>
            <div><h4 class="ws-footer-subheading">Company</h4><ul class="ws-footer-links"><li><a href="/agency/about">About</a></li><li><a href="/agency/contact">Contact</a></li></ul></div>
            <div><h4 class="ws-footer-subheading">Contact</h4><p class="ws-footer-text"><a href="mailto:keithtortorich@gmail.com">keithtortorich@gmail.com</a><br>(888) 302-8368</p></div>
        </div>
        <p class="ws-footer-copyright">&copy; 2026 WebStaffr. All rights reserved.</p>
    </footer>
</body>
</html>''',

    "home.html": '''{% extends "base.html" %}
{% block page_title %}You left money on the table this week | WebStaffr{% endblock %}
{% block content %}
<section class="ws-section-inner">
    <h1 class="ws-section-heading">You left money on the table this week.</h1>
    <p style="font-size: 1.125rem; color: #666; margin-bottom: 40px; max-width: 600px;">27% of calls go unanswered. 85% never get a callback. 78% hire the first person who picks up. WebStaffr answers your phone, books your jobs.</p>
    <a href="/agency/contact" class="ws-btn ws-btn-primary">Get Started Free (No Card Required)</a>

    <div style="margin-top: 60px; padding: 40px; background: var(--ws-cream); border-radius: 8px;">
        <p style="font-size: 0.95rem; color: #666; margin-bottom: 16px;"><strong>The math:</strong> You lose $16,000 a month to unanswered calls. That is $192,000 a year.</p>
        <p style="font-size: 0.95rem; color: #666;">WebStaffr costs less than hiring one part-time person. Books jobs while you sleep.</p>
    </div>
</section>
{% endblock %}''',

    "pricing.html": '''{% extends "base.html" %}
{% block page_title %}Pricing | WebStaffr{% endblock %}
{% block content %}
<section class="ws-section-inner">
    <h1 class="ws-section-heading">Simple pricing. No surprises.</h1>
    <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 24px; margin-top: 40px;">
        <div style="padding: 24px; border: 2px solid var(--ws-border); border-radius: 8px;">
            <h3 style="font-size: 1.125rem; font-weight: 700; margin-bottom: 8px;">Test Drive</h3>
            <p style="font-size: 0.9rem; color: #666; margin-bottom: 16px;">14 days free. No card.</p>
        </div>
        <div style="padding: 24px; border: 2px solid var(--ws-copper); border-radius: 8px; background: var(--ws-cream);">
            <h3 style="font-size: 1.125rem; font-weight: 700; margin-bottom: 8px;">Office Staff</h3>
            <p style="font-size: 2rem; font-weight: 700; color: var(--ws-copper); margin-bottom: 16px;">$497<span style="font-size: 0.875rem;">/month</span></p>
        </div>
        <div style="padding: 24px; border: 2px solid var(--ws-border); border-radius: 8px;">
            <h3 style="font-size: 1.125rem; font-weight: 700; margin-bottom: 8px;">Business Manager</h3>
            <p style="font-size: 2rem; font-weight: 700; color: var(--ws-primary-teal); margin-bottom: 16px;">$2,497<span style="font-size: 0.875rem;">/month</span></p>
        </div>
        <div style="padding: 24px; border: 2px solid var(--ws-border); border-radius: 8px;">
            <h3 style="font-size: 1.125rem; font-weight: 700; margin-bottom: 8px;">White-Glove</h3>
            <p style="font-size: 2rem; font-weight: 700; color: var(--ws-primary-teal); margin-bottom: 16px;">Custom</p>
            <p style="font-size: 0.9rem; color: #666;">$5,000+ per month</p>
        </div>
    </div>
</section>
{% endblock %}''',

    "how_it_works.html": '''{% extends "base.html" %}
{% block page_title %}How It Works | WebStaffr{% endblock %}
{% block content %}
<section class="ws-section-inner">
    <h1 class="ws-section-heading">Three Steps</h1>
    <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 40px; margin-top: 40px;">
        <div>
            <div style="width: 48px; height: 48px; background: var(--ws-copper); color: white; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-weight: 700; font-size: 1.5rem; margin-bottom: 16px;">1</div>
            <h3 style="font-size: 1.25rem; font-weight: 700; margin-bottom: 12px;">Sign up</h3>
            <p style="color: #666;">Start your free trial. No card required. Takes 5 minutes.</p>
        </div>
        <div>
            <div style="width: 48px; height: 48px; background: var(--ws-copper); color: white; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-weight: 700; font-size: 1.5rem; margin-bottom: 16px;">2</div>
            <h3 style="font-size: 1.25rem; font-weight: 700; margin-bottom: 12px;">Deploy Angel</h3>
            <p style="color: #666;">We embed our AI receptionist on your website. Zero coding.</p>
        </div>
        <div>
            <div style="width: 48px; height: 48px; background: var(--ws-copper); color: white; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-weight: 700; font-size: 1.5rem; margin-bottom: 16px;">3</div>
            <h3 style="font-size: 1.25rem; font-weight: 700; margin-bottom: 12px;">Stop losing calls</h3>
            <p style="color: #666;">Angel answers every call, books every job. 24/7.</p>
        </div>
    </div>
</section>
{% endblock %}''',

    "faq.html": '''{% extends "base.html" %}
{% block page_title %}Common Questions | WebStaffr{% endblock %}
{% block content %}
<section class="ws-section-inner">
    <h1 class="ws-section-heading">Common Questions</h1>
    <div style="max-width: 700px; margin: 40px auto;">
        <details style="margin-bottom: 16px; padding: 16px; border: 1px solid var(--ws-border); border-radius: 4px;">
            <summary style="cursor: pointer; font-weight: 600;">How does Angel know my service?</summary>
            <p style="margin-top: 12px; color: #666;">You train Angel on your business during setup. Takes 15 minutes.</p>
        </details>
        <details style="margin-bottom: 16px; padding: 16px; border: 1px solid var(--ws-border); border-radius: 4px;">
            <summary style="cursor: pointer; font-weight: 600;">Can I cancel anytime?</summary>
            <p style="margin-top: 12px; color: #666;">Yes. No contracts. Cancel anytime in your dashboard.</p>
        </details>
        <details style="margin-bottom: 16px; padding: 16px; border: 1px solid var(--ws-border); border-radius: 4px;">
            <summary style="cursor: pointer; font-weight: 600;">Does Angel use real voice?</summary>
            <p style="margin-top: 12px; color: #666;">Yes. Angel talks like a real person. Callers never know it is not human.</p>
        </details>
    </div>
</section>
{% endblock %}''',

    "about.html": '''{% extends "base.html" %}
{% block page_title %}About WebStaffr | WebStaffr{% endblock %}
{% block content %}
<section class="ws-section-inner">
    <h1 class="ws-section-heading">Recurring Office Staff</h1>
    <p style="font-size: 1.125rem; color: #666; max-width: 700px; line-height: 1.8;">WebStaffr builds recurring office staff for home service contractors. Angel is our first employee: an AI receptionist that answers every call, qualifies leads, and books jobs. No hiring. No training. One flat rate. 24/7.</p>
</section>
{% endblock %}''',

    "contact.html": '''{% extends "base.html" %}
{% block page_title %}Get Started with WebStaffr | Contact{% endblock %}
{% block content %}
<section class="ws-section-inner">
    <h1 class="ws-section-heading">Get Your Office Staff Working. Starting Today.</h1>
    <div style="max-width: 600px; margin: 40px auto; background: white; border: 2px solid #1a4d5e; border-radius: 8px; padding: 40px; box-shadow: 0 4px 12px rgba(26, 77, 94, 0.1);">
        <p style="margin: 0 0 24px 0; font-size: 1.1rem; color: #666; text-align: center;">14 days, free. No card. No contract. No risk.</p>
        <form style="display: grid; grid-template-columns: 1fr; gap: 16px;">
            <div>
                <label style="display: block; margin-bottom: 6px; font-weight: 600; color: #2a3a42; font-size: 0.95rem;">Business Name</label>
                <input type="text" placeholder="Your business" style="width: 100%; padding: 10px; border: 1px solid #e2e6ec; border-radius: 4px; font-family: inherit; font-size: 1rem;">
            </div>
            <div>
                <label style="display: block; margin-bottom: 6px; font-weight: 600; color: #2a3a42; font-size: 0.95rem;">Your Name</label>
                <input type="text" placeholder="Your name" style="width: 100%; padding: 10px; border: 1px solid #e2e6ec; border-radius: 4px; font-family: inherit; font-size: 1rem;">
            </div>
            <div>
                <label style="display: block; margin-bottom: 6px; font-weight: 600; color: #2a3a42; font-size: 0.95rem;">Email</label>
                <input type="email" placeholder="your@email.com" style="width: 100%; padding: 10px; border: 1px solid #e2e6ec; border-radius: 4px; font-family: inherit; font-size: 1rem;">
            </div>
            <div>
                <label style="display: block; margin-bottom: 6px; font-weight: 600; color: #2a3a42; font-size: 0.95rem;">Phone</label>
                <input type="tel" placeholder="(888) 555-1234" style="width: 100%; padding: 10px; border: 1px solid #e2e6ec; border-radius: 4px; font-family: inherit; font-size: 1rem;">
            </div>
            <div>
                <label style="display: block; margin-bottom: 6px; font-weight: 600; color: #2a3a42; font-size: 0.95rem;">Industry</label>
                <select style="width: 100%; padding: 10px; border: 1px solid #e2e6ec; border-radius: 4px; font-family: inherit; font-size: 1rem;">
                    <option>Select your trade</option>
                    <option>HVAC</option><option>Plumbing</option><option>Electrical</option><option>Roofing</option>
                </select>
            </div>
            <button type="submit" class="ws-btn ws-btn-primary" style="width: 100%; margin-top: 8px;">Get Started Free (No Card Required)</button>
        </form>
        <p style="margin-top: 24px; text-align: center; font-size: 0.9rem; color: #999;">We will set you up within 24 hours. Email keithtortorich@gmail.com or call (888) 302-8368.</p>
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
