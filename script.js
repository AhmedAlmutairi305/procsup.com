document.addEventListener('DOMContentLoaded', () => {
  const nav = document.getElementById('siteNav');
  const toggle = document.getElementById('navToggle');
  const langToggle = document.getElementById('langToggle');
  const brand = document.querySelector('.brand');

  if (toggle) {
    toggle.addEventListener('click', () => {
      nav.classList.toggle('open');
    });
  }

  // Language toggle: switches dir and lang attribute (lightweight support)
  if (langToggle) {
    langToggle.addEventListener('click', () => {
      const html = document.documentElement;
      if (html.getAttribute('dir') === 'rtl') {
        html.setAttribute('dir', 'ltr');
        html.setAttribute('lang', 'en');
        langToggle.textContent = 'AR';
        if (brand) brand.textContent = 'ProcureCo';
      } else {
        html.setAttribute('dir', 'rtl');
        html.setAttribute('lang', 'ar');
        langToggle.textContent = 'EN';
        if (brand) brand.textContent = 'ProcureCo';
      }
      // close mobile nav on toggle
      if (nav) nav.classList.remove('open');
    });
  }

  // Smooth scroll for anchor links
  document.querySelectorAll('a[href^="#"]').forEach(a => {
    a.addEventListener('click', (e) => {
      const targetId = a.getAttribute('href').slice(1);
      const target = document.getElementById(targetId);
      if (target) {
        e.preventDefault();
        const yOffset = -72; // account for fixed header
        const y = target.getBoundingClientRect().top + window.pageYOffset + yOffset;
        window.scrollTo({ top: y, behavior: 'smooth' });
        if (nav) nav.classList.remove('open');
      }
    });
  });

  // Contact form (demo - no backend)
  const form = document.getElementById('contactForm');
  if (form) {
    form.addEventListener('submit', e => {
      e.preventDefault();
      const data = new FormData(form);
      const name = (data.get('name') || '').toString().trim();
      const email = (data.get('email') || '').toString().trim();
      const message = (data.get('message') || '').toString().trim();
      if (!name || !email || !message) {
        alert('المرجو تعبئة الحقول المطلوبة');
        return;
      }
      alert('تم استلام رسالتك. شكراً لتواصلك معنا — هذا نموذج تجريبي.');
      form.reset();
    });
  }
});
