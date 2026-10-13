#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Exercise browser-facing web routes using a temporary SQLite database."""
from __future__ import annotations

import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "server"))

import app as server_app  # noqa: E402
from core.db import WebDB  # noqa: E402


def main() -> None:
    with tempfile.TemporaryDirectory(prefix="networkall-web-routes-") as td:
        test_db = WebDB(Path(td) / "web-test.db")
        try:
            seeded = test_db.seed_full(force=True)
            if seeded.get("curriculum_source") != "shared-android-curriculum":
                raise SystemExit(f"test DB did not seed shared curriculum: {seeded}")
            server_app.db = lambda: test_db
            server_app.app.config.update(TESTING=True)

            # Verify first-run setup, correct-password login, and rejection of
            # an incorrect password without touching the real server/data files.
            server_app._app_password_path = lambda: Path(td) / "app_access.json"
            login_client = server_app.app.test_client()
            locked_home = login_client.get("/")
            if locked_home.status_code not in (301, 302) or "/login" not in locked_home.headers.get("Location", ""):
                raise SystemExit(f"unlocked web home should redirect to first-run login, got {locked_home.status_code}")
            setup = login_client.get("/login")
            if setup.status_code != 200 or "تأیید رمز" not in setup.get_data(as_text=True):
                raise SystemExit("first-run local web password setup screen is missing")
            first_login = login_client.post("/login", data={
                "next": "/", "password": "engineerjokar", "confirmation": "engineerjokar"
            }, follow_redirects=False)
            if first_login.status_code not in (301, 302):
                raise SystemExit(f"first-run password setup failed: HTTP {first_login.status_code}")
            if not server_app._app_password_path().is_file():
                raise SystemExit("local password hash file was not created")
            if "engineerjokar" in server_app._app_password_path().read_text(encoding="utf-8"):
                raise SystemExit("local password was stored in plaintext")
            wrong_client = server_app.app.test_client()
            wrong_login = wrong_client.post("/login", data={
                "next": "/", "password": "incorrect-password"
            })
            if wrong_login.status_code != 200 or "رمز نادرست" not in wrong_login.get_data(as_text=True):
                raise SystemExit("incorrect local password was not rejected")
            correct_client = server_app.app.test_client()
            correct_login = correct_client.post("/login", data={
                "next": "/", "password": "engineerjokar"
            }, follow_redirects=False)
            if correct_login.status_code not in (301, 302):
                raise SystemExit("correct local password was not accepted")

            client = server_app.app.test_client()

            locked = client.get("/api/chapters")
            if locked.status_code != 401:
                raise SystemExit(f"expected locked browser API to return 401; got {locked.status_code}")

            with client.session_transaction() as sess:
                sess["networkall_unlocked"] = True

            checks = {}
            def get_json(path):
                response = client.get(path)
                if response.status_code != 200:
                    raise SystemExit(f"{path}: HTTP {response.status_code}: {response.get_data(as_text=True)[:240]}")
                try:
                    return response.get_json()
                except Exception as exc:
                    raise SystemExit(f"{path}: expected JSON: {exc}")

            stats = get_json("/api/stats")
            checks["stats"] = stats.get("chapters") == 68 and stats.get("lessons") == seeded.get("lessons")

            chapters = get_json("/api/chapters")
            if len(chapters) != 68:
                raise SystemExit(f"browser chapter count mismatch: {len(chapters)}")
            ch = next((x for x in chapters if int(x["order_index"]) == 1), None)
            if not ch:
                raise SystemExit("chapter 1 missing from web tree")
            levels = get_json(f"/api/chapters/{ch['id']}/levels")
            if not levels:
                raise SystemExit("chapter 1 has no levels")
            lessons = get_json(f"/api/levels/{levels[0]['id']}/lessons")
            if not lessons:
                raise SystemExit("web level route returns no lessons")
            full = get_json(f"/api/lessons/{lessons[0]['id']}")
            if not full.get("title_fa"):
                raise SystemExit("web lesson detail route returned an untitled item")
            scenarios = get_json("/api/scenarios")
            if scenarios:
                detail = get_json(f"/api/scenarios/{scenarios[0]['id']}")
                if not detail.get("title_fa"):
                    raise SystemExit("web scenario detail route returned an untitled item")
            search = get_json("/api/search?q=IP")
            if not isinstance(search, list):
                raise SystemExit("web search should return a JSON array")

            gallery = client.get("/diagrams")
            if gallery.status_code != 200:
                raise SystemExit(f"/diagrams returned HTTP {gallery.status_code}")
            diagram_index = client.get("/static/diagrams/index.json")
            if diagram_index.status_code != 200:
                raise SystemExit(f"web diagram index returned HTTP {diagram_index.status_code}")
            index = diagram_index.get_json()
            if index.get("count") != 100 or len(index.get("diagrams", [])) != 100:
                raise SystemExit("Windows web diagram index does not contain 100 items")

            disabled = client.post("/api/reseed")
            if disabled.status_code != 404:
                raise SystemExit("destructive /api/reseed endpoint should not be exposed")

            print({
                "ok": True,
                "seed": seeded,
                "web_stats": stats,
                "chapters": len(chapters),
                "chapter_1_levels": len(levels),
                "first_level_lessons": len(lessons),
                "scenarios": len(scenarios),
                "search_results": len(search),
                "web_diagrams": index["count"],
                "destructive_reseed_disabled": True,
            })
        finally:
            test_db.conn.close()


if __name__ == "__main__":
    main()
