/* ============================================================
   MedSourcing — site behavior
   ------------------------------------------------------------
   No frameworks, no backend. Plain JavaScript.

   👉 EDIT YOUR CONTACT DETAILS HERE (one place):
   ============================================================ */
const CONFIG = {
  // Email address that receives contact-form submissions and email buttons
  email: "info@procsup.com",

  // WhatsApp number in international format, DIGITS ONLY (no +, spaces, or dashes)
  // Example: 15551234567  ->  wa.me/15551234567
  whatsapp: "966558510594",

  // Friendly number shown on screen (display only)
  whatsappDisplay: "+966 55 851 0594",

  // Brand name used in the email subject line
  brand: "PROCSUP",
};

/* ============================================================
   Run after the DOM is ready (script is loaded with `defer`)
   ============================================================ */
document.addEventListener("DOMContentLoaded", () => {
  applyContactConfig();
  initMobileNav();
  initHeaderShadow();
  initActiveNav();
  initContactForm();
  initReveal();
  setFooterYear();
});

/* ------------------------------------------------------------
   Apply CONFIG to all email / WhatsApp links and labels
   ------------------------------------------------------------ */
function applyContactConfig() {
  const mailto = `mailto:${CONFIG.email}`;
  const waLink = `https://wa.me/${CONFIG.whatsapp}`;

  // Email links
  setHref("emailBtn", mailto);
  setHref("footerEmail", mailto);
  const emailText = document.getElementById("emailText");
  if (emailText) { emailText.href = mailto; emailText.textContent = CONFIG.email; }

  // WhatsApp links
  setHref("whatsappBtn", waLink);
  setHref("footerWhatsapp", waLink);
  const waText = document.getElementById("whatsappText");
  if (waText) { waText.href = waLink; waText.textContent = CONFIG.whatsappDisplay; }

  // Footer WhatsApp display text
  const footerWa = document.getElementById("footerWhatsapp");
  if (footerWa) footerWa.textContent = CONFIG.whatsappDisplay;
}

function setHref(id, href) {
  const el = document.getElementById(id);
  if (el) el.href = href;
}

/* ------------------------------------------------------------
   Mobile navigation (hamburger toggle)
   ------------------------------------------------------------ */
function initMobileNav() {
  const toggle = document.getElementById("navToggle");
  const nav = document.getElementById("primaryNav");
  if (!toggle || !nav) return;

  const closeMenu = () => {
    nav.classList.remove("is-open");
    toggle.setAttribute("aria-expanded", "false");
    toggle.setAttribute("aria-label", "Open menu");
  };
  const openMenu = () => {
    nav.classList.add("is-open");
    toggle.setAttribute("aria-expanded", "true");
    toggle.setAttribute("aria-label", "Close menu");
  };

  toggle.addEventListener("click", () => {
    const isOpen = nav.classList.contains("is-open");
    isOpen ? closeMenu() : openMenu();
  });

  // Close after tapping a link (smooth scroll then collapse)
  nav.querySelectorAll("a").forEach((link) => {
    link.addEventListener("click", closeMenu);
  });

  // Close on Escape
  document.addEventListener("keydown", (e) => {
    if (e.key === "Escape") closeMenu();
  });

  // Close when clicking outside the header
  document.addEventListener("click", (e) => {
    const header = e.target.closest(".site-header");
    if (!header && nav.classList.contains("is-open")) closeMenu();
  });
}

/* ------------------------------------------------------------
   Add a subtle shadow to the header once the page scrolls
   ------------------------------------------------------------ */
function initHeaderShadow() {
  const header = document.querySelector(".site-header");
  if (!header) return;
  const onScroll = () => {
    header.classList.toggle("is-scrolled", window.scrollY > 8);
  };
  onScroll();
  window.addEventListener("scroll", onScroll, { passive: true });
}

/* ------------------------------------------------------------
   Highlight the nav link for the section currently in view
   ------------------------------------------------------------ */
