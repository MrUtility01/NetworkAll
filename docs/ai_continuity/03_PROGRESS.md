# 03 — PROGRESS (Single Source of Truth)

**Last updated by:** Grok — 2026-10-20  
**Overall status:** بیس رسمی ۹ بخشی + فلش‌کارت با مرور فاصله‌دار قفل شد. اولین بسته کامل درس فصل ۱ آماده است.

---

## بیس قطعی محتوا (تأیید کاربر)

هر مبحث باید این اجزا را داشته باشد:

1. آموزش نظری
2. نکات کلیدی
3. مثال‌های تشریحی
4. جداول مرجع
5. دستورات عملی
6. سناریوهای عملی (Lab)
7. عیب‌یابی
8. پرسش‌وپاسخ (سوال و پاسخ جدا)
9. محتوای یادگیری (فلش‌کارت با front/back + spaced repetition، آزمون، تمرین)

---

## وضعیت فصل ۱ (مبانی IT و سخت‌افزار)

| جزء | فایل | وضعیت |
|-----|------|--------|
| درس کامل (۹ بخشی) | `lessons/flat_lessons_ch01.json` | آماده (CPU) |
| فلش‌کارت / Learning Cards | `notes/learning_cards_ch01.json` | ۶ کارت با front/back + spaced_repetition |
| سوالات | `questions/questions_flat_ch01.json` | ۵ سوال |
| پاسخ‌نامه | `answers/answer_key_flat_ch01.json` | ۵ پاسخ + توضیح |
| Lab عملی | `labs/labs_flat_ch01.json` | ۱ لاب کامل |

---

## مراحل بعدی

1. ادامه درس‌های فصل ۱ (مادربرد، RAM، Storage، اسمبل، BIOS/UEFI، سرور سخت‌افزاری) با همین قالب کامل.
2. اتصال loaderها و اپ (Android/Windows) به فایل‌های flat جدید و پشتیبانی از front/back فلش‌کارت و spaced repetition.
3. مهاجرت تدریجی بقیه فصل‌ها.

Schema رسمی: `docs/ai_continuity/02_CONTENT_SCHEMA.md`
