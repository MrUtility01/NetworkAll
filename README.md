# NetworkEncyclopedia / ENGINEER JOKAR — نسخهٔ کاری NetworkAll

دانشنامهٔ شخصی آموزش شبکه و زیرساخت IT، با نسخهٔ ویندوز (Flask + SQLite) و اندروید (Kotlin + Room). مخزن NetworkAll نسخهٔ کاری و آزمایشگاهی است؛ شاخهٔ main این مخزن تا زمان بازبینی تغییرات به‌عنوان مبنا دست‌نخورده می‌ماند.

## اجرای محلی ویندوز

PowerShell را در ریشهٔ پروژه باز کنید و اجرا کنید:

    cd server
    py -m venv .venv
    .\.venv\Scripts\Activate.ps1
    python -m pip install -r requirements.txt
    $env:NETENC_HOST = "127.0.0.1"
    Remove-Item Env:NETENC_TOKEN -ErrorAction SilentlyContinue
    python app.py

سپس این آدرس‌ها در همان رایانه در دسترس‌اند:

- برنامه: http://127.0.0.1:5050/
- تقویم شمسی و برنامه‌ریز: http://127.0.0.1:5050/planner
- فضای کاری: http://127.0.0.1:5050/workspace

در حالت پیش‌فرض، سرور فقط روی loopback گوش می‌دهد؛ از دستگاه دیگر قابل دسترسی نیست. دادهٔ SQLite و کلید Vault داخل server/data ساخته می‌شوند و در Git قرار نمی‌گیرند.

## فعال‌سازی اختیاری همگام‌سازی گوشی روی LAN

تنها وقتی کامپیوتر و گوشی به یک شبکهٔ خصوصی مورد اعتماد وصل‌اند، PowerShell را با مقادیر زیر راه‌اندازی کنید:

    $env:NETENC_TOKEN = ([guid]::NewGuid().ToString("N") + [guid]::NewGuid().ToString("N"))
    $env:NETENC_HOST = "0.0.0.0"
    python app.py

توکن باید حداقل ۲۴ نویسه باشد. در تنظیمات Firewall ویندوز فقط پورت TCP 5050 را برای پروفایل Private و شبکهٔ خودتان مجاز کنید. آدرس IPv4 کامپیوتر را با ipconfig ببینید و در تنظیمات Sync اندروید به شکل http://IP:5050 وارد کنید. توکن را در فیلد token همان تنظیمات بگذارید.

هشدار: Sync فعلی روی HTTP محلی است و برای شبکهٔ عمومی یا اینترنت طراحی نشده. Port forwarding روتر، NAT ورودی یا دسترسی Public برای این برنامه ایجاد نکنید. برای استفاده از LAN از Wi-Fi مورد اعتماد و Firewall محدود استفاده کنید. اگر نیازی به Sync گوشی ندارید، همان حالت پیش‌فرض 127.0.0.1 امن‌تر است.

## تقویم و یادآوری

- ویندوز: تقویم شمسی، انتخاب روز، سررسید، اولویت و Windows toast reminder. یادآوری به اجرای برنامهٔ سرور و نصب وابستگی‌های requirements نیاز دارد.
- اندروید: تقویم شمسی محلی، کارهای روزانه، اولویت و یادآوری زمان‌دار با WorkManager؛ برای نمایش اعلان، اجازهٔ Notifications را فعال کنید.
- نمایش تقویم شمسی بر اساس قابلیت Persian calendar در مرورگر است؛ مرورگر به‌روز پیشنهاد می‌شود.
- وظایف، یادداشت‌ها و پیشرفت آفلاین برنامه در دیتابیس هر دستگاه ذخیره می‌شوند. این تغییرات هنوز تضمین نمی‌کند که همهٔ وظایف/یادداشت‌ها بین ویندوز و اندروید همگام شوند؛ Sync محتوا و پیشرفت درس از دامنهٔ جداگانه است.

## ساختار پروژه

