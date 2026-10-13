# JSON دانشنامه دستورات — NetworkAll فصل ۶۸

این پوشه بسته‌های ورودی برای ادغام افزایشی در curriculum را نگه می‌دارد. رکوردهای جدید با `source_status=review_required` هستند تا بازبینی تخصصی syntax، نسخه و رفتار واقعی انجام شود.

## شمارش واقعی بسته‌های فرمان مستقل

- **Cisco IOS-XE Routing: ۱۶۰۰ رکورد** در `cisco_routing.json` و `cisco_routing_addon_01.json` تا `cisco_routing_addon_08.json`.
- **Cisco Switching: ۲۰ رکورد** در `cisco_switching.json`.
- **MikroTik RouterOS v7: ۱۴۳ رکورد** در `mikrotik_ops_addon.json` و `mikrotik_ops_addon_02.json`.
- **PowerShell: ۱۴۹ رکورد** در `powershell.json` و `powershell_addon_01.json`.
- **Windows Batch: ۲۰ رکورد** در `windows_batch.json`.
- **Linux: ۲۰ رکورد** در `linux.json`.

جمع بسته‌های مستقل بالا **۱۹۵۲ رکورد فرمان** است. رکوردهای قدیمی/ترکیبی در این جمع نیستند تا شمارش دوباره رخ ندهد.

## آزمون‌ها و مواد تمرینی

- `ch68_examples.json` — ۵۰ مثال عملی
- `ch68_scenarios.json` — ۵۰ سناریوی لابراتوری و RCA
- `ch68_questions.json` و `ch68_answer_key.json` — ۵۰ سؤال عمومی و پاسخ‌نامه مستقل
- `cisco_routing_exam.json` و `cisco_routing_exam_answer_key.json` — ۲۵ سؤال پایه Cisco Routing / ACL / NAT؛ به‌علاوه addon با ۲۰ سؤال
- `routeros_exam.json` و `routeros_exam_answer_key.json` — ۳۰ سؤال پایه RouterOS v7؛ به‌علاوه addon با ۲۰ سؤال
- `powershell_exam.json` و `powershell_exam_answer_key.json` — ۲۱ سؤال پایه PowerShell؛ به‌علاوه addon با ۲۰ سؤال
- `ch68_sources.json` — منابع رسمی/سازمانی برای بازبینی
- `VALIDATION.md` — گزارش شمارش، معیارهای ساختاری و محدودیت‌ها

مجموع آزمون‌های تخصصی فعلی **۱۳۶ سؤال و ۱۳۶ پاسخ مستقل** است؛ آزمون عمومی فصل ۶۸ نیز جداگانه ۵۰ سؤال و ۵۰ پاسخ دارد. شناسهٔ سؤال‌ها و پاسخ‌ها باید یکسان باشد و پاسخ صحیح داخل فایل سؤال‌ها ذخیره نمی‌شود.

## بسته‌های قدیمی که حفظ شده‌اند

- `mikrotik.json` — ۲۰ lesson با schema قدیمی‌تر
- `networkall_shell_automation.json` — ۱۲ رکورد ترکیبی
- `networkall_ops_advanced.json` — ۶ رکورد عملیات/عیب‌یابی
- `networkall_shell_expanded.json` — ۵۰ رکورد ترکیبی Linux، Bash، PowerShell، Windows CMD و Windows Batch

این بسته‌های قدیمی جدا از شمار ۱۹۵۲ گزارش می‌شوند؛ schema متفاوت آن‌ها نیازمند ممیزی مستقل است.

## ساخت و اعتبارسنجی

از ریشهٔ مخزن:

```bash
python3 scripts/validate_ch68_command_packs.py
python3 scripts/export_android_index.py
python3 scripts/merge_content_packs_into_android.py
python3 scripts/validate_android_curriculum.py
```

Workflow اندروید اعتبارسنجی مستقل فصل ۶۸ را پیش از ساخت APK اجرا می‌کند. وضعیت آخرین اجرای CI را از [GitHub Actions](https://github.com/MrUtility01/NetworkAll/actions) بررسی کنید؛ موفقیت اعتبارسنجی JSON به‌تنهایی به معنی APK نصب‌شده و آزمایش‌شده روی گوشی نیست.

## معیار کیفیت

نحو و رفتار فرمان باید با نسخه دقیق Cisco IOS-XE، RouterOS، PowerShell، Windows یا توزیع Linux تطبیق داده شود. نمونه خروجی‌های بسته‌های تازه آموزشی‌اند، نه خروجی تضمین‌شده همه دستگاه‌ها. دستورات تغییردهنده باید در لاب یا پس از change approval اجرا شوند و rollback مستند داشته باشند.
