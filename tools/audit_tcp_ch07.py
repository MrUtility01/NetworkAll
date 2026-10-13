#!/usr/bin/env python3
"""Audit the TCP Chapter 7 teaching pack against NetworkAll's depth contract.

Usage:
  python tools/audit_tcp_ch07.py
  python tools/audit_tcp_ch07.py --strict

Default mode reports gaps without failing so authors can iteratively improve content.
Strict mode exits non-zero when any depth, assessment, UID, or schema-contract issue exists.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
PACK = ROOT / "tools/packs/network_transport/tcp_transport_engineering_ch07_pack.json"
FLOORS = {"L0": 600, "L1": 800, "L2": 1200, "L3": 1600, "L4": 2200}
QUESTION_FLOORS = {"L0": 5, "L1": 8, "L2": 10, "L3": 12, "L4": 15}


def words(value: str) -> int:
    # Count Persian/Arabic and Latin technical terms, numbers, and common hyphenated tokens.
    return len(re.findall(r"[\w\u0600-\u06FF]+(?:[-’'][\w\u0600-\u06FF]+)*", value, re.UNICODE))


def fail(message: str, errors: list[str]) -> None:
    errors.append(message)
    print(f"FAIL  {message}")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--strict", action="store_true", help="exit non-zero if any audit gap exists")
    args = parser.parse_args()

    errors: list[str] = []
    if not PACK.is_file():
        print(f"FAIL  pack not found: {PACK}")
        return 2
    try:
        pack: dict[str, Any] = json.loads(PACK.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        print(f"FAIL  invalid JSON: {exc}")
        return 2

    lessons = pack.get("lessons")
    if not isinstance(lessons, list) or not lessons:
        fail("lessons must be a non-empty array", errors)
        lessons = []

    seen_uids: set[str] = set()
    seen_question_ids: set[str] = set()
    questions_by_level = {level: 0 for level in FLOORS}
    levels_seen: set[str] = set()
    print("NetworkAll TCP Chapter 7 content audit")
    print(f"Pack: {PACK.relative_to(ROOT)}")
    print(f"Lesson count: {len(lessons)}")

    for index, lesson in enumerate(lessons, 1):
        if not isinstance(lesson, dict):
            fail(f"lesson #{index} must be an object", errors)
            continue
        uid = lesson.get("uid")
        level = lesson.get("level")
        title = lesson.get("title_fa", f"lesson #{index}")
        if not isinstance(uid, str) or not uid.strip():
            fail(f"{title}: missing stable uid", errors)
        elif uid in seen_uids:
            fail(f"duplicate lesson uid: {uid}", errors)
        else:
            seen_uids.add(uid)

        if level not in FLOORS:
            fail(f"{title}: invalid level {level!r}", errors)
            continue
        levels_seen.add(level)
        body = lesson.get("full_content", "")
        count = words(body) if isinstance(body, str) else 0
        floor = FLOORS[level]
        status = "PASS" if count >= floor else "GAP"
        print(f"{status:4}  {level}  {count:5} words / {floor:4} required  {title}")
        if count < floor:
            fail(f"{uid}: {level} content is {floor - count} words below the floor", errors)

        try:
            metadata = json.loads(lesson.get("meta_json", "{}"))
        except (TypeError, json.JSONDecodeError) as exc:
            fail(f"{uid}: invalid meta_json: {exc}", errors)
            continue
        assessment = metadata.get("assessment", {})
        questions = assessment.get("questions", []) if isinstance(assessment, dict) else []
        if not isinstance(questions, list):
            fail(f"{uid}: assessment.questions must be an array", errors)
            continue
        questions_by_level[level] += len(questions)
        for question in questions:
            if not isinstance(question, dict):
                fail(f"{uid}: question must be an object", errors)
                continue
            qid = question.get("id")
            if not isinstance(qid, str) or not qid.strip():
                fail(f"{uid}: question without id", errors)
                continue
            if question.get("level") != level:
                fail(f"{uid}: question {qid} level does not match lesson level {level}", errors)
            if not str(question.get("prompt", "")).strip():
                fail(f"{uid}: question {qid} has an empty prompt", errors)
            if qid in seen_question_ids:
                fail(f"duplicate question id: {qid}", errors)
            seen_question_ids.add(qid)

    missing_levels = set(FLOORS) - levels_seen
    for level in sorted(missing_levels):
        fail(f"missing instructional level {level}", errors)

    answer_key = pack.get("answer_key", {})
    if not isinstance(answer_key, dict):
        fail("answer_key must be an object", errors)
        answer_key = {}
    missing_answers = seen_question_ids - set(answer_key)
    orphan_answers = set(answer_key) - seen_question_ids
    for qid in sorted(missing_answers):
        fail(f"question has no answer_key entry: {qid}", errors)
    for qid in sorted(orphan_answers):
        fail(f"orphan answer_key entry: {qid}", errors)
    for qid in sorted(seen_question_ids & set(answer_key)):
        answer = answer_key[qid]
        if not isinstance(answer, dict) or not str(answer.get("answer", "")).strip():
            fail(f"answer is empty or malformed: {qid}", errors)
        elif not str(answer.get("rationale", "")).strip():
            fail(f"answer lacks explanatory rationale: {qid}", errors)

    for level, minimum in QUESTION_FLOORS.items():
        actual = questions_by_level[level]
        print(f"{'PASS' if actual >= minimum else 'GAP ':4}  {level}  {actual:3} questions / {minimum:2} required")
        if actual < minimum:
            fail(f"{level}: {actual} questions, {minimum - actual} below minimum", errors)

    contract = pack.get("instructional_contract", {})
    if contract.get("level_floors") != FLOORS:
        fail("instructional_contract.level_floors differs from the repository standard", errors)
    if contract.get("separate_answer_key") is not True:
        fail("separate_answer_key must be true", errors)
    if contract.get("lab_status") != "executed":
        print("NOTE  practical labs are not marked executed; content cannot be considered fully verified")
    if not isinstance(pack.get("sources"), list) or not pack.get("sources"):
        fail("sources must be a non-empty array", errors)
    for lesson in lessons:
        if not isinstance(lesson, dict):
            continue
        for field in ("summary", "learning_objectives", "prerequisites", "full_content", "meta_json"):
            value = lesson.get(field)
            if not value:
                fail(f"{lesson.get('uid', 'unknown lesson')}: required field {field} is empty", errors)
        if not isinstance(lesson.get("learning_objectives"), list) or not lesson.get("learning_objectives"):
            fail(f"{lesson.get('uid', 'unknown lesson')}: learning_objectives must be a non-empty array", errors)
    if pack.get("content_quality", {}).get("status") == "verified" and errors:
        fail("content cannot be marked verified while audit gaps remain", errors)

    print(f"\nQuestions: {len(seen_question_ids)}; answer entries: {len(answer_key)}")
    print(f"Audit findings: {len(errors)}")
    if errors:
        print("Overall: REVIEW REQUIRED")
        return 1 if args.strict else 0
    print("Overall: STRUCTURAL AND DEPTH AUDIT PASSED")
    return 0


if __name__ == "__main__":
    sys.exit(main())
