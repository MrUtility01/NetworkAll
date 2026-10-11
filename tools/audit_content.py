#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Read-only content quality gate for database lessons and all JSON packs.

Usage:
  python tools/audit_content.py
  python tools/audit_content.py --packs-only --json docs/audits/content-audit.json
  python tools/audit_content.py --db server/data/encyclopedia.db
  python tools/audit_content.py --strict --packs-only

This tool reports deficiencies; it never deletes or rewrites lessons.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import sqlite3
import sys
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any, Iterator

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_PACK_ROOT = ROOT / "tools"
DEEP_LEN = 2000
MID_LEN = 800
MIN_PACK_BYTES = 2
SKIP_PARTS = {"_archive_zips", "__pycache__", ".git", "prompts"}
TITLE_FIELDS = ("title_fa", "title", "title_en", "command", "name")
TEXT_FIELDS = (
    "full_content", "content", "explanation", "body", "summary", "description",
    "when_to_use_fa", "steps_fa", "sample_output", "examples", "commands",
    "notes", "lab_hint_fa", "security_notes_fa", "troubleshooting",
)
LAB_MARKERS = ("lab", "لاب", "آزمایشگاه", "مراحل اجرا", "تمرین عملی")
TROUBLESHOOT_MARKERS = ("troubleshoot", "عیب‌یابی", "عیب یابی", "root cause", "rca")
PLACEHOLDERS = (
    "todo", "tbd", "lorem ipsum", "replace me", "fill this", "coming soon",
    "محتوا در دست ساخت", "بعدا تکمیل", "بعداً تکمیل", "تکمیل شود",
)


def _text(value: Any) -> str:
    if value is None:
        return ""
    if isinstance(value, (list, tuple)):
        return "\n".join(_text(x) for x in value)
    if isinstance(value, dict):
        return json.dumps(value, ensure_ascii=False, sort_keys=True)
    return str(value)


def _assessment(item: dict) -> dict:
    value = item.get("assessment")
    if isinstance(value, dict):
        return value
    meta = item.get("meta")
    if isinstance(meta, str):
        try:
            meta = json.loads(meta)
        except Exception:
            meta = {}
    if isinstance(meta, dict) and isinstance(meta.get("assessment"), dict):
        return meta["assessment"]
    return {}


def _candidate(item: dict) -> bool:
    if not any(_text(item.get(k)).strip() for k in TITLE_FIELDS):
        return False
    return (
        any(_text(item.get(k)).strip() for k in TEXT_FIELDS)
        or "assessment" in item
        or "questions" in item
        or "uid" in item
    )


def _walk_items(value: Any, chapter: int | None = None) -> Iterator[tuple[dict, int | None]]:
    if isinstance(value, dict):
        current = chapter
        if value.get("chapter_order") is not None:
            try:
                current = int(value["chapter_order"])
            except (TypeError, ValueError):
                pass
        elif value.get("order") is not None and any(
            k in value for k in ("subchapters", "collections", "lessons")
        ):
            try:
                current = int(value["order"])
            except (TypeError, ValueError):
                pass
        if _candidate(value):
            yield value, current
        for child in value.values():
            if isinstance(child, (dict, list)):
                yield from _walk_items(child, current)
    elif isinstance(value, list):
        for child in value:
            yield from _walk_items(child, chapter)


