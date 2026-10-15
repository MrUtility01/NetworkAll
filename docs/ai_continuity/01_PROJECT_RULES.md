# 01 — PROJECT RULES (Hard Constraints)

**Last updated:** 2026-10-15  
**Sources:** this file + docs/STRUCTURE.md + tools/AI_CONTENT_PACK_PROMPT.md

---

## 1. Architecture (do not change)

```
Windows (Flask + SQLite)  ←— Sync LAN —→  Android (Room + assets)
         │                                      │
         └──────── offline-complete ────────────┘
```

- Windows is fully usable without Android.
- Android is fully usable without Windows (seed from curriculum_index.json.gz).
- Sync is optional.

## 2. Content rules

| Rule | Detail |
|------|--------|
| Depth | full_content ≥ 2000 chars = deep (L3/L4 target: 2500–4000+) |
| 10 mandatory sections | Intro, From-zero, Organizational analogy, Architecture, Worked example, Commands+output, Safe Lab, Troubleshooting (Symptom→Verify), Security, Summary+Glossary |
| Q&A separation | questions never contain correct answers; answer_key is separate |
| Lab safety | Only authorized / lab environments. No real-world attacks. |
| uid | Stable: `lesson:chNN:lvMMM:lKKKK` or `scenario:catXX:sNNN` |
| Language | Fluent Persian (title_fa + full_content) + title_en |
| Storage | Only under `tools/packs/<topic>/` |

## 3. Scale generation rules

- Max 15–20 items per JSON file (avoid truncation).
- Always produce title list first → wait for confirmation → then full JSON.
- After every batch update `03_PROGRESS.md` and `05_CHANGELOG_AI.md`.
- Use `python tools/apply_any_pack.py` and `python tools/audit_content.py`.

## 4. Critical chapters (must not stay thin)

8, 13, 14, 20, 24, 29, **51**, **60**

Chapters 40–60 are currently being enriched.

## 5. Forbidden

- Content that violates schema.
- Malicious or real-world attack code.
- Changing core curriculum structure without coordination.
- Committing tokens, real DB files, or private backups.

## 6. Recommended per-chapter layout

```
tools/packs/ch40_vmware_hyperv/
├── lessons/          # lesson JSON batches
├── scenarios/        # Break/Fix scenarios for this chapter
├── packet_journeys/  # Packet path definitions
├── diagrams/         # Mermaid + ASCII diagrams
├── scripts/          # Python / PowerShell automation
├── notes/            # Knowledge cards / tips
└── README.md         # Chapter-specific status
```
