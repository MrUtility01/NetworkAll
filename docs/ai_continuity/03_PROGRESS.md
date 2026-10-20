# 03 — PROGRESS (Single Source of Truth)

**Last updated by:** Grok — 2026-10-20  
**Overall status:** ساختار ۳۰ فصلی Flat تأیید و شروع شده. مهاجرت فصل ۱ در جریان است.

---

## وضعیت فعلی ساختار جدید (۳۰ فصل Flat)

| مورد | وضعیت |
|------|--------|
| نقشه نهایی ۳۰ فصلی | تأیید شده (`MEGA_CHAPTER_MAP.md`) |
| شاخه کاری | `feature/29-chapter-flat-structure` |
| Schema محتوا (Lesson + Learning Card) | به‌روز شد (نسخه Flat) |
| فصل ۱ — درس اول (CPU) | شروع شد — کیفیت بالا، تک‌سطحی |
| فصل ۱ — کارت‌های یادگیری | ۵ کارت با کیفیت (concept, tip, gotcha, checklist, command_card) |
| بقیه فصل‌ها | pending |

---

## کارهای انجام‌شده در این به‌روزرسانی (۲۰۲۶-۱۰-۲۰)

1. به‌روزرسانی `02_CONTENT_SCHEMA.md` برای ساختار Flat:
   - حذف الزام L0–L4 برای محتوای جدید
   - تعریف دقیق و سخت‌گیرانه **Learning Card** (concept / tip / gotcha / checklist / command_card)
   - قوانین کیفیت برای کارت‌ها

2. شروع مهاجرت فصل ۱:
   - فایل `tools/chapters/1/lessons/flat_lessons_ch01.json` با اولین درس کامل (CPU از صفر تا انتخاب سازمانی)
   - فایل `tools/chapters/1/notes/learning_cards_ch01.json` با ۵ کارت یادگیری باکیفیت و مستقل

3. قوانین محتوا: فقط مبتدی + متوسط، یک سطح در هر مبحث، همه مطالب داخل فصل.

---

## قوانین فعال Learning Card (از این لحظه)

- عنوان خودکفا و حداکثر ۶۰ کاراکتر
- body کامل و مستقل از درس
- حداقل یک related_lessons
- فقط difficulty مبتدی یا متوسط
- هیچ کارت خالی یا template مجاز نیست
- نوع‌ها: concept | tip | gotcha | checklist | command_card

---

## مراحل بعدی فوری

1. ادامه درس‌های فصل ۱ (مادربرد، RAM، Storage پایه، اسمبل، BIOS/UEFI، سرور سخت‌افزاری) با همان کیفیت تک‌سطحی.
2. اتصال loaderها به فایل‌های flat جدید.
3. به‌روزرسانی Android و Windows برای نمایش تک‌سطحی + کارت‌های یادگیری.

---

## یادداشت سازگاری

درس‌ها و محتوای قدیمی با سطح L0–L4 فعلاً حفظ می‌شوند تا مهاجرت کامل شود و پیشرفت کاربران نشکند.
