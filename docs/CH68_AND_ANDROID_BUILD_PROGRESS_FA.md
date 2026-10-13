# گزارش مرحله‌ای ساخت اندروید و غنی‌سازی فصل ۶۸

تاریخ شروع: 2026-10-13
شاخه کاری: `codex/android-repair-port86-20261013`
PR کاندید: https://github.com/MrUtility01/NetworkAll/pull/5

## قرارداد ثبت مراحل

هر مرحله باید با commit مستقل انجام شود؛ تغییرات ساخت، ساختار داده، و محتوای هر پلتفرم در یک commit مبهم ادغام نشوند. بعد از هر مرحله:
1. JSON با UTF-8 و ساختار معتبر parse شود.
2. UIDهای تازه یکتا باشند و UIDهای قبلی حفظ شوند.
3. پلتفرم/فروشنده در هر رکورد روشن باشد.
4. خروجی موردانتظار، کاربرد، پیش‌نیاز، اشتباهات رایج، امنیت و تمرین ثبت شود.
5. CI و نتیجهٔ ساخت APK از هم تفکیک شوند؛ سبز بودن CI به معنی آزمون روی گوشی واقعی نیست.

## مراحل برنامه‌ریزی‌شده

- [x] P0 — بررسی گزارش‌های ساخت شناخته‌شده: اجراهای 38435254123 و 38443696157 هر دو موفق گزارش شده‌اند؛ این دو شناسه خطای تازهٔ گزارش‌شده را بازتولید نمی‌کنند.
- [x] P1 — ثبت قرارداد توسعه و گزارش مرحله‌ای.
- [x] P2 — تکمیل دستورالعمل و ساختار فصل ۶۸ برای Cisco IOS/IOS-XE، MikroTik RouterOS, PowerShell, Windows CMD, Windows Batch, Linux و Bash.
- [ ] P3 — افزودن محتوای Cisco Routing با هدف ۱۶۰۰ رکورد مستقل و قابل‌ممیزی؛ بسته آغازین فعلاً ۳۰ رکورد دارد و هدف ۱۶۰۰ هنوز تکمیل نشده است.
- [x] P3a — بسته Cisco Switching افزایشی با ۲۰ رکورد ثبت شد؛ بسته Cisco Routing همچنان ۳۰/۱۶۰۰ است.
- [x] P4 — بسته افزایشی نخست RouterOS/MikroTik ثبت شد: ۲۰ رکورد.
- [x] P5 — بسته مستقل نخست PowerShell ثبت شد: ۲۰ رکورد.
- [x] P6 — بسته مستقل نخست Windows Batch ثبت شد: ۲۰ رکورد.
- [x] P7 — بسته مستقل نخست Linux ثبت شد: ۲۰ رکورد.
- [x] P8a — اعتبارسنجی ساختاری مستقل بسته‌های جدید ثبت شد؛ بررسی مستقیم JSONها در این مرحله ۱۳۰ رکورد و UID یکتا را تأیید کرد. اعتبارسنجی CI باید با اجرای جدید تأیید شود.
- [x] P8b — بسته‌های جانبی مستقل ۵۰ مثال، ۵۰ سناریو، ۵۰ سؤال، ۵۰ پاسخ و ۱۷ URL منبع ثبت شدند؛ شناسه‌های سؤال/پاسخ و ارجاع به فرمان‌ها در بررسی ساختاری تطبیق دارند.
- [ ] P8c — تکمیل Cisco Routing تا ۱۶۰۰ رکورد مستقل؛ فعلاً ۳۰ رکورد ثبت شده است.
- [ ] P9 — آزمون پذیرش روی گوشی واقعی.

## معیار کیفیت رکورد فرمان

هر فرمان باید پلتفرم و نسخهٔ هدف، سطح دسترسی، نحو، آرگومان‌ها، پیش‌نیازها، خروجی نمونهٔ واقع‌گرایانه، تفسیر، خطاهای رایج، ملاحظات امنیتی، فرمان‌های مرتبط، لابراتوار امن و روش verify/rollback داشته باشد. خروجی ساختگی نباید به‌عنوان خروجی واقعی vendor معرفی شود؛ نمونه‌ها باید صریحاً آموزشی/نمونه برچسب بخورند.

## Commitهای مرحله‌ای ثبت‌شده

