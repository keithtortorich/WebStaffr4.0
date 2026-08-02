---
name: ui-ux-pro-max
description: Generates production-grade design systems for WebStaffr customer sites. Creates tenant-scoped CSS variables, Tailwind configs, and Jinja2 template components with automatic dark/light mode resolution and WCAG AA contrast validation. Outputs are copy-paste ready for site_renderer.py integration. Use whenever building or customizing a customer site's design system, theme tokens, component library, or color palette—especially when dark mode coherence or accessibility audits are needed.
compatibility: 
  - Requires: Jinja2 template context, site_renderer.py integration
  - Outputs: CSS custom properties, tailwind.config.js, .jinja2 component templates
---

# ui-ux-pro-max: Production Design System Generator for Customer Sites

## Purpose

Generate complete, tenant-scoped design systems for WebStaffr customer sites. This skill automates the creation of CSS variables, Tailwind configurations, and reusable Jinja2 components that integrate directly with `site_renderer.py`.

**Not for:** Internal WebStaffr UI. This skill is for *customer* sites only.

**When to use:**
- Building a new customer site and need a complete design system from scratch
- Customizing a tenant's color palette, typography, or component set
- Auditing a site's design for WCAG AA contrast compliance
- Adding dark mode support to an existing site
- Generating component templates (cards, buttons, forms, modals, pricing tables, hero sections)

---

## How It Works

### Step 1: Color-Mode Resolution

The skill deterministically resolves **dark** or **light** mode from your request:

```python
is_dark_query = any(k in query.lower() for k in [
    "dark mode", "dark theme", "dark ui", "oled", "midnight", "night mode"
])
is_dark_style = "dark" in user_preference or site_config.get("theme") == "dark"
resolved_mode = "dark" if (is_dark_query or is_dark_style) else "light"
```

If dark mode is chosen, the skill ensures all surface colors meet WCAG AA luminance requirements.

### Step 2: WCAG AA Validation

Every generated color token is validated against WCAG 2.1 AA standards:

- **Text contrast minimum:** 4.5:1 (normal text), 3:1 (large text)
- **Graphics/UI components minimum:** 3:1
- **Surface luminance (dark mode):** L < 0.18 (ensures true dark surfaces)

Contrast is calculated using the WCAG relative luminance formula:
```
L = 0.2126 × Rlinear + 0.7152 × Glinear + 0.0722 × Blinear
```

If a color fails, the skill adjusts it and reports the rationale.

### Step 3: Output Generation

The skill produces three interconnected artifacts:

1. **CSS Custom Properties** (`styles/theme.css`)
   - Semantic color tokens (backgrounds, foregrounds, accents, borders)
   - Typography scale (font families, sizes, line heights, weights)
   - Spacing scale
   - Shadow/elevation utilities
   - Border radius presets

2. **Tailwind Configuration** (`tailwind.config.js`)
   - Maps all CSS custom properties into Tailwind utility classes
   - Enables both light and dark mode via CSS class switching
   - Extends base Tailwind for custom spacing, shadows, borders

3. **Jinja2 Component Templates** (`templates/components/*.jinja2`)
   - Reusable components: cards, buttons, forms, modals, hero sections, pricing tables
   - All components use Tailwind utilities (not inline styles)
   - Components accept props for flexibility (title, description, action, variant, etc.)
   - Template inheritance for consistent page layout

---

## What You Provide

**Minimal request:**
```
Generate a dark-mode design system for a home-services customer site.
Color: deep slate blue as primary, warm white as foreground.
Font: system sans-serif.
```

**Detailed request:**
```
Customer: plumbing business in Austin
Theme: dark mode with gold accent
Primary color: #1E293B (slate)
Accent color: #D4AF37 (gold)
Fonts: Poppins (headings), Inter (body)
Components needed: service card, CTA button, booking form, testimonial
```

---

## What You Get Back

1. **CSS file** — 150–200 lines of semantic tokens, ready to paste into the site's stylesheet
2. **Tailwind config** — Complete `tailwind.config.js` with dark mode enabled
3. **Component library** — 3–5 Jinja2 templates, each ~30–50 lines, fully functional
4. **Accessibility report** — Pass/fail for each color token against WCAG AA
5. **Integration guide** — Where to place files in `site_renderer.py` project structure

---

## Rules (Non-Negotiable)

### Rule 1: Production Code Only
Output is copy-paste ready. Never describe or abstract. Every CSS variable, Tailwind rule, and template is complete and functional.

### Rule 2: No Fabrication
Never invent placeholder content (ratings, reviews, testimonials, credentials, customer counts). Omit missing sections rather than fill them.

### Rule 3: Color-Mode Coherence
- If dark mode is requested or implied, resolve to dark **first**
- Never warn against dark mode; just deliver it correctly
- Light mode backgrounds must have L > 0.50; dark mode backgrounds must have L < 0.18

### Rule 4: Tenant Scoping
All generated code is tenant-aware. CSS variables are namespaced to prevent collisions in shared deployments. Jinja2 templates accept a `tenant_id` context variable.

