#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Non-destructive structural/coverage audit for NetworkAll JSON content packs.

This is a heuristic triage tool, not a technical correctness checker. It never
edits or deletes content. Weak items should be reviewed and then revised or
quarantined with a backup rather than removed blindly.
"""
from __future__ import annotations

import argparse
import gzip
import json
import re
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PACK_GLOBS = (
    "tools/packs/**/*.json",
    "tools/engineer_jokar_*/*pack*.json",
    "tools/engineer_jokar_*/*curriculum*.json",
    "tools/ENGINEER_JOKAR_*.json",
)
LAB_RE = re.compile(r"\b(lab|laboratory|verify|verification|expected output|cleanup|rollback)\b|لاب|آزمایشگاه|خروجی مورد انتظار|راستی.?آزمایی", re.I)
SCENARIO_RE = re.compile(r"scenario|incident|root cause|symptom|سناریو|علائم|علت ریشه.?ای", re.I)
ANSWER_RE = re.compile(r"answer[_ -]?key|correct[_ -]?answer|پاسخ.?نامه|کلید پاسخ", re.I)
SOURCE_RE = re.compile(r"official source|references?|rfc\s*\d|منابع رسمی|منبع:", re.I)
NETWORK_TERMS = re.compile(r"\b(vlan|trunk|stp|ospf|bgp|router|switch|subnet|routing|ethernet|tcp/ip|network|networking|ipv4|ipv6|ip address|addressing)\b|سوئیچ|روتر|مسیریابی|شبکه|آی.?پی|آدرس", re.I)


def text(value):
    if value is None:
        return ""
    if isinstance(value, str):
        return value
    if isinstance(value, (list, tuple)):
        return "\n".join(text(x) for x in value)
    if isinstance(value, dict):
        return "\n".join(f"{k}: {text(v)}" for k, v in value.items())
    return str(value)


def pack_files():
    found = {}
    for pattern in PACK_GLOBS:
        for path in ROOT.glob(pattern):
            if path.is_file() and path.stat().st_size > 0:
                found[str(path.resolve())] = path
    return sorted(found.values())


def _with_audit_context(item, **context):
    row = dict(item)
    row["_audit_context"] = context
    return row


def extract_items(obj, path):
    """Yield normalized lesson/command-like records from known pack shapes."""
    if not isinstance(obj, dict):
        return []
    items = []
    if isinstance(obj.get("lessons"), list):
        items.extend(x for x in obj["lessons"] if isinstance(x, dict))
    if isinstance(obj.get("commands"), list):
        items.extend(x for x in obj["commands"] if isinstance(x, dict))
    if isinstance(obj.get("chapters"), list):
        for chapter in obj["chapters"]:
            if not isinstance(chapter, dict):
                continue
            try:
                chapter_order = int(chapter.get("order", chapter.get("chapter_order", 0)) or 0)
            except (TypeError, ValueError):
                chapter_order = 0
            chapter_title = text(chapter.get("title_fa") or chapter.get("title_en") or chapter.get("title"))
            for sub in chapter.get("subchapters") or []:
                if isinstance(sub, dict):
                    sub_title = text(sub.get("title_fa") or sub.get("title_en") or sub.get("title"))
                    items.extend(
                        _with_audit_context(
                            row,
                            chapter_order=chapter_order or None,
                            chapter_title=chapter_title,
                            subchapter_title=sub_title,
                        )
                        for row in (sub.get("lessons") or [])
                        if isinstance(row, dict)
                    )
    curriculum = obj.get("curriculum")
    if isinstance(curriculum, dict):
        for chapter in curriculum.get("chapters") or []:
            for collection in (chapter.get("collections") or []) if isinstance(chapter, dict) else []:
                for lesson in (collection.get("lessons") or []) if isinstance(collection, dict) else []:
                    if not isinstance(lesson, dict):
                        continue
                    subs = lesson.get("sub_lessons") or []
                    if subs:
                        items.extend(x for x in subs if isinstance(x, dict))
                    else:
                        items.append(lesson)
    if not items and any(k in obj for k in ("title_fa", "title_en", "uid", "command")):
        items.append(obj)
    return items


def record_blob(item):
    keys = (
        "title_fa", "title_en", "title", "command", "summary", "content",
        "full_content", "explanation", "steps", "steps_fa", "examples",
        "sample_output", "expected_result", "lab", "lab_hint_fa", "scenario",
        "tasks", "solution", "verification", "notes", "references",
        "official_sources", "assessment", "questions", "answer_key",
        "meta", "meta_json", "metaJson",
        "prerequisites", "prerequisites_fa", "commands",
    )
    return "\n".join(text(item.get(k)) for k in keys if k in item)


def mark_template_heavy(rows, records):
    """Flag records dominated by long paragraphs repeated across many lessons."""
    paragraphs_by_record = []
    frequency = Counter()
    for item in records:
        raw = text(item.get("full_content") or item.get("content") or item.get("explanation"))
        paragraphs = [
            re.sub(r"\s+", " ", p).strip().lower()
            for p in re.split(r"\n\s*\n", raw)
            if len(re.sub(r"\s+", " ", p).strip()) >= 70
        ]
        paragraphs_by_record.append((paragraphs, len(raw)))
        frequency.update(set(paragraphs))
    threshold = max(5, (len(records) + 3) // 4)
    repeated = {p for p, count in frequency.items() if count >= threshold}
    for row, (paragraphs, total) in zip(rows, paragraphs_by_record):
        repeated_chars = sum(len(p) for p in paragraphs if p in repeated)
        if total >= 1000 and repeated_chars / max(1, total) >= 0.5:
            row["checks"].append("template_heavy")


def metadata_dicts(item):
    """Return top-level and nested assessment metadata in supported pack shapes."""
    found = [item]
    for key in ("meta", "meta_json", "metaJson"):
        value = item.get(key)
        if isinstance(value, str):
            try:
                value = json.loads(value)
            except (TypeError, ValueError):
                continue
        if not isinstance(value, dict):
            continue
        found.append(value)
        assessment = value.get("assessment")
        if isinstance(assessment, dict):
            found.append(assessment)
    return found


def inspect_record(path, item, index, min_chars):
    title = text(item.get("title_fa") or item.get("title_en") or item.get("title") or item.get("command") or f"item-{index}")
    blob = record_blob(item)
    is_network_topic = bool(NETWORK_TERMS.search(title))
    generic_terms = (
        "vlan", "trunk", "stp", "show running-config", "configure terminal",
        "show ip interface brief", "vrf", "router", "switch", "gateway",
        "uplink", "spanning tree",
    )
    generic_network_boilerplate = (
        not is_network_topic
        and sum(term in blob.lower() for term in generic_terms) >= 4
    )
    meta_nodes = metadata_dicts(item)
    has_assessment = any(
        node.get("assessment") or node.get("questions")
        for node in meta_nodes
    )
    has_answer_key = any(
        node.get("answer_key") or node.get("answers")
        for node in meta_nodes
    ) or bool(ANSWER_RE.search(blob))
    status = text(item.get("source_status") or item.get("status") or (item.get("meta") or {}).get("status")).lower()
    checks = {
        "needs_human_review": any(flag in status for flag in ("review_required", "draft", "seeded", "todo")),
        "shallow": len(blob.strip()) < min_chars,
        "missing_lab_marker": not LAB_RE.search(blob),
        "missing_scenario_marker": not SCENARIO_RE.search(blob),
        "missing_answer_key_marker": not ANSWER_RE.search(blob),
        "missing_source_marker": not SOURCE_RE.search(blob),
        "generic_network_boilerplate": generic_network_boilerplate,
        "missing_title": not any(item.get(k) for k in ("title_fa", "title_en", "title", "command")),
    }
    uid = text(item.get("uid") or item.get("id") or item.get("code")).strip()
    context = item.get("_audit_context") if isinstance(item.get("_audit_context"), dict) else {}
    return {
        "file": str(path.relative_to(ROOT)).replace("\\", "/"),
        "index": index,
        "uid": uid,
        "title": title[:180],
        "chapter_order": context.get("chapter_order"),
        "chapter_title": context.get("chapter_title", ""),
        "subchapter_title": context.get("subchapter_title", ""),
        "content_chars": len(blob),
        "checks": [k for k, value in checks.items() if value],
        "field_presence": {
            "summary": bool(item.get("summary")),
            "content": bool(item.get("full_content") or item.get("content") or item.get("explanation")),
            "examples": bool(item.get("examples") or item.get("sample_output")),
            "commands_or_steps": bool(item.get("commands") or item.get("steps") or item.get("steps_fa")),
            "assessment": bool(has_assessment),
            "answer_key": bool(has_answer_key),
            "sources": bool(item.get("official_sources") or item.get("references") or SOURCE_RE.search(blob)),
        },
    }


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--json", dest="json_path", help="write full report JSON")
    ap.add_argument("--min-chars", type=int, default=1200, help="heuristic minimum combined characters per item (default: 1200)")
    ap.add_argument("--fail-on-warnings", action="store_true", help="return exit code 1 if any warning is found")
    args = ap.parse_args()

    files = pack_files()
    active_asset = ROOT / "android/app/src/main/assets/curriculum_index.json.gz"
    report = {
        "tool": "audit_content_packs",
        "heuristic_only": True,
        "min_chars": args.min_chars,
        "files_scanned": 0,
        "records_scanned": 0,
        "parse_errors": [],
        "file_summaries": [],
        "items": [],
        "duplicate_ids": [],
        "warning_counts": {},
        "notes": [
            "No file is modified or deleted.",
            "Length and marker checks do not establish technical correctness.",
            "Review false positives; some command-reference records are intentionally concise.",
        ],
    }
    id_locations = {}
    for path in files:
        try:
            if path.suffix.lower() == ".gz":
                with gzip.open(path, "rt", encoding="utf-8-sig") as handle:
                    data = json.load(handle)
            else:
                data = json.loads(path.read_text(encoding="utf-8-sig"))
        except Exception as exc:
            report["parse_errors"].append({"file": str(path.relative_to(ROOT)), "error": str(exc)})
            continue
        records = extract_items(data, path)
        report["files_scanned"] += 1
        file_items = [inspect_record(path, item, i, args.min_chars) for i, item in enumerate(records, 1)]
        mark_template_heavy(file_items, records)
        report["records_scanned"] += len(file_items)
        for row in file_items:
            if row["uid"]:
                id_locations.setdefault(row["uid"], []).append({"file": row["file"], "index": row["index"], "title": row["title"]})
            report["items"].append(row)
        report["file_summaries"].append({
            "file": str(path.relative_to(ROOT)).replace("\\", "/"),
            "records": len(file_items),
            "shallow": sum("shallow" in x["checks"] for x in file_items),
            "missing_lab_marker": sum("missing_lab_marker" in x["checks"] for x in file_items),
            "missing_answer_key_marker": sum("missing_answer_key_marker" in x["checks"] for x in file_items),
        })

    # Audit the actual Android curriculum asset separately; pack and output IDs may
    # intentionally overlap, so output records are not mixed into duplicate-ID checks.
    report["active_curriculum"] = {"file": str(active_asset.relative_to(ROOT)), "records": 0, "warnings": {}}
    if active_asset.is_file():
        try:
            with gzip.open(active_asset, "rt", encoding="utf-8-sig") as handle:
                active_data = json.load(handle)
            active_records = extract_items(active_data, active_asset)
            active_rows = [inspect_record(active_asset, item, i, args.min_chars) for i, item in enumerate(active_records, 1)]
            mark_template_heavy(active_rows, active_records)
            report["active_curriculum"]["records"] = len(active_rows)
            active_counts = Counter(check for item in active_rows for check in item["checks"])
            report["active_curriculum"]["warnings"] = dict(sorted(active_counts.items()))
            priority = {
                "missing_title": 100, "shallow": 90, "template_heavy": 80,
                "generic_network_boilerplate": 70, "missing_answer_key_marker": 65,
                "missing_lab_marker": 55, "missing_scenario_marker": 45,
                "missing_source_marker": 35, "needs_human_review": 0,
            }
            review_rows = sorted(
                (item for item in active_rows if item["checks"]),
                key=lambda item: (
                    -sum(priority.get(check, 10) for check in item["checks"]),
                    item["index"],
                ),
            )
            report["active_curriculum"]["review_samples"] = [
                {
                    "uid": item["uid"], "title": item["title"],
                    "chapter_order": item["chapter_order"],
                    "chapter_title": item["chapter_title"],
                    "subchapter_title": item["subchapter_title"],
                    "checks": item["checks"], "content_chars": item["content_chars"],
                }
                for item in review_rows[:500]
            ]
        except Exception as exc:
            report["active_curriculum"]["error"] = str(exc)

    report["duplicate_ids"] = [
        {"uid": uid, "locations": locations}
        for uid, locations in sorted(id_locations.items()) if len(locations) > 1
    ]
    counts = Counter(check for item in report["items"] for check in item["checks"])
    report["warning_counts"] = dict(sorted(counts.items()))
    report["summary"] = {
        "files_found": len(files),
        "files_scanned": report["files_scanned"],
        "records_scanned": report["records_scanned"],
        "parse_errors": len(report["parse_errors"]),
        "duplicate_ids": len(report["duplicate_ids"]),
        "items_with_any_warning": sum(bool(x["checks"]) for x in report["items"]),
    }

    print("=== NetworkAll content-pack audit (non-destructive) ===")
    print(json.dumps(report["summary"], ensure_ascii=False, indent=2))
    if report["parse_errors"]:
        print("\nJSON parse errors:")
        for error in report["parse_errors"]:
            print(" -", error["file"], ":", error["error"])
    print("\nWarning counts:")
    for key, count in report["warning_counts"].items():
        print(f" - {key}: {count}")
    print("\nFiles needing most review:")
    for row in sorted(report["file_summaries"], key=lambda x: (x["shallow"] + x["missing_answer_key_marker"] + x["missing_lab_marker"], x["records"]), reverse=True)[:20]:
        print(f" - {row['file']}: records={row['records']} shallow={row['shallow']} no_lab_marker={row['missing_lab_marker']} no_answer_key_marker={row['missing_answer_key_marker']}")
    if args.json_path:
        out = Path(args.json_path)
        if not out.is_absolute():
            out = ROOT / out
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
        print("\nJSON report:", out)
    warnings = bool(report["parse_errors"] or report["duplicate_ids"] or report["warning_counts"] or report.get("active_curriculum", {}).get("warnings"))
    return 1 if args.fail_on_warnings and warnings else 0


if __name__ == "__main__":
    raise SystemExit(main())
