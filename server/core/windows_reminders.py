# -*- coding: utf-8 -*-
"""Native Windows reminders for local planner tasks.

This is a per-user local scheduler, not a cloud service. It requires the Flask
server to remain running in the signed-in Windows session. Dependency/import
errors are retried so a temporary startup problem does not permanently disable
reminders for the lifetime of the server process.
"""
from __future__ import annotations

import threading
import time
from datetime import datetime

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
    notification_type = None
    connection_factory = None

    while True:
        # Keep retrying startup dependencies instead of ending the daemon thread.
        if notification_type is None:
            try:
                from winotify import Notification
                notification_type = Notification
            except Exception as exc:
                print("Windows reminder notifications unavailable; will retry:", exc)
                time.sleep(30)
                continue

        if connection_factory is None:
            try:
                from workspace_routes import _conn
                connection_factory = _conn
            except Exception as exc:
                print("Windows reminder service cannot import workspace DB; will retry:", exc)
                time.sleep(30)
                continue

        conn = None
        try:
            # Planner timestamps use local wall-clock format to align with the user's calendar.
            # Keep seconds out of the comparison so YYYY-MM-DDTHH:MM due times fire predictably.
            now = datetime.now().strftime("%Y-%m-%dT%H:%M")
            conn = connection_factory()
            rows = conn.execute(
                """SELECT uid,title,body,due_at,remind_at FROM ws_tasks
                   WHERE done=0 AND deleted=0 AND remind_at<>'' AND remind_at<=?
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
                    toast = notification_type(
                        app_id="Engineer Jokar - NetworkEncyclopedia",
                        title=title,
                        msg=detail or "زمان انجام کار رسیده است.",
                        duration="long",
                    )
                    toast.show()
                    # Mark only after the notification API accepts the toast call.
                    # If the database update fails, this row remains eligible and the
                    # next poll retries; no claim is made that OS focus/notification
                    # settings guarantee that the toast was visibly noticed by the user.
                    conn.execute(
                        """UPDATE ws_tasks SET reminded_at=?
                           WHERE uid=? AND done=0 AND deleted=0
                             AND (reminded_at IS NULL OR reminded_at='')""",
                        (datetime.now().astimezone().isoformat(timespec="seconds"), row["uid"]),
                    )
                    conn.commit()
                except Exception as exc:
                    print("Could not deliver planner reminder for task", row["uid"], ":", exc)
        except Exception as exc:
            print("Planner reminder service error; will retry:", exc)
        finally:
            if conn is not None:
                try:
                    conn.close()
                except Exception as exc:
                    print("Could not close reminder DB connection:", exc)
        time.sleep(30)
