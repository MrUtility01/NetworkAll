# چیدمان استاندارد مخزن (منبع حقیقت)

هدف: **سرعت، پایداری، یک مسیر مشخص** — نه پراکندگی فایل.

## ریشه مجاز

```
NetworkAll/
  .github/workflows/build-android-apk.yml   ← تنها workflow
  README.md / INSTALL_FA.md
  android/          ← اپ اندروید
  server/           ← Flask + SQLite
  shared/           ← پروتکل sync مشترک
  scripts/          ← export/merge/icon
  tools/
    packs/          ← فقط JSON محتوای نهایی (منبع ادغام)
    chapter_prompts/ ← فقط پرامپت متنی
    commands_encyclopedia/ ← پرامپت/SCHEMA دستورات (نه JSON حجیم)
    scenarios_200/  ← پرامپت سناریو
    audit_content.py / apply_any_pack.py
    engineer_jokar_*/  ← پک‌های موضوعی قدیمی (مجاز)
  docs/             ← مستندات
  windows/          ← راهنمای ویندوز
```

## قانون طلایی محتوا

| نوع | کجا | کجا نگذار
|-----|-----|----------|
| JSON نهایی درس/دستور | `tools/packs/<موضوع>/` | `prompts/`، ریشه، `docs/` |
| پرامپت ChatGPT | `tools/chapter_prompts/` یا `commands_encyclopedia/prompts/*.md` | کنار JSON ۱۰ مگابایتی |
| آرشیو zip | `tools/_archive_zips/` | ریشه |
| Asset اندروید | `android/.../curriculum_index.json.gz` | کپی پراکنده |

## فصل‌های منطقی برنامه

| order | معنی |
|------|------|
| 1–63 | هسته curriculum |
| 64 | Git |
| 65 | امنیت دفاعی + وایرلس |
| 66 | مسیریابی عمیق |
| 67 | VPN سازمانی |
| 68 | دانشنامه دستورات |

## ادغام (فقط packs)

```bash
python scripts/merge_content_packs_into_android.py
```

اسکریپت **فقط** این‌ها را می‌خواند:
- `tools/packs/**/*.json`
- `tools/engineer_jokar_*/*pack*.json` و `*curriculum*.json`
- `tools/ENGINEER_JOKAR_*.json`

نمی‌خواند: `prompts/`، zip، md، فایل با فاصله در نام (توصیه: rename).

## Actions

فقط یک workflow: **NetworkAll Android APK (validated)** (دستی).
هیچ workflow اضافی نباید اضافه شود مگر نیاز قطعی.

## نام‌گذاری JSON

- انگلیسی، بدون فاصله: `cisco_switching.json`، `mikrotik.json`
- نه: `chapter_68_ mikrotik.json`، `file.json.json`
