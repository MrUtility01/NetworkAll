# -*- coding: utf-8 -*-
"""سرور وب + API همگام‌سازی LAN — قرارداد یکسان با اندروید (فاز ۱ و ۲)."""
from __future__ import annotations

import base64
import hashlib
import json
import os
import socket
import secrets
from datetime import datetime, timezone, timedelta
from pathlib import Path

from flask import Flask, jsonify, redirect, render_template, render_template_string, request, session

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


def load_web_session_secret() -> str:
    """Persist a random secret so sessions survive a normal server restart."""
    p = BASE / "data" / "web_session.key"
    p.parent.mkdir(parents=True, exist_ok=True)
    try:
        current = p.read_text(encoding="utf-8").strip()
        if len(current) >= 48:
            return current
    except OSError:
        pass
    value = secrets.token_urlsafe(48)
    p.write_text(value + "\n", encoding="utf-8")
    try:
        os.chmod(p, 0o600)
    except OSError:
        pass
    return value


app.secret_key = load_web_session_secret()
app.config.update(
    JSON_AS_ASCII=False,
    SESSION_COOKIE_HTTPONLY=True,
    SESSION_COOKIE_SAMESITE="Lax",
    SESSION_COOKIE_SECURE=os.environ.get("NETENC_HTTPS", "0") == "1",
)
app.permanent_session_lifetime = timedelta(hours=12)


def _app_password_path() -> Path:
    return BASE / "data" / "app_access.json"


def _load_app_password():
    p = _app_password_path()
    if not p.exists():
        return None
    try:
        data = json.loads(p.read_text(encoding="utf-8"))
        if not isinstance(data, dict) or not data.get("salt") or not data.get("hash"):
            return {}
        return data
    except Exception:
        return {}


def _save_app_password(password: str) -> None:
    p = _app_password_path()
    p.parent.mkdir(parents=True, exist_ok=True)
    salt = secrets.token_bytes(16)
    iterations = 240_000
    digest = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, iterations, dklen=32)
    data = {
        "algorithm": "PBKDF2-HMAC-SHA256",
        "iterations": iterations,
        "salt": base64.b64encode(salt).decode("ascii"),
        "hash": base64.b64encode(digest).decode("ascii"),
        "created_at": utc_now(),
    }
    temp = p.with_suffix(".json.tmp")
    temp.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    try:
        os.chmod(temp, 0o600)
    except OSError:
        pass
    temp.replace(p)


def _verify_app_password(password: str) -> bool:
    record = _load_app_password()
    if not record:
        return False
    try:
        salt = base64.b64decode(record["salt"], validate=True)
        expected = base64.b64decode(record["hash"], validate=True)
        iterations = int(record.get("iterations", 240_000))
        if len(salt) < 16 or len(expected) != 32 or not 100_000 <= iterations <= 2_000_000:
            return False
        actual = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, iterations, dklen=32)
        return secrets.compare_digest(actual, expected)
    except Exception:
        return False


