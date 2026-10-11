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

from core.db import WebDB
from merge_content_packs_into_android import append_unmatched_as_extra


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
