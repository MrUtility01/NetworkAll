# -*- coding: utf-8 -*-
"""وضعیت مطالعه و صف مرور — SRS (Again/Hard/Good/Easy)."""
from __future__ import annotations

from datetime import datetime, timedelta, timezone
import hashlib
import json
import os


def ensure_study_table(conn):
    conn.executescript(
        """
        CREATE TABLE IF NOT EXISTS study_progress (
            lesson_uid TEXT PRIMARY KEY,
            status TEXT DEFAULT 'new',
            ease REAL DEFAULT 2.5,
            interval_hours INTEGER DEFAULT 1,
            last_studied TEXT,
            next_review TEXT,
            times_studied INTEGER DEFAULT 0,
            notes TEXT DEFAULT '',
            last_updated TEXT NOT NULL DEFAULT '',
            device_id TEXT NOT NULL DEFAULT '',
            deleted INTEGER NOT NULL DEFAULT 0,
            content_hash TEXT NOT NULL DEFAULT ''
        );
        CREATE INDEX IF NOT EXISTS idx_study_next ON study_progress(next_review);
        CREATE INDEX IF NOT EXISTS idx_study_status ON study_progress(status);
        CREATE INDEX IF NOT EXISTS idx_study_deleted_updated ON study_progress(deleted, last_updated);
        """
    )
    # Additive migration for databases created before progress synchronization.
    columns = {row[1] for row in conn.execute("PRAGMA table_info(study_progress)").fetchall()}
    for name, declaration in (
        ("last_updated", "TEXT NOT NULL DEFAULT ''"),
        ("device_id", "TEXT NOT NULL DEFAULT ''"),
        ("deleted", "INTEGER NOT NULL DEFAULT 0"),
        ("content_hash", "TEXT NOT NULL DEFAULT ''"),
    ):
        if name not in columns:
            conn.execute(f"ALTER TABLE study_progress ADD COLUMN {name} {declaration}")
    # Preserve old records and make them visible to incremental sync.
    conn.execute(
        """UPDATE study_progress
           SET last_updated=COALESCE(NULLIF(last_updated,''), NULLIF(last_studied,''), ?)
           WHERE last_updated IS NULL OR last_updated=''""",
        (_now(),),
    )
    conn.commit()


