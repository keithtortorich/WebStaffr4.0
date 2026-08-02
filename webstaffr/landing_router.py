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
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>WebStaffr | 24/7 Receptionist for Home Services</title>
  <meta name="description" content="Stop losing jobs to missed calls. WebStaffr answers your phone 24/7. No AI. No setup fees. Get a real job or it's free.">
  <style>
    :root {
      --primary: #4169E1;        /* Royal blue */
      --secondary: #000080;      /* Navy */
      --accent: #FF6600;         /* Electric orange */
      --bg: #e0e0e0;             /* Light gray */
      --text: #16202e;           /* Dark text */
      --text-light: #5a6672;     /* Muted text */
      --border: #e2e6ec;
      --shadow: 0 2px 8px rgba(16, 24, 38, 0.1);
    }

    * { box-sizing: border-box; }

    body {
      margin: 0;
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
      color: var(--text);
      line-height: 1.6;
      background: var(--bg);
    }

    header {
      background: white;
      border-bottom: 1px solid var(--border);
      padding: 16px 20px;
      position: sticky;
      top: 0;
      z-index: 100;
    }

    .header-inner {
      max-width: 1100px;
      margin: 0 auto;
      display: flex;
      align-items: center;
      justify-content: space-between;
    }

    .logo {
      font-size: 24px;
      font-weight: 700;
      color: var(--secondary);
      text-decoration: none;
    }

    nav {
      display: flex;
      gap: 32px;
      align-items: center;
    }

    nav a {
      color: var(--text);
      text-decoration: none;
      font-size: 14px;
      font-weight: 500;
    }

    nav a:hover {
      color: var(--primary);
    }

    .cta-button {
      background: var(--accent);
      color: white;
      padding: 10px 20px;
      border-radius: 4px;
      text-decoration: none;
      font-weight: 600;
      font-size: 14px;
      border: none;
      cursor: pointer;
      transition: background 0.2s;
    }

    .cta-button:hover {
      background: #e55a00;
    }

    section {
      padding: 60px 20px;
    }

    .container {
      max-width: 1100px;
      margin: 0 auto;
    }

    /* Hero */
    .hero {
      background: linear-gradient(135deg, white 0%, var(--bg) 100%);
      padding: 80px 20px;
      text-align: center;
    }

    .hero h1 {
      font-size: 48px;
      font-weight: 700;
      margin: 0 0 20px 0;
      color: var(--text);
      line-height: 1.2;
    }

    .hero h2 {
      font-size: 24px;
      font-weight: 400;
      margin: 0 0 40px 0;
      color: var(--text-light);
      line-height: 1.4;
    }

    .trust-bar {
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
      gap: 24px;
      margin: 40px 0;
      padding: 30px;
      background: white;
      border-radius: 8px;
      box-shadow: var(--shadow);
    }

    .trust-item {
      text-align: center;
    }

    .trust-stat {
      font-size: 28px;
      font-weight: 700;
      color: var(--accent);
      margin: 0 0 8px 0;
    }

    .trust-label {
      font-size: 14px;
      color: var(--text-light);
      margin: 0;
    }

    .hero-ctas {
      display: flex;
      flex-direction: column;
      gap: 12px;
      align-items: center;
      margin: 40px 0;
    }

    .primary-cta {
      background: var(--accent);
      color: white;
      padding: 16px 32px;
      border: none;
      border-radius: 4px;
      font-size: 16px;
      font-weight: 600;
      cursor: pointer;
      text-decoration: none;
      display: inline-block;
      transition: background 0.2s;
    }

    .primary-cta:hover {
      background: #e55a00;
    }

    .secondary-cta {
      color: var(--primary);
      font-size: 14px;
      font-weight: 500;
      text-decoration: none;
    }

    .secondary-cta:hover {
      text-decoration: underline;
    }

    /* Math Section */
    .math-section {
      background: white;
      padding: 60px 20px;
    }

    .math-section h2 {
      font-size: 36px;
      font-weight: 700;
      text-align: center;
      margin-bottom: 40px;
      color: var(--text);
    }

    .math-content {
      max-width: 700px;
      margin: 0 auto;
      font-size: 16px;
      line-height: 1.8;
    }

    .math-content p {
      margin: 16px 0;
    }

    .highlight {
      color: var(--accent);
      font-weight: 700;
    }

    /* How It Works */
    .how-it-works {
      padding: 60px 20px;
    }

    .how-it-works h2 {
      font-size: 36px;
      font-weight: 700;
      text-align: center;
      margin-bottom: 50px;
      color: var(--text);
    }

    .steps {
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
      gap: 32px;
    }

    .step {
      background: white;
      padding: 30px;
      border-radius: 8px;
      box-shadow: var(--shadow);
      text-align: center;
    }

    .step-num {
      display: inline-flex;
      align-items: center;
      justify-content: center;
      width: 40px;
      height: 40px;
      background: var(--accent);
      color: white;
      border-radius: 50%;
      font-weight: 700;
      font-size: 18px;
      margin-bottom: 16px;
    }

    .step h3 {
      font-size: 20px;
      font-weight: 600;
      margin: 16px 0;
      color: var(--text);
    }

    .step p {
      font-size: 14px;
      color: var(--text-light);
      margin: 12px 0;
    }

    /* Pricing */
    .pricing {
      background: white;
      padding: 60px 20px;
    }

    .pricing h2 {
      font-size: 36px;
      font-weight: 700;
      text-align: center;
      margin-bottom: 50px;
      color: var(--text);
    }

    .pricing-grid {
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
      gap: 24px;
    }

    .pricing-card {
      border: 2px solid var(--border);
      border-radius: 8px;
      padding: 30px;
      text-align: center;
      transition: border-color 0.2s, box-shadow 0.2s;
    }

    .pricing-card:hover {
      border-color: var(--accent);
      box-shadow: 0 8px 16px rgba(255, 102, 0, 0.15);
    }

    .pricing-card.featured {
      border-color: var(--accent);
      background: linear-gradient(135deg, var(--bg) 0%, white 100%);
      transform: scale(1.05);
    }

    .pricing-label {
      font-size: 12px;
      font-weight: 700;
      color: var(--accent);
      text-transform: uppercase;
      letter-spacing: 1px;
      margin-bottom: 12px;
    }

    .pricing-name {
      font-size: 22px;
      font-weight: 700;
      color: var(--text);
      margin: 12px 0;
    }

    .pricing-price {
      font-size: 32px;
      font-weight: 700;
      color: var(--primary);
      margin: 16px 0;
    }

    .pricing-price-sub {
      font-size: 14px;
      color: var(--text-light);
      font-weight: 400;
    }

    .pricing-features {
      list-style: none;
      padding: 24px 0;
      margin: 0;
      text-align: left;
      border-top: 1px solid var(--border);
      border-bottom: 1px solid var(--border);
    }

    .pricing-features li {
      padding: 8px 0;
      font-size: 13px;
      color: var(--text-light);
    }

    .pricing-cta {
      margin-top: 24px;
    }

    /* FAQ */
    .faq {
      padding: 60px 20px;
      background: white;
    }

    .faq h2 {
      font-size: 36px;
      font-weight: 700;
      text-align: center;
      margin-bottom: 50px;
      color: var(--text);
    }

    .faq-item {
      max-width: 700px;
      margin: 0 auto 30px auto;
      border-bottom: 1px solid var(--border);
      padding-bottom: 24px;
    }

    .faq-item:last-child {
      border-bottom: none;
    }

    .faq-question {
      font-size: 18px;
      font-weight: 600;
      color: var(--text);
      margin: 0 0 12px 0;
      cursor: pointer;
    }

    .faq-answer {
      font-size: 15px;
      line-height: 1.7;
      color: var(--text-light);
      margin: 0;
    }

    /* Footer */
    footer {
      background: var(--secondary);
      color: white;
      padding: 60px 20px;
      text-align: center;
    }

    footer h2 {
      font-size: 36px;
      font-weight: 700;
      margin: 0 0 20px 0;
      color: white;
    }

    footer p {
      font-size: 16px;
      margin: 0 0 30px 0;
      opacity: 0.9;
    }

    footer .primary-cta {
      background: var(--accent);
      margin-bottom: 24px;
    }

    footer .guarantee {
      font-size: 13px;
      opacity: 0.7;
      margin-top: 20px;
    }

    @media (max-width: 768px) {
      .hero h1 {
        font-size: 32px;
      }

      .hero h2 {
        font-size: 18px;
      }

      nav {
        gap: 16px;
      }

      .pricing-card.featured {
        transform: scale(1);
      }

      .trust-bar {
        grid-template-columns: 1fr;
      }
    }
  </style>
