# ساختار فصل‌های NetworkAll

در این مسیر فقط پوشه‌های عددی 1 تا 68 وجود دارند. هر فصل محتوای خودش را به تفکیک نوع نگه می‌دارد:

- lessons/lessons.json: متن درس‌های افزوده و اطلاعات اصلی درس
- lessons/base_curriculum.json: ساختار و درس‌های پایه
- questions/questions.json و questions/sources/: سؤال‌ها و فایل‌های آزمون اولیه
- answers/answer_key.json و answers/sources/: پاسخ‌ها و پاسخ‌نامه‌ها
- examples/examples.json: مثال‌ها
- commands/commands.json: دستورات
- labs/labs.json: آزمایش‌ها و سناریوها
- android/ و windows/: تنظیمات مخصوص فصل، بدون تکرار کد مشترک برنامه
- media/ و authoring/: رسانه‌ها و ابزارهای تألیف
- source_archive/: منابعی که هنوز ساختاریافته نشده‌اند، بدون حذف
- build/chapter.json: بستهٔ سازگاری تولیدشده؛ دستی ویرایش نکنید.

پس از ویرایش فایل‌های دسته‌بندی‌شده، از ریشهٔ پروژه اجرا کنید:

    python scripts/assemble_chapter_packs.py --strict
    python scripts/merge_content_packs_into_android.py

در ویندوز، windows/start.bat ابتدا بسته‌ها را از منابع جداگانه بازسازی می‌کند و سپس سرور را بالا می‌آورد.
