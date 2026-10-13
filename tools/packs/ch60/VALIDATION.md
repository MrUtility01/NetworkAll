# VALIDATION.md — بسته فصل ۶۰ NetworkAll

**تاریخ تولید:** 2026-10-13  
**وضعیت:** review_required (تمام محتوا)  
**اصل صفر رعایت شد:** هیچ UID موجودی تغییر نکرده، هیچ فایلی overwrite نشده، فقط افزودن افزایشی.

## فایل‌های تولیدشده

| فایل | نقش | وضعیت |
|------|-----|--------|
| `ch60_pack.json` | درس‌های اصلی (اسکلت کامل + درس‌های غنی مرحله ۱+۲) | مرحله ۱+۲ |
| `ch60_scenarios.json` | سناریوهای عملیاتی | ۱۰+ |
| `ch60_questions.json` | بانک سؤال بدون پاسخ | ۲۰ |
| `ch60_answer_key.json` | پاسخ‌نامه مستقل | ۲۰ |
| `diagrams/ch60/` | دیاگرام‌ها | پایه |
| `VALIDATION.md` | این گزارش | — |

## تعداد واقعی رکوردها (مرحله ۱+۲)

- درس در `ch60_pack.json`: **۱۸**
- سناریو: **۱۰**
- سؤال: **۲۰**
- پاسخ: **۲۰**

## دستور ادغام پیشنهادی

```bash
cp server/data/encyclopedia.db server/data/encyclopedia.db.bak_ch60_$(date +%Y%m%d)
python tools/apply_any_pack.py --db server/data/encyclopedia.db --pack tools/packs/ch60/ch60_pack.json
python tools/apply_any_pack.py --db server/data/encyclopedia.db --pack tools/packs/ch60/ch60_pack.json --apply
python scripts/export_android_index.py
python scripts/merge_content_packs_into_android.py
```

**توجه:** تمام محتوا source_status=review_required و فقط برای Lab مجاز.
