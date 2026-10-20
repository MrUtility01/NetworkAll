# 02 — CONTENT SCHEMA (نسخه Flat / ۳۰ فصلی)

**آخرین به‌روزرسانی:** ۲۰۲۶-۱۰-۲۰  
**تغییر کلیدی:** برای محتوای جدید، سطح‌بندی L0–L4 حذف شد. هر درس فقط یک سطح دارد و از صفر تا متوسط را پوشش می‌دهد.

Canonical schemas for all content types. Every agent must follow these exactly.

---

## Package envelope

```json
{
  "package_schema_version": 2,
  "project": "ENGINEER JOKAR / NetworkAll",
  "generated_on": "YYYY-MM-DD",
  "purpose": "...",
  "compatibility": {
    "preserve_existing_records": true,
    "preserve_existing_uids": true,
    "questions_and_answers_separate": true
  },
  "content_type": "lessons|scenarios|packet_journeys|diagrams|scripts|notes",
  "items": []
}
```

---

## Lesson (درس — تک‌سطحی)

برای محتوای جدید (از فصل ۱ به بعد در ساختار ۳۰تایی):

**فیلدهای الزامی:**
- `uid` (پایدار و یکتا، مثال: `lesson:ch01:cpu:001`)
- `chapter_order` (۱ تا ۳۰)
- `lesson_order` (ترتیب داخل فصل)
- `title_fa`, `title_en`
- `summary` (۱–۲ جمله)
- `full_content` (Markdown کامل، حداقل ۱۸۰۰–۲۵۰۰ کاراکتر، ترجیحاً بیشتر)
- `learning_objectives` (لیست ۳–۷ هدف)
- `source_status`: `"review_required"` یا `"approved"`

**فیلدهای توصیه‌شده قوی:**
- `topic`, `subchapter_order`
- `commands[]`, `examples[]`, `notes[]` (یا ارجاع به learning cards)
- `diagrams[]` (mermaid + ascii)
- `related_scenarios[]`, `scripts[]`
- `meta.assessment` (سوالات مرتبط بدون پاسخ)

**قوانین سطح:**
- `level` را برای محتوای جدید روی `"flat"` بگذارید یا حذف کنید.
- **هیچ** درسی با عنوان یا سطح «پیشرفته / L3 / L4 / خبره» ساخته نمی‌شود.
- محتوای درس باید از صفر (مبتدی) شروع شود و تا سطح متوسط عملیاتی کامل باشد.
- ۱۰ بخش پیشنهادی داخل `full_content`:
  1. معرفی و پیش‌نیاز
  2. آموزش از صفر + تشبیه سازمانی
  3. معماری / سازوکار فنی
  4. مثال مرحله‌ای
  5. دستورات با خروجی مورد انتظار
  6. لابراتوار ایمن (Lab)
  7. عیب‌یابی (Symptom → Verify → Fix)
  8. نکات امنیتی
  9. خلاصه + واژه‌نامه
  10. چک‌لیست تسلط

**سازگاری با محتوای قدیمی:** درس‌های قبلی که هنوز L0–L4 دارند حفظ می‌شوند تا مهاجرت کامل شود.

---

## Learning Card / Note / کارت یادگیری (دقت بسیار بالا)

کارت‌های یادگیری برای مرور سریع، فلش‌کارت، نکات کلیدی و چک‌لیست استفاده می‌شوند. UI اندروید و ویندوز روی این‌ها حساب می‌کند.

```json
{
  "uid": "note:ch01:cpu:cache:001",
  "type": "concept|tip|gotcha|checklist|command_card",
  "title_fa": "عنوان کوتاه و دقیق (حداکثر ۶۰ کاراکتر)",
  "body_fa": "متن کامل کارت. واضح، عملی، بدون آب. برای concept حداقل ۱۵۰ کاراکتر، برای tip/gotcha حداقل ۸۰ کاراکتر.",
  "related_lessons": ["lesson:ch01:cpu:001"],
  "tags": ["cpu", "cache", "hardware"],
  "chapter_order": 1,
  "difficulty": "مبتدی|متوسط",
  "source_status": "review_required"
}
```

### انواع کارت و قوانین کیفیت

| type | کاربرد | حداقل کیفیت |
|------|--------|-------------|
| **concept** | تعریف مفهوم کلیدی + چرا مهم است | توضیح واضح + یک مثال کوتاه سازمانی |
| **tip** | نکته عملی میدانی | مستقیم و قابل اجرا |
| **gotcha** | تله رایج / اشتباه متداول | «چیزی که اغلب اشتباه می‌شود + راه درست» |
| **checklist** | چک‌لیست قبل/حین/بعد کار | لیست شماره‌دار یا بولت، قابل تیک زدن |
| **command_card** | دستور + توضیح کوتاه + خروجی مورد انتظار | فقط دستورات ایمن و رایج |

**قوانین سخت برای کارت یادگیری:**
- عنوان باید خودکفا باشد (بدون نیاز به خواندن درس).
- body_fa باید کامل و مستقل باشد.
- هیچ کارت خالی یا template-مانند مجاز نیست.
- هر کارت حداقل یک `related_lessons` داشته باشد.
- برای فصل‌های جدید: فقط difficulty = مبتدی یا متوسط.
- از تکرار عین متن درس خودداری کنید؛ کارت باید خلاصه یا زاویه متفاوت باشد.

---

## Scenario (Break/Fix)

```json
{
  "uid": "scenario:ch01:s001",
  "code": "CH01-S001",
  "title_fa": "...", "title_en": "...",
  "difficulty": "مبتدی|متوسط",
  "business_context": "...",
  "incident": "...",
  "symptoms": [], "tasks": [], "hints": [],
  "solution": "...", "verification": [],
  "skills_required": [], "estimated_hours": 1–3,
  "vendors": [], "related_chapters": [],
  "lab_environment": "...",
  "safety_note": "فقط محیط آزمایشگاهی مجاز",
  "scripts": [], "diagrams": []
}
```

(برای محتوای جدید level حذف یا flat شود.)

---

## Packet Journey / Diagram / Script

همان ساختار قبلی حفظ می‌شود. برای محتوای جدید `level` را flat یا حذف کنید.

---

## قوانین کلی جدید (اجباری از ۲۰۲۶-۱۰-۲۰)

1. محتوای جدید فقط مبتدی + متوسط.
2. هر مبحث فقط یک درس اصلی (نه ۵ سطح).
3. کارت‌های یادگیری با کیفیت بالا و مستقل.
4. سوال و پاسخ همیشه جدا.
5. uid پایدار حفظ شود تا پیشرفت کاربر و Sync نشکند.
6. full_content واقعی و عمیق باشد، نه template تکراری.
