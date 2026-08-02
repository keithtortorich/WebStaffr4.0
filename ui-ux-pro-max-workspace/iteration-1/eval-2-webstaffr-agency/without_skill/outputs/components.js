/**
 * WebStaffr Design System Components
 * Lightweight, accessible JavaScript components
 * No dependencies - vanilla JS with progressive enhancement
 */

/* ============================================
   CAROUSEL / TESTIMONIALS
   ============================================ */

class TestimonialCarousel {
  constructor(containerSelector) {
    this.container = document.querySelector(containerSelector);
    if (!this.container) return;

    this.slides = this.container.querySelectorAll('.testimonial-slide');
    this.dots = this.container.querySelectorAll('.carousel-dot');
    this.currentIndex = 0;
    this.autoPlayInterval = null;

    this.init();
  }

  init() {
    // Show first slide
    this.showSlide(0);

    // Attach dot click handlers
    this.dots.forEach((dot, index) => {
      dot.addEventListener('click', () => this.showSlide(index));
      dot.setAttribute('aria-label', `Testimonial ${index + 1}`);
    });

    // Auto-play
    this.startAutoPlay();

    // Pause on hover
    this.container.addEventListener('mouseenter', () => this.stopAutoPlay());
    this.container.addEventListener('mouseleave', () => this.startAutoPlay());

    // Keyboard navigation (accessibility)
    document.addEventListener('keydown', (e) => {
      if (e.key === 'ArrowLeft') this.previousSlide();
      if (e.key === 'ArrowRight') this.nextSlide();
    });
  }

  showSlide(index) {
    // Clamp index
    if (index < 0) index = this.slides.length - 1;
    if (index >= this.slides.length) index = 0;

    this.currentIndex = index;

    // Update slides
    this.slides.forEach((slide, i) => {
      if (i === index) {
        slide.classList.add('active');
        slide.setAttribute('aria-hidden', 'false');
      } else {
        slide.classList.remove('active');
        slide.setAttribute('aria-hidden', 'true');
      }
    });

    // Update dots
    this.dots.forEach((dot, i) => {
      if (i === index) {
        dot.classList.add('active');
        dot.setAttribute('aria-current', 'true');
      } else {
        dot.classList.remove('active');
        dot.setAttribute('aria-current', 'false');
      }
    });
  }

  nextSlide() {
    this.showSlide(this.currentIndex + 1);
    this.resetAutoPlay();
  }

  previousSlide() {
    this.showSlide(this.currentIndex - 1);
    this.resetAutoPlay();
  }

  startAutoPlay() {
    this.autoPlayInterval = setInterval(
      () => this.nextSlide(),
      5000 // Change slide every 5 seconds
    );
  }

  stopAutoPlay() {
    clearInterval(this.autoPlayInterval);
  }

  resetAutoPlay() {
    this.stopAutoPlay();
    this.startAutoPlay();
  }

  destroy() {
    this.stopAutoPlay();
  }
}

/* ============================================
   BOOKING FORM
   ============================================ */

class BookingForm {
  constructor(formSelector) {
    this.form = document.querySelector(formSelector);
    if (!this.form) return;

    this.isSubmitting = false;
    this.init();
  }

  init() {
    this.form.addEventListener('submit', (e) => this.handleSubmit(e));

    // Add client-side validation listeners
    const inputs = this.form.querySelectorAll('input, textarea, select');
    inputs.forEach((input) => {
      input.addEventListener('blur', () => this.validateField(input));
      input.addEventListener('change', () => this.validateField(input));
    });
  }

  validateField(field) {
    const isValid = this.isFieldValid(field);
    const group = field.closest('.form-group');

    if (isValid) {
      group?.classList.remove('invalid');
      group?.classList.add('valid');
    } else {
      group?.classList.add('invalid');
      group?.classList.remove('valid');
    }

    return isValid;
  }

  isFieldValid(field) {
    if (field.hasAttribute('required') && !field.value.trim()) {
      return false;
    }

    if (field.type === 'email') {
      const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
      return emailRegex.test(field.value);
    }

    if (field.type === 'tel') {
      const phoneRegex = /^[\d\s\-\+\(\)\.]+$/;
      return phoneRegex.test(field.value);
    }

    return true;
  }

