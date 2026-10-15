# NetworkAll — ENGINEER JOKAR

دانشنامهٔ شخصی شبکه و زیرساخت IT برای ویندوز و اندروید: محتوای آفلاین، جست‌وجو، یادگیری مرحله‌ای و همگام‌سازی شبکهٔ محلی.

## وضعیت انتشار

**نسخهٔ ۱٫۰٫۰ هنوز کاندید انتشار است، نه نسخهٔ نهایی تأییدشده.** بازآرایی محتوا در شاخهٔ feature/modular-chapter-folders و [پیش‌نویس PR شمارهٔ ۸](https://github.com/MrUtility01/NetworkAll/pull/8) نگهداری می‌شود؛ تا ادغام در main و تست نصب واقعی روی دستگاه، Artifact را نسخهٔ نهایی تلقی نکنید.

- مخزن رسمی: https://github.com/MrUtility01/NetworkAll
- بررسی ساخت‌ها: https://github.com/MrUtility01/NetworkAll/actions
- ممیزی و موارد باقی‌مانده: [ممیزی انتشار v1](https://github.com/MrUtility01/NetworkAll/blob/feature/modular-chapter-folders/docs/V1_RELEASE_AUDIT_FA.md)

## مسیر پیشنهادی برای کاندید v1

برای بررسی تغییرهای نسخهٔ ۱، شاخهٔ کاری را دریافت کنید؛ هنوز با `main` یکی نشده است:

```bash
git clone https://github.com/MrUtility01/NetworkAll.git
cd NetworkAll
git fetch origin
git switch feature/modular-chapter-folders
```

Artifact اندروید و ZIP ویندوز را فقط از یک اجرای موفق GitHub Actions دریافت کنید. ZIP ویندوز بستهٔ میزبان/سورس Python است و **EXE مستقل نیست**.

## معماری

| مسیر | نقش |
|---|---|
| `server/` | Flask، SQLite، وب و API |
| `android/` | اپ Kotlin و پایگاه دادهٔ آفلاین |
| `windows/` | راه‌انداز میزبان ویندوز |
| `tools/chapters/1/` تا `tools/chapters/68/` | محتوای هر فصل به‌صورت عددی و تفکیک‌شده بر اساس نوع |
| `scripts/` | خروجی‌گیری، تفکیک محتوا، ساخت بسته‌های سازگاری و اعتبارسنجی |
| `docs/` | معماری، Sync، ممیزی و محدودیت‌های شناخته‌شده |

## ساختار محتوای آموزشی

در tools/chapters فقط پوشه‌های عددی 1 تا 68 وجود دارند. داخل هر پوشه، متن درس‌ها، سؤال‌ها، پاسخ‌نامه‌ها، مثال‌ها، دستورات و لابراتوارها در فایل‌های مستقل نگهداری می‌شوند؛ منابع اولیه هم در پوشه‌های sources یا source_archive حفظ می‌شوند.

نمونهٔ مسیر فصل ۱۳:

    tools/chapters/13/
      lessons/base_curriculum.json
      lessons/lessons.json
      questions/questions.json
      questions/sources/
      answers/answer_key.json
      answers/sources/
      examples/examples.json
      commands/commands.json
      labs/labs.json
      android/manifest.json
      windows/manifest.json
      source_archive/
      build/chapter.json  (تولید خودکار، قابل بازتولید)

فایل‌های مرجع در پوشه‌های نوع محتوا ویرایش می‌شوند؛ build/chapter.json خروجی سازگاری است. Windows با windows/start.bat بسته‌ها را پیش از اجرا می‌سازد و workflow اندروید همان فایل‌های مرجع را برای خروجی آفلاین ادغام می‌کند. پیکربندی اندروید/ویندوز در پوشهٔ هر فصل فقط برای تفاوت‌های همان پلتفرم است تا متن درس دوبار تکثیر نشود.

راهنمای کامل: tools/chapters/README_FA.md؛ فهرست ۶۸ فصل: tools/chapters/INDEX_FA.md.

## قراردادهای کاندید v1

- نام محصول: **NetworkAll**
- نسخهٔ هدف: **1.0.0**
- پورت پیش‌فرض وب/API در میزبان ویندوز: TCP **5050** (قابل تغییر با NETENC_PORT)
- درخت هدف: **۶۸ فصل** با فهرست آموزشی ادغام‌شدهٔ مشترک
- Windows: Python 3.11+ و بستهٔ ZIP
- Android: APK از Artifact معتبر

در اجرای ویندوزی کاندید، توکن Sync باید مخصوص همان نصب باشد؛ توکن، فایل دیتابیس و بکاپ خصوصی را commit یا در URL قرار ندهید. سرور را مستقیماً به اینترنت عمومی expose نکنید.

## نکات مهم

وجود ۶۸ فصل یا ساخت موفق APK به معنی بازبینی علمی تمام درس‌ها نیست. برخی دیاگرام‌ها الگوهای SVG تولیدشده هستند؛ Sync دوطرفهٔ کامل Tasks/Notes/Study Progress، تقویم شمسی، یادآوری‌ها، Backup/Restore و آزمون روی دستگاه واقعی باید طبق ممیزی v1 تأیید شوند. برای استفادهٔ روزانه از داده‌های مهم، تا تکمیل این تست‌ها از آن‌ها بکاپ جداگانه بگیرید.
