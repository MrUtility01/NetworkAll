# فصل ۶۸ — دانشنامه دستورات همه حوزه‌ها

وضعیت: **review_required**؛ این وضعیت عمداً تا اجرای validator و بررسی فنی/ساخت برنامه حفظ می‌شود.

## Inventory محتوای مرجع

- بسته‌های قبلی: ۳۶۰۰ رکورد دستوری در ۸ حوزه؛ حفظ شده‌اند.
- افزونهٔ جدید: ۷۵ رکورد اولیه در ۱۵ فناوری (هر فناوری ۵ رکورد).
- مجموع مرجع دستورات اعلام‌شده: ۳۶۷۵ رکورد.
- سؤال‌های آزمون بستهٔ قبلی: ۱۱۲۰؛ سؤال/پاسخ‌های assessment جاسازی‌شده در افزونه: ۷۵.
- مجموع سؤال‌های اعلام‌شده با احتساب assessmentهای افزونه: ۱۱۹۵.
- شناسه‌های UID در بستهٔ جدید به‌صورت domain-prefixed ساخته شده‌اند؛ یکتایی کل فهرست باید در خروجی ادغام نیز دوباره آزموده شود.
- اعتبارسنجی JSON: بستهٔ افزونه به‌صورت JSON پارس شده و فایل روی شاخهٔ main ثبت شده است.
- **هنوز اجرا نشده:** اجرای merger روی مخزن کامل، تست schema نهایی، آزمون جستجو، اجرای build اندروید/ویندوز و بازبینی syntax تمام فناوری‌ها.

## فناوری‌های افزوده‌شده

| فناوری | رکورد اولیه | وضعیت |
|---|---:|---|
| SSH / OpenSSH | ۵ | نیازمند تکمیل و بازبینی نسخه‌ای |
| Telnet / آزمون TCP | ۵ | نیازمند تکمیل؛ هشدار روشن دربارهٔ رمزنگاری‌نشدن Telnet |
| FTP / FTPS / SFTP | ۵ | نیازمند تکمیل؛ پروتکل‌ها تفکیک شده‌اند |
| VoIP / SIP / PBX | ۵ | نیازمند بازبینی نسخه و PJSIP/chan_sip |
| VMware ESXi / vSphere | ۵ | نیازمند بازبینی نسخه |
| Zabbix | ۵ | نیازمند بازبینی نسخه |
| Wireshark / TShark | ۵ | نیازمند بازبینی syntax/مجوز capture |
| Juniper Junos | ۵ | نیازمند بازبینی مدل و release |
| Aruba AOS-CX | ۵ | نیازمند بازبینی مدل و release |
| Proxmox VE | ۵ | نیازمند بازبینی نسخه |
| Ansible | ۵ | نیازمند بازبینی نسخه/module |
| Terraform | ۵ | نیازمند بازبینی provider/version |
| Kubernetes / kubectl | ۵ | نیازمند بازبینی API/version |
| PowerShell | ۵ | نیازمند تفکیک دقیق Windows PowerShell 5.1 و PowerShell 7+ |
| Microsoft Hyper-V | ۵ | نیازمند بازبینی edition/module |

## فایل‌های فرمان بستهٔ قبلی

| فایل | رکورد |
|---|---:|
| `commands_fortigate.json` | ۵۰۰ |
| `commands_windows.json` | ۵۰۰ |
| `commands_cisco.json` | ۵۰۰ |
| `commands_docker.json` | ۳۰۰ |
| `commands_mikrotik.json` | ۵۰۰ |
| `commands_windows_server.json` | ۳۰۰ |
| `commands_windows_batch.json` | ۵۰۰ |
| `commands_linux.json` | ۵۰۰ |
| **جمع بستهٔ قبلی** | **۳۶۰۰** |
| `commands_additional_technologies.json` | **۷۵** |
| **جمع مرجع** | **۳۶۷۵** |

## هشدارهای مهم

- `commands_windows.json` قبلاً جابه‌جایی آشکار فیلدهای `vendor/platform/category/title/command` داشته است. نگاشت خودکار، جایگزین بازبینی syntax و سطح ریسک نیست.
- اصلاح خودکار UID فقط از برخورد شناسه جلوگیری می‌کند؛ معادل یکتایی معنایی دستورها نیست.
- تعداد ۵ رکورد برای هر فناوری جدید، **شروع غنی‌سازی است و تکمیل فناوری محسوب نمی‌شود**. قرارداد هدف در `AUTHORING_TARGETS_FA.md` حداقل ۵۰۰ مرجع، ۱۰۰ مثال، ۱۰۰ سناریو و ۵۰۰ واحد یادگیری برای هر فناوری تعیین کرده است.
- قبل از اعلام `validated` باید JSON/schema، UIDها، سؤال/پاسخ، duplicate معنایی، syntax رسمی، جستجو و ساخت/نمایش Windows و Android آزموده شوند.
