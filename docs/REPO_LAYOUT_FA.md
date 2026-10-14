# چیدمان مخزن NetworkAll v1

این سند ساختار فعلی را توصیف می‌کند؛ بسته‌های prompt با محتوای واقعاً واردشده به برنامه یکسان نیستند.

```text
NetworkAll/
  .github/workflows/build-apk.yml
  README.md / INSTALL_FA.md / VERSION.txt
  android/       ← Kotlin، Room، offline assets
  server/        ← Flask، SQLite، وب و API
  windows/       ← start.bat و راهنمای میزبان
  shared/        ← قرارداد/توابع کمکی Sync
  scripts/       ← export، merge، validate، diagram و package
  tools/
    packs/       ← بسته‌های محتوای JSON فعال
    reference_import/networkencyclopedia_ordered_fill/ ← درس‌های مرجع در انتظار واردسازی کنترل‌شده
    chapter_prompts/
    commands_encyclopedia/
    scenarios_200/
    apply_any_pack.py / audit_content.py
  docs/          ← وضعیت، معماری، پروتکل و ممیزی
```

## منبع فهرست آموزشی

در Workflow خروجی `scripts/export_android_index.py` فهرست ۱–۶۸ را از هسته می‌سازد؛ سپس `scripts/merge_content_packs_into_android.py` بسته‌های فعال را ادغام می‌کند و `scripts/import_networkencyclopedia_reference.py` درس‌های یکتای مرجع را با UID پایدار وارد می‌کند؛ در پایان `scripts/validate_android_curriculum.py` فهرست نهایی را اعتبارسنجی می‌کند.

Asset نهایی:
`android/app/src/main/assets/curriculum_index.json.gz`

بستهٔ Windows v1 همین Asset ادغام‌شده را همراه دارد. در اولین Seed دیتابیس خالی، ویندوز از آن استفاده می‌کند تا ساختار، UID و متن دروس از APK جدا نشود. اجرای source checkout بدون Asset معتبر ممکن است به مسیر legacy برگردد؛ برای انتشار، فقط بستهٔ ساخته‌شده توسط Workflow معتبر است.

## نگاشت فصل‌ها

| فصل | موضوع | نکته |
|---:|---|---|
| 1–63 | هستهٔ عمومی IT/شبکه/زیرساخت | عمق مطالب بین موضوع‌ها یکسان نیست و باید ممیزی شود |
| 64 | Git و GitHub | hook آموزشی از `tools/chapter_git_teacher.py` |
| 65 | امنیت دفاعی و بی‌سیم | به ادغام بسته‌ها وابسته است |
| 66 | OSPF/BGP/Redistribution | به ادغام بسته‌ها وابسته است |
| 67 | VPN سازمانی | به ادغام بسته‌ها وابسته است |
| 68 | دانشنامهٔ دستورات | باید بر اساس مجموعه‌ها مانند Linux، Bash، PowerShell، Windows CMD/Batch، Cisco و MikroTik تفکیک شود |

## قواعد بستهٔ محتوا

- JSON نهایی در `tools/packs/<موضوع>/` قرار بگیرد.
- promptها در مسیرهای prompt بمانند و واردکننده آن‌ها را به‌عنوان درس تلقی نکند.
- UIDها پایدار و یکتا باشند؛ حذف/تغییر UID می‌تواند همگام‌سازی و سابقهٔ مطالعه را بشکند.
- آزمون باید `questions` و `answer_key` جدا داشته باشد؛ دادهٔ جواب نباید در گزینه‌های سؤال افشا شود.
- خروجی Build باید تعداد فصل/درس‌ها و دارایی‌های بسته‌شده را از خود Artifact بخواند، نه از شمار ثابت در README.

## Workflow

تنها Workflow شناخته‌شده برای خروجی اصلی، `NetworkAll Android APK (validated)` در `.github/workflows/build-apk.yml` است. آن را از [Actions](https://github.com/MrUtility01/NetworkAll/actions) اجرا/بررسی کنید. بستهٔ Windows نیز باید از همان اجرای اعتبارسنجی‌شده تولید شود.
