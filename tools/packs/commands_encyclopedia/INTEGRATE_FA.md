# ادغام فصل ۶۸ در هر دو نسخه

منبع حقیقت محتوا tools/packs/ و فهرست آن tools/packs/pack_catalog.json است. هر بسته فقط یک‌بار در شاخص ادغام می‌شود تا رکوردهای تکراری ساخته نشوند.

## بازسازی شاخص محتوا

در checkout ویندوز/PowerShell:

```powershell
python scripts/export_android_index.py
python scripts/merge_content_packs_into_android.py
```

فایل خروجی اندروید: android/app/src/main/assets/curriculum_index.json.gz

در CI همین شاخص به shared/curriculum_index.json.gz کپی می‌شود و همراه بستهٔ ویندوز می‌آید. سرور ویندوز در نصب تازه از شاخص مشترک استفاده می‌کند؛ دیتابیس موجود و پیشرفت شخصی کاربر به‌صورت خودکار پاک یا بازسازی نمی‌شود.

## ساخت Android

در مخزن GitHub به Actions → Build APK v1 بروید، آخرین اجرای موفق را باز کنید و artifact با نام EngineerJokar-APK-v1 را دریافت کنید.

## ساخت Windows

از همان اجرای موفق، artifact با نام NetworkAll-Windows-Portable را دریافت و استخراج کنید، سپس windows\Start-NetworkAll.bat را اجرا کنید.

این بستهٔ قابل‌حمل مبتنی بر Python است، نه EXE مستقل. به Python 3.11+ و اینترنت برای نصب اولیه وابستگی‌ها نیاز دارد. توکن همگام‌سازی در اجرای اول به‌صورت تصادفی ایجاد می‌شود؛ فایل server\data\sync-token.txt را منتشر نکنید.

## پس از نصب

- سرور ویندوز را روشن نگه دارید.
- گوشی و رایانه باید در شبکهٔ محلی قابل دسترسی باشند.
- در اندروید آدرس http://IP-ویندوز:5050 را تنظیم و توکن خصوصی سرور را وارد کنید.
- نصب نسخهٔ جدید به معنی پاک کردن داده‌های قبلی نیست. برای رفع اشکال Clear data نزنید مگر پس از backup؛ آن کار داده‌های محلی را پاک می‌کند.

## وضعیت کیفیت

بسته‌های جدید PowerShell (۷۱)، CMD/Batch (۳۸)، FortiGate (۳۳) و Issabel/Asterisk (۳۳) با پاسخ‌نامهٔ جدا و منابع مرجع افزوده شده‌اند. این تعداد رکورد به معنی تأیید اجرای تمام labها نیست؛ وضعیت آن‌ها review_required می‌ماند.
