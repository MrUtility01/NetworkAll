# VALIDATION — فصل ۶۳ مستندسازی Runbook و CMDB

**تاریخ:** 2026-10-15  
**وضعیت کلی:** review_required

## فایل‌های تولیدشده
| فایل | توضیح | وضعیت |
|------|--------|--------|
| README_FA.md | راهنمای بسته | آماده |
| manifest.json | شمارش و وضعیت | آماده |
| ch63_pack_part1.json | ۵ درس عمیق اول (Runbook L0–L4 + MOP L0) | آماده |
| VALIDATION.md | این فایل | آماده |

## تعداد واقعی رکوردها (part1)
- درس (lessons): **۵**
- سناریو: ۰ (در partهای بعدی)
- سؤال: داخل meta.assessment چند نمونه (پاسخ‌نامه جدا در آینده)
- نمودار: ۰ (در diagrams/ch63/ بعدی)

## UIDها
همه UIDها با الگوی `lesson:ch63:lvMMM:lKKKK` ساخته شده‌اند و با اسکلت full_curriculum سازگارند. هیچ UID قبلی تغییر نکرده.

## دستور ادغام
```bash
# Dry-run
python tools/apply_any_pack.py --db server/data/encyclopedia.db --pack tools/packs/ch63_documentation_cmdb/ch63_pack_part1.json

# Apply
python tools/apply_any_pack.py --db server/data/encyclopedia.db --pack tools/packs/ch63_documentation_cmdb/ch63_pack_part1.json --apply
```

## موارد بررسی‌نشده / باقی‌مانده
- تکمیل تمام سطوح L0–L4 برای ۷ موضوع ۶۳.۱
- کل ۶۳.۲، ۶۳.۳، ۶۳.۴
- ≥۵۰ مثال مستقل
- ≥۵۰ سناریو عملیاتی
- ≥۵۰ سؤال + answer_key جدا
- دیاگرام‌های Mermaid/SVG
- لاب‌های پایه/متوسط/پیشرفته

## منابع مرجع (اولیه)
- ITIL 4 Practice Guide – Knowledge Management / Service Configuration Management
- NIST SP 800-128 (Guide for Security-Focused Configuration Management)
- Cisco / Juniper / MikroTik documentation best practices for Runbooks
- ServiceNow CMDB documentation (public)
- NetBox documentation (open-source CMDB)

**نکته:** تمام محتوای تولیدشده تا بررسی انسانی با `review_required` علامت‌گذاری شده است.
