# Plumbing Dark Mode Design System — Component Usage Guide

## Quick Reference

### Color Variables
```css
/* Primary */
--color-slate-primary: #1E293B;     /* Cards, sections */
--color-gold-primary: #D4AF37;      /* Buttons, accents, focus */
--color-white: #FFFFFF;             /* Primary text */

/* Background */
--color-gray-900: #0F172A;          /* Dark backgrounds */
--color-slate-light: #334155;       /* Hover states */

/* Semantic */
--color-error: #EF4444;             /* Errors */
--color-success: #10B981;           /* Success states */
--color-warning: #F59E0B;           /* Warnings */
--color-info: #3B82F6;              /* Information */
```

---

## Button Component

### Basic Button
```html
<button class="btn btn-primary">Schedule Service</button>
```

### Button Variants

**Primary (Call-to-Action)**
```html
<button class="btn btn-primary">Book Now</button>
```
- **Use**: Main actions like "Schedule Service", "Call Now"
- **Background**: Gold (#D4AF37)
- **Text**: Dark gray (#0F172A)
- **Contrast**: 10.5:1 (AAA)

**Secondary (Alternative)**
```html
<button class="btn btn-secondary">Learn More</button>
```
- **Use**: Secondary actions like "Learn More", "View Details"
- **Background**: Transparent with gold border
- **Text**: Gold (#D4AF37)
- **Contrast**: 10.5:1 (AAA)

**Tertiary (Text Link)**
```html
<button class="btn btn-tertiary">View Details</button>
```
- **Use**: Minimal emphasis actions
- **Background**: Transparent
- **Text**: Gold (#D4AF37)
- **Contrast**: 10.5:1 (AAA)

### Button Sizes

**Small**
```html
<button class="btn btn-primary btn-sm">Small Button</button>
```
- Padding: 0.5rem 1rem
- Font: 0.875rem

**Default (Medium)**
```html
<button class="btn btn-primary">Default Button</button>
```
- Padding: 1rem 1.5rem
- Font: 1rem

**Large**
```html
<button class="btn btn-primary btn-lg">Large Button</button>
```
- Padding: 1.5rem 2rem
- Font: 1.125rem

### Full Width
```html
<button class="btn btn-primary btn-block">Book an Appointment</button>
```
- Width: 100% of container
- Useful for mobile, forms, and CTAs

### States

**Hover**
```css
.btn-primary:hover {
  background-color: #E8C547;        /* Lighter gold */
  transform: translateY(-2px);      /* Slight lift */
  box-shadow: var(--shadow-lg);     /* Enhanced shadow */
}
```

**Active/Pressed**
```css
.btn-primary:active {
  transform: translateY(0);         /* Return to baseline */
  box-shadow: var(--shadow-md);     /* Lighter shadow */
}
```

**Disabled**
```html
<button class="btn btn-primary" disabled>Disabled</button>
```
- Opacity: 0.5
- Cursor: not-allowed

**Focus (Keyboard)**
- Outline: 2px solid #D4AF37
- Outline offset: 2px
- Works on all variants

### Accessibility
- ✓ Semantic `<button>` element
- ✓ Supports Tab/Space/Enter keys
- ✓ Clear focus indicator
- ✓ Disabled state programmatic
- ✓ No color-only indication
- ✓ Minimum 44×44px touch target

---

## Service Card Component

### Basic Service Card
```html
<article class="service-card">
  <div class="service-card-icon">🚰</div>
  <h3 class="service-card-title">Emergency Repairs</h3>
  <p class="service-card-description">Available 24/7 for urgent plumbing issues.</p>
  <ul class="service-card-features">
    <li>Same-day service</li>
    <li>Certified technicians</li>
  </ul>
  <div class="service-card-cta">
    <button class="btn btn-primary btn-block">Call Now</button>
  </div>
</article>
```

### Structure
1. **Icon** (3rem × 3rem)
   - Emoji or SVG icon
   - Light gold background
   - Centered and padded

2. **Title** (h3, 1.25rem)
   - Bold, white text
   - Service name
   - Short and clear

3. **Description** (0.875–1rem)
   - 2–3 sentences
   - Light gray text (#CBD5E1)
   - Clear line height (1.75)

4. **Features** (list)
   - Checkmarks (✓) in gold
   - 3–5 key features
   - Small text, easy scanning

5. **CTA Button** (full width)
   - Primary button variant
   - Action-oriented label
   - Pressed to bottom of card

### Styling
- **Background**: Slate blue (#1E293B)
- **Border**: 1px solid darker slate
- **Padding**: 2rem
- **Border Radius**: 0.75rem

### States

**Default**
```css
.service-card {
  background-color: #1E293B;
  border: 1px solid #475569;
}
```

**Hover**
```css
.service-card:hover {
  border-color: #D4AF37;            /* Gold border */
  box-shadow: 0 0 0 1px #D4AF37, var(--shadow-xl);
  transform: translateY(-4px);      /* Lift slightly */
}
```

**Focus (Card Button)**
```css
.service-card:focus-within {
  border-color: #D4AF37;
  outline: 2px solid #D4AF37;
  outline-offset: 2px;
}
```

### Grid Layout

**3-Column (Desktop)**
```html
<div class="grid grid-cols-3">
  <article class="service-card">...</article>
  <article class="service-card">...</article>
  <article class="service-card">...</article>
</div>
```

**2-Column (Tablet)**
```html
<div class="grid grid-cols-2">
  <!-- Cards responsive to 2 columns -->
</div>
```

**1-Column (Mobile)**
Auto-responsive via CSS media queries

### Accessibility
- ✓ Semantic `<article>` tag
- ✓ Heading hierarchy (h3)
- ✓ Focusable via card button
- ✓ Checkmarks included in text
- ✓ Card-level focus-within state
- ✓ Hover/focus indication not color-only

---

## Form Component

### Basic Form Group
```html
<div class="form-group">
  <label for="name" class="form-label required">Name</label>
  <input type="text" id="name" class="form-input" placeholder="Enter your name" required>
  <span class="form-hint">Your full name</span>
</div>
```

### Form Inputs

**Text Input**
```html
<input type="text" class="form-input" placeholder="Enter text">
```

**Email Input**
```html
<input type="email" class="form-input" placeholder="your@email.com" required>
```

**Telephone Input**
```html
<input type="tel" class="form-input" placeholder="(555) 000-0000">
```

**Date Input**
```html
<input type="date" class="form-input" required>
```

**Textarea**
```html
<textarea class="form-textarea" placeholder="Describe your issue..."></textarea>
```
- Min height: 120px
- Resizable vertically only

**Select Dropdown**
```html
<select class="form-select" required>
  <option value="">Select an option...</option>
  <option value="option1">Option 1</option>
  <option value="option2">Option 2</option>
</select>
```
- Custom gold chevron indicator
- Clear focus state

### Label & Required Indicator

```html
<label for="email" class="form-label required">Email</label>
<input type="email" id="email" class="form-input" required>
```

The `.required` class adds a red asterisk (*) via CSS `::after`.

**Styling**
- Color: White (#FFFFFF)
- Font weight: Semibold (600)
- Font size: 1rem
- Margin bottom: 0.5rem

### Focus & Validation

**Normal Focus**
```css
.form-input:focus {
  outline: none;
  border-color: #D4AF37;            /* Gold border */
  box-shadow: 0 0 0 3px rgba(212, 175, 55, 0.1);
}
```

**Error State**
```html
<div class="form-field has-error">
  <label for="email" class="form-label">Email</label>
  <input type="email" id="email" class="form-input" aria-invalid="true" aria-describedby="email-error">
  <div id="email-error" class="form-error" role="alert">
    Please enter a valid email
  </div>
</div>
```

**Error Styling**
```css
.form-field.has-error .form-input {
  border-color: #EF4444;            /* Red */
}

.form-field.has-error .form-input:focus {
  box-shadow: 0 0 0 3px rgba(239, 68, 68, 0.1);
}
```

### Checkboxes & Radio Buttons

**Checkbox**
```html
<div class="form-group">
  <label class="checkbox-label">
    <input type="checkbox" class="form-checkbox" checked>
    <span>I agree to the terms and conditions</span>
  </label>
</div>
```

**Radio Button**
```html
<div class="form-group">
  <label class="radio-label">
    <input type="radio" class="form-radio" name="service" value="repair">
    <span>Emergency Repair</span>
  </label>
</div>
```

**Styling**
- Accent color: Gold (#D4AF37)
- Native browser styling
- Clear focus rings
- Flexbox alignment for label+input

### Help Text & Hints

```html
<input class="form-input" aria-describedby="email-hint">
<span id="email-hint" class="form-hint">We'll never share your email</span>
```

**Styling**
- Color: Gray-400 (#94A3B8)
- Font size: 0.875rem
- Margin top: 0.5rem

### Disabled State

```html
<input class="form-input" disabled>
```

**Styling**
- Background: Darker gray (#1E293B)
- Opacity: 0.6
- Cursor: not-allowed

### Booking Form (Multi-Section)

```html
<form class="booking-form">
  <div class="booking-form-section">
    <h3>Your Information</h3>
    <div class="form-row">
      <div class="form-group">
        <label class="form-label required">First Name</label>
        <input type="text" class="form-input" required>
      </div>
      <div class="form-group">
        <label class="form-label required">Last Name</label>
        <input type="text" class="form-input" required>
      </div>
    </div>
  </div>

  <div class="booking-form-section">
    <h3>Service Request</h3>
    <div class="form-row full">
      <div class="form-group">
        <label class="form-label required">Service Type</label>
        <select class="form-select" required>
          <option value="">Select...</option>
        </select>
      </div>
    </div>
  </div>

  <button type="submit" class="btn btn-primary btn-block btn-lg">
    Request Service
  </button>
</form>
```

**Layout Classes**
- `.form-row`: 2 columns
- `.form-row.full`: 1 column
- `.booking-form`: Max width 600px, centered

### Accessibility
- ✓ Labels associated with `for` attribute
- ✓ Required fields marked programmatically
- ✓ Error messages use `role="alert"`
- ✓ Field descriptions via `aria-describedby`
- ✓ Clear focus indicators
- ✓ Placeholder text never replaces labels
- ✓ Native input types for better mobile UX

---

## Testimonial Component

### Basic Testimonial
```html
<article class="testimonial">
  <div class="testimonial-quote">
    "Fast and professional service. Fixed our issue in 2 hours!"
  </div>
  <div class="testimonial-author">
    <div class="testimonial-avatar">SR</div>
    <div>
      <span class="testimonial-name">Sarah Rodriguez</span>
      <span class="testimonial-title">Homeowner, San Diego</span>
      <div class="testimonial-rating" aria-label="5 out of 5 stars">★★★★★</div>
    </div>
  </div>
</article>
```

### Structure
1. **Quote** (italic, larger font)
   - Opening quotation mark (decorative)
   - Main testimonial text
   - Light color

2. **Author Section** (flex layout)
   - **Avatar**: Gradient circle with initials
   - **Name**: Bold white text
   - **Title**: Muted gray
   - **Rating**: Gold stars

### Styling

**Quote Container**
```css
.testimonial {
  background-color: #1E293B;        /* Slate */
  border-left: 4px solid #D4AF37;   /* Gold accent */
  border-radius: 0.5rem;
  padding: 2rem;
  margin-bottom: 2rem;
}
```

**Quote Text**
```css
.testimonial-quote {
  font-size: 1.125rem;
  font-style: italic;
  color: #F1F5F9;                   /* Light gray */
  line-height: 1.75;
  margin-bottom: 1.5rem;
  position: relative;
}

.testimonial-quote::before {
  content: '"';
  font-size: 2.5rem;
  color: #D4AF37;
  opacity: 0.3;
}
```

**Avatar**
```css
.testimonial-avatar {
  width: 3rem;
  height: 3rem;
  border-radius: 50%;
  background: linear-gradient(135deg, #D4AF37, #B8941E);
  display: flex;
  align-items: center;
  justify-content: center;
  color: #0F172A;
  font-weight: bold;
}
```

**Author Info**
```css
.testimonial-name {
  font-weight: 600;
  color: #FFFFFF;
  display: block;
}

.testimonial-title {
  font-size: 0.875rem;
  color: #94A3B8;                   /* Muted gray */
  display: block;
}
```

### Grid Layout

**Multiple Testimonials**
```html
<div class="grid grid-cols-3">
  <article class="testimonial">...</article>
  <article class="testimonial">...</article>
  <article class="testimonial">...</article>
</div>
```

Responsive to 1 column on mobile, 2 on tablet, 3 on desktop.

### Accessibility
- ✓ Semantic `<article>` tag
- ✓ Star rating has `aria-label`
- ✓ Avatar text (initials) conveyed semantically
- ✓ Quote text in color + style (not color-only)
- ✓ High contrast quote text (11.2:1)
- ✓ Clear author attribution

---

## Utility Classes

### Spacing
```html
<div class="mb-lg">Margin bottom large</div>
<div class="p-xl">Padding extra large</div>
```

### Grid
```html
<div class="grid grid-cols-3">
  <div>Column 1</div>
  <div>Column 2</div>
  <div>Column 3</div>
</div>
```

### Flexbox
```html
<div class="flex items-center justify-between gap-lg">
  <div>Left</div>
  <div>Right</div>
</div>
```

### Text
```html
<p class="text-white text-lg font-bold">Bold white heading</p>
<p class="text-gold">Accent text</p>
<p class="text-muted">Muted/secondary text</p>
```

### Screen Reader Only
```html
<span class="sr-only">Additional context for screen readers</span>
```

---

## Responsive Design

### Breakpoints
- **Desktop**: 1200px max width
- **Tablet**: 768px breakpoint
- **Mobile**: 480px breakpoint

### Auto-Responsive Components
- Service card grid: 3 → 2 → 1 column
- Form rows: 2 column → 1 column on mobile
- Button sizes: Reduce padding on mobile
- Font sizes: Scale down on small screens

---

## Color Usage Guidelines

### When to Use Each Color

| Color | Usage | Examples |
|-------|-------|----------|
| Slate (#1E293B) | Cards, panels, sections | Service cards, form containers |
| Gold (#D4AF37) | Buttons, links, accents | CTAs, focus states, highlights |
| White (#FFF) | Primary text, headings | Body copy, labels |
| Light Gray (#E2E8F0) | Secondary text | Descriptions, hints |
| Dark Gray (#475569) | Tertiary text, borders | Dividers, subtle text |
| Green (#10B981) | Success states | Confirmation messages |
| Red (#EF4444) | Error states | Error messages, validation |
| Gold Light (#E8C547) | Hover states, lighter gold | Button hover, focus |

---

## Do's and Don'ts

### ✓ DO
- Use semantic HTML (`<button>`, `<form>`, `<label>`)
- Combine color with other indicators (icons, text)
- Test keyboard navigation
- Provide clear focus indicators
- Use proper heading hierarchy
- Associate labels with inputs

### ✗ DON'T
- Use `<div>` styled as buttons
- Rely on color alone for meaning
- Nest buttons inside links or vice versa
- Use placeholder text instead of labels
- Skip heading levels (h1 → h3)
- Add auto-playing animations or sound

---

**Last Updated**: 2024
**Version**: 1.0
