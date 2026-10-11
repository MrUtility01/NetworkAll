# -*- coding: utf-8 -*-
"""Tasks / Notes / Vault — auth required; vault secrets sealed (not plaintext)."""
from __future__ import annotations

import base64
import hashlib
import hmac
import os
import secrets
import uuid
from datetime import datetime, timezone
from pathlib import Path
import sqlite3

from cryptography.fernet import Fernet, InvalidToken

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


def _vault_key() -> bytes:
    """Stable per-install key; keep vault.key with encrypted DB backups."""
    configured = os.environ.get("NETENC_VAULT_KEY", "").strip()
    if configured:
        return base64.urlsafe_b64encode(hashlib.sha256(configured.encode("utf-8")).digest())
    data_dir = Path(__file__).resolve().parent / "data"
    data_dir.mkdir(parents=True, exist_ok=True)
    key_path = data_dir / "vault.key"
    try:
        raw = key_path.read_bytes()
    except FileNotFoundError:
        raw = secrets.token_bytes(32)
        try:
            with key_path.open("xb") as handle:
                handle.write(raw)
            try:
                os.chmod(key_path, 0o600)
            except OSError:
                pass
        except FileExistsError:
            raw = key_path.read_bytes()
    return base64.urlsafe_b64encode(hashlib.sha256(raw).digest())


def _seal(plain: str) -> str:
    if not plain:
        return ""
    if plain.startswith("enc2:"):
        return plain
    token = Fernet(_vault_key()).encrypt(plain.encode("utf-8")).decode("ascii")
    return "enc2:" + token


def _unseal(blob: str) -> str:
    if not blob:
        return ""
    try:
        if blob.startswith("enc2:"):
            return Fernet(_vault_key()).decrypt(blob[5:].encode("ascii")).decode("utf-8")
        if blob.startswith("enc1:"):
            # Backward-compatible reader for old XOR data. New writes always use Fernet.
            raw = base64.urlsafe_b64decode(blob[5:].encode("ascii"))
            candidates = [_sync_token, "09136555866", "dev"]
            for candidate in candidates:
                if not candidate:
                    continue
                key = hashlib.sha256(candidate.encode("utf-8")).digest()
                out = bytes(b ^ key[i % len(key)] for i, b in enumerate(raw))
                try:
                    return out.decode("utf-8")
                except UnicodeDecodeError:
                    continue
        return "•••• (legacy/unreadable — edit to re-seal)"
    except (InvalidToken, ValueError, UnicodeDecodeError):
        return "•••• (decryption failed)"


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
<a href="/workspace/calendar">تقویم شمسی</a>
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
<input type=text name=due_jalali placeholder="۱۴۰۵/۰۷/۱۹ ۲۱:۳۰">
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


