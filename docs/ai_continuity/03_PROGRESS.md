# 03 — PROGRESS (Single Source of Truth)

**Last updated by:** ChatGPT — 2026-10-15  
**Overall status:** Chapter richness policy registered; full 68-chapter evidence audit is **pending**. Do not treat the earlier preliminary inventory as a completed validation.

---

## Active chapter policy

- Chapters 1–67 default to **فوق‌حرفه‌ای**.
- Target text/structured content: **2 MiB per chapter**.
- Media cap: **5 MiB per chapter**, accounted separately.
- Per chapter: **100 independent examples, 150 independent troubleshooting scenarios, 100 exam questions**, with answer keys stored separately.
- Chapter 68 exception: **خبره**, 5 MiB text/structured target, media cap 5 MiB separately, same example/scenario/question counts, explanations not required.
- File size is not scientific quality. Duplicate/template-only records do not count toward quotas.

## Verified changes in this update

- Registered canonical policy and Chapter 68 exception in `CHAPTER_RICHNESS_AUDIT.md`.
- Updated agent onboarding and project hard constraints so future agents must read and follow the policy.
- Rewrote next actions around an evidence-backed 68-row inventory and Android/Windows parity.
- This update records policy only; it does **not** assert that all chapters have been audited, enriched, or validated.

## Audit work still required

1. Establish exact canonical title and content paths for all 68 chapters.
2. Measure per-chapter text/structured bytes and media bytes separately, including Android compressed asset and Windows runtime/database footprint where measurable.
3. Count records and unique IDs for lessons/examples/scenarios/questions; validate answer-key mapping.
4. Detect exact and near duplicates; inspect scientific coverage and practical depth.
5. Validate schema and test Android + Windows ingestion/display/build.
6. Publish evidence, counts, defects and status for every chapter.

## Architecture references

- `docs/CONTENT_ARCHITECTURE.md`
- `docs/ai_continuity/01_PROJECT_RULES.md`
- `docs/ai_continuity/CHAPTER_RICHNESS_AUDIT.md`

## Previously reported inventory (preliminary; re-check before relying on it)

The older audit noted 5185 lessons in the Android index and large dedicated packs for several topics. Those observations are not equivalent to 68-chapter validation. The exact title map, per-chapter byte counts, duplicate counts and Windows parity still need evidence.
