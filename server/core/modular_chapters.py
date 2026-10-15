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


def _text(value) -> str:
    if value is None:
        return ""
    if isinstance(value, list):
        return "\n".join(str(x) for x in value)
    if isinstance(value, dict):
        return json.dumps(value, ensure_ascii=False, sort_keys=True)
    return str(value)


def _title_key(value) -> str:
    value = re.sub(r"^\[L[0-4]\]\s*", "", str(value or "").strip())
    return re.sub(r"\s+", " ", value).casefold()


def _merge_text(old, new) -> str:
    old, new = _text(old).strip(), _text(new).strip()
    if not old:
        return new
    if not new or new == old or new in old:
        return old
    if old in new:
        return new
    return old + "\n\n---\n\n" + new


def discover_chapter_packs():
    """Yield validated (path, payload) pairs. Invalid files are reported and skipped."""
    if not CHAPTERS_DIR.exists():
        return
    for path in sorted(CHAPTERS_DIR.glob("ch[0-9][0-9]_*/chapter.json")):
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
        chapter_rows = conn.execute(
            """SELECT l.id,l.uid,l.title_fa,l.title_en,l.summary,l.full_content,l.commands,
                      l.examples,l.notes,l.meta_json,l.learning_objectives,l.content_hash
               FROM lessons l JOIN levels lv ON lv.id=l.level_id
               JOIN chapters c ON c.id=lv.chapter_id
               WHERE c.order_index=? ORDER BY l.id""",
            (order,),
        ).fetchall()
        existing_by_title = {}
        for row in chapter_rows:
            existing_by_title.setdefault(_title_key(row["title_fa"]), dict(row))
        pending = []
        merged = 0
        for index, item in enumerate(source_lessons, 1):
            if not isinstance(item, dict):
                print(f"[chapters] SKIP non-object lesson {index} in {path.name}")
                continue
            title = str(item.get("title_fa") or item.get("title_en") or f"درس {index}")
            fingerprint = hashlib.sha256(
                json.dumps(item, ensure_ascii=False, sort_keys=True).encode("utf-8")
            ).hexdigest()
            title_key = _title_key(title)
            matched = existing_by_title.get(title_key)
            if matched:
                old_meta = {}
                try:
                    old_meta = json.loads(matched.get("meta_json") or "{}")
                    if not isinstance(old_meta, dict):
                        old_meta = {}
                except Exception:
                    old_meta = {}
                new_meta = item.get("meta") if isinstance(item.get("meta"), dict) else {}
                for meta_key, meta_value in new_meta.items():
                    if meta_key not in old_meta:
                        old_meta[meta_key] = meta_value
                    elif old_meta[meta_key] != meta_value:
                        old_meta.setdefault(f"source_{meta_key}", meta_value)
                summary_old = _text(matched.get("summary"))
                summary_new = _text(item.get("summary"))
                merged_values = {
                    "summary": summary_new if len(summary_new) > len(summary_old) else summary_old,
                    "full_content": _merge_text(matched.get("full_content"), item.get("full_content")),
                    "commands": _merge_text(matched.get("commands"), item.get("commands")),
                    "examples": _merge_text(matched.get("examples"), item.get("examples")),
                    "notes": _merge_text(matched.get("notes"), item.get("notes")),
                    "learning_objectives": _merge_text(matched.get("learning_objectives"), item.get("learning_objectives")),
                    "meta_json": json.dumps(old_meta, ensure_ascii=False),
                }
                changed = any(_text(matched.get(key)) != _text(value) for key, value in merged_values.items())
                if changed:
                    merged_hash = hashlib.sha256(
                        json.dumps(merged_values, ensure_ascii=False, sort_keys=True).encode("utf-8")
                    ).hexdigest()
                    conn.execute(
                        """UPDATE lessons SET summary=?,full_content=?,commands=?,examples=?,notes=?,
                           learning_objectives=?,meta_json=?,content_hash=?,last_updated=? WHERE id=?""",
                        (merged_values["summary"], merged_values["full_content"], merged_values["commands"],
                         merged_values["examples"], merged_values["notes"], merged_values["learning_objectives"],
                         merged_values["meta_json"], merged_hash, now, matched["id"]),
                    )
                    matched.update(merged_values)
                    matched["content_hash"] = merged_hash
                    merged += 1
                continue

            uid = str(item.get("uid") or f"lesson:ch{order:02d}:mod:{pack_slug}:{index:05d}")
            existing = conn.execute(
                "SELECT content_hash,title_fa FROM lessons WHERE uid=? LIMIT 1", (uid,)
            ).fetchone()
            if existing:
                # A matching UID is only a no-op when the title also matches this chapter.
                # Otherwise keep the new record under a collision-safe UID.
                base_uid = uid
                uid = f"{base_uid}:collision:{pack_slug}:{index:05d}"
                suffix = 2
                while conn.execute("SELECT 1 FROM lessons WHERE uid=? LIMIT 1", (uid,)).fetchone():
                    uid = f"{base_uid}:collision:{pack_slug}:{index:05d}:{suffix}"
                    suffix += 1
            keywords = item.get("search_keywords") or item.get("tags") or []
            if not isinstance(keywords, list):
                keywords = [str(keywords)]
            pending.append((uid, index, title, item, fingerprint, keywords))

        if not pending:
            continue

        level_title = str(payload.get("subchapter_title_fa") or f"محتوای افزوده: {path.stem}")
        cur = conn.execute(
            "INSERT INTO levels(chapter_id,order_index,title_fa,title_en) VALUES (?,?,?,?)",
            (chapter_id, int(level_order), level_title, str(payload.get("subchapter_title_en") or "")),
        )
        level_id = int(cur.lastrowid)

        for lesson_order, (uid, index, title, item, fingerprint, keywords) in enumerate(pending, 1):
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

    if added or merged:
        conn.commit()
        print(f"[chapters] added {added} new lessons; merged {merged} same-title lessons; existing records preserved")
    return {"ok": True, "added": added, "merged": merged}
