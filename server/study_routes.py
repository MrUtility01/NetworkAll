# -*- coding: utf-8 -*-
"""API مطالعه — به app.py وصل می‌شود."""
from __future__ import annotations

from flask import jsonify, request

from core.study import due_reviews, ensure_study_table, mark_study, study_stats


def register_study_routes(app, get_db, require_auth):
    @app.route("/api/study/stats")
    def api_study_stats():
        denied = require_auth()
        if denied:
            return denied
        d = get_db()
        ensure_study_table(d.conn)
        return jsonify(study_stats(d.conn))

    @app.route("/api/study/due")
    def api_study_due():
        denied = require_auth()
        if denied:
            return denied
        try:
            limit = int(request.args.get("limit", 50))
        except (TypeError, ValueError):
            return jsonify({"error": "limit must be an integer"}), 400
        limit = max(1, min(limit, 200))
        d = get_db()
        return jsonify({"items": due_reviews(d.conn, limit)})

    @app.route("/api/study/mark", methods=["POST"])
    def api_study_mark():
        denied = require_auth()
        if denied:
            return denied
        body = request.get_json(force=True, silent=True) or {}
        uid = body.get("uid") or body.get("lesson_uid")
        action = body.get("action") or "studied"
        if not uid:
            return jsonify({"error": "uid required"}), 400
        if action not in {"again", "forgot", "hard", "good", "studied", "easy"}:
            return jsonify({"error": "unsupported study action"}), 400
        d = get_db()
        return jsonify(mark_study(d.conn, str(uid), action))

    @app.route("/api/export")
    def api_export():
        """خروجی JSON سبک برای بکاپ Git/Drive؛ فقط با توکن مجاز."""
        denied = require_auth()
        if denied:
            return denied
        d = get_db()
        chapters = d.list_chapters()
        lessons = []
        for ch in chapters:
            for lv in d.list_levels(ch["id"]):
                for les in d.list_lessons(lv["id"]):
                    full = d.get_lesson(les["id"]) or {}
                    lessons.append({
                        "id": les["id"],
                        "title_fa": les.get("title_fa"),
                        "tags": les.get("tags"),
                        "summary": full.get("summary"),
                        "chapter_id": ch["id"],
                        "level_id": lv["id"],
                    })
        return jsonify({
            "app": "EngineerJokar-NetEnc",
            "chapters": len(chapters),
            "lessons": lessons[:5000],
            "study": study_stats(d.conn),
        })
