# -*- coding: utf-8 -*-
"""SQLite سبک برای نسخه وب — فصل‌های ۱–۶۸ با محتوای غنی."""
from __future__ import annotations

import gzip
import hashlib
import json
import sqlite3
from pathlib import Path
from datetime import datetime

BASE = Path(__file__).resolve().parent.parent
DB_PATH = BASE / "data" / "encyclopedia.db"


class WebDB:
    def __init__(self, path=None):
        self.path = Path(path) if path else DB_PATH
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.conn = sqlite3.connect(str(self.path), check_same_thread=False)
        self.conn.row_factory = sqlite3.Row
        self.conn.execute("PRAGMA foreign_keys = ON")
        self.conn.execute("PRAGMA journal_mode = WAL")
        self._create()

    def _create(self):
        self.conn.executescript(
            """
            CREATE TABLE IF NOT EXISTS chapters (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                order_index INTEGER NOT NULL,
                title_fa TEXT NOT NULL,
                title_en TEXT DEFAULT '',
                description TEXT DEFAULT ''
            );
            CREATE TABLE IF NOT EXISTS levels (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                chapter_id INTEGER NOT NULL,
                order_index INTEGER NOT NULL,
                title_fa TEXT NOT NULL,
                title_en TEXT DEFAULT '',
                FOREIGN KEY (chapter_id) REFERENCES chapters(id) ON DELETE CASCADE
            );
            CREATE TABLE IF NOT EXISTS lessons (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                level_id INTEGER NOT NULL,
                order_index INTEGER NOT NULL,
                title_fa TEXT NOT NULL,
                title_en TEXT DEFAULT '',
                tags TEXT DEFAULT '',
                summary TEXT DEFAULT '',
                full_content TEXT DEFAULT '',
                commands TEXT DEFAULT '',
                examples TEXT DEFAULT '',
                notes TEXT DEFAULT '',
                meta_json TEXT DEFAULT '{}',
                search_query TEXT DEFAULT '',
                learning_objectives TEXT DEFAULT '',
                source_status TEXT DEFAULT 'unverified',
                last_updated TEXT,
                FOREIGN KEY (level_id) REFERENCES levels(id) ON DELETE CASCADE
            );
            CREATE TABLE IF NOT EXISTS scenarios (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                code TEXT UNIQUE,
                title_fa TEXT NOT NULL,
                title_en TEXT,
                category TEXT DEFAULT 'Capstone',
                level TEXT DEFAULT 'L4',
                difficulty TEXT DEFAULT 'خبره',
                users INTEGER DEFAULT 0,
                sites INTEGER DEFAULT 1,
                vendors TEXT DEFAULT '',
                business_context TEXT DEFAULT '',
                requirements TEXT DEFAULT '',
                constraints_text TEXT DEFAULT '',
                initial_state TEXT DEFAULT '',
                incident TEXT DEFAULT '',
                symptoms TEXT DEFAULT '',
                objectives TEXT DEFAULT '',
                tasks TEXT DEFAULT '',
                hints TEXT DEFAULT '',
                expected_result TEXT DEFAULT '',
                solution TEXT DEFAULT '',
                verification TEXT DEFAULT '',
                skills_required TEXT DEFAULT '',
                estimated_hours INTEGER DEFAULT 8,
                last_updated TEXT
            );
            CREATE TABLE IF NOT EXISTS meta (
                key TEXT PRIMARY KEY,
                value TEXT
            );
            CREATE INDEX IF NOT EXISTS idx_levels_ch ON levels(chapter_id);
            CREATE INDEX IF NOT EXISTS idx_lessons_lv ON lessons(level_id);
            """
        )
        self.conn.commit()

    def get_meta(self, key, default=None):
        r = self.conn.execute("SELECT value FROM meta WHERE key=?", (key,)).fetchone()
        return r["value"] if r else default

    def set_meta(self, key, value):
        self.conn.execute(
            "INSERT INTO meta(key,value) VALUES(?,?) ON CONFLICT(key) DO UPDATE SET value=excluded.value",
            (key, value),
        )
        self.conn.commit()

    def chapter_count(self):
        return self.conn.execute("SELECT COUNT(*) c FROM chapters").fetchone()["c"]

    def is_seeded(self):
        return self.chapter_count() >= 64


    @staticmethod
    def _curriculum_family(label):
        value = str(label or "").casefold()
        groups = (
            ("mikrotik", ("mikrotik", "routeros")),
            ("fortigate", ("fortigate", "forti")),
            ("cisco", ("cisco", "ios/ios", "ios-xe", "ios xe")),
            ("powershell", ("powershell", "power shell")),
            ("batch", ("batch",)),
            ("cmd", ("windows cmd", "command prompt", "cmd")),
            ("linux", ("linux", "bash")),
            ("asterisk", ("asterisk", "issabel")),
        )
        for family, terms in groups:
            if any(term in value for term in terms):
                return family
        return ""

    def _merge_missing_curriculum_from_asset(self):
        """Add new curriculum rows by stable UID; never delete or overwrite existing lesson content."""
        asset = BASE.parent / "android" / "app" / "src" / "main" / "assets" / "curriculum_index.json.gz"
        try:
            with gzip.open(asset, "rt", encoding="utf-8") as stream:
                payload = json.load(stream)
            chapters = payload.get("chapters", [])
            if not isinstance(chapters, list):
                return 0
            self.ensure_sync_columns()
            now = datetime.now().astimezone().isoformat(timespec="seconds")
            inserted = 0
            cur = self.conn.cursor()
            for chapter in sorted(chapters, key=lambda x: int(x.get("order") or 0)):
                order = int(chapter.get("order") or 0)
                title_fa = str(chapter.get("title_fa") or f"فصل {order}")
                title_en = str(chapter.get("title_en") or "")
                row = cur.execute("SELECT id FROM chapters WHERE order_index=? ORDER BY id LIMIT 1", (order,)).fetchone()
                if row:
                    chapter_id = row["id"]
                    cur.execute("UPDATE chapters SET title_fa=?, title_en=? WHERE id=?", (title_fa, title_en, chapter_id))
                else:
                    cur.execute("INSERT INTO chapters(order_index,title_fa,title_en) VALUES(?,?,?)", (order,title_fa,title_en))
                    chapter_id = cur.lastrowid
                levels_db = cur.execute("SELECT id,order_index,title_fa FROM levels WHERE chapter_id=? ORDER BY order_index,id", (chapter_id,)).fetchall()
                claimed_level_ids = set()
                for sub in chapter.get("subchapters", []):
                    if not isinstance(sub, dict):
                        continue
                    sub_title = str(sub.get("title_fa") or "زیرشاخهٔ بدون عنوان").strip()
                    sub_en = str(sub.get("title_en") or "")
                    target = next((r for r in levels_db if r["id"] not in claimed_level_ids and str(r["title_fa"]).strip() == sub_title), None)
                    sub_family = self._curriculum_family(sub_title)
                    if target is None and sub_family:
                        target = next((r for r in levels_db if r["id"] not in claimed_level_ids and self._curriculum_family(r["title_fa"]) == sub_family), None)
                    if target is not None:
                        level_id = target["id"]
                        claimed_level_ids.add(level_id)
                        cur.execute("UPDATE levels SET title_fa=?, title_en=? WHERE id=?", (sub_title, sub_en, level_id))
                    else:
                        next_order = cur.execute("SELECT COALESCE(MAX(order_index),0)+1 AS n FROM levels WHERE chapter_id=?", (chapter_id,)).fetchone()["n"]
                        cur.execute("INSERT INTO levels(chapter_id,order_index,title_fa,title_en) VALUES(?,?,?,?)", (chapter_id,next_order,sub_title,sub_en))
                        level_id = cur.lastrowid
                        claimed_level_ids.add(level_id)
                    for item in sub.get("lessons", []):
                        if not isinstance(item, dict):
                            continue
                        uid = str(item.get("uid") or "").strip()
                        if uid and cur.execute("SELECT 1 FROM lessons WHERE uid=? LIMIT 1", (uid,)).fetchone():
                            continue
                        lfa = str(item.get("title_fa") or "").strip()
                        len_ = str(item.get("title_en") or lfa).strip()
                        if not lfa:
                            continue
                        oi = cur.execute("SELECT COALESCE(MAX(order_index),0)+1 AS n FROM lessons WHERE level_id=?", (level_id,)).fetchone()["n"]
                        tag = str(item.get("level") or (lfa[1:3] if lfa.startswith("[L") else "L0"))
                        summary = str(item.get("summary") or "")
                        full_content = str(item.get("full_content") or summary)
                        commands, examples, notes = (str(item.get(k) or "") for k in ("commands","examples","notes"))
                        meta = item.get("meta") if isinstance(item.get("meta"), dict) else {}
                        meta_json = json.dumps(meta, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
                        objectives = item.get("learning_objectives") or []
                        if not isinstance(objectives, list):
                            objectives = [str(objectives)]
                        objectives_text = "\n".join(str(x) for x in objectives)
                        search_keywords = item.get("search_keywords") or []
                        search_query = str(item.get("search_query") or " ".join(str(x) for x in search_keywords))
                        source_status = str(item.get("source_status") or "review_required")
                        record_uid = uid or f"lesson:ch{order:02d}:incremental:{level_id}:{oi:05d}"
                        content_fields = {"uid":record_uid,"entity":"lesson","title_fa":lfa,"title_en":len_,"tags":tag,
                            "summary":summary,"full_content":full_content,"commands":commands,"examples":examples,"notes":notes,
                            "meta_json":meta_json,"search_query":search_query,"learning_objectives":objectives_text,
                            "source_status":source_status,"deleted":False}
                        digest = hashlib.sha256(json.dumps(content_fields,ensure_ascii=False,sort_keys=True,separators=(",",":")).encode("utf-8")).hexdigest()
                        cur.execute("""INSERT INTO lessons(
                            level_id,order_index,title_fa,title_en,tags,summary,full_content,commands,examples,notes,
                            meta_json,search_query,learning_objectives,source_status,last_updated,uid,content_hash,device_id,deleted
                            ) VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
                            (level_id,oi,lfa,len_,tag,summary,full_content,commands,examples,notes,meta_json,search_query,
                             objectives_text,source_status,str(item.get("last_updated") or payload.get("generated_at") or now),
                             record_uid,digest,"windows-curriculum-merge",0))
                        inserted += 1
            self.conn.commit()
            return inserted
        except (OSError, ValueError, TypeError, KeyError, sqlite3.Error) as exc:
            print("incremental curriculum merge skipped:", exc)
            return 0

    def seed_full(self, force=False):
        """Seed from the validated shared curriculum asset when available.

        A release package embeds the same merged index as Android. This avoids
        seeding a shallow, different 68-chapter tree on Windows. A legacy
        title-generated fallback remains for source checkouts without an asset.
        """
        if self.is_seeded() and not force:
            inserted = self._merge_missing_curriculum_from_asset()
            return {"ok": True, "skipped": True, "chapters": self.chapter_count(), "new_lessons": inserted}

        from core.phase_a import CAPSTONE_SCENARIOS
        from core.seed_helpers import insert_rich_lesson

        cur = self.conn.cursor()
        self.ensure_sync_columns()
        if force:
            cur.executescript(
                "DELETE FROM lessons; DELETE FROM levels; DELETE FROM chapters; DELETE FROM scenarios;"
            )

        now = datetime.now().astimezone().isoformat(timespec="seconds")
        curriculum = []
        rich_lookup = {}
        source = "legacy-fallback"

        asset = BASE.parent / "android" / "app" / "src" / "main" / "assets" / "curriculum_index.json.gz"
        try:
            with gzip.open(asset, "rt", encoding="utf-8") as stream:
                payload = json.load(stream)
            chapters = payload.get("chapters")
            orders = {int(ch.get("order", 0)) for ch in chapters or []}
            actual_count = sum(
                len(sub.get("lessons", []))
                for ch in chapters or []
                for sub in ch.get("subchapters", [])
            )
            if (
                isinstance(chapters, list)
                and set(range(1, 69)).issubset(orders)
                and int(payload.get("lesson_count", -1)) == actual_count
            ):
                seen_uids = set()
                for chapter in sorted(chapters, key=lambda x: int(x["order"])):
                    order = int(chapter["order"])
                    levels = []
                    for si, sub in enumerate(chapter.get("subchapters", []), 1):
                        lessons = []
                        for oi, item in enumerate(sub.get("lessons", []), 1):
                            title_fa = str(item.get("title_fa") or "").strip()
                            title_en = str(item.get("title_en") or title_fa).strip()
                            uid = str(item.get("uid") or f"lesson:ch{order:02d}:s{si:03d}:l{oi:04d}")
                            if not title_fa or uid in seen_uids:
                                raise ValueError(f"invalid/duplicate lesson title or uid in chapter {order}: {uid}")
                            seen_uids.add(uid)
                            rich_lookup[(order, si, oi)] = item
                            lessons.append((title_fa, title_en))
                        levels.append((str(sub.get("title_fa") or f"زیرفصل {si}"), lessons))
                    curriculum.append((
                        order,
                        str(chapter.get("title_fa") or f"فصل {order}"),
                        str(chapter.get("title_en") or ""),
                        levels,
                    ))
                source = "shared-android-curriculum"
        except FileNotFoundError:
            pass
        except Exception as e:
            print("shared curriculum asset rejected; using legacy fallback:", e)
            curriculum = []
            rich_lookup = {}

        if not curriculum:
            from core.full_curriculum import get_full_curriculum
            curriculum = list(get_full_curriculum())
            try:
                from core.extra_chapters import ensure_chapters_1_to_68
                curriculum = ensure_chapters_1_to_68(curriculum)
            except Exception as e:
                print("extra_chapters", e)

        n_ch = n_lv = n_les = 0
        for order, title_fa, title_en, levels in curriculum:
            cur.execute(
                "INSERT INTO chapters(order_index, title_fa, title_en) VALUES (?,?,?)",
                (order, title_fa, title_en),
            )
            ch_id = cur.lastrowid
            n_ch += 1
            for li, level_data in enumerate(levels, 1):
                lv_title, lessons = level_data[0], level_data[1]
                lv_title_en = level_data[2] if len(level_data) > 2 else ""
                cur.execute(
                    "INSERT INTO levels(chapter_id, order_index, title_fa, title_en) VALUES (?,?,?,?)",
                    (ch_id, li, lv_title, lv_title_en),
                )
                lv_id = cur.lastrowid
                n_lv += 1
                for oi, (lfa, len_) in enumerate(lessons, 1):
                    record = rich_lookup.get((int(order), li, oi))
                    if record is None:
                        insert_rich_lesson(cur, lv_id, oi, lfa, len_, now)
                    else:
                        meta = record.get("meta") if isinstance(record.get("meta"), dict) else {}
                        meta_json = json.dumps(meta, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
                        objectives = record.get("learning_objectives") or []
                        if not isinstance(objectives, list):
                            objectives = [str(objectives)]
                        objectives_text = "\n".join(str(x) for x in objectives)
                        search_keywords = record.get("search_keywords") or []
                        search_query = str(record.get("search_query") or " ".join(str(x) for x in search_keywords))
                        source_status = str(record.get("source_status") or "review_required")
                        level_tag = str(record.get("level") or "L0")
                        uid = str(record.get("uid") or f"lesson:ch{int(order):02d}:s{li:03d}:l{oi:04d}")
                        content_fields = {
                            "uid": uid,
                            "entity": "lesson",
                            "title_fa": lfa,
                            "title_en": len_,
                            "tags": level_tag,
                            "summary": str(record.get("summary") or ""),
                            "full_content": str(record.get("full_content") or ""),
                            "commands": str(record.get("commands") or ""),
                            "examples": str(record.get("examples") or ""),
                            "notes": str(record.get("notes") or ""),
                            "meta_json": meta_json,
                            "search_query": search_query,
                            "learning_objectives": objectives_text,
                            "source_status": source_status,
                            "deleted": False,
                        }
                        # Same canonical payload as shared.sync_engine.content_hash and Android.
                        digest = hashlib.sha256(
                            json.dumps(content_fields, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")
                        ).hexdigest()
                        cur.execute(
                            """INSERT INTO lessons(
                                level_id, order_index, title_fa, title_en, tags, summary,
                                full_content, commands, examples, notes, meta_json, search_query,
                                learning_objectives, source_status, last_updated, uid, content_hash,
                                device_id, deleted
                            ) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
                            (
                                lv_id, oi, lfa, len_, str(record.get("level") or "L0"),
                                content_fields["summary"], content_fields["full_content"],
                                content_fields["commands"], content_fields["examples"], content_fields["notes"],
                                meta_json,
                                search_query,
                                objectives_text,
                                source_status,
                                str(record.get("last_updated") or payload.get("generated_at") or now),
                                uid,
                                digest, "windows-seed-v1", 0,
                            ),
                        )
                    n_les += 1

        for sc in CAPSTONE_SCENARIOS:
            cur.execute(
                """INSERT OR REPLACE INTO scenarios(
                    code, title_fa, title_en, category, level, difficulty,
                    users, sites, vendors, business_context, requirements,
                    constraints_text, initial_state, incident, symptoms,
                    objectives, tasks, hints, expected_result, solution,
                    verification, skills_required, estimated_hours, last_updated
                ) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
                (
                    sc["code"], sc["title_fa"], sc["title_en"], sc["category"],
                    sc["level"], sc["difficulty"], sc["users"], sc["sites"],
                    sc["vendors"], sc["business_context"], sc["requirements"],
                    sc["constraints"], sc["initial_state"], sc["incident"],
                    sc["symptoms"], sc["objectives"], sc["tasks"], sc["hints"],
                    sc["expected_result"], sc["solution"], sc["verification"],
                    sc["skills_required"], sc["estimated_hours"], now,
                ),
            )

        self.conn.commit()
        self.set_meta("seeded_version", "networkall-v1.0.0" if source == "shared-android-curriculum" else "web-v3-ch68")
        self.set_meta("seeded_at", now)
        return {
            "ok": True, "chapters": n_ch, "levels": n_lv, "lessons": n_les,
            "scenarios": len(CAPSTONE_SCENARIOS), "curriculum_source": source,
        }

    def list_chapters(self):
        rows = self.conn.execute(
            "SELECT id, order_index, title_fa, title_en FROM chapters ORDER BY order_index, id"
        ).fetchall()
        return [dict(r) for r in rows]

    def get_chapter(self, chapter_id: int):
        r = self.conn.execute("SELECT * FROM chapters WHERE id=?", (chapter_id,)).fetchone()
        return dict(r) if r else None

    def list_levels(self, chapter_id: int):
        rows = self.conn.execute(
            "SELECT id, order_index, title_fa, title_en FROM levels WHERE chapter_id=? ORDER BY order_index, id",
            (chapter_id,),
        ).fetchall()
        return [dict(r) for r in rows]

    def list_lessons(self, level_id: int):
        rows = self.conn.execute(
            """SELECT id, order_index, title_fa, title_en, tags,
                      CASE WHEN length(COALESCE(full_content,''))>50 THEN 1 ELSE 0 END AS has_content
               FROM lessons WHERE level_id=? ORDER BY order_index, id""",
            (level_id,),
        ).fetchall()
        return [dict(r) for r in rows]

    def get_lesson(self, lesson_id: int):
        r = self.conn.execute("SELECT * FROM lessons WHERE id=?", (lesson_id,)).fetchone()
        if not r:
            return None
        d = dict(r)
        try:
            d["meta"] = json.loads(d.get("meta_json") or "{}")
        except Exception:
            d["meta"] = {}
        return d

    def list_scenarios(self):
        rows = self.conn.execute(
            "SELECT id, code, title_fa, category, level, difficulty, users, sites, estimated_hours FROM scenarios ORDER BY code"
        ).fetchall()
        return [dict(r) for r in rows]

    def get_scenario(self, scenario_id: int):
        r = self.conn.execute("SELECT * FROM scenarios WHERE id=?", (scenario_id,)).fetchone()
        return dict(r) if r else None

    def search(self, q: str, limit=50):
        q = (q or "").strip()
        if not q:
            return []
        like = f"%{q}%"
        rows = self.conn.execute(
            """SELECT l.id, l.title_fa, l.tags, lv.title_fa AS level_title, c.title_fa AS chapter_title, c.id AS chapter_id
               FROM lessons l
               JOIN levels lv ON lv.id=l.level_id
               JOIN chapters c ON c.id=lv.chapter_id
               WHERE l.title_fa LIKE ? OR l.summary LIKE ? OR l.full_content LIKE ?
               ORDER BY c.order_index, lv.order_index, l.order_index LIMIT ?""",
            (like, like, like, limit),
        ).fetchall()
        return [dict(r) for r in rows]

    def stats(self):
        return {
            "chapters": self.conn.execute("SELECT COUNT(*) c FROM chapters").fetchone()["c"],
            "levels": self.conn.execute("SELECT COUNT(*) c FROM levels").fetchone()["c"],
            "lessons": self.conn.execute("SELECT COUNT(*) c FROM lessons").fetchone()["c"],
            "scenarios": self.conn.execute("SELECT COUNT(*) c FROM scenarios").fetchone()["c"],
            "with_content": self.conn.execute(
                "SELECT COUNT(*) c FROM lessons WHERE length(COALESCE(full_content,''))>50"
            ).fetchone()["c"],
        }

    def ensure_sync_columns(self):
        cols = [
            ("lessons", "uid", "TEXT"),
            ("lessons", "content_hash", "TEXT DEFAULT ''"),
            ("lessons", "device_id", "TEXT DEFAULT ''"),
            ("lessons", "deleted", "INTEGER DEFAULT 0"),
            ("scenarios", "uid", "TEXT"),
            ("scenarios", "content_hash", "TEXT DEFAULT ''"),
            ("scenarios", "device_id", "TEXT DEFAULT ''"),
            ("scenarios", "deleted", "INTEGER DEFAULT 0"),
        ]
        for table, col, defn in cols:
            try:
                self.conn.execute(f"ALTER TABLE {table} ADD COLUMN {col} {defn}")
                self.conn.commit()
            except Exception:
                pass
        rows = self.conn.execute(
            """SELECT l.id, c.order_index AS co, lv.order_index AS lo, l.order_index AS o
               FROM lessons l JOIN levels lv ON lv.id=l.level_id JOIN chapters c ON c.id=lv.chapter_id
               WHERE l.uid IS NULL OR l.uid=''"""
        ).fetchall()
        for r in rows:
            uid = f"lesson:ch{int(r['co']):02d}:lv{int(r['lo']):03d}:l{int(r['o']):04d}"
            self.conn.execute("UPDATE lessons SET uid=? WHERE id=?", (uid, r["id"]))
        for r in self.conn.execute("SELECT id, code FROM scenarios WHERE uid IS NULL OR uid=''").fetchall():
            self.conn.execute("UPDATE scenarios SET uid=? WHERE id=?", (f"scenario:{r['code']}", r["id"]))
        self.conn.commit()

    def sync_index(self):
        self.ensure_sync_columns()
        out = []
        for r in self.conn.execute(
            "SELECT uid, last_updated, content_hash, COALESCE(deleted,0) AS deleted FROM lessons WHERE uid IS NOT NULL AND uid!=''"
        ).fetchall():
            out.append({"uid": r["uid"], "entity": "lesson", "last_updated": r["last_updated"] or "",
                        "content_hash": r["content_hash"] or "", "deleted": bool(r["deleted"])})
        for r in self.conn.execute(
            "SELECT uid, last_updated, content_hash, COALESCE(deleted,0) AS deleted FROM scenarios WHERE uid IS NOT NULL AND uid!=''"
        ).fetchall():
            out.append({"uid": r["uid"], "entity": "scenario", "last_updated": r["last_updated"] or "",
                        "content_hash": r["content_hash"] or "", "deleted": bool(r["deleted"])})
        return out

    def sync_pull(self, uids):
        if not uids:
            return []
        self.ensure_sync_columns()
        qmarks = ",".join("?" * len(uids))
        out = []
        for r in self.conn.execute(
            f"""SELECT uid, title_fa, title_en, tags, summary, full_content, commands, examples, notes,
                       meta_json, search_query, learning_objectives, source_status, last_updated,
                       content_hash, device_id, COALESCE(deleted,0) AS deleted
                FROM lessons WHERE uid IN ({qmarks})""", list(uids)).fetchall():
            d = dict(r)
            d["entity"] = "lesson"
            d["deleted"] = bool(d.get("deleted"))
            out.append(d)
        for r in self.conn.execute(f"SELECT * FROM scenarios WHERE uid IN ({qmarks})", list(uids)).fetchall():
            d = dict(r)
            d["entity"] = "scenario"
            d["deleted"] = bool(d.get("deleted"))
            out.append(d)
        return out

    def sync_apply(self, records):
        self.ensure_sync_columns()
        for rec in records:
            uid = rec.get("uid") or ""
            entity = rec.get("entity") or ("scenario" if uid.startswith("scenario:") else "lesson")
            if entity == "lesson":
                if not self.conn.execute("SELECT id FROM lessons WHERE uid=?", (uid,)).fetchone():
                    continue
                self.conn.execute(
                    """UPDATE lessons SET summary=?, full_content=?, commands=?, examples=?, notes=?,
                       meta_json=?, search_query=?, learning_objectives=?, source_status=?,
                       last_updated=?, content_hash=?, device_id=?, deleted=? WHERE uid=?""",
                    (rec.get("summary", ""), rec.get("full_content", ""), rec.get("commands", ""),
                     rec.get("examples", ""), rec.get("notes", ""), rec.get("meta_json", "{}"),
                     rec.get("search_query", ""), rec.get("learning_objectives", ""),
                     rec.get("source_status", "unverified"), rec.get("last_updated"),
                     rec.get("content_hash", ""), rec.get("device_id", ""),
                     1 if rec.get("deleted") else 0, uid),
                )
            elif entity == "scenario":
                if not self.conn.execute("SELECT id FROM scenarios WHERE uid=?", (uid,)).fetchone():
                    continue
                self.conn.execute(
                    """UPDATE scenarios SET title_fa=?, tasks=?, solution=?, verification=?,
                       last_updated=?, content_hash=?, device_id=?, deleted=? WHERE uid=?""",
                    (rec.get("title_fa") or "", rec.get("tasks", ""), rec.get("solution", ""),
                     rec.get("verification", ""), rec.get("last_updated"), rec.get("content_hash", ""),
                     rec.get("device_id", ""), 1 if rec.get("deleted") else 0, uid),
                )
        self.conn.commit()
