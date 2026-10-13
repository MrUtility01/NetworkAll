# گزارش اعتبارسنجی فصل ۶۸ — وضعیت افزایشی جاری

تاریخ گزارش: 2026-10-13  
شاخه: `codex/android-repair-port86-20261013`

## شمارش واقعی فایل‌های مستقل

| بسته | فایل‌های شمارش‌شده | رکورد فعلی |
|---|---|---:|
| Cisco IOS-XE Routing | `cisco_routing.json` + `cisco_routing_addon_01..08.json` | **۱۶۰۰** |
| Cisco Switching | `cisco_switching.json` | ۲۰ |
| MikroTik RouterOS v7 | `mikrotik_ops_addon.json` + `mikrotik_ops_addon_02.json` | ۱۴۳ |
| PowerShell | `powershell.json` + `powershell_addon_01.json` | ۱۴۹ |
| Windows Batch | `windows_batch.json` | ۲۰ |
| Linux | `linux.json` | ۲۰ |
| **مجموع رکوردهای فرمان در بسته‌های مستقل بالا** | | **۱۹۵۲** |

عدد Cisco Routing از شمار واقعی فایل‌ها به‌دست آمده است: ۱۵۱ رکورد در بسته پایه و ۷ بسته ۲۰۰ رکوردی به‌جز آخرین بسته ۴۹ رکوردی؛ جمع آن‌ها دقیقاً ۱۶۰۰ است. UIDهای Cisco از `cmd:cisco:routing:0001` تا `cmd:cisco:routing:1600` برنامه‌ریزی شده‌اند و validator یکتایی و تعارض UID را بررسی می‌کند.

## مثال‌ها، سناریوها و آزمون‌ها

| مجموعه | تعداد |
|---|---:|
| مثال‌های چندپلتفرمی | ۵۰ |
| سناریوهای چندپلتفرمی | ۵۰ |
| آزمون عمومی فصل ۶۸ | ۵۰ سؤال |
| پاسخ‌نامه مستقل آزمون عمومی | ۵۰ پاسخ |
| آزمون تخصصی Cisco Routing / ACL / NAT | ۲۵ سؤال |
| پاسخ‌نامه مستقل Cisco | ۲۵ پاسخ |
| آزمون تخصصی MikroTik RouterOS v7 | ۲۰ سؤال |
| پاسخ‌نامه مستقل MikroTik | ۲۰ پاسخ |
| آزمون تخصصی PowerShell | ۲۱ سؤال |
| پاسخ‌نامه مستقل PowerShell | ۲۱ پاسخ |
| منابع مستقل فصل ۶۸ | ۱۷ URL در فایل منابع پایه |

مجموع آزمون‌های موجود در فایل‌های جداگانه: **۱۱۶ سؤال و ۱۱۶ پاسخ**. پاسخ‌های درست در فایل‌های answer key نگهداری می‌شوند؛ validator شناسه‌ها، فرمان مرجع، تعداد گزینه‌ها و تطبیق پاسخ با گزینه را بررسی می‌کند.

## فایل‌های آزمون تخصصی جدید

- `cisco_routing_exam.json` و `cisco_routing_exam_answer_key.json`
- `routeros_exam.json` و `routeros_exam_answer_key.json`
- `powershell_exam.json` و `powershell_exam_answer_key.json`

## اعتبارسنجی و محدودیت‌ها

- `scripts/validate_ch68_command_packs.py` باید تمام بسته‌ها را parse کند، حداقل تعداد واقعی، فیلدهای ضروری، UIDهای یکتا، نبود تعارض UID، ارجاع سؤال‌ها به فرمان و تطبیق پاسخ‌نامه را بررسی کند.
- فایل‌های افزوده با `source_status=review_required` باقی می‌مانند. شمار رکورد، به‌تنهایی تأیید صحت تمام syntaxها یا پشتیبانی در همه releaseها نیست.
- خروجی‌های نمونه آموزشی هستند و نباید به‌عنوان خروجی تضمین‌شده همه مدل‌ها و نسخه‌ها معرفی شوند.
- دستورات تغییردهنده باید در لاب یا پس از change approval اجرا شوند؛ rollback و دسترسی مدیریت جایگزین لازم است.
- **۱۶۰۰ رکورد Cisco Routing در فایل‌های مستقل ثبت شده است؛ اعتبارسنجی ساختاری CI و بازبینی انسانی/آزمایش عملی همچنان معیارهای جداگانه‌اند.**

## فرمان‌های اعتبارسنجی

از ریشه مخزن:

```bash
python3 scripts/validate_ch68_command_packs.py
python3 scripts/export_android_index.py
python3 scripts/merge_content_packs_into_android.py
python3 scripts/validate_android_curriculum.py
```
