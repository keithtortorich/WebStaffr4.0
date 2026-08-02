# Dark Mode Design System Integration Guide
## Plumbing Company Site

**Generated:** 2026-08-02  
**Theme:** Dark Mode with Warm Gold Accent  
**Status:** WCAG AA Compliant  

---

## Files Included

| File | Purpose | Size |
|------|---------|------|
| `theme.css` | CSS custom properties and base styles | 7.6 KB |
| `tailwind.config.js` | Tailwind configuration extending theme variables | 2.5 KB |
| `service_card.jinja2` | Reusable service card component | 1.6 KB |
| `cta_button.jinja2` | Call-to-action button (3 variants) | 1.5 KB |
| `booking_form.jinja2` | Service booking form component | 3.5 KB |
| `testimonial.jinja2` | Customer testimonial card | 1.5 KB |
| `accessibility_report.txt` | WCAG AA validation (all tests passing) | 8.8 KB |

---

## Quick Start

### 1. Copy Files to Your Project

```
customer-site/
├── styles/
│   └── theme.css              ← Copy here
├── templates/
│   ├── components/
│   │   ├── service_card.jinja2      ← Copy here
│   │   ├── cta_button.jinja2        ← Copy here
│   │   ├── booking_form.jinja2      ← Copy here
│   │   └── testimonial.jinja2       ← Copy here
│   └── base.jinja2
└── tailwind.config.js         ← Copy here (or merge with existing)
```

### 2. Link CSS in Your Base Template

In your `templates/base.jinja2` (or `_base.html`):

```html
<!DOCTYPE html>
<html lang="en" class="dark">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{{ page_title }}</title>
  
  <!-- Theme CSS (loads CSS custom properties) -->
  <link rel="stylesheet" href="/styles/theme.css">
  
  <!-- Tailwind CSS (compiled from tailwind.config.js) -->
  <link rel="stylesheet" href="/dist/output.css">
</head>
<body>
  {% block content %}{% endblock %}
</body>
</html>
```

**Note:** Add `class="dark"` to the `<html>` tag to enable dark mode by default.

### 3. Build Tailwind

From your project root:

```bash
npm install -D tailwindcss
npx tailwindcss -i ./styles/theme.css -o ./dist/output.css --watch
```

Or add to your build script in `package.json`:

```json
{
  "scripts": {
    "build": "tailwindcss -i ./styles/theme.css -o ./dist/output.css"
  }
}
```

### 4. Use Components in Templates

**Service Card:**
```jinja2
{% include 'components/service_card.jinja2' with context %}
```

With props:
```jinja2
{% set service = {
  'title': 'Drain Cleaning',
  'description': 'Professional drain clearing and maintenance',
  'icon_url': '/images/drain-icon.svg',
  'price': '$149',
  'action_url': '/book/drain-cleaning',
  'action_text': 'Schedule Service',
  'variant': 'default'
} %}
{% include 'components/service_card.jinja2' with context %}
```

**CTA Button:**
```jinja2
{% set button = {
  'text': 'Book Now',
  'url': '/book/emergency-service',
  'variant': 'primary',
  'size': 'md'
} %}
{% include 'components/cta_button.jinja2' with context %}
```

Variants: `primary` (gold bg), `secondary` (bordered), `tertiary` (outline)  
Sizes: `sm` (small), `md` (medium, default), `lg` (large)

**Booking Form:**
```jinja2
{% set form_fields = [
  {'name': 'name', 'label': 'Full Name', 'type': 'text', 'required': true},
  {'name': 'phone', 'label': 'Phone', 'type': 'tel', 'required': true},
  {'name': 'email', 'label': 'Email', 'type': 'email', 'required': false},
  {'name': 'service', 'label': 'Service Needed', 'type': 'select', 'required': true, 'options': [
    {'value': 'drain', 'label': 'Drain Cleaning'},
    {'value': 'leak', 'label': 'Leak Repair'},
    {'value': 'emergency', 'label': 'Emergency Service'}
  ]},
  {'name': 'message', 'label': 'Additional Details', 'type': 'textarea', 'required': false}
] %}

{% set form = {
  'action_url': '/api/book',
  'tenant_id': tenant_id,
  'form_title': 'Schedule Your Service',
  'form_description': 'Fill out the form below and we\'ll get back to you within 2 hours.',
  'fields': form_fields,
  'submit_text': 'Request Service'
} %}
{% include 'components/booking_form.jinja2' with context %}
```

**Testimonial:**
```jinja2
{% set testimonial = {
  'quote': 'Fixed our leaking pipe in 30 minutes. Professional and affordable!',
  'author_name': 'John Smith',
  'author_title': 'Homeowner, Austin TX',
  'author_image': '/images/testimonial-john.jpg',
  'rating': 5
} %}
{% include 'components/testimonial.jinja2' with context %}
```

