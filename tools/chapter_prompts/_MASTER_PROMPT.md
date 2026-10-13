# پرامپت مادر غنی‌سازی کتاب‌محور فصل‌های NetworkAll

مخزن هدف: https://github.com/MrUtility01/NetworkAll

## اصول سخت
- فقط محتوای افزایشی بساز؛ فایل/درس/UID معتبر یا قابلیت فعلی حذف یا overwrite نشود.
- قبل از تولید، عنوان/موضوع فصل و زیرفصل واقعی، سطح L0 تا L4، تکرارها و شکاف‌ها را ممیزی کن.
- هر عنوان با متن درس مرتبط باشد؛ UID موجود ثابت بماند و UID جدید یکتا باشد.
- فارسی فنی روان، عنوان انگلیسی، پیش‌نیاز، اهداف یادگیری، واژه‌نامه و منبع رسمی دقیق داشته باش.
- فرمان/نسخه/منبع/خروجی آزمایش را جعل نکن. فقط لاب مجاز؛ backup و rollback اجباری.
- هر درس باید فصل کتاب واقعی باشد: مبانی، مدل ذهنی، معماری، کارکرد مرحله‌ای، موارد کاربرد/عدم کاربرد، مثال حل‌شده، لاب، خروجی موردانتظار، RCA، خطاهای رایج، امنیت، rollback، checklist، خلاصه و واژه‌نامه.
- حداقل در هر فصل: 50 مثال مستقل، 50 سناریوی واقعی و مستقل، 50 سؤال آزمون با answer_key جدا و IDهای یکسان، نمودار مخصوص هر مفهوم اصلی، لاب برای هر موضوع اصلی و حداقل 10 منبع معتبر.
- هر مثال شامل داده ورودی/فرمان، گام‌ها، خروجی و تفسیر باشد. هر سناریو محیط، هدف/علامت خرابی، محدودیت، شواهد، تحلیل، اصلاح، verify و rollback داشته باشد.
- سوال/options نباید فیلد correct یا پاسخ را افشا کنند. answer_key جدا و دارای ID و دلیل باشد.
- هر نمودار ID، عنوان، lesson_uid، Mermaid source، SVG، manifest و متن جایگزین داشته باشد؛ نمودار تکراری/تزئینی ممنوع.
- فیلدهای lesson: uid، chapter_order، subchapter_order، lesson_order، level، title_fa، title_en، topic، summary، full_content، commands، examples، notes، learning_objectives، meta، source_status.
- محتوای جدید تا بازبینی انسانی source_status=review_required بماند.
- اگر loader فعلی سناریو/نمودار را وارد UI نمی‌کند، آن را asset جدا اعلام کن؛ ادغام‌نشدن را پنهان نکن.
- خروجی‌ها: chNN_pack.json، chNN_answer_key.json، chNN_scenarios.json، diagrams/chNN/manifest.json + SVG/source، و VALIDATION.md با آمار واقعی.
- اول gap analysis و طرح درس‌ها، بعد JSON معتبر؛ بدون placeholder، ellipsis، رکورد تکراری یا منابع جعلی.

پس از ذخیره pack از ریشه مخزن اجرا کن:
    py -3 scripts/export_android_index.py
    py -3 scripts/merge_content_packs_into_android.py
    py -3 scripts/validate_android_curriculum.py
    py -3 scripts/generate_android_diagrams.py

این فرمان‌ها اعتبار ساختاری را بررسی می‌کنند، نه صحت علمی. پیش از migration/reseed از دیتابیس شخصی backup بگیر.
