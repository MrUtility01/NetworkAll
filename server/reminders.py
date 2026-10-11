# -*- coding: utf-8 -*-
"""Local Windows task reminders; no cloud service is used."""
from __future__ import annotations

import os
import threading
import time
from datetime import datetime, timezone

_started = False
_start_lock = threading.Lock()


def _notify_windows(title: str, message: str) -> bool:
    if os.name != "nt":
        return False
    try:
        from winotify import Notification
        Notification(app_id="NetworkAll", title=title, msg=message, duration="short").show()
        return True
    except Exception as exc:
        print("Windows notification unavailable:", exc)
        return False


def _poll_once():
    # Import lazily to avoid circular imports while Flask registers its blueprint.
    from workspace_routes import _conn

    conn = _conn()
    try:
        now = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
        rows = conn.execute(
            """SELECT uid,title,due_at FROM ws_tasks
               WHERE done=0 AND COALESCE(due_at,'')!='' AND due_at<=?
                 AND (COALESCE(last_notified_at,'')='' OR last_notified_at<due_at)
               ORDER BY due_at ASC LIMIT 20""",
            (now,),
        ).fetchall()
        if not rows:
            return
        names = [str(row["title"] or "کار بدون عنوان") for row in rows[:4]]
        message = "، ".join(names)
        if len(rows) > 4:
            message += " و " + str(len(rows) - 4) + " مورد دیگر"
        # Mark as notified after a notification or console fallback, preventing
        # the same overdue task from producing a toast every minute.
        sent = _notify_windows("NetworkAll — موعد کار", message)
        if not sent:
            print("[NetworkAll reminder]", message)
        for row in rows:
            conn.execute("UPDATE ws_tasks SET last_notified_at=? WHERE uid=?", (now, row["uid"]))
        conn.commit()
    finally:
        conn.close()


def _loop():
    while True:
        try:
            _poll_once()
        except Exception as exc:
            print("NetworkAll reminder loop error:", exc)
        time.sleep(60)


def start_reminder_loop():
    """Start one background reminder thread per server process."""
    global _started
    with _start_lock:
        if _started:
            return
        thread = threading.Thread(target=_loop, name="networkall-reminders", daemon=True)
        thread.start()
        _started = True