def _item_quality(item: dict) -> dict:
    pieces = [_text(item.get(k)) for k in TEXT_FIELDS if item.get(k) is not None]
    content = "\n".join(pieces)
    low = content.casefold()
    assessment = _assessment(item)
    questions = assessment.get("questions") if isinstance(assessment, dict) else None
    answers = assessment.get("answer_key") if isinstance(assessment, dict) else None
    if not isinstance(questions, list):
        questions = item.get("questions") if isinstance(item.get("questions"), list) else []
    if not isinstance(answers, list):
        answers = item.get("answer_key") if isinstance(item.get("answer_key"), list) else []
    qids = {str(q.get("id")) for q in questions if isinstance(q, dict) and q.get("id") is not None}
    if isinstance(answers, dict):
        aids = {str(key) for key in answers}
    else:
        aids = {
            str(a.get("question_id", a.get("id")))
            for a in answers if isinstance(a, dict) and a.get("question_id", a.get("id")) is not None
        }
    markers = {
        "lab": any(m in low for m in LAB_MARKERS),
        "troubleshooting": any(m in low for m in TROUBLESHOOT_MARKERS),
        "example": any(m in low for m in ("مثال", "example", "نمونه خروجی", "sample output")),
        "security": any(m in low for m in ("امنیت", "security", "hardening")),
        "verification": any(m in low for m in ("verify", "verification", "راستی‌آزمایی", "اعتبارسنجی")),
    }
    placeholder_hits = [p for p in PLACEHOLDERS if p in low]
    return {
        "content_chars": len(content),
        "band": "deep" if len(content) >= DEEP_LEN else "mid" if len(content) >= MID_LEN else "thin",
        "markers": markers,
        "has_questions": bool(questions),
        "has_answer_key": bool(answers),
        "answer_key_ids_match": bool(questions and answers and qids and qids.issubset(aids)),
        "question_count": len(questions),
        "answer_count": len(answers),
        "placeholder_hits": placeholder_hits,
    }


def audit_packs(pack_root: Path) -> dict:
    candidates = []
    parse_errors = []
    hashes: dict[str, list[str]] = defaultdict(list)
    processed_hashes: set[str] = set()
    parsed_files = 0
    for path in sorted(pack_root.rglob("*.json")):
        if any(part in SKIP_PARTS for part in path.parts):
            continue
        try:
            size = path.stat().st_size
            if size < MIN_PACK_BYTES:
                continue
            digest = hashlib.sha256(path.read_bytes()).hexdigest()
            hashes[digest].append(str(path.relative_to(ROOT)))
            # Exact byte-identical legacy copies are reported but parsed once, avoiding
            # false duplicate-UID alarms while old content locations are being migrated.
            if digest in processed_hashes:
                continue
            processed_hashes.add(digest)
            with path.open("r", encoding="utf-8-sig") as f:
                payload = json.load(f)
            parsed_files += 1
        except Exception as exc:
            parse_errors.append({"path": str(path.relative_to(ROOT)), "error": str(exc)})
            continue
        for item, chapter in _walk_items(payload):
            # The container document itself is not a lesson unless it has actual instructional content.
            if not _candidate(item):
                continue
            q = _item_quality(item)
            title = next((_text(item.get(k)).strip() for k in TITLE_FIELDS if _text(item.get(k)).strip()), "(untitled)")
            candidates.append({
                "path": str(path.relative_to(ROOT)),
                "chapter": chapter,
                "uid": _text(item.get("uid")).strip(),
                "title": title[:180],
                **q,
            })

    uid_paths: dict[str, list[dict]] = defaultdict(list)
    title_paths: dict[tuple[str, str], list[dict]] = defaultdict(list)
    by_chapter: dict[str, list[dict]] = defaultdict(list)
    for item in candidates:
        if item["uid"]:
            uid_paths[item["uid"]].append(item)
        # Group titles per file. Same title can occur in separate L0-L4 rows intentionally.
        key = (item["path"], re.sub(r"^\[L[0-4]\]\s*", "", item["title"]).casefold())
        title_paths[key].append(item)
        by_chapter[str(item["chapter"] or "unspecified")].append(item)

    chapter_summary = []
    for order, rows in sorted(by_chapter.items(), key=lambda pair: (pair[0] == "unspecified", pair[0])):
        bands = Counter(x["band"] for x in rows)
        chapter_summary.append({
            "chapter": order,
            "items": len(rows),
            "deep": bands["deep"],
            "mid": bands["mid"],
            "thin": bands["thin"],
            "pct_deep_or_mid": round(100 * (bands["deep"] + bands["mid"]) / max(1, len(rows)), 1),
            "missing_lab": sum(not x["markers"]["lab"] for x in rows),
            "missing_examples": sum(not x["markers"]["example"] for x in rows),
            "missing_verification": sum(not x["markers"]["verification"] for x in rows),
            "missing_questions": sum(not x["has_questions"] for x in rows),
            "missing_answer_key": sum(not x["has_answer_key"] for x in rows),
            "broken_answer_key": sum(bool(x["has_questions"]) and not x["answer_key_ids_match"] for x in rows),
        })

    return {
        "root": str(pack_root),
        "json_files_parsed": parsed_files,
        "instructional_records": len(candidates),
        "parse_errors": parse_errors,
        "duplicate_file_contents": [paths for paths in hashes.values() if len(paths) > 1],
        "duplicate_uids": {uid: [x["path"] + " :: " + x["title"] for x in rows]
                           for uid, rows in uid_paths.items() if len(rows) > 1},
        "duplicate_titles_within_file": {
            path + " :: " + title: len(rows)
            for (path, title), rows in title_paths.items() if len(rows) > 1
        },
        "bands": dict(Counter(x["band"] for x in candidates)),
        "missing_lab": sum(not x["markers"]["lab"] for x in candidates),
        "missing_troubleshooting": sum(not x["markers"]["troubleshooting"] for x in candidates),
        "missing_examples": sum(not x["markers"]["example"] for x in candidates),
        "missing_security": sum(not x["markers"]["security"] for x in candidates),
        "missing_verification": sum(not x["markers"]["verification"] for x in candidates),
        "missing_questions": sum(not x["has_questions"] for x in candidates),
        "missing_answer_key": sum(not x["has_answer_key"] for x in candidates),
        "broken_answer_key_records": [x for x in candidates if x["has_questions"] and not x["answer_key_ids_match"]][:200],
        "placeholder_records": [x for x in candidates if x["placeholder_hits"]][:200],
        "weakest_records": sorted(candidates, key=lambda x: (x["content_chars"], x["path"]))[:100],
        "chapters": chapter_summary,
    }


