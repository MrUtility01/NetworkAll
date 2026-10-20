# جداسازی کامل داده‌ها + سیستم Import کاربر

**تاریخ:** ۲۰۲۶-۱۰-۲۰  
**وضعیت:** قطعی و اجباری برای تمام محتوای جدید و آینده  
**شاخه:** `feature/29-chapter-flat-structure`

این سند دو مورد درخواستی کاربر را با حداکثر دقت تعریف می‌کند:

1. **جداسازی کامل انواع داده**
2. **قابلیت Import توسط خود کاربر**

---

# بخش ۱ — جداسازی کامل داده‌ها (Data Separation)

هدف: تغییر ظاهر برنامه، فریم‌ورک، یا حتی بازنویسی کامل UI نباید ما را مجبور کند دانشنامه را دوباره تولید کنیم.

## ۱.۱ جدول انواع داده و محل ذخیره

| نوع داده          | شناسه پیشوند          | محل ذخیره محتوا (منبع حقیقت)              | محل ذخیره پیشرفت کاربر          | توضیح |
|-------------------|-----------------------|-------------------------------------------|----------------------------------|-------|
| **درس**           | `lesson:`             | `tools/chapters/N/lessons/`               | جدول `user_lesson_progress`     | شناسه، فصل، مبحث، پیش‌نیاز، زمان مطالعه |
| **سؤال**          | `q:`                  | `tools/chapters/N/questions/`             | جدول `user_quiz_attempts`       | صورت سؤال + گزینه‌ها (بدون جواب) |
| **پاسخ**          | همان uid سؤال         | `tools/chapters/N/answers/`               | —                               | جواب صحیح + توضیح (جدا از سؤال) |
| **فلش‌کارت**      | `note:`               | `tools/chapters/N/notes/`                 | جدول `user_card_reviews`        | front، back، درجه دشواری، سابقه مرور |
| **دستور**         | `cmd:`                | `tools/chapters/N/commands/` + فصل ۳۰     | —                               | پلتفرم، نسخه، کاربرد، پارامتر، مثال |
| **آزمایشگاه**     | `lab:`                | `tools/chapters/N/labs/`                  | جدول `user_lab_progress`        | تجهیزات، مراحل، نتیجه مورد انتظار، عیب‌یابی |
| **پیشرفت کاربر**  | —                     | —                                         | دیتابیس محلی (Room / SQLite)    | درس‌های تکمیل‌شده، نمره آزمون، مرورهای سررسید |

## ۱.۲ قوانین سخت جداسازی

1. **هیچ فایل درسی حق ندارد جواب سؤال را داخل خود نگه دارد.** جواب فقط در `answers/` است.
2. **فلش‌کارت باید `front_fa` و `back_fa` مستقل داشته باشد** تا برنامه بتواند آن را به عنوان کارت واقعی نمایش دهد.
3. **دستورات** هم داخل درس (برای یادگیری) و هم در فصل ۳۰ (برای جست‌وجوی سریع) قابل دسترسی هستند، اما رکورد اصلی یکتاست.
4. **پیشرفت کاربر هرگز داخل فایل‌های محتوا ذخیره نمی‌شود.** فقط در دیتابیس محلی دستگاه.
5. هر رکورد باید `uid` پایدار و یکتا داشته باشد. تغییر عنوان یا متن محتوا نباید uid را عوض کند.
6. رابطه بین رکوردها فقط از طریق uid انجام می‌شود (نه از طریق شماره ردیف یا ترتیب فایل).

## ۱.۳ جداول پیشنهادی دیتابیس پیشرفت کاربر (هر دو پلتفرم)

```sql
-- درس‌های تکمیل‌شده و زمان مطالعه
CREATE TABLE user_lesson_progress (
  uid TEXT PRIMARY KEY,                -- lesson:ch01:cpu:001
  status TEXT,                         -- not_started | in_progress | completed
  started_at TEXT,
  completed_at TEXT,
  time_spent_seconds INTEGER DEFAULT 0,
  last_position TEXT,                  -- برای ادامه از همان جا
  updated_at TEXT
);

-- سابقه آزمون
CREATE TABLE user_quiz_attempts (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  question_uid TEXT,
  selected_answer TEXT,
  is_correct INTEGER,
  attempted_at TEXT
);

-- مرور فلش‌کارت (Spaced Repetition)
CREATE TABLE user_card_reviews (
  card_uid TEXT PRIMARY KEY,
  ease_factor REAL DEFAULT 2.5,
  interval_days INTEGER DEFAULT 1,
  repetitions INTEGER DEFAULT 0,
  next_review_at TEXT,
  last_review_at TEXT,
  last_result TEXT                     -- again | hard | good | easy
);

-- پیشرفت لاب
CREATE TABLE user_lab_progress (
  lab_uid TEXT PRIMARY KEY,
  status TEXT,
  started_at TEXT,
  completed_at TEXT,
  notes TEXT
);
```

## ۱.۴ نتیجه جداسازی

- می‌توانید کل UI را عوض کنید → محتوا دست‌نخورده می‌ماند.
- می‌توانید از Kotlin به Flutter یا از Flask به FastAPI بروید → فقط لایه نمایش عوض می‌شود.
- می‌توانید محتوا را در Git نگه دارید و پیشرفت کاربر را فقط روی دستگاه.
- Sync فقط پیشرفت و تغییرات کاربر را جابه‌جا می‌کند، نه کل دانشنامه را.

---

# بخش ۲ — سیستم Import توسط کاربر (User Import)

