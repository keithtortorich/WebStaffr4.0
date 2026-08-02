# WebStaffr Design System - Quick Reference Color Guide

**Version:** 1.0  
**Print-Friendly:** Yes (Use 100% zoom for accurate colors)  
**Last Updated:** August 2, 2026

---

## Color Palette at a Glance

### Primary Colors

```
Background Primary
#1A1A1A (Dark Gray - Main Background)
RGB: 26, 26, 26
HSL: 0°, 0%, 10%
Usage: Main container, primary background

Text Primary
#CCCCCC (Light Gray - Body Text)
RGB: 204, 204, 204
HSL: 0°, 0%, 80%
Usage: Body text, headings, primary content
Contrast on BG Primary: 10.84:1 ✓ AAA

Accent Primary
#FF6B6B (Red - Action Elements)
RGB: 255, 107, 107
HSL: 0°, 100%, 71%
Usage: Buttons, links, interactive elements
Contrast on BG Primary: 6.27:1 ✓ AA
```

### Secondary Colors

```
Background Secondary
#242424 (Dark Gray - Light Variant)
RGB: 36, 36, 36
HSL: 0°, 0%, 14%
Usage: Card backgrounds, input backgrounds

Text Secondary
#999999 (Gray - Muted Text)
RGB: 153, 153, 153
HSL: 0°, 0%, 60%
Usage: Secondary text, labels, hints
Contrast on BG Primary: 5.98:1 ✓ AA

Accent Dark
#E63946 (Dark Red - Hover/Active)
RGB: 230, 57, 70
HSL: 356°, 78%, 56%
Usage: Hover states, darker accents
Contrast on BG Primary: 4.87:1 ✓ AA
```

### Semantic Colors

```
Success
#52B788 (Green - Success State)
RGB: 82, 183, 136
HSL: 159°, 38%, 52%
Usage: Success messages, confirmations
Contrast on BG Primary: 5.29:1 ✓ AA

Warning
#FFB703 (Gold - Warning State)
RGB: 255, 183, 3
HSL: 42°, 100%, 50%
Usage: Warning alerts, cautionary elements
Contrast on BG Primary: 4.54:1 ✓ AA

Error
#D62828 (Deep Red - Error State)
RGB: 214, 40, 40
HSL: 0°, 68%, 50%
Usage: Error messages, validation failures
Contrast on BG Primary: 3.80:1 ✓ AA (Large)

Info
#4D96FF (Blue - Info State)
RGB: 77, 150, 255
HSL: 217°, 100%, 65%
Usage: Info messages, helpful tips
Contrast on BG Primary: 4.73:1 ✓ AA
```

---

## Color Combinations Quick Reference

### Recommended Combinations ✓

| Foreground | Background | Use Case | Ratio | Status |
|-----------|-----------|----------|-------|--------|
| #CCCCCC (Text) | #1A1A1A (BG) | Body text | 10.84:1 | AAA ✓ |
| #FF6B6B (Accent) | #1A1A1A (BG) | Buttons | 6.27:1 | AA ✓ |
| #52B788 (Success) | #1A1A1A (BG) | Badges | 5.29:1 | AA ✓ |
| #FFB703 (Warning) | #1A1A1A (BG) | Alerts | 4.54:1 | AA ✓ |
| #4D96FF (Info) | #1A1A1A (BG) | Messages | 4.73:1 | AA ✓ |

### NOT Recommended Combinations ✗

| Foreground | Background | Issue | Ratio | Status |
|-----------|-----------|-------|-------|--------|
| #FF6B6B (Accent) | #CCCCCC (Text) | Too light | 1.73:1 | FAIL ✗ |
| #999999 (Muted) | #242424 (Light BG) | Too subtle | 2.89:1 | FAIL ✗ |
| #CCCCCC (Text) | #999999 (Gray) | Low contrast | 1.32:1 | FAIL ✗ |

---

## CSS Variable Quick Lookup

```css
/* Copy-paste ready CSS variables */

:root {
  /* Backgrounds */
  --color-bg-primary: #1A1A1A;
  --color-bg-secondary: #242424;
  --color-bg-tertiary: #2E2E2E;

  /* Text */
  --color-text-primary: #CCCCCC;
  --color-text-secondary: #999999;
  --color-text-tertiary: #666666;
  --color-text-inverse: #1A1A1A;

  /* Accents */
  --color-accent-primary: #FF6B6B;
  --color-accent-dark: #E63946;
  --color-accent-light: #FF9999;

  /* Semantic */
  --color-success: #52B788;
  --color-warning: #FFB703;
  --color-error: #D62828;
  --color-info: #4D96FF;

  /* Borders */
  --color-border: #3A3A3A;
  --color-focus-ring: #FF6B6B;
}
```

---

## Component Color Reference

### Button Styles

```
Primary Button
Background: #FF6B6B
Text: #1A1A1A
Hover: #E63946
Disabled: #3A3A3A

Secondary Button
Background: Transparent
Border: #3A3A3A
Text: #CCCCCC
Hover: #2E2E2E (background)
```

