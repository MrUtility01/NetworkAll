# چیدمان استاندارد مخزن

هدف: یک مسیر مرجع برای هر نوع داده، بارگذاری تدریجی در UI و حفظ تمام محتوای ارزشمند. منبع canonical فایل‌های JSON آموزشی، tools/packs/ است.

## ریشه پروژه

NetworkAll/
  .github/workflows/ — آزمون و ساخت APK
  android/ — اپ Kotlin آفلاین + Room + WorkManager
  server/ — Flask، SQLite، رابط وب و برنامه‌ریز ویندوز
  shared/ — منطق Sync مشترک و infographics/ (HTML + SVG، منبع مشترک هر دو سکو)
  scripts/ — export، merge و ساخت asset اندروید
  tools/
    packs/ — تنها محل JSON نهایی آموزشی، به تفکیک موضوع
    engineer_jokar_*/ — ابزار ساخت/اعتبارسنجی و READMEهای موضوعی
    commands_encyclopedia/ — schema و prompt؛ نه JSON حجیم
    chapter_prompts/ — پرامپت‌های فصل
    scenarios_200/ — طرح‌ریزی سناریوها
    audit_content.py / apply_any_pack.py — ممیزی و واردسازی
  docs/ — معماری، Sync، استاندارد عمق L0–L4، کیفیت محتوا و وضعیت
  windows/ — راهنمای ویندوز، در صورت وجود

## نقشه بسته‌های JSON

| مسیر | دامنه |
|---|---|
| tools/packs/automation_python/ | پایتون شبکه و اتوماسیون |
| tools/packs/security_ethical_hacking/ | امنیت دفاعی |
| tools/packs/wireless_security/ | WLAN و امنیت بی‌سیم |
| tools/packs/routing_deep/ | مسیریابی عمیق و CLI |
| tools/packs/vpn_enterprise/ | VPN سازمانی |
| tools/packs/switching_routing/ | سوئیچینگ/مسیریابی |
| tools/packs/windows_server/ | Windows Server |
| tools/packs/commands_encyclopedia/ | دستورات Cisco/MikroTik |
| tools/packs/git_chapter64/ | محتوای Git متنی |

تعریف ماشینی مسیرهای رسمی در tools/packs/pack_catalog.json نگه‌داری می‌شود.

## فصل‌های منطقی برنامه

| شماره | حوزه |
|---|---|
| 1–63 | هسته curriculum |
| 64 | Git |
| 65 | امنیت دفاعی و Wireless |
| 66 | Routing عمیق |
| 67 | VPN سازمانی |
| 68 | مرجع دستورات |

این شماره‌ها یک نقشهٔ منطقی هستند؛ کیفیت علمی و کامل بودن تک‌تک درس‌ها باید جداگانه با گزارش ممیزی و بررسی فنی تأیید شود.

## گالری اینفوگرافیک

منبع واحد نمودارها در `shared/infographics/` است. صفحهٔ `index.html` در وب ویندوز با مسیر `/infographics` سرو می‌شود و همان پوشه به Android assets اضافه می‌شود؛ برای نگهداری نمودارها نسخهٔ جداگانهٔ Android نسازید. هر SVG باید XML معتبر، توضیح alt، شرح آموزشی و پشتیبانی از نمایش باریک/چاپ داشته باشد.

استاندارد حجم و عمق آموزشی در `docs/CONTENT_DEPTH_STANDARD_FA.md` تعریف شده است؛ تعداد رکوردها سقف کلی ندارد و باید از ماتریس پوشش مهارت‌ها و سناریوهای متمایز محاسبه شود.

## قوانین مهم

- هیچ JSON محتوایی جدیدی در ریشه tools یا engineer_jokar_* نسازید.
- فایل‌های بسیار بزرگ به معنی مجاز بودن بارگذاری کل فایل در هر درخواست نیست: فهرست‌ها lazy-load و نتایج جست‌وجو محدود باشند.
- محتوا را به دلیل کوتاه بودن پاک نکنید؛ ابتدا گزارش شکاف، سپس بازنویسی و تطبیق UID.
- پایگاه داده و پیشرفت کاربر را با seed اجباری پاک نکنید.
- محتوای آزمون و answer_key جدا باشند.
- هر import بزرگ ابتدا dry-run، backup، تراکنش و گزارش دقیق تغییرات داشته باشد.

## ممیزی و ساخت

    python tools/audit_content.py --packs-only --json docs/audits/content-audit.json
    python scripts/merge_content_packs_into_android.py

Workflow ساخت APK ابتدا syntax و regression test را اجرا می‌کند و سپس JSONها را merge می‌کند. شکست merge نباید به‌صورت warning نادیده گرفته شود.
