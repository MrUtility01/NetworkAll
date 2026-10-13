# پرامپت مستقل قابل بارگذاری — فصل 68: دانشنامه جامع دستورات

مخزن هدف: https://github.com/MrUtility01/NetworkAll
شماره فصل: 68
عنوان مطابق curriculum: دانشنامه جامع دستورات
شاخه کاری: codex/android-repair-port86-20261013

## هدف فصل
این فصل باید مرجع عملی و قابل جست‌وجوی فرمان‌های مدیریت، پیکربندی، عیب‌یابی و اتوماسیون باشد. نحو پلتفرم‌ها هرگز با هم مخلوط نشود:

1. Cisco IOS / IOS-XE: switching، VLAN، trunk، STP، EtherChannel، interface، routing، static route، OSPF، BGP، ACL، NAT، prefix-list، route-map، redistribution، QoS، telemetry، logs، backup/restore و عیب‌یابی.
2. MikroTik RouterOS v6/v7: تفاوت نسخه‌ها، interface، bridge/VLAN، IP، routes، DHCP، DNS، firewall filter/NAT، connection tracking، queues، wireless، VPN، routing protocols، logs، backup/export، Safe Mode و rollback.
3. PowerShell 5.1 و 7+: تفاوت سازگاری، object pipeline، Get/Set/Test، شبکه، DNS، سرویس، process، event log، فایل، ACL، remoting، CIM، error handling، functions، modules، scheduled tasks و automation.
4. Windows CMD: دستورات داخلی/خارجی، شبکه، فایل، سرویس، process، log، share، permission، diagnostics و exit code.
5. Windows Batch: پارامترها، quoting، errorlevel، delayed expansion، setlocal/endlocal، for /f، if، call، goto، logging، error handling، idempotency، safe cleanup و Task Scheduler.
6. Linux: ابزارهای POSIX و ابزارهای رایج توزیع‌ها؛ وابستگی به coreutils/iproute2/systemd/apt/dnf و مانند آن مشخص شود.
7. Bash: quoting، expansion، arrays، pipes/redirection، traps، functions، exit status، set -euo pipefail با محدودیت‌ها، logging، SSH، systemd، cron و automation امن.

## تعداد و عمق اجباری
- هدف Cisco Routing: حداقل ۱۶۰۰ رکورد فرمان مستقل و معتبر در بستهٔ تخصصی Cisco Routing. هر رکورد باید تفاوت واقعی در کاربرد، syntax، حالت اجرا، نسخه یا سناریو داشته باشد. رکورد کپی‌شده با عنوان متفاوت، پارامتر تصادفی یا خروجی ساختگی برای افزایش تعداد ممنوع است. تعداد واقعی و رکوردهای ردشده در VALIDATION.md ثبت شود.
- برای MikroTik، PowerShell، Windows Batch/CMD و Linux/Bash بستهٔ مستقل و قابل گسترش ساخته شود؛ تا شمارش واقعی فایل و validator، تکمیل اعلام نشود.
- حداقل ۵۰ مثال مستقل، ۵۰ سناریو، ۵۰ سؤال آزمون و answer_key جدا با IDهای مشترک؛ هرکدام به فرمان/درس واقعی ارجاع دهد.
- نمودار مباحث اصلی با Mermaid، SVG، manifest، lesson_uid و متن جایگزین.
- منابع دقیق و واقعی: Cisco Configuration Guides/Command References، MikroTik RouterOS documentation، Microsoft Learn، Windows commands documentation، GNU manuals و man-pages.
- محتوای تازه تا بازبینی انسانی دارای source_status=review_required باشد.

## قرارداد هر رکورد
فیلدها تا حد مربوط: uid، vendor، platform، version_scope، privilege، category، subcategory، command، syntax، arguments، prerequisites_fa، steps_fa، sample_output، output_fields_fa، when_to_use_fa، common_mistakes_fa، security_notes_fa، lab_hint_fa، verify_steps_fa، rollback_fa، related_commands، search_keywords، source_urls، assessment.

هر درس باید کاربرد و عدم کاربرد، پیش‌نیاز، privilege، syntax، اثر جانبی، خروجی و تفسیر، verify، failure modes، امنیت، مثال حل‌شده، لابراتوار، rollback و واژه‌نامه داشته باشد. خروجی نمونه با «نمونه آموزشی» برچسب بخورد مگر مستند رسمی داشته باشد.

## ایمنی و کیفیت
- فرمان‌های تغییردهنده شبکه، firewall، route، ACL، disk، service و account باید اثر و rollback داشته باشند.
- لاب‌ها با آدرس‌های مستندسازی مانند 192.0.2.0/24 و محیط مجازی ایزوله طراحی شوند؛ تغییر production بدون change plan توصیه نشود.
- هیچ رمز، token، کلید خصوصی یا داده حساس واقعی وارد مخزن نشود.
- UIDها پایدار باشند؛ محتوای موجود حذف/overwrite نشود. قبل از ادغام، UID collision و duplicate command گزارش شود.

## خروجی‌ها
- tools/packs/commands_encyclopedia/cisco_routing.json
- tools/packs/commands_encyclopedia/mikrotik.json و بسته‌های افزایشی RouterOS
- tools/packs/commands_encyclopedia/powershell.json
- tools/packs/commands_encyclopedia/windows_batch.json
- tools/packs/commands_encyclopedia/linux.json
- مثال‌ها، سناریوها، سؤال‌ها، answer_key، منابع و manifest نمودارها
- VALIDATION.md با تعداد واقعی به تفکیک پلتفرم/نسخه، UID یکتا، duplicate command، تطبیق سؤال/پاسخ، منابع و موارد نیازمند بازبینی.

پس از هر مرحله یک commit مستقل با شرح دقیق ثبت کن. ساخت موفق APK یا تکمیل محتوا را بدون خروجی واقعی آن مرحله ادعا نکن.
