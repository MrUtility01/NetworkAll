# ادغام فصل ۶۸ — NetworkAll

فصل دستورات پس از ادغام باید در مجموعه‌های واضح مانند Linux، Bash، PowerShell، Windows CMD/Batch، Cisco و MikroTik دیده شود. عدد نهایی رکورد از JSON فشردهٔ تولیدشده به دست می‌آید؛ به عدد ثابت قدیمی تکیه نکنید.

## زنجیرهٔ ساخت

از ریشهٔ مخزن:

```bash
python scripts/export_android_index.py
python scripts/merge_content_packs_into_android.py
python scripts/validate_android_curriculum.py
python scripts/generate_android_diagrams.py
python scripts/package_windows_v1.py
```

Workflow اصلی همین زنجیره را اجرا می‌کند؛ سپس APK را assemble و دارایی‌های واقعی داخل آن را بررسی می‌کند. بستهٔ Windows از همان curriculum فشرده استفاده می‌کند تا در Seed دیتابیس تازه، عنوان‌ها و UIDها با Android هماهنگ باشند.

برای دریافت خروجی قابل‌تأیید، فقط Artifact یک اجرای سبز در [GitHub Actions](https://github.com/MrUtility01/NetworkAll/actions) را دریافت کنید.

## SQLite ویندوز

`tools/apply_any_pack.py` فقط رکوردهای موجودی را که match می‌کند به‌روزرسانی می‌کند؛ برای ورود مجموعهٔ جدید `commands[]` به مسیر seed مشترک اعتماد کنید. پیش از دستکاری دیتابیس موجود، بکاپ بگیرید.
