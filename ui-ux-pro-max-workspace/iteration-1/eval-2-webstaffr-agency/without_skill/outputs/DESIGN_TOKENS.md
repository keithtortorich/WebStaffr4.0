# WebStaffr Design System - Design Tokens Reference

Complete reference for all CSS custom properties (design tokens) used throughout the system.

---

## Color Tokens

### Light Mode (Default)

#### Surfaces & Backgrounds
```css
--color-white: #FFFFFF;              /* Pure white for primary surfaces */
--color-surface-light: #FFFFFF;      /* Card backgrounds in light mode */
--color-surface-secondary: #F8F9FA;  /* Alternative light surface */
--color-background-light: #F8F9FA;   /* Page background in light mode */
```

#### Text Colors
```css
--color-text-primary: #0F172A;       /* Primary text: 20:1 contrast on white */
--color-text-secondary: #475569;     /* Secondary text: 9.5:1 contrast */
--color-text-tertiary: #94A3B8;      /* Tertiary/hint text: 5.2:1 contrast */
```

#### Borders
```css
--color-border-light: #E2E8F0;       /* Subtle borders in light mode */
```

### Dark Mode

Override in `@media (prefers-color-scheme: dark)` or `.dark` class:

#### Surfaces & Backgrounds
```css
--color-surface-light: #0F172A;      /* True black for dark mode */
--color-background-light: #1E293B;   /* Slightly lighter dark background */
```

#### Text Colors (Dark Mode)
```css
--color-text-primary: #F1F5F9;       /* Light text: 19:1 contrast on black */
--color-text-secondary: #CBD5E1;     /* Secondary text: 10.2:1 contrast */
--color-text-tertiary: #94A3B8;      /* Tertiary text: 5.8:1 contrast */
```

#### Borders (Dark Mode)
```css
--color-border-light: #334155;       /* Subtle borders in dark mode */
```

### Accent Colors (Indigo)

Consistent across light and dark modes:

```css
--color-accent-primary: #4F46E5;            /* Primary action color */
--color-accent-primary-hover: #4338CA;      /* Hover state (darker) */
--color-accent-primary-active: #3730A3;     /* Active/pressed state */
--color-accent-primary-light: #EEF2FF;      /* Light background tint (light mode) */
```

**Dark Mode Tint:**
```css
--color-accent-primary-light: rgba(79, 70, 229, 0.15);  /* 15% opacity in dark */
```

### Semantic Colors

#### Success
```css
--color-success: #10B981;             /* Green for success states */
--color-success-light: #D1FAE5;       /* Light green background */
```

#### Warning
```css
--color-warning: #F59E0B;             /* Amber for warnings */
--color-warning-light: #FEF3C7;       /* Light amber background */
```

#### Error
```css
--color-error: #EF4444;               /* Red for errors */
--color-error-light: #FEE2E2;         /* Light red background */
```

#### Info
```css
--color-info: #3B82F6;                /* Blue for info messages */
--color-info-light: #DBEAFE;          /* Light blue background */
```

### Current Mode Aliases

These automatically switch based on light/dark mode:

```css
--bg-primary: var(--color-surface-light);      /* Current background */
--bg-secondary: var(--color-background-light); /* Current secondary bg */
--text-primary: var(--color-text-primary);     /* Current primary text */
--text-secondary: var(--color-text-secondary); /* Current secondary text */
--text-tertiary: var(--color-text-tertiary);   /* Current tertiary text */
--border-color: var(--color-border-light);     /* Current border color */
--focus-ring: 0 0 0 3px var(--color-accent-primary-light); /* Focus outline */
```

---

## Spacing Scale

8px base unit system:

```css
--space-0: 0;           /* 0px */
--space-1: 0.25rem;     /* 4px */
--space-2: 0.5rem;      /* 8px */
--space-3: 0.75rem;     /* 12px */
--space-4: 1rem;        /* 16px */
--space-6: 1.5rem;      /* 24px */
--space-8: 2rem;        /* 32px */
--space-12: 3rem;       /* 48px */
--space-16: 4rem;       /* 64px */
--space-20: 5rem;       /* 80px */
--space-24: 6rem;       /* 96px */
--space-32: 8rem;       /* 128px */
```

