# -*- coding: utf-8 -*-
"""Regression tests for content merging and assessment checks."""
from __future__ import annotations

import sqlite3
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "server"))
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(ROOT / "tools"))
sys.path.insert(0, str(ROOT / "shared"))

from merge_content_packs_into_android import append_unmatched_as_extra, apply_fields, commands_to_lessons, git_markdown_to_lessons
from sync_engine import compare_lww, content_hash, merge_push
from audit_content import _item_quality
from core.db import WebDB
from core.deep_fallback import build_deep_fallback


class DeepFallbackTests(unittest.TestCase):
    def test_hardware_fallback_uses_hardware_specific_lab_and_answer_key(self):
        lesson = build_deep_fallback("[L1] CPU چیست و چگونه کار می‌کند", "CPU fundamentals")
        content = lesson["full_content"]
        self.assertIn("RAM میز کار است", content)
        self.assertIn("خودآزمایی و پاسخ‌نامه", content)
        self.assertIn("Answer Key", content)
        self.assertNotIn("VLAN / VRF", content)
        self.assertIn("SMART", content)
        self.assertIn("منابع رسمی و مراجع", content)
        self.assertIn("Intel Product Support", content)

    def test_python_fallback_has_python_specific_troubleshooting(self):
        lesson = build_deep_fallback("[L2] Python exception handling", "Python exception handling")
        content = lesson["full_content"]
        self.assertIn("unit test", content)
        self.assertIn("Answer Key", content)
        self.assertIn("ورودی نامعتبر", content)
        self.assertNotIn("لایه ۲ (VLAN", content)
        self.assertIn("Python official documentation", content)

    def test_general_fallback_does_not_inject_network_only_lab(self):
        lesson = build_deep_fallback("[L2] Technical documentation workflow", "Documentation workflow")
        combined = "\\n".join(str(lesson.get(key) or "") for key in ("full_content", "commands", "examples", "notes"))
        self.assertIn("معیار قبولی", combined)
        self.assertIn("حالت مرزی", combined)
        self.assertNotIn("show ip interface brief", combined)
        self.assertNotIn("VLAN / VRF", combined)
        self.assertNotIn("کابل uplink", combined)

    def test_fallback_assessment_has_separate_matching_answer_key(self):
        lesson = build_deep_fallback("[L2] Git merge conflict", "Git merge conflict")
        assessment = lesson["assessment"]
        question_ids = {q["id"] for q in assessment["questions"]}
        answer_ids = {a["id"] for a in assessment["answer_key"]}
        self.assertGreaterEqual(len(assessment["questions"]), 2)
        self.assertEqual(question_ids, answer_ids)
        quality = _item_quality({
            "title_fa": "[L2] Git merge conflict",
            "full_content": lesson["full_content"],
            "assessment": assessment,
        })
        self.assertTrue(quality["has_questions"])
        self.assertTrue(quality["has_answer_key"])
        self.assertTrue(quality["answer_key_ids_match"])


