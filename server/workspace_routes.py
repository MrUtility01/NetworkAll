# -*- coding: utf-8 -*-
"""Tasks / Notes / Vault — auth required; vault secrets sealed (not plaintext)."""
from __future__ import annotations

import base64
import hashlib
import hmac
import os
import uuid
from datetime import datetime, timezone
from pathlib import Path
import sqlite3

from flask import Blueprint, request, jsonify, render_template, render_template_string, make_response, redirect

bp = Blueprint("workspace", __name__)

_check_token = None
_extract_token = None
_sync_token = ""


def set_auth_checker(check_fn, extract_fn, sync_token: str):
    global _check_token, _extract_token, _sync_token
    _check_token = check_fn
    _extract_token = extract_fn
    _sync_token = sync_token or ""


def _authorized() -> bool:
    if _check_token is None:
        return False
    return bool(_check_token())


def _vault_key() -> bytes:
    """Get a per-user AES key. Windows keys are protected with DPAPI."""
    override = os.environ.get("NETENC_VAULT_KEY", "").strip()
    if override:
        return hashlib.sha256(b"NetworkEncyclopedia-vault-v2:" + override.encode("utf-8")).digest()

    key_path = _db_path().parent / "vault.key"
    if key_path.exists():
        stored = key_path.read_bytes()
        if stored.startswith(b"dpapi1:"):
            try:
                import win32crypt
                result = win32crypt.CryptUnprotectData(base64.b64decode(stored[7:]), None, None, None, 0)
                key = result[-1] if isinstance(result, tuple) else result
                if len(key) != 32:
                    raise ValueError("invalid DPAPI key length")
                return bytes(key)
            except Exception as exc:
                raise RuntimeError("کلید Vault ویندوز با حساب فعلی باز نشد؛ فایل vault.key را حذف نکنید.") from exc
        if stored.startswith(b"key1:"):
            key = base64.b64decode(stored[5:])
            if len(key) == 32:
                return key
        raise RuntimeError("قالب فایل کلید Vault ناشناخته است؛ داده‌ها تغییر داده نشدند.")

    key = os.urandom(32)
    key_path.parent.mkdir(parents=True, exist_ok=True)
    if os.name == "nt":
        try:
            import win32crypt
            protected = win32crypt.CryptProtectData(key, "NetworkEncyclopedia Vault", None, None, None, 0)
            if isinstance(protected, tuple):
                protected = protected[-1]
            key_path.write_bytes(b"dpapi1:" + base64.b64encode(protected))
        except Exception as exc:
            raise RuntimeError("ساخت کلید امن ویندوز ناموفق بود؛ بسته pywin32 را نصب کنید.") from exc
    else:
        key_path.write_bytes(b"key1:" + base64.b64encode(key))
        try:
            os.chmod(key_path, 0o600)
        except OSError:
            pass
    return key


def _seal(plain: str) -> str:
    """Authenticated AES-GCM encryption; never falls back to storing plaintext."""
    if not plain:
        return ""
    if plain.startswith("enc2:"):
        return plain
    try:
        from cryptography.hazmat.primitives.ciphers.aead import AESGCM
        nonce = os.urandom(12)
        aad = b"NetworkEncyclopedia-Workspace-Vault-v2"
        encrypted = AESGCM(_vault_key()).encrypt(nonce, plain.encode("utf-8"), aad)
        return "enc2:" + base64.urlsafe_b64encode(nonce + encrypted).decode("ascii")
    except Exception as exc:
        raise RuntimeError("ذخیره‌سازی امن رمز ناموفق بود؛ مقدار به متن ساده تبدیل نشد.") from exc


