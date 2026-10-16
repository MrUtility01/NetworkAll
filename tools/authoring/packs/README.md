# tools/packs — Content Source of Truth

All final educational JSON lives here.

## Professional layout (mandatory for new content)

```
tools/packs/
├── _templates/                 # copy these
├── ch40_vmware_hyperv/
│   ├── README.md
│   ├── manifest.json
│   ├── lessons/
│   ├── scenarios/
│   ├── packet_journeys/
│   ├── diagrams/
│   ├── scripts/
│   └── notes/
├── ch41_proxmox_docker/
├── ch51_automation_ai/
├── ch60_troubleshooting_labs/
└── ...
```

See full rules: `docs/CONTENT_ARCHITECTURE.md`

## Rules

- One chapter = one folder.
- Split into batches (max ~15–20 items per JSON).
- Always keep `manifest.json` and chapter `README.md` up to date.
- Never put new content outside this tree.
- After adding packs run:
  ```bash
  python tools/apply_any_pack.py --db server/data/encyclopedia.db --pack PATH --apply
  python tools/audit_content.py --db server/data/encyclopedia.db
  ```
