# پوشه‌های فصل برای غنی‌سازی NetworkAll

در هر پوشه chNN سه فایل وجود دارد: PROMPT.md قابل بارگذاری در ابزار AI، PACK_TEMPLATE.json برای شروع بسته و README.md. فهرست کامل در INDEX.md.

## بازتولید پوشه‌ها
از ریشه مخزن اجرا کن:
    py -3 tools/chapter_prompts/generate_chapter_prompts.py

## گردش کار
1. tools/chapter_prompts/chNN/PROMPT.md را به ابزار تولید محتوا بده.
2. pack واقعی را در tools/packs/chNN/ ذخیره کن و UID/تغییرات را بررسی کن.
3. از ریشه مخزن اجرا کن:
    py -3 scripts/export_android_index.py
    py -3 scripts/merge_content_packs_into_android.py
    py -3 scripts/validate_android_curriculum.py
    py -3 scripts/generate_android_diagrams.py

ساخت موفق به معنای تأیید علمی نیست؛ قبل از migration/reseed از داده شخصی backup بگیر.
