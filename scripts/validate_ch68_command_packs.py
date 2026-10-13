#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Validate additive Chapter 68 command packs and report Cisco 1600-record goal."""
from __future__ import annotations
import json
import sys
from pathlib import Path
from collections import Counter

ROOT = Path(__file__).resolve().parents[1]
PACKS = ROOT / "tools/packs/commands_encyclopedia"
REQUIRED = {
    "cisco_routing.json": ("cisco_routing", 151),
    "cisco_routing_addon_01.json": ("cisco_routing", 200),
    "cisco_routing_addon_02.json": ("cisco_routing", 200),
    "cisco_routing_addon_03.json": ("cisco_routing", 200),
    "cisco_routing_addon_04.json": ("cisco_routing", 200),
    "cisco_routing_addon_05.json": ("cisco_routing", 200),
    "cisco_routing_addon_06.json": ("cisco_routing", 200),
    "cisco_routing_addon_07.json": ("cisco_routing", 200),
    "cisco_routing_addon_08.json": ("cisco_routing", 49),
    "cisco_switching.json": ("cisco_switching", 20),
    "mikrotik_ops_addon.json": ("mikrotik", 43),
    "mikrotik_ops_addon_02.json": ("mikrotik", 100),
    "mikrotik_ops_addon_03.json": ("mikrotik", 41),
    "powershell.json": ("powershell", 49),
    "powershell_addon_01.json": ("powershell", 100),
    "powershell_addon_02.json": ("powershell", 25),
    "windows_batch.json": ("windows_batch", 20),
    "linux.json": ("linux", 20),
}
FIELDS = (
    "uid", "vendor", "platform", "version_scope", "privilege", "command",
    "title_fa", "syntax", "when_to_use_fa", "prerequisites_fa", "steps_fa",
    "sample_output", "common_mistakes_fa", "security_notes_fa", "lab_hint_fa",
    "verify_steps_fa", "rollback_fa", "source_urls", "assessment",
)

def fail(message: str) -> None:
    print(f"ERROR: {message}", file=sys.stderr)
    raise SystemExit(1)

