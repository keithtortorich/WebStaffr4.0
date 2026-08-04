"""NetBuild.Pro public landing page and investor resources.

Serves the landing page at GET /, demo site previews, and the full
business plan PDF for investors.
"""

from __future__ import annotations

from pathlib import Path

from fastapi import APIRouter

landing_router = APIRouter(tags=["public"])
_INTAKE_PAGE = Path(__file__).parent / "templates" / "intake_start.html"

# Single source of truth for the public contact details. These appear in the
# investor JSON, the investor modal, and the lead-capture form, and previously
# drifted apart across all three.
#
# Confirmed by the founder 2026-07-28: mail goes to his Gmail, not to a mailbox
# on either webstaff.com or webstaffr.com. The stale keith@webstaff.com address
# that used to be here never resolved the domain-spelling conflict between
# LINK_MANIFEST.md ("webstaffr.com") and POST_DEPLOY_VERIFICATION.md
# ("webstaff.com"); that conflict still needs settling for the site URLs, but it
# no longer affects where mail lands. See TASKS.md Pending.
_CONTACT_EMAIL = "keithtortorich@gmail.com"
_CONTACT_PHONE = "(888) 302-8368"
_CONTACT_PHONE_TEL = "+18883028368"

# Small inline SVG icon set for the landing page -- same rationale as the
# customer-site renderer's icon set (webstaffr/templates/site/_icons.html):
# replaces plain-text bullets/numbering with real iconography, no external
# icon-library dependency, no build step. Defined as plain Python string
# constants here (rather than Jinja macros) because this page is a single
# inline-HTML string, not a Jinja template -- same visual language, native
# to this file's own architecture.
_ICON_CHECK = (
    '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" '
    'stroke-width="3" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">'
    '<polyline points="20 6 9 17 4 12"/></svg>'
)
_ICON_X = (
    '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" '
    'stroke-width="3" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">'
    '<line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/></svg>'
)
_ICON_PHONE = (
    '<svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" '
    'stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">'
    '<path d="M22 16.92v3a2 2 0 0 1-2.18 2 19.79 19.79 0 0 1-8.63-3.07 19.5 19.5 0 0 1-6-6 '
    '19.79 19.79 0 0 1-3.07-8.67A2 2 0 0 1 4.11 2h3a2 2 0 0 1 2 1.72c.127.96.361 1.903.7 2.81a2 '
    '2 0 0 1-.45 2.11L8.09 9.91a16 16 0 0 0 6 6l1.27-1.27a2 2 0 0 1 2.11-.45c.907.339 1.85.573 '
    '2.81.7A2 2 0 0 1 22 16.92z"/></svg>'
)
_ICON_ARROW = (
    '<svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" '
    'stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">'
    '<line x1="5" y1="12" x2="19" y2="12"/><polyline points="12 5 19 12 12 19"/></svg>'
)


@landing_router.get("/", response_class=None)
async def landing_page():
    """Serve the public landing page with embedded investor modal and demo gallery."""
    from fastapi.responses import HTMLResponse

    # Read the landing page HTML (created separately as static asset or inline)
    # For now, return a placeholder that redirects to the static version
    # In production, this will read from a file or serve inline
    return HTMLResponse(content=_render_landing_page())


@landing_router.get("/start", response_class=None)
async def intake_page():
    """Serve the one-page, tradesman-facing setup form."""
    from fastapi.responses import HTMLResponse

    return HTMLResponse(content=_INTAKE_PAGE.read_text())


def _render_landing_page() -> str:
    """Substitute contact details into the landing page template.

    Plain token replacement rather than an f-string: the template is mostly
    CSS and JavaScript, so every brace in it would have to be doubled to make
    f-string interpolation safe. Tokens keep the markup readable and keep the
    contact details defined in exactly one place.
    """
    return (
        _LANDING_PAGE_HTML
        .replace("__CONTACT_EMAIL__", _CONTACT_EMAIL)
        .replace("__CONTACT_PHONE_TEL__", _CONTACT_PHONE_TEL)
        .replace("__CONTACT_PHONE__", _CONTACT_PHONE)
        .replace("__ICON_CHECK__", _ICON_CHECK)
        .replace("__ICON_X__", _ICON_X)
        .replace("__ICON_PHONE__", _ICON_PHONE)
        .replace("__ICON_ARROW__", _ICON_ARROW)
    )


