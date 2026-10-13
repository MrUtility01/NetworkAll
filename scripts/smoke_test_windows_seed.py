#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Smoke-test the Windows SQLite seed against the same index shipped to Android."""
from __future__ import annotations

import gzip
import json
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "server"))
ASSET = ROOT / "android/app/src/main/assets/curriculum_index.json.gz"


def main() -> None:
    payload = json.loads(gzip.decompress(ASSET.read_bytes()))
    expected = int(payload["lesson_count"])
    with tempfile.TemporaryDirectory(prefix="networkall-v1-seed-") as td:
        from core.db import WebDB

        db = WebDB(Path(td) / "seed-test.db")
        try:
            result = db.seed_full(force=True)
            stats = db.stats()
            chapters = db.list_chapters()
            if result.get("curriculum_source") != "shared-android-curriculum":
                raise SystemExit(f"Windows used fallback seed, not shared index: {result}")
            if len(chapters) != 68 or stats["chapters"] != 68:
                raise SystemExit(f"Windows chapter count mismatch: {stats}")
            if stats["lessons"] != expected:
                raise SystemExit(f"Windows lesson count {stats['lessons']} != index {expected}")
            if stats["with_content"] < int(expected * 0.90):
                raise SystemExit(f"too few lessons have content: {stats['with_content']}/{expected}")

            ch68 = next((ch for ch in chapters if int(ch["order_index"]) == 68), None)
            if not ch68:
                raise SystemExit("Windows DB missing chapter 68")
            levels = db.list_levels(ch68["id"])
            names = {
                str(level["title_fa"]).split("—", 1)[0].strip()
                for level in levels
            }
            required = {"Linux", "Bash", "PowerShell", "Windows CMD", "Windows Batch"}
            if required - names:
                raise SystemExit(f"Windows Chapter 68 collections missing: {sorted(required - names)}")

            bad_uid = db.conn.execute(
                """SELECT COUNT(*) AS n FROM lessons
                   WHERE uid IS NULL OR uid='' OR content_hash IS NULL OR content_hash=''"""
            ).fetchone()["n"]
            duplicate_uid = db.conn.execute(
                """SELECT COUNT(*) FROM (
                       SELECT uid FROM lessons GROUP BY uid HAVING COUNT(*) > 1
                   )"""
            ).fetchone()[0]
            if bad_uid or duplicate_uid:
                raise SystemExit(f"invalid Windows UIDs/hashes: missing={bad_uid}, duplicate groups={duplicate_uid}")

            print(json.dumps({
                "ok": True,
                "curriculum_source": result["curriculum_source"],
                "chapters": stats["chapters"],
                "levels": stats["levels"],
                "lessons": stats["lessons"],
                "expected_lessons": expected,
                "lessons_with_content": stats["with_content"],
                "scenarios": stats["scenarios"],
                "chapter68_collections": sorted(names),
            }, ensure_ascii=False))
        finally:
            db.conn.close()


if __name__ == "__main__":
    main()