function initActiveNav() {
  const links = Array.from(document.querySelectorAll(".nav__link"));
  const map = new Map();
  links.forEach((link) => {
    const id = link.getAttribute("href");
    if (id && id.startsWith("#")) {
      const section = document.querySelector(id);
      if (section) map.set(section, link);
    }
  });
  if (map.size === 0) return;

  const observer = new IntersectionObserver(
    (entries) => {
      entries.forEach((entry) => {
        if (entry.isIntersecting) {
          links.forEach((l) => l.classList.remove("is-active"));
          const active = map.get(entry.target);
          if (active) active.classList.add("is-active");
        }
      });
    },
    { rootMargin: "-45% 0px -50% 0px" }
  );

  map.forEach((_, section) => observer.observe(section));
}

/* ------------------------------------------------------------
   Contact form -> opens the user's email client (mailto).
   GitHub Pages has no backend, so we compose an email instead.
   ------------------------------------------------------------ */
function initContactForm() {
  const form = document.getElementById("contactForm");
  const status = document.getElementById("formStatus");
  if (!form) return;

  form.addEventListener("submit", (e) => {
    e.preventDefault();

    const name = field(form, "name");
    const email = field(form, "email");
    const company = field(form, "company");
    const type = field(form, "type");
    const message = field(form, "message");

    // Simple validation
    clearErrors(form);
    const errors = [];
    if (!name.value.trim()) errors.push(name);
    if (!isValidEmail(email.value)) errors.push(email);
    if (!message.value.trim()) errors.push(message);

    if (errors.length) {
      errors.forEach((el) => el.classList.add("invalid"));
      setStatus(status, "error", "Please add your name, a valid email, and your requirement.");
      errors[0].focus();
      return;
    }

    // Build the email
    const subject = `[${CONFIG.brand}] ${type.value} — ${name.value.trim()}`;
    const bodyLines = [
      `Name: ${name.value.trim()}`,
      `Email: ${email.value.trim()}`,
      company.value.trim() ? `Company: ${company.value.trim()}` : null,
      `Requirement type: ${type.value}`,
      "",
      "Requirement / message:",
      message.value.trim(),
    ].filter(Boolean);

    const mailtoUrl =
      `mailto:${CONFIG.email}` +
      `?subject=${encodeURIComponent(subject)}` +
      `&body=${encodeURIComponent(bodyLines.join("\n"))}`;

    setStatus(status, "success", "Opening your email app… if nothing happens, email us directly at " + CONFIG.email);
    window.location.href = mailtoUrl;
  });
}

function field(form, name) { return form.querySelector(`[name="${name}"]`); }

function clearErrors(form) {
  form.querySelectorAll(".invalid").forEach((el) => el.classList.remove("invalid"));
}

function isValidEmail(value) {
  return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(value.trim());
}

function setStatus(el, type, msg) {
  if (!el) return;
  el.textContent = msg;
  el.className = "form__status " + type;
}

/* ------------------------------------------------------------
   Subtle scroll reveal for sections (respects reduced motion)
   ------------------------------------------------------------ */
function initReveal() {
  const prefersReduced =
    window.matchMedia &&
    window.matchMedia("(prefers-reduced-motion: reduce)").matches;

  const targets = document.querySelectorAll(
    ".section__head, .card, .category, .step, .feature, " +
    ".suppliers__intro, .about__intro, .about__text, " +
    ".contact__info, .contact__form-wrap"
  );

  if (prefersReduced || !("IntersectionObserver" in window)) {
    targets.forEach((t) => t.classList.add("is-visible"));
    return;
  }

  targets.forEach((t) => t.classList.add("reveal"));

  const observer = new IntersectionObserver(
    (entries, obs) => {
      entries.forEach((entry) => {
        if (entry.isIntersecting) {
          entry.target.classList.add("is-visible");
          obs.unobserve(entry.target);
        }
      });
    },
    { threshold: 0.12 }
  );

  targets.forEach((t) => observer.observe(t));
}

/* ------------------------------------------------------------
   Footer year
   ------------------------------------------------------------ */
function setFooterYear() {
  const el = document.getElementById("year");
  if (el) el.textContent = new Date().getFullYear();
}
