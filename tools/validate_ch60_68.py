#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""اعتبارسنجی ساختاری و یکپارچگی محتوای فصل‌های ۶۰ تا ۶۸."""
import json, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PACK_DIR = ROOT / "tools/packs/ch60_68"
PACK = PACK_DIR / "chapter_60_68_deep_pack.json"
SUPPLEMENT = PACK_DIR / "chapter_60_68_validation_pack.json"
KEY = PACK_DIR / "chapter_60_68_answer_key.json"


def read_json(path):
    return json.loads(path.read_text(encoding="utf-8"))


def main():
    d = read_json(PACK)
    k = read_json(KEY)
    supplement = read_json(SUPPLEMENT)
    base_lessons = d.get("lessons", [])
    extra_lessons = supplement.get("lessons", [])
    lessons = base_lessons + extra_lessons
    scenarios = d.get("scenarios", [])
    questions = d.get("questions", [])
    answers = k.get("answers", [])

    assert [x["chapter_order"] for x in d["chapters"]] == list(range(60, 69)), "chapter range must be 60..68"
    assert len(base_lessons) >= 250, f"expected >=250 base lessons, got {len(base_lessons)}"
    assert len(extra_lessons) == 270, f"expected 270 supplemental lessons, got {len(extra_lessons)}"
    uids = [x.get("uid") for x in lessons]
    assert all(uids) and len(uids) == len(set(uids)), "missing or duplicate lesson uid across packs"
    assert all(60 <= int(x.get("chapter_order", 0)) <= 68 for x in lessons), "lesson outside target chapters"
    for x in lessons:
        for field in ("title_fa", "summary", "full_content", "commands", "examples"):
            assert str(x.get(field, "")).strip(), f"lesson {x.get('uid')} missing {field}"
        assert len(x["full_content"]) >= 900, f"lesson content too short: {x['uid']}"
        assert (x.get("meta") or {}).get("assessment"), f"assessment missing: {x['uid']}"
    assert len(scenarios) >= 90, f"expected >=90 scenarios, got {len(scenarios)}"
    codes = [x.get("code") for x in scenarios]
    assert all(codes) and len(codes) == len(set(codes)), "scenario codes missing/duplicated"
    req = ("title_fa", "incident", "symptoms", "tasks", "solution", "verification")
    for s in scenarios:
        assert all(str(s.get(f, "")).strip() for f in req), f"scenario incomplete: {s.get('code')}"
    qids = [x.get("id") for x in questions]
    aids = [x.get("id") for x in answers]
    assert len(qids) == len(set(qids)) and len(aids) == len(set(aids)), "duplicate quiz ids"
    assert set(qids) == set(aids), "question and answer key IDs differ"
    assert len(answers) == len(questions), "question/answer counts differ"

    # Shared runtime index must expose all lessons on Windows and Android.
    sys.path.insert(0, str(ROOT / "server"))
    from core.extra_chapters import ensure_chapters_1_to_68
    from core.full_curriculum import get_full_curriculum
    curriculum = ensure_chapters_1_to_68(list(get_full_curriculum()))
    by = {int(c[0]): c for c in curriculum}
    assert all(i in by for i in range(60, 69)), "chapter missing from shared curriculum"
    for order in range(60, 69):
        titles = {title for sub in by[order][3] for title, _ in sub[1]}
        expected = [x["title_fa"] for x in lessons if int(x.get("chapter_order") or 0) == order]
        assert all(t in titles for t in expected), f"chapter {order} shared index missing lessons"

    from core.rich_content import build_rich_lesson
    sample = extra_lessons[len(extra_lessons) // 2]
    got = build_rich_lesson(sample["title_fa"], sample.get("title_en", ""), sample.get("level"))
    assert got.get("full_content") == sample["full_content"], "shared content overlay mismatch"
    assert "EJ_ASSESSMENT" in (got.get("notes") or ""), "shared quiz assessment not exposed to clients"

    # Existing Windows DB migration must insert all packs once, without destructive reseed.
    import tempfile
    from core.db import WebDB
    with tempfile.TemporaryDirectory() as tmp:
        testdb = WebDB(Path(tmp) / "validation.db")
        for order in range(60, 69):
            testdb.conn.execute(
                "INSERT INTO chapters(order_index,title_fa,title_en) VALUES(?,?,?)",
                (order, f"Test {order}", f"Test {order}"),
            )
        testdb.conn.commit()
        first = testdb.ensure_ch60_68_deep_lessons()
        second = testdb.ensure_ch60_68_deep_lessons()
        count = testdb.conn.execute("SELECT COUNT(*) c FROM lessons").fetchone()["c"]
        assert first.get("ok") and first.get("inserted") == len(lessons), f"Windows migration first pass: {first}"
        assert second.get("ok") and second.get("inserted") == 0, f"Windows migration not idempotent: {second}"
        assert count == len(lessons), f"Windows DB lesson count mismatch: {count}"
        testdb.conn.close()
    print(
        f"VALID chapters=9 base_lessons={len(base_lessons)} supplemental_lessons={len(extra_lessons)} "
        f"total_lessons={len(lessons)} scenarios={len(scenarios)} questions={len(questions)} "
        f"answer_keys={len(answers)}; Windows DB migration idempotent"
    )


if __name__ == "__main__":
    main()
