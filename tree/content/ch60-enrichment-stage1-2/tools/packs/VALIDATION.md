# VALIDATION.md — بسته فصل ۶۰ NetworkAll

**تاریخ تولید:** 2026-10-13  
**وضعیت:** review_required (تمام محتوا)  
**اصل صفر رعایت شد:** هیچ UID موجودی تغییر نکرده، هیچ فایلی overwrite نشده، فقط افزودن افزایشی.

## فایل‌های تولیدشده

| فایل | نقش | وضعیت |
|------|-----|--------|
| `ch60_pack.json` | درس‌های اصلی (اسکلت کامل + ۸ درس غنی اولیه) | مرحله ۱ کامل |
| `ch60_scenarios.json` | ۱۰ سناریوی عملیاتی کامل (نمونه از ۵۰+) | مرحله ۱ کامل |
| `ch60_questions.json` | ۲۰ سؤال آزمون بدون پاسخ | مرحله ۱ کامل |
| `ch60_answer_key.json` | پاسخ‌نامه مستقل با شناسه یکسان | مرحله ۱ کامل |
| `diagrams/ch60/` | پوشه دیاگرام‌ها | آماده برای مرحله ۲ |
| `VALIDATION.md` | این گزارش | — |

## تعداد واقعی رکوردها (مرحله ۱)

- درس در `ch60_pack.json`: **۸** (پوشش L0–L4 برای Symptom-to-Root-Cause + قوانین Authorized Only + Nmap پایه)
- سناریو: **۱۰**
- سؤال: **۲۰**
- پاسخ: **۲۰** (تطبیق ۱۰۰٪ شناسه)

## شکاف‌های باقی‌مانده (برای مراحل بعدی)

1. گسترش درس‌ها به تمام موضوعات ۶۰.۱ تا ۶۰.۵ (حدود ۲۳۰ درس باقی‌مانده با الگوی همین کیفیت)
2. رساندن سناریوها به حداقل ۵۰ (۴۰ سناریوی دیگر)
3. رساندن سؤالات به حداقل ۵۰
4. تولید ≥۵۰ مثال مستقل در فیلد examples یا فایل جدا
5. دیاگرام‌های Mermaid/SVG برای:
   - درخت تصمیم Symptom → Root Cause
   - Sequence Diagram TCP Handshake
   - توپولوژی LAB-01 تا LAB-20
   - State Machine عیب‌یابی
6. لاب‌های مرحله‌به‌مرحله کامل برای هر LAB سازمانی

## منابع معتبر استفاده‌شده (نمونه‌ها)

- Cisco Troubleshooting Methodology (رسمی)
- ITIL 4 Problem Management / Incident Management
- Nmap Reference Guide (nmap.org)
- Wireshark User’s Guide
- NIST SP 800-115 (Technical Guide to Information Security Testing)
- PTES (Penetration Testing Execution Standard) — فقط بخش‌های مجاز و Lab
- RFC 792 (ICMP), RFC 826 (ARP) برای مفاهیم پایه

هیچ URL یا خروجی فرمان جعلی ساخته نشده. تمام فرمان‌ها از مستندات رسمی یا رفتار استاندارد ابزارها هستند.

## دستور ادغام پیشنهادی (پس از بررسی انسانی)

```bash
# بکاپ اجباری
cp server/data/encyclopedia.db server/data/encyclopedia.db.bak_ch60_$(date +%Y%m%d)

# ادغام درس‌ها (dry-run اول)
python tools/apply_any_pack.py --db server/data/encyclopedia.db --pack tools/packs/ch60/ch60_pack.json

# در صورت صحت
python tools/apply_any_pack.py --db server/data/encyclopedia.db --pack tools/packs/ch60/ch60_pack.json --apply

# سپس export برای اندروید
python scripts/export_android_index.py
python scripts/merge_content_packs_into_android.py
```

**توجه:** فایل‌های scenarios و questions ممکن است نیاز به loader جدا یا import دستی به جدول scenarios و meta.assessment داشته باشند (بسته به نسخه فعلی سرور).

## اثر بر سیستم‌ها

- اندروید / ویندوز: فقط محتوای درس‌های match‌شده غنی می‌شود؛ UID و ساختار حفظ می‌شود.
- جستجو: فیلد search_query اضافه شده.
- آزمون: assessment در meta آماده است (جدا از پاسخ).
- Sync / Notes / Tasks / Progress: هیچ تغییری در schema ایجاد نشده → بدون شکست.

## موارد بررسی‌نشده توسط انسان

- صحت علمی تمام جزئیات فرمان در نسخه‌های خاص (IOS-XE 17.x، RouterOS 7، Windows Server 2022، …)
- تست واقعی ادغام روی DB زنده
- بازبینی حقوقی متن‌های مربوط به Ethical Hacking

**این بسته آمادهٔ مرحله ۲ (گسترش درس‌ها و سناریوها) است.**
