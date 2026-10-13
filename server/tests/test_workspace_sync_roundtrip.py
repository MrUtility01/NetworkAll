"""Round-trip regression tests for cross-platform task/note sync.

Run from the repository root:
    python -m unittest discover -s server/tests -v

The tests use a temporary SQLite database and never touch the user's real data.
"""
from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

SERVER_DIR = Path(__file__).resolve().parents[1]
if str(SERVER_DIR) not in sys.path:
    sys.path.insert(0, str(SERVER_DIR))

import workspace_routes  # noqa: E402


class WorkspaceSyncRoundTripTests(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.db_path = Path(self.temp_dir.name) / "test.db"
        self.path_patcher = patch.object(workspace_routes, "_db_path", return_value=self.db_path)
        self.path_patcher.start()
        # Initialize the isolated schema.
        conn = workspace_routes._conn()
        conn.close()

    def tearDown(self):
        self.path_patcher.stop()
        self.temp_dir.cleanup()

    def test_task_create_update_and_pull_round_trip(self):
        task = {
            "uid": "task-001",
            "entity": "task",
            "title": "آزمایش اتصال",
            "body": "از گوشی به سرور و برعکس",
            "done": False,
            "due_at": "2026-10-15T10:00:00Z",
            "priority": 2,
            "remind_at": "2026-10-15T09:45:00Z",
            "last_updated": "2026-10-12T10:00:00Z",
            "device_id": "android-test",
            "deleted": False,
        }
        self.assertEqual(workspace_routes.sync_apply([task]), 1)
        pulled = workspace_routes.sync_pull(["task-001"])
        self.assertEqual(len(pulled), 1)
        self.assertEqual(pulled[0]["entity"], "task")
        self.assertEqual(pulled[0]["title"], "آزمایش اتصال")
        self.assertEqual(pulled[0]["priority"], 2)
        self.assertEqual(pulled[0]["remind_at"], "2026-10-15T09:45:00Z")

        task["title"] = "آزمایش اتصال اصلاح‌شده"
        task["last_updated"] = "2026-10-12T10:05:00Z"
        self.assertEqual(workspace_routes.sync_apply([task]), 1)
        pulled = workspace_routes.sync_pull(["task-001"])
        self.assertEqual(pulled[0]["title"], "آزمایش اتصال اصلاح‌شده")
        self.assertEqual(len([r for r in workspace_routes.sync_index() if r["uid"] == "task-001"]), 1)

    def test_note_tombstone_survives_manifest_and_pull(self):
        note = {
            "uid": "note-001",
            "entity": "note",
            "title": "یادداشت شبکه",
            "body": "VLAN و trunk",
            "tags": "network,vlan",
            "last_updated": "2026-10-12T11:00:00Z",
            "device_id": "windows-test",
            "deleted": False,
        }
        self.assertEqual(workspace_routes.sync_apply([note]), 1)
        note["deleted"] = True
        note["last_updated"] = "2026-10-12T11:10:00Z"
        self.assertEqual(workspace_routes.sync_apply([note]), 1)

        manifest_item = next(r for r in workspace_routes.sync_index() if r["uid"] == "note-001")
        self.assertTrue(manifest_item["deleted"])
        pulled = workspace_routes.sync_pull(["note-001"])
        self.assertEqual(len(pulled), 1)
        self.assertTrue(pulled[0]["deleted"])
        self.assertEqual(pulled[0]["body"], "VLAN و trunk")

    def test_repeated_push_is_idempotent_by_uid(self):
        note = {
            "uid": "note-repeat",
            "entity": "note",
            "title": "تکرار امن",
            "body": "اجرای دوباره نباید رکورد جدید بسازد",
            "last_updated": "2026-10-12T12:00:00Z",
        }
        self.assertEqual(workspace_routes.sync_apply([note, note]), 2)
        conn = workspace_routes._conn()
        try:
            count = conn.execute(
                "SELECT COUNT(*) FROM ws_notes WHERE uid=?", ("note-repeat",)
            ).fetchone()[0]
        finally:
            conn.close()
        self.assertEqual(count, 1)

    def test_vault_is_never_in_workspace_sync_manifest_or_pull(self):
        conn = workspace_routes._conn()
        try:
            conn.execute(
                "INSERT INTO ws_vault(uid,title,username,secret,last_updated) VALUES(?,?,?,?,?)",
                ("vault-001", "نمونه", "user", "enc2:sealed", "2026-10-12T12:00:00Z"),
            )
            conn.commit()
        finally:
            conn.close()
        self.assertNotIn("vault-001", [r["uid"] for r in workspace_routes.sync_index()])
        self.assertEqual(workspace_routes.sync_pull(["vault-001"]), [])


if __name__ == "__main__":
    unittest.main()
