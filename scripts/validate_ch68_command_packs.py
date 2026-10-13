#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Validate additive Chapter 68 command packs and report Cisco 1600-record goal."""
from __future__ import annotations
import json
import sys
from pathlib import Path
from collections import Counter

ROOT = Path(__file__).resolve().parents[1]
PACKS = ROOT / "tools/packs/commands_encyclopedia"
REQUIRED = {
    "cisco_routing.json": ("cisco", 30),
    "mikrotik_ops_addon.json": ("mikrotik", 20),
    "powershell.json": ("powershell", 20),
    "windows_batch.json": ("windows_batch", 20),
    "linux.json": ("linux", 20),
}
FIELDS = (
    "uid", "vendor", "platform", "version_scope", "privilege", "command",
    "title_fa", "syntax", "when_to_use_fa", "prerequisites_fa", "steps_fa",
    "sample_output", "common_mistakes_fa", "security_notes_fa", "lab_hint_fa",
    "verify_steps_fa", "rollback_fa", "source_urls", "assessment",
)

def fail(message: str) -> None:
    print(f"ERROR: {message}", file=sys.stderr)
    raise SystemExit(1)

def main() -> None:
    global_uids: dict[str, str] = {}
    totals = Counter()
    for filename, (platform, minimum) in REQUIRED.items():
        path = PACKS / filename
        if not path.is_file():
            fail(f"missing required command pack: {path}")
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except Exception as exc:
            fail(f"{filename}: invalid JSON: {exc}")
        if int(data.get("chapter_order", 0)) != 68:
            fail(f"{filename}: chapter_order must be 68")
        commands = data.get("commands")
        if not isinstance(commands, list) or len(commands) < minimum:
            fail(f"{filename}: expected at least {minimum} command records")
        local_uids = set()
        local_commands = set()
        for i, record in enumerate(commands, 1):
            if not isinstance(record, dict):
                fail(f"{filename}[{i}]: record must be an object")
            missing = [field for field in FIELDS if field not in record or record[field] in (None, "", [], {})]
            if missing:
                fail(f"{filename}[{i}]: missing required fields: {missing}")
            uid = str(record["uid"]).strip()
            command = str(record["command"]).strip()
            if uid in local_uids:
                fail(f"{filename}: duplicate UID {uid}")
            if uid in global_uids:
                fail(f"{filename}: UID collision with {global_uids[uid]}: {uid}")
            if command in local_commands:
                fail(f"{filename}: duplicate command string: {command}")
            local_uids.add(uid)
            local_commands.add(command)
            global_uids[uid] = filename
            if record.get("source_status") != "review_required":
                fail(f"{filename}[{i}]: new content must be marked review_required")
            assessment = record.get("assessment")
            if not isinstance(assessment, dict) or not assessment.get("question_fa") or not assessment.get("answer_key_fa"):
                fail(f"{filename}[{i}]: assessment must contain question_fa and answer_key_fa")
        totals[platform] += len(commands)
        print(f"OK {filename}: {len(commands)} records, {len(local_uids)} unique UIDs")
    print("CH68 ADDITIVE PACKS VALID")
    print("Counts:", dict(totals))
    print(f"Cisco Routing progress: {totals['cisco']}/1600 curated records in this dedicated pack.")
    print("Note: structural validation does not replace vendor/version review or real-device labs.")

if __name__ == "__main__":
    main()
