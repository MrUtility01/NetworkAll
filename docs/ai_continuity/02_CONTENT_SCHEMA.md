# 02 — CONTENT SCHEMA (بیس قطعی دانشنامه + برنامه یادگیری)

**آخرین به‌روزرسانی:** ۲۰۲۶-۱۰-۲۰  
**منبع حقیقت:** تأیید کاربر — قالب ۹ بخشی + فلش‌کارت با مرور فاصله‌دار + آزمون + تمرین عملی

این فایل قانون مطلق تولید محتوا است. هر درس/مبحث جدید باید دقیقاً از این قالب پیروی کند.

---

## اصول کلی (غیرقابل مذاکره)

1. **یک مبحث = یک درس مستقل** با پیش‌نیاز و اهداف یادگیری مشخص.
2. **فقط مبتدی + متوسط** (هیچ سطح پیشرفته جداگانه).
3. **تکرار متنی حذف می‌شود**، اما ارزش آموزشی حفظ می‌شود (مثال‌های متفاوت، دستورات vendor-specific، سوالات مستقل، سناریوهای عیب‌یابی مختلف).
4. سوال و پاسخ همیشه در فایل‌های جدا نگهداری می‌شوند.
5. uid پایدار و یکتا برای حفظ پیشرفت کاربر و Sync.
6. محتوا برای نمایش به صورت جلسه مستقل در برنامه مناسب باشد.

---

## قالب استاندارد هر مبحث / درس (۹ بخش اجباری)

هر درس در `full_content` (Markdown) و فیلدهای ساختاریافته باید این بخش‌ها را پوشش دهد:

| بخش | محتوای موردنیاز |
|-----|-----------------|
| **۱. آموزش نظری** | توضیح کامل، اصول کار، معماری و مفاهیم پایه |
| **۲. نکات کلیدی** | نکات مهم، استثناها، محدودیت‌ها و اشتباهات رایج |
| **۳. مثال‌های تشریحی** | مثال‌های واقعی با توضیح مرحله‌به‌مرحله |
| **۴. جداول مرجع** | مقایسه فناوری‌ها، پروتکل‌ها، گزینه‌ها و کاربردها |
| **۵. دستورات عملی** | دستورهای کامل CLI، پارامترها، خروجی نمونه و کاربرد |
| **۶. سناریوهای عملی** | پیاده‌سازی، طراحی شبکه و آزمایشگاه |
| **۷. عیب‌یابی** | نشانه مشکل، علت‌های احتمالی، روش بررسی و راه‌حل |
| **۸. پرسش‌وپاسخ** | ارجاع به سوالات مفهومی و عملی (پاسخ در answer_key جدا) |
| **۹. محتوای یادگیری** | فلش‌کارت، آزمون، مرور نکات دشوار و تمرین |

---

## Lesson Schema (درس)

```json
{
  "uid": "lesson:ch01:cpu:001",
  "chapter_order": 1,
  "lesson_order": 1,
  "level": "flat",
  "title_fa": "...",
  "title_en": "...",
  "topic": "CPU",
  "prerequisites": ["lesson:ch01:intro:001"],
  "learning_objectives": ["...", "..."],
  "summary": "۱–۲ جمله",
  "full_content": "Markdown با ۹ بخش بالا",
  "key_points": ["نکته ۱", "نکته ۲"],
  "examples": [ { "title": "...", "steps": [], "explanation": "..." } ],
  "reference_tables": [ { "title": "...", "headers": [], "rows": [] } ],
  "commands": [ { "os": "linux|windows|cisco|...", "cmd": "...", "params": "...", "sample_output": "...", "use_case": "..." } ],
  "labs": ["lab:ch01:cpu:001"],
  "troubleshooting": [ { "symptom": "...", "possible_causes": [], "verification": [], "fix": "..." } ],
  "related_questions": ["q:ch01:cpu:001", "q:ch01:cpu:002"],
  "learning_cards": ["note:ch01:cpu:concept:001", "..."],
  "estimated_minutes": 25,
  "difficulty": "مبتدی|متوسط",
  "source_status": "review_required"
}
```

