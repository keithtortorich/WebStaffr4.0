"""WebStaffr public landing page and investor resources.

Serves the landing page at GET /, demo site previews, and the full
business plan PDF for investors.
"""

from __future__ import annotations

from fastapi import APIRouter

landing_router = APIRouter(tags=["public"])


@landing_router.get("/", response_class=None)
async def landing_page():
    """Serve the public landing page with embedded investor modal and demo gallery."""
    from fastapi.responses import HTMLResponse

    # Read the landing page HTML (created separately as static asset or inline)
    # For now, return a placeholder that redirects to the static version
    # In production, this will read from a file or serve inline
    return HTMLResponse(content=_LANDING_PAGE_HTML)


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
        "problem": "27% of home-service calls go unanswered. 85% of voicemail callers never call back. A single missed job costs $500-$5,000.",
        "solution": "WebStaffr answers every call 24/7. $497/month. Built for contractors.",
        "unit_economics": {
            "arpu_monthly": 487,
            "gross_margin_pct": 88,
            "cac_payback_months": 4,
            "ltv": 8500
        },
        "ask": "$15K-50K SAFE",
        "contact": {
            "email": "keith@webstaff.com",
            "phone": "(888) 302-8368"
        },
        "pdf": "Full PDF available at deployment — email for early access"
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
    <title>WebStaffr — AI Staff for Home Services</title>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
