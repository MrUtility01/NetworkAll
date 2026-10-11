#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Offline audit for JSON lesson and command packs."""
from __future__ import annotations
import argparse
import hashlib
import json
import re
import statistics
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
TITLE_KEYS = ("title_fa", "title_en", "title", "name", "command")
UID_KEYS = ("uid", "id")
TEXT_KEYS = ("full_content", "content", "body", "explanation", "summary", "notes",
             "examples", "commands", "command", "steps_fa", "when_to_use_fa",
             "lab_hint_fa", "security_notes_fa", "prerequisites_fa")
LAB_RE = re.compile(r"\b(lab|laboratory|topology|hands[- ]on|rollback)\b|لابراتوار|آزمایشگاه|مراحل اجرا", re.I)
SCENARIO_RE = re.compile(r"\b(scenario|case study|incident)\b|سناریو|مطالعه موردی|رخداد", re.I)
VERIFY_RE = re.compile(r"\b(verify|verification|expected output|acceptance criteria)\b|اعتبارسنجی|خروجی مورد انتظار|معیار پذیرش", re.I)
ASSESS_RE = re.compile(r"\b(assessment|questions?|quiz|answer.?key|correct_index)\b|سوالات ارزیابی|پرسش‌های ارزیابی|کلید پاسخ|پاسخ صحیح", re.I)
SOURCE_RE = re.compile(r"\b(reference|references|source|documentation|rfc)\b|منابع معتبر|منبع رسمی|مراجع", re.I)

def text_of(value: Any) -> str:
    if value is None:
        return ""
    if isinstance(value, str):
        return value
    if isinstance(value, (int, float, bool)):
        return str(value)
    if isinstance(value, dict):
        return "\n".join(f"{k}: {text_of(v)}" for k, v in value.items())
    if isinstance(value, list):
        return "\n".join(text_of(v) for v in value)
    return ""

def title_of(record: dict) -> str:
    return next((str(record[k]).strip() for k in TITLE_KEYS if record.get(k) not in (None, "")), "")

def is_record(node: Any) -> bool:
    if not isinstance(node, dict) or "sub_lessons" in node or "collections" in node:
        return False
    return bool(title_of(node) and any(text_of(node.get(k)).strip() for k in TEXT_KEYS))

def walk_records(node: Any, location=()):
    if isinstance(node, dict):
        if is_record(node):
            yield node, location
            return
        for key, val in node.items():
            if isinstance(val, (dict, list)):
                yield from walk_records(val, location + (key,))
    elif isinstance(node, list):
        for i, val in enumerate(node):
            if isinstance(val, (dict, list)):
                yield from walk_records(val, location + (i,))

def primary_content(record: dict) -> str:
    for key in ("full_content", "content", "body", "explanation", "summary"):
        val = text_of(record.get(key)).strip()
        if val:
            return val
    return "\n".join(text_of(record.get(k)) for k in TEXT_KEYS if record.get(k) is not None)

def all_content(record: dict) -> str:
    keys = TEXT_KEYS + ("assessment", "answer_key", "flashcards", "learning_objectives", "tags")
    return "\n".join(text_of(record.get(k)) for k in keys if record.get(k) is not None)

def has_answer(record: dict, blob: str) -> bool:
    assessment = record.get("assessment")
    if isinstance(assessment, dict) and any(assessment.get(k) for k in ("answer_key", "answers", "solutions", "correct_answers")):
        return True
    return bool(record.get("answer_key") or re.search(r"answer.?key|correct_index|کلید پاسخ|پاسخ صحیح", blob, re.I))

def normalized_body(value: str) -> str:
    lines = value.splitlines()
    if lines and lines[0].lstrip().startswith("#"):
        lines = lines[1:]
    value = "\n".join(lines).lower()
    value = re.sub(r"\[[lL][0-4]\]\s*", "", value)
    return re.sub(r"\s+", " ", value).strip()

