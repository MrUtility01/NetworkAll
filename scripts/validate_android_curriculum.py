#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Structural and content-quality checks for the NetworkAll Android curriculum asset."""
from __future__ import annotations

import gzip
import json
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ASSET = ROOT / "android/app/src/main/assets/curriculum_index.json.gz"


def fail(message: str) -> None:
    print(f"ERROR: {message}", file=sys.stderr)
    raise SystemExit(1)


def main() -> None:
    if not ASSET.is_file():
        fail(f"missing Android curriculum asset: {ASSET}")
    if ASSET.stat().st_size < 1024:
        fail(f"asset is suspiciously small: {ASSET.stat().st_size} bytes")
    try:
        with gzip.open(ASSET, "rt", encoding="utf-8") as stream:
            data = json.load(stream)
    except Exception as exc:
        fail(f"gzip/JSON decode failed: {exc}")

    chapters = data.get("chapters")
    if not isinstance(chapters, list) or not chapters:
        fail("chapters must be a non-empty array")
    orders = []
    lessons = []
    chapter_counts = {}
    for chapter in chapters:
        if not isinstance(chapter, dict):
            fail("chapter entry is not an object")
        try:
            order = int(chapter["order"])
        except Exception:
            fail("chapter is missing a numeric order")
        orders.append(order)
        if not str(chapter.get("title_fa") or "").strip():
            fail(f"chapter {order} has no Persian title")
        subs = chapter.get("subchapters")
        if not isinstance(subs, list):
            fail(f"chapter {order} subchapters must be an array")
        count = 0
        for sub in subs:
            if not isinstance(sub, dict) or not str(sub.get("title_fa") or "").strip():
                fail(f"chapter {order} has a malformed/untitled subchapter")
            items = sub.get("lessons")
            if not isinstance(items, list):
                fail(f"chapter {order} lesson list is malformed")
            for lesson in items:
                if not isinstance(lesson, dict):
                    fail(f"chapter {order} contains a non-object lesson")
                lessons.append((order, lesson))
                count += 1
        chapter_counts[order] = count

    if len(orders) != len(set(orders)):
        fail("duplicate chapter order")
    missing = sorted(set(range(1, 69)) - set(orders))
    if missing:
        fail(f"required chapters missing: {missing}")
    if int(data.get("lesson_count", -1)) != len(lessons):
        fail(f"lesson_count={data.get('lesson_count')} but actual={len(lessons)}")

    uids = []
    empty_titles = []
    empty_content = []
    thin_content = []
    depth_by_chapter = {}
    source_status_counts = Counter()
    assessments_by_chapter = Counter()
    for order, lesson in lessons:
        uid = str(lesson.get("uid") or "").strip()
        title = str(lesson.get("title_fa") or "").strip()
        full = str(lesson.get("full_content") or "").strip()
        if not uid:
            fail(f"chapter {order} has a lesson without uid")
        uids.append(uid)
        if not title:
            empty_titles.append(uid)
        if not full:
            empty_content.append(uid)
        if len(full) < 120:
            thin_content.append(uid)
        band = "deep" if len(full) >= 2000 else ("mid" if len(full) >= 800 else "thin")
        depth_by_chapter.setdefault(order, Counter())[band] += 1
        source_status_counts[str(lesson.get("source_status") or "missing")] += 1
        meta = lesson.get("meta") if isinstance(lesson.get("meta"), dict) else {}
        if isinstance(meta.get("assessment"), dict) and meta["assessment"]:
            assessments_by_chapter[order] += 1

    if len(uids) != len(set(uids)):
        duplicates = [uid for uid, n in Counter(uids).items() if n > 1]
        fail(f"duplicate lesson uid(s), examples: {duplicates[:8]}")
    if empty_titles:
        fail(f"{len(empty_titles)} lessons have no title; examples: {empty_titles[:8]}")
    if len(empty_content) > max(3, int(len(lessons) * 0.01)):
        fail(f"{len(empty_content)}/{len(lessons)} lessons have empty full_content")

    print(
        "VALID NetworkAll curriculum: "
        f"asset_version={data.get('version')} release={data.get('release_version')} "
        f"chapters={len(orders)} lessons={len(lessons)} chapter68={chapter_counts.get(68, 0)} "
        f"empty_content={len(empty_content)} very_short(<120 chars)={len(thin_content)} "
        f"gzip_bytes={ASSET.stat().st_size}"
    )
    print("QUALITY SUMMARY (length only, not a factual review):")
    total_depth = Counter()
    for count in depth_by_chapter.values():
        total_depth.update(count)
    print("  all chapters:", dict(total_depth))
    for order in sorted(depth_by_chapter):
        bands = depth_by_chapter[order]
        total = sum(bands.values())
        if bands.get("thin", 0):
            print(f"  chapter {order:02d}: lessons={total} thin(<800)={bands.get('thin',0)} mid(800-1999)={bands.get('mid',0)} deep(>=2000)={bands.get('deep',0)}")
    print("  lessons with meta.assessment:", sum(assessments_by_chapter.values()), "/", len(lessons))
    print("  source_status counts:", dict(source_status_counts))
    if chapter_counts.get(68, 0) == 0:
        fail("chapter 68 has no command lessons")

    # Chapter 68 must remain navigable by platform/collection, not just a flat
    # list of similarly named commands.
    chapter68 = next((ch for ch in chapters if int(ch.get("order", 0)) == 68), {})
    groups = chapter68.get("subchapters", [])
    group_titles = [str(s.get("title_fa") or "").split("—", 1)[0].strip() for s in groups]
    required_groups = {"Linux", "Bash", "PowerShell", "Windows CMD", "Windows Batch"}
    missing_groups = sorted(required_groups - set(group_titles))
    if missing_groups:
        fail(f"chapter 68 missing command collections: {missing_groups}")
    chapter68 = next((ch for ch in chapters if int(ch.get("order", 0)) == 68), {})
    ch68_lessons = [les for order, les in lessons if order == 68]
    unlabeled = []
    empty_groups = []
    for sub in chapter68.get("subchapters", []):
        group = str(sub.get("title_fa") or "").split("—", 1)[0].strip()
        group_lessons = sub.get("lessons", [])
        if not group_lessons:
            empty_groups.append(group)
            continue
        expected_prefix = f"[{group}]"
        for lesson in group_lessons:
            title = str(lesson.get("title_fa") or "").strip()
            if not title.startswith(expected_prefix):
                unlabeled.append({"uid": lesson.get("uid"), "expected": expected_prefix, "title": title[:100]})
    if empty_groups:
        fail(f"chapter 68 contains empty command collections: {empty_groups[:8]}")
    if unlabeled:
        fail(f"chapter 68 lesson title does not match its collection (examples): {unlabeled[:8]}")

    if thin_content:
        print("QUALITY WARNING: thin lesson examples (first 10 uids):", thin_content[:10])


if __name__ == "__main__":
    main()
