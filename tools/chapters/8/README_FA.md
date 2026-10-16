# فصل ۰۸: IPv4، IPv6 و Subnetting

محتوای مرجع فصل در همین مسیر و بر اساس ساختار ماژولار مخزن نگهداری می‌شود. محتوای درس‌های پایه از `lessons/base_curriculum.json` می‌آید و فایل‌های category برای مثال، دستور، لابراتوار، سؤال و پاسخ‌نامه به همان UID درس متصل‌اند.

## مسیرهای مرجع

- `lessons/base_curriculum.json`: برنامهٔ پایه و ۱۳۵ عنوان درس.
- `examples/examples.json`: مثال‌های عملی مرتبط با درس‌ها.
- `commands/commands.json`: دستورهای Windows، PowerShell، Linux و Cisco IOS؛ برخی دستورات وابسته به سیستم/نسخه هستند.
- `labs/labs.json`: لابراتوارهای subnetting، IPv6 و طراحی شبکه.
- `questions/questions.json`: بانک سؤال؛ کلید پاسخ در فایل مستقل قرار دارد.
- `answers/answer_key.json`: پاسخ‌نامهٔ جداگانه و قابل تطبیق با UID سؤال.
- `android/` و `windows/`: متادیتای پلتفرم؛ محتوای اصلی از منابع مشترک همین فصل خوانده می‌شود.
- `build/chapter.json`: خروجی تولیدشده؛ دستی ویرایش نشود.
- `source_archive/`: آرشیو منابع اولیه؛ منبع فعال build نیست.

## موضوعات

IPv4 و آدرس‌های ویژه، RFC1918، APIPA، subnet mask/CIDR، VLSM/FLSM، summarization، IPv6 و انواع آدرس، SLAAC/DHCPv6/NDP و طراحی سگمنت‌های Users/Servers/Voice/CCTV/Guest/Management/DMZ.

## اعتبارسنجی

JSONها باید UTF-8 و JSON معتبر باشند، `schema_version` و `chapter_order` حفظ شوند، و UIDهای رکوردهای category با UIDهای درس/سؤال هماهنگ باشند. پس از تغییر منابع، build و تست‌های برنامه باید اجرا شوند؛ این commit صرفاً اعتبار ساختاری JSON و تعداد رکوردها را بررسی می‌کند و ادعای اجرای build برنامه ندارد.
