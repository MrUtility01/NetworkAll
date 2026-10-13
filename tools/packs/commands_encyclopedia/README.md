# JSON دانشنامه دستورات — NetworkAll فصل ۶۸

این پوشه شامل بسته‌های واقعی ورودی برای merge به فهرست آموزشی است. رکوردهای جدید با `source_status=review_required` باقی می‌مانند تا بازبینی تخصصی انجام شود.

## بسته‌های مستقل افزوده‌شده در مرحله اول

- `cisco_routing.json` — ۳۰ فرمان Cisco IOS-XE در حوزه routing، ACL، NAT و verification.
- `cisco_switching.json` — ۲۰ فرمان Cisco switching برای VLAN، STP، EtherChannel، PoE و عیب‌یابی لایه ۲.
- `mikrotik_ops_addon.json` — ۲۰ فرمان افزایشی MikroTik RouterOS v7.
- `powershell.json` — ۲۰ فرمان PowerShell برای شبکه، سرویس، لاگ، فایل و اتوماسیون.
- `windows_batch.json` — ۲۰ نمونه Windows Batch/CMD برای کنترل خطا، فایل، logging و job.
- `linux.json` — ۲۰ فرمان Linux برای شبکه، DNS، سرویس، storage، process و logs.

مجموع این مرحله ۱۳۰ رکورد فرمان تازه است؛ این تعداد به معنی تکمیل کل دانشنامه نیست. هدف Cisco Routing برابر ۱۶۰۰ رکورد مستقل است و فعلاً ۳۰ رکورد از آن هدف ثبت شده است.

## فایل‌های جانبی آموزشی

- `ch68_examples.json` — ۵۰ مثال عملی
- `ch68_scenarios.json` — ۵۰ سناریوی لابراتوری و RCA
- `ch68_questions.json` — ۵۰ سؤال چهارگزینه‌ای؛ پاسخ صحیح در این فایل نیست
- `ch68_answer_key.json` — پاسخ‌نامه مستقل با IDهای مشترک
- `ch68_sources.json` — ۱۷ URL رسمی/سازمانی یکتا برای شروع بازبینی
- `VALIDATION.md` — شمارش واقعی و محدودیت‌ها

## بسته‌های قدیمی که حفظ شده‌اند

- `mikrotik.json` — ۲۰ lesson با schema قدیمی‌تر
- `networkall_shell_automation.json` — ۱۲ رکورد ترکیبی
- `networkall_ops_advanced.json` — ۶ رکورد عملیات/عیب‌یابی
- `networkall_shell_expanded.json` — ۵۰ رکورد ترکیبی Linux، Bash، PowerShell، Windows CMD و Windows Batch

## ساخت و اعتبارسنجی

از ریشهٔ مخزن:

```bash
python scripts/export_android_index.py
python scripts/merge_content_packs_into_android.py
python scripts/validate_ch68_command_packs.py
python scripts/validate_android_curriculum.py
```

Workflow اندروید اکنون باید اعتبارسنجی مستقل بسته‌های فصل ۶۸ را قبل از build اجرا کند. نتیجه CI باید پس از آخرین commitها بررسی شود؛ در این گزارش هنوز اجرای جدید CI تأیید نشده است.

## معیار کیفیت

نحو و رفتار فرمان باید با نسخه دقیق Cisco IOS-XE، RouterOS، PowerShell، Windows یا توزیع Linux تطبیق داده شود. نمونه خروجی‌های بسته‌های تازه آموزشی‌اند، نه خروجی تضمین‌شده همه دستگاه‌ها. دستورات تغییردهنده باید در لاب یا پس از change approval اجرا شوند و rollback مستند داشته باشند.
