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
import os
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

from flask import Blueprint, request, jsonify, render_template_string, make_response, redirect, session

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
    # Reuse the authenticated local web session instead of prompting twice.
    if session.get("networkall_unlocked") is True:
        return True
    if _check_token is None:
        return False
    return bool(_check_token())


def _vault_key() -> bytes:
    """Load a separate per-install 256-bit key; back it up securely with vault data."""
    key_file = _db_path().parent / "networkall.vaultkey"
    key_file.parent.mkdir(parents=True, exist_ok=True)
    if key_file.exists():
        try:
            encoded = key_file.read_text(encoding="ascii").strip()
            key = base64.urlsafe_b64decode(encoded.encode("ascii"))
        except Exception as exc:
            raise RuntimeError("Vault key file is unreadable; restore networkall.vaultkey from the same backup") from exc
        if len(key) != 32:
            raise RuntimeError("Vault key file has invalid length; restore networkall.vaultkey from the same backup")
        return key
    key = os.urandom(32)
    key_file.write_text(base64.urlsafe_b64encode(key).decode("ascii") + "\n", encoding="ascii")
    try:
        os.chmod(key_file, 0o600)
    except OSError:
        pass
    return key


def _seal(plain: str) -> str:
    if not plain:
        return ""
    nonce = os.urandom(12)
    cipher = AESGCM(_vault_key()).encrypt(nonce, plain.encode("utf-8"), b"NetworkAll/vault/v2")
    return "enc2:" + base64.urlsafe_b64encode(nonce + cipher).decode("ascii")


def _unseal(blob: str) -> str:
    if not blob:
        return ""
    try:
        if blob.startswith("enc2:"):
            key_file = _db_path().parent / "networkall.vaultkey"
            if not key_file.is_file():
                return "•••• (کلید Vault وجود ندارد؛ فایل networkall.vaultkey را از پشتیبان بازیابی کنید)"
            raw = base64.urlsafe_b64decode(blob[5:].encode("ascii"))
            if len(raw) < 29:
                return "••••"
            return AESGCM(_vault_key()).decrypt(raw[:12], raw[12:], b"NetworkAll/vault/v2").decode("utf-8")
        if blob.startswith("enc1:"):
            # Compatibility only: decrypt the legacy XOR format so it can be
            # re-encrypted with AES-GCM on the next authenticated vault view.
            legacy_key = hashlib.sha256((_sync_token or "dev").encode("utf-8")).digest()
            old = base64.urlsafe_b64decode(blob[5:].encode("ascii"))
            plain = bytes(b ^ legacy_key[i % len(legacy_key)] for i, b in enumerate(old))
            return plain.decode("utf-8")
        return "•••• (legacy — edit to re-seal)"
    except Exception:
        return "••••"


LOGIN_PAGE = """
<!doctype html><html lang=fa dir=rtl><head><meta charset=utf-8>
<meta name=viewport content="width=device-width,initial-scale=1">
<title>ورود به فضای کاری NetworkAll</title>
<style>
*{box-sizing:border-box}body{font-family:Tahoma,sans-serif;background:#f3f6fb;color:#172033;display:grid;place-items:center;min-height:100vh;margin:0;padding:18px}
form{background:#fff;border:1px solid #d7e0ec;box-shadow:0 15px 45px #17203312;padding:26px;border-radius:16px;width:min(420px,100%)}
h2{margin:0 0 10px;color:#1645a7}p{line-height:1.9;color:#5b687d;font-size:13px}input,button{width:100%;padding:12px;margin:8px 0;box-sizing:border-box;font-size:15px;border-radius:9px;border:1px solid #cbd6e5}
button{background:#1d4ed8;color:#fff;border-color:#1d4ed8;font-weight:bold;cursor:pointer}.err{color:#b91c1c;font-size:13px}a{color:#1d4ed8}
</style></head><body>
<form method=post action="/workspace/login">
<h2>فضای کاری NetworkAll</h2>
<p>برای ورود از همان توکن نصب NetworkAll استفاده کن. توکن را در لینک، گزارش یا یادداشت اشتراکی قرار نده.</p>
<input type=password name=token placeholder="توکن نصب" required autofocus>
{% if error %}<p class=err>{{ error }}</p>{% endif %}
<button type=submit>ورود امن</button>
<p><a href="/">بازگشت به دانشنامه</a></p>
</form></body></html>
"""


