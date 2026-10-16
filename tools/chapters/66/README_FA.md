# فصل 66: مسیریابی عمیق OSPF/BGP/Redistribution

مسیر اصلی: `tools/chapters/66/`

این فصل روی مفاهیم پیشرفته مسیریابی، عیب‌یابی همسایگی OSPF، سیاست‌های BGP و Redistribution امن تمرکز دارد. محتوای منبع در فایل‌های جداگانه نگهداری می‌شود؛ `build/chapter.json` خروجی تولیدی سازگاری است و نباید دستی ویرایش شود.

## فایل‌های مرجع

- `lessons/base_curriculum.json`: تعریف سه درس پایه که runtime از آن استفاده می‌کند.
- `lessons/lessons.json`: نه درس افزوده درباره OSPF، SPF/Cost، adjacency، BGP، eBGP/iBGP، peering، redistribution، metric و loop prevention.
- `commands/commands.json`: دستورات مشاهده‌ای اختصاصی هر درس برای Cisco IOS/IOS-XE.
- `examples/examples.json`: مثال‌های عملی و قابل‌راستی‌آزمایی متناسب با هر درس.
- `questions/questions.json`: ۲۷ سؤال تخصصی چندگزینه‌ای.
- `answers/answer_key.json`: ۲۷ پاسخ مستقل با توضیح و شناسه متناظر.
- `labs/labs.json`: ۹ سناریوی لابراتواری شامل OSPF Multi-Area، BGP peering، policy و جلوگیری از حلقه.
- `manifest.json`: شمار رکوردها و وضعیت بازبینی.

## ایمنی و اعتبارسنجی

لابراتوارها برای شبیه‌سازهای ایزوله مانند GNS3/EVE-NG/CML نوشته شده‌اند. قبل از هر تغییر، baseline بگیرید و Rollback را آماده کنید. از اعلان Prefix آزمایشی یا تغییر سیاست در شبکه عملیاتی خودداری کنید.

وضعیت فعلی `review_required` است: ساختار JSON و تطبیق شناسه‌ها باید کنترل شود و Build واقعی برنامه‌های Android و Windows هنوز تأیید نهایی لازم دارد.
