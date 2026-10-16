# VALIDATION فصل ۶۷ — غنی‌سازی

تاریخ: 2026-10-16 | status: review_required

## ممیزی قبل
- base_curriculum: فقط ۳ درس کلی
- lessons.json: ۱۵ آیتم عمدتاً thin (۶۰۰–۱۰۰۰ کاراکتر)
- questions / answers / labs: خالی (۰)
- منبع خام بزرگ در source_archive ادغام کامل نشده بود

## بسته enrichment (artifacts + این شاخه)
- lessons_enrichment.json: ۲۰ درس کتاب‌محور جدید (IPsec/SSL/TS/Hardening)
- questions.json: ۵۰ سؤال
- answer_key.json: ۵۰ پاسخ
- labs.json: ۱۰ لاب
- base_curriculum گسترش‌یافته: ۵ زیرفصل

## اصول
- preserve UIDهای موجود `lesson:ch67:bp:*`
- UID جدید: `lesson:ch67:lv...`
- فقط Lab / شبیه‌ساز — بدون دور زدن امنیت سازمان واقعی

## ادغام
فایل‌های کامل در ZIP محلی `ch67_enrichment.zip`؛ پس از بازبینی در `tools/chapters/67/` کپی شوند.