CALENDAR_PAGE = """
<!doctype html><html lang=fa dir=rtl><head><meta charset=utf-8>
<meta name=viewport content="width=device-width,initial-scale=1">
<title>تقویم شمسی NetworkAll</title>
<style>
body{font-family:Tahoma,sans-serif;background:#f7f8fa;color:#0f172a;margin:0;padding:14px}
nav a{margin-left:12px;color:#0369a1;text-decoration:none;font-weight:bold}
table{width:100%;table-layout:fixed;border-collapse:collapse;background:#fff}
th,td{border:1px solid #e2e8f0;vertical-align:top;padding:5px;height:90px;overflow-wrap:anywhere}
th{background:#e2e8f0;font-size:12px}
.day{font-weight:bold;color:#1d4ed8}
.task{font-size:11px;background:#dbeafe;border-radius:5px;padding:3px;margin-top:4px}
nav{margin-bottom:12px}
</style></head><body>
<nav><a href="/workspace?tab=tasks">کارها</a><a href="/workspace/calendar?year={{ prev_year }}&month={{ prev_month }}">ماه قبل</a><a href="/workspace/calendar?year={{ next_year }}&month={{ next_month }}">ماه بعد</a></nav>
<h2>{{ month_name }} {{ year }}</h2>
<p>نمای ماهانه شمسی · موعدها بر اساس ساعت محلی نمایش داده می‌شوند.</p>
<table><thead><tr>{% for name in weekdays %}<th>{{ name }}</th>{% endfor %}</tr></thead><tbody>
{% for week in weeks %}<tr>{% for cell in week %}<td>{% if cell %}<div class=day>{{ cell.day }}</div>{% for task in cell.tasks %}<div class=task>{{ task.title }}{% if task.priority %} · P{{ task.priority }}{% endif %}</div>{% endfor %}{% endif %}</td>{% endfor %}</tr>{% endfor %}
</tbody></table>
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
        reminder_at TEXT DEFAULT '', recurrence TEXT DEFAULT 'none', last_notified_at TEXT DEFAULT '', device_id TEXT DEFAULT 'windows', last_updated TEXT
    )""")
    # Safe additive migration for databases created by older app versions.
    columns = {row["name"] for row in c.execute("PRAGMA table_info(ws_tasks)").fetchall()}
    for name, definition in (
        ("due_at", "TEXT DEFAULT ''"),
        ("priority", "INTEGER DEFAULT 1"),
        ("reminder_at", "TEXT DEFAULT ''"),
        ("recurrence", "TEXT DEFAULT 'none'"),
        ("last_notified_at", "TEXT DEFAULT ''"),
        ("device_id", "TEXT DEFAULT 'windows'"),
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


def _ascii_digits(value: str) -> str:
    out = []
    for ch in value:
        if "۰" <= ch <= "۹":
            out.append(chr(ord("0") + ord(ch) - ord("۰")))
        elif "٠" <= ch <= "٩":
            out.append(chr(ord("0") + ord(ch) - ord("٠")))
        else:
            out.append(ch)
    return "".join(out)


def _jalali_to_gregorian(jy: int, jm: int, jd: int):
    from datetime import date
    if jm not in range(1, 13) or jd < 1 or jd > (31 if jm <= 6 else 30):
        raise ValueError("invalid Jalali date")
    j_year = jy - 979
    j_day_no = 365 * j_year + (j_year // 33) * 8 + ((j_year % 33) + 3) // 4
    j_day_no += (jm - 1) * 31 if jm <= 6 else 186 + (jm - 7) * 30
    j_day_no += jd - 1
    g_day_no = j_day_no + 79
    gy = 1600 + 400 * (g_day_no // 146097)
    g_day_no %= 146097
    leap = True
    if g_day_no >= 36525:
        g_day_no -= 1
        gy += 100 * (g_day_no // 36524)
        g_day_no %= 36524
        if g_day_no >= 365:
            g_day_no += 1
        else:
            leap = False
    gy += 4 * (g_day_no // 1461)
    g_day_no %= 1461
    if g_day_no >= 366:
        leap = False
        g_day_no -= 1
        gy += g_day_no // 365
        g_day_no %= 365
    month_days = [31, 29 if leap else 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
    gm = 0
    while gm < 12 and g_day_no >= month_days[gm]:
        g_day_no -= month_days[gm]
        gm += 1
    return date(gy, gm + 1, g_day_no + 1)


def _parse_jalali_datetime(value: str) -> str:
    import re
    raw = _ascii_digits((value or "").strip()).replace("-", "/")
    match = re.fullmatch(r"(\d{4})/(\d{1,2})/(\d{1,2})(?:\s+(\d{1,2}):(\d{2}))?", raw)
    if not match:
        raise ValueError("date must be YYYY/MM/DD HH:MM in Jalali calendar")
    jy, jm, jd = (int(match.group(i)) for i in (1, 2, 3))
    hour, minute = int(match.group(4) or 0), int(match.group(5) or 0)
    if hour not in range(24) or minute not in range(60):
        raise ValueError("invalid time")
    day = _jalali_to_gregorian(jy, jm, jd)
    # Round-trip check rejects invalid Esfand days rather than silently normalizing them.
    rendered = _jalali_label(day.isoformat() + f"T{hour:02d}:{minute:02d}:00")
    if not rendered.startswith(f"{jy:04d}/{jm:02d}/{jd:02d}"):
        raise ValueError("invalid Jalali day for this year")
    local_dt = datetime(day.year, day.month, day.day, hour, minute).astimezone()
    return local_dt.astimezone(timezone.utc).isoformat().replace("+00:00", "Z")


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


@bp.route("/workspace/calendar")
def workspace_calendar():
    if not _authorized() and not _cookie_ok():
        return redirect("/workspace/login")
    now_parts = _jalali_label(datetime.now().astimezone().isoformat()).split(" ")[0].split("/")
    try:
        year = int(_ascii_digits(request.args.get("year") or now_parts[0]))
        month = int(_ascii_digits(request.args.get("month") or now_parts[1]))
        if month not in range(1, 13):
            raise ValueError
    except ValueError:
        year, month = int(now_parts[0]), int(now_parts[1])
    prev_year, prev_month = (year - 1, 12) if month == 1 else (year, month - 1)
    next_year, next_month = (year + 1, 1) if month == 12 else (year, month + 1)
    first = _jalali_to_gregorian(year, month, 1)
    next_first = _jalali_to_gregorian(next_year, next_month, 1)
    length = (next_first - first).days
    offset = (first.weekday() + 2) % 7  # Saturday first
    conn = _conn()
    try:
        rows = conn.execute("SELECT title,body,due_at,priority FROM ws_tasks WHERE COALESCE(due_at,'')!=''").fetchall()
    finally:
        conn.close()
    by_day = {}
    for row in rows:
        label = _jalali_label(row["due_at"] or "").split(" ")[0]
        try:
            y, m, d = (int(x) for x in label.split("/"))
        except Exception:
            continue
        if y == year and m == month:
            by_day.setdefault(d, []).append({"title": row["title"], "body": row["body"], "priority": row["priority"]})
    weeks, cells = [], [None] * offset
    for day in range(1, length + 1):
        cells.append({"day": day, "tasks": by_day.get(day, [])})
        if len(cells) == 7:
            weeks.append(cells)
            cells = []
    if cells:
        weeks.append(cells + [None] * (7 - len(cells)))
    return render_template_string(
        CALENDAR_PAGE, year=year, month_name=["فروردین","اردیبهشت","خرداد","تیر","مرداد","شهریور","مهر","آبان","آذر","دی","بهمن","اسفند"][month-1],
        prev_year=prev_year, prev_month=prev_month, next_year=next_year, next_month=next_month,
        weekdays=["شنبه","یکشنبه","دوشنبه","سه‌شنبه","چهارشنبه","پنجشنبه","جمعه"], weeks=weeks,
    )


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
                    due_jalali = (request.form.get("due_jalali") or "").strip()
                    due_raw = (request.form.get("due_at") or "").strip()
                    due_at = ""
                    if due_jalali:
                        try:
                            due_at = _parse_jalali_datetime(due_jalali)
                        except ValueError:
                            due_at = ""
                    elif due_raw:
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


@bp.route("/api/workspace/tasks", methods=["GET"])
def api_workspace_tasks():
    if not _authorized():
        return jsonify({"error": "unauthorized"}), 401
    conn = _conn()
    try:
        rows = conn.execute(
            """SELECT uid,title,body,done,due_at,priority,recurrence,last_notified_at,
                      device_id,last_updated FROM ws_tasks ORDER BY due_at, title LIMIT 5000"""
        ).fetchall()
        return jsonify({"items": [dict(row) for row in rows]})
    finally:
        conn.close()


@bp.route("/api/workspace/tasks/sync", methods=["POST"])
def api_workspace_tasks_sync():
    if not _authorized():
        return jsonify({"error": "unauthorized"}), 401
    body = request.get_json(silent=True) or {}
    items = body.get("items") or []
    if not isinstance(items, list) or len(items) > 2000:
        return jsonify({"error": "items must be a list with at most 2000 records"}), 400
    conn = _conn()
    accepted = kept = invalid = 0
    try:
        conn.execute("BEGIN IMMEDIATE")
        for item in items:
            if not isinstance(item, dict):
                invalid += 1
                continue
            uid = str(item.get("uid") or "").strip()
            title = str(item.get("title") or "").strip()
            if not uid or len(uid) > 128 or not title or len(title) > 500:
                invalid += 1
                continue
            body_text = str(item.get("body") or "")[:100000]
            due_at = str(item.get("due_at") or "")[:64]
            recurrence = str(item.get("recurrence") or "none")
            if recurrence not in ("none", "daily", "weekly"):
                recurrence = "none"
            try:
                priority = max(1, min(4, int(item.get("priority") or 1)))
            except (TypeError, ValueError):
                priority = 1
            done = 1 if item.get("done") else 0
            device_id = str(item.get("device_id") or "android")[:128]
            updated = str(item.get("last_updated") or "")
            last_notified = str(item.get("last_notified_at") or "")
            old = conn.execute("SELECT * FROM ws_tasks WHERE uid=?", (uid,)).fetchone()
            if old is None:
                conn.execute(
                    """INSERT INTO ws_tasks(uid,title,body,done,due_at,priority,reminder_at,
                       recurrence,last_notified_at,device_id,last_updated)
                       VALUES(?,?,?,?,?,?,?,?,?,?,?)""",
                    (uid,title,body_text,done,due_at,priority,due_at,recurrence,last_notified,device_id,updated),
                )
                accepted += 1
                continue
            old_updated = str(old["last_updated"] or "")
            old_device = str(old["device_id"] or "windows")
            wins = updated > old_updated or (updated == old_updated and device_id > old_device)
            # Reminder state is operational metadata and merges independently from task edits.
            merged_notified = max(str(old["last_notified_at"] or ""), last_notified)
            if wins:
                reset_notice = due_at != str(old["due_at"] or "")
                conn.execute(
                    """UPDATE ws_tasks SET title=?,body=?,done=?,due_at=?,priority=?,reminder_at=?,
                       recurrence=?,last_notified_at=?,device_id=?,last_updated=? WHERE uid=?""",
                    (title,body_text,done,due_at,priority,due_at,recurrence,
                     "" if reset_notice else merged_notified,device_id,updated,uid),
                )
                accepted += 1
            else:
                if merged_notified != str(old["last_notified_at"] or ""):
                    conn.execute("UPDATE ws_tasks SET last_notified_at=? WHERE uid=?", (merged_notified,uid))
                kept += 1
        conn.commit()
        return jsonify({"accepted": accepted, "kept": kept, "invalid": invalid})
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


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
