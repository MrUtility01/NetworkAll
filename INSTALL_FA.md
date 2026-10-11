# نصب و اجرای NetworkAll در Windows و Android

## ۱) Windows

در PowerShell:

```powershell
git clone https://github.com/MrUtility01/NetworkAll.git
cd NetworkAll
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r server/requirements.txt
python -c "import secrets; print(secrets.token_urlsafe(32))"
$env:NETENC_TOKEN = "توکن تصادفی تولیدشده را اینجا قرار بده"
cd server
python app.py
```

توکن فقط در محیط همان PowerShell فعال است. اگر پنجره بسته شد، در پنجره جدید دوباره آن را تنظیم کن. از توکن ساده، شماره تلفن یا عبارت قابل حدس استفاده نکن.

برای اتصال Android:
1. هر دو دستگاه را به یک شبکه Wi-Fi/LAN خصوصی و مورداعتماد وصل کن.
2. در Windows دستور `ipconfig` را اجرا و IPv4 آداپتور همان شبکه را پیدا کن.
3. در Firewall فقط برای شبکه Private و پورت 5050 اجازه ورودی بده.
4. IP و توکن را در تنظیمات اتصال اپ Android وارد کن.
5. هیچ port forwarding روی روتر ایجاد نکن.

برای اجرای صرفاً محلی روی Windows، قبل از `python app.py` بنویس:

```powershell
$env:NETENC_HOST = "127.0.0.1"
```

## ۲) Android

- پوشه `android/` را در Android Studio باز کن.
- Gradle Sync را اجرا کن.
- ابتدا روی شبیه‌ساز/گوشی آزمایش کن؛ برای APK از workflow موجود **Build Android APK** یا Gradle استفاده کن.
- برای همگام‌سازی LAN، IP میزبان و توکن را در تنظیمات اپ وارد کن.
- پیش از حذف داده‌های اپ یا نصب نسخه‌ای که ممکن است داده را بازنشانی کند، از پیشرفت مطالعه و تنظیمات نسخه پشتیبان تهیه کن.

## ۳) ممیزی محتوا

برای گزارش ساختار و نشانه‌های نقص در پک‌ها:

```powershell
python tools/audit_content_packs.py --json reports/content-audit.json
```

این ابزار غیرمخرب است و محتوایی را حذف نمی‌کند. موارد کم‌عمق یا فاقد نشانه‌های آزمایش/پاسخ‌نامه باید از نظر فنی بازبینی شوند.

## ۴) مسیرهای مرجع

- ساختار مخزن: [docs/REPO_LAYOUT_FA.md](docs/REPO_LAYOUT_FA.md)
- ممیزی و نقشه راه: [docs/QUALITY_AND_ROADMAP_FA.md](docs/QUALITY_AND_ROADMAP_FA.md)
- پروتکل همگام‌سازی: [docs/SYNC_PROTOCOL.md](docs/SYNC_PROTOCOL.md)

## نکته امنیتی

بدون تنظیم `NETENC_TOKEN`، APIهای محافظت‌شده و فضای کاری قفل هستند. این برنامه برای استفاده شخصی در شبکه محلی طراحی شده؛ آن را مستقیماً روی اینترنت عمومی منتشر نکن.
