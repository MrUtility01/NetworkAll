# مخزن مرجع بسته‌های محتوایی — tools/packs/

این تنها مسیر مرجع برای **فایل‌های JSON محتوای آموزشی** است. اسکریپت‌های ساخت و اعتبارسنجی در پوشه‌های tools/engineer_jokar_* می‌مانند، اما JSON نهایی باید در یکی از زیرپوشه‌های این مسیر باشد.

| پوشه | دامنه | فایل اصلی |
|---|---|---|
| automation_python/ | Python و اتوماسیون شبکه/ویندوز | automation_python_curriculum_pack.json |
| security_ethical_hacking/ | امنیت سایبری دفاعی | security_ethical_hacking_pack.json |
| wireless_security/ | امنیت و طراحی WLAN | wireless_security_pack.json |
| routing_deep/ | Routing، OSPF، BGP، Redistribution و CLI | chapter_68_cisco_routing_1600.json، ospf_bgp_redistribution_deep_pack.json |
| vpn_enterprise/ | VPN، IPsec، SSL و عیب‌یابی | vpn_enterprise_ipsec_ssl_troubleshooting_pack.json |
| switching_routing/ | Switching و Routing | switching_routing_curriculum_pack.json |
| windows_server/ | Windows Server و سرویس‌های زیرساخت | windows_server_complete_curriculum_pack.json |
| commands_encyclopedia/ | مرجع دستورات Vendorها | cisco_switching.json، mikrotik.json |
| git_chapter64/ | کتاب/محتوای Git؛ منابع Markdown | Git_Chapter_64_Full.md |

## قوانین نگه‌داری

1. قبل از افزودن فایل، pack_catalog.json و schema مربوط را به‌روزرسانی کنید.
2. هیچ درس یا فصل کم‌عمقی را تنها به‌علت کوتاه بودن حذف نکنید؛ ابتدا شکاف محتوا را گزارش و سپس با UID پایدار بازنویسی یا با محتوای بهتر جایگزین کنید.
3. پرسش‌ها و کلید پاسخ باید جدا بمانند. آزمون خودکار باید تطابق ID سؤال و پاسخ، UID تکراری، JSON نامعتبر و رکوردهای ناقص را گزارش کند.
4. audit_pending یعنی ممیزی علمی/اجرایی هنوز ثبت نشده است؛ نه اینکه محتوا حتماً غلط باشد. هیچ بسته‌ای تا وقتی لابراتوار، خروجی مورد انتظار، عیب‌یابی و منابع آن بررسی نشده، verified محسوب نمی‌شود.
5. متن‌های حجیم به‌صورت فایل JSON در زمان اجرا بارگذاری می‌شوند؛ UI باید نتایج را صفحه‌بندی کند و فهرست‌ها را lazy-load کند. حجم فایل به‌خودی‌خود دلیل حذف محتوا نیست.

## ممیزی

برای ممیزی همه بسته‌ها، فرمان زیر را از ریشه مخزن اجرا کنید:

    python tools/audit_content.py --packs-only --json docs/audits/content-audit.json

اعتبارسنجی اختصاصی بسته Python:

    python tools/engineer_jokar_automation_python/validate_pack.py

گزارش کیفیت را قبل از ادغام بررسی کنید. جزئیات سیاست و دامنه‌ها در pack_catalog.json آمده است.
