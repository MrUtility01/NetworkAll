# VALIDATION.md — بسته فصل ۶۰ NetworkAll

**تاریخ:** 2026-10-13  
**وضعیت:** review_required  
**مراحل:** ۱ + ۲ + ۳

## شمارش نهایی (مرحله ۳)

| بخش | تعداد |
|-----|--------|
| درس در ch60_pack.json | **۲۷** |
| سناریو | **۵۰** |
| سؤال آزمون | **۵۵** |
| پاسخ‌نامه | **۵۵** (شناسه یکسان) |

## فایل‌ها
- `ch60_pack.json` — ۲۷ درس کتاب‌محور
- `ch60_scenarios.json` — ۵۰ سناریو Lab-only
- `ch60_questions.json` / `ch60_answer_key.json`
- `diagrams/ch60/`

## اصول
- preserve_existing_uids = true
- source_status = review_required
- فقط محیط Lab مجاز / Authorized Only

## ادغام
```bash
python tools/apply_any_pack.py --db server/data/encyclopedia.db --pack tools/packs/ch60/ch60_pack.json --apply
```

**مرحله ۳ محلی آماده است** — فایل کامل در artifacts؛ در صورت نیاز با همان روش قبلی push کنید.