_LOGIN_TEMPLATE = r'''<!doctype html>
<html lang="fa" dir="rtl">
<head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>ورود | NetworkAll</title>
<style>
body{font-family:Tahoma,Arial,sans-serif;background:#f3f6fb;color:#172033;display:grid;place-items:center;min-height:100vh;margin:0}
main{background:#fff;border:1px solid #dde5f0;border-radius:16px;padding:28px;width:min(430px,calc(100% - 36px));box-sizing:border-box;box-shadow:0 16px 44px #0f172a12}
h1{color:#1d4ed8;margin:0 0 8px;font-size:26px}p{line-height:1.9;color:#475569;font-size:14px}
label{display:block;margin:14px 0 6px}input{box-sizing:border-box;width:100%;padding:12px;border:1px solid #cbd5e1;border-radius:8px;font:inherit;direction:ltr}
button{margin-top:18px;width:100%;padding:12px;border:0;border-radius:8px;background:#1d4ed8;color:white;font:inherit;cursor:pointer}
.error{color:#b91c1c}small{display:block;color:#64748b;line-height:1.8;margin-top:16px}
</style></head>
<body><main>
<h1>NetworkAll</h1>
{% if setup_mode %}<p>برای اولین اجرا، رمز محلی ویندوز را بسازید. می‌توانید همان رمزی را وارد کنید که روی اندروید انتخاب می‌کنید.</p>
{% else %}<p>برای دسترسی به دانشنامه، رمز محلی را وارد کنید.</p>{% endif %}
{% if error %}<p class="error">{{ error }}</p>{% endif %}
<form method="post" action="/login">
<input type="hidden" name="next" value="{{ next_path }}">
<label for="password">{% if setup_mode %}رمز جدید (حداقل ۸ نویسه){% else %}رمز ورود{% endif %}</label>
<input id="password" name="password" type="password" autocomplete="{% if setup_mode %}new-password{% else %}current-password{% endif %}" minlength="{% if setup_mode %}8{% else %}1{% endif %}" required>
{% if setup_mode %}<label for="confirmation">تأیید رمز</label><input id="confirmation" name="confirmation" type="password" autocomplete="new-password" minlength="8" required>{% endif %}
<button type="submit">{% if setup_mode %}ثبت رمز و ورود{% else %}ورود{% endif %}</button>
</form>
<small>این قفل دسترسی رابط وب را محدود می‌کند؛ جایگزین HTTPS، توکن API، فایروال یا رمزگذاری دیتابیس نیست. برای میزبان LAN فقط شبکهٔ خصوصی و مورداعتماد را مجاز کنید.</small>
</main></body></html>'''


@app.before_request
def require_web_unlock():
    path = request.path
    if (
        path == "/login"
        or path == "/api/health"
        or path == "/api/sync/hello"
        or path.startswith("/api/sync/")
        or path.startswith("/workspace/")
        or path == "/api/workspace/export"
        or path.startswith("/static/")
    ):
        return None
    if session.get("networkall_unlocked") is True:
        return None
    if path.startswith("/api/"):
        return jsonify({"ok": False, "error": "app_locked", "login_url": "/login"}), 401
    return redirect("/login?next=" + path)


@app.route("/login", methods=["GET", "POST"])
def login():
    record = _load_app_password()
    setup_mode = record is None
    error = ""
    next_path = request.args.get("next", "/")
    if request.method == "POST":
        next_path = request.form.get("next", "/")
        if not next_path.startswith("/") or next_path.startswith("//") or chr(92) in next_path:
            next_path = "/"
        password = request.form.get("password", "")
        if setup_mode:
            confirmation = request.form.get("confirmation", "")
            if len(password) < 8:
                error = "رمز باید دست‌کم ۸ نویسه داشته باشد."
            elif password != confirmation:
                error = "دو رمز یکسان نیستند."
            else:
                _save_app_password(password)
                session.clear()
                session["networkall_unlocked"] = True
                session.permanent = True
                return redirect(next_path)
        elif _verify_app_password(password):
            session.clear()
            session["networkall_unlocked"] = True
            session.permanent = True
            return redirect(next_path)
        else:
            error = "رمز نادرست است یا فایل تنظیم رمز قابل خواندن نیست."
    return render_template_string(
        _LOGIN_TEMPLATE,
        setup_mode=setup_mode,
        error=error,
        next_path=next_path,
    )


@app.get("/logout")
def logout():
    session.clear()
    return redirect("/login")


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
    # The authenticated Windows browser session may use the web-learning API.
    # Android/other clients must still present the per-install API token.
    if session.get("networkall_unlocked") is True:
        return None
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


@app.get("/api/stats")
def api_stats():
    denied = require_token()
    if denied:
        return denied
    return jsonify(db().stats())


@app.get("/api/chapters")
def chapters():
    denied = require_token()
    if denied:
        return denied
    return jsonify(db().list_chapters())