</head>
<body style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; margin: 0; padding: 20px; background: #0a0c0f; color: #f0f2f5;">
    <div style="max-width: 1200px; margin: 0 auto;">
        <h1 style="font-size: 3.5rem; margin-bottom: 16px; color: #c8a25a;">WebStaffr</h1>
        <h2 style="font-size: 1.5rem; color: #f0f2f5; max-width: 700px; margin-bottom: 24px; font-weight: 400; line-height: 1.6;">
            You don't need more leads. You need to stop losing the ones you already have.
        </h2>
        <p style="font-size: 1rem; color: #8a94a6; max-width: 600px; margin-bottom: 32px; line-height: 1.6;">
            WebStaffr answers your calls 24/7 so you don't lose jobs you already paid to generate.
            Built for contractors. $497/month. Free for 30 days.
        </p>
        <div style="display: flex; gap: 16px; flex-wrap: wrap;">
            <a href="#demos" style="background: linear-gradient(135deg, #c8a25a, #dab87a); color: #0a0c0f; padding: 16px 32px; border-radius: 8px; text-decoration: none; font-weight: 600; cursor: pointer;">
                See Demos
            </a>
            <a href="#lead-capture" style="background: transparent; color: #c8a25a; padding: 16px 32px; border: 2px solid rgba(255,255,255,0.12); border-radius: 8px; text-decoration: none; font-weight: 600;">
                Apply Now
            </a>
            <a href="#investorModal" onclick="openInvestorModal(); return false;" style="background: transparent; color: #c8a25a; padding: 16px 32px; border: 2px solid rgba(255,255,255,0.12); border-radius: 8px; text-decoration: none; font-weight: 600;">
                Investor Access
            </a>
        </div>
        <hr style="border: none; border-top: 1px solid rgba(255,255,255,0.06); margin: 60px 0;">
        <div id="demos" style="margin-bottom: 60px;">
            <h2 style="color: #c8a25a; margin-bottom: 24px;">Live Demo Sites</h2>
            <p style="color: #8a94a6; font-size: 0.9rem; margin-bottom: 16px;">Click any to see a full working site generated in 48 hours:</p>
            <div style="display: grid; grid-template-columns: repeat(auto-fill, minmax(220px, 1fr)); gap: 16px;">
                <a href="/demos/salon" style="padding: 16px; background: rgba(255,255,255,0.04); border: 1px solid rgba(255,255,255,0.06); border-radius: 8px; text-decoration: none; color: inherit; transition: all 0.3s; display: block;">
                    <strong style="color: #c8a25a;">1. Luna Salon</strong><br><span style="color: #8a94a6; font-size: 0.85rem;">Hair & Beauty</span>
                </a>
                <a href="/demos/plumbing" style="padding: 16px; background: rgba(255,255,255,0.04); border: 1px solid rgba(255,255,255,0.06); border-radius: 8px; text-decoration: none; color: inherit; transition: all 0.3s; display: block;">
                    <strong style="color: #c8a25a;">2. Rivera Plumbing</strong><br><span style="color: #8a94a6; font-size: 0.85rem;">24/7 Service</span>
                </a>
                <a href="/demos/electrician" style="padding: 16px; background: rgba(255,255,255,0.04); border: 1px solid rgba(255,255,255,0.06); border-radius: 8px; text-decoration: none; color: inherit; transition: all 0.3s; display: block;">
                    <strong style="color: #c8a25a;">3. Kim Electric</strong><br><span style="color: #8a94a6; font-size: 0.85rem;">Licensed & Bonded</span>
                </a>
                <a href="/demos/contractor" style="padding: 16px; background: rgba(255,255,255,0.04); border: 1px solid rgba(255,255,255,0.06); border-radius: 8px; text-decoration: none; color: inherit; transition: all 0.3s; display: block;">
                    <strong style="color: #c8a25a;">4. Mendez Construction</strong><br><span style="color: #8a94a6; font-size: 0.85rem;">Full Service Remodel</span>
                </a>
                <a href="/demos/medspa" style="padding: 16px; background: rgba(255,255,255,0.04); border: 1px solid rgba(255,255,255,0.06); border-radius: 8px; text-decoration: none; color: inherit; transition: all 0.3s; display: block;">
                    <strong style="color: #c8a25a;">5. Green Med Spa</strong><br><span style="color: #8a94a6; font-size: 0.85rem;">Med-Grade Skincare</span>
                </a>
                <a href="/demos/dentist" style="padding: 16px; background: rgba(255,255,255,0.04); border: 1px solid rgba(255,255,255,0.06); border-radius: 8px; text-decoration: none; color: inherit; transition: all 0.3s; display: block;">
                    <strong style="color: #c8a25a;">6. Bright Smile Dental</strong><br><span style="color: #8a94a6; font-size: 0.85rem;">Family Dentistry</span>
                </a>
                <a href="/demos/realestate" style="padding: 16px; background: rgba(255,255,255,0.04); border: 1px solid rgba(255,255,255,0.06); border-radius: 8px; text-decoration: none; color: inherit; transition: all 0.3s; display: block;">
                    <strong style="color: #c8a25a;">7. Park Realty Group</strong><br><span style="color: #8a94a6; font-size: 0.85rem;">Local Experts</span>
                </a>
                <a href="/demos/lawfirm" style="padding: 16px; background: rgba(255,255,255,0.04); border: 1px solid rgba(255,255,255,0.06); border-radius: 8px; text-decoration: none; color: inherit; transition: all 0.3s; display: block;">
                    <strong style="color: #c8a25a;">8. Rodriguez Law</strong><br><span style="color: #8a94a6; font-size: 0.85rem;">Criminal & Family</span>
                </a>
                <a href="/demos/gym" style="padding: 16px; background: rgba(255,255,255,0.04); border: 1px solid rgba(255,255,255,0.06); border-radius: 8px; text-decoration: none; color: inherit; transition: all 0.3s; display: block;">
                    <strong style="color: #c8a25a;">9. Ironclad Fitness</strong><br><span style="color: #8a94a6; font-size: 0.85rem;">Small Group Training</span>
                </a>
                <a href="/demos/restaurant" style="padding: 16px; background: rgba(255,255,255,0.04); border: 1px solid rgba(255,255,255,0.06); border-radius: 8px; text-decoration: none; color: inherit; transition: all 0.3s; display: block;">
                    <strong style="color: #c8a25a;">10. Nonna's Recipe</strong><br><span style="color: #8a94a6; font-size: 0.85rem;">Authentic Italian</span>
                </a>
            </div>
        </div>
        <div style="background: rgba(200, 162, 90, 0.1); border: 1px solid rgba(200, 162, 90, 0.3); padding: 24px; border-radius: 8px; margin-top: 40px; margin-bottom: 60px;">
            <h3 style="color: #c8a25a; margin-top: 0;">Investors</h3>
            <p style="color: #8a94a6; margin: 0;">See the full business plan, unit economics, and why this works:</p>
            <a href="/investors/pitch" onclick="event.preventDefault(); fetch('/investors/pitch.pdf').then(r => r.blob()).then(b => window.open(URL.createObjectURL(b)));" style="display: inline-block; margin-top: 12px; background: linear-gradient(135deg, #c8a25a, #dab87a); color: #0a0c0f; padding: 12px 24px; border-radius: 6px; text-decoration: none; font-weight: 600;">
                Download Pitch Deck →
            </a>
            <p style="color: #8a94a6; font-size: 0.9rem; margin-top: 12px; margin-bottom: 0;">Or email: <a href="mailto:keith@webstaff.com" style="color: #c8a25a;">keith@webstaff.com</a></p>
        </div>
        <div id="lead-capture" style="background: rgba(15, 31, 58, 0.5); padding: 40px; border-radius: 8px; text-align: center; margin-bottom: 60px;">
            <h2 style="margin-top: 0; color: #c8a25a;">Get Your Free Website</h2>
            <p style="color: #8a94a6; margin-bottom: 24px;">Answer 3 quick questions. We build it in 48 hours. Try it free for 30 days.</p>
            <form style="max-width: 400px; margin: 0 auto; display: flex; flex-direction: column; gap: 12px;">
                <input type="text" placeholder="Your business name" style="padding: 12px; background: rgba(255,255,255,0.04); border: 1px solid rgba(255,255,255,0.06); border-radius: 6px; color: #f0f2f5;" required>
                <input type="text" placeholder="Your location" style="padding: 12px; background: rgba(255,255,255,0.04); border: 1px solid rgba(255,255,255,0.06); border-radius: 6px; color: #f0f2f5;" required>
                <input type="email" placeholder="Your email" style="padding: 12px; background: rgba(255,255,255,0.04); border: 1px solid rgba(255,255,255,0.06); border-radius: 6px; color: #f0f2f5;" required>
                <button type="submit" style="padding: 12px; background: linear-gradient(135deg, #c8a25a, #dab87a); color: #0a0c0f; border: none; border-radius: 6px; font-weight: 600; cursor: pointer;">
                    Apply for Free Website →
                </button>
            </form>
            <p style="font-size: 0.9rem; color: #8a94a6; margin-top: 12px;">Or call: <a href="tel:+18883028368" style="color: #c8a25a; text-decoration: none;">(888) 302-8368</a></p>
        </div>
    </div>
    <script>
        function openInvestorModal() {
            alert('Investor materials coming soon. Email keith@webstaff.com for early access.');
        }
    </script>
</body>
</html>
"""
