#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Validate shared deep content for chapters 56-59 and Windows/Android consumption."""
import json, sys, tempfile
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
PACK_DIR = ROOT / "tools" / "packs" / "ch56_59"

def main():
    all_items = []
    for order in range(56, 60):
        path = PACK_DIR / f"ch{order}_deep_pack.json"
        data = json.loads(path.read_text(encoding="utf-8"))
        assert data.get("package_schema_version") == "1.0", f"schema: {path.name}"
        rows = data.get("lessons") or []
        assert len(rows) == 100, f"chapter {order}: expected 100 lessons, got {len(rows)}"
        uids = [x.get("uid") for x in rows]
        assert all(uids) and len(set(uids)) == len(uids), f"chapter {order}: duplicate/missing UID"
        counts = {lv: sum(x.get("level") == lv for x in rows) for lv in ("L0","L1","L2","L3","L4")}
        assert counts == {"L0":20,"L1":20,"L2":20,"L3":20,"L4":20}, f"chapter {order}: level counts {counts}"
        for item in rows:
            assert int(item.get("chapter_order") or 0) == order
            assert item.get("title_fa") and item.get("title_en") and item.get("topic")
            assert len(item.get("full_content") or "") >= 800, f"shallow content: {item.get('uid')}"
            assess = (item.get("meta") or {}).get("assessment") or {}
            questions, answers = assess.get("questions") or [], assess.get("answer_key") or []
            assert len(questions) == 3 and len(answers) == 3, f"assessment incomplete: {item.get('uid')}"
            qids = [q.get("id") for q in questions]
            assert len(set(qids)) == len(qids) and all(qids), f"question IDs: {item.get('uid')}"
            assert {a.get("question_id") for a in answers} == set(qids), f"answer_key mismatch: {item.get('uid')}"
            assert all("correct" not in q for q in questions), f"answer leaked into question: {item.get('uid')}"
        all_items.extend(rows)

    sys.path.insert(0, str(ROOT / "server"))
    from core.full_curriculum import get_full_curriculum
    from core.extra_chapters import ensure_chapters_1_to_68
    curriculum = ensure_chapters_1_to_68(list(get_full_curriculum()))
    by_order = {int(c[0]): c for c in curriculum}
    assert set(range(56,60)).issubset(by_order), "curriculum missing chapter 56-59"
    for order in range(56,60):
        titles = {title for _, lessons in by_order[order][3] for title, _ in lessons}
        missing = [x["title_fa"] for x in all_items if int(x["chapter_order"]) == order and x["title_fa"] not in titles]
        assert not missing, f"chapter {order}: overlay missing {len(missing)} titles"

    from core.rich_content import build_rich_lesson
    for item in all_items[::37]:
        rich = build_rich_lesson(item["title_fa"], item["title_en"], item["level"])
        assert len(rich.get("full_content") or "") >= 800, f"rich overlay not applied: {item['uid']}"

    from core.db import WebDB
    with tempfile.TemporaryDirectory() as td:
        db = WebDB(Path(td) / "ch56-59-smoke.db")
        seeded = db.seed_full(force=True)
        assert seeded.get("ok"), seeded
        for order in range(56,60):
            count = db.conn.execute(
                """SELECT COUNT(*) n FROM lessons l JOIN levels lv ON lv.id=l.level_id
                   JOIN chapters c ON c.id=lv.chapter_id
                   WHERE c.order_index=? AND length(COALESCE(l.full_content,''))>=800""", (order,)
            ).fetchone()["n"]
            assert count >= 100, f"Windows DB chapter {order}: only {count} deep lessons"
        first = db.ensure_ch56_59_deep_lessons()
        second = db.ensure_ch56_59_deep_lessons()
        assert first.get("ok") and second.get("ok"), (first, second)
        assert second.get("inserted") == 0, f"migration is not idempotent: {second}"
        db.conn.close()
    print("PASS chapters 56-59: 400 lessons; 20 topics × L0-L4 per chapter; assessment keys separated; Android/Windows overlay and idempotent DB import verified.")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
