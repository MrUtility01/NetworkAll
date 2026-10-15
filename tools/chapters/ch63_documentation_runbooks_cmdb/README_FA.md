# فصل ۶۳ — مستندسازی Runbook و CMDB

**وضعیت:** review_required  
**شاخه هدف:** main  
**تاریخ شروع:** 2026-10-15

## محتویات
- `ch63_pack.json` / `ch63_pack_part*.json` — درس‌های غنی‌شده (L0–L4)
- `ch63_scenarios.json` — سناریوهای عملیاتی (≥۵۰)
- `ch63_questions.json` / `ch63_answer_key.json` — بانک سؤال و پاسخ‌نامه جدا
- `diagrams/ch63/` — دیاگرام‌های Mermaid
- `VALIDATION.md` — گزارش اعتبارسنجی و دستور ادغام
- `manifest.json` — شمارش و وضعیت عمق

## ساختار زیر‌فصل‌ها (از full_curriculum)
1. **۶۳.۱** انواع مستند عملیاتی (Runbook / MOP / SOP / EOP / Preconditions / Validation-Rollback / Escalation)
2. **۶۳.۲** Configuration و Compliance (Golden Config / Versioning / Drift / Compliance / Baseline)
3. **۶۳.۳** دارایی و CMDB (Inventory / CMDB Relationship / Asset Fields / Dependency Mapping / Discovery)
4. **۶۳.۴** الگوهای Runbook نمونه (WAN-DOWN / AD-AUTH / FW-HA / Core-Upgrade / Ransomware)

## ادغام
```bash
python tools/apply_any_pack.py --db server/data/encyclopedia.db --pack tools/packs/ch63_documentation_cmdb/ch63_pack_part1.json
# پس از بررسی dry-run:
python tools/apply_any_pack.py --db server/data/encyclopedia.db --pack tools/packs/ch63_documentation_cmdb/ch63_pack_part1.json --apply
```

تمام محتوا با `source_status: review_required` علامت‌گذاری شده و فقط برای محیط مجاز طراحی شده است.


## فایل‌های اصلی فصل

- base_curriculum.json: تعریف درس‌های پایهٔ همین فصل.
- chapter.json: بستهٔ استاندارد محتوای افزوده و نرمال‌شده.
- manifest.json: فهرست فایل‌ها و شمار رکوردها.
- source_archive/: منابع اولیه، آزمون‌ها و پاسخ‌نامه؛ در build اسکن نمی‌شود.
