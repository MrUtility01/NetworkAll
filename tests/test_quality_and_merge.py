# -*- coding: utf-8 -*-
"""Regression tests for content merging and assessment checks."""
from __future__ import annotations

import json
import sqlite3
import sys
import tempfile
import unittest
from unittest.mock import patch
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
import app as server_app
import workspace_routes
from core.study import study_sync_apply, study_sync_index, study_sync_pull


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

    def test_duplicate_titles_merge_richer_later_pack_instead_of_dropping_it(self):
        data = {"chapters": []}
        short = "محتوای کوتاه " * 400
        detailed = "# Windows Server Remoting\n\n## Lab\n" + "جزئیات تخصصی قابل راستی‌آزمایی " * 500
        added = append_unmatched_as_extra(data, [
            {"uid": "automation-remoting", "title_fa": "[L2] Remoting", "subchapter_order": 3,
             "lesson_order": 1, "full_content": short, "summary": "نسخه کوتاه"},
            {"uid": "windows-remoting", "title_fa": "[L2] Remoting", "subchapter_order": 3,
             "lesson_order": 2, "full_content": detailed, "summary": "نسخه تخصصی ویندوز"},
        ], 35, "فصل ۳۵", "Windows Server")
        lessons = [lesson for sub in data["chapters"][0]["subchapters"] for lesson in sub["lessons"]]
        self.assertEqual(added, 1)
        self.assertEqual(len(lessons), 1)
        self.assertIn("Windows Server Remoting", lessons[0]["full_content"])
        self.assertIn("نسخه تخصصی ویندوز", lessons[0]["summary"])

    def test_assessment_and_learning_objectives_survive_pack_append(self):
        assessment = {
            "questions": [{"id": "q1", "prompt": "سؤال", "options": ["الف", "ب"]}],
            "answer_key": [{"id": "q1", "correct_index": 1, "explanation": "دلیل"}],
        }
        data = {"chapters": []}
        append_unmatched_as_extra(data, [{
            "uid": "pack-lesson",
            "title_fa": "[L1] درس بسته",
            "subchapter_order": 1,
            "meta": {"assessment": assessment, "keywords": ["lab"]},
            "learning_objectives": ["اجرای آزمایش", "تحلیل خروجی"],
            "source_status": "review_required",
        }], 66, "فصل ۶۶", "Routing")
        lesson = data["chapters"][0]["subchapters"][0]["lessons"][0]
        metadata = json.loads(lesson["meta_json"])
        self.assertEqual(metadata["assessment"], assessment)
        self.assertIn("lab", metadata["keywords"])
        self.assertIn("اجرای آزمایش", lesson["learning_objectives"])
        self.assertEqual(lesson["source_status"], "review_required")

    def test_title_merge_preserves_structured_assessment_metadata(self):
        assessment = {
            "questions": [{"id": "q1", "prompt": "سؤال", "options": ["الف", "ب"]}],
            "answer_key": [{"id": "q1", "correct_index": 0, "explanation": "دلیل"}],
        }
        base = {"full_content": "محتوای پایه"}
        apply_fields(base, {
            "full_content": "شرح تکمیلی",
            "meta": {"assessment": assessment},
            "learning_objectives": ["هدف اول"],
            "source_status": "verified",
        })
        self.assertEqual(json.loads(base["meta_json"])["assessment"], assessment)
        self.assertEqual(base["learning_objectives"], "هدف اول")
        self.assertEqual(base["source_status"], "verified")

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

    def test_automation_python_and_windows_packs_have_distinct_uid_namespaces(self):
        auto_path = ROOT / "tools/packs/automation_python/automation_python_curriculum_pack.json"
        windows_path = ROOT / "tools/packs/windows_server/windows_server_complete_curriculum_pack.json"
        auto = json.loads(auto_path.read_text(encoding="utf-8"))
        windows = json.loads(windows_path.read_text(encoding="utf-8"))
        auto_uids = {item.get("uid") for item in auto.get("lessons", []) if item.get("uid")}
        windows_uids = {item.get("uid") for item in windows.get("lessons", []) if item.get("uid")}
        self.assertFalse(auto_uids & windows_uids, f"duplicate lesson UIDs: {sorted(auto_uids & windows_uids)}")
        self.assertTrue(any("اتوماسیون PowerShell" in item.get("title_fa", "") for item in auto.get("lessons", [])))

    def test_command_pack_assessment_is_preserved_as_structured_metadata(self):
        assessment = {
            "questions": [{"id": "q1", "prompt": "کدام دستور؟", "options": ["الف", "ب"]}],
            "answer_key": [{"id": "q1", "correct_index": 0, "explanation": "دلیل"}],
        }
        pack = {
            "chapter_order": 68,
            "commands": [{
                "command": "show version",
                "title_fa": "نمایش نسخه",
                "level": "L1",
                "assessment": assessment,
                "learning_objectives": ["تفسیر خروجی"],
            }],
        }
        lesson = commands_to_lessons(pack, ROOT / "tools/packs/commands_encyclopedia/cisco_switching.json")[0]
        self.assertEqual(lesson["meta"]["assessment"], assessment)
        self.assertIn("EJ_ASSESSMENT", lesson["notes"])

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


