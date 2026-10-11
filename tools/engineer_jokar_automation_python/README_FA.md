# بسته محتوای Python و اتوماسیون شبکه

این پوشه فقط ابزارهای تولید، اعتبارسنجی و اعمال بسته را نگه می‌دارد. JSON نهایی در مسیر canonical زیر قرار دارد:

tools/packs/automation_python/automation_python_curriculum_pack.json

## ابزارها

- build_content_pack.py — تولید مجدد بسته از تعریف موضوع‌ها؛ خروجی مستقیم در مسیر canonical نوشته می‌شود.
- validate_pack.py — کنترل تعداد رکوردها، UID، پوشش، بخش‌های لازم و جدایی سؤال از پاسخ.
- apply_content_pack.py — dry-run یا اعمال هدفمند در SQLite؛ بدون پاک‌کردن رکوردهای نامرتبط.
- apply_ui_patch.py — پچ اختیاری رابط وب قدیمی؛ پیش از اجرا diff را بررسی کنید.

## دامنه

| فصل | زیرفصل | حوزه | تعداد |
|---:|---:|---|---:|
| ۲۱ | ۴ | اتوماسیون MikroTik RouterOS | ۳۵ |
| ۳۵ | ۳ | اتوماسیون ویندوز/PowerShell | ۲۵ |
| ۵۱ | ۱ | Python شبکه | ۲۵ |
| ۵۱ | ۲ | Infrastructure as Code | ۲۵ |
| ۵۱ | ۳ | AI و اتوماسیون IT | ۲۵ |

این بسته شامل ۱۳۵ درس اعلام‌شده برای ۲۷ موضوع و پنج سطح L0 تا L4 است. این اعداد، ادعای تأیید علمی همه درس‌ها نیستند؛ بسته تا بازبینی دقیقِ مثال‌ها، منابع، نسخه‌ها، خروجی لابراتوار و عیب‌یابی باید review_required باقی بماند.

## بازتولید و اعتبارسنجی

از ریشه مخزن اجرا کنید:

    python tools/engineer_jokar_automation_python/build_content_pack.py
    python tools/engineer_jokar_automation_python/validate_pack.py
    python tools/audit_content.py --packs-only --json docs/audits/content-audit.json

## اعمال به دیتابیس

ابتدا نسخه پشتیبان بگیرید و حالت preview را بررسی کنید:

    python tools/engineer_jokar_automation_python/apply_content_pack.py --db server/data/encyclopedia.db

اگر تطبیق دقیق ۱۳۵ رکورد موفق است، سرور را متوقف کنید و پس از backup به‌صورت آگاهانه از --apply استفاده کنید. --overwrite فقط در صورتی استفاده شود که واقعاً قصد جایگزینی فیلدهای آموزشی را دارید. هیچ‌گاه فایل JSON را جایگزین خود فایل دیتابیس نکنید.

## قرارداد پاسخ‌نامه

سؤال‌ها باید به‌تنهایی کلید پاسخ را افشا نکنند. هر سؤال ID پایدار دارد و answer_key جداگانه برای همان ID پاسخ صحیح و توضیح آن را نگه می‌دارد.
