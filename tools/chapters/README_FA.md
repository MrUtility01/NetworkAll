# ساختار محتوای فصل‌های NetworkAll

زیر tools/chapters دقیقاً ۶۸ پوشه با نام عددی 1 تا 68 وجود دارد. نام پوشه شمارهٔ فصل است؛ پوشهٔ chXX یا نام مستعار فصل نسازید.

## درخت استاندارد هر فصل

tools/chapters/1/  (همین ساختار برای 2 تا 68)
├── manifest.json
├── README_FA.md
├── lessons/
│   ├── base_curriculum.json   ← درس‌های پایه
│   ├── lessons.json           ← متن درس‌های افزوده
│   └── sources/               ← متن‌های اولیهٔ همان فصل
├── questions/
│   ├── questions.json
│   └── sources/               ← آزمون‌ها و بانک سؤال اصلی
├── answers/
│   ├── answer_key.json
│   └── sources/               ← پاسخ‌نامه‌ها و کلیدهای اصلی
├── examples/examples.json
├── commands/commands.json
├── labs/labs.json
├── media/                    ← تصویر و دیاگرام
├── authoring/                ← ابزار و پرامپت مختص فصل
├── android/manifest.json
├── windows/manifest.json
├── source_archive/           ← منبع‌هایی که هنوز نرمال نشده‌اند
└── build/chapter.json        ← خروجی خودکار؛ ویرایش دستی ممنوع

## فایل مرجع هر نوع محتوا

- lessons/base_curriculum.json و lessons/lessons.json: درس‌ها و متن آموزشی.
- questions/questions.json: سؤال‌های ساختاریافته؛ فایل‌های اولیه در questions/sources/ حفظ می‌شوند.
- answers/answer_key.json: پاسخ ساختاریافته؛ اصل پاسخ‌نامه در answers/sources/ می‌ماند.
- examples/examples.json: مثال‌ها و راه‌حل‌های نمونه.
- commands/commands.json: فرمان‌ها و مثال‌های CLI.
- labs/labs.json: سناریوهای آزمایش و عیب‌یابی.
- android/ و windows/: فقط پیکربندی/منبع مختص همان بستر؛ کد مشترک تکثیر نمی‌شود.

خالی بودن items در یک بانک یعنی برای آن فصل هنوز رکورد ساختاریافته‌ای در منبع پیدا نشده؛ فایل‌های اصلی در sources/ یا source_archive/ حذف نمی‌شوند.

## افزودن محتوا

درس جدید را در lessons/lessons.json و با UID پایدار و یکتا اضافه کنید. سؤال، پاسخ، مثال، فرمان و لاب را در فایل همان نوع و با همان UID درس ثبت کنید؛ در هر رکورد، fields باید فقط فیلدهای مربوط به همان نوع را داشته باشد.

build/chapter.json خروجی تولیدی assemble_chapter_packs.py است و در Git نگهداری نمی‌شود. ساخت اندروید و اجرای windows/start.bat آن را از فایل‌های مرجع می‌سازند.

برای بازتولید و اعتبارسنجی از ریشهٔ مخزن اجرا کنید:

    python scripts/assemble_chapter_packs.py --strict
    python scripts/merge_content_packs_into_android.py

فهرست شماره‌ها و شمار رکوردهای پایه/افزوده در INDEX_FA.md است.
