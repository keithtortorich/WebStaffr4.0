# Post-Deploy Verification Checklist

**Run these tests after push deploys to Vercel.**

---

## 1. Landing Page Loads

**Test:** Visit `https://webstaff.com/` (or your domain)

- [ ] Page loads without errors
- [ ] Canonical message visible in H2: "You don't need more leads..."
- [ ] Subheading: "WebStaffr answers your calls 24/7..."
- [ ] Three CTA buttons present: See Demos | Apply Now | Investor Access
- [ ] "Live Demo Sites" section visible with numbered list (1-10)

---

## 2. Demo Site Links Work (10 tests)

**Test each:** Click the demo link on landing page

| # | Demo | Link | Status |
|---|------|------|--------|
| 1 | Luna Salon | `/demos/salon` | [ ] Works |
| 2 | Rivera Plumbing | `/demos/plumbing` | [ ] Works |
| 3 | Kim Electric | `/demos/electrician` | [ ] Works |
| 4 | Mendez Construction | `/demos/contractor` | [ ] Works |
| 5 | Green Med Spa | `/demos/medspa` | [ ] Works |
| 6 | Bright Smile Dental | `/demos/dentist` | [ ] Works |
| 7 | Park Realty Group | `/demos/realestate` | [ ] Works |
| 8 | Rodriguez Law | `/demos/lawfirm` | [ ] Works |
| 9 | Ironclad Fitness | `/demos/gym` | [ ] Works |
| 10 | Nonna's Recipe | `/demos/restaurant` | [ ] Works |

**For each demo site, verify:**
- [ ] Page loads without 404 or error
- [ ] Site hero section visible with canonical messaging
- [ ] Business name displayed correctly
- [ ] Services list visible
- [ ] Lead capture form present
- [ ] Angel chat widget visible (bottom right, pulsing)
- [ ] No fake data (never-fabricate rule enforced)

---

## 3. Investor Resources (1 test)

**Test:** Click "Investor Access" on landing page or visit `/investors/pitch`

- [ ] Page/API endpoint responds (JSON or PDF)
- [ ] If JSON: unit economics visible (ARPU, margin, CAC payback, LTV)
- [ ] If JSON: canonical message visible ("You don't need more leads...")
- [ ] Contact info present (keithtortorich@gmail.com, phone number)
- [ ] Download button works (if PDF available)

---

## 4. Site Template Updates

**Test:** Open any demo site and verify hero section

- [ ] Hero tag shows "Industry - 24/7 Answering"
- [ ] H1 headline: "Stop losing jobs you already paid to generate"
- [ ] Hero subtitle mentions "Every call answered. Every lead followed up."
- [ ] CTA buttons say "Start 30-Day Free Trial" and "See How It Works"

---

## 5. Messaging Consistency

**Test:** Read copy across pages

- [ ] Landing page hero: canonical message present
- [ ] Demo sites: canonical message in hero
- [ ] Investor email subject line: "You don't need more leads..."
- [ ] No "AI" language in customer-facing copy
- [ ] No em-dashes (use single dash or double hyphen)
- [ ] Contractor language used ("on the job," "on a ladder," etc.)

---

## 6. Technical Checks

**Test:** Browser console and network

- [ ] No JavaScript errors in console
- [ ] No 404s in network tab
- [ ] Page load time < 2 seconds
- [ ] All images load correctly
- [ ] No CORS errors (demo sites served under `/sites/` with CORS enabled)
- [ ] JSON-LD schema present on demo sites (view page source, search for `@type`)

---

## 7. Form Submission (Optional)

**Test:** Lead capture form on landing page

- [ ] Form submits without error
- [ ] Submission recorded in database
- [ ] Confirmation message shown (or email sent)

---

## 8. Angel Widget (Optional)

**Test:** Chat widget on demo site

- [ ] Widget loads in bottom-right corner
- [ ] Hover animation works (pulsing)
- [ ] Click opens chat interface
- [ ] Messages can be sent (if backend configured)

---

## Troubleshooting

| Issue | Check | Fix |
|-------|-------|-----|
| Demo link returns 404 | Tenant exists in DB | Run `seed_demo_tenants.py` or submit intake form |
| Demo link shows no data | Intake submission exists | Verify latest submission has real data (not null) |
| Hero headline missing | Template renders | Check `webstaffr/templates/site/home.html` deployed correctly |
| Investor endpoint returns 500 | Endpoint configured | Check `/investors/pitch` route in `landing_router.py` |
| Angel widget not showing | CORS configured correctly | Verify `/sites/` in `_CORS_SCOPED_PREFIXES` |

---

## Rollback Indicators

Stop and rollback if you see:
- [ ] Landing page doesn't load
- [ ] All 10 demo links return 404
- [ ] Investor endpoint returns 500
- [ ] Site template breaks (missing content)
- [ ] Security: internal fields leaking (lead_routing, approver, etc.)

**Rollback command:**
```bash
git revert <commit_hash>
git push origin main
```

---

## Sign-Off

Once all checks pass:

- [ ] All 11 links functional
- [ ] Canonical messaging visible across pages
- [ ] No errors in console
- [ ] Demo sites render correctly
- [ ] Investor resources available
- [ ] Messaging consistent (no "AI", no em-dashes, contractor language)

**Status:** ✓ DEPLOYMENT SUCCESSFUL

---

**Time to verify:** ~15 minutes  
**Date verified:** ____________________  
**Verified by:** ____________________

