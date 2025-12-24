// ===== Helpers =====
const $ = (sel) => document.querySelector(sel);

function toast(msg) {
  const el = $("#toast");
  if (!el) return;
  el.textContent = msg;
  el.hidden = false;
  setTimeout(() => (el.hidden = true), 2600);
}

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
$("#year").textContent = new Date().getFullYear().toString();
$("#siteUrl").textContent = window.location.origin || "https://procsup.com";

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

// ===== Quote Form -> mailto (no backend) =====
$("#quoteForm")?.addEventListener("submit", (e) => {
  e.preventDefault();
  const form = e.target;
  const data = new FormData(form);

  const name = String(data.get("name") || "").trim();
  const email = String(data.get("email") || "").trim();
  const requirements = String(data.get("requirements") || "").trim();

  const to = "info@procsup.com";
  const subject = encodeURIComponent(`Quote Request - ${name || "Client"}`);
  const body = encodeURIComponent(
`Hello Procsup,

My name: ${name}
My email: ${email}

Requirements:
${requirements}

Best regards,
${name}`
  );

  const link = `mailto:${to}?subject=${subject}&body=${body}`;
  window.location.href = link;
  toast("Opening your email app with a pre-filled message...");
});
