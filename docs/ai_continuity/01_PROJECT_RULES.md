# 01 — PROJECT RULES (Hard Constraints)

**Last updated:** 2026-10-15  
**Sources:** this file + docs/STRUCTURE.md + docs/CONTENT_ARCHITECTURE.md + tools/AI_CONTENT_PACK_PROMPT.md

---

## 1. Architecture (do not change)

```
Windows (Flask + SQLite)  ←— Sync LAN —→  Android (Room + assets)
         │                                      │
         └──────── offline-complete ────────────┘
```

- Windows is fully usable without Android.
- Android is fully usable without Windows.
- Sync is optional.

## 2. Quality-first policy

- App size may grow significantly. **Acceptable.**
- Thin content is worse than large deep content.
- Prefer 20 excellent lessons over 80 thin ones.
- No UI hang is more important than small APK size.

## 3. Content rules

| Rule | Detail |
|------|--------|
| Depth | full_content ≥ 2000 = deep (L3/L4 target 2500–6000+) |
| 10 mandatory sections | Intro, From-zero, Organizational analogy, Architecture, Worked example, Commands+output, Safe Lab, Troubleshooting (Symptom→Verify), Security, Summary+Glossary |
| Q&A separation | questions never contain correct answers; answer_key separate |
| Lab safety | Only authorized / lab environments |
| uid | Stable and unique |
| Language | Fluent Persian + title_en |
| Storage | Only under `tools/packs/<chapter_slug>/` with subfolders |

## 4. Scalable layout (mandatory for new content)

```
tools/packs/chXX_slug/
├── README.md
├── manifest.json
├── lessons/
├── scenarios/
├── packet_journeys/
├── diagrams/
├── scripts/
└── notes/
```

- Max 12–18 lessons per JSON batch.
- Always update manifest + `docs/ai_continuity/03_PROGRESS.md`.

## 5. Critical chapters

8, 13, 14, 20, 24, 29, **40**, **51**, **60** must reach deep status before adding new thin chapters.

## 6. Forbidden

- Giant single JSON files.
- Content that violates schema.
- Real-world attack code.
- Committing tokens or private DBs.


## 7. Mandatory 68-chapter richness policy (canonical, 2026-10-15)

Before producing or describing chapter content, read `docs/ai_continuity/CHAPTER_RICHNESS_AUDIT.md` and `docs/ai_continuity/CHAPTER_TARGET_SELECTION.md`.

- Chapters 1–67 default: expertise **خبره**, text/structured-content target **5 MiB per chapter**, separate media cap **8 MiB**, 100 independent examples, 150 independent troubleshooting scenarios, 100 exam questions; explanations required.
- Chapter 68 exception: expertise **خبره**, text/structured-content target **5 MiB**, separate media cap **5 MiB**, 100 independent examples, 150 independent scenarios, 100 exam questions; explanations not required.
- Measure text/structure and media separately; distinguish raw source, compressed/uncompressed Android assets and Windows runtime/database sizes.
- Never conflate size with scientific quality. Do not pad targets with duplicate, generic or templated records.
- Keep answer keys separate from question prompts.
- Every chapter remains **ممیزی‌نشده** until actual counts, duplicate checks, scientific coverage, schema validation and Android/Windows parity evidence are recorded.
- A pack existing, JSON parsing, or a successful build alone is not proof of chapter completion.
- Do not claim repository-wide audit completion until the 68-row evidence report is populated and both Android and Windows integration checks have passed.
