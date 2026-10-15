#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Build compatibility packs from the type-separated numeric chapter source files."""
from __future__ import annotations
import argparse, json, os
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CHAPTERS = ROOT / "tools" / "chapters"
CATEGORIES = {
    "questions": "questions.json",
    "answers": "answer_key.json",
    "examples": "examples.json",
    "commands": "commands.json",
    "labs": "labs.json",
}

def read_json(path: Path):
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:
        raise ValueError(f"Invalid JSON at {path.relative_to(ROOT)}: {exc}") from exc

def write_atomic(path: Path, value) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(value, ensure_ascii=False, separators=(",", ":")) + "\n", encoding="utf-8")
    os.replace(tmp, path)

def legacy_pack(order: int):
    numeric = CHAPTERS / str(order) / "chapter.json"
    if numeric.is_file():
        return numeric
    for directory in sorted(CHAPTERS.glob(f"ch{order:02d}_*")):
        candidate = directory / "chapter.json"
        if candidate.is_file():
            return candidate
    return None

def assemble_chapter(order: int, strict: bool = False):
    chapter = CHAPTERS / str(order)
    lesson_path = chapter / "lessons" / "lessons.json"
    if not lesson_path.is_file():
        legacy = legacy_pack(order)
        if strict:
            raise FileNotFoundError(f"Chapter {order} has no numeric lessons/lessons.json")
        return legacy, 0
    doc = read_json(lesson_path)
    records = doc.get("items")
    if not isinstance(records, list):
        raise ValueError(f"{lesson_path.relative_to(ROOT)} must have an items array")

    rows, order_uids = {}, []
    for index, item in enumerate(records, 1):
        if not isinstance(item, dict):
            raise ValueError(f"Invalid lesson item {index} in {lesson_path.relative_to(ROOT)}")
        item = dict(item)
        uid = str(item.get("uid") or f"lesson:ch{order:02d}:numeric:{index:05d}")
        if uid in rows:
            raise ValueError(f"Duplicate UID {uid!r} in chapter {order}")
        item["uid"] = uid
        rows[uid] = item
        order_uids.append(uid)

    for category, filename in CATEGORIES.items():
        path = chapter / category / filename
        if not path.is_file():
            if strict:
                raise FileNotFoundError(f"Missing category file: {path.relative_to(ROOT)}")
            continue
        category_doc = read_json(path)
        items = category_doc.get("items")
        if not isinstance(items, list):
            raise ValueError(f"{path.relative_to(ROOT)} must have an items array")
        for index, item in enumerate(items, 1):
            if not isinstance(item, dict) or not item.get("uid"):
                raise ValueError(f"Invalid category item {index} in {path.relative_to(ROOT)}")
            uid = str(item["uid"])
            if uid not in rows:
                rows[uid] = {
                    "uid": uid,
                    "chapter_order": order,
                    "title_fa": str(item.get("title_fa") or f"محتوای پیوندنشده {index}"),
                    "title_en": str(item.get("title_en") or ""),
                    "meta": {"orphaned_category_source": path.relative_to(ROOT).as_posix()},
                }
                order_uids.append(uid)
            fields = item.get("fields")
            if isinstance(fields, dict):
                # The type-specific file is authoritative for its field.
                rows[uid].update(fields)

    metadata = doc.get("pack_metadata")
    if not isinstance(metadata, dict):
        metadata = {}
    pack = dict(metadata)
    pack.setdefault("schema_version", 1)
    pack["chapter_order"] = int(pack.get("chapter_order") or order)
    if pack["chapter_order"] != order:
        raise ValueError(f"Chapter number mismatch in {lesson_path.relative_to(ROOT)}")
    pack.setdefault("chapter_title_fa", f"فصل {order}")
    pack.setdefault("chapter_title_en", f"Chapter {order}")
    pack["lessons"] = [rows[uid] for uid in order_uids]
    out = chapter / "build" / "chapter.json"
    write_atomic(out, pack)
    return out, len(pack["lessons"])

def assemble_all(strict: bool = False):
    outputs = {}
    for order in range(1, 69):
        path, count = assemble_chapter(order, strict)
        if path:
            outputs[order] = (path, count)
    if strict and set(outputs) != set(range(1, 69)):
        raise RuntimeError(f"Compiled packs missing for chapters: {sorted(set(range(1,69))-set(outputs))}")
    print(f"[chapter-assemble] chapters={len(outputs)} lessons={sum(count for _,count in outputs.values())} strict={strict}")
    return outputs

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--strict", action="store_true", help="Require the numeric/type-separated layout for all 68 chapters")
    args = parser.parse_args()
    assemble_all(args.strict)

if __name__ == "__main__":
    main()