@app.get("/api/chapters/<int:chapter_id>/levels")
def chapter_levels(chapter_id: int):
    denied = require_token()
    if denied:
        return denied
    return jsonify(db().list_levels(chapter_id))


@app.get("/api/levels/<int:level_id>/lessons")
def level_lessons(level_id: int):
    denied = require_token()
    if denied:
        return denied
    return jsonify(db().list_lessons(level_id))


@app.get("/api/lessons/<int:lesson_id>")
def lesson_by_id(lesson_id: int):
    denied = require_token()
    if denied:
        return denied
    result = db().get_lesson(lesson_id)
    if result is None:
        return jsonify({"error": "not found"}), 404
    return jsonify(result)


@app.get("/api/lessons/<int:lesson_id>/specialized-depth")
def lesson_specialized_depth(lesson_id: int):
    """Return optional, read-only specialty templates without mutating/syncing lesson content."""
    denied = require_token()
    if denied:
        return denied
    result = db().get_lesson(lesson_id)
    if result is None:
        return jsonify({"error": "not found"}), 404

    from core.specialized_depth import detect_specialty, specialized_block

    title_fa = str(result.get("title_fa") or "")
    title_en = str(result.get("title_en") or "")
    raw_level = str(result.get("tags") or "L2").strip().upper()
    level = raw_level if raw_level in {"L0", "L1", "L2", "L3", "L4"} else "L2"
    specialty = detect_specialty(title_fa, title_en)
    block = specialized_block(title_fa, title_en, level)
    available = bool(specialty and any(str(value or "").strip() for value in block.values()))
    return jsonify({
        "ok": True,
        "available": available,
        "specialty": specialty,
        "review_status": "review_required" if available else "not_applicable",
        "notice_fa": (
            "این بخش یک الگوی تکمیلی تولیدشده بر اساس حوزهٔ فناوری است؛ قبل از استفاده عملی، "
            "دستورات و نسخهٔ محصول را با مستندات رسمی بررسی کنید. این پاسخ در پایگاه داده ذخیره نمی‌شود."
            if available else ""
        ),
        "topic_fa": title_fa,
        **block,
    })


@app.get("/api/infographics")
def api_infographics():
    """Compatibility API backed by the shared Android/Windows SVG diagram index."""
    denied = require_token()
    if denied:
        return denied
    index_path = Path(app.static_folder) / "diagrams" / "index.json"
    try:
        payload = json.loads(index_path.read_text(encoding="utf-8"))
    except Exception as exc:
        return jsonify({"error": "diagram_index_unavailable", "detail": str(exc), "items": [], "count": 0}), 503

    items = []
    for row in payload.get("diagrams", []):
        asset = str(row.get("asset") or "")
        # Whitelist the generated asset naming scheme; never accept arbitrary paths.
        if not (asset.startswith("diagram_") and len(asset) == 15 and
                asset[8:11].isdigit() and asset.endswith(".svg")):
            continue
        svg_path = index_path.parent / asset
        if not svg_path.is_file():
            continue
        items.append({
            "title": str(row.get("title_fa") or row.get("collection") or row.get("id") or "NetworkAll"),
            "svg": svg_path.read_text(encoding="utf-8"),
        })
    return jsonify({"items": items, "count": len(items)})


@app.get("/api/scenarios")
def scenarios_list():
    denied = require_token()
    if denied:
        return denied
    return jsonify(db().list_scenarios())


@app.get("/api/scenarios/<int:scenario_id>")
def scenario_detail(scenario_id: int):
    denied = require_token()
    if denied:
        return denied
    result = db().get_scenario(scenario_id)
    if result is None:
        return jsonify({"error": "not found"}), 404
    return jsonify(result)


@app.get("/api/search")
def search_lessons():
    denied = require_token()
    if denied:
        return denied
    query = (request.args.get("q") or "").strip()
    return jsonify(db().search(query, limit=100))


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
