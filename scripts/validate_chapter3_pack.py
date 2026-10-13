#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Validate the additive BIOS/UEFI chapter pack and its merged Android lessons."""
from __future__ import annotations

import gzip
import json
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PACK = ROOT / "tools/packs/ch03"
ASSET = ROOT / "android/app/src/main/assets/curriculum_index.json.gz"


def fail(message: str) -> None:
    print("ERROR:", message, file=sys.stderr)
    raise SystemExit(1)


def load(path: Path) -> dict:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:
        fail(f"invalid JSON {path.relative_to(ROOT)}: {exc}")


def main() -> None:
    pack = load(PACK / "ch03_pack.json")
    examples = load(PACK / "ch03_examples.json").get("examples", [])
    scenarios = load(PACK / "ch03_scenarios.json").get("scenarios", [])
    questions = load(PACK / "ch03_questions.json").get("questions", [])
    answers = load(PACK / "ch03_answer_key.json").get("answer_key", [])
    sources = load(PACK / "ch03_sources.json").get("sources", [])
    manifest = load(PACK / "diagrams/manifest.json")
    lessons = pack.get("lessons", [])

    if pack.get("package_schema_version") != 1 or pack.get("chapter_order") != 3:
        fail("wrong chapter 3 package schema/order")
    if len(lessons) != 50:
        fail(f"expected 50 lessons, got {len(lessons)}")
    uids = {row.get("uid") for row in lessons}
    if len(uids) != 50 or None in uids:
        fail("lesson UIDs are missing or duplicated")
    if any(row.get("source_status") != "review_required" for row in lessons):
        fail("all new lessons must remain review_required")
    if min(len(str(row.get("full_content") or "")) for row in lessons) < 1800:
        fail("at least one lesson is below the minimum content length")
    if (len(examples), len(scenarios), len(questions), len(answers)) != (50, 50, 50, 50):
        fail("expected 50 examples, 50 scenarios, 50 questions and 50 answers")

    for name, rows in (("examples", examples), ("scenarios", scenarios), ("questions", questions)):
        ids = [row.get("id") for row in rows]
        if any(not value for value in ids) or len(ids) != len(set(ids)):
            fail(f"{name} IDs are missing or duplicated")
        if any(row.get("lesson_uid") not in uids for row in rows):
            fail(f"{name} contains an unknown lesson_uid")
    qids = {row.get("id") for row in questions}
    aids = {row.get("question_id") for row in answers}
    if qids != aids or len(aids) != 50:
        fail("question IDs do not match answer_key IDs")
    if any(any(key in row for key in ("answer", "correct", "correct_index", "correct_option_id")) for row in questions):
        fail("answer leaked into question records")
    if len(sources) < 10 or any(not str(row.get("url") or "").startswith("https://") for row in sources):
        fail("at least ten HTTPS source references are required")

    diagrams = manifest.get("diagrams", [])
    if manifest.get("diagram_count") != 10 or len(diagrams) != 10:
        fail("expected ten diagram manifest entries")
    for diagram in diagrams:
        stem = str(diagram.get("id") or "")
        svg = PACK / "diagrams" / f"{stem}.svg"
        mermaid = PACK / "diagrams" / f"{stem}.mmd"
        if not svg.is_file() or not mermaid.is_file():
            fail(f"diagram source/SVG missing for {stem}")
        try:
            if not ET.parse(svg).getroot().tag.endswith("svg"):
                fail(f"invalid SVG root for {stem}")
        except Exception as exc:
            fail(f"invalid SVG {stem}: {exc}")
        if not mermaid.read_text(encoding="utf-8").lstrip().startswith("%%"):
            fail(f"Mermaid source missing title for {stem}")

    if not ASSET.is_file():
        fail("merged Android curriculum asset missing")
    with gzip.open(ASSET, "rt", encoding="utf-8") as stream:
        curriculum = json.load(stream)
    chapter = next((row for row in curriculum.get("chapters", []) if int(row.get("order", -1)) == 3), None)
    if chapter is None:
        fail("merged curriculum has no chapter 3")
    merged = {
        lesson.get("uid")
        for sub in chapter.get("subchapters", [])
        for lesson in sub.get("lessons", [])
    }
    missing = sorted(uid for uid in uids if uid not in merged)
    if missing:
        fail(f"chapter 3 lessons were not merged into Android curriculum: {missing[:5]}")

    print(json.dumps({
        "ok": True, "chapter": 3, "lessons": len(lessons), "examples": len(examples),
        "scenarios": len(scenarios), "questions": len(questions), "answer_keys": len(answers),
        "sources": len(sources), "diagrams": len(diagrams), "merged_lessons": len(uids),
        "source_status": "review_required"
    }, ensure_ascii=False))


if __name__ == "__main__":
    main()
