# ساختار ماژولار فصل‌ها

هر فصل جدید را در پوشه‌ای مستقل قرار بدهید. فایل‌های این مسیر به‌صورت خودکار توسط اسکریپت ادغام اندروید خوانده می‌شوند:

```text
tools/chapters/
  README_FA.md
  69-linux/
    chapter.json
  70-git/
    chapter.json
```

هر فایل JSON باید یک بستهٔ محتوای استاندارد داشته باشد و در ریشهٔ آن `chapter_order`، `chapter_title_fa` و `chapter_title_en` تعریف شود. محتوای آموزشی در آرایهٔ `lessons` قرار می‌گیرد.

نمونهٔ حداقلی:

```json
{
  "schema_version": 1,
  "chapter_order": 69,
  "chapter_title_fa": "فصل ۶۹: لینوکس",
  "chapter_title_en": "Linux Administration",
  "lessons": [
    {
      "uid": "lesson:ch69:linux:0001",
      "subchapter_order": 1,
      "lesson_order": 1,
      "level": "L1",
      "title_fa": "ساختار فایل‌سیستم لینوکس",
      "title_en": "Linux Filesystem Hierarchy",
      "summary": "آشنایی با مسیرها و پوشه‌های اصلی لینوکس.",
      "full_content": "## هدف\nشناخت مسیرهای اصلی فایل‌سیستم و کاربرد آن‌ها.\n\n## آزمایش\nدستور `ls -la /` را اجرا و خروجی را بررسی کنید.",
      "commands": "ls -la /",
      "examples": "ls -la /",
      "notes": "lab: inspect the root filesystem"
    }
  ]
}
```

## قرارداد محتوا

- شمارهٔ فصل در `chapter_order` باید یکتا باشد؛ فصل‌های موجود را بدون قصد جایگزینی دوباره شماره‌گذاری نکنید.
- هر درس یک `uid` پایدار و یکتا داشته باشد.
- برای سازگاری، `title_fa`, `summary`, `full_content`, `commands`, `examples` و `notes` را نگه دارید.
- محتوای هر فصل را فقط در پوشهٔ خودش نگه دارید؛ از قرار دادن توکن، رمز، دیتابیس شخصی یا اطلاعات محرمانه در Git خودداری کنید.
- پس از اضافه‌کردن فصل، ادغام اندروید را با `python scripts/merge_content_packs_into_android.py` اجرا و خروجی را بررسی کنید.

> نکته: فایل‌های JSON ریشهٔ `tools/chapters/` با این قرارداد طراحی شده‌اند؛ برای واردسازی در ویندوز، مسیر دیتابیس و اسکریپت واردسازی باید جداگانه پیکربندی شود. این مستند به‌تنهایی به معنی اضافه‌شدن خودکار به دیتابیس ویندوز نیست.
