# فصل ۶۸: دانشنامه جامع دستورات و عملیات سیستم

این فصل، مرجع عملیاتی چندسکویی برای مدیریت شبکه و سیستم‌عامل است.

## دانشنامه enrichment (جدید)

- **فایل ZIP:** `ch68_all_domains.zip`
- **مسیر استخراج:** `commands/sources/encyclopedia/`
- **اسکریپت:** `commands/sources/encyclopedia/EXTRACT.sh`

```bash
cd tools/chapters/68
bash commands/sources/encyclopedia/EXTRACT.sh
# یا:
unzip -o ch68_all_domains.zip
mkdir -p commands/sources/encyclopedia
cp -r ch68_commands_encyclopedia/* commands/sources/encyclopedia/
# پاک‌سازی مسیر تو در توی اشتباه:
rm -rf commands/sources/tools
```

| حوزه | تعداد |
|------|--------|
| Linux | 500 |
| Windows PowerShell | 500 |
| Windows Batch/CMD | 500 |
| Cisco IOS-XE | 500 |
| MikroTik | 500 |
| FortiGate | 500 |
| Docker | 300 |
| Windows Server/AD | 300 |
| **جمع دستورات SCHEMA** | **3600** |
| آزمون کاربرد دستور در ZIP قبلی | **1120** |
| افزونهٔ فناوری‌های تکمیلی (خارج از ZIP) | **150** |
| **جمع مرجع‌های دستوری فعلی** | **3750** |
| assessmentهای جاسازی‌شده در افزونه | **150** |
| **جمع سؤال/پاسخ با احتساب افزونه** | **1270** |

هر رکورد شامل: vendor، category، when_to_use_fa، flashcards، assessment (دستور→کاربرد).

## محتوای canonical قبلی

- `lessons/base_curriculum.json`: ۱۴ مسیر/درس پایه
- `lessons/lessons.json`: محتوای افزودهٔ قبلی
- `commands/commands.json`: ۳٬۰۴۶ رکورد موجود (حفظ شود؛ overwrite نشود)
- `examples/examples.json`: ۳٬۰۴۶ رکورد
- `questions/questions.json` / `answers/answer_key.json`: ۵۱ سؤال/پاسخ قبلی
- `labs/labs.json`: ۱۸ لاب

## ایمنی

- فقط Lab / با مجوز
- secret در لاگ ذخیره نشود
- فایروال را سراسری خاموش نکنید

## سازگاری

`build/chapter.json` را دستی ویرایش نکنید. `manifest.json` شمارش encyclopedia را دارد. status enrichment: review_required


## اصلاح ساختار دسته‌بندی و جستجو (اکتبر ۲۰۲۶)

علت نمایش نام‌های عمومی «زیرفصل N» این بود که مرحلهٔ تبدیل محتوا برای رکوردهای دستورات نام بخش معنادار تولید نمی‌کرد و فایل مرجع قدیمی `commands/commands.json` نیز در قالب `items[].fields.commands` بیشتر فقط متن دستور را نگه می‌داشت.

### نام بخش‌ها در برنامه

1. مبانی و اطلاعات دستگاه
2. رابط‌ها و وضعیت پورت‌ها
3. VLAN و Switching
4. Routing و جدول مسیریابی
5. ACL و کنترل دسترسی
6. NAT و ترجمه آدرس
7. DHCP و DNS
8. VPN و تونل‌ها
9. لاگ، مانیتورینگ و عیب‌یابی
10. پیکربندی، ذخیره‌سازی و مدیریت تغییر
11. امنیت و کاربران
12. سایر دستورات و ابزارها

هر دستور هنگام ساخت فهرست اندروید به بخش مربوطه دسته‌بندی می‌شود. عنوان دستور بدون پیشوند سطح آموزشی `[L1]` نمایش داده می‌شود. متن درس شامل دستور، توضیح کاربرد، مراحل بررسی، نکته ایمنی و کلیدواژه‌های فارسی/انگلیسی است تا جستجو بر اساس نام دستور، کاربرد یا دسته قابل انجام باشد. برای دستورات رایج، توضیح اختصاصی و برای سایر موارد توضیح مبتنی بر دسته تولید می‌شود.

### بازسازی فهرست برنامه

از ریشهٔ مخزن اجرا شود:

```bash
python scripts/merge_content_packs_into_android.py
```

سپس اجرای تست‌ها و ساخت Android/Windows را از طریق CI انجام دهید. فایل `android/app/src/main/assets/curriculum_index.json.gz` خروجی تولیدی است؛ آن را دستی ویرایش نکنید. فایل‌های مرجع و بستهٔ ZIP موجود حفظ می‌شوند.


## قرارداد غنی‌سازی عمیق و سهمیه‌های هدف

سند الزامات رسمی محتوا: [`AUTHORING_TARGETS_FA.md`](AUTHORING_TARGETS_FA.md). برای هر فناوری اصلی (MikroTik، Cisco، Windows Batch، PowerShell، VoIP، FortiGate، VMware ESXi، SSH، Telnet، FTP/SFTP و Bash) هدف جداگانه تعریف شده است: حداقل ۵۰۰ مرجع دستور/گزینه، ۱۰۰ مثال، ۱۰۰ سناریو و ۵۰۰ واحد یادگیری. این سهمیه‌ها هدف هستند و تا وقتی validator تعداد رکوردهای واقعی و متمایز را تأیید نکند، نباید به‌عنوان تکمیل‌شده گزارش شوند.

در مورد SSH/Telnet/FTP، رکوردها باید بر اساس کلاینت/سرور و پیاده‌سازی مشخص باشند؛ گزینه‌ها نباید به‌صورت صوری برای افزایش شمار ساخته شوند. SFTP باید از FTP/FTPS تفکیک شود. هر دستور باید آرگومان‌ها، محل اجرا، سطح دسترسی، نسخه/پلتفرم، مثال، خروجی/روش بررسی، ریسک و کلیدواژه‌های جستجو را داشته باشد. حجم برنامه محدودیتی برای این پروژه نیست؛ حفظ محتوای فعلی اولویت دارد.


## افزونهٔ فناوری‌های تکمیلی (۱۷ اکتبر ۲۰۲۶)

فایل افزایشی `commands/sources/encyclopedia/commands_additional_technologies.json` به مخزن اضافه شده است: **۱۵۰ رکورد اولیه در ۱۵ حوزه**: SSH/OpenSSH، Telnet، FTP/FTPS/SFTP، VoIP/SIP/PBX، VMware ESXi، Zabbix، Wireshark/TShark، Juniper Junos، Aruba AOS-CX، Proxmox VE، Ansible، Terraform، Kubernetes، PowerShell و Hyper-V.

اسکریپت `scripts/merge_content_packs_into_android.py` اکنون این فایل را نیز می‌خواند و فناوری‌های افزوده را در بخش‌های مجزای فصل ۶۸ قرار می‌دهد. برای بازسازی خروجی تولیدی، از ریشهٔ مخزن اجرا کنید:

```bash
python scripts/merge_content_packs_into_android.py
```

**مهم:** ۱۰ رکورد در هر فناوری صرفاً نقطهٔ شروع است؛ هیچ‌یک از این ۱۵ فناوری هنوز به سهمیهٔ کامل قرارداد `AUTHORING_TARGETS_FA.md` نرسیده است. build و تست runtime پس از تغییر هنوز اجرا/تأیید نشده‌اند. محتوای موجود و ZIP قبلی حذف نشده‌اند.
