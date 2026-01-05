const i18n = {
  ar: {
    dir: "rtl",
    title: "الموقع تحت الصيانة",
    desc: "نقوم حاليًا بتحديث الموقع. ترقبونا قريبًا.",
    note: "للاستفسارات: ",
    footer: "شكرًا لتفهمكم."
  },
  en: {
    dir: "ltr",
    title: "Website Under Maintenance",
    desc: "We are currently updating the website. Please check back soon.",
    note: "For inquiries: ",
    footer: "Thank you for your patience."
  },
  zh: {
    dir: "ltr",
    title: "网站维护中",
    desc: "我们正在更新网站内容，请稍后再来。",
    note: "如需咨询：",
    footer: "感谢您的理解。"
  }
};

function setLang(lang){
  const t = i18n[lang] || i18n.en;

  document.documentElement.lang = lang;
  document.documentElement.dir = t.dir;

  document.getElementById("title").textContent = t.title;
  document.getElementById("desc").textContent = t.desc;
  document.getElementById("note").textContent = t.note;
  document.getElementById("footerText").textContent = t.footer;

  document.querySelectorAll(".lang-btn").forEach(btn => {
    btn.classList.toggle("active", btn.dataset.lang === lang);
  });

  localStorage.setItem("site_lang", lang);
}

document.addEventListener("DOMContentLoaded", () => {
  // Default: Arabic, unless user previously chose another language
  const saved = localStorage.getItem("site_lang") || "ar";
  setLang(saved);

  document.querySelectorAll(".lang-btn").forEach(btn => {
    btn.addEventListener("click", () => setLang(btn.dataset.lang));
  });
});
