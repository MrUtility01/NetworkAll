# 04 — NEXT ACTIONS

**Last updated:** 2026-10-15 — richness targets registered; full audit still pending.

## Priority 0 — Required before claiming any chapter is complete

1. Build the 68-row audit inventory from canonical curriculum/source data. Record exact title and source path for every chapter.
2. For each chapter, measure text/structured source size, compressed and uncompressed Android asset contribution, Windows runtime/database contribution, and media size separately.
3. Count unique lessons, independent examples, independent scenarios and exam questions; check separate answer-key coverage.
4. Run exact/near-duplicate detection and scientific-coverage gap review.
5. Validate schema and stable unique IDs; verify Android and Windows both ingest/display the intended content.
6. Publish findings and gaps in `CHAPTER_RICHNESS_AUDIT.md` before doing broad enrichment. Mark completion only after evidence-backed validation.

## Per-chapter target selection

- User-facing 68-row selection form: `docs/ai_continuity/CHAPTER_TARGET_SELECTION.md`.
- Ask the user to confirm or change each chapter's level, text/structured size target, separate media ceiling, independent examples, independent scenarios, exam questions, and explanation requirement before starting broad enrichment.
- Do not infer a chapter-specific target from content size. Do not claim audit/enrichment completion until measurements, duplicate checks, coverage review, schema checks, and Android/Windows integration evidence are recorded.

## Canonical targets

- Chapters 1–67 default: **فوق‌حرفه‌ای**, 2 MiB text/structured content per chapter, media cap 5 MiB separately, 100 independent examples, 150 independent scenarios, 100 exam questions.
- Chapter 68 exception: **خبره**, 5 MiB text/structured content, media cap 5 MiB separately, 100 examples, 150 scenarios, 100 exam questions, explanations not required.
- Size is not a quality score; no repeated filler to reach quotas. See `CHAPTER_RICHNESS_AUDIT.md`.

## Priority 1 — Known high-risk content gaps (reconfirm against the new audit)

1. Chapter 40 — migrate/expand old VMware/Hyper-V content into canonical structure.
2. Chapter 60 — continue the labs pack; validate real scenario/question counts.
3. Chapter 51 — expand automation content and verify its canonical integration.
4. Thin/partial chapters identified by the 68-row evidence audit, not by approximate titles alone.

## Agent instruction

```
1. Read docs/ai_continuity/00_START_HERE.md, 01_PROJECT_RULES.md, 02_CONTENT_SCHEMA.md,
   03_PROGRESS.md, 04_NEXT_ACTIONS.md, 05_CHANGELOG_AI.md, and CHAPTER_RICHNESS_AUDIT.md.
2. Verify canonical titles and content locations for all 68 chapters.
3. Run measurable audit checks before proposing enrichment.
4. Enrich in bounded batches under the correct canonical tools/packs/chXX_* structure.
5. Update manifest + 03_PROGRESS.md + this file + 05_CHANGELOG_AI.md.
6. Never claim completion without evidence and Android/Windows checks.
```
