document.getElementById('language-switcher').addEventListener('change', function(e) {
    const language = e.target.value;

    if (language === 'ar') {
        // Load Arabic content (this is a simplified version for demonstration)
        document.body.setAttribute('dir', 'rtl');
        document.querySelector('h1').innerText = 'مرحباً بكم في خدماتنا للتوريدات';
        document.querySelector('p').innerText = 'شريكك الموثوق للبحث والتوريد والخدمات اللوجستية.';
    } else if (language === 'zh') {
        // Load Chinese content (simplified)
        document.body.setAttribute('dir', 'ltr');
        document.querySelector('h1').innerText = '欢迎来到我们的采购服务';
        document.querySelector('p').innerText = '您值得信赖的采购、物流合作伙伴。';
    } else {
        // Default to English
        document.body.setAttribute('dir', 'ltr');
        document.querySelector('h1').innerText = 'Welcome to Our Procurement Services';
        document.querySelector('p').innerText = 'Your trusted partner for sourcing, procurement, and logistics solutions.';
    }
});
