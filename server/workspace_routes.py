# -*- coding: utf-8 -*-
"""Tasks / Notes / Vault — auth required; vault secrets sealed (not plaintext)."""
from __future__ import annotations

import base64
import hashlib
import hmac
import uuid
from datetime import datetime, timezone
from pathlib import Path
import sqlite3

from flask import Blueprint, request, jsonify, render_template_string, make_response, redirect

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


def _seal(plain: str) -> str:
    if not plain:
        return ""
    if plain.startswith("enc1:"):
        return plain
    key = hashlib.sha256((_sync_token or "dev").encode("utf-8")).digest()
    raw = plain.encode("utf-8")
    out = bytes(b ^ key[i % len(key)] for i, b in enumerate(raw))
    return "enc1:" + base64.urlsafe_b64encode(out).decode("ascii")


def _unseal(blob: str) -> str:
    if not blob:
        return ""
    if not blob.startswith("enc1:"):
        return "•••• (legacy — edit to re-seal)"
    try:
        key = hashlib.sha256((_sync_token or "dev").encode("utf-8")).digest()
        raw = base64.urlsafe_b64decode(blob[5:].encode("ascii"))
        out = bytes(b ^ key[i % len(key)] for i, b in enumerate(raw))
        return out.decode("utf-8")
    except Exception:
        return "••••"


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
{% if tab=='tasks' %}
<label>موعد (در رابط به تقویم شمسی نمایش داده می‌شود)</label>
<input type=datetime-local name=due_at>
<label>اولویت</label>
<select name=priority><option value=1>عادی</option><option value=2>مهم</option><option value=3>بالا</option><option value=4>فوری</option></select>
<label>تکرار</label>
<select name=recurrence><option value=none>یک‌باره</option><option value=daily>روزانه</option><option value=weekly>هفتگی</option></select>
{% endif %}
{% if tab=='vault' %}<input name=username placeholder="نام کاربری">{% endif %}
<button type=submit>ذخیره</button>
</form>
{% for it in items %}
<div class=card>
<b>{{ '✓ ' if tab=='tasks' and it.done else '' }}{{ it.title }}</b>
<pre style="white-space:pre-wrap;margin:8px 0">{{ it.body }}</pre>
{% if tab=='tasks' %}
<form method=post><input type=hidden name=toggle value="{{ it.uid }}">
<button type=submit>{{ 'بازگرداندن به کارهای باز' if it.done else 'علامت‌گذاری به‌عنوان انجام‌شده' }}</button></form>
{% endif %}
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
    c = sqlite3.connect(str(_db_path()))
    c.row_factory = sqlite3.Row
    c.execute("""CREATE TABLE IF NOT EXISTS ws_tasks(
        uid TEXT PRIMARY KEY, title TEXT, body TEXT, done INT DEFAULT 0,
        due_at TEXT DEFAULT '', priority INTEGER DEFAULT 1,
        reminder_at TEXT DEFAULT '', recurrence TEXT DEFAULT 'none', last_notified_at TEXT DEFAULT '', last_updated TEXT
    )""")
    # Safe additive migration for databases created by older app versions.
    columns = {row["name"] for row in c.execute("PRAGMA table_info(ws_tasks)").fetchall()}
    for name, definition in (
        ("due_at", "TEXT DEFAULT ''"),
        ("priority", "INTEGER DEFAULT 1"),
        ("reminder_at", "TEXT DEFAULT ''"),
        ("recurrence", "TEXT DEFAULT 'none'"),
        ("last_notified_at", "TEXT DEFAULT ''"),
    ):
        if name not in columns:
            c.execute(f"ALTER TABLE ws_tasks ADD COLUMN {name} {definition}")
    c.execute("CREATE TABLE IF NOT EXISTS ws_notes(uid TEXT PRIMARY KEY, title TEXT, body TEXT, last_updated TEXT)")
    c.execute("CREATE TABLE IF NOT EXISTS ws_vault(uid TEXT PRIMARY KEY, title TEXT, username TEXT, secret TEXT, last_updated TEXT)")
    c.commit()
    return c


