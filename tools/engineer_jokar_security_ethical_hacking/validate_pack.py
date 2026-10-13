# -*- coding: utf-8 -*-
"""Validate the canonical defensive-security pack without changing any content."""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_PACK = ROOT / "packs" / "security_ethical_hacking" / "security_ethical_hacking_pack.json"
path = Path(sys.argv[1]) if len(sys.argv) > 1 else DEFAULT_PACK
if not path.is_absolute():
    path = Path.cwd() / path
if not path.is_file():
    raise SystemExit("Pack not found: " + str(path))

data = json.loads(path.read_text(encoding="utf-8"))
lessons = data.get("lessons")
assert isinstance(lessons, list) and len(lessons) == 110, (
    "expected 110 lessons, got " + str(len(lessons) if isinstance(lessons, list) else "non-list")
)
uids = [item.get("uid") for item in lessons]
assert all(uids), "missing UID"
assert len(set(uids)) == len(uids), "duplicate UID"

for lesson in lessons:
    for key in ("uid", "chapter_order", "subchapter_order", "lesson_order", "title_fa", "title_en", "summary", "full_content", "meta"):
        assert key in lesson, (lesson.get("uid"), "missing " + key)
    assessment = (lesson.get("meta") or {}).get("assessment") or {}
    questions = assessment.get("questions")
    answer_key = assessment.get("answer_key")
    assert isinstance(questions, list) and questions, (lesson["uid"], "missing questions")
    qids = {str(q.get("id")) for q in questions if isinstance(q, dict) and q.get("id") is not None}
    if isinstance(answer_key, dict):
        aids = {str(key) for key in answer_key}
    elif isinstance(answer_key, list):
        aids = {
            str(a.get("question_id", a.get("id")))
            for a in answer_key if isinstance(a, dict) and a.get("question_id", a.get("id")) is not None
        }
    else:
        aids = set()
    assert qids and qids == aids, (lesson["uid"], "question/answer IDs differ", sorted(qids), sorted(aids))
    assert all(not any(k in q for k in ("answer", "correct_index", "correct_option_id")) for q in questions), (
        lesson["uid"], "answer leaked into question"
    )

print("OK: " + str(len(lessons)) + " security lessons; unique UIDs; separate answer keys.")
