# فصل ۶۰ — عیب‌یابی هک اخلاقی لاب سازمانی

**وضعیت:** `review_required`؛ پیش از انتشار نهایی، اعتبارسنج پروژه و build برنامه باید اجرا شود.

## شمار محتوا پس از تکمیل
- ۲۴۰ عنوان پایه و ۲۴۰ رکورد غنی‌سازی‌شده با تطبیق عنوان
- ۱۰۰ سؤال و ۱۰۰ پاسخ‌نامه مستقل
- ۶۰ مثال عملی
- ۶۰ رکورد دستورات و بررسی‌ها
- ۲۰ لابراتوار

## محورهای آموزشی
- RCA و روش‌های Bottom-Up، Top-Down، Divide and Conquer و Follow the Path
- Known-Good، Baseline، Change History و هم‌بستگی لاگ‌ها
- ابزارهای Windows/Linux، DNS/DHCP، routing، firewall و packet capture
- Nmap محدود به Scope و مجوز کتبی؛ Rules of Engagement و شرط توقف
- شواهد قابل تکرار، مدیریت تغییر، Verify، rollback و گزارش incident

## ساختار
فایل‌های canonical در `lessons/`, `questions/`, `answers/`, `examples/`, `commands/`, `labs/` هستند. منابع اولیه در `source_archive/` حفظ شده‌اند. `build/chapter.json` تولیدی است و نباید دستی ویرایش شود.

## ایمنی
فقط لاب ایزوله یا دارایی دارای مجوز کتبی. اسکن خارج از Scope، تست حجمی علیه سرویس واقعی، جمع‌آوری payload حساس و تغییر production بدون Change Request ممنوع است. با خروج از Scope یا اثر ناخواسته، تست متوقف و شواهد حفظ شود.