def _jalali_label(value: str) -> str:
    """Format an ISO timestamp as Jalali date/time without another dependency."""
    if not value:
        return "بدون موعد"
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
        if parsed.tzinfo is not None:
            parsed = parsed.astimezone()
        gy, gm, gd = parsed.year, parsed.month, parsed.day
        gdm = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
        gy0, gm0, gd0 = gy - 1600, gm - 1, gd - 1
        day_no = 365 * gy0 + (gy0 + 3) // 4 - (gy0 + 99) // 100 + (gy0 + 399) // 400
        day_no += sum(gdm[:gm0])
        if gm0 > 1 and (gy % 4 == 0 and gy % 100 != 0 or gy % 400 == 0):
            day_no += 1
        day_no += gd0
        j_day_no = day_no - 79
        j_np = j_day_no // 12053
        j_day_no %= 12053
        jy = 979 + 33 * j_np + 4 * (j_day_no // 1461)
        j_day_no %= 1461
        if j_day_no >= 366:
            jy += (j_day_no - 1) // 365
            j_day_no = (j_day_no - 1) % 365
        if j_day_no < 186:
            jm, jd = 1 + j_day_no // 31, 1 + j_day_no % 31
        else:
            jm, jd = 7 + (j_day_no - 186) // 30, 1 + (j_day_no - 186) % 30
        return f"{jy:04d}/{jm:02d}/{jd:02d} {parsed.hour:02d}:{parsed.minute:02d}"
    except (ValueError, TypeError, OverflowError):
        return value


def _cookie_ok() -> bool:
    # An unset server token must never turn the workspace into a public endpoint.
    if not _sync_token:
        return False
    c = request.cookies.get("netenc_token") or ""
    return bool(c) and hmac.compare_digest(c, _sync_token)


@bp.route("/workspace/login", methods=["GET", "POST"])
def workspace_login():
    err = ""
    if request.method == "POST":
        tok = (request.form.get("token") or "").strip()
        if _sync_token and tok and hmac.compare_digest(tok, _sync_token):
            resp = make_response(redirect("/workspace"))
            resp.set_cookie("netenc_token", tok, httponly=True, samesite="Lax", max_age=60 * 60 * 12)
            return resp
        if not _sync_token:
            err = "دسترسی قفل است؛ ابتدا NETENC_TOKEN را در محیط سرور تنظیم کنید."
        else:
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
        elif tab == "tasks" and request.form.get("toggle"):
            uid = request.form["toggle"]
            row = c.execute("SELECT done, recurrence, due_at FROM ws_tasks WHERE uid=?", (uid,)).fetchone()
            now_dt = datetime.now(timezone.utc)
            now = now_dt.isoformat().replace("+00:00", "Z")
            if row and not row["done"] and row["recurrence"] in ("daily", "weekly") and row["due_at"]:
                try:
                    due = datetime.fromisoformat(row["due_at"].replace("Z", "+00:00"))
                    if due.tzinfo is None:
                        due = due.replace(tzinfo=timezone.utc)
                    base = max(due, now_dt)
                    from datetime import timedelta
                    next_due = base + (timedelta(days=1) if row["recurrence"] == "daily" else timedelta(days=7))
                    next_iso = next_due.isoformat().replace("+00:00", "Z")
                    c.execute("UPDATE ws_tasks SET done=0,due_at=?,reminder_at=?,last_notified_at='',last_updated=? WHERE uid=?",
                              (next_iso, next_iso, now, uid))
                except (ValueError, TypeError):
                    c.execute("UPDATE ws_tasks SET done=1,last_updated=? WHERE uid=?", (now, uid))
            else:
                c.execute("UPDATE ws_tasks SET done=CASE WHEN done=1 THEN 0 ELSE 1 END, last_updated=? WHERE uid=?",
                          (now, uid))
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
                    due_raw = (request.form.get("due_at") or "").strip()
                    due_at = ""
                    if due_raw:
                        try:
                            parsed = datetime.fromisoformat(due_raw)
                            due_at = parsed.astimezone(timezone.utc).isoformat().replace("+00:00", "Z")
                        except ValueError:
                            due_at = ""
                    recurrence = request.form.get("recurrence") or "none"
                    if recurrence not in ("none", "daily", "weekly"):
                        recurrence = "none"
                    try:
                        priority = max(1, min(4, int(request.form.get("priority") or 1)))
                    except ValueError:
                        priority = 1
                    c.execute(
                        """INSERT INTO ws_tasks(uid,title,body,done,due_at,priority,reminder_at,recurrence,last_notified_at,last_updated)
                           VALUES(?,?,?,?,?,?,?,?,?,?)""",
                        (uid, title, body, 0, due_at, priority, due_at, recurrence, "", now),
                    )
                c.commit()
    if tab == "notes":
        items = c.execute("SELECT uid,title,body FROM ws_notes ORDER BY last_updated DESC").fetchall()
        title = "یادداشت‌ها"
    elif tab == "vault":
        rows = c.execute("SELECT uid,title,username,secret FROM ws_vault ORDER BY title").fetchall()
        items = []
        for r in rows:
            secret_show = _unseal(r["secret"]) if (_authorized() or _cookie_ok()) else "••••"
            items.append({"uid": r["uid"], "title": r["title"], "body": f"{r['username']}\n{secret_show}"})
        title = "مدیریت رمز ورود (sealed)"
    else:
        rows = c.execute("SELECT uid,title,body,done,due_at,priority FROM ws_tasks ORDER BY done ASC, CASE WHEN due_at='' THEN 1 ELSE 0 END, due_at ASC, priority DESC, last_updated DESC").fetchall()
        items = []
        for row in rows:
            item = dict(row)
            due_label = _jalali_label(item.get("due_at") or "")
            item["body"] = (item.get("body") or "") + ("\nموعد شمسی: " + due_label if item.get("due_at") else "\nبدون موعد") + "\nاولویت: " + str(item.get("priority") or 1)
            items.append(item)
        title = "مدیریت کارها و زمان‌بندی"
    return render_template_string(PAGE, items=items, title=title, tab=tab)


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
