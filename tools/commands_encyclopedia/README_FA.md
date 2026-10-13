# دانشنامهٔ دستورات — NetworkAll فصل ۶۸

فصل دستورات باید بر اساس مجموعه/پلتفرم واضح باشد، نه فقط یک فهرست تخت:

- Cisco IOS/IOS-XE
- MikroTik RouterOS 7
- Linux
- Bash
- PowerShell
- Windows CMD
- Windows Batch
- FortiGate CLI
- Issabel/Asterisk و ابزارهای عمومی، در صورت وجود بستهٔ ممیزی‌شده

## قرارداد هر رکورد

رکورد کامل باید command/title_fa/title_en، platform/vendor/category، syntax، آرگومان‌ها، پیش‌نیاز، کاربرد، مراحل، خروجی نمونه، تفسیر خروجی، دستورات مرتبط، خطاهای رایج، لابراتوار کنترل‌شده، ملاحظات امنیتی و کلمات جست‌وجو داشته باشد. `assessment.questions` و `assessment.answer_key` باید جدا باشند. UID پایدار و یکتا باشد.

## مسیر فایل‌ها

```text
tools/commands_encyclopedia/       # SCHEMA، پرامپت‌ها و مراحل کار
tools/packs/commands_encyclopedia/ # JSONهای واقعیِ واردشونده
scripts/merge_content_packs_into_android.py
scripts/validate_android_curriculum.py
```

## روند ساخت

```bash
python scripts/export_android_index.py
python scripts/merge_content_packs_into_android.py
python scripts/validate_android_curriculum.py
```

برای Release از GitHub Actions استفاده کنید تا asset نهایی داخل APK بررسی شود. Windows v1 نیز همان Asset ادغام‌شده را برای Seed دیتابیس تازه می‌خواند.

**نکتهٔ مهم:** فایل‌های پرامپت/مرحله، خودشان رکورد آموزشی واردشده نیستند. همین‌طور `tools/apply_any_pack.py` تنها محتوای درس‌هایی را که بتواند match کند به‌روزرسانی می‌کند و برای همهٔ شکل‌های `commands[]` جایگزین merge/loader نیست. تعداد هدف در پرامپت را با تعداد واقعی بستهٔ validate‌شده اشتباه نگیرید.
