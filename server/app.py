# -*- coding: utf-8 -*-
"""سرور وب + API همگام‌سازی LAN — قرارداد یکسان با اندروید (فاز ۱ و ۲)."""
from __future__ import annotations

import hashlib
import json
import os
import socket
import secrets
from datetime import datetime, timezone
from pathlib import Path

from flask import Flask, jsonify, render_template, request

from core.db import WebDB

try:
    from shared.sync_engine import SCHEMA_VERSION, build_manifest, compare_lww, content_hash, utc_now
except Exception:
    SCHEMA_VERSION = 1

    def utc_now():
        return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")

    def content_hash(payload):
        keys = sorted(k for k in payload.keys() if k not in ("device_id", "last_updated", "content_hash"))
        blob = json.dumps({k: payload[k] for k in keys}, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
        return hashlib.sha256(blob.encode("utf-8")).hexdigest()

    def compare_lww(server, client):
        su, cu = server.get("last_updated") or "", client.get("last_updated") or ""
        sh, ch = server.get("content_hash") or "", client.get("content_hash") or content_hash(client)
        if cu > su:
            return "accept_client"
        if cu < su:
            return "keep_server"
        if sh == ch:
            return "equal"
        return "conflict"

    def build_manifest(records, since=None):
        items = []
        for r in records:
            if since and (r.get("last_updated") or "") <= since:
                continue
            items.append({
                "uid": r["uid"], "entity": r.get("entity", "lesson"),
                "last_updated": r.get("last_updated"), "content_hash": r.get("content_hash"),
                "deleted": bool(r.get("deleted")),
            })
        return {"schema_version": SCHEMA_VERSION, "generated_at": utc_now(), "items": items}


BASE = Path(__file__).resolve().parent
app = Flask(__name__, template_folder=str(BASE / "templates"), static_folder=str(BASE / "static"))
app.config["JSON_AS_ASCII"] = False

_MODULE_STATUS = {"workspace": False, "study": False, "workspace_error": "", "study_error": ""}

try:
    from workspace_routes import bp as workspace_bp, set_auth_checker
    app.register_blueprint(workspace_bp)
    _MODULE_STATUS["workspace"] = True
except Exception as _e:
    _MODULE_STATUS["workspace_error"] = str(_e)
    print("workspace routes skipped", _e)

try:
    from study_routes import register_study_routes
except Exception as _e:
    register_study_routes = None
    _MODULE_STATUS["study_error"] = str(_e)

def load_or_create_sync_token() -> str:
    """Use an explicit environment secret or a private, per-install token file."""
    configured = os.environ.get("NETENC_TOKEN", "").strip()
    if configured:
        return configured
    token_file = BASE / "data" / "networkall.token"
    token_file.parent.mkdir(parents=True, exist_ok=True)
    try:
        current = token_file.read_text(encoding="utf-8").strip()
        if len(current) >= 32:
            return current
    except OSError:
        pass
    token = secrets.token_urlsafe(32)
    token_file.write_text(token + "\n", encoding="utf-8")
    try:
        os.chmod(token_file, 0o600)
    except OSError:
        pass
    print(f"Generated per-install sync token. Copy it from: {token_file}")
    return token


SYNC_TOKEN = load_or_create_sync_token()
DEVICE_ID = os.environ.get("NETENC_DEVICE", socket.gethostname() or "windows-host")
# Safe default for manual/local launches. windows/start.bat opts into LAN binding.
BIND_HOST = os.environ.get("NETENC_HOST", "127.0.0.1")

_db = None


def db() -> WebDB:
    global _db
    if _db is None:
        _db = WebDB()
        if not _db.is_seeded():
            print("seed curriculum...")
            print(_db.seed_full(force=True))
        _db.ensure_sync_columns()
    return _db


def extract_token() -> str:
    auth = request.headers.get("Authorization", "")
    if auth.startswith("Bearer "):
        return auth[7:].strip()
    t = request.headers.get("X-NetEnc-Token", "") or ""
    if t:
        return t.strip()
    # Never accept secrets in URLs: they leak into browser history and access logs.
    return (request.cookies.get("netenc_token") or "").strip()


def check_token() -> bool:
    return bool(SYNC_TOKEN) and extract_token() == SYNC_TOKEN


def require_token():
    if check_token():
        return None
    return jsonify({"ok": False, "error": "unauthorized", "hint": "Authorization: Bearer <NETENC_TOKEN>"}), 401


if _MODULE_STATUS["workspace"]:
    try:
        set_auth_checker(check_token, extract_token, SYNC_TOKEN)
    except Exception as e:
        print("workspace auth wire", e)


@app.get("/")
def index():
    return render_template("index.html")

@app.get("/diagrams")
def diagrams_gallery():
    # SVGs are generated into server/static/diagrams by the shared content build.
    return render_template("diagrams.html")


@app.get("/api/health")
def health():
    st = {}
    try:
        st = db().stats()
    except Exception as e:
        st = {"error": str(e)}
    return jsonify({
        "ok": True,
        "device": DEVICE_ID,
        "schema_version": SCHEMA_VERSION,
        "sync_protocol": "v1-aligned",
        "token_required": bool(SYNC_TOKEN),
        "token_source": "environment" if os.environ.get("NETENC_TOKEN", "").strip() else "per-install-file",
        "modules": {
            "workspace": _MODULE_STATUS["workspace"],
            "study": bool(register_study_routes),
            "workspace_error": _MODULE_STATUS.get("workspace_error") or None,
            "study_error": _MODULE_STATUS.get("study_error") or None,
        },
        "stats": st,
    })


@app.get("/api/chapters")
def chapters():
    denied = require_token()
    if denied:
        return denied
    return jsonify(db().list_chapters())


@app.get("/api/lessons")
def lessons():
    denied = require_token()
    if denied:
        return denied
    level_id = request.args.get("level_id") or request.args.get("chapter_id")
    try:
        lid = int(level_id) if level_id else None
    except ValueError:
        lid = None
    if lid is None:
        return jsonify([])
    return jsonify(db().list_lessons(lid))


@app.get("/api/lesson/<uid>")
def lesson(uid: str):
    denied = require_token()
    if denied:
        return denied
    rows = db().sync_pull([uid])
    if rows:
        return jsonify(rows[0])
    try:
        row = db().get_lesson(int(uid))
        if row:
            return jsonify(row)
    except Exception:
        pass
    return jsonify({"error": "not found"}), 404


@app.get("/api/sync/hello")
def sync_hello():
    denied = require_token()
    if denied:
        return denied
    st = {}
    try:
        st = db().stats()
    except Exception:
        pass
    lan = ""
    try:
        lan = socket.gethostbyname(socket.gethostname())
    except Exception:
        pass
    return jsonify({
        "ok": True,
        "schema_version": SCHEMA_VERSION,
        "device_id": DEVICE_ID,
        "lan_ip": lan,
        "stats": st,
        "protocol": {
            "hello": "GET /api/sync/hello",
            "manifest": "GET /api/sync/manifest?since=",
            "pull": "POST /api/sync/pull {uids:[]}",
            "push": "POST /api/sync/push {records:[]}",
            "auth": "Authorization: Bearer <token> or X-NetEnc-Token",
        },
    })


@app.get("/api/sync/manifest")
def sync_manifest():
    denied = require_token()
    if denied:
        return denied
    since = request.args.get("since") or None
    records = db().sync_index()
    return jsonify(build_manifest(records, since=since))


@app.post("/api/sync/pull")
def sync_pull():
    denied = require_token()
    if denied:
        return denied
    body = request.get_json(force=True, silent=True) or {}
    uids = body.get("uids") or []
    if not isinstance(uids, list):
        return jsonify({"error": "uids must be a list"}), 400
    records = db().sync_pull(uids)
    return jsonify({"records": records, "count": len(records), "generated_at": utc_now()})


@app.post("/api/sync/push")
def sync_push():
    denied = require_token()
    if denied:
        return denied
    body = request.get_json(force=True, silent=True) or {}
    records = body.get("records") or body.get("items") or []
    if not isinstance(records, list):
        return jsonify({"error": "records must be a list"}), 400
    accepted = kept = conflicts = 0
    conflict_uids = []
    index = {r["uid"]: r for r in db().sync_index()}
    to_apply = []
    for item in records:
        uid = (item or {}).get("uid") or ""
        if not uid:
            kept += 1
            continue
        server = index.get(uid)
        if not server:
            to_apply.append(item)
            accepted += 1
            continue
        decision = compare_lww(server, item)
        if decision == "accept_client":
            to_apply.append(item)
            accepted += 1
        elif decision == "conflict":
            conflicts += 1
            conflict_uids.append(uid)
            kept += 1
        else:
            kept += 1
    if to_apply:
        db().sync_apply(to_apply)
    return jsonify({
        "accepted": accepted,
        "kept": kept,
        "conflicts": conflicts,
        "conflict_uids": conflict_uids,
        "server_time": utc_now(),
    })


def main():
    host = BIND_HOST
    port = int(os.environ.get("NETENC_PORT", os.environ.get("PORT", "86")))
    db()
    if register_study_routes:
        try:
            register_study_routes(app, db)
            _MODULE_STATUS["study"] = True
        except Exception as e:
            _MODULE_STATUS["study_error"] = str(e)
            print("study routes", e)
    print(f"NetworkAll listening on http://{host}:{port}")
    print("  sync: /api/sync/hello | manifest | pull | push")
    token_source = "environment" if os.environ.get("NETENC_TOKEN", "").strip() else "per-install-file"
    print(f"  token_required={bool(SYNC_TOKEN)} token_source={token_source}")
    app.run(host=host, port=port, debug=False)


if __name__ == "__main__":
    main()
