#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Build one shared Android/Windows diagram library from the reference infographic code and curated chapter manifests."""
from __future__ import annotations

import json
import re
import sys
import xml.etree.ElementTree as ET
from collections import Counter
from html import escape
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SERVER = ROOT / "server"
sys.path.insert(0, str(SERVER))
from core.infographics import all_infographics  # noqa: E402

OUT = ROOT / "android/app/src/main/assets/diagrams"
WEB_OUT = ROOT / "server/static/diagrams"
CHAPTER_SOURCE = ROOT / "tools/packs"


def write_svg(path: Path, svg: str) -> None:
    try:
        ET.fromstring(svg)
    except Exception as exc:
        raise SystemExit(f"Invalid SVG generated for {path}: {exc}") from exc
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(svg, encoding="utf-8")


def chapter_svg(title: str, alt: str, chapter: int) -> str:
    """Create a chapter-specific diagram when a manifest points multiple topics at one generic SVG."""
    text = alt or title
    parts = [x.strip(" .؛،") for x in re.split(r"\s*(?:←|→|↔|;|؛|\. )\s*", text) if x.strip(" .؛،")]
    labels = parts[:4]
    if len(labels) < 2:
        labels = [title, "مراحل اصلی", "راستی‌آزمایی"]
    while len(labels) < 3:
        labels.append("کنترل نتیجه")
    labels = [x[:46] for x in labels[:4]]
    width, height = 1100, 390
    xs = [35, 305, 575, 845]
    pieces = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">',
        '<rect width="1100" height="390" rx="20" fill="#f8fafc"/>',
        f'<text x="550" y="42" text-anchor="middle" font-family="Tahoma,Arial,sans-serif" font-size="23" font-weight="700" fill="#0f172a">{escape(title)}</text>',
        f'<text x="550" y="70" text-anchor="middle" font-family="Tahoma,Arial,sans-serif" font-size="14" fill="#475569">فصل {chapter} · نمودار موضوعی</text>',
    ]
    colors = ["#dbeafe", "#dcfce7", "#fef3c7", "#ede9fe"]
    count = len(labels)
    for i, label in enumerate(labels):
        x = xs[i]
        pieces.append(f'<rect x="{x}" y="115" width="220" height="100" rx="14" fill="{colors[i]}" stroke="#64748b" stroke-width="2"/>')
        # Split long labels into two lines to keep them readable on narrow screens.
        words = label.split()
        line1, line2 = "", ""
        for word in words:
            if len((line1 + " " + word).strip()) <= 24:
                line1 = (line1 + " " + word).strip()
            else:
                line2 = (line2 + " " + word).strip()
        pieces.append(f'<text x="{x + 110}" y="157" text-anchor="middle" font-family="Tahoma,Arial,sans-serif" font-size="15" font-weight="600" fill="#0f172a">{escape(line1)}</text>')
        if line2:
            pieces.append(f'<text x="{x + 110}" y="180" text-anchor="middle" font-family="Tahoma,Arial,sans-serif" font-size="13" fill="#0f172a">{escape(line2[:24])}</text>')
        pieces.append(f'<text x="{x + 110}" y="201" text-anchor="middle" font-family="Tahoma,Arial,sans-serif" font-size="11" fill="#334155">مرحله {i + 1}</text>')
        if i < count - 1:
            pieces.append(f'<path d="M {x + 220} 165 H {xs[i + 1] - 12} l -10 -7 m 10 7 l -10 7" fill="none" stroke="#334155" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"/>')
    pieces += [
        '<rect x="35" y="260" width="1030" height="78" rx="12" fill="#e2e8f0"/>',
        f'<text x="550" y="289" text-anchor="middle" font-family="Tahoma,Arial,sans-serif" font-size="15" font-weight="700" fill="#0f172a">راهنمای نمودار</text>',
        f'<text x="550" y="315" text-anchor="middle" font-family="Tahoma,Arial,sans-serif" font-size="13" fill="#334155">{escape((alt or title)[:120])}</text>',
        '</svg>',
    ]
    return "\n".join(pieces)


