# WebStaffr Design System - Component Library

Complete documentation of all production-ready components with usage examples.

---

## Table of Contents

1. [Buttons](#buttons)
2. [Cards](#cards)
3. [Forms](#forms)
4. [Hero Section](#hero-section)
5. [Feature Grid](#feature-grid)
6. [Pricing Table](#pricing-table)
7. [Testimonial Carousel](#testimonial-carousel)
8. [Booking Widget](#booking-widget)
9. [Navigation](#navigation)
10. [Utility Classes](#utility-classes)

---

## Buttons

### Primary Button

The main action button. Use for primary CTAs.

```html
<button class="btn btn-primary">Get Started</button>
<button class="btn btn-primary btn-sm">Small</button>
<button class="btn btn-primary btn-lg">Large</button>
<button class="btn btn-primary" disabled>Disabled</button>
```

**Styles:**
- Background: `--color-accent-primary` (#4F46E5)
- Text: White
- Hover: Darker indigo with shadow lift
- Active: Deepest indigo
- Disabled: 50% opacity, no pointer events

**States:**
- ✓ Default
- ✓ Hover (lift + shadow)
- ✓ Active (darker)
- ✓ Focus (ring)
- ✓ Disabled
- ✓ Loading

### Secondary Button

Outline button for secondary actions.

```html
<button class="btn btn-secondary">Learn More</button>
<button class="btn btn-secondary btn-sm">Small</button>
<button class="btn btn-secondary btn-lg">Large</button>
```

**Styles:**
- Background: Transparent
- Border: 2px solid accent
- Text: Accent color
- Hover: Light accent background

### Ghost Button

Minimal button for tertiary actions.

```html
<button class="btn btn-ghost">Skip</button>
```

**Styles:**
- Background: Transparent
- Border: None
- Text: Accent color
- Hover: Light accent background

### Button Sizes

```css
.btn-sm       /* 14px, small padding */
.btn          /* 16px, default (standard) */
.btn-lg       /* 18px, large padding */
```

### Button with Icon

```html
<button class="btn btn-primary">
  <span>📱</span>
  Download App
</button>
```

**Icon Guidelines:**
- Use Unicode emoji or SVG icons
- Maintain gap spacing with `gap: var(--space-2)`
- Icons should be 16–24px
- No icon-only buttons without `aria-label`

---

## Cards

### Basic Card

```html
<div class="card">
  <h3>Feature Title</h3>
  <p>Description of feature or content.</p>
</div>
```

**Styles:**
- Background: `--bg-primary`
- Border: 1px solid border color
- Padding: `var(--space-8)`
- Border-radius: `var(--radius-lg)`
- Shadow: `var(--shadow-sm)` → `var(--shadow-md)` on hover

### Card Variants

```html
<!-- Small padding -->
<div class="card card-sm">Content</div>

<!-- Large padding -->
<div class="card card-lg">Content</div>
```

**Responsive:** Cards stack on mobile, maintain grid on desktop.

---

## Forms

### Form Group

```html
<div class="form-group">
  <label for="email" class="form-label">
    Email <span class="required">*</span>
  </label>
  <input
    type="email"
    id="email"
    name="email"
    class="form-field"
    required
    aria-required="true"
    placeholder="you@example.com"
  />
</div>
```

**Accessibility:**
- ✓ Label associated with input via `for` attribute
- ✓ `aria-required="true"` on required fields
- ✓ Type-specific inputs (email, tel, date)
- ✓ Clear placeholder text

### Text Input

```html
<input
  type="text"
  class="form-field"
  placeholder="Full name"
/>
```

**Supported Types:**
- `text`
- `email`
- `tel`
- `url`
- `number`
- `date`
- `time`
- `password`

### Select Dropdown

```html
<select class="form-field" required>
  <option value="">Select an option</option>
  <option value="option1">Option 1</option>
  <option value="option2">Option 2</option>
</select>
```

### Textarea

```html
<textarea
  class="form-field"
  placeholder="Your message"
  rows="5"
></textarea>
```

**Default:** `min-height: 8rem`, `resize: vertical`

### Form Validation

```html
<div class="form-group invalid">
  <label for="email" class="form-label">Email</label>
  <input type="email" id="email" class="form-field" />
  <div role="alert" class="error-message">
    Please enter a valid email address.
  </div>
</div>
```

**Validation States:**
- `.invalid` — Add to `.form-group` on error
- `.valid` — Add to `.form-group` on success
- `role="alert"` — For error messages

---

## Hero Section

### Hero Layout

```html
<section class="hero">
  <div class="hero-content">
    <h1>Headline</h1>
    <p class="hero-subtitle">Subheadline or description</p>
    <div class="hero-cta">
      <button class="btn btn-primary btn-lg">Primary CTA</button>
      <button class="btn btn-secondary btn-lg">Secondary CTA</button>
    </div>
  </div>
</section>
```

**Features:**
- ✓ Full viewport height (90vh on desktop, 70vh tablet, 60vh mobile)
- ✓ Gradient background with radial accents
- ✓ Centered content with max-width constraint
- ✓ Responsive CTA buttons (row on desktop, column on mobile)

**Styling:**
- Background: Gradient + radial overlay
- Text alignment: Center
- Padding: `var(--space-8)` responsive
- Dark mode: Adjusted gradient opacity

---

## Feature Grid

### Feature Card Grid

```html
<div class="features">
  <div class="feature card card-sm">
    <div class="feature-icon">📞</div>
    <h3>Feature Name</h3>
    <p>Brief description of the feature or capability.</p>
  </div>
  <!-- Repeat for each feature -->
</div>
```

**Grid Layout:**
- Auto-fit: `minmax(300px, 1fr)` (3 columns on desktop)
- Tablet: 2 columns
- Mobile: 1 column
- Gap: `var(--space-8)` responsive

**Feature Icon:**
- Size: 48px × 48px
- Background: Light accent
- Icon color: Accent primary
- Border-radius: `var(--radius-lg)`

---

## Pricing Table

### Table Structure

```html
<table class="pricing-table">
  <thead>
    <tr>
      <th>Feature</th>
      <th>Starter</th>
      <th>Professional</th>
      <th class="highlight">Enterprise</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td>Live Voice Calls</td>
      <td class="text-center">100/mo</td>
      <td class="text-center">1,000/mo</td>
      <td class="highlight text-center">Unlimited</td>
    </tr>
    <tr>
      <td>Integrations</td>
      <td class="text-center">3</td>
      <td class="text-center">10+</td>
      <td class="highlight text-center">Custom</td>
    </tr>
    <tr>
      <td>Support</td>
      <td class="text-center">Email</td>
      <td class="text-center">Priority</td>
      <td class="highlight text-center">Dedicated</td>
    </tr>
  </tbody>
</table>
```

**Styles:**
- Header: Dark background, bold text
- Rows: 1px borders, hover highlight
- Highlight column: Light accent background
- Responsive: Font size reduces on mobile

**Accessibility:**
- ✓ Semantic `<thead>`, `<tbody>`, `<tfoot>`
- ✓ Use `scope="col"` on `<th>` elements
- ✓ Data cells associated with headers

---

## Testimonial Carousel

### Carousel Structure

```html
<div class="testimonial-carousel">
  <!-- Slide 1 (visible by default) -->
  <div class="testimonial-slide active">
    <p class="testimonial-quote">
      "Quote text goes here..."
    </p>
    <div class="testimonial-author">
      <div class="testimonial-avatar">JD</div>
      <div class="testimonial-info">
        <h4>John Doe</h4>
        <p>Title, Company</p>
      </div>
    </div>
  </div>

  <!-- Slide 2 -->
  <div class="testimonial-slide">
    <!-- Same structure -->
  </div>

  <!-- Controls -->
  <div class="carousel-controls">
    <button class="carousel-dot active" aria-current="true"></button>
    <button class="carousel-dot" aria-current="false"></button>
    <button class="carousel-dot" aria-current="false"></button>
  </div>
</div>
```

**JavaScript Initialization:**
```javascript
const carousel = new TestimonialCarousel('.testimonial-carousel');
```

**Features:**
- ✓ Auto-play (5-second intervals)
- ✓ Keyboard navigation (arrow keys)
- ✓ Pause on hover
- ✓ Clickable dot indicators
- ✓ Accessible (ARIA labels, screen reader friendly)

**Styles:**
- Background: Secondary color
- Quote: Italic, large text
- Avatar: 48px circular, accent background
- Dot size: 8px (24px when active)

---

## Booking Widget

### Booking Form

```html
<div class="booking-widget">
  <h3 class="booking-title">Book a Demo</h3>
  <form>
    <div class="form-group">
      <label for="name" class="form-label">
        Full Name <span class="required">*</span>
      </label>
      <input
        type="text"
        id="name"
        name="name"
        class="form-field"
        required
        aria-required="true"
      />
    </div>

    <div class="form-group">
      <label for="email" class="form-label">
        Email <span class="required">*</span>
      </label>
      <input
        type="email"
        id="email"
        name="email"
        class="form-field"
        required
        aria-required="true"
      />
    </div>

    <div class="form-group">
      <label for="message" class="form-label">Message</label>
      <textarea
        id="message"
        name="message"
        class="form-field"
      ></textarea>
    </div>

    <button type="submit" class="btn btn-primary booking-submit">
      Book Now
    </button>
  </form>
</div>
```

**JavaScript Initialization:**
```javascript
const booking = new BookingForm('.booking-widget form');
```

**Features:**
- ✓ Client-side validation
- ✓ Server-side validation required
- ✓ Clear error/success messages
- ✓ Loading state during submission
- ✓ Full width button on submit

**Responsive:**
- Desktop: Max-width 400px, centered
- Tablet: Max-width 100%
- Mobile: Full width, no side padding

---

## Navigation

### Header Navigation

```html
<header>
  <nav>
    <a href="#" class="logo">WebStaffr</a>

    <ul class="nav-links" data-menu>
      <li><a href="#features">Features</a></li>
      <li><a href="#pricing">Pricing</a></li>
      <li><a href="#testimonials">Testimonials</a></li>
      <li><a href="#booking">Book Demo</a></li>
    </ul>

    <button
      data-theme-toggle
      aria-label="Toggle dark mode"
    >
      🌙
    </button>

    <button
      data-menu-toggle
      aria-label="Toggle menu"
      aria-expanded="false"
    >
      ☰
    </button>
  </nav>
</header>
```

**JavaScript Initialization:**
```javascript
new ThemeToggle('[data-theme-toggle]');
new MobileMenu('[data-menu-toggle]', '[data-menu]');
new ScrollSpy('nav', 'section[id]');
```

**Features:**
- ✓ Sticky header
- ✓ Mobile hamburger menu
- ✓ Dark/light mode toggle
- ✓ Active link highlighting (ScrollSpy)
- ✓ Smooth scroll to sections

---

## Utility Classes

### Spacing

```html
<!-- Margin -->
<div class="mt-4 mb-8 mt-16">Content</div>

<!-- Padding -->
<div class="pt-8 pb-8 px-4 py-4">Content</div>
```

Available: `mt-4`, `mb-4`, `mt-8`, `mb-8`, `mt-16`, `mb-16`, `pt-8`, `pb-8`, `px-4`, `py-4`

### Text

```html
<!-- Alignment -->
<div class="text-center">Centered</div>
<div class="text-left">Left-aligned</div>
<div class="text-right">Right-aligned</div>

<!-- Color -->
<p class="text-primary">Primary text</p>
<p class="text-secondary">Secondary text</p>
<p class="text-tertiary">Tertiary text</p>
<p class="text-accent">Accent text</p>

<!-- Size -->
<p class="text-sm">Small (14px)</p>
<p class="text-base">Base (16px)</p>
<p class="text-lg">Large (18px)</p>
<p class="text-xl">XL (20px)</p>

<!-- Weight -->
<p class="font-normal">Regular (400)</p>
<p class="font-medium">Medium (500)</p>
<p class="font-semibold">Semibold (600)</p>
<p class="font-bold">Bold (700)</p>
```

### Display & Flexbox

```html
<!-- Flexbox -->
<div class="flex gap-4">Item 1</div>
<div class="flex flex-col gap-8">Column</div>
<div class="flex-center">Centered flex</div>

<!-- Grid -->
<div class="grid grid-cols-2 gap-4">
  <div>Column 1</div>
  <div>Column 2</div>
</div>

<div class="grid grid-cols-3">
  <div>1</div>
  <div>2</div>
  <div>3</div>
</div>

<!-- Display -->
<div class="hidden">Hidden</div>
<div class="block">Block</div>
<div class="inline-block">Inline block</div>
```

### Sections

```html
<section class="section">
  <div class="container">
    <div class="section-title">
      <h2>Section Title</h2>
      <p class="section-subtitle">Subtitle text</p>
    </div>

    <!-- Content -->
  </div>
</section>
```

**Responsive Containers:**
- Max-width: 1280px
- Padding: `var(--space-4)` (responsive)
- Centered with auto margins

---

## Best Practices

### Do's
- ✓ Use semantic HTML (`<button>`, `<a>`, `<form>`)
- ✓ Include proper ARIA labels
- ✓ Test components in light and dark modes
- ✓ Use CSS tokens instead of hardcoded values
- ✓ Maintain 4.5:1 contrast ratio
- ✓ Provide focus states
- ✓ Use meaningful button text

### Don'ts
- ✗ Don't use `<div>` for buttons/links
- ✗ Don't hide focus indicators
- ✗ Don't use color alone to convey meaning
- ✗ Don't disable form validation
- ✗ Don't use `aria-label` on non-interactive elements
- ✗ Don't override semantic meaning with CSS
- ✗ Don't use more than 3 accent colors

---

**Last Updated:** 2025-08-02  
**Status:** Production Ready  
**Components:** 15+ patterns  
**Accessibility:** WCAG AA Compliant