def load_curriculum_skeleton() -> list[dict]:
    sys.path.insert(0, str(ROOT / "server"))
    from core.full_curriculum import get_full_curriculum
    curriculum = get_full_curriculum()
    out = []
    for order, title_fa, title_en, levels in curriculum:
        out.append({
            "order": int(order),
            "title_fa": title_fa,
            "levels": len(levels),
            "lessons": sum(len(items) for _, items in levels),
        })
    return out


def audit_db(db_path: Path) -> dict:
    conn = sqlite3.connect(str(db_path))
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    chapters = cur.execute("SELECT id, order_index, title_fa FROM chapters ORDER BY order_index").fetchall()
    stats = {
        "chapters": len(chapters),
        "levels": cur.execute("SELECT COUNT(*) c FROM levels").fetchone()["c"],
        "lessons": cur.execute("SELECT COUNT(*) c FROM lessons").fetchone()["c"],
        "scenarios": cur.execute("SELECT COUNT(*) c FROM scenarios").fetchone()["c"],
    }
    by_chapter, shallow, missing = [], [], Counter()
    for ch in chapters:
        rows = cur.execute("""
            SELECT l.title_fa, l.summary, l.full_content, l.commands, l.examples, l.notes, l.meta_json
            FROM lessons l JOIN levels lv ON lv.id=l.level_id
            WHERE lv.chapter_id=? ORDER BY lv.order_index, l.order_index
        """, (ch["id"],)).fetchall()
        bands = Counter()
        for row in rows:
            content = "\n".join(_text(row[k]) for k in ("full_content", "summary", "commands", "examples", "notes"))
            low = content.casefold()
            bands["deep" if len(row["full_content"] or "") >= DEEP_LEN else "mid" if len(row["full_content"] or "") >= MID_LEN else "thin"] += 1
            for name, markers in (
                ("lab", LAB_MARKERS),
                ("troubleshooting", TROUBLESHOOT_MARKERS),
                ("example", ("مثال", "example", "نمونه خروجی", "sample output")),
                ("verification", ("verify", "verification", "راستی‌آزمایی", "اعتبارسنجی")),
                ("security", ("امنیت", "security", "hardening")),
            ):
                if not any(marker in low for marker in markers):
                    missing[name] += 1
            try:
                meta = json.loads(row["meta_json"] or "{}")
            except Exception:
                meta = {}
            assessment = meta.get("assessment") if isinstance(meta, dict) else {}
            if not isinstance(assessment, dict) or not assessment.get("questions"):
                missing["questions"] += 1
            if not isinstance(assessment, dict) or not assessment.get("answer_key"):
                missing["answer_key"] += 1
            n = len(row["full_content"] or "")
            if n < 400:
                shallow.append({"chapter": ch["order_index"], "title": (row["title_fa"] or "")[:100], "full_len": n})
        by_chapter.append({
            "order": ch["order_index"], "title_fa": ch["title_fa"], "lessons": len(rows),
            "deep_ge_2000": bands["deep"], "mid_ge_800": bands["mid"], "thin_lt_800": bands["thin"],
            "depth_score": round(100 * (bands["deep"] + 0.5 * bands["mid"]) / max(1, len(rows)), 1),
        })
    weakest = sorted(by_chapter, key=lambda x: (x["depth_score"], -x["thin_lt_800"]))
    sc_rows = cur.execute("""
        SELECT code,title_fa,length(COALESCE(tasks,'')) AS tasks_len,
               length(COALESCE(solution,'')) AS solution_len,
               length(COALESCE(verification,'')) AS verification_len FROM scenarios
    """).fetchall()
    conn.close()
    return {
        "db": str(db_path), "stats": stats, "chapter_depth": by_chapter,
        "weakest_chapters": weakest[:15], "strongest_chapters": list(reversed(weakest[-10:])),
        "shallow_lessons": shallow[:300], "shallow_count": len(shallow),
        "missing_sections": dict(missing),
        "thin_scenarios": [dict(x) for x in sc_rows if x["tasks_len"] < 80 or x["solution_len"] < 40 or x["verification_len"] < 40],
    }


