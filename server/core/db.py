# -*- coding: utf-8 -*-
"""SQLite سبک برای نسخه وب — فصل‌های ۱–۶۸ با محتوای غنی."""
from __future__ import annotations

import gzip
import json
import sqlite3
import re
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
        self.conn.execute("PRAGMA journal_mode=WAL")
        self.conn.execute("PRAGMA busy_timeout=5000")
        self.conn.execute("PRAGMA journal_mode = WAL")
        self._create()
        self._ensure_search_index()

    def _ensure_search_index(self):
        """Create a maintained FTS5 index when SQLite supports it; LIKE remains fallback."""
        try:
            self.conn.executescript(
                """
                CREATE VIRTUAL TABLE IF NOT EXISTS lessons_fts USING fts5(
                    title_fa, title_en, tags, summary, full_content, commands, examples,
                    content='lessons', content_rowid='id', tokenize='unicode61'
                );
                CREATE TRIGGER IF NOT EXISTS lessons_fts_ai AFTER INSERT ON lessons BEGIN
                    INSERT INTO lessons_fts(rowid, title_fa, title_en, tags, summary, full_content, commands, examples)
                    VALUES (new.id, new.title_fa, new.title_en, new.tags, new.summary, new.full_content, new.commands, new.examples);
                END;
                CREATE TRIGGER IF NOT EXISTS lessons_fts_ad AFTER DELETE ON lessons BEGIN
                    INSERT INTO lessons_fts(lessons_fts, rowid, title_fa, title_en, tags, summary, full_content, commands, examples)
                    VALUES ('delete', old.id, old.title_fa, old.title_en, old.tags, old.summary, old.full_content, old.commands, old.examples);
                END;
                CREATE TRIGGER IF NOT EXISTS lessons_fts_au AFTER UPDATE ON lessons BEGIN
                    INSERT INTO lessons_fts(lessons_fts, rowid, title_fa, title_en, tags, summary, full_content, commands, examples)
                    VALUES ('delete', old.id, old.title_fa, old.title_en, old.tags, old.summary, old.full_content, old.commands, old.examples);
                    INSERT INTO lessons_fts(rowid, title_fa, title_en, tags, summary, full_content, commands, examples)
                    VALUES (new.id, new.title_fa, new.title_en, new.tags, new.summary, new.full_content, new.commands, new.examples);
                END;
                """
            )
            if self.get_meta("search_fts_ready") != "1":
                self.conn.execute("INSERT INTO lessons_fts(lessons_fts) VALUES ('rebuild')")
                self.set_meta("search_fts_ready", "1")
            self._fts_available = True
        except sqlite3.OperationalError as exc:
            # Some bundled SQLite builds may omit FTS5; the app remains functional.
            self._fts_available = False
            print("FTS5 unavailable; using LIKE search fallback:", exc)


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

    def backup(self, backup_dir=None):
        """Create a consistent SQLite backup before destructive maintenance."""
        directory = Path(backup_dir) if backup_dir else self.path.parent / "backups"
        directory.mkdir(parents=True, exist_ok=True)
        stamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
        target = directory / f"{self.path.stem}_{stamp}.db"
        with sqlite3.connect(str(target)) as destination:
            self.conn.backup(destination)
        return target

    def _load_merged_curriculum_index(self):
        """Read the same merged curriculum index shipped to Windows and Android.

        This is only used on a seed operation. Existing seeded databases return
        early in seed_full(), preserving notes, progress, and synced user data.
        """
        package_root = BASE.parent
        candidates = (
            package_root / "shared" / "curriculum_index.json.gz",
            package_root / "android" / "app" / "src" / "main" / "assets" / "curriculum_index.json.gz",
        )
        for path in candidates:
            if not path.is_file():
                continue
            try:
                with gzip.open(path, "rt", encoding="utf-8") as stream:
                    payload = json.load(stream)
                chapters = payload.get("chapters")
                orders = {int(ch.get("order", 0)) for ch in chapters or [] if isinstance(ch, dict)}
                if isinstance(chapters, list) and len(orders) >= 64 and 68 in orders:
                    return payload
                print(f"Ignoring incomplete curriculum index: {path}")
            except (OSError, EOFError, ValueError, TypeError) as exc:
                print(f"Could not load curriculum index {path}: {exc}")
        return None

    def seed_full(self, force=False):
        """ساخت کامل فصل‌های ۱–۶۸ با محتوای غنی."""
        if self.is_seeded() and not force:
            return {"ok": True, "skipped": True, "chapters": self.chapter_count()}

        from core.full_curriculum import get_full_curriculum
        from core.phase_a import CAPSTONE_SCENARIOS, default_meta
        from core.seed_helpers import insert_rich_lesson

        backup_path = None
        cur = self.conn.cursor()
        if force:
            backup_path = self.backup()
            cur.executescript(
                "DELETE FROM lessons; DELETE FROM levels; DELETE FROM chapters; DELETE FROM scenarios;"
            )

        merged_index = self._load_merged_curriculum_index()
        n_ch = n_lv = n_les = 0
        now = datetime.now().isoformat()

        if merged_index:
            # Fresh installs consume the exact same merged index packaged for Android.
            for ch in sorted(merged_index.get("chapters") or [], key=lambda item: int(item.get("order", 0))):
                order = int(ch.get("order", 0))
                title_fa = str(ch.get("title_fa") or f"فصل {order}")
                title_en = str(ch.get("title_en") or "")
                cur.execute(
                    "INSERT INTO chapters(order_index, title_fa, title_en) VALUES (?,?,?)",
                    (order, title_fa, title_en),
                )
                ch_id = cur.lastrowid
                n_ch += 1
                for li, sub in enumerate(ch.get("subchapters") or [], 1):
                    sub_fa = str(sub.get("title_fa") or f"بخش {li}")
                    sub_en = str(sub.get("title_en") or "")
                    cur.execute(
                        "INSERT INTO levels(chapter_id, order_index, title_fa, title_en) VALUES (?,?,?,?)",
                        (ch_id, li, sub_fa, sub_en),
                    )
                    lv_id = cur.lastrowid
                    n_lv += 1
                    for oi, lesson in enumerate(sub.get("lessons") or [], 1):
                        if not isinstance(lesson, dict):
                            continue
                        meta_raw = lesson.get("meta_json")
                        if isinstance(meta_raw, dict):
                            meta_value = json.dumps(meta_raw, ensure_ascii=False)
                            meta_obj = meta_raw
                        else:
                            meta_value = str(meta_raw or "{}")
                            try:
                                meta_obj = json.loads(meta_value)
                                if not isinstance(meta_obj, dict):
                                    meta_obj = {}
                            except (TypeError, ValueError):
                                meta_obj = {}
                                meta_value = "{}"
                        objectives = lesson.get("learning_objectives") or ""
                        if isinstance(objectives, (list, tuple)):
                            objectives = "؛".join(str(value) for value in objectives)
                        tags = " ".join(
                            str(value) for value in (
                                meta_obj.get("category"), meta_obj.get("topic"),
                                meta_obj.get("level") or lesson.get("level"),
                            ) if value
                        )
                        title = str(lesson.get("title_fa") or lesson.get("title_en") or f"درس {oi}")
                        cur.execute(
                            """INSERT INTO lessons(
                                level_id, order_index, title_fa, title_en, tags, summary,
                                full_content, commands, examples, notes, meta_json, search_query,
                                learning_objectives, source_status, last_updated
                            ) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
                            (
                                lv_id, oi, title, str(lesson.get("title_en") or ""), tags,
                                str(lesson.get("summary") or ""), str(lesson.get("full_content") or ""),
                                str(lesson.get("commands") or ""), str(lesson.get("examples") or ""),
                                str(lesson.get("notes") or ""), meta_value,
                                str(lesson.get("search_query") or ""), str(objectives),
                                str(lesson.get("source_status") or "review_required"),
                                str(lesson.get("last_updated") or now),
                            ),
                        )
                        n_les += 1
            if n_ch < 64 or n_les == 0:
                raise RuntimeError(
                    f"Merged curriculum index appears incomplete (chapters={n_ch}, lessons={n_les}); "
                    "refusing to mark the database as seeded."
                )
            print(f"Seeded from shared merged curriculum index: chapters={n_ch}, lessons={n_les}")
        else:
            # Source-only/developer checkouts without the shared artifact use the core curriculum.
            curriculum = get_full_curriculum()
            try:
                from core.extra_chapters import ensure_chapters_1_to_68
                curriculum = ensure_chapters_1_to_68(list(curriculum))
            except Exception as e:
                print("extra_chapters", e)
            for order, title_fa, title_en, levels in curriculum:
                cur.execute(
                    "INSERT INTO chapters(order_index, title_fa, title_en) VALUES (?,?,?)",
                    (order, title_fa, title_en),
                )
                ch_id = cur.lastrowid
                n_ch += 1
                for li, (lv_title, lessons) in enumerate(levels, 1):
                    cur.execute(
                        "INSERT INTO levels(chapter_id, order_index, title_fa) VALUES (?,?,?)",
                        (ch_id, li, lv_title),
                    )
                    lv_id = cur.lastrowid
                    n_lv += 1
                    for oi, (lfa, len_) in enumerate(lessons, 1):
                        insert_rich_lesson(cur, lv_id, oi, lfa, len_, now)
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
        self.set_meta("seeded_version", "web-v3-ch68")
        self.set_meta("seeded_at", now)
        return {"ok": True, "chapters": n_ch, "levels": n_lv, "lessons": n_les, "scenarios": len(CAPSTONE_SCENARIOS), "backup": str(backup_path) if backup_path else None}

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
        try:
            limit = max(1, min(int(limit), 100))
        except (TypeError, ValueError):
            limit = 50

        # FTS5 is much faster than scanning every long lesson body with LIKE.
        # Tokenize conservatively and quote each token to avoid interpreting user
        # input as FTS operators. Prefix matching supports partial English words.
        tokens = re.findall(r"[\w\u0600-\u06FF]+", q, flags=re.UNICODE)
        if self._fts_available and tokens:
            match_query = " AND ".join('"' + t.replace('"', '""') + '"*' for t in tokens)
            try:
                rows = self.conn.execute(
                    """SELECT l.id, l.title_fa, l.tags, lv.title_fa AS level_title,
                              c.title_fa AS chapter_title, c.id AS chapter_id
                       FROM lessons_fts
                       JOIN lessons l ON l.id=lessons_fts.rowid
                       JOIN levels lv ON lv.id=l.level_id
                       JOIN chapters c ON c.id=lv.chapter_id
                       WHERE lessons_fts MATCH ?
                       ORDER BY bm25(lessons_fts), c.order_index, lv.order_index, l.order_index
                       LIMIT ?""",
                    (match_query, limit),
                ).fetchall()
                return [dict(r) for r in rows]
            except sqlite3.OperationalError:
                pass

        like = f"%{q}%"
        rows = self.conn.execute(
            """SELECT l.id, l.title_fa, l.tags, lv.title_fa AS level_title,
                      c.title_fa AS chapter_title, c.id AS chapter_id
               FROM lessons l
               JOIN levels lv ON lv.id=l.level_id
               JOIN chapters c ON c.id=lv.chapter_id
               WHERE l.title_fa LIKE ? OR l.title_en LIKE ? OR l.tags LIKE ?
                  OR l.summary LIKE ? OR l.full_content LIKE ? OR l.commands LIKE ?
               ORDER BY c.order_index, lv.order_index, l.order_index LIMIT ?""",
            (like, like, like, like, like, like, limit),
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
            d = dict(r); d["entity"] = "lesson"; out.append(d)
        for r in self.conn.execute(f"SELECT * FROM scenarios WHERE uid IN ({qmarks})", list(uids)).fetchall():
            d = dict(r); d["entity"] = "scenario"; out.append(d)
        return out

    def sync_apply(self, records):
        self.ensure_sync_columns()
        applied = 0
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
                applied += 1
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
                applied += 1
        self.conn.commit()
        return applied
