# -*- coding: utf-8 -*-
"""Load standalone chapter JSON packs into SQLite without deleting existing curriculum."""
from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path
from datetime import datetime

REPO_ROOT = Path(__file__).resolve().parents[2]
CHAPTERS_DIR = REPO_ROOT / "tools" / "chapters"


def _slug(value: str) -> str:
    value = re.sub(r"[^a-zA-Z0-9_-]+", "-", value.strip().lower()).strip("-")
    return value or "pack"


def discover_chapter_packs():
    """Yield validated (path, payload) pairs. Invalid files are reported and skipped."""
    if not CHAPTERS_DIR.exists():
        return
    for path in sorted(CHAPTERS_DIR.rglob("*.json")):
        try:
            payload = json.loads(path.read_text(encoding="utf-8"))
            order = int(payload["chapter_order"])
            lessons = payload.get("lessons")
            if order < 1 or not isinstance(lessons, list):
                raise ValueError("chapter_order must be positive and lessons must be a list")
            yield path, payload
        except Exception as exc:
            print(f"[chapters] SKIP {path.relative_to(REPO_ROOT)}: {exc}")


def import_chapter_packs(database):
    """Idempotently import packs. Existing chapter and lesson content is never replaced."""
    database.ensure_sync_columns()
    conn = database.conn
    now = datetime.now().isoformat(timespec="seconds")
    added = 0

    for path, payload in discover_chapter_packs() or ():
        order = int(payload["chapter_order"])
        title_fa = str(payload.get("chapter_title_fa") or payload.get("title_fa") or f"فصل {order}")
        title_en = str(payload.get("chapter_title_en") or payload.get("title_en") or f"Chapter {order}")
        relative = path.relative_to(CHAPTERS_DIR).with_suffix("")
        pack_slug = _slug("-".join(relative.parts))
        chapter = conn.execute(
            "SELECT id FROM chapters WHERE order_index=? ORDER BY id LIMIT 1", (order,)
        ).fetchone()
        if chapter:
            chapter_id = int(chapter["id"])
        else:
            cur = conn.execute(
                "INSERT INTO chapters(order_index,title_fa,title_en,description) VALUES (?,?,?,?)",
                (order, title_fa, title_en, "ماژول مستقل؛ واردشده از tools/chapters"),
            )
            chapter_id = int(cur.lastrowid)

        level_order = conn.execute(
            "SELECT COALESCE(MAX(order_index),0)+1 AS n FROM levels WHERE chapter_id=?",
            (chapter_id,),
        ).fetchone()["n"]
        # Do not create an empty level or re-import a pack whose UIDs already exist.
        source_lessons = payload.get("lessons") or []
        pending = []
        for index, item in enumerate(source_lessons, 1):
            if not isinstance(item, dict):
                print(f"[chapters] SKIP non-object lesson {index} in {path.name}")
                continue
            uid = str(item.get("uid") or f"lesson:ch{order:02d}:mod:{pack_slug}:{index:05d}")
            fingerprint = hashlib.sha256(
                json.dumps(item, ensure_ascii=False, sort_keys=True).encode("utf-8")
            ).hexdigest()
            existing = conn.execute(
                "SELECT content_hash FROM lessons WHERE uid=? LIMIT 1", (uid,)
            ).fetchone()
            if existing:
                # Re-importing the exact same lesson is a no-op. A different lesson with
                # a colliding UID is preserved under a deterministic collision-safe UID.
                if str(existing["content_hash"] or "") == fingerprint:
                    continue
                base_uid = uid
                uid = f"{base_uid}:collision:{pack_slug}:{index:05d}"
                suffix = 2
                while True:
                    collision = conn.execute(
                        "SELECT content_hash FROM lessons WHERE uid=? LIMIT 1", (uid,)
                    ).fetchone()
                    if not collision:
                        break
                    if str(collision["content_hash"] or "") == fingerprint:
                        uid = ""
                        break
                    uid = f"{base_uid}:collision:{pack_slug}:{index:05d}:{suffix}"
                    suffix += 1
                if not uid:
                    continue
            title = str(item.get("title_fa") or item.get("title_en") or f"درس {index}")
            pending.append((uid, index, title, item, fingerprint))

        if not pending:
            continue

        level_title = str(payload.get("subchapter_title_fa") or f"محتوای افزوده: {path.stem}")
        cur = conn.execute(
            "INSERT INTO levels(chapter_id,order_index,title_fa,title_en) VALUES (?,?,?,?)",
            (chapter_id, int(level_order), level_title, str(payload.get("subchapter_title_en") or "")),
        )
        level_id = int(cur.lastrowid)

        for lesson_order, (uid, index, title, item, fingerprint) in enumerate(pending, 1):
            meta = item.get("meta") if isinstance(item.get("meta"), dict) else {}
            keywords = item.get("search_keywords") or item.get("tags") or []
            if not isinstance(keywords, list):
                keywords = [str(keywords)]
            conn.execute(
                """INSERT INTO lessons(
                    level_id,order_index,title_fa,title_en,tags,summary,full_content,
                    commands,examples,notes,meta_json,search_query,learning_objectives,
                    source_status,last_updated,uid,content_hash,device_id,deleted
                ) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,0)""",
                (
                    level_id, lesson_order, title, str(item.get("title_en") or ""),
                    ",".join(str(x) for x in keywords),
                    str(item.get("summary") or ""), str(item.get("full_content") or ""),
                    "\n".join(map(str, item.get("commands", []))) if isinstance(item.get("commands"), list) else str(item.get("commands") or ""),
                    "\n".join(map(str, item.get("examples", []))) if isinstance(item.get("examples"), list) else str(item.get("examples") or ""),
                    str(item.get("notes") or ""), json.dumps(meta, ensure_ascii=False),
                    " ".join(str(x) for x in keywords), str(item.get("learning_objectives") or ""),
                    str(item.get("source_status") or "modular_pack"), now, uid,
                    fingerprint,
                    "modular-import",
                ),
            )
            added += 1

    if added:
        conn.commit()
        print(f"[chapters] imported {added} new lessons; existing lessons preserved")
    return {"ok": True, "added": added}