### Form Elements

```
Input Background
#242424

Input Border
#3A3A3A

Input Text
#CCCCCC

Input Focus Ring
#FF6B6B (2px)

Placeholder Text
#999999

Error Text
#D62828
```

### Alerts

```
Success Alert
Background: rgba(82, 183, 136, 0.1)
Border: #52B788
Text: #52B788

Warning Alert
Background: rgba(255, 183, 3, 0.1)
Border: #FFB703
Text: #FFB703

Error Alert
Background: rgba(214, 40, 40, 0.1)
Border: #D62828
Text: #D62828
```

### Navigation & Links

```
Standard Link
Color: #FF6B6B
Hover: #E63946
Visited: #FF9999 (optional)
Focus: 2px solid #FF6B6B outline
```

---

## Do's and Don'ts

### DO ✓
- Use #CCCCCC for body text on #1A1A1A
- Use #FF6B6B for buttons and interactive elements
- Add icon/text with color indicators (not color alone)
- Test colors with contrast checker before using
- Respect user's color preferences (dark/light mode)

### DON'T ✗
- Don't use #FF6B6B as text on #CCCCCC (fails accessibility)
- Don't rely on color to convey information (use text/icons too)
- Don't assume colors look the same on all screens
- Don't forget focus indicators on interactive elements
- Don't use pale colors (#999999+) for important text

---

## Testing Checklist

Before using any color combination:

- [ ] Check contrast with WebAIM Contrast Checker
- [ ] Verify WCAG AA minimum (4.5:1 for normal text)
- [ ] Simulate with color blindness tool
- [ ] Test on multiple monitors
- [ ] Check printed version (grayscale)
- [ ] Verify with screen reader (if using color for info)

---

## Color Accessibility By The Numbers

| Ratio | Level | Use Case | Minimum Size |
|-------|-------|----------|--------------|
| 7:1 | AAA Enhanced | Any text, preferred | Any |
| 4.5:1 | AA Compliant | Normal text (16pt+) | Any |
| 3:1 | AA Large Text | Large text (18pt+ or 14pt bold) | 18pt+ |
| < 3:1 | Fails | Not for text | N/A - Graphics only |

**Your Current Palette:**
- Text + Background: 10.84:1 (AAA ✓)
- Accent + Background: 6.27:1 (AA ✓)
- Accent + Text: 1.73:1 (FAIL - avoid)

---

## Print This Page

**Print Settings:**
- Set zoom to 100%
- Keep colors (don't print as grayscale)
- Print full page
- Use as physical reference

**Colors will be most accurate when printed on high-quality photo paper.**

---

## Color Palette Hex Codes (Sorted)

For copy-pasting into tools:

```
#1A1A1A - Primary Background
#242424 - Secondary Background  
#2E2E2E - Tertiary Background
#3A3A3A - Border Color
#4D96FF - Info Blue
#52B788 - Success Green
#666666 - Tertiary Text
#999999 - Secondary Text
#CCCCCC - Primary Text
#D62828 - Error Red
#E63946 - Accent Dark Red
#FF6B6B - Accent Primary Red
#FF9999 - Accent Light Red
#FFB703 - Warning Gold
```

---

## Common Questions

### Q: Can I use the light versions for body text?
**A:** No. #999999 on #1A1A1A only gives 5.98:1. Use #CCCCCC (10.84:1) for main text.

### Q: Can I use the accent color as text?
**A:** Only on #1A1A1A background. On #CCCCCC text, the ratio is 1.73:1 (fails). Always test first.

### Q: What if the colors look different on my screen?
**A:** Monitor calibration varies. Always test with WebAIM Contrast Checker and actual users.

### Q: Should I create a light theme version?
**A:** Yes. Use the same color relationships but inverted. Test accessibility on both.

### Q: How do I remember all these colors?
**A:** Use CSS custom properties (variables). You only need to remember: primary, secondary, accent, success, warning, error, info.

---

## Additional Resources

**Contrast Checking:**
- WebAIM Contrast Checker: https://webaim.org/resources/contrastchecker/
- Contrast Ratio: https://contrast-ratio.com/

**Color Blindness Testing:**
- Color Oracle: https://colororacle.org/
- Coblis Simulator: https://www.color-blindness.com/coblis-color-blindness-simulator/

**Design Tool Sync:**
- Figma Color Variables: figma.com/plugin-docs/api/figma_variables/
- Sketch Libraries: developer.sketch.com/reference/api

**Accessibility Standards:**
- WCAG 2.1: https://www.w3.org/WAI/WCAG21/quickref/
- A11y Project: https://www.a11yproject.com/

---

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0 | 2026-08-02 | Initial quick reference guide |

---

**This is a quick reference guide. For complete documentation, see:**
- `01_WCAG_AA_AUDIT_REPORT.md` — Full audit results
- `02_DESIGN_SYSTEM_COLORS.css` — Complete CSS implementation
- `04_DESIGN_SYSTEM_DOCUMENTATION.md` — Comprehensive guide
