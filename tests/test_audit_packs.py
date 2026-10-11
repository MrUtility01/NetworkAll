from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from tools.audit_packs import audit_file, run


class PackAuditTests(unittest.TestCase):
    def write_pack(self, root: Path, rel: str, payload: dict) -> Path:
        path = root / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(payload, ensure_ascii=False), encoding="utf-8")
        return path

    def test_audits_lesson_features_and_length(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            path = self.write_pack(root, "tools/packs/sample.json", {
                "package_schema_version": 1,
                "lessons": [{
                    "uid": "lesson:ch01:lv001:l0001",
                    "title_fa": "نمونه درس",
                    "title_en": "Sample lesson",
                    "summary": "خلاصه",
                    "full_content": (
                        "## آموزش از صفر\n" + ("مفهوم فنی با جزئیات و مثال واقعی. " * 70)
                        + "\n## Lab\nمراحل اجرا و خروجی مورد انتظار.\n"
                    ),
                    "commands": "show version",
                    "assessment": {
                        "questions": [{"id": "q1", "prompt": "پرسش"}],
                        "answer_key": [{"id": "q1", "correct_index": 0}],
                    },
                }],
            })
            report = audit_file(path, root)
            self.assertEqual(report["records"], 1)
            self.assertEqual(report["uid_missing"], 0)
            self.assertEqual(report["deep_ge_2000"], 1)
            self.assertEqual(report["coverage"]["has_lab"], 1)
            self.assertEqual(report["coverage"]["has_answer_key"], 1)
            self.assertEqual(report["structural_errors"], [])

    def test_duplicate_uids_inside_pack_are_structural_error(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            path = self.write_pack(root, "tools/packs/sample.json", {
                "lessons": [
                    {"uid": "same", "title_fa": "الف", "full_content": "متن اول"},
                    {"uid": "same", "title_fa": "ب", "full_content": "متن دوم"},
                ],
            })
            report = audit_file(path, root)
            self.assertIn("duplicate_uids_within_pack", report["structural_errors"])

    def test_cross_pack_uid_collision_is_reported(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            payload = {"lessons": [{"uid": "same", "title_fa": "درس", "full_content": "متن"}]}
            self.write_pack(root, "tools/packs/a.json", payload)
            self.write_pack(root, "tools/legacy/b.json", payload)
            report = run(root)
            self.assertEqual(report["summary"]["packs_scanned"], 2)
            self.assertEqual(report["summary"]["cross_pack_duplicate_uids"], 1)

    def test_empty_pack_is_flagged(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            path = self.write_pack(root, "tools/packs/empty.json", {"lessons": []})
            report = audit_file(path, root)
            self.assertIn("no_records_found", report["structural_errors"])


if __name__ == "__main__":
    unittest.main()