_DIGIT_TO_ASCII = str.maketrans("۰۱۲۳۴۵۶۷۸۹٠١٢٣٤٥٦٧٨٩", "01234567890123456789")
_ASCII_TO_PERSIAN = str.maketrans("0123456789", "۰۱۲۳۴۵۶۷۸۹")

def _normalize_date_digits(value):
    return str(value or "").translate(_DIGIT_TO_ASCII).strip()

def _jalali_to_gregorian(year, month, day):
    jy = year + 1595
    days = -355668 + 365 * jy + (jy // 33) * 8 + ((jy % 33 + 3) // 4) + day
    days += (month - 1) * 31 if month < 7 else (month - 7) * 30 + 186
    gy = 400 * (days // 146097)
    days %= 146097
    if days > 36524:
        gy += 100 * ((days - 1) // 36524)
        days = (days - 1) % 36524
        if days >= 365:
            days += 1
    gy += 4 * (days // 1461)
    days %= 1461
    if days > 365:
        gy += (days - 1) // 365
        days = (days - 1) % 365
    gd = days + 1
    leap = gy % 4 == 0 and (gy % 100 != 0 or gy % 400 == 0)
    month_lengths = [31, 29 if leap else 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
    gm = 1
    while gm <= 12 and gd > month_lengths[gm - 1]:
        gd -= month_lengths[gm - 1]
        gm += 1
    return datetime(gy, gm, gd).date()

def _jalali_days_in_month(year, month):
    if month < 1 or month > 12:
        return 0
    if month <= 6:
        return 31
    if month <= 11:
        return 30
    return 30 if (_jalali_to_gregorian(year + 1, 1, 1) - _jalali_to_gregorian(year, 1, 1)).days == 366 else 29

def _gregorian_to_jalali(date_value):
    offsets = (0, 31, 59, 90, 120, 151, 181, 212, 243, 273, 304, 334)
    gy, gm, gd = date_value.year, date_value.month, date_value.day
    if gy > 1600:
        jy, gy = 979, gy - 1600
    else:
        jy, gy = 0, gy - 621
    gy2 = gy + 1 if gm > 2 else gy
    days = 365 * gy + (gy2 + 3) // 4 - (gy2 + 99) // 100 + (gy2 + 399) // 400 - 80 + gd + offsets[gm - 1]
    jy += 33 * (days // 12053)
    days %= 12053
    jy += 4 * (days // 1461)
    days %= 1461
    if days > 365:
        jy += (days - 1) // 365
        days = (days - 1) % 365
    if days < 186:
        jm, jd = 1 + days // 31, 1 + days % 31
    else:
        jm, jd = 7 + (days - 186) // 30, 1 + (days - 186) % 30
    return jy, jm, jd

def jalali_date(value):
    if not value:
        return ""
    try:
        day = datetime.strptime(str(value)[:10], "%Y-%m-%d").date()
        y, m, d = _gregorian_to_jalali(day)
        return f"{y:04d}/{m:02d}/{d:02d}".translate(_ASCII_TO_PERSIAN)
    except Exception:
        return str(value)

def jalali_datetime(value):
    if not value:
        return ""
    try:
        dt = datetime.fromisoformat(str(value).replace("Z", "+00:00"))
        if dt.tzinfo is not None:
            dt = dt.astimezone()
        return (jalali_date(dt.date().isoformat()) + " " + dt.strftime("%H:%M")).strip()
    except Exception:
        return str(value)

def parse_jalali_due_date(value):
    normalized = _normalize_date_digits(value).replace("-", "/")
    if not normalized:
        return ""
    parts = normalized.split("/")
    if len(parts) != 3:
        raise ValueError("تاریخ را به‌شکل ۱۴۰۵/۰۷/۲۲ وارد کنید.")
    try:
        year, month, day = map(int, parts)
        if year >= 1700:  # accept old Gregorian values from existing installs
            parsed = datetime(year, month, day).date()
        else:
            if not 1 <= month <= 12 or not 1 <= day <= _jalali_days_in_month(year, month):
                raise ValueError
            parsed = _jalali_to_gregorian(year, month, day)
        return parsed.isoformat()
    except Exception:
        raise ValueError("تاریخ شمسی معتبر نیست؛ نمونهٔ درست: ۱۴۰۵/۰۷/۲۲.")


PAGE = """
<!doctype html><html lang=fa dir=rtl><head><meta charset=utf-8>
<meta name=viewport content="width=device-width,initial-scale=1">
<title>فضای کاری NetworkAll</title>
<style>
:root{color-scheme:light}*{box-sizing:border-box}body{font-family:Tahoma,sans-serif;background:#f5f7fb;margin:0;padding:18px;color:#172033}
.wrap{max-width:1120px;margin:0 auto}.top{display:flex;gap:9px;align-items:center;flex-wrap:wrap;margin-bottom:18px}.top a{color:#1d4ed8;text-decoration:none;background:#fff;border:1px solid #d7e0ec;padding:9px 12px;border-radius:9px;font-size:12px}.brand{font-size:22px;font-weight:700;color:#1645a7;margin-left:auto}
h1{font-size:24px;margin:12px 0 6px}h2{font-size:15px}.muted,.badge{font-size:12px;color:#5b687d;line-height:1.9}.card{background:#fff;border:1px solid #d7e0ec;border-radius:13px;padding:15px;margin:11px 0;box-shadow:0 2px 7px #17203306}
.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(220px,1fr));gap:9px}label{display:block;font-size:12px;color:#43536a;margin:5px 0}
input,textarea,select,button{font:inherit}input,textarea,select{width:100%;margin:4px 0;padding:10px;border:1px solid #cbd6e5;border-radius:9px;background:#fff;color:#172033}
textarea{resize:vertical;line-height:1.8}button{padding:9px 12px;border-radius:9px;border:1px solid #1d4ed8;background:#1d4ed8;color:#fff;cursor:pointer;font-size:12px}button.secondary{background:#fff;color:#26354a;border-color:#cbd6e5}button.danger{background:#fff7f7;color:#b91c1c;border-color:#fecaca}
.actions{display:flex;gap:7px;flex-wrap:wrap;margin-top:10px}.actions form{display:inline-flex}.actions button{margin:0}
.form-grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(190px,1fr));gap:8px}.form-grid .wide{grid-column:1/-1}
.item-title{font-size:15px;font-weight:700;margin-bottom:6px}.item-body{white-space:pre-wrap;overflow-wrap:anywhere;line-height:1.9;color:#33445a;font-size:13px;margin:9px 0}.tags{display:flex;gap:6px;flex-wrap:wrap}.tag{font-size:11px;background:#edf3fb;border:1px solid #d7e0ec;border-radius:999px;padding:3px 8px;color:#3c4d64}
.search-row{display:flex;gap:8px;align-items:center}.search-row input{flex:1}.task-done{border-right:4px solid #16a34a}.task-open{border-right:4px solid #3b82f6}.priority-urgent{color:#b91c1c}.priority-high{color:#9a3412}.priority-normal{color:#1d4ed8}.priority-low{color:#64748b}
details{margin-top:12px;border-top:1px solid #e5ebf3;padding-top:10px}summary{cursor:pointer;color:#1d4ed8;font-size:12px;font-weight:bold}a{color:#1d4ed8}
.notice{font-size:12px;line-height:1.9;color:#56657a;background:#eef5ff;border:1px solid #cfe0fb;padding:12px;border-radius:10px}
@media(max-width:600px){body{padding:12px}.brand{width:100%}.search-row{align-items:stretch;flex-direction:column}}
</style></head><body><main class=wrap>
<nav class=top><span class=brand>NetworkAll / فضای کاری</span><a href="/">دانشنامه</a><a href="/diagrams">دیاگرام و عیب‌یابی</a><a href="/?view=incidents">سناریوهای واقعی</a><a href="/?view=quiz">مرکز آزمون</a><a href="/workspace?tab=tasks">کارها</a><a href="/workspace?tab=knowledge">مدیریت دانش</a><a href="/workspace?tab=notes">یادداشت‌ها</a><a href="/workspace?tab=vault">Vault</a><a href="/api/workspace/export">خروجی پشتیبان</a><a href="/workspace/logout">خروج</a></nav>
<div class=notice>کارها، دانش و یادداشت‌ها در دیتابیس محلی این نصب نگهداری می‌شوند. پیش از انتقال پوشه یا دستگاه، از پشتیبان استفاده کن. رمزهای Vault به‌صورت رمزگذاری‌شده ذخیره می‌شوند؛ فایل کلید Vault را جداگانه و امن پشتیبان بگیر.</div>
<h1>{{ title }}</h1><p class=muted>جستجو، دسته‌بندی و ثبت پیگیری‌ها؛ همهٔ تاریخ‌های قابل مشاهده و ورود سررسید با تقویم شمسی هستند.</p>
<form method=get action="/workspace" class=search-row><input type=hidden name=tab value="{{ tab }}"><input name=q value="{{ q }}" placeholder="جستجو در عنوان، متن، دسته یا برچسب"><button type=submit>جستجو</button><a href="/workspace?tab={{ tab }}">پاک‌کردن</a></form>
<section class=card><h2>{% if tab=='tasks' %}ثبت کار جدید{% elif tab in ('notes','knowledge') %}ثبت یادداشت / دانش جدید{% else %}ثبت مورد Vault{% endif %}</h2>
<form method=post class=form-grid>
<div><label>عنوان</label><input name=title placeholder="عنوان کوتاه و قابل جستجو" required></div>
{% if tab=='tasks' %}
<div><label>سررسید</label><input name=due_date type=text inputmode=numeric autocomplete=off placeholder="۱۴۰۵/۰۷/۲۲"></div>
<div><label>اولویت</label><select name=priority><option value=normal>عادی</option><option value=high>بالا</option><option value=urgent>فوری</option><option value=low>پایین</option></select></div>
<div><label>دسته</label><input name=category placeholder="شبکه، سرور، مشتری…" value="عمومی"></div>
{% elif tab in ('notes','knowledge') %}
<div><label>دسته</label><input name=category placeholder="Cisco، MikroTik، Windows…" value="عمومی"></div>
<div><label>برچسب‌ها</label><input name=tags placeholder="VLAN, DNS, OSPF"></div>
{% elif tab=='vault' %}
<div><label>نام کاربری (اختیاری)</label><input name=username autocomplete=off></div>
{% endif %}
<div class=wide><label>{% if tab=='vault' %}رمز / Secret — فقط در Vault رمزگذاری‌شده ذخیره می‌شود{% elif tab=='tasks' %}شرح، گام بعدی یا معیار پایان{% else %}متن، فرمان، شواهد، لینک یا نتیجهٔ آزمایش{% endif %}</label><textarea name=body rows=4 placeholder="جزئیات را دقیق ثبت کن…"></textarea></div>
<div class=wide><button type=submit>ذخیره</button></div>
</form></section>
{% for it in items %}
<article class="card {% if tab=='tasks' and it.done %}task-done{% elif tab=='tasks' %}task-open{% endif %}">
<div class=item-title>{{ it.title }} {% if tab=='tasks' and it.done %}<span class=tag>انجام‌شده</span>{% endif %}{% if tab in ('notes','knowledge') and it.favorite %}<span class=tag>★ مهم</span>{% endif %}</div>
<div class=tags>
{% if tab=='tasks' %}
<span class="tag priority-{{ it.priority or 'normal' }}">اولویت: {% if it.priority=='urgent' %}فوری{% elif it.priority=='high' %}بالا{% elif it.priority=='low' %}پایین{% else %}عادی{% endif %}</span>
<span class=tag>سررسید شمسی: {{ jalali_date(it.due_date) or 'ندارد' }}</span><span class=tag>{{ it.category or 'عمومی' }}</span>
{% elif tab in ('notes','knowledge') %}
<span class=tag>{{ it.category or 'عمومی' }}</span>{% if it.tags %}<span class=tag>{{ it.tags }}</span>{% endif %}
{% elif tab=='vault' and it.username %}<span class=tag>نام کاربری: {{ it.username }}</span>
{% endif %}
<span class=tag>به‌روزرسانی: {{ jalali_datetime(it.last_updated) }}</span>
</div>
{% if it.body %}<div class=item-body>{{ it.body }}</div>{% endif %}
<div class=actions>
{% if tab=='tasks' %}
<form method=post><input type=hidden name=action value=toggle><input type=hidden name=uid value="{{ it.uid }}"><button type=submit class=secondary>{% if it.done %}بازکردن دوباره{% else %}علامت انجام‌شده{% endif %}</button></form>
{% elif tab in ('notes','knowledge') %}
<form method=post><input type=hidden name=action value=toggle_favorite><input type=hidden name=uid value="{{ it.uid }}"><button type=submit class=secondary>{% if it.favorite %}برداشتن از مهم‌ها{% else %}★ افزودن به مهم‌ها{% endif %}</button></form>
{% endif %}
<form method=post onsubmit="return confirm('این مورد حذف شود؟')"><input type=hidden name=delete value="{{ it.uid }}"><button type=submit class=danger>حذف</button></form>
{% if tab!='vault' %}
<details><summary>ویرایش عنوان و جزئیات</summary>
<form method=post class=form-grid>
<input type=hidden name=edit_uid value="{{ it.uid }}">
<div><label>عنوان</label><input name=title value="{{ it.title }}" required></div>
{% if tab=='tasks' %}
<div><label>سررسید</label><input name=due_date type=text inputmode=numeric autocomplete=off placeholder="۱۴۰۵/۰۷/۲۲" value="{{ jalali_date(it.due_date) }}"></div>
<div><label>اولویت</label><select name=priority><option value=normal {% if it.priority=='normal' %}selected{% endif %}>عادی</option><option value=high {% if it.priority=='high' %}selected{% endif %}>بالا</option><option value=urgent {% if it.priority=='urgent' %}selected{% endif %}>فوری</option><option value=low {% if it.priority=='low' %}selected{% endif %}>پایین</option></select></div>
<div><label>دسته</label><input name=category value="{{ it.category or 'عمومی' }}"></div>
{% else %}
<div><label>دسته</label><input name=category value="{{ it.category or 'عمومی' }}"></div><div><label>برچسب‌ها</label><input name=tags value="{{ it.tags or '' }}"></div>
{% endif %}
<div class=wide><label>متن</label><textarea name=body rows=4>{{ it.body }}</textarea></div>
<div class=wide><button type=submit>ذخیرهٔ ویرایش</button></div>
</form></details>
{% endif %}
</div></article>
{% else %}<section class=card>هنوز موردی در این بخش ثبت نشده یا نتیجه‌ای با این جستجو پیدا نشد.</section>{% endfor %}
</main></body></html>
"""

def _db_path():
    root = Path(__file__).resolve().parent
    for path in (root / "data" / "encyclopedia.db", root / "encyclopedia.db"):
        if path.is_file():
            return path
    path = root / "data" / "encyclopedia.db"
    path.parent.mkdir(parents=True, exist_ok=True)
    return path


def _conn():
    c = sqlite3.connect(str(_db_path()))
    c.row_factory = sqlite3.Row
    c.execute("""CREATE TABLE IF NOT EXISTS ws_tasks(
        uid TEXT PRIMARY KEY, title TEXT, body TEXT, done INT DEFAULT 0,
        last_updated TEXT, priority TEXT NOT NULL DEFAULT 'normal',
        due_date TEXT NOT NULL DEFAULT '', category TEXT NOT NULL DEFAULT 'عمومی'
    )""")
    c.execute("""CREATE TABLE IF NOT EXISTS ws_notes(
        uid TEXT PRIMARY KEY, title TEXT, body TEXT, last_updated TEXT,
        category TEXT NOT NULL DEFAULT 'عمومی', tags TEXT NOT NULL DEFAULT '',
        favorite INTEGER NOT NULL DEFAULT 0
    )""")
    c.execute("CREATE TABLE IF NOT EXISTS ws_vault(uid TEXT PRIMARY KEY, title TEXT, username TEXT, secret TEXT, last_updated TEXT)")
    migrations = {
        "ws_tasks": {
            "priority": "TEXT NOT NULL DEFAULT 'normal'",
            "due_date": "TEXT NOT NULL DEFAULT ''",
            "category": "TEXT NOT NULL DEFAULT 'عمومی'",
        },
        "ws_notes": {
            "category": "TEXT NOT NULL DEFAULT 'عمومی'",
            "tags": "TEXT NOT NULL DEFAULT ''",
            "favorite": "INTEGER NOT NULL DEFAULT 0",
        },
    }
    for table, columns in migrations.items():
        present = {row["name"] for row in c.execute(f"PRAGMA table_info({table})").fetchall()}
        for name, definition in columns.items():
            if name not in present:
                c.execute(f"ALTER TABLE {table} ADD COLUMN {name} {definition}")
    c.commit()
    return c


def _cookie_ok() -> bool:
    if not _sync_token:
        return True
    c = request.cookies.get("netenc_token") or ""
    return hmac.compare_digest(c, _sync_token)


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
    if tab not in ("tasks", "notes", "knowledge", "vault"):
        tab = "tasks"
    note_tab = tab in ("notes", "knowledge")
    c = _conn()
    try:
        if request.method == "POST":
            now = datetime.now(timezone.utc).isoformat()
            delete_uid = (request.form.get("delete") or "").strip()
            action = (request.form.get("action") or "").strip()
            uid = (request.form.get("uid") or "").strip()
            edit_uid = (request.form.get("edit_uid") or "").strip()
            if delete_uid:
                table = "ws_notes" if note_tab else ("ws_vault" if tab == "vault" else "ws_tasks")
                c.execute(f"DELETE FROM {table} WHERE uid=?", (delete_uid,))
                c.commit()
            elif action == "toggle" and tab == "tasks" and uid:
                c.execute("UPDATE ws_tasks SET done=CASE WHEN done=1 THEN 0 ELSE 1 END,last_updated=? WHERE uid=?", (now, uid))
                c.commit()
            elif action == "toggle_favorite" and note_tab and uid:
                c.execute("UPDATE ws_notes SET favorite=CASE WHEN favorite=1 THEN 0 ELSE 1 END,last_updated=? WHERE uid=?", (now, uid))
                c.commit()
            else:
                title = (request.form.get("title") or "").strip()[:240]
                body = (request.form.get("body") or "")[:100000]
                username = (request.form.get("username") or "").strip()[:240]
                category = (request.form.get("category") or "عمومی").strip()[:100] or "عمومی"
                tags = (request.form.get("tags") or "").strip()[:500]
                priority = (request.form.get("priority") or "normal").strip().lower()
                if priority not in ("low", "normal", "high", "urgent"):
                    priority = "normal"
                due_date = (request.form.get("due_date") or "").strip()
                if due_date:
                    try:
                        due_date = parse_jalali_due_date(due_date)
                    except ValueError:
                        due_date = ""
                if title and tab == "tasks":
                    if edit_uid:
                        c.execute("UPDATE ws_tasks SET title=?,body=?,priority=?,due_date=?,category=?,last_updated=? WHERE uid=?",
                                  (title, body, priority, due_date, category, now, edit_uid))
                    else:
                        c.execute("INSERT INTO ws_tasks(uid,title,body,done,last_updated,priority,due_date,category) VALUES(?,?,?,?,?,?,?,?)",
                                  (str(uuid.uuid4()), title, body, 0, now, priority, due_date, category))
                    c.commit()
                elif title and note_tab:
                    if edit_uid:
                        c.execute("UPDATE ws_notes SET title=?,body=?,category=?,tags=?,last_updated=? WHERE uid=?",
                                  (title, body, category, tags, now, edit_uid))
                    else:
                        c.execute("INSERT INTO ws_notes(uid,title,body,last_updated,category,tags,favorite) VALUES(?,?,?,?,?,?,0)",
                                  (str(uuid.uuid4()), title, body, now, category, tags))
                    c.commit()
                elif title and tab == "vault":
                    c.execute("INSERT INTO ws_vault(uid,title,username,secret,last_updated) VALUES(?,?,?,?,?)",
                              (str(uuid.uuid4()), title, username, _seal(body), now))
                    c.commit()
        q = (request.args.get("q") or "").strip()[:200]
        like = f"%{q}%"
        if tab == "tasks":
            title = "مدیریت کارها و پیگیری عملیات"
            items = c.execute(
                """SELECT uid,title,body,done,last_updated,priority,due_date,category FROM ws_tasks
                   WHERE ?='' OR title LIKE ? OR body LIKE ? OR category LIKE ?
                   ORDER BY done ASC, CASE priority WHEN 'urgent' THEN 0 WHEN 'high' THEN 1 WHEN 'normal' THEN 2 ELSE 3 END,
                   CASE WHEN due_date='' THEN '9999-12-31' ELSE due_date END, last_updated DESC""",
                (q, like, like, like),
            ).fetchall()
        elif note_tab:
            title = "مدیریت دانش فنی" if tab == "knowledge" else "یادداشت‌ها و شواهد"
            items = c.execute(
                """SELECT uid,title,body,last_updated,category,tags,favorite FROM ws_notes
                   WHERE ?='' OR title LIKE ? OR body LIKE ? OR tags LIKE ? OR category LIKE ?
                   ORDER BY favorite DESC,last_updated DESC""",
                (q, like, like, like, like),
            ).fetchall()
        else:
            title = "Vault — اطلاعات حساس رمزگذاری‌شده"
            rows = c.execute(
                """SELECT uid,title,username,secret,last_updated FROM ws_vault
                   WHERE ?='' OR title LIKE ? OR username LIKE ? ORDER BY title""",
                (q, like, like),
            ).fetchall()
            items = []
            for row in rows:
                stored = row["secret"] or ""
                secret_show = _unseal(stored) if (_authorized() or _cookie_ok()) else "••••"
                if stored.startswith("enc1:") and not secret_show.startswith("••••"):
                    c.execute("UPDATE ws_vault SET secret=? WHERE uid=?", (_seal(secret_show), row["uid"]))
                items.append({"uid": row["uid"], "title": row["title"], "username": row["username"],
                              "body": secret_show, "last_updated": row["last_updated"]})
            c.commit()
        return render_template_string(PAGE, items=items, title=title, tab=tab, q=q, jalali_date=jalali_date, jalali_datetime=jalali_datetime)
    finally:
        c.close()



@bp.route("/api/workspace/export")
def workspace_export():
    if not _authorized():
        return jsonify({"error": "unauthorized"}), 401
    c = _conn()
    vault = []
    needs_legacy_token = False
    needs_vault_key = False
    for r in c.execute("SELECT * FROM ws_vault").fetchall():
        d = dict(r)
        secret_blob = d.get("secret") or ""
        # Keep backup output encrypted; never serialize a plaintext secret.
        d["secret_sealed"] = secret_blob.startswith(("enc1:", "enc2:"))
        d["encryption"] = "AES-256-GCM" if secret_blob.startswith("enc2:") else (
            "legacy-XOR" if secret_blob.startswith("enc1:") else "none"
        )
        needs_vault_key = needs_vault_key or secret_blob.startswith("enc2:")
        needs_legacy_token = needs_legacy_token or secret_blob.startswith("enc1:")
        vault.append(d)
    return jsonify({
        "format": "NetworkAll-workspace-backup-v1",
        "tasks": [dict(r) for r in c.execute("SELECT * FROM ws_tasks").fetchall()],
        "notes": [dict(r) for r in c.execute("SELECT * FROM ws_notes").fetchall()],
        "vault": vault,
        "vault_key_backup_required": needs_vault_key,
        "legacy_sync_token_required_for_enc1": needs_legacy_token,
    })