def _study_hash(record):
    semantic = {k: record[k] for k in sorted(record)
                if k not in ("device_id", "last_updated", "content_hash")}
    packed = json.dumps(semantic, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(packed.encode("utf-8")).hexdigest()


def _study_record(row):
    raw = dict(row)
    item = {
        "uid": raw.get("lesson_uid") or "",
        "entity": "study",
        "status": raw.get("status") or "new",
        "ease": float(raw.get("ease") if raw.get("ease") is not None else 2.5),
        "interval_hours": int(raw.get("interval_hours") or 0),
        "last_studied": raw.get("last_studied") or "",
        "next_review": raw.get("next_review") or "",
        "times_studied": int(raw.get("times_studied") or 0),
        "notes": raw.get("notes") or "",
        "last_updated": raw.get("last_updated") or "",
        "device_id": raw.get("device_id") or "",
        "deleted": bool(raw.get("deleted", 0)),
    }
    item["content_hash"] = _study_hash(item)
    return item


def study_sync_index(conn):
    ensure_study_table(conn)
    return [
        {key: record[key] for key in ("uid", "entity", "last_updated", "content_hash", "deleted")}
        for record in (_study_record(row) for row in conn.execute("SELECT * FROM study_progress").fetchall())
    ]


def study_sync_pull(conn, uids):
    ensure_study_table(conn)
    clean = list(dict.fromkeys(str(uid) for uid in uids if str(uid).strip()))
    if not clean:
        return []
    marks = ",".join("?" for _ in clean)
    rows = conn.execute(
        f"SELECT * FROM study_progress WHERE lesson_uid IN ({marks})", clean
    ).fetchall()
    return [_study_record(row) for row in rows]


def study_sync_apply(conn, records):
    ensure_study_table(conn)
    now = datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")
    applied = 0
    for record in records:
        if not isinstance(record, dict):
            continue
        uid = str(record.get("uid") or "").strip()
        status = str(record.get("status") or "new").lower()
        if not uid or len(uid) > 256 or status not in {"new", "learning", "known", "review"}:
            continue
        try:
            ease = float(record.get("ease", 2.5))
            interval = int(record.get("interval_hours", record.get("intervalHours", 1)))
            times = int(record.get("times_studied", record.get("timesStudied", 0)))
        except (TypeError, ValueError, OverflowError):
            continue
        if not 1.0 <= ease <= 4.0 or not 0 <= interval <= 24 * 365 or not 0 <= times <= 10_000_000:
            continue
        last_studied = str(record.get("last_studied", record.get("lastStudied", "")) or "")[:64]
        next_review = str(record.get("next_review", record.get("nextReview", "")) or "")[:64]
        notes = str(record.get("notes") or "")[:20_000]
        updated = str(record.get("last_updated", record.get("lastUpdated", "")) or now)[:64]
        device = str(record.get("device_id", record.get("deviceId", "")) or "")[:128]
        deleted = 1 if record.get("deleted") is True or record.get("deleted") == 1 else 0
        conn.execute(
            """INSERT INTO study_progress(
                lesson_uid,status,ease,interval_hours,last_studied,next_review,times_studied,
                notes,last_updated,device_id,deleted,content_hash
            ) VALUES(?,?,?,?,?,?,?,?,?,?,?,?)
            ON CONFLICT(lesson_uid) DO UPDATE SET
                status=excluded.status,ease=excluded.ease,interval_hours=excluded.interval_hours,
                last_studied=excluded.last_studied,next_review=excluded.next_review,
                times_studied=excluded.times_studied,notes=excluded.notes,
                last_updated=excluded.last_updated,device_id=excluded.device_id,
                deleted=excluded.deleted,content_hash=excluded.content_hash""",
            (uid,status,ease,interval,last_studied,next_review,times,notes,updated,device,deleted,
             str(record.get("content_hash") or "")[:128]),
        )
        applied += 1
    conn.commit()
    return applied


def _now():
    return datetime.utcnow().replace(microsecond=0).isoformat() + "Z"


def mark_study(conn, lesson_uid: str, action: str):
    """action: again | hard | good | easy | studied | forgot"""
    ensure_study_table(conn)
    row = conn.execute("SELECT * FROM study_progress WHERE lesson_uid=?", (lesson_uid,)).fetchone()
    now = datetime.utcnow()
    if row is None:
        ease, interval, times = 2.5, 0, 0
    else:
        ease = float(row["ease"] if hasattr(row, "keys") else row[2] or 2.5)
        interval = int(row["interval_hours"] if hasattr(row, "keys") else row[3] or 0)
        times = int(row["times_studied"] if hasattr(row, "keys") else row[6] or 0)

    times += 1
    action = (action or "good").lower()
    if action in ("again", "forgot"):
        ease = max(1.3, ease - 0.25)
        interval = 1
        status = "learning"
        next_r = now + timedelta(hours=1)
    elif action == "hard":
        ease = max(1.3, ease - 0.1)
        interval = 6 if interval <= 0 else max(3, int(interval * 1.2))
        status = "review"
        next_r = now + timedelta(hours=interval)
    elif action == "easy":
        ease = min(3.0, ease + 0.15)
        interval = 72 if interval <= 0 else max(48, int(interval * ease * 1.3))
        if interval > 24 * 45:
            interval = 24 * 45
        status = "known" if times >= 2 else "learning"
        next_r = now + timedelta(hours=interval)
    else:
        if interval <= 0 or interval < 24:
            interval = 24
        else:
            interval = max(24, int(interval * ease))
        if interval > 24 * 30:
            interval = 24 * 30
        status = "known" if times >= 3 and interval >= 72 else "learning"
        next_r = now + timedelta(hours=interval)

    updated_at = _now()
    conn.execute(
        """INSERT INTO study_progress(
               lesson_uid,status,ease,interval_hours,last_studied,next_review,times_studied,
               last_updated,device_id,deleted,content_hash
           ) VALUES(?,?,?,?,?,?,?,?,?,?,?)
           ON CONFLICT(lesson_uid) DO UPDATE SET
             status=excluded.status, ease=excluded.ease, interval_hours=excluded.interval_hours,
             last_studied=excluded.last_studied, next_review=excluded.next_review,
             times_studied=excluded.times_studied, last_updated=excluded.last_updated,
             device_id=excluded.device_id, deleted=0, content_hash=''""",
        (lesson_uid, status, ease, interval, updated_at, next_r.replace(microsecond=0).isoformat() + "Z",
         times, updated_at, os.environ.get("NETENC_DEVICE", "server")[:128], 0, ""),
    )
    conn.commit()
    return {"uid": lesson_uid, "status": status, "next_review": next_r.isoformat() + "Z",
            "interval_hours": interval, "ease": ease, "times_studied": times,
            "last_updated": updated_at}


def due_reviews(conn, limit=50):
    ensure_study_table(conn)
    now = _now()
    rows = conn.execute(
        """SELECT lesson_uid, status, next_review, times_studied FROM study_progress
           WHERE next_review IS NOT NULL AND next_review <= ? ORDER BY next_review LIMIT ?""",
        (now, limit),
    ).fetchall()
    return [dict(r) if hasattr(r, "keys") else {"lesson_uid": r[0], "status": r[1], "next_review": r[2], "times_studied": r[3]} for r in rows]


def study_stats(conn):
    ensure_study_table(conn)
    def cnt(st):
        return conn.execute("SELECT COUNT(*) c FROM study_progress WHERE status=?", (st,)).fetchone()[0]
    total = conn.execute("SELECT COUNT(*) c FROM study_progress").fetchone()[0]
    return {"tracked": total, "new": cnt("new"), "learning": cnt("learning"),
            "known": cnt("known"), "review": cnt("review"), "due": len(due_reviews(conn, 500))}
