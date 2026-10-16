# چیدمان استاندارد مخزن (منبع حقیقت)

هدف: **یک پروژه واحد، تجربهٔ کاملاً یکسان ویندوز و اندروید، حجم کنترل‌شده، گسترش‌پذیری بالا**.

## ریشه مجاز

```
NetworkAll/
  .github/workflows/          ← CI (ساخت APK و ...)
  README.md / INSTALL_FA.md
  android/                    ← اپ اندروید
  server/                     ← Flask + SQLite (ویندوز)
  shared/                     ← پروتکل sync مشترک
  scripts/                    ← assemble / merge / export
  tools/
    chapters/                 ← ★ منبع حقیقت اصلی محتوا (۱ تا ۶۸)
      index.json              ← فهرست ماشینی
      INDEX_FA.md             ← فهرست انسانی
      README_FA.md            ← قرارداد ساختار
      1/ … 68/                ← هر فصل ماژولار
    packs/                    ← بسته‌های تخصصی (در حال مهاجرت)
    chapter_prompts/          ← پرامپت تولید محتوا
    commands_encyclopedia/    ← دانشنامه دستورات
    audit_content.py
    apply_any_pack.py
  docs/                       ← مستندات (STRUCTURE.md و ...)
  windows/                    ← راهنما و لانچر ویندوز
```

## قانون طلایی محتوا

| نوع | کجا | کجا نگذار |
|-----|-----|----------|
| درس، سوال، پاسخ، مثال، دستور، لاب | `tools/chapters/N/` | تکرار در android/ یا windows/ |
| فهرست ماشینی | `tools/chapters/index.json` | — |
| پرامپت تولید | `tools/chapter_prompts/` | کنار JSON حجیم |
| آرشیو zip | `tools/_archive_zips/` | ریشه |
| Asset نهایی اندروید | `android/.../curriculum_index.json.gz` | کپی پراکنده |
| ویدیو / فیلم / فایل حجیم | **ممنوع** | — |

## فصل‌های منطقی برنامه

| order | معنی |
|------|------|
| 1–63 | هسته curriculum |
| 64 | Git و GitHub |
| 65 | امنیت دفاعی + وایرلس |
| 66 | مسیریابی عمیق OSPF/BGP |
| 67 | VPN سازمانی |
| 68 | دانشنامه جامع دستورات |

## یکسان‌سازی ویندوز و اندروید

- هر دو پلتفرم از **همان** پوشه‌های `tools/chapters/N/` می‌خوانند.
- پوشه‌های `windows/` و `android/` داخل هر فصل فقط تنظیمات جزئی پلتفرم دارند.
- هیچ محتوای آموزشی تکراری وجود ندارد.
- حجم کم می‌ماند چون فقط متن + JSON است.

## ادغام و ساخت

```bash
python scripts/assemble_chapter_packs.py --strict
python scripts/merge_content_packs_into_android.py
```

اسکریپت‌ها فایل‌های canonical داخل `tools/chapters/` را می‌خوانند و خروجی نهایی را برای هر دو پلتفرم تولید می‌کنند.

## نام‌گذاری

- پوشه فصل: فقط عدد (`1`, `2`, … `68`)
- UID رکوردها: پایدار و یکتا (`ch01-lesson-001`, `ch01-q-015`, …)
- JSON: انگلیسی، بدون فاصله

این چیدمان برای تجربهٔ یکسان و گسترش بلندمدت طراحی شده است.
