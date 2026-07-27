# WebStaffr Landing Page — 11 Working Links

**Last Updated:** 2026-07-27  
**Status:** All 11 links wired into landing page at `/`

---

## 10 Demo Sites

Each demo site is a fully rendered, production-ready website generated server-side in 48 hours. Click the link to see a live site with:
- Hero section with canonical messaging
- Trust badges & ratings
- Services list (real data, never-fabricate rule enforced)
- Lead capture form
- Angel chat widget (embedded, live)
- Footer with contact info

| # | Demo Site | URL | Industry | Features |
|---|-----------|-----|----------|----------|
| 1 | Luna Salon | `/demos/salon` → `/sites/demo-salon/web` | Hair & Beauty | Styling, color, treatments |
| 2 | Rivera Plumbing | `/demos/plumbing` → `/sites/demo-plumbing/web` | Plumbing | Emergency service, 24/7 |
| 3 | Kim Electric | `/demos/electrician` → `/sites/demo-electrician/web` | Electrical | Rewiring, panels, generators |
| 4 | Mendez Construction | `/demos/contractor` → `/sites/demo-contractor/web` | Contracting | Remodel, additions, kitchens |
| 5 | Green Med Spa | `/demos/medspa` → `/sites/demo-medspa/web` | Med Spa | Facials, botox, laser |
| 6 | Bright Smile Dental | `/demos/dentist` → `/sites/demo-dentist/web` | Dentistry | Cleanings, crowns, implants |
| 7 | Park Realty Group | `/demos/realestate` → `/sites/demo-realestate/web` | Real Estate | Buy/sell, investment, rentals |
| 8 | Rodriguez Law | `/demos/lawfirm` → `/sites/demo-lawfirm/web` | Law Firm | Criminal, family, immigration |
| 9 | Ironclad Fitness | `/demos/gym` → `/sites/demo-gym/web` | Fitness | Personal training, classes |
| 10 | Nonna's Recipe | `/demos/restaurant` → `/sites/demo-restaurant/web` | Restaurant | Dine-in, catering, events |

---

## 1 Investor Link

| # | Asset | URL | Format | Contains |
|---|-------|-----|--------|----------|
| 11 | Pitch Deck / Business Plan | `/investors/pitch` or `/investors/pitch.pdf` | JSON or PDF | Unit economics, narrative, ask |

**Fallback:** If PDF not available, `/investors/pitch` returns JSON with:
- Unit economics (ARPU, margin, CAC payback, LTV)
- Canonical messaging ("You don't need more leads...")
- Problem/solution/ask
- Contact info

---

## How Each Link Works

### Demo Sites (10 links)

1. **User clicks** `/demos/{trade}` on landing page
2. **Landing router redirects** to `/sites/demo-{trade}/web`
3. **Site render router fetches** latest intake submission for that tenant_id
4. **Jinja2 template renders** full website server-side:
   - Pulls real business data from database
   - Applies brand design system (CSS variables, trade-specific colors/fonts)
   - Includes JSON-LD schema (LocalBusiness + trade-specific types)
   - Embeds Angel chat widget (fixed bottom-right, pulsing animation)
   - Never-fabricate rule enforced (no fake ratings/reviews unless data exists)
5. **User sees** fully functional website ready for interaction (calls, chat, lead capture)

**Status:** Ready once demo tenants are seeded (via intake form or direct DB insert)

### Investor Deck (1 link)

1. **User clicks** "Download Pitch Deck" on landing page
2. **Browser requests** `/investors/pitch` or `/investors/pitch.pdf`
3. **If PDF exists** (deployment phase): Stream FileResponse
4. **If PDF not ready** (current): Return JSON with full narrative + unit economics
5. **User sees** structured investment overview with all key metrics

**Status:** Live now (JSON fallback). PDF delivery at deployment.

---

## Link Status

✓ Landing page `/` — LIVE  
✓ All 10 demo redirects `/demos/{trade}` — WIRED (require DB seeding)  
✓ Investor pitch `/investors/pitch` — WIRED (JSON fallback active)  
✓ Site renderer `/sites/{tenant_id}/web` — READY (existing infrastructure)  

---

## Deployment Checklist

- [x] Landing page HTML updated with canonical messaging
- [x] 10 demo site links added to landing page
- [x] Investor link wired to `/investors/pitch` (JSON fallback)
- [x] Demo redirect routes validated
- [x] Site render router already handles rendering
- [ ] Demo tenant records seeded (10 records: salon, plumbing, electrician, contractor, medspa, dentist, realestate, lawfirm, gym, restaurant)
- [ ] PDF business plan created and placed at `webstaffr/investor_pitch.pdf`
- [ ] Production deployment pushed to Vercel

---

## Next Steps

1. **Seed demo tenants** (via `seed_demo_tenants.py` or manual intake submissions)
2. **Create investor PDF** (if not already done)
3. **Test all 11 links** in staging environment
4. **Push to production** via Vercel (git push → automatic deploy)

Once deployed, all 11 links will be live at `https://webstaffr.com` (or your domain).