def _unseal(blob: str) -> str:
    if not blob:
        return ""
    if blob.startswith("enc2:"):
        try:
            from cryptography.hazmat.primitives.ciphers.aead import AESGCM
            payload = base64.urlsafe_b64decode(blob[5:].encode("ascii"))
            if len(payload) < 29:
                raise ValueError("encrypted data is too short")
            nonce, ciphertext = payload[:12], payload[12:]
            aad = b"NetworkEncyclopedia-Workspace-Vault-v2"
            return AESGCM(_vault_key()).decrypt(nonce, ciphertext, aad).decode("utf-8")
        except Exception:
            return "•••• (رمز قابل رمزگشایی نیست؛ کلید را بررسی کنید)"
    if blob.startswith("enc1:"):
        # One-way migration path for the legacy XOR envelope. Re-seal immediately
        # in workspace_page when this legacy value can be decrypted.
        try:
            key = hashlib.sha256((_sync_token or "dev").encode("utf-8")).digest()
            raw = base64.urlsafe_b64decode(blob[5:].encode("ascii"))
            plain = bytes(b ^ key[i % len(key)] for i, b in enumerate(raw))
            return plain.decode("utf-8")
        except Exception:
            return "•••• (legacy vault record cannot be decrypted)"
    return "•••• (legacy plaintext record is intentionally masked)"


LOGIN_PAGE = """
<!doctype html><html lang=fa dir=rtl><head><meta charset=utf-8>
<meta name=viewport content="width=device-width,initial-scale=1">
<title>ورود فضای کاری</title>
<style>
body{font-family:Tahoma,sans-serif;background:#0f172a;color:#e2e8f0;display:flex;min-height:100vh;align-items:center;justify-content:center}
form{background:#1e293b;padding:24px;border-radius:12px;width:min(360px,92vw)}
input,button{width:100%;padding:10px;margin:8px 0;box-sizing:border-box;font-size:15px;border-radius:8px;border:0}
button{background:#0ea5e9;color:#fff;font-weight:bold}
.err{color:#fca5a5;font-size:13px}
</style></head><body>
<form method=post action="/workspace/login">
<h2>فضای کاری — نیاز به توکن</h2>
<p style="color:#94a3b8;font-size:13px">همان NETENC_TOKEN سرور / توکن Sync اندروید</p>
<input type=password name=token placeholder="توکن" required autofocus>
{% if error %}<p class=err>{{ error }}</p>{% endif %}
<button type=submit>ورود</button>
<p style="font-size:12px;color:#64748b"><a href="/" style="color:#38bdf8">بازگشت</a></p>
</form>
</body></html>
"""

PAGE = """
<!doctype html><html lang=fa dir=rtl><head><meta charset=utf-8>
<meta name=viewport content="width=device-width,initial-scale=1">
<title>فضای کاری</title>
<style>
body{font-family:Tahoma,sans-serif;background:#f7f8fa;margin:0;padding:16px;color:#0f172a}
.card{background:#fff;border-radius:12px;padding:12px;margin:8px 0;box-shadow:0 1px 3px #0001}
input,textarea,button{width:100%;margin:4px 0;padding:10px;box-sizing:border-box;font-size:15px}
button{background:#0ea5e9;color:#fff;border:0;border-radius:8px}
nav a{margin-left:12px;color:#0369a1;text-decoration:none;font-weight:bold}
.badge{font-size:12px;color:#64748b}
</style></head><body>
<nav>
<a href="/">خانه</a>
<a href="/workspace?tab=tasks">کارها</a>
<a href="/workspace?tab=notes">یادداشت</a>
<a href="/workspace?tab=vault">رمزها</a>
<a href="/workspace/logout">خروج</a>
</nav>
<p class="badge">دسترسی با توکن · vault به صورت sealed ذخیره می‌شود</p>
<h2>{{ title }}</h2>
<form method=post>
<input name=title placeholder="عنوان" required>
<textarea name=body rows=4 placeholder="{{ 'رمز (ذخیره sealed)' if tab=='vault' else 'متن' }}"></textarea>
{% if tab=='vault' %}<input name=username placeholder="نام کاربری">{% endif %}
<button type=submit>ذخیره</button>
</form>
{% for it in items %}
<div class=card>
<b>{{ it.title }}</b>
<pre style="white-space:pre-wrap;margin:8px 0">{{ it.body }}</pre>
<form method=post><input type=hidden name=delete value="{{ it.uid }}">
<button type=submit style="background:#ef4444">حذف</button></form>
</div>
{% else %}<p>موردی نیست.</p>{% endfor %}
</body></html>
"""


