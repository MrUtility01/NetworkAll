#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Import staged NetworkEncyclopedia lessons into the shared Android/Windows curriculum.

Only genuinely new lesson titles are added. Existing UIDs and lesson bodies are left
untouched; every imported record receives a deterministic UID and review_required status.
"""
from __future__ import annotations

import gzip
import hashlib
import json
import re
import unicodedata
from collections import defaultdict
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
ASSET = ROOT / "android/app/src/main/assets/curriculum_index.json.gz"
SOURCE_DIR = ROOT / "tools/reference_import/networkencyclopedia_ordered_fill"
MIN_EXPECTED_PACKS = 30

_LEVEL_RE = re.compile(r"^\s*\[L([0-4])\]\s*", re.IGNORECASE)
_ANY_LABEL_RE = re.compile(r"^\s*\[[^\]]+\]\s*")
_TRANSLATION = str.maketrans({
    "ي": "ی", "ى": "ی", "ك": "ک", "ۀ": "ه", "ة": "ه",
    "\u200c": "", "\u200f": "", "\u200e": "",
})


def as_text(value: Any) -> str:
    if value is None:
        return ""
    if isinstance(value, str):
        return value.strip()
    if isinstance(value, (list, tuple)):
        return "\n".join(as_text(item) for item in value if as_text(item))
    if isinstance(value, dict):
        return json.dumps(value, ensure_ascii=False, sort_keys=True)
    return str(value).strip()


def as_string_list(value: Any) -> list[str]:
    if isinstance(value, list):
        return list(dict.fromkeys(as_text(x) for x in value if as_text(x)))
    if isinstance(value, str):
        return list(dict.fromkeys(x.strip() for x in value.splitlines() if x.strip()))
    return []


def strip_leading_labels(value: str) -> str:
    title = as_text(value)
    while True:
        stripped = _ANY_LABEL_RE.sub("", title, count=1)
        if stripped == title:
            return title.strip()
        title = stripped


def normalize_title(value: Any) -> str:
    title = unicodedata.normalize("NFKC", as_text(value)).translate(_TRANSLATION).casefold()
    title = strip_leading_labels(title)
    return re.sub(r"[^\w]+", "", title, flags=re.UNICODE)


def title_keys(lesson: dict[str, Any]) -> set[str]:
    return {
        key
        for key in (
            normalize_title(lesson.get("title_fa") or lesson.get("title")),
            normalize_title(lesson.get("title_en")),
        )
        if key
    }


def lesson_level(title: str) -> str:
    match = _LEVEL_RE.match(title or "")
    return "L" + match.group(1) if match else "L0"


def ch68_collection(lesson: dict[str, Any]) -> str:
    blob = " ".join(
        as_text(lesson.get(key))
        for key in ("title_fa", "title_en", "summary", "commands", "full_content")
    ).casefold()
    rules = (
        ("PowerShell", ("powershell", "test-netconnection", "get-net")),
        ("Windows Batch", ("windows batch", "batch", "@echo off", "errorlevel")),
        ("Windows CMD", ("windows cmd", "command prompt", "ipconfig /all", "cmd.exe")),
        ("Bash", ("bash", "shell scripting")),
        ("Linux", ("linux", "iproute2", "tcpdump", "nftables", "systemctl")),
        ("MikroTik RouterOS", ("mikrotik", "routeros", "winbox")),
        ("FortiGate", ("fortigate", "fortios", "fortinet")),
        ("Cisco IOS/IOS-XE", ("cisco", "ios-xe", "show privilege", "show users", "show logging")),
    )
    for label, needles in rules:
        if any(needle in blob for needle in needles):
            return label
    return "NetworkEncyclopedia"


def stable_uid(chapter_order: int, pack_relative: str, lesson: dict[str, Any],
               existing_uids: set[str]) -> str:
    identity = "|".join((
        pack_relative,
        str(chapter_order),
        normalize_title(lesson.get("title_fa") or lesson.get("title")),
        normalize_title(lesson.get("title_en")),
    ))
    digest = hashlib.sha256(identity.encode("utf-8")).hexdigest()[:20]
    uid = f"lesson:ch{chapter_order:02d}:refnetenc:{digest}"
    suffix = 2
    while uid in existing_uids:
        uid = f"lesson:ch{chapter_order:02d}:refnetenc:{digest}-{suffix}"
        suffix += 1
    existing_uids.add(uid)
    return uid


def find_or_create_subchapter(chapter: dict[str, Any], chapter_order: int,
                              collection: str | None) -> tuple[dict[str, Any], int]:
    subs = chapter.setdefault("subchapters", [])
    if chapter_order == 68 and collection:
        for index, sub in enumerate(subs, 1):
            label = as_text(sub.get("title_fa")).split("—", 1)[0].strip()
            if label == collection:
                return sub, index
        title = f"{collection} — تکمیلی از NetworkEncyclopedia"
    else:
        title = "NetworkEncyclopedia — درس‌های تکمیلی"
        for index, sub in enumerate(subs, 1):
            if as_text(sub.get("title_fa")) == title:
                return sub, index
    new_subchapter = {"title_fa": title, "lessons": []}
    subs.append(new_subchapter)
    return new_subchapter, len(subs)


def normalized_lesson(chapter_order: int, row: dict[str, Any], pack_relative: str,
                      existing_uids: set[str], subchapter_order: int,
                      lesson_order: int) -> dict[str, Any]:
    raw_title = as_text(row.get("title_fa") or row.get("title"))
    title_en = as_text(row.get("title_en"))
    level = lesson_level(raw_title)
    collection = ch68_collection(row) if chapter_order == 68 else ""

    title_fa = raw_title
    if chapter_order == 68:
        title_fa = f"[{collection}] {strip_leading_labels(raw_title)}"

    summary = as_text(row.get("summary"))
    full_content = as_text(row.get("full_content") or row.get("content"))
    commands = as_text(row.get("commands"))
    examples = as_text(row.get("examples"))
    notes = as_text(row.get("notes"))
    if not full_content:
        sections = []
        for heading, body in (
            ("خلاصه", summary), ("دستورات", commands),
            ("مثال‌ها و Lab", examples), ("نکته‌ها", notes),
        ):
            if body:
                sections.append(f"## {heading}\n{body}")
        full_content = "\n\n".join(sections)
    if not full_content.strip():
        raise ValueError(f"lesson has no usable content: {pack_relative} — {raw_title}")

    meta = row.get("meta") if isinstance(row.get("meta"), dict) else {}
    meta = dict(meta)
    meta.update({
        "reference_source": "NetworkEncyclopedia",
        "reference_pack": pack_relative,
        "source_status": "review_required",
    })
    objectives = as_string_list(row.get("learning_objectives"))
    keywords = as_string_list(row.get("search_keywords"))
    for value in (title_fa, title_en):
        if value and value not in keywords:
            keywords.append(value)

    return {
        "uid": stable_uid(chapter_order, pack_relative, row, existing_uids),
        "title_fa": title_fa,
        "title_en": title_en,
        "level": level,
        "summary": summary,
        "full_content": full_content,
        "commands": commands,
        "examples": examples,
        "notes": notes,
        "meta": meta,
        "learning_objectives": objectives,
        "search_keywords": keywords,
        "search_query": as_text(row.get("search_query")) or " ".join(keywords),
        "source_status": "review_required",
        "subchapter_order": subchapter_order,
        "lesson_order": lesson_order,
        **({"collection": collection} if collection else {}),
    }


def load_curriculum() -> dict[str, Any]:
    if not ASSET.is_file():
        raise SystemExit(f"missing shared curriculum asset: {ASSET}")
    try:
        return json.loads(gzip.decompress(ASSET.read_bytes()).decode("utf-8"))
    except Exception as exc:
        raise SystemExit(f"cannot read shared curriculum JSON/GZIP: {exc}") from exc


def main() -> None:
    if not SOURCE_DIR.is_dir():
        raise SystemExit(f"missing staged reference directory: {SOURCE_DIR}")
    pack_paths = sorted(SOURCE_DIR.glob("*.json"))
    if len(pack_paths) < MIN_EXPECTED_PACKS:
        raise SystemExit(
            f"expected at least {MIN_EXPECTED_PACKS} staged reference packs, found {len(pack_paths)}"
        )

    data = load_curriculum()
    chapters = data.get("chapters")
    if not isinstance(chapters, list):
        raise SystemExit("curriculum chapters must be a list")
    chapter_map: dict[int, dict[str, Any]] = {}
    seen_titles: set[str] = set()
    seen_uids: set[str] = set()
    for chapter in chapters:
        try:
            order = int(chapter.get("order"))
        except (TypeError, ValueError):
            raise SystemExit(f"invalid chapter order: {chapter!r}")
        if order in chapter_map:
            raise SystemExit(f"duplicate chapter order in curriculum: {order}")
        chapter_map[order] = chapter
        for sub in chapter.get("subchapters", []):
            for lesson in sub.get("lessons", []):
                seen_titles.update(title_keys(lesson))
                uid = as_text(lesson.get("uid"))
                if uid:
                    seen_uids.add(uid)

    source_count = added_count = duplicate_count = 0
    per_chapter: dict[int, int] = defaultdict(int)
    per_pack: list[tuple[str, int, int]] = []
    for path in pack_paths:
        try:
            pack = json.loads(path.read_text(encoding="utf-8"))
        except Exception as exc:
            raise SystemExit(f"invalid staged JSON pack {path.relative_to(ROOT)}: {exc}") from exc
        if not isinstance(pack, dict) or not isinstance(pack.get("lessons"), list):
            raise SystemExit(f"pack must contain a lessons array: {path.relative_to(ROOT)}")
        relative = path.relative_to(ROOT).as_posix()
        pack_added = pack_duplicates = 0

        for row in pack["lessons"]:
            if not isinstance(row, dict):
                raise SystemExit(f"non-object lesson in {relative}")
            source_count += 1
            title = as_text(row.get("title_fa") or row.get("title"))
            if not title:
                raise SystemExit(f"lesson missing title_fa in {relative}")
            try:
                chapter_order = int(row.get("chapter_order") or 0)
            except (TypeError, ValueError):
                chapter_order = 0
            if chapter_order not in chapter_map:
                raise SystemExit(f"lesson chapter_order {chapter_order} is not in 1–68: {relative} — {title}")
            keys = title_keys(row)
            if not keys:
                raise SystemExit(f"lesson title cannot be normalized: {relative} — {title}")
            if keys & seen_titles:
                duplicate_count += 1
                pack_duplicates += 1
                continue

            chapter = chapter_map[chapter_order]
            collection = ch68_collection(row) if chapter_order == 68 else None
            subchapter, sub_order = find_or_create_subchapter(chapter, chapter_order, collection)
            new_lesson = normalized_lesson(
                chapter_order, row, relative, seen_uids,
                sub_order, len(subchapter.setdefault("lessons", [])) + 1,
            )
            subchapter["lessons"].append(new_lesson)
            seen_titles.update(keys)
            seen_titles.update(title_keys(new_lesson))
            added_count += 1
            pack_added += 1
            per_chapter[chapter_order] += 1
        per_pack.append((path.name, pack_added, pack_duplicates))

    if source_count == 0:
        raise SystemExit("reference packs contain no lessons")
    if added_count == 0:
        raise SystemExit("no new NetworkEncyclopedia lessons were imported; check title matching")

    data["chapters"].sort(key=lambda item: int(item.get("order") or 0))
    data["lesson_count"] = sum(
        len(sub.get("lessons", []))
        for chapter in data["chapters"]
        for sub in chapter.get("subchapters", [])
    )
    data["version"] = int(data.get("version") or 1) + 1
    raw = json.dumps(data, ensure_ascii=False, separators=(",", ":")).encode("utf-8")
    ASSET.write_bytes(gzip.compress(raw, compresslevel=9, mtime=0))

    print(
        "NetworkEncyclopedia reference import OK: "
        f"packs={len(pack_paths)} source_lessons={source_count} "
        f"added={added_count} duplicate_titles_skipped={duplicate_count} "
        f"total_curriculum_lessons={data['lesson_count']} "
        f"gzip_bytes={ASSET.stat().st_size}"
    )
    print("added by chapter:", dict(sorted(per_chapter.items())))
    for name, added, duplicates in per_pack:
        print(f"  {name}: added={added} duplicates={duplicates}")


if __name__ == "__main__":
    main()
