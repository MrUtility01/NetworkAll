# NetworkAll v1.0.0 — Android Client

## نصب

APK را فقط از Artifact یک اجرای موفق `NetworkAll Android APK (validated)` دریافت کنید. Application ID برابر `com.netenc.app` است؛ `versionName=1.0.0` و `versionCode=4`. در اولین اجرا رمز ورود محلی را تنظیم کنید؛ رمز به‌صورت hash نمک‌دار در فضای خصوصی برنامه نگهداری می‌شود. این قفل جایگزین رمزگذاری دیتابیس نیست.

## اتصال به ویندوز

- ویندوز و گوشی باید در شبکهٔ محلی‌ای باشند که اتصال بین دستگاه‌ها را مسدود نکند.
- API host: `http://IP-ویندوز:86`
- API token: محتوای فایل `server/data/networkall.token` در نصب ویندوز.
- برای دسترسی LAN، Windows Firewall باید TCP/86 را فقط در شبکهٔ خصوصی اجازه دهد.

## کد و ساخت

پروژهٔ Android Studio در پوشهٔ `android/` است. Workflow اصلی در `.github/workflows/build-apk.yml` ابتدا curriculum را export/merge/validate می‌کند، دیاگرام‌ها را می‌سازد، Gradle را اجرا و دارایی‌های APK را بررسی می‌کند.

وجود دکمهٔ Sync یا endpoint به‌تنهایی تضمین نمی‌کند همهٔ داده‌های Tasks/Notes/Study Progress دوطرفه منتقل شوند. برای شرح معیارهای پذیرش، `docs/V1_RELEASE_AUDIT_FA.md` را ببینید.
