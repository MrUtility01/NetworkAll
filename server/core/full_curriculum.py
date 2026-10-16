# -*- coding: utf-8 -*-
"""Canonical curriculum loader: each chapter's base lessons live beside its chapter files."""
from __future__ import annotations

import json
from pathlib import Path

LEVELS = [
    ("L0", "آشنایی", "Intro"),
    ("L1", "مقدماتی", "Junior"),
    ("L2", "ادمین", "Admin"),
    ("L3", "مهندس", "Senior"),
    ("L4", "خبره", "Architect"),
]

ROOT = Path(__file__).resolve().parents[2]
CHAPTERS_DIR = ROOT / "tools" / "chapters"


def _expand(topic_fa, topic_en=""):
    return [
        (f"[{code}] {topic_fa} — {fa_level}", f"[{code}] {topic_en or topic_fa} — {en_level}")
        for code, fa_level, en_level in LEVELS
    ]


def _sub(title, topics):
    lessons = []
    for topic in topics:
        fa, en = topic if isinstance(topic, tuple) else (topic, "")
        lessons.extend(_expand(fa, en))
    return title, lessons


def _lesson_tuple(item):
    fa = str(item.get("title_fa") or item.get("title_en") or "درس")
    en = str(item.get("title_en") or fa)
    extra = item.get("extra_fields")
    if not isinstance(extra, list):
        extra = []
    if item.get("source_record") is not None:
        extra = [*extra, item["source_record"]]
    return tuple([fa, en, *extra])


def get_full_curriculum():
    """Return the same public tuple shape as the former inline curriculum, loaded per chapter."""
    if not CHAPTERS_DIR.is_dir():
        raise RuntimeError(f"Canonical chapter directory is missing: {CHAPTERS_DIR}")

    result = []
    seen = set()
    for order in range(1, 69):
        numeric = CHAPTERS_DIR / str(order)
        legacy_dirs = sorted(CHAPTERS_DIR.glob(f"ch{order:02d}_*"))
        candidates = [
            numeric / "lessons" / "base_curriculum.json",
            numeric / "base_curriculum.json",
        ]
        for legacy_dir in legacy_dirs:
            candidates.extend([
                legacy_dir / "lessons" / "base_curriculum.json",
                legacy_dir / "base_curriculum.json",
            ])
        path = next((candidate for candidate in candidates if candidate.is_file()), None)
        if path is None:
            continue
        payload = json.loads(path.read_text(encoding="utf-8"))
        order = int(payload.get("chapter_order") or 0)
        if not 1 <= order <= 68:
            raise ValueError(f"Invalid chapter_order in {path}: {order}")
        if payload.get("kind") != "baseline_curriculum":
            raise ValueError(f"Unexpected baseline schema in {path}")
        if order in seen:
            raise ValueError(f"Duplicate base curriculum for chapter {order}")
        seen.add(order)

        levels = []
        raw_levels = payload.get("levels")
        if not isinstance(raw_levels, list):
            raise ValueError(f"levels must be a list in {path}")
        for level in raw_levels:
            if not isinstance(level, dict):
                raise ValueError(f"Invalid level record in {path}")
            lesson_rows = level.get("lessons")
            if not isinstance(lesson_rows, list):
                raise ValueError(f"Invalid lessons list in {path}, level={level.get('title_fa')}")
            lessons = [_lesson_tuple(row) for row in lesson_rows if isinstance(row, dict)]
            levels.append((str(level.get("title_fa") or "زیرفصل"), lessons))

        result.append((
            order,
            str(payload.get("chapter_title_fa") or f"فصل {order}"),
            str(payload.get("chapter_title_en") or f"Chapter {order}"),
            levels,
        ))

    missing = sorted(set(range(1, 69)) - seen)
    if missing:
        raise RuntimeError(
            "Baseline chapter files are incomplete; missing chapters: "
            + ", ".join(str(x) for x in missing)
        )
    result.sort(key=lambda chapter: chapter[0])
    return result
