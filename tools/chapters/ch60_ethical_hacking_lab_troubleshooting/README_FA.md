# فصل ۶۰ — بسته غنی‌سازی (مرحله ۱ و ۲)

**وضعیت:** review_required  
**شاخه:** content/ch60-enrichment-stage1-2

## محتویات
- `ch60_pack.json` — درس‌های غنی‌شده (روش‌شناسی + عیب‌یابی عملی + قوانین Authorized Only + Nmap)
- `ch60_scenarios.json` — سناریوهای عملیاتی
- `ch60_questions.json` / `ch60_answer_key.json` — بانک سؤال و پاسخ‌نامه جدا
- `diagrams/ch60/` — دیاگرام‌های Mermaid
- `VALIDATION.md` — گزارش اعتبارسنجی و دستور ادغام

## ادغام
```bash
python tools/apply_any_pack.py --db server/data/encyclopedia.db --pack tools/packs/ch60/ch60_pack.json
# پس از بررسی:
python tools/apply_any_pack.py --db server/data/encyclopedia.db --pack tools/packs/ch60/ch60_pack.json --apply
```

تمام محتوا فقط برای محیط Lab مجاز طراحی شده است.


## فایل‌های اصلی فصل

- base_curriculum.json: تعریف درس‌های پایهٔ همین فصل.
- chapter.json: بستهٔ استاندارد محتوای افزوده و نرمال‌شده.
- manifest.json: فهرست فایل‌ها و شمار رکوردها.
- source_archive/: منابع اولیه، آزمون‌ها و پاسخ‌نامه؛ در build اسکن نمی‌شود.