def audit_file(path: Path, root: Path) -> dict:
    rel = path.relative_to(root).as_posix()
    raw = path.read_text(encoding="utf-8-sig")
    data = json.loads(raw)
    records = list(walk_records(data))
    titles = [title_of(r) for r, _ in records if title_of(r)]
    uids = [str(r[k]).strip() for r, _ in records for k in UID_KEYS if r.get(k) not in (None, "")]
    duplicate_uids = sorted(k for k, n in Counter(uids).items() if n > 1)
    rows, body_hashes, paragraphs = [], Counter(), Counter()
    for r, loc in records:
        body = primary_content(r)
        blob = all_content(r)
        assessment = r.get("assessment")
        has_assessment = bool(assessment) or bool(ASSESS_RE.search(blob))
        row = {
            "uid": next((str(r[k]) for k in UID_KEYS if r.get(k)), ""),
            "title": title_of(r),
            "location": "/".join(map(str, loc)),
            "chapter_order": r.get("chapter_order"),
            "level": str(r.get("level") or ""),
            "content_chars": len(body),
            "has_lab": bool(LAB_RE.search(blob)),
            "has_scenario": bool(SCENARIO_RE.search(blob)),
            "has_verification": bool(VERIFY_RE.search(blob)),
            "has_commands": bool(r.get("commands") or r.get("command") or chr(96) * 3 in blob),
            "has_assessment": has_assessment,
            "has_answer_key": has_answer(r, blob),
            "has_sources": bool(SOURCE_RE.search(blob)),
            "has_title_en": bool(text_of(r.get("title_en")).strip()),
            "body_hash": hashlib.sha256(normalized_body(body).encode("utf-8")).hexdigest() if body else "",
        }
        rows.append(row)
        if row["body_hash"]:
            body_hashes[row["body_hash"]] += 1
        for p in re.split(r"\n\s*\n", body):
            p = re.sub(r"\s+", " ", p).strip().lower()
            p = re.sub(r"\[[lL][0-4]\]\s*", "", p)
            if len(p) >= 120:
                paragraphs[p] += 1
    lengths = sorted(r["content_chars"] for r in rows)
    n = len(rows)
    coverage = {k: sum(bool(r[k]) for r in rows) for k in
                ("has_lab", "has_scenario", "has_verification", "has_commands", "has_assessment", "has_answer_key", "has_sources")}
    pct = {k: round(v * 100 / n, 1) if n else 0 for k, v in coverage.items()}
    repeated_threshold = max(3, int(n * 0.4 + 0.999))
    repeated = [{"records": v, "text": k[:240]} for k, v in paragraphs.items() if v >= repeated_threshold]
    repeated.sort(key=lambda x: x["records"], reverse=True)
    missing_uid = sum(not any(r.get(k) for k in UID_KEYS) for r, _ in records)
    missing_content = sum(not primary_content(r) for r, _ in records)
    errors = []
    if not records:
        errors.append("no_records_found")
    if duplicate_uids:
        errors.append("duplicate_uids_within_pack")
    if missing_uid:
        errors.append("records_missing_uid")
    if missing_content:
        errors.append("records_missing_content")
    score = round(
        (sum(x >= 800 for x in lengths) / n * 35 if n else 0)
        + pct["has_lab"] * 0.15 + pct["has_verification"] * 0.15
        + pct["has_assessment"] * 0.15 + pct["has_answer_key"] * 0.10
        + pct["has_scenario"] * 0.10, 1)
    return {
        "path": rel, "bytes": len(raw.encode("utf-8")), "root_keys": list(data) if isinstance(data, dict) else [],
        "records": n, "uid_missing": missing_uid, "duplicate_uids": duplicate_uids[:30],
        "duplicate_title_count": sum(v > 1 for v in Counter(titles).values()),
        "duplicate_body_count": sum(v - 1 for v in body_hashes.values() if v > 1),
        "shallow_lt_800": sum(x < 800 for x in lengths),
        "mid_800_to_1999": sum(800 <= x < 2000 for x in lengths),
        "deep_ge_2000": sum(x >= 2000 for x in lengths),
        "content_chars": {"min": lengths[0] if lengths else 0, "median": statistics.median(lengths) if lengths else 0,
                          "mean": round(statistics.mean(lengths), 1) if lengths else 0, "max": lengths[-1] if lengths else 0},
        "coverage": coverage, "coverage_pct": pct,
        "repeated_paragraph_count": len(repeated), "repeated_paragraphs": repeated[:10],
        "quality_score_heuristic": score, "structural_errors": errors,
        "weakest_lessons": sorted(rows, key=lambda r: (r["has_lab"] + r["has_verification"] + r["has_assessment"] + r["has_answer_key"], r["content_chars"]))[:12],
    }

def discover(root: Path):
    tool_dir = root / "tools"
    return sorted(p for p in tool_dir.rglob("*.json") if "_archive_zips" not in p.parts) if tool_dir.exists() else []