---

## Color Palette Reference

### Backgrounds (Dark Mode)
- **Primary:** `#0F172A` — Main background
- **Secondary:** `#1E293B` — Card/elevation surfaces
- **Tertiary:** `#334155` — Borders and subtle elements

### Text
- **Primary:** `#F8FAFC` — Main text (17.06:1 contrast)
- **Muted:** `#94A3B8` — Secondary text (6.96:1 contrast)
- **Subtle:** `#B0B8C6` — Tertiary text (7.33:1 contrast)

### Accent (Gold)
- **Primary:** `#D4AF37` — CTAs, highlights
- **Hover:** `#C9A227` — Button hover states
- **Light:** `#E6C547` — Background wash

### Status
- **Success:** `#10B981` (7.04:1 contrast)
- **Error:** `#EF4444` (4.74:1 contrast)
- **Warning:** `#F59E0B` (8.31:1 contrast)

### Typography
- **Headings:** Inter, 600–700 weight
- **Body:** Inter, 400–500 weight
- **Mono:** Monaco or system monospace

---

## Customization

### Change the Accent Color

Edit `theme.css`:

```css
:root {
  --color-accent-primary: #YOUR_HEX_HERE;
  --color-accent-hover: #DARKER_HEX;
  --color-accent-light: #LIGHTER_HEX;
}
```

Then run the WCAG validator (in Python):

```python
from wcag_validator import contrast_ratio

ratio = contrast_ratio('#YOUR_HEX', '#0F172A')
print(f"Contrast ratio: {ratio}:1 (min 3.0:1 for UI components)")
```

### Add a New Component

1. Create `templates/components/your_component.jinja2`
2. Use CSS custom properties (not hardcoded colors)
3. Accept props via Jinja2 context
4. Test with `accessibility_report.txt` guidelines

Example template structure:

```jinja2
{# Your Component #}
<div class="bg-bg-secondary border border-border rounded-lg p-6">
  <h3 class="text-xl font-heading font-bold text-fg-primary">
    {{ title }}
  </h3>
  <p class="text-sm text-fg-muted">
    {{ description }}
  </p>
</div>
```

### Switch Between Light/Dark Mode

At runtime, add/remove the `dark` class on `<html>`:

```javascript
// Toggle dark mode
document.documentElement.classList.toggle('dark');

// Or programmatically:
document.documentElement.classList.add('dark');    // Enable dark
document.documentElement.classList.remove('dark'); // Disable dark
```

Tailwind's `darkMode: 'class'` config enables this automatically.

---

## Accessibility Notes

✓ **All colors tested against WCAG 2.1 Level AA**  
✓ **Dark mode backgrounds are true dark (L < 0.18)**  
✓ **All text meets 4.5:1 minimum contrast**  
✓ **All interactive elements 44x44px minimum**  
✓ **Focus states provide visible outlines**  

**When adding content:**
- Use semantic HTML (`<h1>`, `<p>`, `<label>`, etc.)
- Never rely on color alone to convey information
- Include `alt` text for all images
- Test with a screen reader (NVDA, JAWS, or VoiceOver)

---

## Troubleshooting

### Colors look wrong on mobile
- Check device brightness settings
- Test on OLED screens (gold may appear too bright)
- Verify Tailwind is compiled: `npm run build`

### Focus outlines not visible
- Check `theme.css` for `:focus-visible` rules
- Ensure outline color passes contrast (it does: 8.49:1)
- Test on different browsers (Chrome, Safari, Firefox)

### Components don't render
- Verify Jinja2 template path matches include statement
- Check that CSS variables are loaded (link to `theme.css`)
- Inspect browser console for template errors

### Tailwind utilities not working
- Ensure `tailwind.config.js` content paths are correct
- Re-run build: `npm run build`
- Clear node_modules and reinstall: `rm -rf node_modules && npm install`

---

## Production Checklist

Before deploying:

- [ ] All CSS files minified (Tailwind handles this automatically)
- [ ] Components tested in real browser (Chrome, Safari, Firefox)
- [ ] Accessibility audit passed (run screen reader on key pages)
- [ ] Dark mode toggle works (if supporting light mode)
- [ ] Images have alt text
- [ ] Form validation works end-to-end
- [ ] Mobile responsive (test on iPhone, Android)
- [ ] Performance: Lighthouse score > 90
- [ ] No console errors or warnings

---

## Support

All components are production-ready and follow WebStaffr standards:
- Tenant-scoped (support multi-tenant deployments)
- No hardcoded content (no placeholder reviews/ratings)
- Semantic HTML (accessible to screen readers)
- Configurable via props (no edit-the-template solutions)

For questions, refer to the `accessibility_report.txt` for WCAG AA validation details.

---

**Design System Version:** 1.0  
**Last Updated:** 2026-08-02  
**Next Review:** 2026-09-02
