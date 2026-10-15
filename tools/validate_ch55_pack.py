#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Validate chapter 55 shared content pack and Windows SQLite import."""
from __future__ import annotations
import json, sys, tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PACK = ROOT / "tools" / "packs" / "ch55" / "chapter_55_cctv_access_bms_iot_pack.json"

def main():
    data = json.loads(PACK.read_text(encoding="utf-8"))
    assert data.get("package_schema_version") == "1.0"
    rows = data.get("lessons") or []
    assert len(rows) >= 100, f"expected >=100 lessons, got {len(rows)}"
    seen = set()
    counts = {}
    topics = set()
    for row in rows:
        uid = row.get("uid")
        assert uid and uid not in seen, f"missing/duplicate uid: {uid}"
        seen.add(uid)
        assert int(row.get("chapter_order") or 0) == 55
        assert row.get("level") in {"L0", "L1", "L2", "L3", "L4"}
        assert row.get("title_fa") and row.get("title_en")
        assert len(row.get("full_content") or "") >= 800, f"shallow content: {uid}"
        assessment = (row.get("meta") or {}).get("assessment") or {}
        questions = assessment.get("questions") or []
        answers = assessment.get("answer_key") or []
        assert questions and answers and len(questions) == len(answers), f"assessment mismatch: {uid}"
        qids = {q.get("id") for q in questions}
        assert len(qids) == len(questions), f"duplicate question id: {uid}"
        assert all(a.get("question_id") in qids for a in answers), f"answer key mismatch: {uid}"
        counts[row["level"]] = counts.get(row["level"], 0) + 1
        topics.add(row.get("topic"))
    assert counts == {"L0": len(rows)//5, "L1": len(rows)//5, "L2": len(rows)//5, "L3": len(rows)//5, "L4": len(rows)//5}, counts
    assert len(topics) >= 20, f"expected >=20 topics, got {len(topics)}"

    sys.path.insert(0, str(ROOT / "server"))
    from core.db import WebDB
    with tempfile.TemporaryDirectory() as td:
        db = WebDB(Path(td) / "chapter55-smoke.db")
        seeded = db.seed_full(force=True)
        assert seeded.get("ok"), seeded
        imported = db.ensure_ch55_deep_lessons()
        assert imported.get("ok"), imported
        deep = db.conn.execute(
            """SELECT COUNT(*) n FROM lessons l
               JOIN levels lv ON lv.id=l.level_id
               JOIN chapters c ON c.id=lv.chapter_id
               WHERE c.order_index=55 AND length(COALESCE(l.full_content,''))>=800"""
        ).fetchone()["n"]
        assert deep >= len(rows), f"Windows DB imported {deep}/{len(rows)} deep lessons"
        db.conn.close()
    print(f"PASS chapter 55: topics={len(topics)} lessons={len(rows)} levels={counts}; Windows DB deep lessons={deep}")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