def main() -> int:
    ap = argparse.ArgumentParser(description="Read-only instructional content audit")
    ap.add_argument("--db", help="SQLite database path")
    ap.add_argument("--json", help="write report JSON")
    ap.add_argument("--packs-root", default=str(DEFAULT_PACK_ROOT), help="root directory to recursively scan for JSON packs")
    ap.add_argument("--packs-only", action="store_true", help="audit JSON packs without curriculum/database")
    ap.add_argument("--curriculum-only", action="store_true", help="only summarize the Python curriculum skeleton")
    ap.add_argument("--strict", action="store_true", help="exit non-zero on malformed JSON, duplicate UIDs, or mismatched answer keys")
    args = ap.parse_args()

    report: dict[str, Any] = {}
    if not args.packs_only and not args.db:
        try:
            report["curriculum"] = load_curriculum_skeleton()
            report["curriculum_summary"] = {
                "chapters": len(report["curriculum"]),
                "lessons": sum(x["lessons"] for x in report["curriculum"]),
                "missing_orders_1_to_68": sorted(set(range(1, 69)) - {x["order"] for x in report["curriculum"]}),
            }
        except Exception as exc:
            report["curriculum_error"] = str(exc)
    if not args.curriculum_only:
        try:
            report["packs"] = audit_packs(Path(args.packs_root).resolve())
        except Exception as exc:
            report["packs_error"] = str(exc)
    if args.db:
        db_path = Path(args.db)
        if not db_path.is_file():
            db_path = ROOT / args.db
        if not db_path.is_file():
            print("DB not found:", args.db, file=sys.stderr)
            return 2
        report["database"] = audit_db(db_path)

    print(json.dumps(report, ensure_ascii=False, indent=2))
    if args.json:
        target = Path(args.json)
        if not target.is_absolute():
            target = ROOT / target
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
        print(f"Wrote report: {target}")
    if args.strict:
        pack = report.get("packs", {})
        if pack.get("parse_errors") or pack.get("duplicate_uids") or pack.get("broken_answer_key_records"):
            return 1
        if report.get("packs_error"):
            return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
