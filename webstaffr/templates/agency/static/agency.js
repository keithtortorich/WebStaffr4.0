// WebStaffr Agency Site — minimal interactivity

document.addEventListener('DOMContentLoaded', () => {
  // Smooth scroll on anchor links
  document.querySelectorAll('a[href^="#"]').forEach(link => {
    link.addEventListener('click', (e) => {
      e.preventDefault();
      const target = document.querySelector(link.getAttribute('href'));
      if (target) {
        target.scrollIntoView({ behavior: 'smooth' });
      }
    });
  });

  // Form submit (placeholder)
  const forms = document.querySelectorAll('form');
  forms.forEach(form => {
    form.addEventListener('submit', (e) => {
      e.preventDefault();
      alert('Thank you! We'll contact you within 24 hours.');
      form.reset();
    });
  });
});