class StudySyncMigrationTests(unittest.TestCase):
    def test_old_study_table_is_migrated_without_losing_progress_and_can_sync(self):
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "legacy-study.sqlite"
            conn = sqlite3.connect(str(path))
            conn.row_factory = sqlite3.Row
            conn.execute(
                """CREATE TABLE study_progress (
                    lesson_uid TEXT PRIMARY KEY, status TEXT DEFAULT 'new',
                    ease REAL DEFAULT 2.5, interval_hours INTEGER DEFAULT 1,
                    last_studied TEXT, next_review TEXT, times_studied INTEGER DEFAULT 0,
                    notes TEXT DEFAULT ''
                )"""
            )
            stamp = "2026-10-10T15:00:00Z"
            conn.execute(
                """INSERT INTO study_progress
                   (lesson_uid,status,ease,interval_hours,last_studied,next_review,times_studied,notes)
                   VALUES(?,?,?,?,?,?,?,?)""",
                ("lesson:legacy", "learning", 2.7, 24, stamp, "2026-10-11T15:00:00Z", 4, "preserve this"),
            )
            conn.commit()

            manifest = study_sync_index(conn)
            item = next(row for row in manifest if row["uid"] == "lesson:legacy")
            self.assertEqual(item["last_updated"], stamp)
            pulled = study_sync_pull(conn, ["lesson:legacy"])
            self.assertEqual(pulled[0]["notes"], "preserve this")
            self.assertEqual(pulled[0]["times_studied"], 4)

            incoming = {
                "uid": "lesson:new-progress", "entity": "study", "status": "known",
                "ease": 2.8, "interval_hours": 72, "last_studied": stamp,
                "next_review": "2026-10-13T15:00:00Z", "times_studied": 3,
                "notes": "synced from Android", "last_updated": "2026-10-12T04:00:00Z",
                "device_id": "android-test", "deleted": False,
            }
            self.assertEqual(study_sync_apply(conn, [incoming]), 1)
            remote = {row["uid"]: row for row in study_sync_pull(conn, ["lesson:new-progress"])}
            self.assertEqual(remote["lesson:new-progress"]["status"], "known")
            self.assertEqual(remote["lesson:new-progress"]["device_id"], "android-test")
            self.assertEqual(remote["lesson:new-progress"]["notes"], "synced from Android")
            conn.close()


