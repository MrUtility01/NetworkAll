#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Create a baseline data file inside each of the 68 canonical chapter folders."""
from __future__ import annotations
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "server"))
from core.full_curriculum import get_full_curriculum
from core.extra_chapters import ensure_chapters_1_to_68

def render_lesson(value):
    if isinstance(value, (tuple, list)):
        row = list(value)
        out = {
            "title_fa": str(row[0]) if row else "",
            "title_en": str(row[1]) if len(row) > 1 else (str(row[0]) if row else "")
        }
        if len(row) > 2:
            out["extra_fields"] = row[2:]
        return out
    if isinstance(value, dict):
        return {
            "title_fa": str(value.get("title_fa") or value.get("title_en") or "درس"),
            "title_en": str(value.get("title_en") or value.get("title_fa") or ""),
            "source_record": value
        }
    return {"title_fa": str(value), "title_en": str(value)}

def main():
    chapters = ensure_chapters_1_to_68(list(get_full_curriculum()))
    numbers = set()
    total = 0
    for record in chapters:
        order = int(record[0])
        candidates = list((ROOT / "tools" / "chapters").glob(f"ch{order:02d}_*"))
        if len(candidates) != 1:
            raise RuntimeError(f"Expected exactly one folder for chapter {order}; found {len(candidates)}")
        levels = []
        for raw_level in record[3] or []:
            lesson_rows = [render_lesson(x) for x in (raw_level[1] or [])]
            levels.append({"title_fa": str(raw_level[0]), "lessons": lesson_rows})
            total += len(lesson_rows)
        payload = {
            "schema_version": 1,
            "kind": "baseline_curriculum",
            "chapter_order": order,
            "chapter_title_fa": str(record[1]),
            "chapter_title_en": str(record[2]),
            "source": "Exported from the currently running curriculum implementation; original code is retained during migration.",
            "levels": levels,
            "counts": {"levels": len(levels), "lessons": sum(len(x["lessons"]) for x in levels)}
        }
        out_path = candidates[0] / "base_curriculum.json"
        out_path.write_text(json.dumps(payload, ensure_ascii=False, separators=(",", ":")) + "\n", encoding="utf-8")
        numbers.add(order)
    if numbers != set(range(1, 69)):
        raise RuntimeError(f"Baseline export expected chapters 1..68, found {sorted(numbers)}")
    print(f"BASELINE EXPORT OK: chapters={len(numbers)} lessons={total}")

if __name__ == "__main__":
    main()
