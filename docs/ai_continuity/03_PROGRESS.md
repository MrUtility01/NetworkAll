# 03 — PROGRESS (Single Source of Truth)

**Last updated by:** Grok — 2026-10-20  
**Overall status:** منطق Import سمت سرور (ویندوز) کامل پیاده‌سازی و به app متصل شد.

---

## Import سمت سرور (ویندوز) ✅

| جزء | فایل | وضعیت |
|-----|------|--------|
| موتور اعتبارسنجی + Import | `server/core/import_pack.py` | آماده |
| API Routes | `server/import_routes.py` | آماده |
| اتصال به app | `server/app.py` | متصل |
| جداول دیتابیس | content_notes, content_questions, content_answers, content_commands, content_labs, imported_packs | ساخته می‌شوند |
| نمونه بسته | `tools/import_samples/sample_cpu_extra/` | آماده |

### APIهای فعال

```
POST   /api/import/pack          ← آپلود و وارد کردن .nacp / .zip
POST   /api/import/validate      ← فقط اعتبارسنجی
GET    /api/import/packs         ← فهرست بسته‌های واردشده
DELETE /api/import/packs/<id>    ← حذف ثبت بسته
```

### رفتار

- اعتبارسنجی سخت (manifest، uid یکتا، front/back فلش‌کارت، تطابق سوال/پاسخ، محدودیت حجم)
- حالت `merge` → اضافه به فصل موجود
- حالت `new_chapter` → ساخت فصل جدید
- ذخیره بسته در `server/data/user_packs/`
- جداول جدا برای notes / questions / answers / commands / labs

---

## وضعیت کلی

| بخش | وضعیت |
|-----|--------|
| جداسازی داده‌ها | کامل |
| سیستم Import (طراحی + نمونه) | کامل |
| منطق Import سمت سرور | کامل |
| RTL + کارت + مرور فصل (UI) | مرحله بعدی |
| Import سمت اندروید | بعد از UI |
