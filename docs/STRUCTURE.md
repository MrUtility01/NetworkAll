# معماری و استاندارد عمق محتوای NetworkAll v1

## معماری

```text
Windows (Flask + SQLite)  ←— LAN API —→  Android (Kotlin + Room)
           └──────── Shared merged curriculum index ────────┘
```

فهرست مشترک درس‌ها از `scripts/export_android_index.py` و `scripts/merge_content_packs_into_android.py` ساخته می‌شود. انتشار باید همین خروجی نهایی را هم داخل APK و هم داخل Windows bundle قرار دهد. دیتابیس قدیمی ویندوز/اندروید ممکن است به‌طور خودکار بازسازی نشود تا داده‌های شخصی از بین نرود.

## نقشهٔ پوشه‌ها

| مسیر | نقش |
|---|---|
| `server/core/full_curriculum.py` | هستهٔ درس‌های ۱–۶۳ |
| `server/core/extra_chapters.py` | fallback فصل‌های ۶۴–۶۸ برای source checkout |
| `server/core/rich_content.py` | محتوای آموزشی تولیدشده هنگام Seed قدیمی |
| `server/core/db.py` | SQLite، Seed و import از asset مشترک |
| `android/.../OfflineSeeder.kt` | Seed آفلاین Room |
| `tools/chapter_git_teacher.py` | hook فصل Git |
| `tools/packs/` | بسته‌های آموزشی واردشدنی |
| `scripts/validate_android_curriculum.py` | کنترل ساختاری فهرست |
| `docs/V1_RELEASE_AUDIT_FA.md` | ممیزی و موارد باقی‌مانده |

## تعریف درس عمیق

درس باید پیش‌نیاز و هدف روشن، مدل ذهنی، معماری، مثال گام‌به‌گام، خروجی موردانتظار، آزمایشگاه قابل‌بازتولید، خطای رایج، RCA، rollback/امنیت، واژه‌نامه و ارزیابی داشته باشد. پاسخ‌نامه باید مستقل و UIDها پایدار باشند.

آستانهٔ ممیزی قدیمی در `tools/audit_content.py` متن را به سه گروه تقسیم می‌کند: deep (حداقل ۲۰۰۰ کاراکتر)، mid (۸۰۰–۱۹۹۹) و thin (کمتر از ۸۰۰). این معیار فقط طول است؛ طول زیاد به معنی صحت علمی نیست.

## شکاف‌ها

- وجود اسکلت ۶۸ فصل به معنی کامل بودن ۶۸ کتاب نیست.
- بعضی فصل‌های پایه متن fallback و قالبی دارند؛ نیازمند بازنویسی اختصاصی هستند.
- سناریوهای نمونه، آزمون‌های تولیدی و دیاگرام‌های الگو باید جداگانه بازبینی شوند.
- همگام‌سازی کامل Tasks/Notes/Study Progress هنوز نیازمند آزمون پذیرش دوطرفه است.
- از ساخت بسته صرفاً بر اساس تعداد درس‌ها نتیجه نگیرید؛ کیفیت و تناسب عنوان/محتوا باید بررسی شود.

## ترتیب کار

1. اجرای export و ادغام packها.
2. اعتبارسنجی JSON، ۶۸ فصل، UID، نام مجموعه‌ها و answer key.
3. گزارش درس‌های thin و عنوان‌های نامرتبط.
4. اجرای تست‌های backend و Gradle.
5. ممیزی APK و Windows ZIP.
6. نصب تازه، حفظ داده‌های قدیمی، اتصال LAN و Sync دوطرفه.
