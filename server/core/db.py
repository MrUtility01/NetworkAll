# -*- coding: utf-8 -*-
"""SQLite سبک برای نسخه وب — فصل‌های ۱–۶۸ با محتوای غنی."""
from __future__ import annotations

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

    def seed_full(self, force=False):
        """ساخت کامل فصل‌های ۱–۶۸ با محتوای غنی."""
        if self.is_seeded() and not force:
            return {"ok": True, "skipped": True, "chapters": self.chapter_count()}

        from core.full_curriculum import get_full_curriculum
        from core.phase_a import CAPSTONE_SCENARIOS, default_meta
        from core.seed_helpers import insert_rich_lesson

        cur = self.conn.cursor()
        if force:
            cur.executescript(
                "DELETE FROM lessons; DELETE FROM levels; DELETE FROM chapters; DELETE FROM scenarios;"
            )

        curriculum = get_full_curriculum()
        try:
            from core.extra_chapters import ensure_chapters_1_to_68
            curriculum = ensure_chapters_1_to_68(list(curriculum))
        except Exception as e:
            print("extra_chapters", e)
        n_ch = n_lv = n_les = 0
        now = datetime.now().isoformat()

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
        return {"ok": True, "chapters": n_ch, "levels": n_lv, "lessons": n_les, "scenarios": len(CAPSTONE_SCENARIOS)}


    def ensure_ch60_68_deep_lessons(self):
        """Idempotently add the shared deep lesson pack to an existing Windows DB without deleting user data."""
        pack_dir = BASE.parent / "tools" / "packs" / "ch60_68"
        base_pack = pack_dir / "chapter_60_68_deep_pack.json"
        pack_paths = [base_pack] + [
            path for path in sorted(pack_dir.glob("*pack*.json")) if path != base_pack
        ]
        if not pack_paths[0].is_file():
            return {"ok": False, "reason": "chapter 60-68 pack missing"}
        items = []
        for pack_path in pack_paths:
            if not pack_path.is_file():
                continue
            try:
                pack = json.loads(pack_path.read_text(encoding="utf-8"))
                raw_items = pack.get("lessons") or []
                if pack_path == base_pack and len(raw_items) < 250:
                    return {"ok": False, "reason": f"expected >=250 lessons; found {len(raw_items)}"}
                pack_items = [
                    item for item in raw_items
                    if isinstance(item, dict)
                    and item.get("title_fa")
                    and item.get("full_content")
                    and 60 <= int(item.get("chapter_order") or 0) <= 68
                ]
                items.extend(pack_items)
            except Exception as exc:
                return {"ok": False, "reason": f"invalid chapter pack {pack_path.name}: {exc}"}
        if len(items) < 800:
            return {"ok": False, "reason": f"expected >=800 chapter 60-68 lessons; found {len(items)}"}
        now = datetime.now().isoformat(timespec="seconds")
        inserted = updated = skipped = 0
        for order in range(60, 69):
            chapter = self.conn.execute(
                "SELECT id FROM chapters WHERE order_index=? ORDER BY id LIMIT 1", (order,)
            ).fetchone()
            if not chapter:
                continue
            chapter_id = chapter["id"]
            level = self.conn.execute(
                "SELECT id FROM levels WHERE chapter_id=? AND title_fa=? ORDER BY id LIMIT 1",
                (chapter_id, "غنی‌سازی و اعتبارسنجی"),
            ).fetchone()
            rows = [x for x in items if int(x.get("chapter_order") or 0) == order]
            if not rows:
                continue
            if not level:
                max_level = self.conn.execute(
                    "SELECT COALESCE(MAX(order_index),0) n FROM levels WHERE chapter_id=?",
                    (chapter_id,),
                ).fetchone()["n"]
                self.conn.execute(
                    "INSERT INTO levels(chapter_id,order_index,title_fa,title_en) VALUES(?,?,?,?)",
                    (chapter_id, int(max_level)+1, "غنی‌سازی و اعتبارسنجی", "Deep enrichment and validation"),
                )
                level_id = self.conn.execute("SELECT last_insert_rowid() id").fetchone()["id"]
            else:
                level_id = level["id"]
            for item in rows:
                title = (item.get("title_fa") or "").strip()
                if not title:
                    continue
                existing = self.conn.execute(
                    """SELECT l.id,l.full_content FROM lessons l
                       JOIN levels lv ON lv.id=l.level_id
                       WHERE lv.chapter_id=? AND l.title_fa=?
                       ORDER BY length(COALESCE(l.full_content,'')) DESC, l.id LIMIT 1""",
                    (chapter_id, title),
                ).fetchone()
                meta_obj = item.get("meta") or {}
                meta = json.dumps(meta_obj, ensure_ascii=False)
                notes = item.get("notes") or ""
                assessment = meta_obj.get("assessment")
                if assessment and "EJ_ASSESSMENT" not in notes:
                    notes += "\n\n<!-- EJ_ASSESSMENT\n" + json.dumps(assessment, ensure_ascii=False) + "\n-->\n"
                values = (
                    item.get("title_en") or "", "chapter-" + str(order),
                    item.get("summary") or "", item.get("full_content") or "",
                    item.get("commands") or "", item.get("examples") or "",
                    notes, meta, " ".join([
                        title, str(item.get("topic") or ""), str(item.get("commands") or ""),
                        str(item.get("summary") or "")
                    ]),
                    "\n".join(item.get("learning_objectives") or []), "review_required", now,
                )
                if existing:
                    if len(str(existing["full_content"] or "")) < len(str(item.get("full_content") or "")):
                        self.conn.execute(
                            """UPDATE lessons SET title_en=?,tags=?,summary=?,full_content=?,commands=?,examples=?,
                               notes=?,meta_json=?,search_query=?,learning_objectives=?,source_status=?,last_updated=?
                               WHERE id=?""",
                            (*values, existing["id"]),
                        )
                        updated += 1
                    else:
                        skipped += 1
                    continue
                next_order = self.conn.execute(
                    "SELECT COALESCE(MAX(order_index),0)+1 n FROM lessons WHERE level_id=?", (level_id,)
                ).fetchone()["n"]
                self.conn.execute(
                    """INSERT INTO lessons(level_id,order_index,title_fa,title_en,tags,summary,full_content,
                       commands,examples,notes,meta_json,search_query,learning_objectives,source_status,last_updated)
                       VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
                    (level_id, next_order, title, *values),
                )
                inserted += 1
        self.conn.commit()
        self.set_meta("chapter_60_68_pack_version", "ch60-68-deep-v2")
        return {"ok": True, "inserted": inserted, "updated": updated, "skipped": skipped}

    def ensure_ch55_deep_lessons(self):
        """Idempotently import the shared chapter 55 CCTV/Access/BMS/IoT pack."""
        pack_path = BASE.parent / "tools" / "packs" / "ch55" / "chapter_55_cctv_access_bms_iot_pack.json"
        if not pack_path.is_file():
            return {"ok": False, "reason": "chapter 55 pack missing"}
        try:
            pack = json.loads(pack_path.read_text(encoding="utf-8"))
            items = [x for x in (pack.get("lessons") or [])
                     if isinstance(x, dict) and int(x.get("chapter_order") or 0) == 55
                     and x.get("title_fa") and len(x.get("full_content") or "") >= 800]
            if len(items) < 100:
                return {"ok": False, "reason": f"expected >=100 deep chapter 55 lessons; found {len(items)}"}
            if len({x.get("uid") for x in items}) != len(items):
                return {"ok": False, "reason": "duplicate UID in chapter 55 pack"}
        except Exception as exc:
            return {"ok": False, "reason": f"invalid chapter 55 pack: {exc}"}
        chapter = self.conn.execute(
            "SELECT id FROM chapters WHERE order_index=55 ORDER BY id LIMIT 1"
        ).fetchone()
        if not chapter:
            return {"ok": False, "reason": "chapter 55 missing from seeded curriculum"}
        chapter_id = chapter["id"]
        level = self.conn.execute(
            "SELECT id FROM levels WHERE chapter_id=? AND title_fa=? ORDER BY id LIMIT 1",
            (chapter_id, "غنی‌سازی و اعتبارسنجی"),
        ).fetchone()
        if not level:
            max_level = self.conn.execute(
                "SELECT COALESCE(MAX(order_index),0) n FROM levels WHERE chapter_id=?", (chapter_id,)
            ).fetchone()["n"]
            self.conn.execute(
                "INSERT INTO levels(chapter_id,order_index,title_fa,title_en) VALUES(?,?,?,?)",
                (chapter_id, int(max_level)+1, "غنی‌سازی و اعتبارسنجی", "Deep enrichment and validation"),
            )
            level_id = self.conn.execute("SELECT last_insert_rowid() id").fetchone()["id"]
        else:
            level_id = level["id"]
        now = datetime.now().isoformat(timespec="seconds")
        inserted = updated = skipped = 0
        for item in items:
            title = str(item.get("title_fa") or "").strip()
            meta_obj = item.get("meta") or {}
            notes = item.get("notes") or ""
            assessment = meta_obj.get("assessment")
            if assessment and "EJ_ASSESSMENT" not in notes:
                notes += "\n\n<!-- EJ_ASSESSMENT\n" + json.dumps(assessment, ensure_ascii=False) + "\n-->\n"
            values = (
                item.get("title_en") or "", "chapter-55", item.get("summary") or "",
                item.get("full_content") or "", item.get("commands") or "", item.get("examples") or "",
                notes, json.dumps(meta_obj, ensure_ascii=False),
                " ".join([title, str(item.get("topic") or ""), str(item.get("commands") or ""),
                          str(item.get("summary") or "")]),
                "\n".join(item.get("learning_objectives") or []), "review_required", now,
            )
            existing = self.conn.execute(
                """SELECT l.id,l.full_content FROM lessons l JOIN levels lv ON lv.id=l.level_id
                   WHERE lv.chapter_id=? AND l.title_fa=?
                   ORDER BY length(COALESCE(l.full_content,'')) DESC,l.id LIMIT 1""",
                (chapter_id, title),
            ).fetchone()
            if existing:
                if len(str(existing["full_content"] or "")) < len(str(item.get("full_content") or "")):
                    self.conn.execute(
                        """UPDATE lessons SET title_en=?,tags=?,summary=?,full_content=?,commands=?,examples=?,
                           notes=?,meta_json=?,search_query=?,learning_objectives=?,source_status=?,last_updated=?
                           WHERE id=?""", (*values, existing["id"])
                    )
                    updated += 1
                else:
                    skipped += 1
                continue
            next_order = self.conn.execute(
                "SELECT COALESCE(MAX(order_index),0)+1 n FROM lessons WHERE level_id=?", (level_id,)
            ).fetchone()["n"]
            self.conn.execute(
                """INSERT INTO lessons(level_id,order_index,title_fa,title_en,tags,summary,full_content,
                   commands,examples,notes,meta_json,search_query,learning_objectives,source_status,last_updated)
                   VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
                (level_id, next_order, title, *values),
            )
            inserted += 1
        self.conn.commit()
        self.set_meta("chapter_55_pack_version", "ch55-cctv-access-bms-iot-v1")
        return {"ok": True, "inserted": inserted, "updated": updated, "skipped": skipped}

    def ensure_scenario_pack(self):
        """بارگذاری بستهٔ سناریوهای مشترک؛ idempotent و قابل تکرار در startup."""
        pack_path = BASE.parent / "tools" / "packs" / "scenarios" / "scenarios_150.json"
        if not pack_path.is_file():
            return {"ok": False, "reason": "scenario pack missing"}
        try:
            pack = json.loads(pack_path.read_text(encoding="utf-8"))
            items = pack.get("scenarios") or []
            if len(items) < 240:
                return {"ok": False, "reason": f"expected >=240 scenarios; found {len(items)}"}
        except Exception as exc:
            return {"ok": False, "reason": f"invalid scenario pack: {exc}"}
        marker = "shared-240-ch60-68-v2"
        current = self.conn.execute("SELECT COUNT(*) c FROM scenarios").fetchone()["c"]
        if self.get_meta("scenario_pack_version") == marker and current >= 240:
            return {"ok": True, "skipped": True, "pack_scenarios": len(items), "total_scenarios": current}
        now = datetime.now().isoformat(timespec="seconds")
        for item in items:
            self.conn.execute(
                """INSERT OR REPLACE INTO scenarios(
                    code,title_fa,title_en,category,level,difficulty,users,sites,vendors,
                    business_context,requirements,constraints_text,initial_state,incident,symptoms,
                    objectives,tasks,hints,expected_result,solution,verification,skills_required,
                    estimated_hours,last_updated
                ) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
                (
                    item.get("code",""), item.get("title_fa",""), item.get("title_en",""),
                    item.get("category","Troubleshooting"), item.get("level","L3"),
                    item.get("difficulty","متوسط"), int(item.get("users") or 0),
                    int(item.get("sites") or 1), item.get("vendors",""),
                    item.get("business_context",""), item.get("requirements",""),
                    item.get("constraints_text",""), item.get("initial_state",""),
                    item.get("incident",""), item.get("symptoms",""), item.get("objectives",""),
                    item.get("tasks",""), item.get("hints",""), item.get("expected_result",""),
                    item.get("solution",""), item.get("verification",""),
                    item.get("skills_required",""), int(item.get("estimated_hours") or 1), now,
                ),
            )
        self.conn.commit()
        self.set_meta("scenario_pack_version", marker)
        return {"ok": True, "pack_scenarios": len(items),
                "total_scenarios": self.conn.execute("SELECT COUNT(*) c FROM scenarios").fetchone()["c"]}

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
            "SELECT id, code, title_fa, category, level, difficulty, users, sites, estimated_hours, last_updated FROM scenarios ORDER BY code"
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
            d = dict(r); d["entity"] = "lesson"; out.append(d)
        for r in self.conn.execute(f"SELECT * FROM scenarios WHERE uid IN ({qmarks})", list(uids)).fetchall():
            d = dict(r); d["entity"] = "scenario"; out.append(d)
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
