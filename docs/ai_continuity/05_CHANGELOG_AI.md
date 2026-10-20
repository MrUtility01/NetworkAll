# 05 — CHANGELOG AI

---

## [2026-10-20 evening] — Grok

### Done (دقت روی کارت یادگیری)
- Updated `02_CONTENT_SCHEMA.md`:
  - Lesson جدید = تک‌سطحی (level: flat)
  - تعریف سخت‌گیرانه و کامل **Learning Card** (concept / tip / gotcha / checklist / command_card)
  - قوانین کیفیت عنوان، body، related_lessons، difficulty
- Created first high-quality flat lesson for Chapter 1:
  - `tools/chapters/1/lessons/flat_lessons_ch01.json` → درس «پردازنده (CPU) — از صفر تا انتخاب سازمانی»
- Created 5 high-quality Learning Cards:
  - `tools/chapters/1/notes/learning_cards_ch01.json`
  - concept, tip, gotcha, checklist, command_card
- Updated `03_PROGRESS.md`

### Quality focus
کارت‌های یادگیری مستقل، عملی، بدون تکرار متن درس، با عنوان خودکفا و لینک به درس اصلی ساخته شدند.

---

## [2026-10-20] — Grok

### Done
- User confirmed final structure:
  - ۳۰ فصل (سخت‌افزار + ۲۹ فصل قبلی)
  - فقط سطح مبتدی + متوسط
  - هر مبحث فقط **یک سطح** (بدون L0–L4 و بدون سطح پیشرفته جدا)
  - تمام مطالب داخل همان فصل
- Updated `docs/ai_continuity/MEGA_CHAPTER_MAP.md` to final 30-chapter flat version.
- Created branch `feature/29-chapter-flat-structure`.
- Added `tools/chapters/INDEX_30_FLAT_FA.md`.
- Migration will start from Chapter 1 (مبانی IT و سخت‌افزار).

### Next
1. Create placeholder structure for new chapters 1–30 under tools/chapters/ (or packs).
2. Migrate content of old chapters 1–5 into new Chapter 1 (flat, beginner+intermediate).
3. Update full_curriculum.py / chapter_loader / Android & Windows to support 30 chapters and single-level lessons.

---

## [2026-10-18] — Grok

### Done
- Registered user request for mega-chapter curriculum.
- Created `docs/ai_continuity/MEGA_CHAPTER_MAP.md` with:
  - 20 mega-chapters (M01–M20)
  - Network = single full chapter (M03)
  - Cisco = single full chapter (M04)
  - MikroTik = single full chapter (M05)
  - Mapping from old chapters 01–68 → new mega-chapters
  - Recommended pack folder layout

### Waiting
User confirmation on the proposed map before any curriculum code or mass migration.

### Note
Existing deep packs (Cisco, MikroTik, FortiGate, Windows Server, VPN, Routing, etc.) will be preserved and moved under the matching mega-chapter folders after approval.