class SyncApiContractTests(unittest.TestCase):
    def test_sync_push_persists_tasks_notes_and_tombstones_but_rejects_missing_lessons(self):
        with tempfile.TemporaryDirectory() as td:
            db = WebDB(Path(td) / "sync-api.sqlite")
            stamp = "2026-10-12T04:00:00Z"
            payload = {
                "records": [
                    {"uid": "task-1", "entity": "task", "title": "LAN sync test",
                     "body": "Created on Android", "done": False, "priority": 2,
                     "due_at": "", "last_updated": stamp, "device_id": "android-test"},
                    {"uid": "note-1", "entity": "note", "title": "OSPF notes",
                     "body": "Neighbor state checklist", "tags": "routing",
                     "last_updated": stamp, "device_id": "android-test", "deleted": True},
                    {"uid": "lesson:study-test", "entity": "study", "status": "learning",
                     "ease": 2.5, "interval_hours": 24, "last_studied": stamp,
                     "next_review": "2026-10-13T04:00:00Z", "times_studied": 2,
                     "notes": "Revise OSPF neighbor states", "last_updated": stamp,
                     "device_id": "android-test", "deleted": False},
                    {"uid": "lesson:missing", "entity": "lesson", "title_fa": "درس ناشناخته"},
                    {"uid": "vault-1", "entity": "vault", "title": "must not sync", "secret": "plaintext"},
                    {"uid": "note-invalid", "entity": "note", "title": "   ",
                     "body": "must not be silently dropped", "tags": "routing",
                     "last_updated": stamp, "device_id": "android-test"},
                    {"uid": "lesson:study-invalid", "entity": "study", "status": "corrupted",
                     "ease": 2.5, "interval_hours": 24, "times_studied": 2,
                     "notes": "must be reported", "last_updated": stamp,
                     "device_id": "android-test"},
                ]
            }
            with (
                patch.object(server_app, "db", return_value=db),
                patch.object(server_app, "require_token", return_value=None),
                patch.object(workspace_routes, "_db_path", return_value=db.path),
            ):
                client = server_app.app.test_client()
                response = client.post("/api/sync/push", json=payload)
                self.assertEqual(response.status_code, 200)
                body = response.get_json()
                self.assertEqual(body["accepted"], 3)
                self.assertEqual(body["unsupported"], 1)
                self.assertEqual(body["unsupported_uids"], ["vault-1"])
                self.assertEqual(body["missing_targets"], 1)
                self.assertEqual(body["missing_target_uids"], ["lesson:missing"])
                self.assertEqual(body["invalid"], 2)
                self.assertEqual(body["invalid_uids"], ["note-invalid", "lesson:study-invalid"])
                self.assertEqual(body["apply_rejected"], 0)

                manifest = client.get("/api/sync/manifest").get_json()
                by_uid = {item["uid"]: item for item in manifest["items"]}
                self.assertIn("task-1", by_uid)
                self.assertIn("note-1", by_uid)
                self.assertNotIn("note-invalid", by_uid)
                self.assertTrue(by_uid["note-1"]["deleted"])
                self.assertIn("lesson:study-test", by_uid)
                self.assertEqual(by_uid["lesson:study-test"]["entity"], "study")

                pulled = client.post("/api/sync/pull", json={"uids": ["task-1", "note-1", "lesson:study-test"]}).get_json()
                records = {item["uid"]: item for item in pulled["records"]}
                self.assertEqual(records["task-1"]["title"], "LAN sync test")
                self.assertEqual(records["task-1"]["device_id"], "android-test")
                self.assertTrue(records["note-1"]["deleted"])
                self.assertNotIn("secret", records["note-1"])
                self.assertEqual(records["lesson:study-test"]["times_studied"], 2)
                self.assertEqual(records["lesson:study-test"]["notes"], "Revise OSPF neighbor states")
            db.conn.close()


    def test_sync_push_does_not_claim_success_when_storage_rejects_existing_lesson(self):
        with tempfile.TemporaryDirectory() as td:
            db = WebDB(Path(td) / "sync-reject.sqlite")
            chapter_id = db.conn.execute(
                "INSERT INTO chapters(order_index, title_fa, title_en) VALUES(1, ?, ?)",
                ("آزمایشی", "Test"),
            ).lastrowid
            level_id = db.conn.execute(
                "INSERT INTO levels(chapter_id, order_index, title_fa, title_en) VALUES(?, 1, ?, ?)",
                (chapter_id, "بخش آزمایشی", "Test level"),
            ).lastrowid
            db.conn.execute(
                "INSERT INTO lessons(level_id, order_index, title_fa, last_updated) VALUES(?, 1, ?, ?)",
                (level_id, "درس آزمایشی", "2026-10-11T00:00:00Z"),
            )
            db.conn.commit()
            db.ensure_sync_columns()
            uid = db.conn.execute("SELECT uid FROM lessons LIMIT 1").fetchone()["uid"]
            payload = {
                "records": [{
                    "uid": uid, "entity": "lesson", "title_fa": "درس ویرایش‌شده",
                    "full_content": "متن درس", "last_updated": "2026-10-12T00:00:00Z",
                    "device_id": "android-test",
                }]
            }
            original_apply = db.sync_apply
            self.assertEqual(original_apply(payload["records"]), 1)

            # Simulate a race where the target disappears between index and apply.
            db.conn.execute("UPDATE lessons SET last_updated=? WHERE uid=?", ("2026-10-11T00:00:00Z", uid))
            db.conn.commit()
            db.sync_apply = lambda records: 0
            try:
                with (
                    patch.object(server_app, "db", return_value=db),
                    patch.object(server_app, "require_token", return_value=None),
                ):
                    response = server_app.app.test_client().post("/api/sync/push", json=payload)
                    body = response.get_json()
                    self.assertEqual(response.status_code, 200)
                    self.assertEqual(body["accepted"], 0)
                    self.assertEqual(body["apply_rejected"], 1)
            finally:
                db.conn.close()


if __name__ == "__main__":
    unittest.main()