class ContentMergeTests(unittest.TestCase):
    def test_pack_merge_does_not_overwrite_longer_base_lesson(self):
        base = {
            "full_content": "BASE_DEEP_CONTENT " * 400,
            "examples": "Baseline lab and expected result.",
            "commands": "show baseline",
        }
        incoming = {
            "full_content": "## Lab تخصصی\nScenario: یک رخداد واقعی\nExpected result: سرویس سالم بماند.",
            "examples": "Scenario-specific lab steps.",
            "commands": "show topic-specific-status",
        }
        apply_fields(base, incoming)
        self.assertIn("BASE_DEEP_CONTENT", base["full_content"])
        self.assertIn("Scenario: یک رخداد واقعی", base["full_content"])
        self.assertIn("Baseline lab", base["examples"])
        self.assertIn("Scenario-specific lab steps", base["examples"])
        self.assertIn("show baseline", base["commands"])
        self.assertIn("show topic-specific-status", base["commands"])

    def test_append_preserves_base_chapter_and_existing_lesson(self):
        data = {
            "chapters": [{
                "order": 66,
                "title_fa": "فصل ۶۶",
                "subchapters": [{
                    "title_fa": "محتوای پایه",
                    "lessons": [{"uid": "base-1", "title_fa": "[L0] مبانی مسیریابی"}],
                }],
            }]
        }
        added = [
            {"uid": "base-1", "title_fa": "[L0] مبانی مسیریابی", "subchapter_order": 1},
            {"uid": "route-1", "title_fa": "[L2] OSPF عملی", "subchapter_order": 1, "lesson_order": 1,
             "full_content": "شرح آموزش", "meta": {}},
        ]
        appended = append_unmatched_as_extra(data, added, 66, "فصل ۶۶", "Routing Deep")
        self.assertEqual(appended, 1)
        self.assertEqual(len(data["chapters"]), 1)
        chapter = data["chapters"][0]
        self.assertEqual(chapter["subchapters"][0]["lessons"][0]["uid"], "base-1")
        all_lessons = [lesson for sub in chapter["subchapters"] for lesson in sub["lessons"]]
        self.assertEqual(sum(x["uid"] == "base-1" for x in all_lessons), 1)
        self.assertEqual(sum(x["uid"] == "route-1" for x in all_lessons), 1)

    def test_creates_chapter_if_missing(self):
        data = {"chapters": []}
        appended = append_unmatched_as_extra(
            data, [{"uid": "new-1", "title_fa": "دستور جدید", "subchapter_order": 1}],
            68, "فصل ۶۸", "Commands",
        )
        self.assertEqual(appended, 1)
        self.assertEqual([c["order"] for c in data["chapters"]], [68])

    def test_unrelated_lesson_with_colliding_uid_is_preserved(self):
        data = {"chapters": [{"order": 68, "title_fa": "دستورات", "subchapters": [
            {"title_fa": "زیرفصل", "lessons": [{"uid": "collision", "title_fa": "دستور اول"}]}
        ]}]}
        added = append_unmatched_as_extra(
            data, [{"uid": "collision", "title_fa": "دستور دوم", "subchapter_order": 1, "full_content": "شرح"}],
            68, "فصل ۶۸", "Commands",
        )
        self.assertEqual(added, 1)
        lessons = [lesson for sub in data["chapters"][0]["subchapters"] for lesson in sub["lessons"]]
        self.assertEqual(len(lessons), 2)
        self.assertNotEqual(lessons[0]["uid"], lessons[1]["uid"])

    def test_command_ids_are_namespaced_by_source_pack(self):
        pack = {"chapter_order": 68, "commands": [{"command": "show version", "title_fa": "نمایش نسخه", "level": "L1"}]}
        first = commands_to_lessons(pack, ROOT / "tools/packs/commands_encyclopedia/cisco_switching.json")
        second = commands_to_lessons(pack, ROOT / "tools/packs/routing_deep/chapter_68_cisco_routing_1600.json")
        self.assertNotEqual(first[0]["uid"], second[0]["uid"])

    def test_git_markdown_book_splits_into_level_lessons(self):
        markdown = """# فصل ۶۴
## ۶۴.۱ مبانی و راه‌اندازی
### Git و GitHub — L0
## ۱. مدل ذهنی
متن مقدماتی.
## ۴. سناریوی عملی
سناریوی آزمایشی.
## ۶. آزمایشگاه
آزمایش محلی.
### Git و GitHub — L1
## ۱. مدل ذهنی
متن پیشرفته.
"""
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "Git_Chapter_64_Full.md"
            path.write_text(markdown, encoding="utf-8")
            lessons = git_markdown_to_lessons(path)
        self.assertEqual(len(lessons), 2)
        self.assertEqual(lessons[0]["chapter_order"], 64)
        self.assertEqual(lessons[0]["subchapter_order"], 1)
        self.assertIn("سناریوی عملی", lessons[0]["examples"])

    def test_sync_compares_timezone_offsets_by_instant(self):
        server_record = {"uid": "x", "last_updated": "2026-10-11T12:00:00Z", "title": "same"}
        client_record = {"uid": "x", "last_updated": "2026-10-11T15:30:00+03:30", "title": "same"}
        server_record["content_hash"] = content_hash(server_record)
        client_record["content_hash"] = content_hash(client_record)
        self.assertEqual(compare_lww(server_record, client_record), "equal")

    def test_sync_merge_does_not_mutate_incoming_record(self):
        incoming = {"uid": "new", "last_updated": "2026-10-11T12:00:00Z", "title": "lesson"}
        applied, _, _ = merge_push({}, [incoming])
        self.assertNotIn("content_hash", incoming)
        self.assertIn("content_hash", applied[0])

    def test_fts_search_finds_english_terms_and_falls_back_cleanly(self):
        with tempfile.TemporaryDirectory() as td:
            db = WebDB(Path(td) / "search.sqlite")
            chapter_id = db.conn.execute(
                "INSERT INTO chapters(order_index, title_fa, title_en) VALUES(1, ?, ?)",
                ("مسیریابی", "Routing"),
            ).lastrowid
            level_id = db.conn.execute(
                "INSERT INTO levels(chapter_id, order_index, title_fa, title_en) VALUES(?, 1, ?, ?)",
                (chapter_id, "مبتدی", "Beginner"),
            ).lastrowid
            db.conn.execute(
                """INSERT INTO lessons(level_id, order_index, title_fa, title_en, tags, summary, full_content, commands, examples)
                   VALUES(?, 1, ?, ?, ?, ?, ?, ?, ?)""",
                (level_id, "مسیریابی BGP", "BGP routing", "BGP", "neighbor", "BGP establishes routing adjacencies.", "show ip bgp summary", "Verify neighbor state."),
            )
            db.conn.commit()
            rows = db.search("BGP")
            self.assertTrue(any("BGP" in str(row.get("title_fa", "")) for row in rows))
            db.conn.close()

    def test_database_backup_is_consistent_and_readable(self):
        with tempfile.TemporaryDirectory() as td:
            db = WebDB(Path(td) / "source.sqlite")
            db.conn.execute(
                "INSERT INTO chapters(order_index, title_fa, title_en) VALUES(1, ?, ?)",
                ("فصل آزمایشی", "Test chapter"),
            )
            db.conn.commit()
            backup = db.backup(Path(td) / "backups")
            self.assertTrue(backup.is_file())
            with sqlite3.connect(str(backup)) as copied:
                count = copied.execute("SELECT COUNT(*) FROM chapters").fetchone()[0]
            self.assertEqual(count, 1)
            db.conn.close()

    def test_assessment_requires_matching_separate_answer_key(self):
        result = _item_quality({
            "title_fa": "آزمون نمونه",
            "full_content": "این یک مثال و Lab برای راستی‌آزمایی و امنیت است.",
            "assessment": {
                "questions": [{"id": "q1", "prompt": "؟", "options": ["الف", "ب"]}],
                "answer_key": [{"id": "q2", "correct_index": 0}],
            },
        })
        self.assertTrue(result["has_questions"])
        self.assertTrue(result["has_answer_key"])
        self.assertFalse(result["answer_key_ids_match"])


if __name__ == "__main__":
    unittest.main()