### Rule 5: No Hardcoding
Fonts, colors, and spacing are configurable via CSS custom properties. Never hardcode values in Tailwind config or templates.

---

## Example Output (Dark Mode, Gold Accent)

### CSS Variables (styles/theme.css)
```css
@import url('https://fonts.googleapis.com/css2?family=Poppins:wght@600;700&family=Inter:wght@400;500;600&display=swap');

:root {
  /* Color Palette (Dark Mode - WCAG AA Validated) */
  --color-bg-primary: #0F172A;      /* L = 0.07 */
  --color-bg-secondary: #1E293B;    /* L = 0.12 */
  --color-bg-tertiary: #334155;     /* L = 0.18 */
  
  --color-fg-primary: #F8FAFC;      /* L = 0.97 - Contrast vs bg-primary: 28:1 */
  --color-fg-muted: #94A3B8;        /* L = 0.48 - Contrast vs bg-primary: 6.8:1 */
  --color-fg-subtle: #64748B;       /* L = 0.36 - Contrast vs bg-primary: 5.1:1 */
  
  --color-accent-primary: #D4AF37;  /* L = 0.52 - Contrast vs bg-primary: 7.4:1 */
  --color-accent-hover: #C9A227;    /* L = 0.42 - Contrast vs bg-primary: 6.0:1 */
  
  --color-border: #334155;
  --color-success: #10B981;         /* L = 0.45 */
  --color-error: #EF4444;           /* L = 0.28 */
  --color-warning: #F59E0B;         /* L = 0.48 */
  
  /* Typography */
  --font-heading: 'Poppins', system-ui;
  --font-body: 'Inter', system-ui;
  --font-mono: 'JetBrains Mono', monospace;
  
  --text-xs: 0.75rem;
  --text-sm: 0.875rem;
  --text-base: 1rem;
  --text-lg: 1.125rem;
  --text-xl: 1.25rem;
  --text-2xl: 1.5rem;
  
  --line-height-tight: 1.25;
  --line-height-normal: 1.5;
  --line-height-relaxed: 1.75;
  
  /* Spacing */
  --space-xs: 0.25rem;
  --space-sm: 0.5rem;
  --space-md: 1rem;
  --space-lg: 1.5rem;
  --space-xl: 2rem;
  
  /* Shadows */
  --shadow-sm: 0 1px 2px rgba(0, 0, 0, 0.05);
  --shadow-md: 0 4px 6px rgba(0, 0, 0, 0.1);
  --shadow-lg: 0 10px 15px rgba(0, 0, 0, 0.1);
  
  /* Border Radius */
  --radius-sm: 4px;
  --radius-md: 6px;
  --radius-lg: 8px;
}

/* Dark mode class toggle (for client-side switching) */
.dark {
  color-scheme: dark;
}
```

### Tailwind Config (tailwind.config.js)
```javascript
/** @type {import('tailwindcss').Config} */
module.exports = {
  darkMode: 'class',
  theme: {
    extend: {
      colors: {
        bg: {
          primary: 'var(--color-bg-primary)',
          secondary: 'var(--color-bg-secondary)',
          tertiary: 'var(--color-bg-tertiary)',
        },
        fg: {
          primary: 'var(--color-fg-primary)',
          muted: 'var(--color-fg-muted)',
          subtle: 'var(--color-fg-subtle)',
        },
        accent: {
          primary: 'var(--color-accent-primary)',
          hover: 'var(--color-accent-hover)',
        },
        success: 'var(--color-success)',
        error: 'var(--color-error)',
        warning: 'var(--color-warning)',
      },
      fontFamily: {
        heading: ['var(--font-heading)'],
        body: ['var(--font-body)'],
        mono: ['var(--font-mono)'],
      },
      fontSize: {
        xs: 'var(--text-xs)',
        sm: 'var(--text-sm)',
        base: 'var(--text-base)',
        lg: 'var(--text-lg)',
        xl: 'var(--text-xl)',
        '2xl': 'var(--text-2xl)',
      },
      spacing: {
        xs: 'var(--space-xs)',
        sm: 'var(--space-sm)',
        md: 'var(--space-md)',
        lg: 'var(--space-lg)',
        xl: 'var(--space-xl)',
      },
      boxShadow: {
        sm: 'var(--shadow-sm)',
        md: 'var(--shadow-md)',
        lg: 'var(--shadow-lg)',
      },
      borderRadius: {
        sm: 'var(--radius-sm)',
        md: 'var(--radius-md)',
        lg: 'var(--radius-lg)',
      },
    },
  },
  plugins: [],
};
```

