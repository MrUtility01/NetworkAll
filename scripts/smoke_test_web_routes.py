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
            locked_depth = client.get("/api/lessons/1/specialized-depth")
            if locked_depth.status_code != 401:
                raise SystemExit(f"specialty endpoint must require authentication; got {locked_depth.status_code}")
            locked_infographics = client.get("/api/infographics")
            if locked_infographics.status_code != 401:
                raise SystemExit(f"infographics endpoint must require authentication; got {locked_infographics.status_code}")

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

            # Temporary fixture gives this test a stable specialty input without
            # depending on the current wording of a real curriculum lesson.
            fixture = test_db.conn.execute(
                """INSERT INTO lessons(
                    level_id, order_index, title_fa, title_en, tags, summary, full_content
                ) VALUES (?,?,?,?,?,?,?)""",
                (levels[0]["id"], 9999, "MikroTik RouterOS firewall", "MikroTik RouterOS firewall",
                 "L2", "test fixture", "# Test fixture"),
            )
            test_db.conn.commit()
            depth = get_json(f"/api/lessons/{fixture.lastrowid}/specialized-depth")
            if not depth.get("available") or depth.get("specialty") != "mikrotik":
                raise SystemExit("specialty endpoint did not identify MikroTik content")
            if depth.get("review_status") != "review_required":
                raise SystemExit("specialty template is missing the review-required status")
            if not depth.get("extra_full") or not depth.get("extra_commands") or not depth.get("extra_lab"):
                raise SystemExit("specialty endpoint returned an incomplete teaching template")

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
            infographics = get_json("/api/infographics")
            if infographics.get("count") != 100 or len(infographics.get("items", [])) != 100:
                raise SystemExit("compatibility /api/infographics should return all 100 SVG items")
            combined_response = client.get("/static/diagrams/combined_index.json")
            if combined_response.status_code != 200:
                raise SystemExit(f"combined diagram index HTTP {combined_response.status_code}")
            combined = combined_response.get_json()
            if combined.get("count") != 141 or len(combined.get("diagrams", [])) != 141:
                raise SystemExit("combined gallery should contain 100 existing + 41 Chapter 1 diagrams")
            ch1_response = client.get("/static/diagrams/ch01/index.json")
            if ch1_response.status_code != 200:
                raise SystemExit(f"Chapter 1 diagram index HTTP {ch1_response.status_code}")
            ch1_index = ch1_response.get_json()
            if ch1_index.get("count") != 41 or len(ch1_index.get("diagrams", [])) != 41:
                raise SystemExit("Chapter 1 gallery should expose 41 diagrams")
            if not infographics["items"][0].get("svg", "").lstrip().startswith("<svg"):
                raise SystemExit("/api/infographics returned invalid SVG content")

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
                "infographics_compat_api": infographics["count"],
                "combined_gallery_diagrams": combined["count"],
                "chapter_1_diagrams": ch1_index["count"],
                "specialty_depth_review_required": depth["review_status"],
                "destructive_reseed_disabled": True,
            })
        finally:
            test_db.conn.close()


if __name__ == "__main__":
    main()