def normalize_chapter_row(chapter: int, row: dict, asset: str) -> dict:
    return {
        "id": row.get("id", row.get("diagram_id", row.get("diagram_id", row.get("id", row.get("diagram_id", ""))))),
        "title_fa": row.get("title_fa") or f"نمودار فصل {chapter}",
        "collection": row.get("collection") or f"فصل {chapter}",
        "asset": f"ch{chapter:02d}/{asset}",
        "alt_fa": row.get("alt_fa") or row.get("description") or row.get("title_fa") or "",
        "lesson_uid": row.get("lesson_uid") or "",
        "source_status": row.get("source_status") or "review_required",
        "chapter_order": chapter,
    }


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    WEB_OUT.mkdir(parents=True, exist_ok=True)

    # Use the reference repository's actual SVG infographic library rather than
    # generating 100 copies of the same four generic labels.
    generated = all_infographics()
    if len(generated) != 100:
        raise SystemExit(f"Expected 100 reference infographics, got {len(generated)}")
    generic_items = []
    for num, (title, svg) in enumerate(generated, 1):
        filename = f"diagram_{num:03d}.svg"
        write_svg(OUT / filename, svg)
        write_svg(WEB_OUT / filename, svg)
        generic_items.append({
            "id": num,
            "title_fa": title,
            "collection": title,
            "asset": filename,
            "alt_fa": f"اینفوگرافیک آموزشی: {title}",
            "source_status": "review_required",
        })

    # Publish every curated chapter manifest that has real diagram assets.
    # The same normalized index is consumed by Android and the Windows web UI.
    chapter_items_by_order = {}
    manifests = sorted(CHAPTER_SOURCE.glob("ch[0-9][0-9]/diagrams/manifest.json"))
    for manifest_path in manifests:
        match = re.search(r"ch(\d{2})", str(manifest_path.parent.parent.name))
        if not match:
            continue
        chapter = int(match.group(1))
        data = json.loads(manifest_path.read_text(encoding="utf-8"))
        rows = data.get("diagrams") or []
        if not rows:
            continue
        source_dir = manifest_path.parent
        source_keys = []
        for row in rows:
            src_name = row.get("asset_source_file") or row.get("svg_file") or row.get("svg")
            if not src_name:
                continue
            if Path(src_name).name != src_name or not src_name.lower().endswith(".svg"):
                raise SystemExit(f"Unsafe SVG source name in {manifest_path}: {src_name}")
            source_keys.append(src_name)
        duplicate_sources = {name for name, n in Counter(source_keys).items() if n > 1}
        chapter_items = []
        chapter_out = OUT / f"ch{chapter:02d}"
        web_chapter_out = WEB_OUT / f"ch{chapter:02d}"
        chapter_out.mkdir(parents=True, exist_ok=True)
        web_chapter_out.mkdir(parents=True, exist_ok=True)

        for pos, row in enumerate(rows, 1):
            src_name = row.get("asset_source_file") or row.get("svg_file") or row.get("svg")
            if not src_name:
                continue
            src_path = source_dir / src_name
            if not src_path.is_file():
                raise SystemExit(f"Missing curated SVG source: {src_path}")

            # Chapter 2's current manifest maps 12 distinct topics to one shared
            # overview SVG. Render those entries from their own title/alt text
            # so the gallery does not falsely display the same picture 12 times.
            if src_name in duplicate_sources:
                filename = f"diagram_{pos:02d}.svg"
                svg = chapter_svg(
                    row.get("title_fa") or f"فصل {chapter}",
                    row.get("alt_fa") or row.get("title_fa") or "",
                    chapter,
                )
            else:
                filename = src_name
                svg = src_path.read_text(encoding="utf-8")
            write_svg(chapter_out / filename, svg)
            write_svg(web_chapter_out / filename, svg)
            chapter_items.append(normalize_chapter_row(chapter, row, filename))

        if chapter_items:
            chapter_index = {"version": 1, "chapter_order": chapter, "count": len(chapter_items), "diagrams": chapter_items}
            text = json.dumps(chapter_index, ensure_ascii=False, indent=2)
            (chapter_out / "index.json").write_text(text, encoding="utf-8")
            (web_chapter_out / "index.json").write_text(text, encoding="utf-8")
            chapter_items_by_order[chapter] = chapter_items

    # Legacy root index remains the 100-item general collection.
    root_index = {"version": 1, "count": len(generic_items), "diagrams": generic_items}
    (OUT / "index.json").write_text(json.dumps(root_index, ensure_ascii=False, indent=2), encoding="utf-8")
    (WEB_OUT / "index.json").write_text(json.dumps(root_index, ensure_ascii=False, indent=2), encoding="utf-8")

    combined = list(generic_items)
    for chapter in sorted(chapter_items_by_order):
        combined.extend(chapter_items_by_order[chapter])
    combined_index = {"version": 1, "count": len(combined), "diagrams": combined}
    combined_text = json.dumps(combined_index, ensure_ascii=False, indent=2)
    (OUT / "combined_index.json").write_text(combined_text, encoding="utf-8")
    (WEB_OUT / "combined_index.json").write_text(combined_text, encoding="utf-8")

    expected = {1: 41, 2: 12, 3: 10, 9: 8}
    for chapter, count in expected.items():
        actual = len(chapter_items_by_order.get(chapter, []))
        if actual != count:
            raise SystemExit(f"Chapter {chapter} diagrams expected {count}, got {actual}")
    expected_combined = 100 + sum(expected.values())
    if len(combined) != expected_combined:
        raise SystemExit(f"Expected {expected_combined} combined diagrams, got {len(combined)}")
    for item in combined:
        for root in (OUT, WEB_OUT):
            path = root / item["asset"]
            if not path.is_file():
                raise SystemExit(f"Missing published diagram: {path}")
            try:
                ET.parse(path)
            except Exception as exc:
                raise SystemExit(f"Invalid published SVG {path}: {exc}") from exc

    print(
        f"Generated shared library: general={len(generic_items)}; "
        f"chapter_counts={{{', '.join(f'{k}: {len(v)}' for k, v in sorted(chapter_items_by_order.items()))}}}; "
        f"combined={len(combined)}; Android and web assets validated."
    )


if __name__ == "__main__":
    main()