| مسیر | وظیفه |
|---|---|
| server/ | API، وب، SQLite، فضای کاری و برنامه‌ریز ویندوز |
| android/ | اپ آفلاین Kotlin، Room و WorkManager |
| shared/ | منطق همگام‌سازی مشترک |
| scripts/ | export و merge محتوای اندروید |
| tools/packs/ | تنها مسیر مرجع JSONهای محتوایی |
| tools/engineer_jokar_*/ | اسکریپت‌های تولید/اعتبارسنجی موضوعی |
| docs/ | معماری، پروتکل و سیاست محتوا |

راهنمای ساختار: [docs/REPO_LAYOUT_FA.md](docs/REPO_LAYOUT_FA.md)

استاندارد آموزش و سیاست ممیزی: [docs/CONTENT_GOVERNANCE_FA.md](docs/CONTENT_GOVERNANCE_FA.md)

فهرست رسمی بسته‌ها: [tools/packs/pack_catalog.json](tools/packs/pack_catalog.json)

## بررسی عمق و صحت محتوا

برای ساخت گزارش فقط‌خواندنی از JSONهای محتوایی:

    python tools/audit_content.py --packs-only --json docs/audits/content-audit.json
    python scripts/merge_content_packs_into_android.py
    python tools/audit_content_packs.py --json docs/audits/active-curriculum-audit.json

گزارش اول ساختار و کیفیت منابع JSON را بررسی می‌کند. پس از ادغام، گزارش دوم خودِ asset فعال اندروید را نیز می‌سنجد و رکوردهای کوتاه، فاقد لابراتوار/سناریو/کلید پاسخ، دارای UID تکراری یا متکی بر boilerplate تکراری را مشخص می‌کند. آستانهٔ طول جایگزین بازبینی علمی نیست؛ وضعیت هر بسته در pack_catalog.json شفاف باقی می‌ماند.

هرگز صرفاً به‌دلیل کوتاه بودن یک درس را پاک نکنید. شکاف آن را ثبت و درس را با UID پایدار و محتوای جایگزین کامل کنید. import انبوه باید ابتدا dry-run، backup و سپس گزارش تغییرات داشته باشد.

## آزمون‌ها و ساخت APK

- Python syntax + آزمون‌های رگرسیون: python -m compileall -q server shared scripts tools tests و python -m unittest discover -s tests -v
- Workflow ساخت APK: [.github/workflows/build-apk.yml](.github/workflows/build-apk.yml)
- فایل APK در Artifact اجرای موفق GitHub Actions قرار می‌گیرد. APK تولیدشده برای نصب مستقیم/آزمایش است، نه انتشار فروشگاهی.

## امنیت و داده‌ها

- توکن پیش‌فرض مشترک دیگر وجود ندارد.
- برای سرور محلی از 127.0.0.1 استفاده کنید؛ برای LAN توکن تصادفی طولانی اجباری است.
- Vault ویندوز از AES-GCM و در ویندوز از حفاظت کلید DPAPI استفاده می‌کند؛ اندروید از AES-GCM با Android Keystore استفاده می‌کند.
- فایل‌های DB، vault.key، پشتیبان‌ها و APK را commit نکنید. اگر رمزگشایی Vault خطا داد، فایل کلید را حذف نکنید.
- اسکریپت seed اکنون دیتابیس غیرخالی را خودکار پاک نمی‌کند. برای تعمیرات دستی همیشه backup بگیرید.

## نقشهٔ راه همگام‌سازی ویندوز و اندروید

مشخصات هدف، امنیت LAN، مالکیت داده‌ها، سیاست تعارض و معیارهای پذیرش در [docs/CROSS_PLATFORM_SYNC_SPEC_FA.md](docs/CROSS_PLATFORM_SYNC_SPEC_FA.md) ثبت شده است. پیگیری اجرایی: [Issue #3](https://github.com/MrUtility01/NetworkAll/issues/3).

نکتهٔ مهم: نسخهٔ فعلی دارای پروتکل اولیهٔ sync برای محتواست، اما تا زمانی که آزمون round-trip برای وظایف، یادداشت‌ها و پیشرفت مطالعه در هر دو جهت اجرا نشده باشد، نباید آن داده‌ها را همگام‌شده فرض کرد. Vault نیز تا طراحی انتقال امن کلید، از همگام‌سازی عمومی مستثناست.
