# NetworkAll — دانشنامه شخصی شبکه و زیرساخت IT

دانشنامه local-first برای استفاده شخصی روی Windows و Android؛ محتوای آموزشی، لابراتوار، سناریو، آزمون، جستجو و همگام‌سازی اختیاری در شبکه محلی.

## شروع سریع — Windows PowerShell

```powershell
git clone https://github.com/MrUtility01/NetworkAll.git
cd NetworkAll
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r server/requirements.txt
# یک توکن تصادفی تولید کن و مقدار خروجی را در خط بعد جایگزین کن:
python -c "import secrets; print(secrets.token_urlsafe(32))"
$env:NETENC_TOKEN = "PASTE_A_RANDOM_TOKEN_HERE"
cd server
python app.py
```

سرور روی پورت 5050 اجرا می‌شود. برای اتصال گوشی، Windows و گوشی باید روی شبکه خصوصی مورداعتماد باشند؛ IP محلی Windows را با `ipconfig` پیدا کن و در تنظیمات اتصال اپ وارد کن. اگر Windows Firewall پرسید، دسترسی را فقط برای شبکه Private مجاز کن. پورت را روی روتر به اینترنت forward نکن. اگر فقط روی همان کامپیوتر می‌خواهی، پیش از اجرا `$env:NETENC_HOST = "127.0.0.1"` را تنظیم کن.

**مهم:** بدون `NETENC_TOKEN`، APIهای محافظت‌شده و فضای کاری قفل می‌مانند. توکن را در URL قرار نده و آن را در Git commit نکن.

## Android

Android Studio را روی پوشه `android/` باز کن و از workflow **Build Android APK** یا Gradle build برای ساخت APK استفاده کن. برای نصب روزمره، از APK خروجی همان commit استفاده کن؛ پیش از Clear data از پیشرفت و تنظیمات بکاپ بگیر.

## ساختار

جزئیات چیدمان: [docs/REPO_LAYOUT_FA.md](docs/REPO_LAYOUT_FA.md)  
یافته‌های ممیزی و نقشه راه: [docs/QUALITY_AND_ROADMAP_FA.md](docs/QUALITY_AND_ROADMAP_FA.md)

| مسیر | نقش |
|---|---|
| `server/` | Flask API، SQLite و رابط Windows |
| `android/` | اپ آفلاین Android |
| `shared/` | قرارداد همگام‌سازی مشترک |
| `tools/packs/<موضوع>/` | منبع محتوای آموزشی نهایی |
| `tools/audit_content_packs.py` | ممیزی غیرمخرب عمق/ساختار پک‌ها |
| `scripts/merge_content_packs_into_android.py` | ادغام پک‌ها در asset اندروید |
| `docs/` | معماری، نصب، پروتکل و ممیزی |

## ممیزی محتوای پک‌ها

```powershell
python tools/audit_content_packs.py --json reports/content-audit.json
```

این گزارش موارد کم‌عمق، نبود نشانه‌های لابراتوار/پاسخ‌نامه، شناسه‌های تکراری و JSON نامعتبر را برای بازبینی مشخص می‌کند. این ابزار heuristic است و به‌تنهایی صحت فنی درس را اثبات نمی‌کند؛ هیچ محتوایی را حذف یا تغییر نمی‌دهد.

## افزودن محتوای جدید

1. فایل JSON نهایی را در `tools/packs/<موضوع>/` قرار بده.
2. ساختار و شناسه‌های محتوا را بررسی کن.
3. ممیزی را اجرا کن.
4. ادغام را اجرا و diff را بررسی کن.
5. تست‌های Python و Android را اجرا کن و سپس commit/PR بساز.

## امنیت و داده

- توکن واقعی فقط در متغیر محیطی `NETENC_TOKEN` تنظیم شود.
- داده‌های محلی و پیشرفت مطالعه باید قابل پشتیبان‌گیری و بازیابی باشند.
- برای همگام‌سازی LAN از شبکه خصوصی استفاده کن؛ این برنامه را بدون hardening و HTTPS روی اینترنت عمومی منتشر نکن.
