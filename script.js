// Pause/resume marquee animations when out of viewport; respect reduced motion
(function(){
  try{
    if (window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches) return;
    // handle both horizontal marquees and the new aside vertical carousel
    const containers = Array.from(document.querySelectorAll('.marquee, .aside-strip'));
    if (!containers.length) return;

    const onVisibilityChange = (entries)=>{
      entries.forEach(entry=>{
        const track = entry.target.querySelector('.marquee-track, .aside-track');
        if (!track) return;
        track.style.animationPlayState = entry.isIntersecting ? 'running' : 'paused';
      });
    };

    const observer = new IntersectionObserver(onVisibilityChange, {threshold:0.2});
    containers.forEach(c => {
      const track = c.querySelector('.marquee-track, .aside-track');
      if (track) track.style.animationPlayState = 'running';
      observer.observe(c);
    });
  }catch(e){
    // fail silently
  }
})();

document.addEventListener('DOMContentLoaded', () => {
  const nav = document.getElementById('siteNav');
  const toggle = document.getElementById('navToggle');
  const langToggle = document.getElementById('langToggle');
  const brand = document.querySelector('.brand');

  // Supported languages and translations
  const langs = ['ar', 'en', 'zh'];
  let current = 0; // index in langs (default AR)

  const translations = {
    brand: { ar: 'Procsup', en: 'Procsup', zh: 'Procsup' },
    navHome: { ar: 'الرئيسية', en: 'Home', zh: '首页' },
    navAbout: { ar: 'من نحن', en: 'About', zh: '关于我们' },
    navServices: { ar: 'الخدمات', en: 'Services', zh: '服务' },
    navClients: { ar: 'العملاء', en: 'Clients', zh: '客户' },
    navCompliance: { ar: 'الامتثال', en: 'Compliance', zh: '合规' },
    navContact: { ar: 'اتصل بنا', en: 'Contact', zh: '联系我们' },

    heroTitle: { ar: 'حلول مهنية للمشتريات والتموين', en: 'Professional Procurement & Sourcing Solutions', zh: '专业采购与供应解决方案' },
    heroDesc: { ar: 'نقدّم خدمات متكاملة في المشتريات، التوريد، اللوجستيات والامتثال لمؤسسات تحتاج إلى شريك موثوق.', en: 'We provide end-to-end procurement, sourcing, logistics and compliance services for organizations seeking a reliable partner.', zh: '我们为寻求可靠合作伙伴的组织提供端到端采购、供应、物流和合规服务。' },
    ctaPrimary: { ar: 'اطلب استشارة', en: 'Request Consultation', zh: '请求咨询' },
    ctaSecondary: { ar: 'خدماتنا', en: 'Our Services', zh: '我们的服务' },

    aboutTitle: { ar: 'من نحن', en: 'About Us', zh: '关于我们' },
    aboutText: { ar: 'شركة متخصصة في تقديم حلول المشتريات والتموين للمؤسسات الحكومية والخاصة، نعمل على تقليل التكلفة وتحسين سلسلة الإمداد مع ضمان أعلى معايير الشفافية والامتثال.', en: 'A firm specialized in procurement and sourcing solutions for public and private organizations, focused on cost reduction and supply chain optimization while ensuring transparency and compliance.', zh: '一家专注于为公共和私营组织提供采购与供应解决方案的公司，致力于降低成本并优化供应链，同时确保透明与合规。' },

    servicesTitle: { ar: 'خدماتنا', en: 'Our Services', zh: '我们的服务' },
    svc1Title: { ar: 'المشتريات الاستراتيجية', en: 'Strategic Procurement', zh: '战略采购' },
    svc1Text: { ar: 'تحليل وفحص احتياجات المؤسسة وإدارة المنافسات للحصول على أفضل الأسعار والجودة.', en: 'Analyze requirements and manage tenders to secure best value and quality.', zh: '分析需求并管理招标，以获取最佳价值和质量。' },
    svc2Title: { ar: 'التوريد العالمي', en: 'Global Sourcing', zh: '全球采购' },
    svc2Text: { ar: 'شبكات موردين موثوقة وإدارة عقود التوريد محلياً ودولياً.', en: 'Trusted supplier networks and contract management locally and internationally.', zh: '可信赖的供应商网络与本地及国际合同管理。' },
    svc3Title: { ar: 'الخدمات اللوجستية', en: 'Logistics Services', zh: '物流服务' },
    svc3Text: { ar: 'حلول تخزين وشحن مخصصة مع تتبّع وتحسين سلسلة الإمداد.', en: 'Tailored warehousing and shipping with tracking and supply-chain optimization.', zh: '定制的仓储与运输解决方案，含追踪与供应链优化。' },
    svc4Title: { ar: 'الامتثال والشهادات', en: 'Compliance & Certifications', zh: '合规与认证' },
    svc4Text: { ar: 'دعم امتثال تنظيمي، تدقيق الموردين وحفظ معايير الجودة.', en: 'Regulatory compliance support, supplier audits and quality assurance.', zh: '提供法规合规支持、供应商审计与质量保证。' },

    clientsTitle: { ar: 'عملاؤنا وشركاؤنا', en: 'Our Clients & Partners', zh: '我们的客户与合作伙伴' },

    complianceTitle: { ar: 'الامتثال والشهادات', en: 'Compliance & Certifications', zh: '合规与认证' },
    complianceText: { ar: 'نلتزم بأعلى معايير الشفافية والجودة في جميع عملياتنا.', en: 'We adhere to the highest standards of transparency and quality across operations.', zh: '我们在所有运营中遵循最高的透明度和质量标准。' },

    contactTitle: { ar: 'تواصل معنا', en: 'Contact Us', zh: '联系我们' },
    labelName: { ar: 'الاسم', en: 'Name', zh: '姓名' },
    labelEmail: { ar: 'البريد الإلكتروني', en: 'Email', zh: '电子邮件' },
    labelMessage: { ar: 'الرسالة', en: 'Message', zh: '留言' },
    contactSubmit: { ar: 'إرسال الرسالة', en: 'Send Message', zh: '发送消息' },

    footerTag: { ar: 'شريكك في المشتريات والتموين', en: 'Your procurement & sourcing partner', zh: '您的采购与供应合作伙伴' },
    footerContact: { ar: 'info@procureco.example • +966 5X XXX XXXX', en: 'info@procureco.example • +966 5X XXX XXXX', zh: 'info@procureco.example • +966 5X XXX XXXX' },
    copyright: { ar: '© 2026 ProcureCo — جميع الحقوق محفوظة', en: '© 2026 ProcureCo — All rights reserved', zh: '© 2026 ProcureCo — 保留所有权利' }
  };

  // Apply translations to all elements having data-i18n
  function applyTranslations(lang) {
    document.querySelectorAll('[data-i18n]').forEach(el => {
      const key = el.getAttribute('data-i18n');
      if (translations[key] && translations[key][lang]) {
        // For inputs inside labels, update only the text nodes (use span wrappers in HTML)
        if (el.tagName.toLowerCase() === 'input' || el.tagName.toLowerCase() === 'textarea') return;
        el.textContent = translations[key][lang];
      }
    });
    // set html lang and dir
    const html = document.documentElement;
    html.setAttribute('lang', lang);
    if (lang === 'ar') html.setAttribute('dir', 'rtl'); else html.setAttribute('dir', 'ltr');
    // update language button label to show next language
    if (langToggle) {
      const next = langs[(langs.indexOf(lang) + 1) % langs.length];
      langToggle.textContent = next.toUpperCase();
    }
  }

  // Initialize language
  applyTranslations(langs[current]);

  // Nav toggle (mobile)
  if (toggle) {
    toggle.addEventListener('click', () => {
      if (nav) nav.classList.toggle('open');
    });
  }

  // Cycle language on button click
  if (langToggle) {
    langToggle.addEventListener('click', () => {
      current = (current + 1) % langs.length;
      const lang = langs[current];
      applyTranslations(lang);
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

  // Contact form (demo - no backend) with localized messages
  const form = document.getElementById('contactForm');
  if (form) {
    form.addEventListener('submit', e => {
      e.preventDefault();
      const data = new FormData(form);
      const name = (data.get('name') || '').toString().trim();
      const email = (data.get('email') || '').toString().trim();
      const message = (data.get('message') || '').toString().trim();
      const lang = langs[current];
      if (!name || !email || !message) {
        const msg = { ar: 'المرجو تعبئة الحقول المطلوبة', en: 'Please fill in the required fields', zh: '请填写必填字段' };
        alert(msg[lang]);
        return;
      }
      const recieved = { ar: 'تم استلام رسالتك. شكراً لتواصلك معنا — هذا نموذج تجريبي.', en: 'Your message has been received. Thank you — demo only.', zh: '已收到您的消息。谢谢 — 仅演示用。' };
      alert(recieved[lang]);
      form.reset();
    });
  }
});

