#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Validate the shared Android/Windows SVG library and mixed-ID Android gallery contract."""
from __future__ import annotations

import json
import re
import xml.etree.ElementTree as ET
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ANDROID = ROOT / "android/app/src/main/assets/diagrams"
WEB = ROOT / "server/static/diagrams"
GALLERY = ROOT / "android/app/src/main/java/com/netenc/app/DiagramGalleryActivity.kt"


def read_json(base: Path, relative: str) -> dict:
    return json.loads((base / relative).read_text(encoding="utf-8"))


def validate_index(base: Path, index_path: str, expected_count: int | None = None) -> list[dict]:
    index = read_json(base, index_path)
    rows = index.get("diagrams")
    assert isinstance(rows, list), f"{base / index_path}: diagrams must be a list"
    assert index.get("count") == len(rows), f"{base / index_path}: count does not match rows"
    if expected_count is not None:
        assert len(rows) == expected_count, f"{base / index_path}: expected {expected_count}, got {len(rows)}"
    for row in rows:
        asset = row.get("asset")
        assert isinstance(asset, str) and asset and not asset.startswith("/"), f"Invalid asset path: {asset!r}"
        assert ".." not in Path(asset).parts, f"Unsafe asset path: {asset}"
        path = base / asset
        assert path.is_file(), f"Missing SVG: {path}"
        assert path.suffix.lower() == ".svg", f"Not an SVG asset: {path}"
        ET.parse(path)
        assert row.get("title_fa"), f"Missing Persian title for {asset}"
    return rows


def main() -> None:
    general = validate_index(ANDROID, "index.json", 100)
    web_general = validate_index(WEB, "index.json", 100)
    assert [r["asset"] for r in general] == [r["asset"] for r in web_general]

    chapter_counts = {1: 41, 2: 12, 3: 10, 9: 8}
    chapter_rows: list[dict] = []
    for chapter, expected in chapter_counts.items():
        rel = f"ch{chapter:02d}/index.json"
        rows = validate_index(ANDROID, rel, expected)
        web_rows = validate_index(WEB, rel, expected)
        assert [r["asset"] for r in rows] == [r["asset"] for r in web_rows], f"Android/web mismatch: {rel}"
        assert all(int(r.get("chapter_order", 0)) == chapter for r in rows), f"Wrong chapter metadata: {rel}"
        chapter_rows.extend(rows)

    combined = validate_index(ANDROID, "combined_index.json", 100 + len(chapter_rows))
    web_combined = validate_index(WEB, "combined_index.json", 100 + len(chapter_rows))
    assert [r["asset"] for r in combined] == [r["asset"] for r in web_combined], "Combined Android/web indexes differ"

    # The general catalog uses integer IDs; curated chapter manifests use string IDs.
    id_types = {type(row.get("id")) for row in combined}
    assert int in id_types and str in id_types, f"Regression fixture missing mixed ID types: {id_types}"
    gallery = GALLERY.read_text(encoding="utf-8")
    assert "private fun displayId(" in gallery, "Gallery must format numeric and string diagram IDs safely"
    assert not re.search(r'getInt\(\s*"id"\s*\)', gallery), "Unsafe getInt(id) breaks string IDs from chapter manifests"

    print(
        f"Diagram validation passed: general={len(general)}; "
        f"chapter_counts={chapter_counts}; combined={len(combined)}; "
        f"mixed_id_types={','.join(sorted(t.__name__ for t in id_types))}; "
        "all Android/web SVG files parse and gallery ID handling is safe."
    )


if __name__ == "__main__":
    main()
