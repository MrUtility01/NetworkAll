from __future__ import annotations

import unittest

from shared.sync_engine import compare_lww, content_hash, merge_push


class SyncTimestampTests(unittest.TestCase):
    def test_fractional_timestamp_is_compared_as_instant(self):
        server = {"uid": "x", "last_updated": "2026-10-11T20:00:01Z", "title": "same"}
        client = {"uid": "x", "last_updated": "2026-10-11T20:00:01.500Z", "title": "same"}
        server["content_hash"] = content_hash(server)
        client["content_hash"] = content_hash(client)
        self.assertEqual(compare_lww(server, client), "accept_client")

    def test_timezone_offsets_are_normalized(self):
        server = {"uid": "x", "last_updated": "2026-10-11T23:00:00+03:00", "title": "same"}
        client = {"uid": "x", "last_updated": "2026-10-11T20:00:00Z", "title": "same"}
        server["content_hash"] = content_hash(server)
        client["content_hash"] = content_hash(client)
        self.assertEqual(compare_lww(server, client), "equal")

    def test_malformed_timestamp_does_not_win_silently(self):
        server = {"uid": "x", "last_updated": "not-a-date", "content_hash": "a"}
        client = {"uid": "x", "last_updated": "2026-10-11T20:00:00Z", "content_hash": "b"}
        self.assertEqual(compare_lww(server, client), "conflict")

    def test_merge_push_does_not_mutate_callers_records(self):
        client = {"uid": "new", "entity": "note", "last_updated": "2026-10-11T20:00:00Z", "title": "N"}
        applied, rejected, conflicts = merge_push({}, [client])
        self.assertEqual(len(applied), 1)
        self.assertEqual(rejected, [])
        self.assertEqual(conflicts, [])
        self.assertNotIn("content_hash", client)
        self.assertIn("content_hash", applied[0])


if __name__ == "__main__":
    unittest.main()