def run(root: Path) -> dict:
    packs, uid_to_paths = [], defaultdict(set)
    for path in discover(root):
        try:
            item = audit_file(path, root)
            packs.append(item)
            data = json.loads(path.read_text(encoding="utf-8-sig"))
            for r, _ in walk_records(data):
                uid = next((str(r[k]).strip() for k in UID_KEYS if r.get(k) not in (None, "")), "")
                if uid:
                    uid_to_paths[uid].add(path.relative_to(root).as_posix())
        except Exception as exc:
            packs.append({"path": path.relative_to(root).as_posix(), "error": f"{type(exc).__name__}: {exc}",
                          "records": 0, "structural_errors": ["invalid_json_or_pack"]})
    cross = [{"uid": uid, "paths": sorted(paths)} for uid, paths in uid_to_paths.items() if len(paths) > 1]
    return {
        "schema_version": 1,
        "summary": {"packs_scanned": len(packs), "invalid_packs": sum(bool(p.get("error")) for p in packs),
                    "structurally_flagged_packs": sum(bool(p.get("structural_errors")) for p in packs),
                    "records": sum(p.get("records", 0) for p in packs), "cross_pack_duplicate_uids": len(cross)},
        "cross_pack_duplicate_uids_sample": cross[:100], "packs": packs,
    }

def markdown(report: dict) -> str:
    lines = ["# گزارش ممیزی محتوا", "", "امتیاز غربالگری ماشینی است و جای بازبینی علمی را نمی‌گیرد.", "",
             f"- فایل‌ها: {report['summary']['packs_scanned']}",
             f"- JSON نامعتبر: {report['summary']['invalid_packs']}",
             f"- رکوردهای قابل شناسایی: {report['summary']['records']}",
             f"- UIDهای تکراری بین فایل‌ها: {report['summary']['cross_pack_duplicate_uids']}", "",
             "| فایل | رکورد | امتیاز | متن <۸۰۰ | متن ≥۲۰۰۰ | Lab | Verify | آزمون | پاسخ‌نامه | پاراگراف تکراری |",
             "|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|"]
    for p in sorted(report["packs"], key=lambda x: (x.get("quality_score_heuristic", 0), x.get("records", 0))):
        if p.get("error"):
            lines.append(f"| {p['path']} | — | — | — | — | — | — | — | — | — |")
            continue
        c = p["coverage_pct"]
        lines.append(f"| {p['path']} | {p['records']} | {p['quality_score_heuristic']} | {p['shallow_lt_800']} | "
                     f"{p['deep_ge_2000']} | {c['has_lab']}% | {c['has_verification']}% | {c['has_assessment']}% | "
                     f"{c['has_answer_key']}% | {p['repeated_paragraph_count']} |")
    lines.extend(["", "## هشدارهای ساختاری", ""])
    errors = [p for p in report["packs"] if p.get("error") or p.get("structural_errors")]
    if not errors:
        lines.append("خطای ساختاری ماشینی مشاهده نشد.")
    for p in errors:
        lines.append(f"- {p['path']}: {p.get('error') or ', '.join(p.get('structural_errors', []))}")
    return "\n".join(lines) + "\n"

def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--root", type=Path, default=ROOT)
    ap.add_argument("--json-out", type=Path)
    ap.add_argument("--markdown-out", type=Path)
    ap.add_argument("--strict", action="store_true", help="fail on invalid JSON, missing content/UID, or duplicate UIDs in a pack")
    ap.add_argument("--strict-json", action="store_true", help="fail only when a source JSON file cannot be parsed")
    args = ap.parse_args()
    root = args.root.resolve()
    report = run(root)
    print(json.dumps(report["summary"], ensure_ascii=False, indent=2))
    for p in sorted(report["packs"], key=lambda x: (x.get("quality_score_heuristic", 0), x.get("records", 0))):
        if p.get("error"):
            print(f"ERROR {p['path']}: {p['error']}")
        else:
            c = p["coverage_pct"]
            print(f"{p['quality_score_heuristic']:5.1f} | {p['records']:5d} rec | <800={p['shallow_lt_800']:4d} | "
                  f"lab={c['has_lab']:5.1f}% verify={c['has_verification']:5.1f}% assess={c['has_assessment']:5.1f}% "
                  f"answer={c['has_answer_key']:5.1f}% | {p['path']}")
    if args.json_out:
        args.json_out.parent.mkdir(parents=True, exist_ok=True)
        args.json_out.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    if args.markdown_out:
        args.markdown_out.parent.mkdir(parents=True, exist_ok=True)
        args.markdown_out.write_text(markdown(report), encoding="utf-8")
    if args.strict and any(p.get("error") or p.get("structural_errors") for p in report["packs"]):
        return 1
    if args.strict_json and any(p.get("error") for p in report["packs"]):
        return 1
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