@landing_router.get("/investors/pitch")
@landing_router.get("/investors/pitch.pdf")
async def investor_pitch():
    """Serve the full business plan PDF (when available)."""
    from fastapi.responses import FileResponse, JSONResponse
    import os

    pdf_path = os.path.join(os.path.dirname(__file__), "investor_pitch.pdf")
    if os.path.exists(pdf_path):
        return FileResponse(pdf_path, media_type="application/pdf", filename="WebStaffr_Pitch.pdf")

    # Fallback: return investor summary from INVESTOR_EMAIL_FINAL.md
    return JSONResponse({
        "message": "NetBuild.Pro Investment Overview",
        "narrative": "You don't need more leads. You need to stop losing the ones you already have.",
        "problem": "27% of home-service calls go unanswered. A single missed job costs $500-$5,000.",
        "solution": "NetBuild.Pro answers every call 24/7. $497/month. Built for contractors.",
        "unit_economics": {
            "arpu_monthly": 487,
            "gross_margin_pct": 88,
            "cac_payback_months": 4,
            "ltv": 8500
        },
        "ask": "$15K-50K SAFE",
        "contact": {
            "email": _CONTACT_EMAIL,
            "phone": _CONTACT_PHONE
        },
        "pdf": "Full PDF available at deployment. Email for early access."
    })


@landing_router.get("/demos/{trade}")
async def demo_redirect(trade: str):
    """Redirect demo site links to live customer sites.

    /demos/hvac → /sites/demo-hvac/web
    /demos/plumbing → /sites/demo-plumbing/web
    etc.
    """
    from fastapi.responses import RedirectResponse

    valid_trades = [
        "salon", "contractor", "restaurant", "medspa", "dentist",
        "plumbing", "electrician", "realestate", "lawfirm", "gym"
    ]

    if trade.lower() not in valid_trades:
        return {"error": f"Demo for '{trade}' not found. Available: {', '.join(valid_trades)}"}

    tenant_id = f"demo-{trade.lower()}"
    return RedirectResponse(url=f"/sites/{tenant_id}/web", status_code=302)