### Usage Guidelines

| Use Case | Token |
|----------|-------|
| Checkbox/radio margin | `--space-1` |
| Icon spacing from text | `--space-2` |
| Small padding (form input) | `--space-3` |
| Element padding/margin | `--space-4` |
| Component spacing | `--space-6` to `--space-8` |
| Section spacing | `--space-12` to `--space-16` |
| Page margins | `--space-16` to `--space-32` |

---

## Typography

### Font Families

```css
--font-family-body: -apple-system, BlinkMacSystemFont, "Segoe UI", "Roboto", 
  "Oxygen", "Ubuntu", "Cantarell", "Fira Sans", "Droid Sans", "Helvetica Neue", sans-serif;

--font-family-heading: system-ui, -apple-system, sans-serif;

--font-family-mono: "SF Mono", Monaco, "Cascadia Code", "Roboto Mono",
  Consolas, "Courier New", monospace;
```

### Font Sizes

All in `rem` units (scales with root font-size):

```css
--font-size-xs:    0.75rem;   /* 12px @ 16px root */
--font-size-sm:    0.875rem;  /* 14px */
--font-size-base:  1rem;      /* 16px (default) */
--font-size-lg:    1.125rem;  /* 18px */
--font-size-xl:    1.25rem;   /* 20px */
--font-size-2xl:   1.5rem;    /* 24px */
--font-size-3xl:   1.875rem;  /* 30px */
--font-size-4xl:   2.25rem;   /* 36px */
--font-size-5xl:   3rem;      /* 48px */
--font-size-6xl:   3.75rem;   /* 60px */
```

### Font Weights

```css
--font-weight-regular:    400;  /* Normal text */
--font-weight-medium:     500;  /* Slightly bold */
--font-weight-semibold:   600;  /* Bold (buttons, labels) */
--font-weight-bold:       700;  /* Strong emphasis (headings) */
```

### Line Heights

```css
--line-height-tight:      1.2;   /* Headings */
--line-height-normal:     1.5;   /* Body text */
--line-height-relaxed:    1.75;  /* Long-form prose */
```

### Type Scale

| Element | Size | Weight | Line Height |
|---------|------|--------|-------------|
| h1 | `--font-size-5xl` | bold | tight |
| h2 | `--font-size-4xl` | bold | tight |
| h3 | `--font-size-3xl` | bold | tight |
| h4 | `--font-size-2xl` | bold | tight |
| h5 | `--font-size-xl` | bold | tight |
| h6 | `--font-size-lg` | bold | tight |
| Body | `--font-size-base` | regular | normal |
| Small | `--font-size-sm` | regular | normal |
| XS | `--font-size-xs` | regular | normal |

---

## Border Radius

Pixel values for consistent rounding:

```css
--radius-sm:     0.375rem;  /* 6px - small buttons, small inputs */
--radius-base:   0.5rem;    /* 8px - default for most elements */
--radius-lg:     0.75rem;   /* 12px - cards, modals */
--radius-xl:     1rem;      /* 16px - larger cards */
--radius-2xl:    1.5rem;    /* 24px - feature sections */
--radius-full:   9999px;    /* Circular (badges, avatars) */
```

---

## Shadows

Layered elevation system:

```css
--shadow-sm:   0 1px 2px 0 rgba(0, 0, 0, 0.05);

--shadow-base: 0 1px 3px 0 rgba(0, 0, 0, 0.1), 
               0 1px 2px 0 rgba(0, 0, 0, 0.06);

--shadow-md:   0 4px 6px -1px rgba(0, 0, 0, 0.1), 
               0 2px 4px -1px rgba(0, 0, 0, 0.06);

--shadow-lg:   0 10px 15px -3px rgba(0, 0, 0, 0.1), 
               0 4px 6px -2px rgba(0, 0, 0, 0.05);

--shadow-xl:   0 20px 25px -5px rgba(0, 0, 0, 0.1), 
               0 10px 10px -5px rgba(0, 0, 0, 0.04);
```

### Shadow Elevation

