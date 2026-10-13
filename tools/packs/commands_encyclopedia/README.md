# JSON دانشنامه دستورات — NetworkAll فصل ۶۸

فایل‌های JSON واقعاً موجود در این پوشه:

- `cisco_switching.json` — Cisco switching، اگر فایل در clone شما معتبر و غیرخالی باشد
- `mikrotik.json` — بستهٔ RouterOS
- `networkall_shell_automation.json` — Linux / Bash / PowerShell / CMD
- `networkall_ops_advanced.json` — عملیات و عیب‌یابی پیشرفته
- `networkall_shell_expanded.json` — ۵۰ رکورد تکمیلی برای Linux، Bash، PowerShell، Windows CMD و Windows Batch

فهرست قدیمی که `cisco_routing.json`, `fortigate.json`, `issabel.json`, `powershell.json` و `ALL.json` را نام می‌برد، به‌تنهایی وجود این فایل‌ها را تضمین نمی‌کند. قبل از ارجاع یا ادغام، نام و JSON واقعی فایل را بررسی کنید.

از ریشهٔ مخزن، زنجیرهٔ ساخت را اجرا کنید:

```bash
python scripts/export_android_index.py
python scripts/merge_content_packs_into_android.py
python scripts/validate_android_curriculum.py
```

Workflow انتشار باید خروجی merge را بررسی کند و هر پنج مجموعهٔ shell را در فصل ۶۸ ببیند. تعداد فرمان‌ها را از فایل‌های واقعی و گزارش Workflow بخوانید، نه از عددهای قدیمی در promptها.
