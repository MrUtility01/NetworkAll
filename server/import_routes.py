# -*- coding: utf-8 -*-
"""
API وارد کردن بسته محتوای کاربر (NACP)

POST   /api/import/pack          ← آپلود فایل .nacp یا .zip
GET    /api/import/packs         ← فهرست بسته‌های واردشده
DELETE /api/import/packs/<id>    ← حذف ثبت بسته
POST   /api/import/validate      ← فقط اعتبارسنجی بدون وارد کردن
"""
from __future__ import annotations

import tempfile
from pathlib import Path

from flask import Blueprint, jsonify, request

from core.import_pack import PackImporter, PackValidationError

bp = Blueprint("import_pack", __name__)

_db_getter = None
_auth_checker = None


def init_import_routes(app, db_getter, require_token_fn):
    """ثبت blueprint و اتصال به db و احراز هویت."""
    global _db_getter, _auth_checker
    _db_getter = db_getter
    _auth_checker = require_token_fn
    app.register_blueprint(bp)


def _denied():
    if _auth_checker:
        return _auth_checker()
    return None


def _db():
    return _db_getter()


@bp.post("/api/import/pack")
def import_pack():
    """آپلود و وارد کردن بسته .nacp / .zip"""
    denied = _denied()
    if denied:
        return denied

    if "file" not in request.files and "pack" not in request.files:
        return jsonify({"ok": False, "error": "فایل ارسال نشده. فیلد file یا pack را بفرستید."}), 400

    f = request.files.get("file") or request.files.get("pack")
    if not f or not f.filename:
        return jsonify({"ok": False, "error": "فایل خالی است."}), 400

    filename = f.filename.lower()
    if not (filename.endswith(".nacp") or filename.endswith(".zip")):
        return jsonify({"ok": False, "error": "فقط فایل .nacp یا .zip پذیرفته می‌شود."}), 400

    tmp = None
    try:
        tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".nacp")
        f.save(tmp.name)
        tmp.close()

        importer = PackImporter(_db())
        validated = importer.validate_zip(Path(tmp.name))
        result = importer.import_validated(validated)
        return jsonify(result)
    except PackValidationError as e:
        return jsonify({"ok": False, "error": e.message, "details": e.details}), 400
    except Exception as e:
        return jsonify({"ok": False, "error": str(e)}), 500
    finally:
        if tmp:
            try:
                Path(tmp.name).unlink(missing_ok=True)
            except Exception:
                pass


@bp.post("/api/import/validate")
def validate_pack():
    """فقط اعتبارسنجی بسته بدون وارد کردن."""
    denied = _denied()
    if denied:
        return denied

    if "file" not in request.files and "pack" not in request.files:
        return jsonify({"ok": False, "error": "فایل ارسال نشده."}), 400

    f = request.files.get("file") or request.files.get("pack")
    if not f or not f.filename:
        return jsonify({"ok": False, "error": "فایل خالی است."}), 400

    tmp = None
    try:
        tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".nacp")
        f.save(tmp.name)
        tmp.close()

        importer = PackImporter(_db())
        validated = importer.validate_zip(Path(tmp.name))
        manifest = validated["manifest"]
        return jsonify({
            "ok": True,
            "valid": True,
            "pack_id": manifest.get("pack_id"),
            "title_fa": manifest.get("title_fa"),
            "target_chapter_mode": manifest.get("target_chapter_mode"),
            "target_chapter_order": manifest.get("target_chapter_order"),
            "counts": manifest.get("counts") or {},
            "size_bytes": validated.get("size_bytes"),
        })
    except PackValidationError as e:
        return jsonify({"ok": False, "valid": False, "error": e.message, "details": e.details}), 400
    except Exception as e:
        return jsonify({"ok": False, "error": str(e)}), 500
    finally:
        if tmp:
            try:
                Path(tmp.name).unlink(missing_ok=True)
            except Exception:
                pass


@bp.get("/api/import/packs")
def list_packs():
    denied = _denied()
    if denied:
        return denied
    try:
        importer = PackImporter(_db())
        packs = importer.list_imported_packs()
        return jsonify({"ok": True, "packs": packs, "count": len(packs)})
    except Exception as e:
        return jsonify({"ok": False, "error": str(e)}), 500


@bp.delete("/api/import/packs/<pack_id>")
def delete_pack(pack_id: str):
    denied = _denied()
    if denied:
        return denied
    try:
        importer = PackImporter(_db())
        result = importer.delete_pack(pack_id)
        status = 200 if result.get("ok") else 404
        return jsonify(result), status
    except Exception as e:
        return jsonify({"ok": False, "error": str(e)}), 500
