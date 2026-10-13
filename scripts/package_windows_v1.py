#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Build a clean NetworkAll v1 Windows host/source ZIP from the validated shared curriculum."""
from __future__ import annotations

import gzip
import hashlib
import json
from pathlib import Path
from zipfile import ZIP_DEFLATED, ZipFile

ROOT = Path(__file__).resolve().parents[1]
VERSION = "1.0.0"
ASSET = ROOT / "android/app/src/main/assets/curriculum_index.json.gz"
OUT_DIR = ROOT / "dist"
OUT = OUT_DIR / f"NetworkAll-Windows-v{VERSION}.zip"
PACKAGE_ROOT = f"NetworkAll-Windows-v{VERSION}"
INCLUDE_ROOTS = [
    "server", "windows", "shared", "tools", "scripts", "docs",
    "INSTALL_FA.md", "README.md", "README_FA.txt", "VERSION.txt",
    "android/app/src/main/assets/curriculum_index.json.gz",
]
EXCLUDE_DIRS = {
    ".git", ".venv", "venv", "__pycache__", "node_modules", "build",
    ".gradle", ".idea", ".vscode", "data", "dist", "_archive_zips",
}
EXCLUDE_SUFFIXES = {".pyc", ".pyo", ".apk", ".aab", ".db", ".sqlite", ".sqlite3", ".pem", ".key", ".zip", ".7z", ".rar", ".exe", ".log"}
REQUIRED = [
    "server/app.py",
    "server/core/db.py",
    "server/requirements.txt",
    "windows/start.bat",
    "android/app/src/main/assets/curriculum_index.json.gz",
    "server/static/diagrams/index.json",
    "scripts/export_android_index.py",
    "scripts/merge_content_packs_into_android.py",
    "docs/V1_RELEASE_AUDIT_FA.md",
    "README.md",
    "INSTALL_FA.md",
]


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def curriculum_report() -> dict:
    if not ASSET.is_file():
        raise SystemExit(f"missing shared curriculum asset: {ASSET}")
    if ASSET.stat().st_size < 100_000:
        raise SystemExit(f"curriculum asset suspiciously small: {ASSET.stat().st_size} bytes")
    payload = json.loads(gzip.decompress(ASSET.read_bytes()))
    chapters = payload.get("chapters")
    if not isinstance(chapters, list):
        raise SystemExit("curriculum chapters is not an array")
    orders = {int(ch.get("order", -1)) for ch in chapters}
    if not set(range(1, 69)).issubset(orders):
        raise SystemExit(f"curriculum does not include all chapters 1–68; found {sorted(orders)}")
    actual = sum(
        len(sub.get("lessons", []))
        for ch in chapters
        for sub in ch.get("subchapters", [])
    )
    if int(payload.get("lesson_count", -1)) != actual:
        raise SystemExit(f"lesson_count mismatch declared={payload.get('lesson_count')} actual={actual}")
    uids = []
    for ch in chapters:
        for sub in ch.get("subchapters", []):
            for lesson in sub.get("lessons", []):
                uid = str(lesson.get("uid") or "").strip()
                title = str(lesson.get("title_fa") or "").strip()
                if not uid or not title:
                    raise SystemExit(f"missing UID/title in chapter {ch.get('order')}: {uid!r}")
                uids.append(uid)
    if len(uids) != len(set(uids)):
        raise SystemExit("curriculum contains duplicate lesson UIDs")
    chapter68 = next(ch for ch in chapters if int(ch.get("order")) == 68)
    groups = {
        str(sub.get("title_fa") or "").split("—", 1)[0].strip()
        for sub in chapter68.get("subchapters", [])
    }
    required_groups = {"Linux", "Bash", "PowerShell", "Windows CMD", "Windows Batch"}
    missing = sorted(required_groups - groups)
    if missing:
        raise SystemExit(f"chapter 68 is missing required command collections: {missing}")
    web_diagrams = ROOT / "server/static/diagrams"
    web_index_path = web_diagrams / "index.json"
    if not web_index_path.is_file():
        raise SystemExit(f"missing Windows web diagrams index: {web_index_path}")
    web_index = json.loads(web_index_path.read_text(encoding="utf-8"))
    web_items = web_index.get("diagrams", [])
    if web_index.get("count") != 100 or len(web_items) != 100:
        raise SystemExit(f"Windows web diagram index must contain 100 entries: {web_index.get('count')}")
    if not all((web_diagrams / item.get("asset", "")).is_file() for item in web_items):
        raise SystemExit("Windows web diagram index references a missing SVG")
    return {
        "release_version": VERSION,
        "curriculum_version": payload.get("version"),
        "chapters": len(orders),
        "lessons": actual,
        "chapter68_collections": sorted(groups),
        "diagrams": len(web_items),
        "web_diagram_svg_bytes": sum(p.stat().st_size for p in web_diagrams.glob("*.svg")),
        "asset_compressed_bytes": ASSET.stat().st_size,
    }