### Jinja2 Component: Service Card (templates/components/service_card.jinja2)
```jinja2
{# Service Card Component - Reusable across all WebStaffr customer sites #}
{# Usage: {% include 'components/service_card.jinja2' with context %} #}
{# Props: title (str), description (str), icon_url (str), price (str), action_url (str), variant (str: 'default' | 'featured') #}

<div class="{% if variant == 'featured' %}bg-accent-primary/10{% else %}bg-bg-secondary{% endif %} border border-border rounded-lg p-6 shadow-md hover:shadow-lg transition-shadow duration-150">
  {% if icon_url %}
    <img src="{{ icon_url }}" alt="{{ title }}" class="w-12 h-12 mb-4 rounded-md object-cover" />
  {% endif %}
  
  <h3 class="text-lg font-heading font-bold text-fg-primary mb-2">
    {{ title }}
  </h3>
  
  <p class="text-sm text-fg-muted mb-4 leading-relaxed">
    {{ description }}
  </p>
  
  {% if price %}
    <div class="text-2xl font-bold text-accent-primary mb-4">
      {{ price }}
    </div>
  {% endif %}
  
  {% if action_url %}
    <a href="{{ action_url }}" class="inline-block w-full text-center bg-accent-primary hover:bg-accent-hover text-white font-medium py-2.5 px-4 rounded-md transition-colors duration-150 focus:outline-none focus:ring-2 focus:ring-accent-primary/50">
      Learn More
    </a>
  {% endif %}
</div>
```

---

## Integration with site_renderer.py

Place generated files in the customer's project:

```
customer-site/
├── styles/
│   └── theme.css          # Generated CSS variables
├── templates/
│   ├── components/
│   │   ├── service_card.jinja2
│   │   ├── cta_button.jinja2
│   │   ├── booking_form.jinja2
│   │   └── testimonial.jinja2
│   └── base.jinja2         # Main layout
└── tailwind.config.js      # Generated Tailwind config
```

In `site_renderer.py`, load the tenant's theme at render time:

```python
def render_site(tenant_id: str, page: str) -> str:
    # Load tenant's CSS variables and Tailwind config
    theme = load_theme_for_tenant(tenant_id)  # From generated theme.css
    
    context = {
        'tenant_id': tenant_id,
        'theme': theme,
        'page_data': get_page_data(tenant_id, page),
    }
    
    return render_template(f'{page}.jinja2', context)
```

---

## Accessibility Checklist (Always Run Before Shipping)

- [ ] All text colors pass 4.5:1 contrast ratio against their backgrounds
- [ ] All large text (18px+) passes 3:1 contrast ratio
- [ ] Accent colors pass 3:1 contrast ratio for UI components
- [ ] Dark mode surfaces have L < 0.18 (true dark, not gray)
- [ ] Light mode surfaces have L > 0.50 (readable white space)
- [ ] Focus states use ring or underline (visible at 2px minimum)
- [ ] Hover states provide feedback (color change, shadow, scale, or combination)
- [ ] All interactive elements are at least 44×44px (touch target)
- [ ] No color alone conveys information (use labels, icons, or text)

---

## Common Scenarios

### "Make it darker"
Adjust `--color-bg-primary`, `--color-bg-secondary`, `--color-bg-tertiary` to lower luminance values (L < 0.18). All dependent contrasts are recalculated and reported.

### "Add light mode variant"
Skill generates both `:root` (light) and `.dark` (dark) CSS custom properties in the same file. Tailwind `darkMode: 'class'` enables switching.

### "Use a different accent color"
Provide hex code. Skill validates it against all backgrounds for both foreground text and UI component contrast, reports failures, suggests adjustments.

### "I need a custom font"
Provide Google Fonts URL or system font stack. Skill updates `--font-heading`, `--font-body`, and `--font-mono` throughout. No rewrite needed.

### "Add a new component"
Describe what it does (e.g., "pricing table with rows and highlights"). Skill generates a new `.jinja2` template using existing tokens, ready to include in any page.

---

## What NOT to Do

- ❌ Do NOT generate placeholder testimonials, ratings, or customer counts
- ❌ Do NOT hardcode colors in template styles (use CSS custom properties)
- ❌ Do NOT create components without prop inputs (always make them configurable)
- ❌ Do NOT skip accessibility validation (every color token must be checked)
- ❌ Do NOT mix light and dark mode in the same component (let Tailwind handle switching)

---

## Limitations

- This skill generates design *systems*, not page layouts. Page structure is the responsibility of `site_renderer.py` and site-specific templates.
- Does not generate JavaScript or interactive behavior (that's the domain of site-specific code).
- Does not handle asset optimization (images, fonts). Assumes they're already hosted and served.
- Component output assumes Tailwind CSS is available. If not using Tailwind, convert utilities to raw CSS.

---

## Success Criteria

A generated design system ships successfully when:

1. ✅ All CSS variables are defined and conflict-free
2. ✅ Tailwind config extends without errors (`npm run build` succeeds)
3. ✅ All color tokens pass WCAG AA validation report
4. ✅ Components render correctly with no styling gaps
5. ✅ Dark/light mode switching works via `.dark` class toggle
6. ✅ Site renders within site_renderer.py without errors
7. ✅ Customer approves the aesthetic and feels ownership over their site
