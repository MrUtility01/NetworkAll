# -*- coding: utf-8 -*-
"""Regression tests for non-destructive content merge and searchable local DB."""
from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "server"))
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(ROOT / "shared"))

from core.db import WebDB
from merge_content_packs_into_android import append_unmatched_as_extra, commands_to_lessons, git_markdown_to_lessons
from sync_engine import compare_lww, content_hash, merge_push
from workspace_routes import _jalali_to_gregorian, _jalali_label


class ContentMergeTests(unittest.TestCase):
    def test_existing_chapter_and_lessons_are_preserved(self):
        data = {
            "chapters": [{
                "order": 66,
                "title_fa": "فصل ۶۶ قدیمی",
                "title_en": "Existing",
                "subchapters": [{
                    "title_fa": "محتوای قبلی",
                    "lessons": [{"uid": "old-uid", "title_fa": "درس قدیمی", "full_content": "متن"}],
                }],
            }]
        }
        added = append_unmatched_as_extra(
            data,
            [{"uid": "new-uid", "title_fa": "درس تازه", "subchapter_order": 2, "full_content": "شرح"}],
            66, "فصل جدید", "New",
        )
        self.assertEqual(added, 1)
        chapter = next(c for c in data["chapters"] if c["order"] == 66)
        all_uids = [l["uid"] for sub in chapter["subchapters"] for l in sub["lessons"]]
        self.assertIn("old-uid", all_uids)
        self.assertIn("new-uid", all_uids)
        self.assertEqual(len([c for c in data["chapters"] if c["order"] == 66]), 1)

    def test_duplicate_title_is_not_added_under_a_new_uid(self):
        data = {
            "chapters": [{
                "order": 64,
                "title_fa": "Git",
                "subchapters": [{"title_fa": "زیرفصل 1", "lessons": [{"uid": "old", "title_fa": "[L0] Git basics", "full_content": "rich"}]}],
            }]
        }
        added = append_unmatched_as_extra(
            data, [{"uid": "new", "title_fa": "[L0] Git basics", "full_content": "other"}],
            64, "Git", "Git",
        )
        self.assertEqual(added, 0)

    def test_command_uid_is_namespaced_by_source_pack(self):
        data = {"chapter_order": 68, "commands": [{"command": "show version", "title_fa": "نمایش نسخه", "level": "L1"}]}
        a = commands_to_lessons(data, ROOT / "tools/packs/commands_encyclopedia/cisco_switching.json")
        b = commands_to_lessons(data, ROOT / "tools/packs/routing_deep/chapter_68_cisco_routing_1600.json")
        self.assertNotEqual(a[0]["uid"], b[0]["uid"])

    def test_git_markdown_is_split_into_lesson_records(self):
        markdown = """# فصل ۶۴
## ۶۴.۱ مبانی و راه‌اندازی
### Git و GitHub — L0
## ۱. تعریف و مدل ذهنی
مفهوم Git.
## ۴. سناریوی عملی
تمرین مجاز.
## ۶. آزمایشگاه
آزمایش محلی.
### Git و GitHub — L1
## ۱. تعریف و مدل ذهنی
مفهوم پیشرفته‌تر.
## ۴. سناریوی عملی
تمرین دوم.
"""
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "Git_Chapter_64_Full.md"
            path.write_text(markdown, encoding="utf-8")
            lessons = git_markdown_to_lessons(path)
        self.assertEqual(len(lessons), 2)
        self.assertEqual(lessons[0]["chapter_order"], 64)
        self.assertEqual(lessons[0]["subchapter_order"], 1)
        self.assertIn("سناریوی عملی", lessons[0]["examples"])

    def test_duplicate_uid_is_not_added_twice(self):
        data = {
            "chapters": [{
                "order": 68,
                "title_fa": "دستورات",
                "subchapters": [{"title_fa": "زیرفصل 1", "lessons": [{"uid": "same", "title_fa": "اصل"}]}],
            }]
        }
        added = append_unmatched_as_extra(
            data, [{"uid": "same", "title_fa": "تکراری", "subchapter_order": 1}],
            68, "دستورات", "Commands",
        )
        self.assertEqual(added, 0)
        chapter = data["chapters"][0]
        self.assertEqual(sum(len(s["lessons"]) for s in chapter["subchapters"]), 1)


class SyncEngineTests(unittest.TestCase):
    def test_timestamps_compare_by_instant_not_timezone_text(self):
        server_record = {"uid": "x", "last_updated": "2026-10-11T12:00:00Z", "title": "same"}
        client_record = {"uid": "x", "last_updated": "2026-10-11T15:30:00+03:30", "title": "same"}
        server_record["content_hash"] = content_hash(server_record)
        client_record["content_hash"] = content_hash(client_record)
        self.assertEqual(compare_lww(server_record, client_record), "equal")

    def test_merge_does_not_mutate_input_record(self):
        incoming = {"uid": "new", "last_updated": "2026-10-11T12:00:00Z", "title": "lesson"}
        applied, _, _ = merge_push({}, [incoming])
        self.assertNotIn("content_hash", incoming)
        self.assertIn("content_hash", applied[0])


class JalaliCalendarTests(unittest.TestCase):
    def test_known_jalali_date_round_trip(self):
        self.assertEqual(str(_jalali_to_gregorian(1405, 7, 19)), "2026-10-11")
        self.assertTrue(_jalali_label("2026-10-11T12:00:00").startswith("1405/07/19"))


class SearchTests(unittest.TestCase):
    def test_persian_and_english_search(self):
        with tempfile.TemporaryDirectory() as td:
            db = WebDB(Path(td) / "test.db")
            try:
                cur = db.conn.cursor()
                cur.execute("INSERT INTO chapters(order_index,title_fa,title_en) VALUES (1,'شبکه','Network')")
                ch_id = cur.lastrowid
                cur.execute("INSERT INTO levels(chapter_id,order_index,title_fa,title_en) VALUES (?,?,?,?)", (ch_id,1,'مقدماتی','Basics'))
                lv_id = cur.lastrowid
                cur.execute(
                    "INSERT INTO lessons(level_id,order_index,title_fa,title_en,tags,summary,full_content) VALUES (?,?,?,?,?,?,?)",
                    (lv_id,1,'Subnetting و IPv4','Subnetting IPv4','ip,cidr','تقسیم شبکه','آموزش CIDR و ماسک شبکه'),
                )
                db.conn.commit()
                self.assertTrue(db.search("Subnetting"))
                self.assertTrue(db.search("ماسک"))
            finally:
                db.conn.close()


if __name__ == "__main__":
    unittest.main()
