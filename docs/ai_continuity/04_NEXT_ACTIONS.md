# 04 — NEXT ACTIONS

**Last updated:** 2026-10-20

## Priority 0 — 30-Chapter Flat Structure (CONFIRMED)

User confirmed:
- ۳۰ فصل (سخت‌افزار به عنوان فصل ۱)
- فقط مبتدی + متوسط
- هر مبحث فقط یک سطح (بدون L0-L4 و بدون پیشرفته جدا)
- شروع از ابتدا

**Current branch:** `feature/29-chapter-flat-structure`

### Immediate next steps
1. Create skeleton folders for new chapters 1–30 (under `tools/chapters/` or `tools/packs/`).
2. Migrate old chapters 1–5 content into **new Chapter 1** (مبانی IT و سخت‌افزار) as single-level lessons containing beginner-to-intermediate material.
3. Update `server/core/full_curriculum.py`, `chapter_loader.py`, and related loaders to use the new 30-chapter list and flat structure.
4. Update Android Room schema / manifests and Windows starter to match.
5. Keep old 68-chapter data readable during transition (compatibility layer).

### After Chapter 1 is migrated
- Proceed sequentially: Chapter 2 → 3 → 4 → ...
- Critical path after hardware: 4 (IPv4/IPv6), 7 (Cisco Switching), 8 (Routing), 11 (FortiGate), 14 (MikroTik), 30 (Commands).

## Agent instruction

```
1. Read docs/ai_continuity/MEGA_CHAPTER_MAP.md (final 30-chapter version)
2. Start migration from Chapter 1 (hardware)
3. All new lessons must be single-level (beginner + intermediate content inside one lesson)
4. Do not create advanced-only lessons
```
