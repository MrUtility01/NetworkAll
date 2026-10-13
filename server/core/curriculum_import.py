# -*- coding: utf-8 -*-
"""Non-destructive synchronization of the shared curriculum index into the Windows SQLite database."""
from __future__ import annotations

import gzip
import hashlib
import json
import re
import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
DEFAULT_INDEX = ROOT / "shared" / "curriculum_index.json.gz"

LEGACY_UID_PREFIXES = (
    ("lesson:ch09:tcp-engineering:", "lesson:ch07:tcp:"),
    ("lesson:ch09:udp-quic:", "lesson:ch08:udp:"),
    ("lesson:ch08:ipv4-subnetting:", "lesson:ipv4-subnetting:"),
    ("lesson:ch49:mikrotik-monitoring-zabbix:", "lesson:ch22:monitoring-logging-zabbix:"),
    ("lesson:ch49:zabbix-operations:", "lesson:ch23:zabbix-operations:"),
)


def _now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _norm(value: Any) -> str:
    return re.sub(r"\s+", " ", str(value or "").replace("\u200c", " ")).strip().casefold()


def _legacy_uid(uid: str) -> str | None:
    for current_prefix, old_prefix in LEGACY_UID_PREFIXES:
        if uid.startswith(current_prefix):
            return old_prefix + uid[len(current_prefix):]
    return None


def _study_table(conn: sqlite3.Connection) -> None:
    # Use the application's additive migration so older progress tables are upgraded safely.
    from core.study import ensure_study_table
    ensure_study_table(conn)


def _migrate_study_uid(conn: sqlite3.Connection, old_uid: str, new_uid: str, now: str) -> None:
    if not old_uid or old_uid == new_uid:
        return
    old = conn.execute("SELECT * FROM study_progress WHERE lesson_uid=?", (old_uid,)).fetchone()
    if old is None:
        return
    new = conn.execute("SELECT * FROM study_progress WHERE lesson_uid=?", (new_uid,)).fetchone()
    if new is None:
        conn.execute(
            "UPDATE study_progress SET lesson_uid=?, last_updated=?, device_id='curriculum-migration' WHERE lesson_uid=?",
            (new_uid, now, old_uid),
        )
        return

    old_d, new_d = dict(old), dict(new)
    old_key = str(old_d.get("last_updated") or old_d.get("last_studied") or "")
    new_key = str(new_d.get("last_updated") or new_d.get("last_studied") or "")
    preferred, secondary = (old_d, new_d) if old_key > new_key else (new_d, old_d)
    last_studied = max(str(old_d.get("last_studied") or ""), str(new_d.get("last_studied") or ""))
    conn.execute(
        """UPDATE study_progress SET status=?, ease=?, interval_hours=?, last_studied=?,
           next_review=?, times_studied=?, notes=?, last_updated=?, device_id=?, deleted=?,
           content_hash='' WHERE lesson_uid=?""",
        (
            preferred.get("status") or secondary.get("status") or "new",
            float(preferred.get("ease") or secondary.get("ease") or 2.5),
            max(int(old_d.get("interval_hours") or 0), int(new_d.get("interval_hours") or 0)),
            last_studied,
            preferred.get("next_review") or secondary.get("next_review") or "",
            max(int(old_d.get("times_studied") or 0), int(new_d.get("times_studied") or 0)),
            preferred.get("notes") or secondary.get("notes") or "",
            now,
            preferred.get("device_id") or secondary.get("device_id") or "curriculum-migration",
            1 if old_d.get("deleted") and new_d.get("deleted") else 0,
            new_uid,
        ),
    )
    conn.execute("DELETE FROM study_progress WHERE lesson_uid=?", (old_uid,))