</head>
<body>
  <!-- Header -->
  <header>
    <div class="header-inner">
      <a class="logo" href="/">WebStaffr</a>
      <nav>
        <a href="#how-it-works">HOW IT WORKS</a>
        <a href="#pricing">PRICING</a>
        <a href="#faq">FAQ</a>
        <button class="cta-button">START NOW</button>
      </nav>
    </div>
  </header>

  <!-- Hero -->
  <section class="hero">
    <div class="container">
      <h1>You left money on the table this week.</h1>
      <h2>WebStaffr answers your phone so you don't lose jobs you already paid to generate.</h2>

      <div class="trust-bar">
        <div class="trust-item">
          <div class="trust-stat">27%</div>
          <div class="trust-label">of calls go unanswered<br><span style="font-size: 12px; color: var(--accent);">That's revenue walking out the door</span></div>
        </div>
        <div class="trust-item">
          <div class="trust-stat">85%</div>
          <div class="trust-label">never call back<br><span style="font-size: 12px; color: var(--accent);">They call your competitor instead</span></div>
        </div>
        <div class="trust-item">
          <div class="trust-stat">78%</div>
          <div class="trust-label">hire whoever responds first<br><span style="font-size: 12px; color: var(--accent);">Speed = money</span></div>
        </div>
      </div>

      <div class="hero-ctas">
        <button class="primary-cta">No Card. No Contract. Get a Job Or It's Free.</button>
        <a href="#pricing" class="secondary-cta">Just Tell Me Yes</a>
      </div>
    </div>
  </section>

  <!-- Math Section -->
  <section class="math-section">
    <div class="container">
      <h2>Let's Do The Math.</h2>
      <div class="math-content">
        <p>How many calls do you think you're missing in a typical week?</p>
        <p>Most contractors we talk to say 10. Sometimes more.</p>
        <p>That's 40 a month. At $400 a job average, that's <span class="highlight">$16,000 a month.</span> <span class="highlight">$192,000 a year.</span></p>
        <p>Does that number hurt?</p>
        <p>It should.</p>
        <p>And that's just the jobs you <em>know</em> you're losing. There are more, the ones you never find out about because the customer already called someone else.</p>
        <p>That's why we built WebStaffr. Not to automate. To recover.</p>
      </div>
    </div>
  </section>

  <!-- How It Works -->
  <section class="how-it-works" id="how-it-works">
    <div class="container">
      <h2>Three Steps. Zero Risk.</h2>
      <div class="steps">
        <div class="step">
          <div class="step-num">1</div>
          <h3>Tell Us About Your Business</h3>
          <p>No card now. No long application. Just a few questions: your business name, industry, what you want customers to know.</p>
          <p style="font-size: 12px; color: var(--accent); font-weight: 600;">Start Now</p>
        </div>
        <div class="step">
          <div class="step-num">2</div>
          <h3>We Handle Your Calls</h3>
          <p>Within hours, your phone is answered 24/7. Nights, weekends, lunch breaks, while you're on a job. Every customer call gets answered. Every lead gets booked or forwarded to you.</p>
        </div>
        <div class="step">
          <div class="step-num">3</div>
          <h3>You Verify. You Decide.</h3>
          <p>In 14 days, we show you every job we captured. Real customers. Real appointments. You verify they're legitimate. If we didn't capture a job, we cancel. No bill. No hard feelings.</p>
        </div>
      </div>
    </div>
  </section>

  <!-- Pricing -->
  <section class="pricing" id="pricing">
    <div class="container">
      <h2>Simple Pricing. One Job Pays For The Month.</h2>
      <div class="pricing-grid">
        <div class="pricing-card">
          <div class="pricing-label">Test Drive</div>
          <h3 class="pricing-name">Everything Starts Here</h3>
          <div class="pricing-price">Free<div class="pricing-price-sub">14 days</div></div>
          <ul class="pricing-features">
            <li>Professional website</li>
            <li>Live appointment booking</li>
            <li>Lead capture and follow-up</li>
            <li>24/7 answering</li>
          </ul>
          <div class="pricing-cta">
            <button class="primary-cta">No Card. No Contract. Get a Job Or It's Free.</button>
          </div>
        </div>

        <div class="pricing-card featured">
          <div class="pricing-label">Most Popular</div>
          <h3 class="pricing-name">Office Staff</h3>
          <div class="pricing-price">$497<div class="pricing-price-sub">/month</div></div>
          <ul class="pricing-features">
            <li>Everything in Test Drive</li>
            <li>24/7 Receptionist</li>
            <li>Service Advisor</li>
            <li>Lead Coordinator</li>
            <li>Reputation Manager</li>
            <li>Website Operations Manager</li>
          </ul>
          <div class="pricing-cta">
            <button class="primary-cta">Get Your Office Staff Today</button>
          </div>
          <p style="font-size: 12px; color: var(--text-light); margin-top: 16px;">Month-to-month. Cancel anytime.</p>
        </div>

        <div class="pricing-card">
          <div class="pricing-label">Scale</div>
          <h3 class="pricing-name">Business Manager</h3>
          <div class="pricing-price">$2,497<div class="pricing-price-sub">/month</div></div>
          <ul class="pricing-features">
            <li>Everything in Office Staff</li>
            <li>Sales Consultant</li>
            <li>Marketing Coordinator</li>
            <li>Growth Manager</li>
          </ul>
          <div class="pricing-cta">
            <button class="cta-button">Talk To Us About Business Manager</button>
          </div>
        </div>
      </div>
    </div>
  </section>

  <!-- FAQ -->
  <section class="faq" id="faq">
    <div class="container">
      <h2>FAQ</h2>

      <div class="faq-item">
        <h3 class="faq-question">Why is the website free?</h3>
        <p class="faq-answer">Because we'd rather show you what WebStaffr can do than tell you. Once you see it working, the rest is an easy decision.</p>
      </div>

      <div class="faq-item">
        <h3 class="faq-question">What happens after 14 days?</h3>
        <p class="faq-answer">You choose. We send you the details of every job we captured. Real customers, real appointments. You verify they're real. If we didn't get any, no bill. If we did, you decide whether to keep going, month-to-month, cancel anytime.</p>
      </div>

      <div class="faq-item">
        <h3 class="faq-question">Can I switch plans later?</h3>
        <p class="faq-answer">Yes. Most contractors start with Office Staff and move to Business Manager once they've seen the results. Some scale back if they get slower. It's your business. You're in control.</p>
      </div>

      <div class="faq-item">
        <h3 class="faq-question">Is there a setup fee?</h3>
        <p class="faq-answer">No. What you see is what you pay. No surprises.</p>
      </div>

      <div class="faq-item">
        <h3 class="faq-question">I already have someone answering the phone.</h3>
        <p class="faq-answer">Good. WebStaffr covers the hours they can't: nights, weekends, lunch breaks, when you're on a job site. It backs up your team instead of replacing them. And it never calls in sick.</p>
      </div>

      <div class="faq-item">
        <h3 class="faq-question">I've been burned before.</h3>
        <p class="faq-answer">We're putting our money where our mouth is. No risk to you. 14 days, free. We get you a job or we cancel.</p>
      </div>

      <div class="faq-item">
        <h3 class="faq-question">I don't trust software like this.</h3>
        <p class="faq-answer">You shouldn't. That's why we don't ask you to trust us. We prove it works or we don't get paid. Fair?</p>
      </div>

      <div class="faq-item">
        <h3 class="faq-question">I can't afford $497.</h3>
        <p class="faq-answer">Can you afford to lose $16,000 a month? Because that's what's happening right now. What's the real concern here?</p>
      </div>

      <div class="faq-item">
        <h3 class="faq-question">Send me an email.</h3>
        <p class="faq-answer">Happy to. But real quick, what's the hesitation? Because if it works, you pay nothing. If it doesn't, you pay nothing. So what's the real objection?</p>
      </div>
    </div>
  </section>

  <!-- Footer -->
  <footer>
    <div class="container">
      <h2>Get Your Office Staff Working. Starting Today.</h2>
      <p>14 days, free. No card. No contract. No risk.<br>Just tell me yes.</p>
      <button class="primary-cta">Get Started. No Card Required.</button>
      <p class="guarantee">Backed by a 14-day performance guarantee. If we don't capture a paying job in 14 days, we cancel. No bill. No hard feelings.</p>
    </div>
  </footer>
</body>
</html>
"""
