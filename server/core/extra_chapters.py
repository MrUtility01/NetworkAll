# -*- coding: utf-8 -*-
"""فصل‌های ۶۴–۶۸ مکمل هستهٔ ۱–۶۳ برای seed ویندوز و export."""
from __future__ import annotations
from pathlib import Path
import json
import runpy

ROOT = Path(__file__).resolve().parents[2]


def _ensure_deep_packs() -> None:
    """Create the canonical shared 60-68 packs if files are absent or placeholders."""
    pack_dir = ROOT / "tools" / "packs" / "ch60_68"
    names = (
        "ch60_68_ch60_pack.json",
        "ch60_68_ch61_63_pack.json",
        "ch60_68_ch64_68_pack.json",
    )
    try:
        valid = True
        total = 0
        for name in names:
            path = pack_dir / name
            if not path.is_file() or path.stat().st_size < 1000:
                valid = False
                break
            data = json.loads(path.read_text(encoding="utf-8"))
            lessons = data.get("lessons") or []
            if not lessons:
                valid = False
                break
            total += len(lessons)
        if valid and total >= 800:
            return
        generator = ROOT / "tools" / "generate_ch60_68_packs.py"
        if generator.is_file():
            runpy.run_path(str(generator), run_name="__main__")
    except (OSError, ValueError, TypeError, RuntimeError) as exc:
        # Preserve the existing curriculum if a read-only deployment cannot generate packs.
        print("ch60_68 pack generation skipped:", exc)


def _minimal(title_fa: str, title_en: str):
    return [
        (
            "مقدمه",
            [
                (f"[L0] {title_fa} — آشنایی", f"[L0] {title_en} — Intro"),
                (f"[L1] {title_fa} — مبانی", f"[L1] {title_en} — Basics"),
                (f"[L2] {title_fa} — پیاده‌سازی", f"[L2] {title_en} — Implement"),
            ],
        )
    ]


def _git_levels():
    try:
        from core.chapter64_git_hook import get_git_chapter_levels

        return get_git_chapter_levels()
    except Exception:
        return _minimal("Git و GitHub", "Git GitHub")


def _lessons_from_pack_json(path: Path, limit: int = 200):
    if not path.is_file():
        return None
    try:
        d = json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return None
    items = []
    if d.get("commands"):
        for i, c in enumerate(d["commands"][:limit], 1):
            if not isinstance(c, dict):
                continue
            cmd = c.get("command") or c.get("title_en") or f"cmd-{i}"
            title = c.get("title_fa") or cmd
            level = c.get("level") or "L1"
            if not str(title).startswith("["):
                title = f"[{level}] {title}"
            items.append((title, c.get("title_en") or cmd))
    elif d.get("lessons"):
        for i, les in enumerate(d["lessons"][:limit], 1):
            if not isinstance(les, dict):
                continue
            title = les.get("title_fa") or f"lesson-{i}"
            items.append((title, les.get("title_en") or title))
    if not items:
        return None
    return [("محتوای پک", items)]


def ensure_chapters_1_to_68(curriculum: list) -> list:
    # The generator is shared by Android export and Windows/Flask seeding.
    _ensure_deep_packs()
    by = {int(c[0]): c for c in curriculum}
    if 64 not in by:
        by[64] = (64, "فصل ۶۴: Git و GitHub", "Ch64 Git GitHub", _git_levels())
    if 65 not in by:
        by[65] = (
            65,
            "فصل ۶۵: امنیت سایبری و هک اخلاقی (دفاعی) + بی‌سیم",
            "Ch65 Security Wireless",
            _minimal("امنیت دفاعی و وایرلس", "Security Wireless"),
        )
    if 66 not in by:
        by[66] = (
            66,
            "فصل ۶۶: مسیریابی عمیق OSPF/BGP/Redistribution",
            "Ch66 Routing Deep",
            _minimal("مسیریابی عمیق", "Deep Routing"),
        )
    if 67 not in by:
        by[67] = (
            67,
            "فصل ۶۷: VPN سازمانی IPsec/SSL و عیب‌یابی",
            "Ch67 Enterprise VPN",
            _minimal("VPN سازمانی", "Enterprise VPN"),
        )
    if 68 not in by:
        packs = ROOT / "tools" / "packs" / "commands_encyclopedia"
        levels = None
        for name in ("cisco_switching.json", "mikrotik.json"):
            lv = _lessons_from_pack_json(packs / name, limit=150)
            if lv:
                levels = levels or []
                levels.append((name.replace(".json", ""), lv[0][1]))
        if not levels:
            levels = _minimal("دانشنامه دستورات", "Commands Encyclopedia")
        by[68] = (
            68,
            "فصل ۶۸: دانشنامه جامع دستورات",
            "Ch68 Commands Encyclopedia",
            levels,
        )

    # Load every shared chapter 60-68 content pack, including generated add-ons.
    overlay_paths = sorted((ROOT / "tools" / "packs" / "ch60_68").glob("*pack*.json"))
    for overlay_path in overlay_paths:
        try:
            overlay = json.loads(overlay_path.read_text(encoding="utf-8"))
            chapter_records = overlay.get("chapters") or overlay.get("scope") or []
            if not chapter_records:
                chapter_records = [
                    {"chapter_order": order}
                    for order in sorted({
                        int(item.get("chapter_order") or 0)
                        for item in overlay.get("lessons", [])
                        if int(item.get("chapter_order") or 0) in by
                    })
                ]
            for chapter in chapter_records:
                order = int(chapter.get("chapter_order") or 0)
                if order not in by:
                    continue
                record = by[order]
                subs = list(record[3])
                existing = {title for sub in subs for title, _ in sub[1]}
                additions = []
                for item in overlay.get("lessons", []):
                    if int(item.get("chapter_order") or 0) == order:
                        title = item.get("title_fa") or ""
                        if title and title not in existing:
                            additions.append((title, item.get("title_en") or title))
                            existing.add(title)
                if additions:
                    subs.append(("غنی‌سازی و اعتبارسنجی", additions))
                    by[order] = (record[0], record[1], record[2], subs)
        except (OSError, ValueError, TypeError):
            continue

    return [by[k] for k in sorted(by)]
