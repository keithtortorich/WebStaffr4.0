"""WebStaffr public landing page and investor resources.

Serves the landing page at GET /, demo site previews, and the full
business plan PDF for investors.
"""

from __future__ import annotations

from fastapi import APIRouter

landing_router = APIRouter(tags=["public"])

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
        "message": "WebStaffr Investment Overview",
        "narrative": "You don't need more leads. You need to stop losing the ones you already have.",
        "problem": "27% of home-service calls go unanswered. A single missed job costs $500-$5,000.",
        "solution": "WebStaffr answers every call 24/7. $497/month. Built for contractors.",
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


# Placeholder HTML — in production, read from a static file
_LANDING_PAGE_HTML = """
<!DOCTYPE html>
<html>
<head>
    <title>WebStaffr | 24/7 Receptionist for Home Services</title>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <style>
        @keyframes fadeInUp {
            from { opacity: 0; transform: translateY(20px); }
            to { opacity: 1; transform: translateY(0); }
        }
        @keyframes fadeIn {
            from { opacity: 0; }
            to { opacity: 1; }
        }
        @keyframes slideInRight {
            from { opacity: 0; transform: translateX(-20px); }
            to { opacity: 1; transform: translateX(0); }
        }
        .animate-fade-in { animation: fadeIn 0.6s ease-out forwards; }
        .animate-fade-up { animation: fadeInUp 0.7s ease-out forwards; }
        .animate-slide-in { animation: slideInRight 0.8s ease-out forwards; }
        .demo-card { transition: all 0.3s ease; }
        .demo-card:hover {
            transform: translateY(-4px);
            background: rgba(255,255,255,0.08) !important;
            border-color: rgba(200,162,90,0.5) !important;
        }
        .cta-button { transition: all 0.2s ease; }
        .cta-button:hover {
            transform: scale(1.02);
            box-shadow: 0 8px 24px rgba(200,162,90,0.3);
        }
        .phone-link { transition: all 0.2s ease; }
        .phone-link:hover {
            opacity: 0.85;
            transform: scale(1.03);
        }
    </style>
</head>
<body style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; margin: 0; background: #0a0c0f; color: #f0f2f5;">
    <div style="display: flex; align-items: center; justify-content: space-between; gap: 16px; flex-wrap: wrap; padding: 14px 20px; border-bottom: 1px solid rgba(255,255,255,0.06); position: sticky; top: 0; background: rgba(10,12,15,0.92); backdrop-filter: blur(6px); z-index: 10;">
        <span style="font-weight: 700; font-size: 1.1rem; letter-spacing: 0.02em; color: #f0f2f5;">WebStaffr</span>
        <a href="tel:__CONTACT_PHONE_TEL__" style="display: inline-flex; align-items: center; gap: 8px; background: linear-gradient(135deg, #c8a25a, #dab87a); color: #0a0c0f; padding: 9px 18px; border-radius: 6px; font-weight: 700; text-decoration: none; font-size: 0.9rem;">__ICON_PHONE__ __CONTACT_PHONE__</a>
    </div>
    <div style="max-width: 1200px; margin: 0 auto; padding: 20px;">
        <h1 class="animate-fade-up" style="font-size: 2.5rem; margin-bottom: 24px; color: #f0f2f5;">WebStaffr: One Problem, One Solution</h1>

        <div class="animate-fade-up" style="background: rgba(200, 162, 90, 0.08); border-left: 4px solid #c8a25a; padding: 32px; margin-bottom: 60px; border-radius: 4px; animation-delay: 0.1s;">
            <h2 style="color: #c8a25a; margin-top: 0; font-size: 1.5rem;">The One Problem</h2>
            <p style="color: #f0f2f5; line-height: 1.8; margin: 0 0 16px 0; font-size: 1.1rem;">
                <strong>Contractors lose revenue because they can't answer the phone while they're working.</strong>
            </p>
            <p style="color: #8a94a6; line-height: 1.8; margin: 0;">
                That's it. Everything else is a symptom.
                <br><br>
                Missed calls become lost jobs. Lost jobs become revenue leaks. Revenue leaks become cash flow problems. Cash flow problems become stress, sleepless nights, and wondering if you can make payroll.
                <br><br>
                But it all starts with one thing: <strong>You're on a job. The phone rings. You can't get to it.</strong>
            </p>
        </div>

        <div class="animate-fade-up" style="margin-bottom: 60px; animation-delay: 0.2s;">
            <h3 style="color: #c8a25a; margin-bottom: 20px;">The Math That Makes It Real</h3>
            <div style="background: rgba(255,255,255,0.02); border: 1px solid rgba(255,255,255,0.06); padding: 24px; border-radius: 8px; margin-bottom: 24px;">
                <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 20px; margin-bottom: 24px;">
                    <div>
                        <div style="font-size: 2rem; font-weight: 600; color: #c8a25a;">27%</div>
                        <div style="color: #8a94a6; font-size: 0.9rem;">of home service calls go unanswered</div>
                    </div>
                    <div>
                        <div style="font-size: 1.4rem; font-weight: 700; color: #c8a25a; line-height: 1.25;">Speed wins the job</div>
                        <div style="color: #8a94a6; font-size: 0.9rem;">Speed-to-lead research (MIT/Oldroyd) ties faster first response to higher close rates</div>
                    </div>
                </div>
                <p style="color: #8a94a6; margin: 0; line-height: 1.8;">
                    <strong style="color: #f0f2f5;">If you miss 10 calls in a week:</strong> most leave voicemail, and most of those never call back. Every one of them is a lead your competitor can pick up instead.
                    <br><br>
                    <strong style="color: #c8a25a;">A single missed job = $500–$5,000.</strong> A single missed call costs more than a month of WebStaffr.
                </p>
            </div>
        </div>

        <div class="animate-fade-up" style="background: rgba(200, 162, 90, 0.08); border-left: 4px solid #c8a25a; padding: 32px; margin-bottom: 60px; border-radius: 4px; animation-delay: 0.3s;">
            <h2 style="color: #c8a25a; margin-top: 0; font-size: 1.5rem;">The One Solution</h2>
            <p style="color: #f0f2f5; line-height: 1.8; margin: 0 0 16px 0; font-size: 1.1rem;">
                <strong>WebStaffr answers your phone so you don't have to.</strong>
            </p>
            <p style="color: #8a94a6; line-height: 1.8; margin: 0;">
                It's not software. It's not AI. It's not a chatbot.
                <br><br>
                It's a <strong>24/7 Receptionist</strong> that picks up every call, pre-qualifies the lead, and books appointments directly into your calendar. While you're on a ladder, under a house, or driving to the next job, your phone is still ringing, and still getting answered.
            </p>
        </div>

        <div class="animate-fade-up" style="margin-bottom: 60px; animation-delay: 0.4s;">
            <h3 style="color: #c8a25a; margin-bottom: 20px;">Why WebStaffr</h3>
            <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 20px;">
                <div style="background: rgba(255,0,0,0.05); border: 1px solid rgba(255,100,100,0.2); padding: 16px; border-radius: 6px;">
                    <div style="color: #f0f2f5; font-weight: 600; margin-bottom: 8px; display: flex; align-items: center; gap: 8px;"><span style="color: #ff6b6b;">__ICON_X__</span> Hire a human receptionist</div>
                    <div style="color: #8a94a6; font-size: 0.9rem;">$3,500+/month. Can't work 24/7. Calls in sick. Takes vacations. Can't handle 3 calls at once.</div>
                </div>
                <div style="background: rgba(255,0,0,0.05); border: 1px solid rgba(255,100,100,0.2); padding: 16px; border-radius: 6px;">
                    <div style="color: #f0f2f5; font-weight: 600; margin-bottom: 8px; display: flex; align-items: center; gap: 8px;"><span style="color: #ff6b6b;">__ICON_X__</span> Let calls go to voicemail</div>
                    <div style="color: #8a94a6; font-size: 0.9rem;">Most never call back. They call your competitor instead.</div>
                </div>
                <div style="background: rgba(255,0,0,0.05); border: 1px solid rgba(255,100,100,0.2); padding: 16px; border-radius: 6px;">
                    <div style="color: #f0f2f5; font-weight: 600; margin-bottom: 8px; display: flex; align-items: center; gap: 8px;"><span style="color: #ff6b6b;">__ICON_X__</span> Call back later</div>
                    <div style="color: #8a94a6; font-size: 0.9rem;">The lead's already talking to whoever picked up first.</div>
                </div>
                <div style="background: rgba(200,162,90,0.1); border: 1px solid rgba(200,162,90,0.3); padding: 16px; border-radius: 6px;">
                    <div style="color: #c8a25a; font-weight: 600; margin-bottom: 8px; display: flex; align-items: center; gap: 8px;">__ICON_CHECK__ WebStaffr</div>
                    <div style="color: #8a94a6; font-size: 0.9rem;">$497/month. 24/7/365. Answers every call. Qualifies every lead. Books every job. Built for contractors.</div>
                </div>
            </div>
        </div>

        <div style="margin-bottom: 60px;">
            <h3 style="color: #c8a25a; margin-bottom: 24px;">See It Live: 10 Home Service Industries</h3>
            <div style="display: grid; grid-template-columns: repeat(auto-fill, minmax(200px, 1fr)); gap: 16px;">
                <a href="/demos/hvac" class="demo-card" style="padding: 16px; background: rgba(255,255,255,0.04); border: 1px solid rgba(255,255,255,0.06); border-radius: 8px; text-decoration: none; color: inherit; display: flex; align-items: center; justify-content: space-between; gap: 8px;">
                    <span><strong style="color: #c8a25a;">HVAC</strong><br><span style="color: #8a94a6; font-size: 0.85rem;">66% unanswered</span></span><span style="color: #c8a25a; opacity: .6;">__ICON_ARROW__</span>
                </a>
                <a href="/demos/plumbing" class="demo-card" style="padding: 16px; background: rgba(255,255,255,0.04); border: 1px solid rgba(255,255,255,0.06); border-radius: 8px; text-decoration: none; color: inherit; display: flex; align-items: center; justify-content: space-between; gap: 8px;">
                    <span><strong style="color: #c8a25a;">Plumbing</strong><br><span style="color: #8a94a6; font-size: 0.85rem;">26% unanswered</span></span><span style="color: #c8a25a; opacity: .6;">__ICON_ARROW__</span>
                </a>
                <a href="/demos/electrical" style="padding: 16px; background: rgba(255,255,255,0.04); border: 1px solid rgba(255,255,255,0.06); border-radius: 8px; text-decoration: none; color: inherit; transition: all 0.3s; display: flex; align-items: center; justify-content: space-between; gap: 8px;">
                    <span><strong style="color: #c8a25a;">Electrical</strong><br><span style="color: #8a94a6; font-size: 0.85rem;">24% unanswered</span></span><span style="color: #c8a25a; opacity: .6;">__ICON_ARROW__</span>
                </a>
                <a href="/demos/roofing" style="padding: 16px; background: rgba(255,255,255,0.04); border: 1px solid rgba(255,255,255,0.06); border-radius: 8px; text-decoration: none; color: inherit; transition: all 0.3s; display: flex; align-items: center; justify-content: space-between; gap: 8px;">
                    <span><strong style="color: #c8a25a;">Roofing</strong><br><span style="color: #8a94a6; font-size: 0.85rem;">Storm-driven</span></span><span style="color: #c8a25a; opacity: .6;">__ICON_ARROW__</span>
                </a>
                <a href="/demos/water-damage" style="padding: 16px; background: rgba(255,255,255,0.04); border: 1px solid rgba(255,255,255,0.06); border-radius: 8px; text-decoration: none; color: inherit; transition: all 0.3s; display: flex; align-items: center; justify-content: space-between; gap: 8px;">
                    <span><strong style="color: #c8a25a;">Water Damage</strong><br><span style="color: #8a94a6; font-size: 0.85rem;">24/7 emergency</span></span><span style="color: #c8a25a; opacity: .6;">__ICON_ARROW__</span>
                </a>
                <a href="/demos/garage-door" style="padding: 16px; background: rgba(255,255,255,0.04); border: 1px solid rgba(255,255,255,0.06); border-radius: 8px; text-decoration: none; color: inherit; transition: all 0.3s; display: flex; align-items: center; justify-content: space-between; gap: 8px;">
                    <span><strong style="color: #c8a25a;">Garage Door</strong><br><span style="color: #8a94a6; font-size: 0.85rem;">After-hours demand</span></span><span style="color: #c8a25a; opacity: .6;">__ICON_ARROW__</span>
                </a>
                <a href="/demos/pest-control" style="padding: 16px; background: rgba(255,255,255,0.04); border: 1px solid rgba(255,255,255,0.06); border-radius: 8px; text-decoration: none; color: inherit; transition: all 0.3s; display: flex; align-items: center; justify-content: space-between; gap: 8px;">
                    <span><strong style="color: #c8a25a;">Pest Control</strong><br><span style="color: #8a94a6; font-size: 0.85rem;">27% unanswered</span></span><span style="color: #c8a25a; opacity: .6;">__ICON_ARROW__</span>
                </a>
                <a href="/demos/landscaping" style="padding: 16px; background: rgba(255,255,255,0.04); border: 1px solid rgba(255,255,255,0.06); border-radius: 8px; text-decoration: none; color: inherit; transition: all 0.3s; display: flex; align-items: center; justify-content: space-between; gap: 8px;">
                    <span><strong style="color: #c8a25a;">Landscaping</strong><br><span style="color: #8a94a6; font-size: 0.85rem;">High volume</span></span><span style="color: #c8a25a; opacity: .6;">__ICON_ARROW__</span>
                </a>
                <a href="/demos/tree-service" style="padding: 16px; background: rgba(255,255,255,0.04); border: 1px solid rgba(255,255,255,0.06); border-radius: 8px; text-decoration: none; color: inherit; transition: all 0.3s; display: flex; align-items: center; justify-content: space-between; gap: 8px;">
                    <span><strong style="color: #c8a25a;">Tree Service</strong><br><span style="color: #8a94a6; font-size: 0.85rem;">Storm-driven</span></span><span style="color: #c8a25a; opacity: .6;">__ICON_ARROW__</span>
                </a>
                <a href="/demos/cleaning" style="padding: 16px; background: rgba(255,255,255,0.04); border: 1px solid rgba(255,255,255,0.06); border-radius: 8px; text-decoration: none; color: inherit; transition: all 0.3s; display: flex; align-items: center; justify-content: space-between; gap: 8px;">
                    <span><strong style="color: #c8a25a;">Cleaning</strong><br><span style="color: #8a94a6; font-size: 0.85rem;">Recurring</span></span><span style="color: #c8a25a; opacity: .6;">__ICON_ARROW__</span>
                </a>
            </div>
        </div>

        <div style="text-align: center; padding: 40px 0; border-top: 1px solid rgba(255,255,255,0.06);">
            <h2 style="color: #f0f2f5; margin: 0 0 16px 0; font-size: 1.3rem;">
                <strong style="color: #c8a25a;">You don't need more leads.</strong><br>You need to stop losing the ones you already have.
            </h2>
            <p style="color: #8a94a6; margin: 0; max-width: 600px; margin-left: auto; margin-right: auto;">
                WebStaffr recovers revenue by making sure you never miss another call. Everything else is just how we do it: the website, the reviews, the follow-ups.
            </p>
        </div>
        <div id="lead-capture" class="animate-fade-up" style="background: rgba(15, 31, 58, 0.5); padding: 40px; border-radius: 8px; text-align: center; margin-bottom: 60px; animation-delay: 0.5s;">
            <h2 style="margin-top: 0; color: #c8a25a;">Get Your Free Website</h2>
            <p style="color: #8a94a6; margin-bottom: 24px;">Answer 3 quick questions. We build it in 48 hours. Try it free for 30 days.</p>
            <form id="lead-form" style="max-width: 400px; margin: 0 auto; display: flex; flex-direction: column; gap: 12px;">
                <input id="lead-biz" type="text" placeholder="Your business name" style="padding: 12px; background: rgba(255,255,255,0.04); border: 1px solid rgba(255,255,255,0.06); border-radius: 6px; color: #f0f2f5; transition: all 0.2s ease;" required>
                <input id="lead-loc" type="text" placeholder="Your location" style="padding: 12px; background: rgba(255,255,255,0.04); border: 1px solid rgba(255,255,255,0.06); border-radius: 6px; color: #f0f2f5; transition: all 0.2s ease;" required>
                <input id="lead-email" type="email" placeholder="Your email" style="padding: 12px; background: rgba(255,255,255,0.04); border: 1px solid rgba(255,255,255,0.06); border-radius: 6px; color: #f0f2f5; transition: all 0.2s ease;" required>
                <button type="submit" class="cta-button" style="padding: 12px; background: linear-gradient(135deg, #c8a25a, #dab87a); color: #0a0c0f; border: none; border-radius: 6px; font-weight: 600; cursor: pointer;">
                    Apply for Free Website
                </button>
            </form>
            <p id="lead-form-status" role="status" aria-live="polite" style="font-size: 0.9rem; color: #c8a25a; margin-top: 12px; min-height: 1.2em;"></p>
            <p style="font-size: 0.9rem; color: #8a94a6; margin-top: 12px; display: flex; align-items: center; justify-content: center; gap: 6px;">Or call: <a href="tel:__CONTACT_PHONE_TEL__" class="phone-link" style="color: #c8a25a; text-decoration: none; display: inline-flex; align-items: center; gap: 6px;">__ICON_PHONE__ __CONTACT_PHONE__</a></p>
        </div>
    </div>
    <script>
        function openInvestorModal() {
            alert('Investor materials coming soon. Email __CONTACT_EMAIL__ for early access.');
        }

        // Interim lead capture. This hands the submission to the visitor's mail
        // client rather than posting to the backend: /intake requires twelve
        // fields (two of them internal-only and never public), so this three
        // field form has no endpoint it can legitimately post to yet. Before
        // this, the button did nothing at all and every submission was silently
        // discarded. Replace with a real POST once the public intake contract
        // is decided -- see TASKS.md.
        (function () {
            var form = document.getElementById('lead-form');
            if (!form) { return; }
            form.addEventListener('submit', function (event) {
                event.preventDefault();
                var biz = document.getElementById('lead-biz').value.trim();
                var loc = document.getElementById('lead-loc').value.trim();
                var email = document.getElementById('lead-email').value.trim();
                if (!biz || !loc || !email) { return; }
                var subject = 'Free website application: ' + biz;
                var body = 'Business name: ' + biz + '\\n'
                         + 'Location: ' + loc + '\\n'
                         + 'Email: ' + email + '\\n';
                var status = document.getElementById('lead-form-status');
                status.textContent = 'Opening your email app to send this to our team. '
                                   + 'If nothing happens, call __CONTACT_PHONE__.';
                window.location.href = 'mailto:__CONTACT_EMAIL__'
                    + '?subject=' + encodeURIComponent(subject)
                    + '&body=' + encodeURIComponent(body);
            });
        })();
    </script>
</body>
</html>
"""