هدف: کاربر بتواند خودش بسته محتوا بسازد و وارد برنامه کند تا به فهرست فصل‌ها اضافه شود.

## ۲.۱ فرمت بسته Import (NetworkAll Content Pack)

هر بسته یک فایل **ZIP** با پسوند پیشنهادی `.nacp` (NetworkAll Content Pack) است.

### ساختار داخل ZIP

```
my-pack.nacp  (یا .zip)
├── manifest.json                 ← الزامی
├── lessons/
│   └── lessons.json
├── notes/
│   └── learning_cards.json
├── questions/
│   └── questions.json
├── answers/
│   └── answer_key.json
├── commands/
│   └── commands.json
├── labs/
│   └── labs.json
└── media/                        ← اختیاری (فقط تصویر کوچک یا SVG)
    └── ...
```

### نمونه manifest.json (الزامی و سخت‌گیرانه)

```json
{
  "pack_schema_version": 1,
  "pack_id": "user.jokar.cpu-extra.2026-10",
  "title_fa": "مباحث تکمیلی پردازنده",
  "title_en": "CPU Extra Topics",
  "description_fa": "بسته‌ای که خودم ساختم برای نکات بیشتر CPU",
  "author": "ENGINEER JOKAR",
  "created_at": "2026-10-20",
  "target_chapter_order": 1,
  "target_chapter_mode": "merge",          // merge | new_chapter
  "new_chapter_title_fa": null,
  "compatibility": {
    "min_app_version": "1.0.0",
    "preserve_existing_uids": true
  },
  "counts": {
    "lessons": 2,
    "notes": 8,
    "questions": 10,
    "answers": 10,
    "commands": 5,
    "labs": 1
  },
  "content_files": [
    "lessons/lessons.json",
    "notes/learning_cards.json",
    "questions/questions.json",
    "answers/answer_key.json",
    "commands/commands.json",
    "labs/labs.json"
  ]
}
```

### قوانین اعتبارسنجی Import (اجباری)

برنامه قبل از وارد کردن باید این موارد را چک کند:

1. وجود `manifest.json` و معتبر بودن JSON
2. `pack_schema_version` پشتیبانی‌شده باشد
3. تمام فایل‌های اعلام‌شده در `content_files` وجود داشته باشند
4. هر رکورد `uid` یکتا داشته باشد
5. اگر `uid` قبلاً در دیتابیس وجود دارد → رفتار طبق `preserve_existing_uids`
6. سوال بدون پاسخ متناظر یا پاسخ بدون سوال رد شود
7. فلش‌کارت بدون `front_fa` یا `back_fa` رد شود
8. حجم کل بسته از حد معقول (مثلاً ۲۰ مگابایت) بیشتر نباشد
9. فقط فیلدهای تعریف‌شده در Schema پذیرفته شوند (فیلد اضافی نادیده گرفته شود)

## ۲.۲ رفتار بعد از Import موفق

| حالت | رفتار |
|------|--------|
| `target_chapter_mode = "merge"` | محتوا به فصل مشخص‌شده (`target_chapter_order`) اضافه می‌شود |
| `target_chapter_mode = "new_chapter"` | یک فصل جدید در انتهای فهرست ساخته می‌شود و عنوان از `new_chapter_title_fa` گرفته می‌شود |
| درس‌های جدید | در فهرست درس‌های همان فصل ظاهر می‌شوند |
| فلش‌کارت‌ها | وارد سیستم مرور فاصله‌دار می‌شوند |
| سوالات | در آزمون‌های فصل قابل استفاده می‌شوند |
| دستورات | هم در درس و هم در جست‌وجوی دستورات دیده می‌شوند |

## ۲.۳ محل ذخیره بسته‌های واردشده توسط کاربر

- **ویندوز:** `server/data/user_packs/` + ثبت در جدول `imported_packs`
- **اندروید:** پوشه داخلی اپ `files/user_packs/` + ثبت در Room

محتوای واردشده توسط کاربر **هرگز** با محتوای اصلی Git قاطی نمی‌شود مگر اینکه کاربر صریحاً بخواهد آن را به مخزن اضافه کند.

## ۲.۴ رابط کاربری پیشنهادی

**ویندوز و اندروید:**

- دکمه «وارد کردن بسته محتوا»
- انتخاب فایل `.nacp` یا `.zip`
- نمایش خلاصه manifest (عنوان، تعداد درس، تعداد کارت، ...)
- دکمه تأیید بعد از اعتبارسنجی
- پیام موفقیت + تعداد رکوردهای اضافه‌شده
- امکان حذف بسته واردشده (بدون تأثیر روی پیشرفت کاربر اگر بخواهد نگه دارد)

## ۲.۵ نمونه بسته آماده برای تست

یک بسته نمونه کوچک در مسیر زیر قرار می‌گیرد:

```
tools/import_samples/sample_cpu_extra.nacp/
```

(بعد از تأیید این سند ساخته خواهد شد)

---

# خلاصه اجرایی

| مورد | وضعیت |
|------|--------|
| جداسازی درس / سؤال / پاسخ / فلش‌کارت / دستور / لاب / پیشرفت | تعریف کامل و اجباری |
| Schema فلش‌کارت با front/back + spaced repetition | آماده |
| فرمت Import (`.nacp`) | تعریف کامل |
| قوانین اعتبارسنجی Import | تعریف کامل |
| محل ذخیره بسته‌های کاربر | تعریف کامل |
| جدا بودن پیشرفت کاربر از محتوا | تعریف کامل |

این دو مورد از این لحظه بخشی از قوانین پروژه هستند و هر تغییر آینده باید با آن‌ها سازگار باشد.