def _db_path():
    root = Path(__file__).resolve().parent
    for p in (root / "data" / "encyclopedia.db", root / "encyclopedia.db"):
        if p.is_file():
            return p
    p = root / "data" / "encyclopedia.db"
    p.parent.mkdir(parents=True, exist_ok=True)
    return p


def _conn():
    c = sqlite3.connect(str(_db_path()), timeout=10)
    c.row_factory = sqlite3.Row
    c.execute("PRAGMA busy_timeout = 10000")
    c.execute("""CREATE TABLE IF NOT EXISTS ws_tasks(
        uid TEXT PRIMARY KEY, title TEXT NOT NULL, body TEXT DEFAULT '', done INT DEFAULT 0,
        last_updated TEXT, due_at TEXT NOT NULL DEFAULT '', priority INTEGER NOT NULL DEFAULT 1,
        remind_at TEXT NOT NULL DEFAULT '', reminded_at TEXT NOT NULL DEFAULT ''
    )""")
    c.execute("CREATE TABLE IF NOT EXISTS ws_notes(uid TEXT PRIMARY KEY, title TEXT, body TEXT, last_updated TEXT)")
    c.execute("CREATE TABLE IF NOT EXISTS ws_vault(uid TEXT PRIMARY KEY, title TEXT, username TEXT, secret TEXT, last_updated TEXT)")
    # Non-destructive migration for databases made by older versions.
    task_columns = {row["name"] for row in c.execute("PRAGMA table_info(ws_tasks)").fetchall()}
    for name, declaration in (
        ("due_at", "TEXT NOT NULL DEFAULT ''"),
        ("priority", "INTEGER NOT NULL DEFAULT 1"),
        ("remind_at", "TEXT NOT NULL DEFAULT ''"),
        ("reminded_at", "TEXT NOT NULL DEFAULT ''"),
    ):
        if name not in task_columns:
            c.execute(f"ALTER TABLE ws_tasks ADD COLUMN {name} {declaration}")
    c.execute("CREATE INDEX IF NOT EXISTS idx_ws_tasks_due ON ws_tasks(due_at, done)")
    c.execute("CREATE INDEX IF NOT EXISTS idx_ws_tasks_reminder ON ws_tasks(remind_at, reminded_at, done)")
    c.commit()
    return c


def _cookie_ok() -> bool:
    # When no shared token is configured, defer to the server's local-only
    # auth policy. Never let an empty token bypass auth on a remote bind.
    if not _sync_token:
        return bool(_check_token and _check_token())
    cookie = request.cookies.get("netenc_token") or ""
    return hmac.compare_digest(cookie, _sync_token)


@bp.route("/workspace/login", methods=["GET", "POST"])
def workspace_login():
    err = ""
    if request.method == "POST":
        tok = (request.form.get("token") or "").strip()
        if _sync_token and tok == _sync_token:
            resp = make_response(redirect("/workspace"))
            resp.set_cookie("netenc_token", tok, httponly=True, samesite="Lax", max_age=60 * 60 * 12)
            return resp
        if not _sync_token:
            return redirect("/workspace")
        err = "توکن نادرست"
    return render_template_string(LOGIN_PAGE, error=err)


@bp.route("/workspace/logout")
def workspace_logout():
    resp = make_response(redirect("/workspace/login"))
    resp.set_cookie("netenc_token", "", expires=0)
    return resp


