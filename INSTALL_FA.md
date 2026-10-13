# راهنمای نصب NetworkAll v1.0.0

این راهنما برای شاخهٔ `codex/android-repair-port86-20261013` نوشته شده است. خروجی ویندوز یک بستهٔ قابل‌حمل Python است، نه EXE مستقل؛ خروجی اندروید APK است که باید از اجرای موفق GitHub Actions دریافت شود.

## ۱) ویندوز (میزبان)

1. نصب Python 3.11 یا بالاتر؛ گزینهٔ **Add Python to PATH** فعال باشد.
2. دریافت فایل `NetworkAll-Windows-v1.0.0.zip` از Artifact یک اجرای موفق [GitHub Actions](https://github.com/MrUtility01/NetworkAll/actions).
3. استخراج کامل ZIP در یک پوشهٔ قابل‌نوشتن. فایل‌ها را از داخل ZIP اجرا نکنید.
4. اجرای `windows\start.bat`.
5. در صورت اولین اجرا، نصب وابستگی‌ها و ساخت پایگاه داده انجام می‌شود.
6. وب‌برنامه: `http://127.0.0.1:86`.

Launcher یک محیط مجازی محلی در `.venv` می‌سازد و سرور را روی TCP/86 و رابط شبکهٔ محلی راه‌اندازی می‌کند. به منظور اتصال گوشی، اجازهٔ ورودی TCP/86 را فقط روی شبکهٔ خصوصی مورداعتماد فعال کنید؛ سرور را مستقیماً به اینترنت عمومی متصل نکنید.

### توکن همگام‌سازی

پس از اولین شروع، توکن محلی در `server\data\networkall.token` ساخته می‌شود. محتوای فایل را در Android → Settings → API token وارد کنید. این توکن به‌صورت پیش‌فرض داخل سورس عمومی hard-code نشده است.

برای اجرای دستی فقط روی همان PC، سرور به‌صورت پیش‌فرض روی loopback گوش می‌دهد. اتصال LAN را با تنظیم `NETENC_HOST=0.0.0.0` و فایروال محدود به شبکهٔ خصوصی فعال کنید.

### داده‌های قبلی

بستهٔ ZIP پایگاه دادهٔ شخصی همراه خود ندارد. در اولین اجرای یک پوشهٔ تازه، دیتابیس از همان curriculum ادغام‌شده‌ای ساخته می‌شود که در APK استفاده می‌شود. فایل‌های دیتابیس نصب قبلی را بدون نسخهٔ پشتیبان حذف یا جایگزین نکنید؛ Seed خودکار، دیتابیس موجود را به‌صورت مخرب بازنویسی نمی‌کند.

## ۲) اندروید

1. در [GitHub Actions](https://github.com/MrUtility01/NetworkAll/actions)، اجرای موفق `NetworkAll Android APK (validated)` را باز کنید.
2. Artifact با نام `NetworkAll-Android-v1.0.0` را دانلود و APK داخل آن را نصب کنید.
3. در اولین اجرا یک رمز ورود محلی و تأیید آن تنظیم کنید (رمز را در اولین اجرا خودتان انتخاب می‌کنید). این قفل رمزگذاری دیتابیس نیست.\n4. مجوز اعلان را در Android، در صورت درخواست، بدهید.
5. Settings → API host: `http://IP-کامپیوتر:86`.
6. Settings → API token: همان متن فایل `server\data\networkall.token` در ویندوز.
7. روی هر دو دستگاه از یک شبکهٔ محلی قابل‌دسترسی استفاده کنید و ابتدا Sync/Hello را بررسی کنید.

**هشدار به‌روزرسانی:** Application ID برابر `com.netenc.app` باقی مانده است. بااین‌حال، پیش از uninstall یا Clear data از اطلاعات شخصی بکاپ بگیرید. Clear data داده‌های محلی را پاک می‌کند و فقط برای رفع seed ناقص، با داشتن بکاپ، استفاده شود.

## ۳) بازسازی و اعتبارسنجی محتوا

از ریشهٔ مخزن، در Python 3.11+:

```bat
python scripts\export_android_index.py
python scripts\merge_content_packs_into_android.py
python scripts\validate_android_curriculum.py
python scripts\generate_android_diagrams.py
python scripts\package_windows_v1.py
```

Workflow اندروید همین زنجیره را اجرا می‌کند و سپس APK را بررسی می‌کند. APK تنها زمانی خروجی تأییدشده است که Workflow سبز باشد و کنترل محتویات بسته نیز موفق شود.

## ۴) پروتکل Sync

- `GET /api/sync/hello`
- `GET /api/sync/manifest?since=<iso>`
- `POST /api/sync/pull`
- `POST /api/sync/push`

وجود endpoint به‌تنهایی همگام‌سازی کامل Tasks، Notes و Study Progress را اثبات نمی‌کند. پیش از اتکا به داده‌های مهم، ایجاد، ویرایش، حذف، تعارض، قطع شبکه و بازیابی بکاپ را در هر دو جهت آزمایش کنید. مشخصات و محدودیت‌ها در [docs/SYNC_PROTOCOL.md](docs/SYNC_PROTOCOL.md) و [docs/V1_RELEASE_AUDIT_FA.md](docs/V1_RELEASE_AUDIT_FA.md) آمده است.