---

## Learning Card / Flashcard (کارت یادگیری + مرور فاصله‌دار)

برای فلش‌کارت و مرور فاصله‌دار طراحی شده است. برنامه باید بتواند پاسخ کاربر و زمان مرور بعدی را ثبت کند.

```json
{
  "uid": "note:ch01:cpu:concept:001",
  "type": "concept|tip|gotcha|checklist|command_card|definition|difference|port|protocol",
  "title_fa": "عنوان کوتاه و خودکفا (≤ ۶۰ کاراکتر)",
  "front_fa": "سوال یا مفهومی که کاربر می‌بیند (برای فلش‌کارت)",
  "back_fa": "پاسخ کامل و مستقل",
  "body_fa": "توضیح تکمیلی (اختیاری، برای نمایش غنی‌تر)",
  "related_lessons": ["lesson:ch01:cpu:001"],
  "tags": ["cpu", "cache"],
  "chapter_order": 1,
  "difficulty": "مبتدی|متوسط",
  "spaced_repetition": {
    "ease_factor_default": 2.5,
    "interval_days_default": 1
  },
  "source_status": "review_required"
}
```

**قوانین کیفیت کارت:**
- `front_fa` و `back_fa` الزامی برای فلش‌کارت واقعی.
- عنوان و front خودکفا باشند.
- تکرار عین متن درس ممنوع؛ کارت باید زاویه خلاصه یا متفاوت داشته باشد.
- فقط مبتدی یا متوسط.

---

## Question + Answer (آزمون و ارزیابی)

سوال و پاسخ همیشه جدا هستند.

**questions.json:**
```json
{
  "uid": "q:ch01:cpu:001",
  "lesson_uid": "lesson:ch01:cpu:001",
  "type": "multiple_choice|true_false|short_answer|scenario",
  "question_fa": "...",
  "options": ["الف", "ب", "ج", "د"],
  "difficulty": "مبتدی|متوسط",
  "tags": [],
  "chapter_order": 1
}
```

**answer_key.json:**
```json
{
  "uid": "q:ch01:cpu:001",
  "correct": "ب",
  "explanation_fa": "توضیح کامل چرا این جواب درست است و بقیه غلط‌اند",
  "related_lesson": "lesson:ch01:cpu:001"
}
```

---

## Lab / Scenario (تمرین و مهارت عملی)

```json
{
  "uid": "lab:ch01:cpu:001",
  "title_fa": "...",
  "difficulty": "مبتدی|متوسط",
  "objective": "...",
  "initial_state": "وضعیت اولیه محیط",
  "required_commands": [],
  "steps": [],
  "expected_result": "...",
  "verification_steps": [],
  "common_errors": [ { "error": "...", "cause": "...", "fix": "..." } ],
  "safety_note": "فقط محیط آزمایشگاهی مجاز",
  "related_lesson": "lesson:ch01:cpu:001"
}
```

---

## Commands (مرجع دستورات داخل درس و فصل ۳۰)

```json
{
  "uid": "cmd:ch01:linux:lscpu",
  "vendor_or_os": "linux",
  "command": "lscpu",
  "parameters": "...",
  "sample_output": "...",
  "use_case": "...",
  "related_lessons": [],
  "chapter_order": 1
}
```

فصل ۳۰ فقط دستورات است (دسته‌بندی‌شده و قابل جست‌وجو).

---

## قوانین تولید محتوا

- هر درس کوچک و مستقل باشد تا در برنامه به صورت یک جلسه نمایش داده شود.
- مثال‌ها، دستورات vendor-specific، سوالات و سناریوهای عیب‌یابی حتی اگر موضوع مشابه باشد، حفظ شوند.
- متن‌های تکراری توضیحی ادغام شوند.
- نسخه و تفاوت‌های فنی مهم مخلوط نشوند.
- full_content حداقل ۱۸۰۰ کاراکتر و غنی باشد.

این Schema از این لحظه بیس تمام تولید محتوا در شاخه `feature/29-chapter-flat-structure` است.
