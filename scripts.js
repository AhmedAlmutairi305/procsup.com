// لغة الموقع الافتراضية هي الإنجليزية
const translations = {
    en: {
        home: "Welcome to Our Procurement Services",
        about: "About Us",
        services: "Our Services",
        sourcing: "Sourcing",
        procurement: "Procurement",س
        logistics: "Logistics",
        clients: "Our Clients",
        compliance: "Compliance & Certifications",
        contact: "Contact Us",
        submit: "Submit"
    },
    ar: {
        home: "مرحبًا بكم في خدماتنا للتوريدات",
        about: "من نحن",
        services: "خدماتنا",
        sourcing: "التوريد",
        procurement: "المشتريات",
        logistics: "اللوجستيات",
        clients: "عملائنا",
        compliance: "التوافق والشهادات",
        contact: "اتصل بنا",
        submit: "إرسال"
    },
    zh: {
        home: "欢迎来到我们的采购服务",
        about: "关于我们",
        services: "我们的服务",
        sourcing: "采购来源",
        procurement: "采购",
        logistics: "物流",
        clients: "我们的客户",
        compliance: "合规与认证",
        contact: "联系我们",
        submit: "提交"
    }
};

// تحديث النصوص بناءً على اللغة المختارة
document.getElementById('language-switcher').addEventListener('change', function(e) {
    const selectedLang = e.target.value;
    const textElements = document.querySelectorAll('[data-translate]');

    textElements.forEach(el => {
        const translationKey = el.getAttribute('data-translate');
        if (translations[selectedLang] && translations[selectedLang][translationKey]) {
            el.innerText = translations[selectedLang][translationKey];
        }
    });
});
