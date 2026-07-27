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
        <h1 style="font-size: 2.5rem; margin-bottom: 24px; color: #f0f2f5;">WebStaffr — One Problem, One Solution</h1>

        <div style="background: rgba(200, 162, 90, 0.08); border-left: 4px solid #c8a25a; padding: 32px; margin-bottom: 60px; border-radius: 4px;">
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

        <div style="margin-bottom: 60px;">
            <h3 style="color: #c8a25a; margin-bottom: 20px;">The Math That Makes It Real</h3>
            <div style="background: rgba(255,255,255,0.02); border: 1px solid rgba(255,255,255,0.06); padding: 24px; border-radius: 8px; margin-bottom: 24px;">
                <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 20px; margin-bottom: 24px;">
                    <div>
                        <div style="font-size: 2rem; font-weight: 600; color: #c8a25a;">27%</div>
                        <div style="color: #8a94a6; font-size: 0.9rem;">of home service calls go unanswered</div>
                    </div>
                    <div>
                        <div style="font-size: 2rem; font-weight: 600; color: #c8a25a;">78%</div>
                        <div style="color: #8a94a6; font-size: 0.9rem;">of homeowners hire whoever responds first</div>
                    </div>
                </div>
                <p style="color: #8a94a6; margin: 0; line-height: 1.8;">
                    <strong style="color: #f0f2f5;">If you miss 10 calls in a week:</strong> most leave voicemail, and most of those never call back. The majority hire your competitor.
                    <br><br>
                    <strong style="color: #c8a25a;">A single missed job = $500–$5,000.</strong> A single missed call costs more than a month of WebStaffr.
                </p>
            </div>
        </div>

        <div style="background: rgba(200, 162, 90, 0.08); border-left: 4px solid #c8a25a; padding: 32px; margin-bottom: 60px; border-radius: 4px;">
            <h2 style="color: #c8a25a; margin-top: 0; font-size: 1.5rem;">The One Solution</h2>
            <p style="color: #f0f2f5; line-height: 1.8; margin: 0 0 16px 0; font-size: 1.1rem;">
                <strong>WebStaffr answers your phone so you don't have to.</strong>
            </p>
            <p style="color: #8a94a6; line-height: 1.8; margin: 0;">
                It's not software. It's not AI. It's not a chatbot.
                <br><br>
                It's a <strong>24/7 Receptionist</strong> that picks up every call, pre-qualifies the lead, and books appointments directly into your calendar. While you're on a ladder, under a house, or driving to the next job, your phone is still ringing—and still getting answered.
            </p>
        </div>

        <div style="margin-bottom: 60px;">
            <h3 style="color: #c8a25a; margin-bottom: 20px;">Why WebStaffr</h3>
            <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 20px;">
                <div style="background: rgba(255,0,0,0.05); border: 1px solid rgba(255,100,100,0.2); padding: 16px; border-radius: 6px;">
                    <div style="color: #f0f2f5; font-weight: 600; margin-bottom: 8px;">Hire a human receptionist</div>
                    <div style="color: #8a94a6; font-size: 0.9rem;">$3,500+/month. Can't work 24/7. Calls in sick. Takes vacations. Can't handle 3 calls at once.</div>
                </div>
                <div style="background: rgba(255,0,0,0.05); border: 1px solid rgba(255,100,100,0.2); padding: 16px; border-radius: 6px;">
                    <div style="color: #f0f2f5; font-weight: 600; margin-bottom: 8px;">Let calls go to voicemail</div>
                    <div style="color: #8a94a6; font-size: 0.9rem;">Most never call back. They call your competitor instead.</div>
                </div>
                <div style="background: rgba(255,0,0,0.05); border: 1px solid rgba(255,100,100,0.2); padding: 16px; border-radius: 6px;">
                    <div style="color: #f0f2f5; font-weight: 600; margin-bottom: 8px;">Call back later</div>
                    <div style="color: #8a94a6; font-size: 0.9rem;">The lead is already gone. 78% hire whoever responds first.</div>
                </div>
                <div style="background: rgba(200,162,90,0.1); border: 1px solid rgba(200,162,90,0.3); padding: 16px; border-radius: 6px;">
                    <div style="color: #c8a25a; font-weight: 600; margin-bottom: 8px;">WebStaffr</div>
                    <div style="color: #8a94a6; font-size: 0.9rem;">$497/month. 24/7/365. Answers every call. Qualifies every lead. Books every job. Built for contractors.</div>
                </div>
            </div>
        </div>

        <div style="margin-bottom: 60px;">
            <h3 style="color: #c8a25a; margin-bottom: 24px;">See It Live — 10 Home Service Industries</h3>
            <div style="display: grid; grid-template-columns: repeat(auto-fill, minmax(200px, 1fr)); gap: 16px;">
                <a href="/demos/hvac" style="padding: 16px; background: rgba(255,255,255,0.04); border: 1px solid rgba(255,255,255,0.06); border-radius: 8px; text-decoration: none; color: inherit; transition: all 0.3s; display: block;">
                    <strong style="color: #c8a25a;">1. HVAC</strong><br><span style="color: #8a94a6; font-size: 0.85rem;">66% unanswered</span>
                </a>
                <a href="/demos/plumbing" style="padding: 16px; background: rgba(255,255,255,0.04); border: 1px solid rgba(255,255,255,0.06); border-radius: 8px; text-decoration: none; color: inherit; transition: all 0.3s; display: block;">
                    <strong style="color: #c8a25a;">2. Plumbing</strong><br><span style="color: #8a94a6; font-size: 0.85rem;">26% unanswered</span>
                </a>
                <a href="/demos/electrical" style="padding: 16px; background: rgba(255,255,255,0.04); border: 1px solid rgba(255,255,255,0.06); border-radius: 8px; text-decoration: none; color: inherit; transition: all 0.3s; display: block;">
                    <strong style="color: #c8a25a;">3. Electrical</strong><br><span style="color: #8a94a6; font-size: 0.85rem;">24% unanswered</span>
                </a>
                <a href="/demos/roofing" style="padding: 16px; background: rgba(255,255,255,0.04); border: 1px solid rgba(255,255,255,0.06); border-radius: 8px; text-decoration: none; color: inherit; transition: all 0.3s; display: block;">
                    <strong style="color: #c8a25a;">4. Roofing</strong><br><span style="color: #8a94a6; font-size: 0.85rem;">Storm-driven</span>
                </a>
                <a href="/demos/water-damage" style="padding: 16px; background: rgba(255,255,255,0.04); border: 1px solid rgba(255,255,255,0.06); border-radius: 8px; text-decoration: none; color: inherit; transition: all 0.3s; display: block;">
                    <strong style="color: #c8a25a;">5. Water Damage</strong><br><span style="color: #8a94a6; font-size: 0.85rem;">24/7 emergency</span>
                </a>
                <a href="/demos/garage-door" style="padding: 16px; background: rgba(255,255,255,0.04); border: 1px solid rgba(255,255,255,0.06); border-radius: 8px; text-decoration: none; color: inherit; transition: all 0.3s; display: block;">
                    <strong style="color: #c8a25a;">6. Garage Door</strong><br><span style="color: #8a94a6; font-size: 0.85rem;">After-hours demand</span>
                </a>
                <a href="/demos/pest-control" style="padding: 16px; background: rgba(255,255,255,0.04); border: 1px solid rgba(255,255,255,0.06); border-radius: 8px; text-decoration: none; color: inherit; transition: all 0.3s; display: block;">
                    <strong style="color: #c8a25a;">7. Pest Control</strong><br><span style="color: #8a94a6; font-size: 0.85rem;">27% unanswered</span>
                </a>
                <a href="/demos/landscaping" style="padding: 16px; background: rgba(255,255,255,0.04); border: 1px solid rgba(255,255,255,0.06); border-radius: 8px; text-decoration: none; color: inherit; transition: all 0.3s; display: block;">
                    <strong style="color: #c8a25a;">8. Landscaping</strong><br><span style="color: #8a94a6; font-size: 0.85rem;">High volume</span>
                </a>
                <a href="/demos/tree-service" style="padding: 16px; background: rgba(255,255,255,0.04); border: 1px solid rgba(255,255,255,0.06); border-radius: 8px; text-decoration: none; color: inherit; transition: all 0.3s; display: block;">
                    <strong style="color: #c8a25a;">9. Tree Service</strong><br><span style="color: #8a94a6; font-size: 0.85rem;">Storm-driven</span>
                </a>
                <a href="/demos/cleaning" style="padding: 16px; background: rgba(255,255,255,0.04); border: 1px solid rgba(255,255,255,0.06); border-radius: 8px; text-decoration: none; color: inherit; transition: all 0.3s; display: block;">
                    <strong style="color: #c8a25a;">10. Cleaning</strong><br><span style="color: #8a94a6; font-size: 0.85rem;">Recurring</span>
                </a>
            </div>
        </div>

        <div style="text-align: center; padding: 40px 0; border-top: 1px solid rgba(255,255,255,0.06);">
            <h2 style="color: #f0f2f5; margin: 0 0 16px 0; font-size: 1.3rem;">
                <strong style="color: #c8a25a;">You don't need more leads.</strong><br>You need to stop losing the ones you already have.
            </h2>
            <p style="color: #8a94a6; margin: 0; max-width: 600px; margin-left: auto; margin-right: auto;">
                WebStaffr recovers revenue by making sure you never miss another call. Everything else—the website, the reviews, the follow-ups—is just how we do it.
            </p>
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
