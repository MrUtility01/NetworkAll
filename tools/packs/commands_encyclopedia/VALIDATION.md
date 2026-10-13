# گزارش اعتبارسنجی فصل ۶۸ — وضعیت افزایشی جاری

تاریخ گزارش: 2026-10-13  
شاخه: `codex/android-repair-port86-20261013`

## شمارش واقعی فایل‌های مستقل

| بسته | فایل‌های شمارش‌شده | رکورد فعلی |
|---|---|---:|
| Cisco IOS-XE Routing | `cisco_routing.json` + `cisco_routing_addon_01..08.json` | **۱۶۰۰** |
| Cisco Switching | `cisco_switching.json` | ۲۰ |
| MikroTik RouterOS v7 | `mikrotik_ops_addon.json` (43) + `mikrotik_ops_addon_02.json` (100) + `mikrotik_ops_addon_03.json` (51) | **۱۹۴** |
| PowerShell | `powershell.json` (49) + `powershell_addon_01.json` (100) + `powershell_addon_02.json` (35) | **۱۸۴** |
| Windows Batch | `windows_batch.json` | ۲۰ |
| Linux | `linux.json` | ۲۰ |
| **مجموع رکوردهای فرمان در بسته‌های مستقل بالا** | | **۲۰۳۸** |

عدد Cisco Routing از شمار واقعی فایل‌ها به‌دست آمده است: ۱۵۱ رکورد در بسته پایه و ۷ بسته ۲۰۰ رکوردی به‌جز آخرین بسته ۴۹ رکوردی؛ جمع آن‌ها دقیقاً ۱۶۰۰ است. UIDهای Cisco از `cmd:cisco:routing:0001` تا `cmd:cisco:routing:1600` برنامه‌ریزی شده‌اند و validator یکتایی و تعارض UID را بررسی می‌کند.

## مثال‌ها، سناریوها و آزمون‌ها

| مجموعه | تعداد |
|---|---:|
| مثال‌های چندپلتفرمی | ۵۰ |
| سناریوهای چندپلتفرمی | ۵۰ |
| آزمون عمومی فصل ۶۸ | ۵۰ سؤال |
| پاسخ‌نامه مستقل آزمون عمومی | ۵۰ پاسخ |
| آزمون تخصصی Cisco Routing / ACL / NAT (base + addon 01) | **۴۵ سؤال** |
| پاسخ‌نامه مستقل Cisco | **۴۵ پاسخ** |
| آزمون تخصصی MikroTik RouterOS v7 (base + addon 01) | **۵۰ سؤال** |
| پاسخ‌نامه مستقل MikroTik | **۵۰ پاسخ** |
| آزمون تخصصی PowerShell (base + addon 01) | **۴۱ سؤال** |
| پاسخ‌نامه مستقل PowerShell | **۴۱ پاسخ** |
| منابع مستقل فصل ۶۸ | ۱۷ URL در فایل منابع پایه |

مجموع آزمون‌های تخصصی موجود در فایل‌های جداگانه: **۱۳۶ سؤال و ۱۳۶ پاسخ** (Cisco=45، RouterOS=50، PowerShell=41)؛ به‌علاوه آزمون عمومی فصل ۶۸ با ۵۰ سؤال و ۵۰ پاسخ. پاسخ‌های درست در فایل‌های answer key نگهداری می‌شوند؛ validator شناسه‌ها، فرمان مرجع، تعداد گزینه‌ها و تطبیق پاسخ با گزینه را بررسی می‌کند.

## فایل‌های آزمون تخصصی جدید

- `cisco_routing_exam.json` + `cisco_routing_exam_addon_01.json`؛ هر کدام answer key جدا
- `routeros_exam.json` + `routeros_exam_addon_01.json`؛ هر کدام answer key جدا
- `powershell_exam.json` + `powershell_exam_addon_01.json`؛ هر کدام answer key جدا

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


## Batch افزایشی جدید — 2026-10-13

- RouterOS v7: فایل `mikrotik_ops_addon_03.json` پس از افزودن ۱۰ رکورد جدید اکنون **۵۱ رکورد** دارد؛ جمع مستقل RouterOS اکنون **۱۹۴** رکورد است.
- PowerShell: فایل `powershell_addon_02.json` پس از افزودن ۱۰ رکورد جدید اکنون **۳۵ رکورد** دارد؛ جمع مستقل PowerShell اکنون **۱۸۴** رکورد است.
- آزمون‌های تخصصی هر پلتفرم در فایل‌های addon جدا و answer key مستقل نگهداری می‌شوند: Cisco پنج سؤال جدید (جمع ۴۵)، RouterOS پنج سؤال جدید (جمع ۵۰)، PowerShell پنج سؤال جدید (جمع ۴۱) در مرحله تازه؛ هر آزمون با answer key مستقل.
- جمع بسته‌های فرمان در جدول بالا **۲۰۳۸ رکورد** است؛ شمارش بر اساس آرایه‌های `commands` فایل‌های مستقل انجام شده است.
- validator به‌روزرسانی شده تا فایل‌های جدید، UIDها، ارجاع آزمون به فرمان و تطبیق پاسخ‌نامه را در CI بررسی کند. نتیجه اجرای CI پس از این commitها باید جداگانه تأیید شود.


## رفع خطای CI و ممیزی جدید

- اجرای ناموفق [38460964232](https://github.com/MrUtility01/NetworkAll/actions/runs/38460964232) در مرحلهٔ `Validate Chapter 68 command packs` متوقف شد: `routeros_exam.json` دارای ۳۰ سؤال و `routeros_exam_answer_key.json` فقط ۲۰ پاسخ بود.
- ۱۰ پاسخِ مفقود برای `routeros-exam-021..030` افزوده شد؛ اکنون آزمون پایه RouterOS برابر ۳۰ سؤال/۳۰ پاسخ و با addon جدید مجموع RouterOS برابر ۴۵/۴۵ است.
- ممیزی مستقل فایل‌های فرمان: Cisco Routing=۱۶۰۰، RouterOS=۱۹۴، PowerShell=۱۸۴؛ جمع تمام بسته‌های فرمان جدول بالا=۲۰۳۸. بسته‌های جدید ۲۰ رکورد افزوده‌اند؛ یکتایی UID و فرمان و ارجاع آزمون باید با اجرای تازه CI تأیید شود.
- در batch تازه، برای هر پلتفرم پنج سؤال دیگر و پاسخ‌نامه مستقل افزوده شد؛ شمار کل آزمون‌های تخصصی اکنون Cisco=۴۵، RouterOS=۵۰ و PowerShell=۴۱ است (جمع ۱۳۶ سؤال/پاسخ تخصصی).