# Approved copy from WEBSTAFFR_AGENCY_SITE_COPY_HORMOZI_VOSS.md - replace with Hormozi-Voss methodology
# Hook: "You left money on the table this week"
# Subhead: "WebStaffr answers your phone so you don't lose jobs you already paid to generate"
# Math: $16,000/month narrative (Voss quantifiable pain formula)
# Structure: 3 steps, zero risk (Hormozi-Voss sales formula)
# Pricing: Test Drive free 14d, Office Staff $497 featured, Business Manager $2,497, White-Glove custom
# Colors: royal blue, navy, electric orange, light gray bg
_LANDING_PAGE_HTML = """
<!DOCTYPE html>
<html>
<head>
    <title>NetBuild.Pro | Receptionist for Home Services</title>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; background: #f5f5f5; color: #1a1a1a; line-height: 1.6; }
        header { background: linear-gradient(135deg, #4169E1 0%, #1f2937 100%); color: white; padding: 16px 20px; display: flex; align-items: center; justify-content: space-between; sticky: top; z-index: 100; }
        header h1 { font-size: 1.3rem; font-weight: 700; }
        header a { color: #FF6600; text-decoration: none; font-weight: 600; }
        .container { max-width: 1000px; margin: 0 auto; padding: 40px 20px; }
        h2 { font-size: 2.2rem; margin-bottom: 20px; color: #1f2937; }
        h3 { font-size: 1.5rem; margin-bottom: 16px; color: #1f2937; }
        p { margin-bottom: 16px; color: #4b5563; font-size: 1.05rem; }
        .hook { background: #FF6600; color: white; padding: 40px; text-align: center; margin-bottom: 40px; border-radius: 8px; }
        .hook h2 { color: white; font-size: 2.8rem; margin: 0; }
        .subhead { font-size: 1.3rem; color: white; margin-top: 16px; }
        .math-box { background: white; border-left: 4px solid #FF6600; padding: 24px; margin-bottom: 40px; border-radius: 4px; box-shadow: 0 2px 8px rgba(0,0,0,0.1); }
        .math-box strong { color: #FF6600; }
        .pricing { background: white; padding: 40px; border-radius: 8px; margin-bottom: 40px; box-shadow: 0 2px 8px rgba(0,0,0,0.1); }
        .pricing-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 20px; margin-top: 24px; }
        .pricing-card { background: #f9fafb; border: 1px solid #e5e7eb; padding: 20px; border-radius: 6px; text-align: center; }
        .pricing-card.featured { background: #1f2937; color: white; border-color: #FF6600; }
        .pricing-card.featured h4 { color: #FF6600; }
        .price { font-size: 2rem; font-weight: 700; margin: 12px 0; }
        .faq { background: white; padding: 40px; border-radius: 8px; box-shadow: 0 2px 8px rgba(0,0,0,0.1); }
        .faq-item { margin-bottom: 24px; }
        .faq-question { font-weight: 600; color: #1f2937; margin-bottom: 8px; }
        .faq-answer { color: #4b5563; }
        .cta-section { background: linear-gradient(135deg, #4169E1 0%, #1f2937 100%); color: white; padding: 40px; border-radius: 8px; text-align: center; margin-bottom: 40px; }
        .cta-section h3 { color: white; }
        button { background: #FF6600; color: white; border: none; padding: 12px 24px; border-radius: 6px; font-weight: 600; cursor: pointer; font-size: 1rem; }
        button:hover { background: #e55c00; }
        .demo-links { display: grid; grid-template-columns: repeat(auto-fit, minmax(180px, 1fr)); gap: 16px; margin-top: 24px; }
        .demo-link { background: white; border: 1px solid #e5e7eb; padding: 16px; border-radius: 6px; text-decoration: none; color: #1f2937; text-align: center; transition: all 0.2s; }
        .demo-link:hover { border-color: #FF6600; transform: translateY(-2px); }
        .no-ai { font-size: 0.9rem; color: #6b7280; font-style: italic; margin-top: 16px; }
    </style>
</head>
<body>
    <header>
        <h1>NetBuild.Pro</h1>
        <a href="tel:__CONTACT_PHONE_TEL__">__CONTACT_PHONE__</a>
    </header>

    <div class="hook">
        <h2>You left money on the table this week.</h2>
        <p class="subhead">NetBuild.Pro answers your phone so you don't lose jobs you already paid to generate.</p>
    </div>

    <div class="container">
        <div class="math-box">
            <h3>The Math</h3>
            <p><strong>27% of home service calls go unanswered.</strong> Most don't call back.</p>
            <p>A single missed job costs <strong>$500 to $5,000</strong>. Lose 10 calls a week, you're walking away from <strong>$16,000 a month</strong> in revenue.</p>
            <p>NetBuild.Pro costs <strong>$497/month</strong> and answers every call.</p>
            <p class="no-ai">No software. No AI. No chatbot. A 24/7 receptionist that qualifies leads and books appointments.</p>
        </div>

        <div class="pricing">
            <h3>Pick Your Plan</h3>
            <p>Start free for 14 days. No credit card. Cancel anytime.</p>
            <div class="pricing-grid">
                <div class="pricing-card">
                    <h4>Test Drive</h4>
                    <p style="color: #8b5cf6;">14 days free</p>
                    <p style="font-size: 0.9rem;">Try it risk-free</p>
                </div>
                <div class="pricing-card featured">
                    <h4>Office Staff</h4>
                    <div class="price">$497</div>
                    <p style="font-size: 0.9rem;">/month. Most popular.</p>
                    <a href="/start" class="start-link" style="display:block; background:#FF6600; color:white; width:100%; margin-top:12px; padding:12px 24px; border-radius:6px; font-weight:600; text-decoration:none;">Start Free</a>
                </div>
                <div class="pricing-card">
                    <h4>Business Manager</h4>
                    <div class="price">$2,497</div>
                    <p style="font-size: 0.9rem;">/month. Full front office.</p>
                </div>
                <div class="pricing-card">
                    <h4>White-Glove</h4>
                    <p style="color: #FF6600;">Custom pricing</p>
                    <p style="font-size: 0.9rem;">Enterprise support</p>
                </div>
            </div>
        </div>

        <div style="text-align: center; margin-bottom: 40px;">
            <h3>See It Live</h3>
            <div class="demo-links">
                <a href="/demos/hvac" class="demo-link">HVAC</a>
                <a href="/demos/plumbing" class="demo-link">Plumbing</a>
                <a href="/demos/electrical" class="demo-link">Electrical</a>
                <a href="/demos/roofing" class="demo-link">Roofing</a>
                <a href="/demos/water-damage" class="demo-link">Water Damage</a>
                <a href="/demos/garage-door" class="demo-link">Garage Door</a>
                <a href="/demos/pest-control" class="demo-link">Pest Control</a>
                <a href="/demos/landscaping" class="demo-link">Landscaping</a>
                <a href="/demos/tree-service" class="demo-link">Tree Service</a>
                <a href="/demos/cleaning" class="demo-link">Cleaning</a>
            </div>
        </div>

        <div class="faq">
            <h3>Common Questions</h3>
            <div class="faq-item">
                <div class="faq-question">Fair?</div>
                <div class="faq-answer">You get $16K in monthly calls answered. We get $497. Fair.</div>
            </div>
            <div class="faq-item">
                <div class="faq-question">What's the real concern here?</div>
                <div class="faq-answer">That it won't work as well as a human. It will. We use proven voice AI and your team's own sales process. Faster, cheaper, on-call.</div>
            </div>
            <div class="faq-item">
                <div class="faq-question">Can I cancel?</div>
                <div class="faq-answer">Yes. Anytime. No contract.</div>
            </div>
            <div class="faq-item">
                <div class="faq-question">How fast does it book?</div>
                <div class="faq-answer">Instantly. Appointments go straight to your calendar and GHL. Caller gets a confirmation text.</div>
            </div>
            <div class="faq-item">
                <div class="faq-question">Does it need my sales process?</div>
                <div class="faq-answer">Yes. We import your intake questions, your pricing, your objection responses. It sounds like your team.</div>
            </div>
            <div class="faq-item">
                <div class="faq-question">What if I'm not ready?</div>
                <div class="faq-answer">Fourteen days free. Set it up, try it with real calls, decide after.</div>
            </div>
            <div class="faq-item">
                <div class="faq-question">What if a call is weird?</div>
                <div class="faq-answer">It transfers to you or voicemail. You stay in control.</div>
            </div>
            <div class="faq-item">
                <div class="faq-question">Will my customers notice?</div>
                <div class="faq-answer">No. They get a fast answer and a real person if they ask. That's all they need.</div>
            </div>
            <div class="faq-item">
                <div class="faq-question">What's next?</div>
                <div class="faq-answer">Click below. Pick a date. We'll call you to set it up. Fourteen days later, decide.</div>
            </div>
        </div>

        <div class="cta-section">
            <h3>Stop Leaving Money on the Table</h3>
            <p>Start your free 14-day trial. Answers every call while you work.</p>
            <a href="/start" class="start-link" style="display:inline-block; background:#FF6600; color:white; font-size:1.1rem; padding:14px 28px; margin-top:16px; border-radius:6px; font-weight:600; text-decoration:none;">Get Started Free</a>
            <p style="margin-top: 16px; font-size: 0.95rem;">Questions? Call <a href="tel:__CONTACT_PHONE_TEL__" style="color: #FF6600; text-decoration: none;">__CONTACT_PHONE__</a> or email __CONTACT_EMAIL__</p>
        </div>
    </div>
</body>
</html>
"""
