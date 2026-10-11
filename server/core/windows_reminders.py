# -*- coding: utf-8 -*-
"""Native Windows reminders for local planner tasks.

The service runs only inside the user's Windows app process. It is not a cloud
scheduler; reminders require the local Python server to remain running.
"""
from __future__ import annotations

import threading
import time
from datetime import datetime
from pathlib import Path

_LOCK = threading.Lock()
_STARTED = False


def start_windows_reminder_service() -> bool:
    """Start one background reminder poller on Windows; safe to call repeatedly."""
    global _STARTED
    import os
    if os.name != "nt":
        return False
    with _LOCK:
        if _STARTED:
            return True
        _STARTED = True
    thread = threading.Thread(target=_run, name="NetEncWindowsReminders", daemon=True)
    thread.start()
    return True


def _run() -> None:
    try:
        from winotify import Notification
    except Exception as exc:
        print("Windows reminder notifications unavailable; install requirements:", exc)
        return

    try:
        from workspace_routes import _conn
    except Exception as exc:
        print("Windows reminder service cannot import workspace DB:", exc)
        return

    while True:
        try:
            now = datetime.now().strftime("%Y-%m-%dT%H:%M")
            conn = _conn()
            rows = conn.execute(
                """SELECT uid,title,body,due_at FROM ws_tasks
                   WHERE done=0 AND remind_at<>'' AND remind_at<=?
                     AND (reminded_at IS NULL OR reminded_at='')
                   ORDER BY remind_at LIMIT 30""",
                (now,),
            ).fetchall()
            for row in rows:
                title = (row["title"] or "کار برنامه‌ریزی‌شده")[:180]
                body = (row["body"] or "").strip().replace("\x00", "")[:500]
                due_at = (row["due_at"] or "").replace("T", " ")
                detail = ("سررسید: " + due_at + ("\n" + body if body else ""))[:700]
                try:
                    toast = Notification(
                        app_id="Engineer Jokar - NetworkEncyclopedia",
                        title=title,
                        msg=detail or "زمان انجام کار رسیده است.",
                        duration="long",
                    )
                    toast.show()
                    conn.execute(
                        "UPDATE ws_tasks SET reminded_at=? WHERE uid=? AND (reminded_at IS NULL OR reminded_at='')",
                        (datetime.now().astimezone().isoformat(timespec="seconds"), row["uid"]),
                    )
                    conn.commit()
                except Exception as exc:
                    print("Could not display planner reminder:", exc)
            conn.close()
        except Exception as exc:
            print("Planner reminder service error:", exc)
        time.sleep(30)
