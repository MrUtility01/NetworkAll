# یادآوری‌های NetworkAll در ویندوز و اندروید

## رفتار و محدودیت‌های واقعی

- **Windows:** سرور محلی Flask یک poller دارد که موعدهای task ذخیره‌شده در SQLite را بررسی می‌کند و با Toast ویندوز از طریق `winotify` اعلان می‌فرستد. اعلان به اجرای process سرور در نشست کاربر نیاز دارد؛ اگر سرور بسته باشد، اعلان همان لحظه تحویل نمی‌شود.
- **اجرای خودکار ویندوز:** `scripts/install_windows_reminder_startup.ps1` یک Scheduled Task در context کاربر فعلی می‌سازد تا سرور بعد از sign-in به‌صورت مخفی اجرا بماند. اجرا با سطح دسترسی Limited است و دسترسی LAN فعال نمی‌کند. برای حذف آن `scripts/remove_windows_reminder_startup.ps1` اجرا شود. Runner با فاصلهٔ ۱۰ ثانیه پس از خروج سرور دوباره تلاش می‌کند.
- **Android:** `TaskReminderScheduler` از WorkManager و `TaskReminderWorker` از notification channel استفاده می‌کنند. زمان‌بندی هنگام startup، ورود به برنامه و پس از sync تطبیق داده می‌شود؛ Android 13+ به اجازهٔ اعلان نیاز دارد.
- **زمان دقیق:** WorkManager برای کار پس‌زمینه مقاوم است، اما ممکن است به‌علت Doze، محدودیت باتری یا سیاست سازندهٔ گوشی دیر اجرا شود؛ زمان دقیق تا ثانیه تضمین نمی‌شود.
- **همگام‌سازی موعد:** فقط `remind_at` بین دستگاه‌ها منتقل می‌شود. `reminded_at` تاریخچهٔ محلی تحویل اعلان است و به دستگاه دیگر کپی نمی‌شود. یادآوری فقط برای task زمان‌دار فعال می‌شود، نه برای موعد تمام‌روزه.
- **امنیت LAN:** اسکریپت startup فقط از binding پیش‌فرض `127.0.0.1` استفاده می‌کند. برای Sync گوشی باید جداگانه و آگاهانه `NETENC_HOST=0.0.0.0`، توکن قوی و Firewall محدود به Private profile تنظیم شود. این اسکریپت پورت عمومی یا firewall rule ایجاد نمی‌کند.

## نصب روی ویندوز

1. وابستگی‌های پروژه را از پوشهٔ مخزن نصب کنید:

   `python -m pip install -r server/requirements.txt`

2. PowerShell را در پوشهٔ مخزن باز و اجرا کنید:

   `powershell -ExecutionPolicy Bypass -File .\scripts\install_windows_reminder_startup.ps1 -StartNow`

3. در صورت خطا، فایل‌های `%LOCALAPPDATA%\NetworkAll\logs\server.stderr.log` و `runner.log` را بررسی کنید.
4. برای حذف شروع خودکار:

   `powershell -ExecutionPolicy Bypass -File .\scripts\remove_windows_reminder_startup.ps1`

حذف Scheduled Task داده‌های پایگاه‌داده، یادداشت‌ها یا فایل‌های گزارش را پاک نمی‌کند.

## معیارهای پذیرش نهایی (هنوز اجرا نشده)

- ساخت task زمان‌دار در Windows؛ toast یک‌بار نمایش داده شود و `reminded_at` ثبت شود.
- sign out/sign in و restart ویندوز؛ runner با یک instance شروع شود و موعد آینده از دست نرود.
- ساخت task زمان‌دار در Android؛ پس از اجازهٔ اعلان، notification ظاهر شود و با done/delete لغو شود.
- همگام‌سازی task زمان‌دار در هر دو جهت؛ موعد به دستگاه دیگر برسد و هر دستگاه اعلان محلی خود را ارائه دهد.
- نبود مجوز اعلان یا خاموش‌بودن process باید به‌عنوان محدودیت ثبت شود، نه موفقیت کاذب.
- آزمون deadline واقعی، reboot، Doze و timezone در آخرین مرحلهٔ تست انجام شود.