@bp.route("/workspace", methods=["GET", "POST"])
def workspace_page():
    if not _authorized() and not _cookie_ok():
        return redirect("/workspace/login")
    tab = request.args.get("tab") or "tasks"
    if tab not in ("tasks", "notes", "vault"):
        tab = "tasks"
    c = _conn()
    if request.method == "POST":
        if request.form.get("delete"):
            uid = request.form["delete"]
            table = {"notes": "ws_notes", "vault": "ws_vault"}.get(tab, "ws_tasks")
            c.execute(f"DELETE FROM {table} WHERE uid=?", (uid,))
            c.commit()
        else:
            title = (request.form.get("title") or "").strip()
            body = request.form.get("body") or ""
            username = request.form.get("username") or ""
            if title:
                uid = str(uuid.uuid4())
                now = datetime.now(timezone.utc).isoformat()
                if tab == "notes":
                    c.execute("INSERT INTO ws_notes VALUES(?,?,?,?)", (uid, title, body, now))
                elif tab == "vault":
                    c.execute("INSERT INTO ws_vault VALUES(?,?,?,?,?)", (uid, title, username, _seal(body), now))
                else:
                    c.execute("INSERT INTO ws_tasks(uid,title,body,done,last_updated) VALUES(?,?,?,?,?)", (uid, title, body, 0, now))
                c.commit()
    if tab == "notes":
        items = c.execute("SELECT uid,title,body FROM ws_notes ORDER BY last_updated DESC").fetchall()
        title = "یادداشت‌ها"
    elif tab == "vault":
        rows = c.execute("SELECT uid,title,username,secret FROM ws_vault ORDER BY title").fetchall()
        items = []
        migrated_any = False
        for r in rows:
            secret_blob = r["secret"] or ""
            if _authorized() or _cookie_ok():
                if secret_blob.startswith("enc1:"):
                    secret_show = _unseal(secret_blob)
                    if not str(secret_show).startswith("••••"):
                        try:
                            secret_blob = _seal(secret_show)
                            c.execute("UPDATE ws_vault SET secret=? WHERE uid=?", (secret_blob, r["uid"]))
                            migrated_any = True
                        except Exception as exc:
                            print("legacy sealed vault migration skipped for", r["uid"], exc)
                elif secret_blob.startswith("enc2:"):
                    secret_show = _unseal(secret_blob)
                else:
                    # Older versions could persist plaintext when encryption failed.
                    # On an authenticated local Vault view, show once and immediately re-seal.
                    secret_show = secret_blob
                    if secret_blob:
                        try:
                            secret_blob = _seal(secret_blob)
                            c.execute("UPDATE ws_vault SET secret=? WHERE uid=?", (secret_blob, r["uid"]))
                            migrated_any = True
                        except Exception as exc:
                            secret_show = "•••• (رمز قدیمی؛ مهاجرت امن ناموفق بود)"
                            print("legacy plaintext vault migration failed for", r["uid"], exc)
            else:
                secret_show = "••••"
            items.append({"uid": r["uid"], "title": r["title"], "body": f"{r['username']}\n{secret_show}"})
        if migrated_any:
            c.commit()
        title = "مدیریت رمز ورود (AES-GCM)"
    else:
        items = c.execute("SELECT uid,title,body FROM ws_tasks ORDER BY last_updated DESC").fetchall()
        title = "مدیریت کارها"
    return render_template_string(PAGE, items=items, title=title, tab=tab)



def _planner_auth_error():
    if _authorized() or _cookie_ok():
        return None
    return jsonify({"ok": False, "error": "unauthorized"}), 401


def _valid_local_datetime(value):
    value = str(value or "").strip()
    if not value:
        return ""
    try:
        # Accept an all-day Jalali-calendar selection (stored as ISO Gregorian date)
        # or a local wall time. Windows compares the latter in the same local zone.
        if len(value) == 10:
            datetime.strptime(value, "%Y-%m-%d")
        else:
            datetime.strptime(value, "%Y-%m-%dT%H:%M")
    except ValueError:
        return None
    return value


@bp.route("/planner")
def planner_page():
    if not _authorized() and not _cookie_ok():
        return redirect("/workspace/login")
    return render_template("planner.html")


