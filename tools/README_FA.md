# راهنمای پوشه tools

این پوشه ابزارهای مدیریت محتوا و اسکریپت‌های آموزشی را نگه‌داری می‌کند. **تنها محل JSONهای نهایی آموزشی، tools/packs/** است. اسکریپت‌های ساخت و اعتبارسنجی در پوشه‌های مهندسی باقی می‌مانند.

## ساختار

- tools/packs/ — مخزن استاندارد JSONهای نهایی، پوشه‌بندی‌شده بر اساس موضوع
- tools/packs/pack_catalog.json — فهرست رسمی مسیرها و وضعیت ممیزی
- tools/engineer_jokar_automation_python/ — سازنده، اعتبارسنجی و importer بسته Python/Automation؛ خروجی JSON در tools/packs/automation_python/
- tools/engineer_jokar_security_ethical_hacking/ — اعتبارسنجی و راهنمای محتوای امنیت دفاعی؛ JSON زیر tools/packs/security_ethical_hacking/
- tools/engineer_jokar_wireless_security/ — مستندات و ابزارهای WLAN؛ JSON زیر tools/packs/wireless_security/
- tools/commands_encyclopedia/ — schema، پرامپت‌ها و مراحل نگارش؛ خروجی JSON زیر tools/packs/commands_encyclopedia/
- tools/chapter_prompts/ — پرامپت‌های فصل
- tools/audit_content.py — گزارش ممیزی فقط‌خواندنی

## واردسازی

از ریشه مخزن، ابتدا فقط پیش‌نمایش بگیرید:

    python tools/apply_any_pack.py --db server/data/encyclopedia.db --pack tools/packs/automation_python/automation_python_curriculum_pack.json

برای اعتبارسنجی بسته اتوماسیون:

    python tools/engineer_jokar_automation_python/validate_pack.py

برای گزارش کیفیت همه JSONها:

    python tools/audit_content.py --packs-only --json docs/audits/content-audit.json

فرمان --all اکنون فایل‌های tools/packs/**/*.json را هم شامل می‌کند. پیش از هر اعمال واقعی، دیتابیس را پشتیبان‌گیری کنید و dry-run را بررسی کنید.

## ساخت/بازسازی بسته Automation

    python tools/engineer_jokar_automation_python/build_content_pack.py

این اسکریپت خروجی را مستقیماً در tools/packs/automation_python/ می‌نویسد. JSON نهایی را در پوشه اسکریپت کپی نکنید.

## اندروید

Workflow ساخت اندروید پس از export، JSONهای canonical زیر tools/packs را برای ادغام بررسی می‌کند و در خروجی GZip آفلاین تولید می‌کند. نام فایل‌ها انگلیسی و بدون فاصله باشد. پرامپت، ZIP آرشیوی و JSON تولیدی را در یک پوشه مخلوط نکنید.

جزئیات بیشتر در [docs/CONTENT_GOVERNANCE_FA.md](../docs/CONTENT_GOVERNANCE_FA.md) آمده است.
