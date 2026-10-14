#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Structural checks for the shared multi-platform incident runbook library."""
from __future__ import annotations
import json
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
PACK = ROOT / "shared" / "incident_runbooks.json"

def main():
    data = json.loads(PACK.read_text(encoding="utf-8"))
    rows = data.get("incidents")
    assert isinstance(rows, list) and len(rows) >= 150, f"expected >=150 scenarios, got {len(rows) if isinstance(rows, list) else type(rows)}"
    ids = [str(row.get("id") or "") for row in rows]
    assert all(ids) and len(ids) == len(set(ids)), "scenario IDs must be unique and non-empty"
    required = ("code", "title_fa", "title_en", "domain", "platform", "environment", "root_cause",
                "fix_summary", "verification", "rollback", "prevention", "source_status")
    for row in rows:
        missing = [key for key in required if not str(row.get(key) or "").strip()]
        assert not missing, f"{row.get('id')}: missing {missing}"
        steps = row.get("steps") or row.get("diagnostic_steps")
        assert isinstance(steps, list) and len(steps) >= 5, f"{row['id']}: fewer than five diagnostic steps"
        for index, step in enumerate(steps, 1):
            for key in ("title", "purpose", "commands", "expected", "interpretation", "if_match", "if_not_match"):
                assert str(step.get(key) or "").strip(), f"{row['id']} step {index}: missing {key}"
        assert row.get("source_status") == "review_required", f"{row['id']}: missing review status"
    print(f"Shared incident runbooks OK: {len(rows)} scenarios; each has five evidence/verify/branch steps")

if __name__ == "__main__":
    main()
