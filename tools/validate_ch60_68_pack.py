#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Validate shared chapter 60-68 content packs and Windows/Android curriculum overlay."""
from __future__ import annotations
import json, sys, tempfile
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
PACKS = [
    ROOT / "tools/packs/ch60_68/ch60_68_ch60_pack.json",
    ROOT / "tools/packs/ch60_68/ch60_68_ch61_63_pack.json",
    ROOT / "tools/packs/ch60_68/ch60_68_ch64_68_pack.json",
]
def main():
    all_lessons=[]
    chapter_counts={i:0 for i in range(60,69)}
    seen_uids=set()
    for path in PACKS:
        data=json.loads(path.read_text(encoding="utf-8"))
        assert data.get("package_schema_version") == "1.0", f"bad schema: {path.name}"
        assert data.get("lessons"), f"no lessons: {path.name}"
        for item in data["lessons"]:
            uid=item.get("uid")
            assert uid and uid not in seen_uids, f"missing/duplicate uid: {uid}"
            seen_uids.add(uid)
            ch=int(item.get("chapter_order") or 0)
            assert ch in chapter_counts, f"out-of-range chapter: {ch}"
            assert item.get("level") in {"L0","L1","L2","L3","L4"}
            assert item.get("title_fa") and item.get("title_en")
            assert len(item.get("full_content") or "") >= 800, f"shallow content: {uid}"
            assessment=(item.get("meta") or {}).get("assessment") or {}
            questions=assessment.get("questions") or []
            answers=assessment.get("answer_key") or []
            assert questions and answers and len(questions)==len(answers), f"assessment/key mismatch: {uid}"
            question_ids={q.get("id") for q in questions}
            assert len(question_ids)==len(questions), f"duplicate question id: {uid}"
            assert all(a.get("question_id") in question_ids for a in answers), f"answer key references unknown question: {uid}"
            chapter_counts[ch]+=1
            all_lessons.append(item)
    assert all(chapter_counts.values()), f"chapter missing pack lessons: {chapter_counts}"
    assert all(n % 5 == 0 for n in chapter_counts.values()), f"expected five-level topic groups: {chapter_counts}"
    sys.path.insert(0, str(ROOT / "server"))
    from core.full_curriculum import get_full_curriculum
    from core.extra_chapters import ensure_chapters_1_to_68
    curriculum=ensure_chapters_1_to_68(get_full_curriculum())
    chapter_numbers={int(ch[0]) for ch in curriculum}
    assert set(range(60,69)).issubset(chapter_numbers), "shared curriculum missing chapter 60-68"
    titles_by_ch={int(ch[0]):{title for _, lessons in ch[3] for title, _ in lessons} for ch in curriculum}
    missing=[(x["chapter_order"],x["title_fa"]) for x in all_lessons if x["title_fa"] not in titles_by_ch.get(int(x["chapter_order"]),set())]
    assert not missing, f"shared curriculum overlay missing {len(missing)} titles; sample={missing[:5]}"
    # Windows/Flask SQLite smoke test: seed a disposable DB, then apply the same packs.
    from core.db import WebDB
    with tempfile.TemporaryDirectory() as temp_dir:
        test_db = WebDB(Path(temp_dir) / "smoke.db")
        seeded = test_db.seed_full(force=True)
        applied = test_db.ensure_ch60_68_deep_lessons()
        assert seeded.get("ok"), f"Windows seed failed: {seeded}"
        assert applied.get("ok"), f"Windows pack import failed: {applied}"
        processed = int(applied.get("inserted", 0)) + int(applied.get("updated", 0)) + int(applied.get("skipped", 0))
        assert processed >= 800, f"Windows pack import processed too few records: {applied}"
        deep_count = test_db.conn.execute(
            """SELECT COUNT(*) n FROM lessons l
               JOIN levels lv ON lv.id=l.level_id
               JOIN chapters c ON c.id=lv.chapter_id
               WHERE c.order_index BETWEEN 60 AND 68
                 AND length(COALESCE(l.full_content,'')) >= 800"""
        ).fetchone()["n"]
        assert deep_count >= 800, f"Windows DB has too few deep lessons: {deep_count}"
        test_db.conn.close()
    print("PASS: JSON schema, UID uniqueness, deep content, 5-level groups, separated answer_key and shared curriculum overlay.")
    print("chapter lesson counts:", chapter_counts)
    print("total lessons:", len(all_lessons))
    return 0
if __name__ == "__main__":
    raise SystemExit(main())