  async handleSubmit(e) {
    e.preventDefault();

    if (this.isSubmitting) return;

    // Validate all fields
    const inputs = this.form.querySelectorAll('input, textarea, select');
    let isFormValid = true;

    inputs.forEach((input) => {
      if (!this.validateField(input)) {
        isFormValid = false;
      }
    });

    if (!isFormValid) {
      this.showError('Please fill in all required fields correctly.');
      return;
    }

    this.isSubmitting = true;
    this.setSubmitButtonState(true);

    try {
      // Simulate API call (replace with actual endpoint)
      const formData = new FormData(this.form);
      const data = Object.fromEntries(formData);

      // Send to your backend
      const response = await fetch('/api/booking', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(data),
      });

      if (response.ok) {
        this.showSuccess('Booking submitted successfully!');
        this.form.reset();
      } else {
        const error = await response.json();
        this.showError(error.message || 'Something went wrong. Please try again.');
      }
    } catch (error) {
      console.error('Booking error:', error);
      this.showError('Network error. Please check your connection and try again.');
    } finally {
      this.isSubmitting = false;
      this.setSubmitButtonState(false);
    }
  }

  setSubmitButtonState(isLoading) {
    const submitBtn = this.form.querySelector('button[type="submit"]');
    if (!submitBtn) return;

    if (isLoading) {
      submitBtn.disabled = true;
      submitBtn.classList.add('btn-loading');
      submitBtn.textContent = 'Submitting...';
    } else {
      submitBtn.disabled = false;
      submitBtn.classList.remove('btn-loading');
      submitBtn.textContent = 'Book Now';
    }
  }

  showError(message) {
    const alert = this.createAlert('error', message);
    this.form.insertBefore(alert, this.form.firstChild);
    this.scrollToAlert(alert);
  }

  showSuccess(message) {
    const alert = this.createAlert('success', message);
    this.form.insertBefore(alert, this.form.firstChild);
    this.scrollToAlert(alert);

    setTimeout(() => alert.remove(), 5000);
  }

  createAlert(type, message) {
    const alert = document.createElement('div');
    const bgColor = type === 'error' ? 'var(--color-error-light)' : 'var(--color-success-light)';
    const textColor = type === 'error' ? 'var(--color-error)' : 'var(--color-success)';

    alert.setAttribute('role', 'alert');
    alert.style.cssText = `
      padding: 1rem;
      margin-bottom: 1rem;
      border-radius: 0.5rem;
      background-color: ${bgColor};
      color: ${textColor};
      border: 1px solid ${textColor};
    `;
    alert.textContent = message;

    return alert;
  }

  scrollToAlert(element) {
    element.scrollIntoView({ behavior: 'smooth', block: 'start' });
  }

  destroy() {
    this.form?.removeEventListener('submit', (e) => this.handleSubmit(e));
  }
}

/* ============================================
   THEME TOGGLE
   ============================================ */

class ThemeToggle {
  constructor(toggleSelector = '[data-theme-toggle]') {
    this.toggle = document.querySelector(toggleSelector);
    if (!this.toggle) return;

    this.preferredTheme = this.getPreferredTheme();
    this.init();
  }

  init() {
    this.applyTheme(this.preferredTheme);
    this.toggle.addEventListener('click', () => this.toggleTheme());

    // Listen for system preference changes
    window
      .matchMedia('(prefers-color-scheme: dark)')
      .addEventListener('change', (e) => {
        if (!this.hasSavedPreference()) {
          this.applyTheme(e.matches ? 'dark' : 'light');
        }
      });
  }

  toggleTheme() {
    const newTheme = this.preferredTheme === 'dark' ? 'light' : 'dark';
    this.setPreferredTheme(newTheme);
    this.applyTheme(newTheme);
  }

  applyTheme(theme) {
    this.preferredTheme = theme;

    const html = document.documentElement;
    if (theme === 'dark') {
      html.classList.add('dark');
      html.setAttribute('data-theme', 'dark');
      this.toggle?.setAttribute('aria-label', 'Switch to light mode');
      this.toggle?.innerHTML = '☀️';
    } else {
      html.classList.remove('dark');
      html.setAttribute('data-theme', 'light');
      this.toggle?.setAttribute('aria-label', 'Switch to dark mode');
      this.toggle?.innerHTML = '🌙';
    }
  }

  getPreferredTheme() {
    // Check localStorage first
    const saved = localStorage.getItem('theme');
    if (saved) return saved;

    // Fall back to system preference
    return window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light';
  }

  setPreferredTheme(theme) {
    localStorage.setItem('theme', theme);
    this.preferredTheme = theme;
  }

  hasSavedPreference() {
    return localStorage.getItem('theme') !== null;
  }
}

/* ============================================
   MOBILE MENU TOGGLE
   ============================================ */

class MobileMenu {
  constructor(toggleSelector = '[data-menu-toggle]', menuSelector = '[data-menu]') {
    this.toggle = document.querySelector(toggleSelector);
    this.menu = document.querySelector(menuSelector);
    if (!this.toggle || !this.menu) return;

    this.isOpen = false;
    this.init();
  }

