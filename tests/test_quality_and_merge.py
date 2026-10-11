# -*- coding: utf-8 -*-
"""Regression tests for content merging and assessment checks."""
from __future__ import annotations

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(ROOT / "tools"))

from merge_content_packs_into_android import append_unmatched_as_extra
from audit_content import _item_quality


class ContentMergeTests(unittest.TestCase):
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
