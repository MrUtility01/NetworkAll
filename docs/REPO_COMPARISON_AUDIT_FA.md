# ممیزی مقایسه‌ای NetworkEncyclopedia و NetworkAll

تاریخ: 2026-10-13
مخزن هدف: https://github.com/MrUtility01/NetworkAll
مخزن مرجع: https://github.com/MrUtility01/NetworkEncyclopedia

مقایسه درخت فایل‌ها بین NetworkEncyclopedia/main و شاخه candidate یعنی codex/android-repair-port86-20261013 نشان داد 48 مسیر متنی/کد فقط در مخزن مرجع و 16 مسیر فقط در شاخه candidate هستند. این اختلاف مسیر به‌تنهایی اثبات نمی‌کند محتوای مرجع از اپ حذف شده؛ ممکن است معادل جدید یا merge قبلی وجود داشته باشد. به همین دلیل کل مخزن مرجع نباید روی NetworkAll کپی شود.

نامزدهای مهم برای ممیزی/ادغام افزایشی:
- tools/packs/commands_encyclopedia/linux.json، powershell.json و batch.json
- tools/packs/ordered_fill/ شامل rich_deep_pack_v11.json تا rich_deep_pack_v34.json و بسته‌های تکمیلی
- tools/packs/real_lessons_core/real_lessons_core_pack.json
- tools/packs/scenarios/scenarios_pack_v1.json
- server/core/chapter18_25_teacher.py، infographics.py، pack_loader.py و specialized_depth.py
- tools/import_netmaster/ و windows/INSTALL_LAN_FA.md

این‌ها نامزد ادغام‌اند، نه فایل‌های آمادهٔ کپی؛ انتقال بدون بررسی به tools/packs/**/*.json ممکن است درس و UID تکراری وارد کند.

قابلیت‌های شاخهٔ candidate NetworkAll که باید حفظ شوند: گالری دیاگرام Android و صفحه دیاگرام وب، زمان‌بند/Worker یادآوری Task، smoke-testهای Seed/Vault/Web، تولید 100 SVG، اعتبارسنجی curriculum، بسته‌بندی Windows و سه pack جدید networkall_ops_advanced.json، networkall_shell_automation.json و networkall_shell_expanded.json.

قاعده: backup/hash بگیر؛ UID، عنوان، فصل/زیرفصل، منابع، مثال و answer_key را بررسی کن؛ فقط موارد یکتا را به pack افزایشی منتقل کن؛ اختلاف index/APK/Windows ZIP را گزارش بده و اول روی build/DB آزمایشی تست کن.