  init() {
    this.toggle.addEventListener('click', () => this.toggleMenu());

    // Close menu when clicking on a link
    this.menu.querySelectorAll('a').forEach((link) => {
      link.addEventListener('click', () => this.closeMenu());
    });

    // Close menu on Escape key
    document.addEventListener('keydown', (e) => {
      if (e.key === 'Escape') this.closeMenu();
    });

    // Close menu when clicking outside
    document.addEventListener('click', (e) => {
      if (!this.toggle.contains(e.target) && !this.menu.contains(e.target)) {
        this.closeMenu();
      }
    });
  }

  toggleMenu() {
    this.isOpen ? this.closeMenu() : this.openMenu();
  }

  openMenu() {
    this.isOpen = true;
    this.menu.classList.add('open');
    this.toggle.setAttribute('aria-expanded', 'true');
    document.body.style.overflow = 'hidden';
  }

  closeMenu() {
    this.isOpen = false;
    this.menu.classList.remove('open');
    this.toggle.setAttribute('aria-expanded', 'false');
    document.body.style.overflow = '';
  }
}

/* ============================================
   SCROLL SPY (Highlight active nav)
   ============================================ */

class ScrollSpy {
  constructor(navSelector = 'nav', sectionSelector = 'section[id]') {
    this.nav = document.querySelector(navSelector);
    this.sections = document.querySelectorAll(sectionSelector);
    if (!this.nav || this.sections.length === 0) return;

    this.links = this.nav.querySelectorAll('a[href^="#"]');
    this.init();
  }

  init() {
    window.addEventListener('scroll', () => this.updateActiveLink());
    this.updateActiveLink();
  }

  updateActiveLink() {
    let current = '';

    this.sections.forEach((section) => {
      const sectionTop = section.offsetTop;
      const sectionHeight = section.clientHeight;

      if (window.pageYOffset >= sectionTop - 200) {
        current = section.getAttribute('id');
      }
    });

    this.links.forEach((link) => {
      link.classList.remove('active');
      if (link.getAttribute('href').slice(1) === current) {
        link.classList.add('active');
        link.setAttribute('aria-current', 'page');
      } else {
        link.setAttribute('aria-current', 'false');
      }
    });
  }
}

/* ============================================
   SMOOTH SCROLL
   ============================================ */

class SmoothScroll {
  constructor() {
    this.init();
  }

  init() {
    document.addEventListener('click', (e) => {
      const link = e.target.closest('a[href^="#"]');
      if (!link) return;

      e.preventDefault();
      const targetId = link.getAttribute('href').slice(1);
      const target = document.getElementById(targetId);

      if (target) {
        target.scrollIntoView({ behavior: 'smooth' });
      }
    });
  }
}

/* ============================================
   LAZY IMAGE LOADING
   ============================================ */

class LazyImages {
  constructor(selector = 'img[data-src]') {
    this.images = document.querySelectorAll(selector);
    this.init();
  }

  init() {
    if ('IntersectionObserver' in window) {
      const observer = new IntersectionObserver((entries) => {
        entries.forEach((entry) => {
          if (entry.isIntersecting) {
            this.loadImage(entry.target);
            observer.unobserve(entry.target);
          }
        });
      });

      this.images.forEach((img) => observer.observe(img));
    } else {
      // Fallback for older browsers
      this.images.forEach((img) => this.loadImage(img));
    }
  }

  loadImage(img) {
    const src = img.getAttribute('data-src');
    if (!src) return;

    img.src = src;
    img.removeAttribute('data-src');
    img.classList.add('loaded');
  }
}

/* ============================================
   INITIALIZATION
   ============================================ */

// Auto-initialize on DOM ready
if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', () => {
    initializeComponents();
  });
} else {
  initializeComponents();
}

function initializeComponents() {
  // Initialize all components
  new TestimonialCarousel('.testimonial-carousel');
  new BookingForm('.booking-widget form');
  new ThemeToggle('[data-theme-toggle]');
  new MobileMenu('[data-menu-toggle]', '[data-menu]');
  new ScrollSpy('nav', 'section[id]');
  new SmoothScroll();
  new LazyImages('img[data-src]');

  // Log initialization
  console.log('WebStaffr Design System components initialized');
}

// Export for use in other contexts
if (typeof module !== 'undefined' && module.exports) {
  module.exports = {
    TestimonialCarousel,
    BookingForm,
    ThemeToggle,
    MobileMenu,
    ScrollSpy,
    SmoothScroll,
    LazyImages,
  };
}