def main() -> None:
    global_uids: dict[str, str] = {}
    totals = Counter()
    for filename, (platform, minimum) in REQUIRED.items():
        path = PACKS / filename
        if not path.is_file():
            fail(f"missing required command pack: {path}")
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except Exception as exc:
            fail(f"{filename}: invalid JSON: {exc}")
        if int(data.get("chapter_order", 0)) != 68:
            fail(f"{filename}: chapter_order must be 68")
        commands = data.get("commands")
        if not isinstance(commands, list) or len(commands) < minimum:
            fail(f"{filename}: expected at least {minimum} command records")
        local_uids = set()
        local_commands = set()
        for i, record in enumerate(commands, 1):
            if not isinstance(record, dict):
                fail(f"{filename}[{i}]: record must be an object")
            missing = [field for field in FIELDS if field not in record or record[field] in (None, "", [], {})]
            if missing:
                fail(f"{filename}[{i}]: missing required fields: {missing}")
            uid = str(record["uid"]).strip()
            command = str(record["command"]).strip()
            if uid in local_uids:
                fail(f"{filename}: duplicate UID {uid}")
            if uid in global_uids:
                fail(f"{filename}: UID collision with {global_uids[uid]}: {uid}")
            if command in local_commands:
                fail(f"{filename}: duplicate command string: {command}")
            local_uids.add(uid)
            local_commands.add(command)
            global_uids[uid] = filename
            if record.get("source_status") != "review_required":
                fail(f"{filename}[{i}]: new content must be marked review_required")
            assessment = record.get("assessment")
            if not isinstance(assessment, dict) or not assessment.get("question_fa") or not assessment.get("answer_key_fa"):
                fail(f"{filename}[{i}]: assessment must contain question_fa and answer_key_fa")
        totals[platform] += len(commands)
        print(f"OK {filename}: {len(commands)} records, {len(local_uids)} unique UIDs")
    # Validate independent examples, scenarios, questions and answer key.
    command_uids = set(global_uids)
    def read_collection(filename: str, key: str, expected: int = 50) -> list:
        path = PACKS / filename
        if not path.is_file():
            fail(f"missing Chapter 68 support file: {filename}")
        try:
            payload = json.loads(path.read_text(encoding="utf-8"))
        except Exception as exc:
            fail(f"{filename}: invalid JSON: {exc}")
        items = payload.get(key)
        if not isinstance(items, list) or len(items) < expected:
            fail(f"{filename}: expected at least {expected} items in {key}")
        return items

    examples = read_collection("ch68_examples.json", "examples")
    scenarios = read_collection("ch68_scenarios.json", "scenarios")
    questions = read_collection("ch68_questions.json", "questions")
    answers = read_collection("ch68_answer_key.json", "answers")
    answer_by_id = {str(a.get("id")): a for a in answers}
    if len(answer_by_id) != len(answers):
        fail("answer key contains duplicate IDs")
    question_by_id = {str(q.get("id")): q for q in questions}
    if len(question_by_id) != len(questions):
        fail("questions contain duplicate IDs")
    if set(question_by_id) != set(answer_by_id):
        fail("question IDs and answer-key IDs do not match exactly")
    for collection_name, items in (("examples", examples), ("scenarios", scenarios), ("questions", questions)):
        ids = [str(item.get("id") or "") for item in items]
        if any(not item_id for item_id in ids) or len(ids) != len(set(ids)):
            fail(f"{collection_name}: missing or duplicate IDs")
        for item in items:
            if item.get("command_uid") not in command_uids:
                fail(f"{collection_name}: unknown command_uid {item.get('command_uid')}")
    for qid, question in question_by_id.items():
        answer = answer_by_id[qid]
        options = question.get("options") or []
        index = answer.get("correct_option_index")
        if not isinstance(index, int) or index < 0 or index >= len(options):
            fail(f"{qid}: correct_option_index is outside the options array")
        if options[index] != answer.get("correct_answer_fa"):
            fail(f"{qid}: answer key does not match the selected option")
        if not answer.get("explanation_fa"):
            fail(f"{qid}: answer key has no explanation")

    # Platform-specific exams and their separate answer keys.
    exam_specs = (
        ("cisco_routing_exam.json", "cisco_routing_exam_answer_key.json", "cisco", 20),
        ("routeros_exam.json", "routeros_exam_answer_key.json", "mikrotik", 20),
        ("powershell_exam.json", "powershell_exam_answer_key.json", "powershell", 20),
        ("cisco_routing_exam_addon_01.json", "cisco_routing_exam_addon_01_answer_key.json", "cisco", 15),
        ("routeros_exam_addon_01.json", "routeros_exam_addon_01_answer_key.json", "mikrotik", 15),
        ("powershell_exam_addon_01.json", "powershell_exam_addon_01_answer_key.json", "powershell", 15),
    )
    exam_counts = {}
    for qfile, afile, vendor, minimum in exam_specs:
        qdata = json.loads((PACKS / qfile).read_text(encoding="utf-8"))
        adata = json.loads((PACKS / afile).read_text(encoding="utf-8"))
        qs = qdata.get("questions")
        ans = adata.get("answers")
        if not isinstance(qs, list) or len(qs) < minimum:
            fail(f"{qfile}: expected at least {minimum} specialized questions")
        if not isinstance(ans, list) or len(ans) != len(qs):
            fail(f"{afile}: answer count must match question count")
        qmap = {str(q.get("id")): q for q in qs}
        amap = {str(a.get("id")): a for a in ans}
        if len(qmap) != len(qs) or set(qmap) != set(amap):
            fail(f"{qfile}/{afile}: duplicate or mismatched IDs")
        for qid, q in qmap.items():
            if q.get("vendor") != vendor or q.get("source_status") != "review_required":
                fail(f"{qfile}:{qid}: wrong vendor or source status")
            if q.get("command_uid") not in command_uids:
                fail(f"{qfile}:{qid}: unknown command_uid")
            options = q.get("options") or []
            if len(options) != 4:
                fail(f"{qfile}:{qid}: expected four options")
            a = amap[qid]
            idx = a.get("correct_option_index")
            if not isinstance(idx, int) or idx < 0 or idx >= len(options):
                fail(f"{afile}:{qid}: invalid correct_option_index")
            if options[idx] != a.get("correct_answer_fa") or not a.get("explanation_fa"):
                fail(f"{afile}:{qid}: answer key does not match option or lacks explanation")
        exam_counts[vendor] = exam_counts.get(vendor, 0) + len(qs)
        print(f"OK {qfile}: questions={len(qs)} answers={len(ans)}")

    source_data = json.loads((PACKS / "ch68_sources.json").read_text(encoding="utf-8"))
    if len(source_data.get("sources") or []) < 5:
        fail("Chapter 68 must have at least five source entries")
    print("CH68 ADDITIVE PACKS VALID")
    print("Command counts:", dict(totals))
    print(f"Examples={len(examples)} scenarios={len(scenarios)} questions={len(questions)} answers={len(answers)} sources={len(source_data['sources'])}")
    if totals["cisco_routing"] != 1600:
        fail(f"Cisco Routing must total exactly 1600 records across the dedicated base/add-on packs; found {totals['cisco_routing']}")
    print(f"Cisco Routing total: {totals['cisco_routing']}/1600 records across 9 JSON files; source review and IOS-XE lab validation remain required.")
    print("Note: structural validation does not replace vendor/version review or real-device labs.")

if __name__ == "__main__":
    main()
