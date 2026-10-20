# -*- coding: utf-8 -*-
"""
موتور Import بسته محتوای کاربر (NetworkAll Content Pack - .nacp)

فرمت: ZIP با manifest.json + پوشه‌های lessons/notes/questions/answers/commands/labs
مستند کامل: docs/DATA_SEPARATION_AND_IMPORT.md
"""
from __future__ import annotations

import json
import shutil
import tempfile
import zipfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

# حداکثر حجم بسته (بایت) — ۲۰ مگابایت
MAX_PACK_BYTES = 20 * 1024 * 1024
SUPPORTED_SCHEMA = {1}

REQUIRED_MANIFEST_KEYS = {
    "pack_schema_version",
    "pack_id",
    "title_fa",
    "target_chapter_mode",
    "content_files",
}

ALLOWED_CONTENT_DIRS = {
    "lessons",
    "notes",
    "questions",
    "answers",
    "commands",
    "labs",
}


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


class PackValidationError(Exception):
    """خطای اعتبارسنجی بسته."""

    def __init__(self, message: str, details: list[str] | None = None):
        super().__init__(message)
        self.message = message
        self.details = details or []


class PackImporter:
    """اعتبارسنجی و وارد کردن بسته .nacp / .zip به دیتابیس."""

    def __init__(self, db, user_packs_dir: Path | None = None):
        self.db = db
        base = Path(__file__).resolve().parent.parent
        self.user_packs_dir = user_packs_dir or (base / "data" / "user_packs")
        self.user_packs_dir.mkdir(parents=True, exist_ok=True)

    # ------------------------------------------------------------------
    # اعتبارسنجی
    # ------------------------------------------------------------------

    def validate_zip(self, zip_path: Path) -> dict[str, Any]:
        """فایل ZIP را باز می‌کند، manifest و فایل‌ها را اعتبارسنجی می‌کند و دیکشنری نتیجه برمی‌گرداند."""
        if not zip_path.exists():
            raise PackValidationError("فایل بسته پیدا نشد.")

        size = zip_path.stat().st_size
        if size > MAX_PACK_BYTES:
            raise PackValidationError(
                f"حجم بسته بیش از حد مجاز است ({size} بایت > {MAX_PACK_BYTES} بایت)."
            )
        if size < 64:
            raise PackValidationError("فایل بسته خیلی کوچک یا خالی است.")

        try:
            zf = zipfile.ZipFile(zip_path, "r")
        except zipfile.BadZipFile as e:
            raise PackValidationError("فایل ZIP معتبر نیست.", [str(e)]) from e

        with zf:
            names = set(zf.namelist())
            # جلوگیری از path traversal
            for n in names:
                if n.startswith("/") or ".." in Path(n).parts:
                    raise PackValidationError(f"مسیر غیرمجاز داخل بسته: {n}")

            if "manifest.json" not in names:
                # گاهی پوشه ریشه وجود دارد
                manifest_candidates = [n for n in names if n.endswith("manifest.json")]
                if not manifest_candidates:
                    raise PackValidationError("manifest.json داخل بسته پیدا نشد.")
                manifest_name = manifest_candidates[0]
            else:
                manifest_name = "manifest.json"

            try:
                raw = zf.read(manifest_name).decode("utf-8")
                manifest = json.loads(raw)
            except Exception as e:
                raise PackValidationError("manifest.json قابل خواندن یا JSON معتبر نیست.", [str(e)]) from e

            errors: list[str] = []
            for key in REQUIRED_MANIFEST_KEYS:
                if key not in manifest:
                    errors.append(f"کلید اجباری manifest وجود ندارد: {key}")

            schema_ver = manifest.get("pack_schema_version")
            if schema_ver not in SUPPORTED_SCHEMA:
                errors.append(f"pack_schema_version پشتیبانی‌نشده: {schema_ver} (مجاز: {sorted(SUPPORTED_SCHEMA)})")

            mode = manifest.get("target_chapter_mode")
            if mode not in ("merge", "new_chapter"):
                errors.append("target_chapter_mode باید merge یا new_chapter باشد.")

            if mode == "merge" and not manifest.get("target_chapter_order"):
                errors.append("در حالت merge باید target_chapter_order مشخص باشد.")

            if mode == "new_chapter" and not (manifest.get("new_chapter_title_fa") or "").strip():
                errors.append("در حالت new_chapter باید new_chapter_title_fa مشخص باشد.")

            content_files = manifest.get("content_files") or []
            if not isinstance(content_files, list) or not content_files:
                errors.append("content_files باید لیست غیردخالی باشد.")

            # بررسی وجود فایل‌های اعلام‌شده
            prefix = ""
            if manifest_name != "manifest.json":
                prefix = str(Path(manifest_name).parent) + "/"
                if prefix == "./":
                    prefix = ""

            loaded: dict[str, Any] = {}
            for rel in content_files:
                full = prefix + rel if prefix and not rel.startswith(prefix) else rel
                # نرمال‌سازی
                full = full.replace("\\", "/")
                if full not in names and rel not in names:
                    errors.append(f"فایل اعلام‌شده در بسته نیست: {rel}")
                    continue
                actual = full if full in names else rel
                try:
                    data = json.loads(zf.read(actual).decode("utf-8"))
                    loaded[rel] = data
                except Exception as e:
                    errors.append(f"خواندن/پارس JSON ناموفق: {rel} → {e}")

            if errors:
                raise PackValidationError("اعتبارسنجی بسته ناموفق بود.", errors)

            # اعتبارسنجی داخلی رکوردها
            record_errors = self._validate_records(loaded)
            if record_errors:
                raise PackValidationError("خطا در رکوردهای محتوا.", record_errors)

            return {
                "manifest": manifest,
                "loaded": loaded,
                "zip_path": str(zip_path),
                "size_bytes": size,
            }

    def _validate_records(self, loaded: dict[str, Any]) -> list[str]:
        errs: list[str] = []
        all_uids: set[str] = set()
        question_uids: set[str] = set()
        answer_uids: set[str] = set()

        def check_items(key: str, require_front_back: bool = False):
            data = loaded.get(key)
            if data is None:
                return
            items = data.get("items") if isinstance(data, dict) else data
            if not isinstance(items, list):
                errs.append(f"{key}: باید لیست items داشته باشد.")
                return
            for i, item in enumerate(items):
                if not isinstance(item, dict):
                    errs.append(f"{key}[{i}]: رکورد باید object باشد.")
                    continue
                uid = (item.get("uid") or "").strip()
                if not uid:
                    errs.append(f"{key}[{i}]: uid خالی است.")
                    continue
                if uid in all_uids:
                    errs.append(f"uid تکراری داخل بسته: {uid}")
                all_uids.add(uid)
                if require_front_back:
                    if not (item.get("front_fa") or "").strip():
                        errs.append(f"فلش‌کارت بدون front_fa: {uid}")
                    if not (item.get("back_fa") or "").strip():
                        errs.append(f"فلش‌کارت بدون back_fa: {uid}")
                if key.startswith("questions"):
                    question_uids.add(uid)
                if key.startswith("answers"):
                    answer_uids.add(uid)

        check_items("lessons/lessons.json")
        check_items("notes/learning_cards.json", require_front_back=True)
        check_items("questions/questions.json")
        check_items("answers/answer_key.json")
        check_items("commands/commands.json")
        check_items("labs/labs.json")

        # سوال بدون پاسخ یا برعکس
        for qu in question_uids:
            if qu not in answer_uids:
                errs.append(f"سوال بدون پاسخ متناظر: {qu}")
        for au in answer_uids:
            if au not in question_uids:
                errs.append(f"پاسخ بدون سوال متناظر: {au}")

        return errs

    # ------------------------------------------------------------------
    # وارد کردن به دیتابیس
    # ------------------------------------------------------------------

    def import_validated(self, validated: dict[str, Any]) -> dict[str, Any]:
        """بسته اعتبارسنجی‌شده را در دیتابیس و پوشه user_packs ذخیره می‌کند."""
        self._ensure_import_tables()

        manifest = validated["manifest"]
        loaded = validated["loaded"]
        pack_id = manifest["pack_id"]
        mode = manifest["target_chapter_mode"]
        now = utc_now()

        # کپی فایل بسته به محل دائمی
        dest_dir = self.user_packs_dir / pack_id.replace(":", "_").replace("/", "_")
        if dest_dir.exists():
            shutil.rmtree(dest_dir)
        dest_dir.mkdir(parents=True)
        src_zip = Path(validated["zip_path"])
        shutil.copy2(src_zip, dest_dir / "pack.nacp")

        # ذخیره manifest
        (dest_dir / "manifest.json").write_text(
            json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8"
        )

        chapter_order = None
        chapter_id = None

        if mode == "merge":
            chapter_order = int(manifest["target_chapter_order"])
            chapter_id = self._find_chapter_id(chapter_order)
            if chapter_id is None:
                raise PackValidationError(f"فصل با order_index={chapter_order} در دیتابیس پیدا نشد.")
        else:
            # new_chapter
            title_fa = manifest["new_chapter_title_fa"].strip()
            title_en = (manifest.get("title_en") or "").strip()
            chapter_order, chapter_id = self._create_chapter(title_fa, title_en)

        counts = {"lessons": 0, "notes": 0, "questions": 0, "answers": 0, "commands": 0, "labs": 0}

        # lessons
        items = self._extract_items(loaded.get("lessons/lessons.json"))
        for item in items:
            self._upsert_lesson(item, chapter_id, chapter_order, now)
            counts["lessons"] += 1

        # notes / flashcards
        items = self._extract_items(loaded.get("notes/learning_cards.json"))
        for item in items:
            self._upsert_note(item, chapter_order, now)
            counts["notes"] += 1

        # questions
        items = self._extract_items(loaded.get("questions/questions.json"))
        for item in items:
            self._upsert_question(item, chapter_order, now)
            counts["questions"] += 1

        # answers
        items = self._extract_items(loaded.get("answers/answer_key.json"))
        for item in items:
            self._upsert_answer(item, now)
            counts["answers"] += 1

        # commands
        items = self._extract_items(loaded.get("commands/commands.json"))
        for item in items:
            self._upsert_command(item, chapter_order, now)
            counts["commands"] += 1

        # labs
        items = self._extract_items(loaded.get("labs/labs.json"))
        for item in items:
            self._upsert_lab(item, chapter_order, now)
            counts["labs"] += 1

        # ثبت در جدول imported_packs
        self.db.conn.execute(
            """
            INSERT INTO imported_packs(
                pack_id, title_fa, title_en, author, created_at, imported_at,
                target_mode, target_chapter_order, chapter_id, counts_json, storage_path
            ) VALUES (?,?,?,?,?,?,?,?,?,?,?)
            ON CONFLICT(pack_id) DO UPDATE SET
                title_fa=excluded.title_fa,
                imported_at=excluded.imported_at,
                counts_json=excluded.counts_json,
                storage_path=excluded.storage_path
            """,
            (
                pack_id,
                manifest.get("title_fa", ""),
                manifest.get("title_en", ""),
                manifest.get("author", ""),
                manifest.get("created_at", ""),
                now,
                mode,
                chapter_order,
                chapter_id,
                json.dumps(counts, ensure_ascii=False),
                str(dest_dir),
            ),
        )
        self.db.conn.commit()

        return {
            "ok": True,
            "pack_id": pack_id,
            "mode": mode,
            "chapter_order": chapter_order,
            "chapter_id": chapter_id,
            "counts": counts,
            "imported_at": now,
            "storage_path": str(dest_dir),
        }

    # ------------------------------------------------------------------
    # helpers
    # ------------------------------------------------------------------

    def _extract_items(self, data: Any) -> list[dict]:
        if data is None:
            return []
        if isinstance(data, dict):
            items = data.get("items") or []
        elif isinstance(data, list):
            items = data
        else:
            return []
        return [x for x in items if isinstance(x, dict)]

    def _find_chapter_id(self, order_index: int) -> int | None:
        row = self.db.conn.execute(
            "SELECT id FROM chapters WHERE order_index=? ORDER BY id LIMIT 1",
            (order_index,),
        ).fetchone()
        return int(row["id"]) if row else None

    def _create_chapter(self, title_fa: str, title_en: str = "") -> tuple[int, int]:
        row = self.db.conn.execute("SELECT MAX(order_index) AS m FROM chapters").fetchone()
        next_order = (row["m"] or 0) + 1
        cur = self.db.conn.execute(
            "INSERT INTO chapters(order_index, title_fa, title_en, description) VALUES (?,?,?,?)",
            (next_order, title_fa, title_en, "فصل واردشده توسط کاربر"),
        )
        chapter_id = cur.lastrowid
        # یک level پیش‌فرض برای سازگاری با ساختار فعلی
        self.db.conn.execute(
            "INSERT INTO levels(chapter_id, order_index, title_fa) VALUES (?,?,?)",
            (chapter_id, 1, "محتوای واردشده"),
        )
        self.db.conn.commit()
        return next_order, chapter_id

    def _get_or_create_import_level(self, chapter_id: int) -> int:
        row = self.db.conn.execute(
            "SELECT id FROM levels WHERE chapter_id=? ORDER BY order_index LIMIT 1",
            (chapter_id,),
        ).fetchone()
        if row:
            return int(row["id"])
        cur = self.db.conn.execute(
            "INSERT INTO levels(chapter_id, order_index, title_fa) VALUES (?,?,?)",
            (chapter_id, 1, "محتوای واردشده"),
        )
        self.db.conn.commit()
        return int(cur.lastrowid)

    def _upsert_lesson(self, item: dict, chapter_id: int, chapter_order: int, now: str):
        uid = item["uid"]
        level_id = self._get_or_create_import_level(chapter_id)
        title_fa = item.get("title_fa") or uid
        title_en = item.get("title_en") or ""
        summary = item.get("summary") or ""
        full_content = item.get("full_content") or ""
        order_index = int(item.get("lesson_order") or 0)
        meta = {
            "source": "user_import",
            "learning_objectives": item.get("learning_objectives") or [],
            "key_points": item.get("key_points") or [],
            "learning_cards": item.get("learning_cards") or [],
            "related_questions": item.get("related_questions") or [],
            "difficulty": item.get("difficulty") or "",
            "estimated_minutes": item.get("estimated_minutes"),
        }
        existing = self.db.conn.execute("SELECT id FROM lessons WHERE uid=?", (uid,)).fetchone()
        if existing:
            self.db.conn.execute(
                """UPDATE lessons SET title_fa=?, title_en=?, summary=?, full_content=?,
                   order_index=?, meta_json=?, last_updated=?, source_status=?
                   WHERE uid=?""",
                (
                    title_fa, title_en, summary, full_content, order_index,
                    json.dumps(meta, ensure_ascii=False), now,
                    item.get("source_status") or "review_required", uid,
                ),
            )
        else:
            self.db.conn.execute(
                """INSERT INTO lessons(
                    level_id, order_index, title_fa, title_en, summary, full_content,
                    meta_json, uid, last_updated, source_status
                ) VALUES (?,?,?,?,?,?,?,?,?,?)""",
                (
                    level_id, order_index, title_fa, title_en, summary, full_content,
                    json.dumps(meta, ensure_ascii=False), uid, now,
                    item.get("source_status") or "review_required",
                ),
            )

    def _upsert_note(self, item: dict, chapter_order: int, now: str):
        uid = item["uid"]
        self.db.conn.execute(
            """
            INSERT INTO content_notes(
                uid, type, title_fa, front_fa, back_fa, body_fa,
                related_lessons, tags, chapter_order, difficulty,
                ease_factor_default, interval_days_default, source_status, last_updated
            ) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?)
            ON CONFLICT(uid) DO UPDATE SET
                type=excluded.type,
                title_fa=excluded.title_fa,
                front_fa=excluded.front_fa,
                back_fa=excluded.back_fa,
                body_fa=excluded.body_fa,
                related_lessons=excluded.related_lessons,
                tags=excluded.tags,
                difficulty=excluded.difficulty,
                last_updated=excluded.last_updated
            """,
            (
                uid,
                item.get("type") or "concept",
                item.get("title_fa") or "",
                item.get("front_fa") or "",
                item.get("back_fa") or "",
                item.get("body_fa") or "",
                json.dumps(item.get("related_lessons") or [], ensure_ascii=False),
                json.dumps(item.get("tags") or [], ensure_ascii=False),
                chapter_order or item.get("chapter_order") or 0,
                item.get("difficulty") or "مبتدی",
                (item.get("spaced_repetition") or {}).get("ease_factor_default", 2.5),
                (item.get("spaced_repetition") or {}).get("interval_days_default", 1),
                item.get("source_status") or "review_required",
                now,
            ),
        )

    def _upsert_question(self, item: dict, chapter_order: int, now: str):
        uid = item["uid"]
        self.db.conn.execute(
            """
            INSERT INTO content_questions(
                uid, lesson_uid, type, question_fa, options_json,
                difficulty, tags, chapter_order, last_updated
            ) VALUES (?,?,?,?,?,?,?,?,?)
            ON CONFLICT(uid) DO UPDATE SET
                lesson_uid=excluded.lesson_uid,
                type=excluded.type,
                question_fa=excluded.question_fa,
                options_json=excluded.options_json,
                difficulty=excluded.difficulty,
                tags=excluded.tags,
                last_updated=excluded.last_updated
            """,
            (
                uid,
                item.get("lesson_uid") or "",
                item.get("type") or "multiple_choice",
                item.get("question_fa") or "",
                json.dumps(item.get("options") or [], ensure_ascii=False),
                item.get("difficulty") or "مبتدی",
                json.dumps(item.get("tags") or [], ensure_ascii=False),
                chapter_order or item.get("chapter_order") or 0,
                now,
            ),
        )

    def _upsert_answer(self, item: dict, now: str):
        uid = item["uid"]
        self.db.conn.execute(
            """
            INSERT INTO content_answers(
                uid, correct, explanation_fa, related_lesson, last_updated
            ) VALUES (?,?,?,?,?)
            ON CONFLICT(uid) DO UPDATE SET
                correct=excluded.correct,
                explanation_fa=excluded.explanation_fa,
                related_lesson=excluded.related_lesson,
                last_updated=excluded.last_updated
            """,
            (
                uid,
                item.get("correct") or "",
                item.get("explanation_fa") or "",
                item.get("related_lesson") or "",
                now,
            ),
        )

    def _upsert_command(self, item: dict, chapter_order: int, now: str):
        uid = item["uid"]
        self.db.conn.execute(
            """
            INSERT INTO content_commands(
                uid, vendor_or_os, command, parameters, sample_output,
                use_case, related_lessons, chapter_order, last_updated
            ) VALUES (?,?,?,?,?,?,?,?,?)
            ON CONFLICT(uid) DO UPDATE SET
                vendor_or_os=excluded.vendor_or_os,
                command=excluded.command,
                parameters=excluded.parameters,
                sample_output=excluded.sample_output,
                use_case=excluded.use_case,
                related_lessons=excluded.related_lessons,
                last_updated=excluded.last_updated
            """,
            (
                uid,
                item.get("vendor_or_os") or "",
                item.get("command") or "",
                item.get("parameters") or "",
                item.get("sample_output") or "",
                item.get("use_case") or "",
                json.dumps(item.get("related_lessons") or [], ensure_ascii=False),
                chapter_order or item.get("chapter_order") or 0,
                now,
            ),
        )

    def _upsert_lab(self, item: dict, chapter_order: int, now: str):
        uid = item["uid"]
        self.db.conn.execute(
            """
            INSERT INTO content_labs(
                uid, title_fa, difficulty, objective, initial_state,
                required_commands, steps, expected_result, verification_steps,
                common_errors, safety_note, related_lesson, chapter_order, last_updated
            ) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?)
            ON CONFLICT(uid) DO UPDATE SET
                title_fa=excluded.title_fa,
                difficulty=excluded.difficulty,
                objective=excluded.objective,
                initial_state=excluded.initial_state,
                required_commands=excluded.required_commands,
                steps=excluded.steps,
                expected_result=excluded.expected_result,
                verification_steps=excluded.verification_steps,
                common_errors=excluded.common_errors,
                safety_note=excluded.safety_note,
                related_lesson=excluded.related_lesson,
                last_updated=excluded.last_updated
            """,
            (
                uid,
                item.get("title_fa") or "",
                item.get("difficulty") or "مبتدی",
                item.get("objective") or "",
                item.get("initial_state") or "",
                json.dumps(item.get("required_commands") or [], ensure_ascii=False),
                json.dumps(item.get("steps") or [], ensure_ascii=False),
                item.get("expected_result") or "",
                json.dumps(item.get("verification_steps") or [], ensure_ascii=False),
                json.dumps(item.get("common_errors") or [], ensure_ascii=False),
                item.get("safety_note") or "",
                item.get("related_lesson") or "",
                chapter_order or item.get("chapter_order") or 0,
                now,
            ),
        )

    def _ensure_import_tables(self):
        self.db.conn.executescript(
            """
            CREATE TABLE IF NOT EXISTS imported_packs (
                pack_id TEXT PRIMARY KEY,
                title_fa TEXT,
                title_en TEXT,
                author TEXT,
                created_at TEXT,
                imported_at TEXT,
                target_mode TEXT,
                target_chapter_order INTEGER,
                chapter_id INTEGER,
                counts_json TEXT,
                storage_path TEXT
            );

            CREATE TABLE IF NOT EXISTS content_notes (
                uid TEXT PRIMARY KEY,
                type TEXT,
                title_fa TEXT,
                front_fa TEXT,
                back_fa TEXT,
                body_fa TEXT,
                related_lessons TEXT,
                tags TEXT,
                chapter_order INTEGER,
                difficulty TEXT,
                ease_factor_default REAL DEFAULT 2.5,
                interval_days_default INTEGER DEFAULT 1,
                source_status TEXT,
                last_updated TEXT
            );

            CREATE TABLE IF NOT EXISTS content_questions (
                uid TEXT PRIMARY KEY,
                lesson_uid TEXT,
                type TEXT,
                question_fa TEXT,
                options_json TEXT,
                difficulty TEXT,
                tags TEXT,
                chapter_order INTEGER,
                last_updated TEXT
            );

            CREATE TABLE IF NOT EXISTS content_answers (
                uid TEXT PRIMARY KEY,
                correct TEXT,
                explanation_fa TEXT,
                related_lesson TEXT,
                last_updated TEXT
            );

            CREATE TABLE IF NOT EXISTS content_commands (
                uid TEXT PRIMARY KEY,
                vendor_or_os TEXT,
                command TEXT,
                parameters TEXT,
                sample_output TEXT,
                use_case TEXT,
                related_lessons TEXT,
                chapter_order INTEGER,
                last_updated TEXT
            );

            CREATE TABLE IF NOT EXISTS content_labs (
                uid TEXT PRIMARY KEY,
                title_fa TEXT,
                difficulty TEXT,
                objective TEXT,
                initial_state TEXT,
                required_commands TEXT,
                steps TEXT,
                expected_result TEXT,
                verification_steps TEXT,
                common_errors TEXT,
                safety_note TEXT,
                related_lesson TEXT,
                chapter_order INTEGER,
                last_updated TEXT
            );
            """
        )
        self.db.conn.commit()

    # ------------------------------------------------------------------
    # مدیریت بسته‌های واردشده
    # ------------------------------------------------------------------

    def list_imported_packs(self) -> list[dict]:
        self._ensure_import_tables()
        rows = self.db.conn.execute(
            "SELECT * FROM imported_packs ORDER BY imported_at DESC"
        ).fetchall()
        out = []
        for r in rows:
            d = dict(r)
            try:
                d["counts"] = json.loads(d.get("counts_json") or "{}")
            except Exception:
                d["counts"] = {}
            out.append(d)
        return out

    def delete_pack(self, pack_id: str, remove_content: bool = False) -> dict:
        self._ensure_import_tables()
        row = self.db.conn.execute(
            "SELECT storage_path FROM imported_packs WHERE pack_id=?", (pack_id,)
        ).fetchone()
        if not row:
            return {"ok": False, "error": "pack not found"}

        storage = row["storage_path"]
        if storage and Path(storage).exists():
            shutil.rmtree(storage, ignore_errors=True)

        self.db.conn.execute("DELETE FROM imported_packs WHERE pack_id=?", (pack_id,))
        # فعلاً محتوای واردشده را حذف نمی‌کنیم مگر صریحاً خواسته شود
        # (برای جلوگیری از از دست رفتن پیشرفت کاربر)
        self.db.conn.commit()
        return {"ok": True, "pack_id": pack_id, "content_removed": False}