- گزارش و قرارداد مراحل: `570aa6165562b29d9c348edf3acb9a29369cd5cc`
- بسته Cisco Switching ترمیم‌شده: `ff7ce6714edad50601c6e3a167c5a0a503ae4bc4`
- منابع Cisco Switching: `a0a1b863211b478c00f861e96e2e6b9e95abce64`
- Validator برای Cisco Switching: `e6e8d752db22c14f7b72e4276c794a4229b9c145`
- دستورالعمل فصل ۶۸: `38ae38b519bd8ee65ca1a8cc00fa4d3f3725b90f`
- Cisco Routing (۳۰ رکورد آغازین): `5c5974e58fd4ef118641a711170bad6f26c950bc`
- MikroTik (۲۰ رکورد): `c17f9fce8c35e225d43b75f61ecab3136eb777d7`
- PowerShell (۲۰ رکورد): `489d7249a74d194f4b80488083b43aed084be514`
- Windows Batch (۲۰ رکورد): `54ebe15abbbd85ff1f22f68dc018f4e9af96d2c1`
- Linux (۲۰ رکورد): `26dff223317ecaff3e1bef0c1e71f5d0e919ee5c`
- Validator بسته‌ها: `1fbc91ea4d0694f33f53585b9d52ccaeb0e78150`
- CI برای اعتبارسنجی فصل ۶۸: `1ea67d3a4529d3362e31dd7c78e29b66b1874d80`
- مثال‌های عملی: `b32b008a831f9ee31236bbe2233eeff4e0665979`
- سناریوهای عیب‌یابی: `19add15141b5fddd71999fb3f4eb98b28f76e8e8`
- سؤال‌های مستقل: `ed3399dab260152e1cb6698bdaa4b474f78e8eda`
- پاسخ‌نامه مستقل: `0d33f413df67cfafb11df10766f0e78cb477d14b`
- منابع: `6211e1d9db76d568392e93cd865ea4bb1751e877`
- اعتبارسنجی جانبی: `1028f42dfba21202550d0e61454675900374be22`
- حفظ UIDهای فرمان برای ارجاع: `84229d7d42716589d9448284989ff1b88ef15506` و اصلاح newline: `42decb1bff71019b75fc030fcb823b12c2c9388e`
- نمایه بسته‌ها: `6c8265b66ffa121b8c325beeb955c1474f56d73`

## خطای ساخت اندروید

برای عیب‌یابی خطای جدید باید URL اجرای ناموفق یا log مرحلهٔ شکست در اختیار باشد. اجرای موفق قبلی نمی‌تواند علت خطای جدید را اثبات کند. هر اصلاح Kotlin/Gradle باید با ساخت تازه و audit نهایی APK تأیید شود.


## مرحله افزایشی فصل ۹ — ARP / ICMP / TCP / UDP

- [x] C9-P1 — بسته درس‌های فصل ۹ ساخته شد: ۲۱ درس افزایشی با UIDهای یکتا، سطح‌های L0 تا L4، مدل ذهنی، لاب امن، RCA، امنیت و rollback.
- [x] C9-P2 — ۵۰ مثال عملی با فرمان/ورودی، گام‌ها، خروجی مورد انتظار و تفسیر ساخته شد.
- [x] C9-P3 — ۵۰ سناریوی عیب‌یابی با شواهد، فرضیه، اقدام اصلاحی، verification و rollback ساخته شد.
- [x] C9-P4 — ۵۵ سؤال و پاسخ‌نامه مستقل ساخته شد؛ IDها تطبیق دارند و پاسخ صحیح در فایل سؤال‌ها علامت نخورده است.
- [x] C9-P5 — ۱۶ منبع رسمی/استاندارد و ۸ نمودار با Mermaid، SVG و manifest ثبت شدند.
- [x] C9-P6 — اسکریپت `scripts/validate_ch09_pack.py` افزوده شد و در Workflow پیش از اعتبارسنجی نهایی اجرا خواهد شد.
- [x] C9-P7 — ادغام‌گر برای افزودن درس‌های تازه فصل ۹ بدون حذف درس‌های موجود توسعه یافت.
- [ ] C9-P8 — اجرای تازه GitHub Actions و تأیید نهایی merge/APK هنوز باید از run واقعی بررسی شود.

### فایل‌های فصل ۹

- [بسته درس‌ها](https://github.com/MrUtility01/NetworkAll/blob/codex/android-repair-port86-20261013/tools/packs/ch09/ch09_pack.json)
- [۵۰ مثال](https://github.com/MrUtility01/NetworkAll/blob/codex/android-repair-port86-20261013/tools/packs/ch09/ch09_examples.json)
- [۵۰ سناریو](https://github.com/MrUtility01/NetworkAll/blob/codex/android-repair-port86-20261013/tools/packs/ch09/ch09_scenarios.json)
- [۵۵ سؤال](https://github.com/MrUtility01/NetworkAll/blob/codex/android-repair-port86-20261013/tools/packs/ch09/ch09_questions.json)
- [پاسخ‌نامه مستقل](https://github.com/MrUtility01/NetworkAll/blob/codex/android-repair-port86-20261013/tools/packs/ch09/ch09_answer_key.json)
- [منابع](https://github.com/MrUtility01/NetworkAll/blob/codex/android-repair-port86-20261013/tools/packs/ch09/ch09_sources.json)
- [نمودارها و manifest](https://github.com/MrUtility01/NetworkAll/tree/codex/android-repair-port86-20261013/tools/packs/ch09/diagrams)
- [گزارش اعتبارسنجی](https://github.com/MrUtility01/NetworkAll/blob/codex/android-repair-port86-20261013/tools/packs/ch09/VALIDATION.md)

**محدودیت مهم:** محتوا هنوز `review_required` است. فایل‌های SVG/Mermaid در repository هستند، اما تا زمان اجرای موفق workflow و بررسی loader، نمایش همهٔ نمودارها در UI یا نصب موفق APK ادعا نمی‌شود.