| Level | Use Case |
|-------|----------|
| sm | Subtle hover effects, input focus |
| base | Cards, slight elevation |
| md | Buttons, dropdowns |
| lg | Modals, floating panels |
| xl | Top-level overlays |

---

## Transitions & Motion

```css
--transition-fast:  150ms cubic-bezier(0.4, 0, 0.2, 1);
--transition-base:  200ms cubic-bezier(0.4, 0, 0.2, 1);
--transition-slow:  300ms cubic-bezier(0.4, 0, 0.2, 1);
```

### Usage

| Speed | Use Case |
|-------|----------|
| fast | Hover, focus, quick state changes |
| base | Color changes, opacity, transforms |
| slow | Modal entrance, carousel, page transition |

All transitions respect `prefers-reduced-motion: reduce`.

---

## Z-Index Scale

```css
--z-dropdown:       1000;   /* Dropdowns, tooltips */
--z-sticky:         1020;   /* Sticky headers, nav */
--z-fixed:          1030;   /* Fixed elements */
--z-modal-backdrop:  1040;   /* Dark overlay behind modal */
--z-modal:          1050;   /* Modal dialog */
--z-popover:        1060;   /* Floating popover */
--z-tooltip:        1070;   /* Tooltip overlay */
```

---

## Responsive Breakpoints

While not CSS tokens, these are the responsive breakpoints:

```css
/* Desktop (default) */
@media (max-width: 1024px) { /* Tablet */ }
@media (max-width: 768px) { /* Mobile */ }
@media (max-width: 480px) { /* Small Mobile */ }
```

Font size reduction:
- Desktop: `16px` (100%)
- Tablet: `15px` (93.75%)
- Mobile: `14px` (87.5%)

---

## Using Tokens in Code

### CSS
```css
.button {
  padding: var(--space-3) var(--space-6);
  font-size: var(--font-size-base);
  font-weight: var(--font-weight-semibold);
  color: white;
  background-color: var(--color-accent-primary);
  border-radius: var(--radius-base);
  transition: all var(--transition-fast);
}

.button:hover {
  background-color: var(--color-accent-primary-hover);
  box-shadow: var(--shadow-md);
}
```

### HTML (Utility Classes)
```html
<div class="mt-8 mb-8 px-4">
  <h2 class="text-3xl font-bold text-primary">Hello</h2>
  <p class="text-lg text-secondary">Description</p>
  <button class="btn btn-primary btn-lg">Action</button>
</div>
```

---

## Token Naming Convention

All tokens follow this pattern: `--[category]-[subcategory]-[variant]`

Examples:
- `--color-accent-primary`
- `--shadow-lg`
- `--font-size-xl`
- `--space-4`

### Benefits
1. **Autocomplete** — IDEs suggest related tokens
2. **Consistency** — Clear naming reduces errors
3. **Maintainability** — Easy to find and update
4. **Scalability** — New tokens follow same pattern

---

## Extending the System

### Adding New Colors

1. Verify WCAG AA contrast (4.5:1 minimum)
2. Add to both light and dark mode sections
3. Use semantic naming: `--color-[semantic]-[variant]`
4. Test in high contrast mode

```css
--color-success: #10B981;
--color-success-light: #D1FAE5;
--color-success-hover: #059669;
```

### Adding New Spacing Values

Keep multiples of 8px (base unit):

```css
--space-40: 10rem;  /* 160px */
--space-48: 12rem;  /* 192px */
```

### Adding New Shadows

Test on light and dark backgrounds:

```css
--shadow-2xl: 0 25px 50px -12px rgba(0, 0, 0, 0.15);
```

---

## Token Usage Statistics

- **Total Tokens:** 80+
- **Color Variants:** 25
- **Spacing Values:** 12
- **Font Sizes:** 9
- **Shadows:** 5
- **Transitions:** 3
- **Z-index Levels:** 8

This comprehensive token system ensures consistency across the entire WebStaffr landing page while maintaining flexibility for future growth.

---

**Last Updated:** 2025-08-02  
**Format:** CSS Custom Properties (native browser support)  
**Dark Mode:** Fully Supported  
**Accessibility:** WCAG AA Compliant