def included_files() -> list[Path]:
    found: dict[str, Path] = {}
    for item in INCLUDE_ROOTS:
        path = ROOT / item
        if not path.exists():
            continue
        if path.is_file():
            found[item] = path
            continue
        for f in path.rglob("*"):
            if not f.is_file():
                continue
            rel = f.relative_to(ROOT)
            parts = set(rel.parts)
            if parts & EXCLUDE_DIRS or f.suffix.lower() in EXCLUDE_SUFFIXES:
                continue
            if f.name.lower() in {".env", ".env.local", "secrets.json", "credentials.json"}:
                continue
            if f.name.endswith(".db.bak") or ".bak_" in f.name:
                continue
            found[rel.as_posix()] = f
    return [found[k] for k in sorted(found)]


def main() -> None:
    report = curriculum_report()
    files = included_files()
    missing = [p for p in REQUIRED if p not in {f.relative_to(ROOT).as_posix() for f in files}]
    if missing:
        raise SystemExit(f"Windows package missing required files: {missing}")
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    manifest = {
        **report,
        "package": OUT.name,
        "package_type": "Windows host/source bundle (Python required; not a standalone EXE)",
        "source_files": [],
    }
    with ZipFile(OUT, "w", compression=ZIP_DEFLATED, compresslevel=9) as z:
        for f in files:
            raw = f.read_bytes()
            rel = f.relative_to(ROOT).as_posix()
            z.writestr(f"{PACKAGE_ROOT}/{rel}", raw)
            manifest["source_files"].append({
                "path": rel,
                "bytes": len(raw),
                "sha256": sha256(raw),
            })
        readme = (
            "NetworkAll v1.0.0 — Windows host/source package\n"
            "-----------------------------------------------\n"
            "1) Extract the entire ZIP to a writable folder.\n"
            "2) Install Python 3.11+ and enable 'Add Python to PATH'.\n"
            "3) Open windows\\start.bat. Dependencies are installed on first run.\n"
            "4) Web UI: http://127.0.0.1:86\n"
            "5) The release seeds Windows from the same merged curriculum index as Android.\n"
            "This is a portable source bundle, not a standalone EXE.\n"
            "Back up server\\data before replacing or resetting an existing installation.\n"
        )
        z.writestr(f"{PACKAGE_ROOT}/PACKAGE_README.txt", readme.encode("utf-8"))
        z.writestr(
            f"{PACKAGE_ROOT}/VERSION.txt",
            f"NetworkAll\nVersion: {VERSION}\nPort: 86\nCurriculum chapters: 68\nLessons: {report['lessons']}\n",
        )
        z.writestr(
            f"{PACKAGE_ROOT}/PACKAGE_MANIFEST.json",
            json.dumps(manifest, ensure_ascii=False, indent=2).encode("utf-8"),
        )
    with ZipFile(OUT) as z:
        names = z.namelist()
        for required in REQUIRED:
            if f"{PACKAGE_ROOT}/{required}" not in names:
                raise SystemExit(f"zip verification failed: {required} not found")
        packaged_svg = [
            n for n in names
            if n.startswith(f"{PACKAGE_ROOT}/server/static/diagrams/") and n.endswith(".svg")
        ]
        if len(packaged_svg) != 100:
            raise SystemExit(f"Windows ZIP must contain 100 web SVG diagrams, found {len(packaged_svg)}")
        if any(n.endswith((".db", ".sqlite", ".sqlite3", ".apk", ".aab")) for n in names):
            raise SystemExit("package contains database or install artifacts that must not be bundled")
    print(json.dumps({**report, "output": str(OUT), "package_bytes": OUT.stat().st_size, "files": len(files)}, ensure_ascii=False))


if __name__ == "__main__":
    main()
