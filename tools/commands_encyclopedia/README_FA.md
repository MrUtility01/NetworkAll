# دانشنامه جامع دستورات — فصل ۶۸ NetworkAll

این پوشه **قالب، Schema و دستورالعمل تولید** را نگه می‌دارد. بسته‌های JSON واقعی که merge می‌شوند در `tools/packs/commands_encyclopedia/` قرار دارند.

## ساختار هر رکورد
هر فرمان باید پلتفرم/فروشنده، کاربرد، syntax، آرگومان‌ها، پیش‌نیاز، مراحل، خروجی نمونه و تفسیر آن، خطاهای رایج، دستورهای مرتبط، Lab، ملاحظات امنیتی، کلمات جست‌وجو، فلش‌کارت‌ها و ارزیابی داشته باشد. در ارزیابی، `questions` و `answer_key` جدا هستند.

## مجموعه‌های فصل ۶۸
1. Cisco IOS/IOS-XE
2. MikroTik RouterOS 7
3. Linux
4. Bash
5. PowerShell
6. Windows CMD
7. Windows Batch
8. FortiGate CLI و Issabel/Asterisk، فقط وقتی JSON معتبر آن‌ها در پوشهٔ pack موجود باشد.

## بسته‌های shell اضافه‌شده در v1
`networkall_shell_expanded.json` شامل ۵۰ فرمان عملیاتی تکمیلی (۱۰ مورد برای هر یک از پنج پلتفرم/شل Linux، Bash، PowerShell، CMD و Batch) با نمونه خروجی آموزشی، مراحل، Lab، امنیت، دو فلش‌کارت و MCQ با پاسخ مجزا است. خروجی نمونه برای نمایش روش تفسیر است؛ باید با نسخه و پیکربندی واقعی تطبیق داده شود.

## اعتبارسنجی و خروجی
```bash
python scripts/export_android_index.py
python scripts/merge_content_packs_into_android.py
python scripts/validate_android_curriculum.py
python scripts/generate_android_diagrams.py
```

تعداد نهایی را از گزارش واقعی بخوانید. وجود prompt یا نام فایل در README، به معنی وجود pack کامل نیست. بسته‌های موجود اما ناقص را قبل از انتشار اصلاح یا از فهرست «تکمیل‌شده» حذف کنید.
