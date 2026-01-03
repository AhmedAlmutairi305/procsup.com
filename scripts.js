diff --git a/scripts.js b/scripts.js
index 2e2313db851746614a3572f714605681a9eadb09..52c3332d3caab345f0eeac256a0108700d1b0b24 100644
--- a/scripts.js
+++ b/scripts.js
@@ -1,333 +1,440 @@
 // ===== Mobile Nav =====
 const navToggle = document.getElementById("navToggle");
 const navLinks = document.getElementById("navLinks");
 
 navToggle?.addEventListener("click", () => {
   const isOpen = navLinks.classList.toggle("show");
   navToggle.setAttribute("aria-expanded", String(isOpen));
 });
 
 // Close menu on link click (mobile)
 navLinks?.addEventListener("click", (e) => {
   if (e.target.tagName.toLowerCase() === "a") {
     navLinks.classList.remove("show");
     navToggle.setAttribute("aria-expanded", "false");
   }
 });
 
 // Footer year
 document.getElementById("year").textContent = new Date().getFullYear();
 
 // ===== i18n (EN / AR / ZH) =====
+const languageSwitcher = document.getElementById("languageSwitcher");
+
+const i18n = {
   en: {
     "meta.title": "Procsup | Procurement & Sourcing",
     "brand.name": "Procsup",
     "nav.home": "Home",
     "nav.about": "About",
     "nav.services": "Services",
     "nav.why": "Why Us",
     "nav.clients": "Clients",
     "nav.contact": "Contact",
 
     "hero.badge": "Procurement • Sourcing • Logistics",
     "hero.h1": "Your Trusted Procurement Partner",
     "hero.p": "End-to-end procurement solutions for institutions and businesses—supplier sourcing, negotiation, compliance, and delivery.",
+    "hero.cta1": "Explore Services",
+    "hero.cta2": "Request a Quote",
+    "hero.pill1": "Regional expertise",
+    "hero.pill2": "Cross-border compliance",
+    "hero.pill3": "On-time delivery",
+    "hero.stat1": "Verified suppliers",
+    "hero.stat2": "Support & tracking",
+    "hero.stat3": "Compliance focus",
+    "hero.cardTag": "Ready for Arabic & English",
+    "hero.logoPlaceholder": "Place your logo here",
+    "hero.cardTitle": "Quick Overview",
+    "hero.card1": "Supplier identification & vetting",
+    "hero.card2": "Procurement & contract management",
+    "hero.card3": "Shipping, customs, and final delivery",
+    "hero.card4": "Quality checks & documentation",
+    "hero.cardNote": "Tip: Replace the brand name, colors, and service bullets — everything else is ready.",
+    "hero.tag1": "Mobile friendly",
+    "hero.tag2": "Tablet ready",
+    "hero.tag3": "Desktop polished",
+
+    "highlight.h2": "Everything you need to look credible",
+    "highlight.p": "Clean layout, bilingual content, and modern CTA blocks.",
+    "highlight.f1t": "Bilingual by default",
+    "highlight.f1p": "Toggle instantly between English and Arabic with right-to-left support.",
+    "highlight.f2t": "Responsive grids",
+    "highlight.f2p": "Optimized layouts for phone, tablet, and desktop screens.",
+    "highlight.f3t": "Brand-ready",
+    "highlight.f3p": "Swap the logo slot, accent colors, and texts without changing the structure.",
+
+    "about.h2": "About Us",
+    "about.p1": "We help organizations purchase efficiently from global markets with clear processes and reliable supplier networks.",
+    "about.p2": "From sourcing to delivery, we provide a single point of contact—reducing risk, improving transparency, and saving time.",
+    "about.pill1": "Transparent",
+    "about.pill2": "Reliable",
     "about.pill3": "Compliance-first",
     "about.boxTitle": "What You Get",
     "about.b1t": "One Contract",
     "about.b1p": "Single invoice & clear scope.",
     "about.b2t": "Risk Control",
     "about.b2p": "Supplier vetting & documentation.",
     "about.b3t": "Delivery",
     "about.b3p": "Shipping, customs & last mile.",
     "about.b4t": "Support",
     "about.b4p": "Fast response and tracking.",
 
     "services.h2": "Services",
     "services.p": "Choose a service package or mix based on your needs.",
     "services.s1t": "Sourcing",
     "services.s1p": "Find verified suppliers, compare quotes, and match specifications.",
     "services.s1b1": "Supplier shortlist",
     "services.s1b2": "Samples & evaluation",
     "services.s1b3": "Factory checks (optional)",
     "services.s2t": "Procurement",
     "services.s2p": "Negotiation, purchase orders, contracts, and timeline management.",
     "services.s2b1": "Negotiation support",
     "services.s2b2": "Contract & PO management",
     "services.s2b3": "Quality documentation",
+    "services.s3t": "Logistics",
+    "services.s3p": "Shipping, customs clearance, insurance, and door-to-door delivery.",
+    "services.s3b1": "Freight options",
+    "services.s3b2": "Customs & compliance",
+    "services.s3b3": "Tracking & delivery",
+
+    "process.h2": "Clear, repeatable process",
+    "process.p": "From request to delivery, you have a single team and clear milestones.",
+    "process.s1t": "Discovery",
+    "process.s1p": "Requirements, specs, and timelines clarified.",
+    "process.s2t": "Sourcing & evaluation",
+    "process.s2p": "Supplier shortlist, samples, and compliance checks.",
+    "process.s3t": "Procurement",
+    "process.s3p": "Negotiation, contracts, and PO management.",
+    "process.s4t": "Logistics",
+    "process.s4p": "Shipping, customs, delivery, and tracking.",
+
+    "why.h2": "Why Choose Us",
+    "why.p": "Practical, predictable, and professional execution.",
+    "why.w1t": "Single Point of Contact",
+    "why.w1p": "One team handling procurement + logistics from start to finish.",
+    "why.w2t": "Compliance & Documentation",
     "why.w2p": "Paperwork and requirements handled clearly and on time.",
     "why.w3t": "Cost Transparency",
     "why.w3p": "Clear pricing structure with options that fit your budget.",
     "why.w4t": "Reliable Network",
     "why.w4p": "Vetted suppliers and repeatable workflows for consistency.",
 
     "clients.h2": "Clients",
     "clients.p": "A simple area to show sectors or key partners.",
     "clients.c1": "Government",
     "clients.c2": "Healthcare",
+    "clients.c3": "Education",
+    "clients.c4": "Construction",
+    "clients.c5": "Retail",
+
+    "cta.badge": "Ready to modernize",
+    "cta.title": "Ship a polished landing page this week.",
+    "cta.p": "Drop in your logo, adjust the palette, and publish a bilingual experience.",
+    "cta.cta1": "Book a call",
+    "cta.cta2": "Review services",
+
+    "contact.h2": "Contact",
+    "contact.p": "Tell us what you need, and we’ll respond with the next steps and timeline.",
+    "contact.emailLabel": "Email",
+    "contact.phoneLabel": "Phone",
+    "contact.locLabel": "Location",
     "contact.locVal": "Saudi Arabia",
 
     "form.name": "Name",
     "form.email": "Email",
     "form.msg": "Message",
     "form.submit": "Send",
     "form.note": "Later you can connect this form to EmailJS / Formspree / your backend.",
 
     "footer.rights": "All rights reserved.",
     "footer.top": "Back to top ↑"
   },
 
   ar: {
     "meta.title": "Procsup | المشتريات والتوريد",
     "brand.name": "Procsup",
     "nav.home": "الرئيسية",
     "nav.about": "من نحن",
     "nav.services": "الخدمات",
     "nav.why": "لماذا نحن",
     "nav.clients": "العملاء",
     "nav.contact": "تواصل معنا",
 
     "hero.badge": "مشتريات • توريد • لوجستيات",
     "hero.h1": "شريكك الموثوق في المشتريات",
     "hero.p": "حلول مشتريات متكاملة للجهات والمؤسسات—توريد الموردين، التفاوض، الامتثال، والتسليم.",
+    "hero.cta1": "استعرض الخدمات",
+    "hero.cta2": "اطلب عرض سعر",
+    "hero.pill1": "خبرة محلية",
+    "hero.pill2": "امتثال عابر للحدود",
+    "hero.pill3": "تسليم في الموعد",
+    "hero.stat1": "موردون موثوقون",
+    "hero.stat2": "دعم وتتبع",
+    "hero.stat3": "تركيز على الامتثال",
+    "hero.cardTag": "جاهز بالعربية والإنجليزية",
+    "hero.logoPlaceholder": "ضع شعارك هنا",
+    "hero.cardTitle": "نظرة سريعة",
+    "hero.card1": "تحديد الموردين والتحقق منهم",
+    "hero.card2": "إدارة المشتريات والعقود",
+    "hero.card3": "الشحن والتخليص والتسليم",
+    "hero.card4": "فحص الجودة والوثائق",
+    "hero.cardNote": "معلومة: غيّر الاسم والألوان ونص الخدمات — والباقي جاهز.",
+    "hero.tag1": "متوافق مع الجوال",
+    "hero.tag2": "مناسب للأجهزة اللوحية",
+    "hero.tag3": "مصمم لسطح المكتب",
+
+    "highlight.h2": "كل ما تحتاجه لتبدو احترافياً",
+    "highlight.p": "تصميم نظيف، محتوى ثنائي اللغة، وأزرار دعوة حديثة.",
+    "highlight.f1t": "ثنائي اللغة افتراضياً",
+    "highlight.f1p": "التبديل الفوري بين العربية والإنجليزية مع دعم الاتجاه.",
+    "highlight.f2t": "شبكات مرنة",
+    "highlight.f2p": "تخطيطات محسّنة للجوال والتابلت وسطح المكتب.",
+    "highlight.f3t": "جاهز للهوية",
+    "highlight.f3p": "استبدل مكان الشعار والألوان والنصوص دون تغيير الهيكل.",
+
+    "about.h2": "من نحن",
+    "about.p1": "نساعد الجهات في الشراء بكفاءة من الأسواق العالمية عبر إجراءات واضحة وشبكة موردين موثوقة.",
+    "about.p2": "من التوريد إلى التسليم، نوفر نقطة تواصل واحدة لتقليل المخاطر ورفع الشفافية وتوفير الوقت.",
+    "about.pill1": "شفافية",
     "about.pill2": "اعتمادية",
     "about.pill3": "امتثال أولاً",
     "about.boxTitle": "وش بتحصل؟",
     "about.b1t": "عقد واحد",
     "about.b1p": "فاتورة ونطاق واضح.",
     "about.b2t": "إدارة مخاطر",
     "about.b2p": "تحقق من الموردين والوثائق.",
     "about.b3t": "تسليم",
     "about.b3p": "شحن وتخليص وتوصيل.",
     "about.b4t": "دعم",
     "about.b4p": "استجابة سريعة وتتبع.",
 
     "services.h2": "الخدمات",
     "services.p": "اختر باقة خدمات أو ادمجها حسب احتياجك.",
     "services.s1t": "التوريد (Sourcing)",
     "services.s1p": "تحديد موردين موثوقين ومقارنة عروض الأسعار ومطابقة المواصفات.",
     "services.s1b1": "قائمة موردين مختصرة",
     "services.s1b2": "عينات وتقييم",
     "services.s1b3": "زيارة/فحص مصنع (اختياري)",
     "services.s2t": "المشتريات (Procurement)",
     "services.s2p": "تفاوض وأوامر شراء وعقود وإدارة جداول التنفيذ.",
     "services.s2b1": "دعم التفاوض",
     "services.s2b2": "إدارة العقود وأوامر الشراء",
     "services.s2b3": "وثائق الجودة",
+    "services.s3t": "اللوجستيات (Logistics)",
+    "services.s3p": "الشحن والتخليص الجمركي والتأمين والتوصيل حتى بابك.",
+    "services.s3b1": "خيارات شحن متعددة",
+    "services.s3b2": "جمارك وامتثال",
+    "services.s3b3": "تتبع وتسليم",
+
+    "process.h2": "إجراء واضح ومتكرر",
+    "process.p": "من الطلب إلى التسليم، فريق واحد ومراحل واضحة.",
+    "process.s1t": "اكتشاف",
+    "process.s1p": "توضيح المتطلبات والمواصفات والجداول.",
+    "process.s2t": "توريد وتقييم",
+    "process.s2p": "قائمة موردين وعينات وفحص الامتثال.",
+    "process.s3t": "مشتريات",
+    "process.s3p": "تفاوض وعقود وإدارة أوامر الشراء.",
+    "process.s4t": "لوجستيات",
+    "process.s4p": "شحن وتخليص وتسليم وتتبع.",
+
+    "why.h2": "لماذا نحن",
+    "why.p": "تنفيذ عملي وواضح واحترافي.",
+    "why.w1t": "نقطة تواصل واحدة",
+    "why.w1p": "فريق واحد يدير المشتريات واللوجستيات من البداية للنهاية.",
+    "why.w2t": "امتثال ووثائق",
     "why.w2p": "إدارة المتطلبات والأوراق بشكل واضح وفي الوقت.",
     "why.w3t": "شفافية تكلفة",
     "why.w3p": "تسعير واضح وخيارات تناسب ميزانيتك.",
     "why.w4t": "شبكة موثوقة",
     "why.w4p": "موردون تم التحقق منهم وإجراءات ثابتة.",
 
     "clients.h2": "العملاء",
     "clients.p": "مكان بسيط لعرض القطاعات أو الشركاء.",
     "clients.c1": "جهات حكومية",
     "clients.c2": "الرعاية الصحية",
+    "clients.c3": "التعليم",
+    "clients.c4": "الإنشاءات",
+    "clients.c5": "التجزئة",
+
+    "cta.badge": "جاهزون للتحديث",
+    "cta.title": "اطلق صفحة هبوط احترافية هذا الأسبوع.",
+    "cta.p": "أضف شعارك وغيّر الألوان وانشر تجربة ثنائية اللغة.",
+    "cta.cta1": "احجز اتصال",
+    "cta.cta2": "راجع الخدمات",
+
+    "contact.h2": "تواصل معنا",
+    "contact.p": "اكتب احتياجك وبنرد عليك بالخطوات والمدة المتوقعة.",
+    "contact.emailLabel": "البريد",
+    "contact.phoneLabel": "الجوال",
+    "contact.locLabel": "الموقع",
     "contact.locVal": "السعودية",
 
     "form.name": "الاسم",
     "form.email": "البريد الإلكتروني",
     "form.msg": "الرسالة",
     "form.submit": "إرسال",
     "form.note": "لاحقاً تقدر تربط النموذج بـ EmailJS / Formspree أو سيرفرك.",
 
     "footer.rights": "جميع الحقوق محفوظة.",
     "footer.top": "للأعلى ↑"
   },
 
   zh: {
     "meta.title": "Procsup | 采购与供应链",
     "brand.name": "Procsup",
     "nav.home": "首页",
     "nav.about": "关于我们",
     "nav.services": "服务",
     "nav.why": "为什么选择我们",
     "nav.clients": "客户",
     "nav.contact": "联系我们",
 
     "hero.badge": "采购 • 供应 • 物流",
     "hero.h1": "值得信赖的采购合作伙伴",
     "hero.p": "为机构与企业提供端到端采购解决方案：供应商寻源、谈判、合规与交付。",
+    "hero.cta1": "查看服务",
+    "hero.cta2": "获取报价",
+    "hero.pill1": "本地化优势",
+    "hero.pill2": "跨境合规",
+    "hero.pill3": "准时交付",
+    "hero.stat1": "优质供应商",
+    "hero.stat2": "支持与追踪",
+    "hero.stat3": "合规优先",
+    "hero.cardTag": "支持中英/阿语",
+    "hero.logoPlaceholder": "在此放置你的标志",
+    "hero.cardTitle": "快速概览",
+    "hero.card1": "供应商筛选与审核",
+    "hero.card2": "采购与合同管理",
+    "hero.card3": "运输、清关与交付",
+    "hero.card4": "质量检查与文件",
+    "hero.cardNote": "提示：只需替换品牌名、颜色和服务文案即可上线。",
+    "hero.tag1": "移动端友好",
+    "hero.tag2": "平板端适配",
+    "hero.tag3": "桌面端精致",
+
+    "highlight.h2": "帮你快速建立可信形象",
+    "highlight.p": "简洁布局、双语内容和现代行动按钮。",
+    "highlight.f1t": "默认双语",
+    "highlight.f1p": "英文与阿文一键切换，含 RTL 支持。",
+    "highlight.f2t": "自适应网格",
+    "highlight.f2p": "为手机、平板和桌面优化的布局。",
+    "highlight.f3t": "品牌就绪",
+    "highlight.f3p": "替换标志位与主色，无需改动结构。",
+
+    "about.h2": "关于我们",
+    "about.p1": "我们通过清晰流程与可靠供应商网络，帮助组织高效对接全球市场。",
+    "about.p2": "从寻源到交付，我们提供单一对接窗口，降低风险并提升透明度。",
+    "about.pill1": "透明",
     "about.pill2": "可靠",
     "about.pill3": "合规优先",
     "about.boxTitle": "你将获得",
     "about.b1t": "一份合同",
     "about.b1p": "发票与范围清晰。",
     "about.b2t": "风险控制",
     "about.b2p": "供应商审核与文件。",
     "about.b3t": "交付",
     "about.b3p": "运输、清关与末端配送。",
     "about.b4t": "支持",
     "about.b4p": "快速响应与追踪。",
 
     "services.h2": "服务",
     "services.p": "可选择单项服务或组合方案。",
     "services.s1t": "寻源",
     "services.s1p": "筛选可靠供应商，对比报价并匹配规格。",
     "services.s1b1": "供应商清单",
     "services.s1b2": "样品与评估",
     "services.s1b3": "工厂审核（可选）",
     "services.s2t": "采购",
     "services.s2p": "谈判、订单、合同与交期管理。",
     "services.s2b1": "谈判支持",
     "services.s2b2": "合同与订单管理",
     "services.s2b3": "质量文件",
+    "services.s3t": "物流",
+    "services.s3p": "运输、清关、保险与门到门交付。",
+    "services.s3b1": "多种运输方案",
+    "services.s3b2": "清关与合规",
+    "services.s3b3": "追踪与交付",
+
+    "process.h2": "清晰且可复制的流程",
+    "process.p": "从需求到交付，一个团队负责并有明确里程碑。",
+    "process.s1t": "需求澄清",
+    "process.s1p": "确认要求、规格与时间。",
+    "process.s2t": "寻源与评估",
+    "process.s2p": "供应商清单、样品与合规检查。",
+    "process.s3t": "采购执行",
+    "process.s3p": "谈判、合同与订单管理。",
+    "process.s4t": "物流交付",
+    "process.s4p": "运输、清关、交付与追踪。",
+
+    "why.h2": "为什么选择我们",
+    "why.p": "可执行、可预期、专业交付。",
+    "why.w1t": "单一对接窗口",
+    "why.w1p": "一个团队贯穿采购与物流全流程。",
+    "why.w2t": "合规与文件",
     "why.w2p": "文件与要求按时、清晰交付。",
     "why.w3t": "成本透明",
     "why.w3p": "定价结构清晰，方案灵活。",
     "why.w4t": "可靠网络",
     "why.w4p": "审核供应商与标准化流程保障一致性。",
 
     "clients.h2": "客户",
     "clients.p": "用于展示行业或关键合作伙伴。",
     "clients.c1": "政府",
     "clients.c2": "医疗",
+    "clients.c3": "教育",
+    "clients.c4": "建筑",
+    "clients.c5": "零售",
+
+    "cta.badge": "随时升级",
+    "cta.title": "一周内上线精致着陆页。",
+    "cta.p": "放入你的 Logo，调整配色，发布双语体验。",
+    "cta.cta1": "预约沟通",
+    "cta.cta2": "查看服务",
+
+    "contact.h2": "联系我们",
+    "contact.p": "告诉我们你的需求，我们会回复下一步与时间计划。",
+    "contact.emailLabel": "邮箱",
+    "contact.phoneLabel": "电话",
     "contact.locLabel": "地区",
     "contact.locVal": "沙特阿拉伯",
 
     "form.name": "姓名",
     "form.email": "邮箱",
     "form.msg": "留言",
     "form.submit": "发送",
     "form.note": "后续可接入 EmailJS / Formspree 或你的后端。",
 
     "footer.rights": "版权所有。",
     "footer.top": "返回顶部 ↑"
+  }
+};
+
+function setLanguage(lang) {
+  // direction + lang
   document.documentElement.lang = lang;
   document.documentElement.dir = (lang === "ar") ? "rtl" : "ltr";
 
   // Apply translations
   document.querySelectorAll("[data-i18n]").forEach(el => {
     const key = el.getAttribute("data-i18n");
     const value = i18n?.[lang]?.[key];
     if (value) el.textContent = value;
   });
 
   // Persist
+  localStorage.setItem("site_lang", lang);
+}
+
+const saved = localStorage.getItem("site_lang") || "en";
+
+if (languageSwitcher) {
+  languageSwitcher.value = saved;
+  setLanguage(saved);
+
+  languageSwitcher.addEventListener("change", (e) => {
+    setLanguage(e.target.value);
+  });
+} else {
+  setLanguage(saved);
+}
