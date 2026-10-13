# پرامپت مستقل قابل بارگذاری — فصل 35: PowerShell CMD

مخزن هدف: https://github.com/MrUtility01/NetworkAll
شماره فصل: 35
عنوان مطابق فهرست curriculum: PowerShell CMD
کلیدواژه‌های شروع: PowerShell automation

ابتدا محتوای موجود را از نظر تناسب عنوان و محتوا، عمق، سطح L0-L4، UIDهای تکراری و شکاف‌ها ممیزی کن. گزارش شکاف بده و فقط محتوای افزایشی و یکتا تولید کن.

## معیارهای اجباری
حداقل 50 مثال مستقل، 50 سناریوی مستقل، 50 سؤال آزمون، answer_key جدا با ID مشترک، نمودار برای تمام مباحث اصلی، لاب امن، منابع رسمی دقیق، پوشش L0-L4 و rollback. محتوای موجود را حذف یا overwrite نکن؛ داده یا منبع ساختگی نساز.
- هر مثال شامل ورودی/فرمان، مراحل، خروجی موردانتظار و تفسیر باشد.
- هر سناریو شامل محیط، هدف/نشانه خرابی، محدودیت، شواهد، تحلیل، اصلاح، verify و rollback/درس‌آموخته باشد.
- هر سؤال ID ثابت داشته باشد؛ صورت سؤال/options بدون جواب صحیح و answer_key فایل جدا با توضیح فارسی تولید شود.
- هر مفهوم اصلی نمودار اختصاصی داشته باشد: Mermaid source، SVG، manifest دارای عنوان و lesson_uid و متن جایگزین.
- هر درس: آموزش از صفر، مدل ذهنی، معماری، کاربرد/عدم کاربرد، مثال حل‌شده، لاب، RCA، امنیت، rollback، checklist و واژه‌نامه.
- حداقل 10 منبع رسمی دقیق مرتبط؛ نسخه/URL/خروجی ساختگی ممنوع.


## قرارداد lesson
فیلدهای uid، chapter_order=35، subchapter_order، lesson_order، level، title_fa، title_en، topic، summary، full_content، commands، examples، notes، learning_objectives، meta، source_status. برای محتواهای جدید source_status=review_required ثبت شود.

## خروجی
1. ch35_pack.json با package_schema_version=1، project=ENGINEER JOKAR / NetworkAll، chapter_order=35 و lessons سازگار با importer فعلی.
2. ch35_answer_key.json با IDهای یکسان، پاسخ و دلیل.
3. ch35_scenarios.json با حداقل 50 سناریوی ساختاریافته.
4. diagrams/ch35/manifest.json به همراه SVG و source.
5. VALIDATION.md با تعداد واقعی، UIDهای یکتا، تطبیق سؤال/پاسخ، منابع و موارد نیازمند بازبینی.
بسته اصلی زیر tools/packs/ch35/ قرار گیرد. JSON ناقص یا placeholder ممنوع. تا پشتیبانی و تست loader، دارایی‌های جداگانه سناریو/دیاگرام را به عنوان واردشده در UI معرفی نکن.
