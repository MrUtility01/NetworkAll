# فصل ۰۳ — BIOS، UEFI و فرآیند بوت

محتوای افزوده با ساختار نوع‌تفکیک‌شده نگهداری می‌شود. تعریف‌های پایه در `lessons/base_curriculum.json` حفظ شده‌اند و درس‌ها با `merge_strategy: by_title` غنی می‌شوند.

## محتوا
- ۸۰ درس غنی‌شده برای تمام ۸۰ عنوان پایه و سطوح L0 تا L4، با مسیر یادگیری متفاوت در هر سطح
- ۱۶ مجموعه دستور تشخیصی Windows/Linux
- ۱۶ مثال سناریومحور
- ۴۸ سؤال چهارگزینه‌ای و ۴۸ پاسخ تشریحی جدا
- ۱۲ لابراتوار با شواهد، معیار پذیرش و rollback

## ایمنی
پیش از تغییر firmware، TPM، BCD، GRUB یا جدول پارتیشن بکاپ و طرح بازگشت تهیه کنید. ابتدا فرمان‌های مشاهده‌ای را اجرا کنید؛ از `format`، `diskpart clean` و بازنویسی کور bootloader پرهیز کنید. کلید بازیابی BitLocker و سازگاری UEFI/GPT را پیش از تغییر بررسی کنید.

## ساخت
```bash
python scripts/assemble_chapter_packs.py --strict
python scripts/export_android_index.py
python scripts/merge_content_packs_into_android.py
```
`build/chapter.json` و شاخص Android خروجی تولیدی‌اند و نباید دستی ویرایش شوند.