@bp.route("/api/planner/tasks", methods=["GET", "POST"])
def planner_tasks():
    denied = _planner_auth_error()
    if denied:
        return denied
    c = _conn()
    if request.method == "GET":
        try:
            limit = max(1, min(1000, int(request.args.get("limit", "1000"))))
        except ValueError:
            c.close()
            return jsonify({"ok": False, "error": "invalid_limit"}), 400
        rows = c.execute(
            """SELECT uid,title,body,done,last_updated,due_at,priority,remind_at
               FROM ws_tasks ORDER BY
                 CASE WHEN due_at='' THEN 1 ELSE 0 END, due_at ASC, priority DESC, last_updated DESC
               LIMIT ?""", (limit,)
        ).fetchall()
        c.close()
        return jsonify({"ok": True, "items": [dict(row) for row in rows]})

    payload = request.get_json(silent=True)
    if not isinstance(payload, dict):
        c.close()
        return jsonify({"ok": False, "error": "JSON object required"}), 400
    title = str(payload.get("title") or "").strip()
    body = str(payload.get("body") or "").strip()
    due_at = _valid_local_datetime(payload.get("due_at"))
    try:
        priority = int(payload.get("priority", 2))
    except (TypeError, ValueError):
        priority = 0
    if not title or len(title) > 200 or len(body) > 5000:
        c.close()
        return jsonify({"ok": False, "error": "title is required (max 200) and body max is 5000"}), 400
    if due_at is None:
        c.close()
        return jsonify({"ok": False, "error": "due_at must be YYYY-MM-DDTHH:MM"}), 400
    if priority not in (1, 2, 3):
        c.close()
        return jsonify({"ok": False, "error": "priority must be 1, 2, or 3"}), 400
    remind_at = due_at if payload.get("reminder") and "T" in due_at else ""
    uid = uuid.uuid4().hex
    now = datetime.now(timezone.utc).isoformat()
    c.execute(
        """INSERT INTO ws_tasks(uid,title,body,done,last_updated,due_at,priority,remind_at,reminded_at)
           VALUES(?,?,?,?,?,?,?,?,?)""",
        (uid, title, body, 0, now, due_at, priority, remind_at, ""),
    )
    c.commit()
    row = c.execute(
        "SELECT uid,title,body,done,last_updated,due_at,priority,remind_at FROM ws_tasks WHERE uid=?",
        (uid,)
    ).fetchone()
    c.close()
    return jsonify({"ok": True, "item": dict(row)}), 201


@bp.route("/api/planner/tasks/<uid>", methods=["PATCH", "DELETE"])
def planner_task_item(uid):
    denied = _planner_auth_error()
    if denied:
        return denied
    if len(uid) > 80:
        return jsonify({"ok": False, "error": "invalid uid"}), 400
    c = _conn()
    existing = c.execute("SELECT uid FROM ws_tasks WHERE uid=?", (uid,)).fetchone()
    if not existing:
        c.close()
        return jsonify({"ok": False, "error": "not_found"}), 404
    if request.method == "DELETE":
        c.execute("DELETE FROM ws_tasks WHERE uid=?", (uid,))
        c.commit()
        c.close()
        return jsonify({"ok": True, "deleted": uid})
    payload = request.get_json(silent=True)
    if not isinstance(payload, dict) or not isinstance(payload.get("done"), bool):
        c.close()
        return jsonify({"ok": False, "error": "JSON boolean field 'done' required"}), 400
    c.execute(
        "UPDATE ws_tasks SET done=?,last_updated=?,reminded_at=CASE WHEN ?=0 THEN '' ELSE reminded_at END WHERE uid=?",
        (1 if payload["done"] else 0, datetime.now(timezone.utc).isoformat(),
         1 if payload["done"] else 0, uid),
    )
    c.commit()
    c.close()
    return jsonify({"ok": True, "uid": uid, "done": payload["done"]})


@bp.route("/api/workspace/export")
def workspace_export():
    if not _authorized():
        return jsonify({"error": "unauthorized"}), 401
    c = _conn()
    vault = []
    for r in c.execute("SELECT * FROM ws_vault").fetchall():
        d = dict(r)
        d["secret"] = _unseal(d.get("secret") or "")
        d["secret_sealed"] = True
        vault.append(d)
    return jsonify({
        "tasks": [dict(r) for r in c.execute("SELECT * FROM ws_tasks").fetchall()],
        "notes": [dict(r) for r in c.execute("SELECT * FROM ws_notes").fetchall()],
        "vault": vault,
    })
