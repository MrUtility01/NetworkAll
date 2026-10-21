"""Regression tests for authentication token transport.

Run from repository root with:
    python -m unittest discover -s server/tests -v
"""
from __future__ import annotations

import sys
import unittest
from pathlib import Path

SERVER_DIR = Path(__file__).resolve().parents[1]
if str(SERVER_DIR) not in sys.path:
    sys.path.insert(0, str(SERVER_DIR))

import app as server_app  # noqa: E402


class TokenTransportTests(unittest.TestCase):
    def test_bearer_header_is_accepted(self):
        with server_app.app.test_request_context(
            "/api/sync/hello",
            headers={"Authorization": "Bearer test-secret"},
        ):
            self.assertEqual(server_app.extract_token(), "test-secret")

    def test_custom_header_is_accepted(self):
        with server_app.app.test_request_context(
            "/api/sync/hello",
            headers={"X-NetEnc-Token": "test-secret"},
        ):
            self.assertEqual(server_app.extract_token(), "test-secret")

    def test_cookie_is_accepted_for_web_session(self):
        with server_app.app.test_request_context(
            "/workspace",
            headers={"Cookie": "netenc_token=test-secret"},
        ):
            self.assertEqual(server_app.extract_token(), "test-secret")

    def test_query_parameter_is_not_an_authentication_source(self):
        with server_app.app.test_request_context(
            "/api/sync/hello?token=test-secret",
        ):
            self.assertEqual(server_app.extract_token(), "")


if __name__ == "__main__":
    unittest.main()
