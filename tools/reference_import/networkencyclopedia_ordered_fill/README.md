# Staged reference packs from NetworkEncyclopedia

These are reference snapshots from `MrUtility01/NetworkEncyclopedia` staged for the NetworkAll release pipeline:

- `ordered_fill/*.json`: ordered, deep lessons for existing chapters.
- `real_lessons_core_pack.json`: a core pack with additional real lessons.

Do not move these files into `tools/packs/` directly. The production content merger can replace fields on exact-title matches, and older/smaller packs may overwrite better NetworkAll material. Instead, `scripts/import_networkencyclopedia_reference.py` validates these staged lesson records, skips existing/duplicate titles, assigns deterministic UIDs to genuinely new lessons, marks them `review_required`, and appends them to the shared curriculum index used by Android and Windows.

The importer runs after chapter export and the normal content-pack merge, then before final curriculum validation. Windows is seeded from that same generated index, so the two platforms receive the same imported lessons.

Five staged JSON files required syntax normalization because the source snapshots contained unescaped line breaks, invalid backslash escapes, or embedded quote characters. The lesson wording and examples were preserved; the source `NetworkEncyclopedia` repository was not modified. Imported technical content remains marked for expert review.