def _payload_counts(payload: dict) -> tuple[int, int]:
    chapters = payload.get("chapters")
    if not isinstance(chapters, list) or not chapters:
        raise ValueError("Curriculum index has no chapter array")
    orders = [int(ch.get("order") or 0) for ch in chapters]
    if len(orders) != len(set(orders)):
        raise ValueError("Curriculum index contains duplicate chapter order")
    lesson_count = 0
    seen_uids = set()
    for chapter in chapters:
        for sub in chapter.get("subchapters") or []:
            for lesson in sub.get("lessons") or []:
                uid = str(lesson.get("uid") or "").strip()
                if not uid:
                    raise ValueError("Curriculum index contains a lesson without UID")
                if uid in seen_uids:
                    raise ValueError(f"Curriculum index contains duplicate UID: {uid}")
                seen_uids.add(uid)
                lesson_count += 1
    declared = int(payload.get("lesson_count") or 0)
    if declared and declared != lesson_count:
        raise ValueError(f"Curriculum index count mismatch: declared={declared}; actual={lesson_count}")
    return len(chapters), lesson_count


def sync_canonical_curriculum(db, asset_path: str | Path | None = None) -> dict:
    """Upsert shared lessons, keep user progress and soft deletions, and back up before refresh."""
    path = Path(asset_path) if asset_path else DEFAULT_INDEX
    if not path.is_file():
        return {"ok": True, "skipped": True, "reason": "shared curriculum index not packaged"}

    raw = gzip.open(path, "rb").read()
    digest = hashlib.sha256(raw).hexdigest()
    if db.get_meta("curriculum_index_sha256") == digest:
        return {"ok": True, "skipped": True, "reason": "curriculum index unchanged"}

    payload = json.loads(raw.decode("utf-8"))
    chapter_count, lesson_count = _payload_counts(payload)
    db.ensure_sync_columns()
    _study_table(db.conn)
    conn = db.conn
    old_digest = db.get_meta("curriculum_index_sha256")
    existing_count = int(conn.execute("SELECT COUNT(*) FROM lessons").fetchone()[0])
    backup_path = None
    if existing_count > 0 and old_digest != digest:
        backup_path = db.backup()

    now = _now()
    chapters_by_order = {
        int(row["order_index"]): dict(row)
        for row in conn.execute("SELECT id, order_index, title_fa, title_en FROM chapters ORDER BY id").fetchall()
        if int(row["order_index"] or 0) > 0
    }
    lessons_by_uid = {}
    for row in conn.execute("SELECT * FROM lessons WHERE uid IS NOT NULL AND uid!='' ORDER BY id").fetchall():
        lessons_by_uid.setdefault(str(row["uid"]), dict(row))
    lessons_by_level = {}
    for row in conn.execute("SELECT * FROM lessons ORDER BY id").fetchall():
        lessons_by_level.setdefault(int(row["level_id"]), []).append(dict(row))
    used_row_ids: set[int] = set()
    imported = 0
    updated = 0
    added = 0
    migrated_uids = 0
    soft_deleted_duplicates = 0

    try:
        conn.execute("BEGIN IMMEDIATE")
        for chapter in payload["chapters"]:
            chapter_order = int(chapter.get("order") or 0)
            if chapter_order <= 0:
                raise ValueError(f"Invalid chapter order: {chapter_order}")
            existing_chapter = chapters_by_order.get(chapter_order)
            if existing_chapter:
                chapter_id = int(existing_chapter["id"])
                conn.execute(
                    "UPDATE chapters SET title_fa=?, title_en=? WHERE id=?",
                    (str(chapter.get("title_fa") or f"فصل {chapter_order}"),
                     str(chapter.get("title_en") or ""), chapter_id),
                )
            else:
                cur = conn.execute(
                    "INSERT INTO chapters(order_index,title_fa,title_en) VALUES(?,?,?)",
                    (chapter_order, str(chapter.get("title_fa") or f"فصل {chapter_order}"),
                     str(chapter.get("title_en") or "")),
                )
                chapter_id = int(cur.lastrowid)
                chapters_by_order[chapter_order] = {
                    "id": chapter_id, "order_index": chapter_order,
                    "title_fa": chapter.get("title_fa") or "", "title_en": chapter.get("title_en") or ""
                }

            levels = conn.execute(
                "SELECT id, order_index, title_fa FROM levels WHERE chapter_id=? ORDER BY order_index,id",
                (chapter_id,),
            ).fetchall()
            levels_by_order = {}
            for row in levels:
                levels_by_order.setdefault(int(row["order_index"]), dict(row))

            for sub_index, sub in enumerate(chapter.get("subchapters") or [], 1):
                sub_order = int(sub.get("subchapter_order") or sub_index)
                if sub_order <= 0:
                    sub_order = sub_index
                sub_title = str(sub.get("title_fa") or f"زیرشاخهٔ {sub_order}")
                existing_level = levels_by_order.get(sub_order)
                if existing_level:
                    level_id = int(existing_level["id"])
                    conn.execute(
                        "UPDATE levels SET title_fa=?, order_index=? WHERE id=?",
                        (sub_title, sub_order, level_id),
                    )
                else:
                    cur = conn.execute(
                        "INSERT INTO levels(chapter_id,order_index,title_fa) VALUES(?,?,?)",
                        (chapter_id, sub_order, sub_title),
                    )
                    level_id = int(cur.lastrowid)
                    levels_by_order[sub_order] = {"id": level_id, "order_index": sub_order, "title_fa": sub_title}
                    lessons_by_level[level_id] = []

                for lesson_index, lesson in enumerate(sub.get("lessons") or [], 1):
                    uid = str(lesson.get("uid") or "").strip()
                    if not uid:
                        continue
                    candidate = lessons_by_uid.get(uid)
                    legacy_uid = _legacy_uid(uid)
                    legacy_row = lessons_by_uid.get(legacy_uid) if legacy_uid else None
                    if candidate is None and legacy_row is not None and int(legacy_row["id"]) not in used_row_ids:
                        candidate = legacy_row
                    if candidate is None:
                        title_key = (_norm(lesson.get("title_fa")), _norm(lesson.get("title_en")))
                        for old_row in lessons_by_level.get(level_id, []):
                            if int(old_row["id"]) in used_row_ids or int(old_row["id"]) in {int(x["id"]) for x in lessons_by_uid.values() if str(x.get("uid") or "") == uid}:
                                continue
                            old_key = (_norm(old_row.get("title_fa")), _norm(old_row.get("title_en")))
                            if title_key == old_key or (title_key[0] and title_key[0] == old_key[0]):
                                candidate = old_row
                                break

                    meta_json = str(lesson.get("meta_json") or "{}")
                    try:
                        meta = json.loads(meta_json)
                        if not isinstance(meta, dict):
                            meta = {}
                    except Exception:
                        meta = {}
                    assessment = lesson.get("assessment")
                    if isinstance(assessment, dict) and assessment:
                        meta["assessment"] = assessment
                        meta_json = json.dumps(meta, ensure_ascii=False, separators=(",", ":"))
                    title_fa = str(lesson.get("title_fa") or "")
                    title_en = str(lesson.get("title_en") or "")
                    summary = str(lesson.get("summary") or "")
                    full_content = str(lesson.get("full_content") or "")
                    commands = str(lesson.get("commands") or "")
                    examples = str(lesson.get("examples") or "")
                    notes = str(lesson.get("notes") or "")
                    objectives = str(lesson.get("learning_objectives") or "")
                    search_query = str(lesson.get("search_query") or f"{title_fa} {title_en} {summary}")
                    source_status = str(lesson.get("source_status") or "review_required")
                    row_updated = str(lesson.get("last_updated") or now)
                    content_hash = hashlib.sha256(
                        json.dumps(
                            [title_fa, title_en, summary, full_content, commands, examples, notes, meta_json, objectives],
                            ensure_ascii=False, separators=(",", ":")
                        ).encode("utf-8")
                    ).hexdigest()

                    if candidate is not None:
                        old_uid = str(candidate.get("uid") or "")
                        row_id = int(candidate["id"])
                        was_deleted = int(candidate.get("deleted") or 0)
                        conn.execute(
                            """UPDATE lessons SET uid=?, level_id=?, order_index=?, title_fa=?, title_en=?, tags=?,
                               summary=?, full_content=?, commands=?, examples=?, notes=?, meta_json=?, search_query=?,
                               learning_objectives=?, source_status=?, last_updated=?, content_hash=?, device_id=?, deleted=?
                               WHERE id=?""",
                            (
                                uid, level_id, lesson_index, title_fa, title_en, str(lesson.get("level") or "L0"),
                                summary, full_content, commands, examples, notes, meta_json, search_query,
                                objectives, source_status, now if old_uid != uid or old_digest != digest else row_updated,
                                content_hash, "curriculum-index", was_deleted, row_id,
                            ),
                        )
                        if old_uid and old_uid != uid:
                            _migrate_study_uid(conn, old_uid, uid, now)
                            lessons_by_uid.pop(old_uid, None)
                            migrated_uids += 1
                        candidate.update({
                            "uid": uid, "level_id": level_id, "order_index": lesson_index,
                            "title_fa": title_fa, "title_en": title_en, "summary": summary,
                            "full_content": full_content, "commands": commands, "examples": examples,
                            "notes": notes, "meta_json": meta_json, "deleted": was_deleted,
                        })
                        lessons_by_uid[uid] = candidate
                        used_row_ids.add(row_id)
                        updated += 1
                    else:
                        cur = conn.execute(
                            """INSERT INTO lessons(level_id,order_index,title_fa,title_en,tags,summary,full_content,
                               commands,examples,notes,meta_json,search_query,learning_objectives,source_status,
                               last_updated,uid,content_hash,device_id,deleted)
                               VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,0)""",
                            (
                                level_id, lesson_index, title_fa, title_en, str(lesson.get("level") or "L0"),
                                summary, full_content, commands, examples, notes, meta_json, search_query,
                                objectives, source_status, now, uid, content_hash, "curriculum-index",
                            ),
                        )
                        row_id = int(cur.lastrowid)
                        new_row = {
                            "id": row_id, "uid": uid, "level_id": level_id, "order_index": lesson_index,
                            "title_fa": title_fa, "title_en": title_en, "summary": summary,
                            "full_content": full_content, "commands": commands, "examples": examples,
                            "notes": notes, "meta_json": meta_json, "deleted": 0,
                        }
                        lessons_by_uid[uid] = new_row
                        lessons_by_level.setdefault(level_id, []).append(new_row)
                        used_row_ids.add(row_id)
                        added += 1
                    imported += 1

                    # If a legacy duplicate already had the canonical UID counterpart, retain
                    # it as a tombstone so that progress has one visible lesson identity.
                    if candidate is not None and legacy_uid and uid in lessons_by_uid:
                        duplicate = lessons_by_uid.get(legacy_uid)
                        if duplicate and int(duplicate["id"]) != int(candidate["id"]):
                            _migrate_study_uid(conn, legacy_uid, uid, now)
                            conn.execute("UPDATE lessons SET deleted=1, last_updated=? WHERE id=?", (now, int(duplicate["id"])))
                            lessons_by_uid.pop(legacy_uid, None)
                            soft_deleted_duplicates += 1

        conn.execute(
            "INSERT INTO meta(key,value) VALUES('curriculum_index_sha256',?) ON CONFLICT(key) DO UPDATE SET value=excluded.value",
            (digest,),
        )
        conn.execute(
            "INSERT INTO meta(key,value) VALUES('curriculum_index_version',?) ON CONFLICT(key) DO UPDATE SET value=excluded.value",
            (str(payload.get("version") or "unknown"),),
        )
        conn.commit()
    except Exception:
        conn.rollback()
        raise

    return {
        "ok": True, "skipped": False, "chapters": chapter_count, "lessons": lesson_count,
        "imported": imported, "updated": updated, "added": added, "migrated_uids": migrated_uids,
        "soft_deleted_duplicates": soft_deleted_duplicates, "backup": str(backup_path) if backup_path else None,
        "version": payload.get("version"),
    }
