# 00 — START HERE

**Project:** NetworkAll / ENGINEER JOKAR  
**Repository:** https://github.com/MrUtility01/NetworkAll  
**Purpose:** Multi-agent continuity system. Every AI agent MUST read this first.

---

## Mandatory workflow for every new agent

1. Read this file completely.
2. Read in order:
   - `01_PROJECT_RULES.md`
   - `02_CONTENT_SCHEMA.md`
   - `03_PROGRESS.md`
   - `04_NEXT_ACTIONS.md`
   - `05_CHANGELOG_AI.md` (latest entries)\n   - `CHAPTER_RICHNESS_AUDIT.md` (canonical targets and audit status)
   - `CHAPTER_TARGET_SELECTION.md` (the finalized 68-row target register; do not ask for global defaults again, only record explicit per-chapter exceptions)
3. Check `03_PROGRESS.md` before any content work.\n4. Before chapter work, apply the finalized targets in `CHAPTER_TARGET_SELECTION.md` and validation gates in `CHAPTER_RICHNESS_AUDIT.md`; all 68 chapters currently remain audit-pending. Do not infer completion from file size or build success.
4. After every batch, update `03_PROGRESS.md` + `05_CHANGELOG_AI.md`.
5. Never violate rules in `01_PROJECT_RULES.md`.

---

## Directory layout (source of truth)

```
docs/ai_continuity/
├── 00_START_HERE.md
├── 01_PROJECT_RULES.md
├── 02_CONTENT_SCHEMA.md
├── 03_PROGRESS.md
├── 04_NEXT_ACTIONS.md
├── 05_CHANGELOG_AI.md
└── chapter_status/          ← one file per chapter (recommended)
    ├── ch40.md
    ├── ch41.md
    └── ...
```

Content packs live under:

```
tools/packs/
├── ch40_vmware_hyperv/
│   ├── lessons/
│   ├── scenarios/
│   ├── packet_journeys/
│   ├── diagrams/
│   └── scripts/
├── ch41_proxmox_docker/
└── ...
```

---

## Golden rule

> Agents communicate only through these files.  
> No important state may live only in chat history.
