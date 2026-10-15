# Content Architecture — Professional & Scalable

**Goal:** Highest quality educational content. App size may grow.  
**Non-negotiables:** No UI hang, all features work, easy multi-agent expansion.

---

## 1. Design principles

| Principle | Rule |
|-----------|------|
| Quality first | Prefer deep (2500–6000+ chars) over thin |
| Modular | One chapter = one folder. Never one giant JSON |
| Separation of concerns | Lessons, Scenarios, Packet Journeys, Diagrams, Scripts, Notes are separate |
| Performance | Load only what is needed. Full text stays in DB; UI never loads entire chapter at once |
| Expandable | Adding 500 lessons / 500 scenarios / 500 scripts must remain manageable |
| Multi-agent safe | Every change updates `docs/ai_continuity/` |

---

## 2. Canonical directory layout

```
tools/packs/
├── README.md                          ← this architecture summary
├── _templates/                        ← copy from here
│   ├── chapter_README.md
│   ├── lesson_batch.json
│   ├── scenario_batch.json
│   ├── packet_journey_batch.json
│   ├── diagram_batch.json
│   ├── script_batch.json
│   └── note_batch.json
│
├── ch40_vmware_hyperv/                ← example
│   ├── README.md                      ← status, owners, last audit
│   ├── manifest.json                  ← counts + content hashes
│   ├── lessons/
│   │   ├── batch_01.json
│   │   ├── batch_02.json
│   │   └── ...
│   ├── scenarios/
│   ├── packet_journeys/
│   ├── diagrams/
│   ├── scripts/
│   └── notes/                         ← tips, checklists, knowledge cards
│
├── ch41_proxmox_docker/
├── ch51_automation_ai/
├── ch60_troubleshooting_labs/
└── scenarios_global/                  ← cross-chapter Capstone if needed
```

### Why this layout prevents hang

- Android Room + Windows SQLite load by chapter / by level / by uid.
- Never put 200 lessons in a single JSON file.
- `apply_any_pack.py` processes one pack at a time.
- `curriculum_index.json.gz` can stay as index-only; full bodies live in DB.

---

## 3. File size & batch rules (performance)

| Item | Max recommended |
|------|-----------------|
| Lessons per JSON batch | 12–18 |
| Scenarios per JSON batch | 15–20 |
| Packet journeys per batch | 20 |
| Scripts per batch | 15 |
| Single `full_content` | Prefer < 12 KB (still deep) |
| Total chapter pack on disk | No hard limit — quality wins |

If a batch grows too large, split it. Never merge everything into one file.

---

## 4. manifest.json (required per chapter)

```json
{
  "chapter_order": 40,
  "slug": "vmware_hyperv",
  "title_fa": "فصل ۴۰: VMware Hyper-V",
  "title_en": "Ch40 Virtualization",
  "last_updated": "2026-10-15",
  "status": "in_progress",
  "counts": {
    "lessons": 0,
    "scenarios": 0,
    "packet_journeys": 0,
    "diagrams": 0,
    "scripts": 0,
    "notes": 0
  },
  "depth_summary": {
    "deep": 0,
    "mid": 0,
    "thin": 0
  },
  "batches": [
    "lessons/batch_01.json"
  ],
  "notes": "Target: 15–25 dense lessons before marking complete."
}
```

---

## 5. Content type responsibilities

| Folder | Responsibility | Loaded when |
|--------|----------------|-------------|
| `lessons/` | Core teaching content + assessment | User opens lesson |
| `scenarios/` | Break/Fix + Capstone | Scenario list / Lab mode |
| `packet_journeys/` | Step-by-step packet paths | Related lesson or search |
| `diagrams/` | Mermaid + ASCII architecture | Inside lesson or diagram viewer |
| `scripts/` | Safe Python / PowerShell / automation | Lab or copy button |
| `notes/` | Tips, gotchas, checklists, knowledge cards | Search / related / flash |

---

## 6. Performance & “no hang” rules

1. **Never** load full chapter content into memory on UI thread.
2. Android: use Room queries with LIMIT + paging. Prefer index + on-demand body.
3. Windows: same — API returns summary first, full body on demand.
4. Large Mermaid diagrams stay as text; render only when page is visible.
5. Scripts are stored as text; execution only in user Lab environment.
6. After every pack apply → run `audit_content.py` and record depth in manifest.

---

## 7. Expansion workflow (multi-agent safe)

1. Create chapter folder from `_templates/`.
2. Write `README.md` + empty `manifest.json`.
3. Produce title list → confirm → generate batch JSON.
4. Place under correct subfolder.
5. Run apply + audit.
6. Update `manifest.json` counts + `docs/ai_continuity/03_PROGRESS.md`.
7. Commit with clear message.

---

## 8. Quality over size policy

- App size may reach hundreds of MB. Acceptable.
- Thin content is worse than large deep content.
- Prefer 20 excellent lessons over 80 thin ones.
- Critical chapters (51, 60, 40, …) must reach deep before new chapters are added.

---

## 9. Link to continuity system

Every structural decision is recorded in:

- `docs/ai_continuity/01_PROJECT_RULES.md`
- `docs/ai_continuity/02_CONTENT_SCHEMA.md`
- `docs/ai_continuity/03_PROGRESS.md`
