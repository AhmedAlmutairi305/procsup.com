// ===== Helpers =====
const $ = (sel) => document.querySelector(sel);

function toast(msg) {
  const el = $("#toast");
  if (!el) return;
  el.textContent = msg;
  el.hidden = false;
  setTimeout(() => (el.hidden = true), 2600);
}

// ===== Language Toggle (EN / AR) =====
const langToggle = $("#langToggle");
const langEls = document.querySelectorAll("[data-lang]");
const htmlEl = document.documentElement;

function setLang(lang) {
  langEls.forEach(el => {
    el.hidden = el.getAttribute("data-lang") !== lang;
  });

  if (lang === "ar") {
    htmlEl.setAttribute("dir", "rtl");
    htmlEl.setAttribute("lang", "ar");
    if (langToggle) langToggle.textContent = "EN";
  } else {
    htmlEl.setAttribute("dir", "ltr");
    htmlEl.setAttribute("lang", "en");
    if (langToggle) langToggle.textContent = "AR";
  }

  localStorage.setItem("siteLang", lang);
}

// Load saved language (default EN)
const savedLang = localStorage.getItem("siteLang") || "en";
setLang(savedLang);

langToggle?.addEventListener("click", () => {
  const current = htmlEl.getAttribute("lang");
  setLang(current === "en" ? "ar" : "en");
});

// ===== Mobile Menu =====
const btnMenu = $("#btnMenu");
const mobileMenu = $("#mobileMenu");

btnMenu?.addEventListener("click", () => {
  const isHidden = mobileMenu?.hasAttribute("hidden");
  if (!mobileMenu) return;
  if (isHidden) mobileMenu.removeAttribute("hidden");
  else mobileMenu.setAttribute("hidden", "");
});

// ===== Scroll to Contact =====
function scrollToContact() {
  $("#contact")?.scrollIntoView({ behavior: "smooth" });
  mobileMenu?.setAttribute("hidden", "");
}

$("#btnScrollContact")?.addEventListener("click", scrollToContact);
$("#btnScrollContact2")?.addEventListener("click", scrollToContact);

// ===== Footer year + site url =====
const yearEl = $("#year");
if (yearEl) yearEl.textContent = new Date().getFullYear().toString();

const siteUrlEl = $("#siteUrl");
if (siteUrlEl) siteUrlEl.textContent = window.location.origin || "https://procsup.com";

// ===== Animated Counters =====
function animateCounters() {
  const counters = document.querySelectorAll("[data-counter]");
  counters.forEach((el) => {
    const target = Number(el.getAttribute("data-counter") || 0);
    let current = 0;
    const step = Math.max(1, Math.floor(target / 40));
    const timer = setInterval(() => {
      current += step;
      if (current >= target) {
        current = target;
        clearInterval(timer);
      }
      el.textContent = String(current);
    }, 25);
  });
}

// run counters once when hero is visible
const hero = document.querySelector(".hero");
if (hero && "IntersectionObserver" in window) {
  const io = new IntersectionObserver((entries) => {
    if (entries.some((e) => e.isIntersecting)) {
      animateCounters();
      io.disconnect();
    }
  });
  io.observe(hero);
} else {
  animateCounters();
}

// ===== Quote Form -> mailto (Language Aware) =====
$("#quoteForm")?.addEventListener("submit", (e) => {
  e.preventDefault();
  const form = e.target;
  const data = new FormData(form);

  const name = String(data.get("name") || "").trim();
  const email = String(data.get("email") || "").trim();
  const requirements = String(data.get("requirements") || "").trim();

  const lang = htmlEl.getAttribute("lang") || "en";
  const to = "info@procsup.com";

  let subject = "";
  let body = "";

  if (lang === "ar") {
    subject = encodeURIComponent(`طلب عرض سعر - ${name || "عميل"}`);
    body = encodeURIComponent(
`السلام عليكم فريق Procsup،

الاسم: ${name}
البريد الإلكتروني: ${email}

تفاصيل الطلب:
${requirements}

شاكرين ومقدرين،
${name}`
    );
  } else {
    subject = encodeURIComponent(`Quote Request - ${name || "Client"}`);
    body = encodeURIComponent(
`Hello Procsup,

My name: ${name}
My email: ${email}

Requirements:
${requirements}

Best regards,
${name}`
    );
  }

  const link = `mailto:${to}?subject=${subject}&body=${body}`;
  window.location.href = link;

  toast(lang === "ar"
    ? "سيتم فتح تطبيق البريد مع رسالة جاهزة"
    : "Opening your email app with a pre-filled message..."
  );
});
