# مرحله ۸ — اعتبارسنجی و انتشار

`ALL.json` فقط وقتی استفاده شود که واقعاً تولید و اعتبارسنجی شده باشد؛ این نام پیش‌فرض/تضمین‌شده نیست.

از ریشهٔ NetworkAll:

```bash
python scripts/export_android_index.py
python scripts/merge_content_packs_into_android.py
python scripts/validate_android_curriculum.py
python scripts/generate_android_diagrams.py
python scripts/package_windows_v1.py
```

سپس commit/push شاخهٔ کاری و Workflow **NetworkAll Android APK (validated)** را باز کنید. APK فقط پس از موفقیت compile و audit داخل فایل، خروجی قابل‌تأیید است. Windows ZIP نیز از همان index ساخته می‌شود.

`tools/apply_any_pack.py` برای به‌روزرسانی محتوای رکوردهای موجود در SQLite طراحی شده است؛ آن را به‌عنوان importer عمومی تمام اشکال `commands[]` فرض نکنید.
