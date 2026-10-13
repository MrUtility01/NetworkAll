#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Validate Chapter 09 source assets and confirm its lessons reached the Android curriculum."""
from __future__ import annotations
import gzip, json, sys, xml.etree.ElementTree as ET
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PACK = ROOT / "tools/packs/ch09"
ASSET = ROOT / "android/app/src/main/assets/curriculum_index.json.gz"

def fail(message: str) -> None:
    print(f"ERROR ch09: {message}", file=sys.stderr)
    raise SystemExit(1)

def read_json(name: str):
    path = PACK / name
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:
        fail(f"{name}: invalid/missing JSON: {exc}")

def main() -> None:
    pack = read_json("ch09_pack.json")
    examples = read_json("ch09_examples.json").get("examples")
    scenarios = read_json("ch09_scenarios.json").get("scenarios")
    questions = read_json("ch09_questions.json").get("questions")
    answers = read_json("ch09_answer_key.json").get("answer_key")
    sources = read_json("ch09_sources.json").get("sources")
    labs = read_json("ch09_labs.json").get("labs")
    case_studies = read_json("ch09_case_studies.json").get("case_studies")
    manifest = read_json("diagrams/manifest.json")
    lessons = pack.get("lessons")
    if pack.get("chapter_order") != 9 or not isinstance(lessons, list):
        fail("pack must target chapter 9 and contain lessons")
    uids = [str(x.get("uid") or "") for x in lessons]
    if not lessons or any(not x for x in uids) or len(uids) != len(set(uids)):
        fail("lesson UIDs are empty or duplicated")
    for lesson in lessons:
        required = ("title_fa", "title_en", "level", "summary", "full_content", "learning_objectives", "source_status")
        missing = [key for key in required if not lesson.get(key)]
        if missing:
            fail(f"{lesson.get('uid')}: missing fields {missing}")
        if lesson.get("chapter_order") != 9 or lesson.get("source_status") != "review_required":
            fail(f"{lesson.get('uid')}: incorrect chapter/source status")
    if len(examples) < 50 or len(scenarios) < 50 or len(questions) < 50 or len(answers) < 50 or len(sources) < 10 or len(labs) < 10 or len(case_studies) < 10:
        fail("minimum examples/scenarios/questions/answers/sources/labs/case-studies not met")
    for name, rows in (("examples", examples), ("scenarios", scenarios), ("questions", questions), ("answers", answers)):
        ids = [str(x.get("id") or "") for x in rows]
        if any(not x for x in ids) or len(ids) != len(set(ids)):
            fail(f"{name}: missing or duplicate IDs")
    qmap = {x["id"]: x for x in questions}
    amap = {x["id"]: x for x in answers}
    if set(qmap) != set(amap):
        fail("question and answer-key IDs do not match")
    for qid, q in qmap.items():
        ans = amap[qid]
        idx = ans.get("correct_option_index")
        if not isinstance(idx, int) or idx < 0 or idx >= len(q.get("options", [])):
            fail(f"{qid}: invalid correct_option_index")
        if q["options"][idx] != ans.get("correct_answer_fa") or not ans.get("explanation_fa"):
            fail(f"{qid}: answer key does not match options or has no explanation")
    for kind, rows in (("examples", examples), ("scenarios", scenarios), ("questions", questions), ("labs", labs), ("case_studies", case_studies)):
        for row in rows:
            if row.get("lesson_uid") not in set(uids):
                fail(f"{kind} {row.get('id')} refers to unknown lesson_uid")
    source_urls = [x.get("url") for x in sources]
    if any(not x for x in source_urls) or len(source_urls) != len(set(source_urls)):
        fail("source URLs missing or duplicated")
    diagrams = manifest.get("diagrams") or []
    if len(diagrams) < 6:
        fail("expected at least six chapter-specific diagrams")
    for diagram in diagrams:
        if diagram.get("lesson_uid") not in set(uids):
            fail(f"diagram {diagram.get('id')} refers to unknown lesson")
        for field in ("source_file", "svg_file"):
            path = PACK / "diagrams" / str(diagram.get(field) or "")
            if not path.is_file():
                fail(f"missing diagram asset: {path}")
        try:
            ET.parse(PACK / "diagrams" / diagram["svg_file"])
        except Exception as exc:
            fail(f"invalid SVG {diagram['svg_file']}: {exc}")
    if not ASSET.is_file():
        fail("Android curriculum asset is missing; run export and merge first")
    try:
        data = json.loads(gzip.open(ASSET, "rt", encoding="utf-8").read())
    except Exception as exc:
        fail(f"Android curriculum asset cannot be decoded: {exc}")
    chapter = next((c for c in data.get("chapters", []) if int(c.get("order", 0)) == 9), None)
    if chapter is None:
        fail("chapter 9 missing from merged Android curriculum")
    merged = [les for sub in chapter.get("subchapters", []) for les in sub.get("lessons", [])]
    merged_uids = {str(x.get("uid") or "") for x in merged}
    missing = sorted(set(uids) - merged_uids)
    if missing:
        fail(f"{len(missing)} chapter-pack lessons not merged; examples: {missing[:5]}")
    print(f"CH09 VALID: lessons={len(lessons)} examples={len(examples)} scenarios={len(scenarios)} questions={len(questions)} answers={len(answers)} labs={len(labs)} case_studies={len(case_studies)} sources={len(sources)} diagrams={len(diagrams)} merged={len(set(uids) & merged_uids)}")
    print("Structural validation only; technical review and real-network testing remain required.")

if __name__ == "__main__":
    main()
