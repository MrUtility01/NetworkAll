# -*- coding: utf-8 -*-
"""فصل‌های ۶۴–۶۸ مکمل هستهٔ ۱–۶۳ برای seed ویندوز و export."""
from __future__ import annotations
from pathlib import Path
import json

ROOT = Path(__file__).resolve().parents[2]


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

    # Shared deep curriculum overlay for chapters 60–68. This same index is used
    # by Windows/Flask and the Android offline export; existing lessons/UIDs stay intact.
    overlay_path = ROOT / "tools" / "packs" / "ch60_68" / "chapter_60_68_deep_pack.json"
    try:
        overlay = json.loads(overlay_path.read_text(encoding="utf-8"))
        for chapter in overlay.get("chapters", []):
            order = int(chapter.get("chapter_order") or 0)
            if order not in by:
                continue
            record = by[order]
            subs = list(record[3])
            existing = {title for sub in subs for title, _ in sub[1]}
            pack_lessons = [
                (item.get("title_fa", ""), item.get("title_en", ""))
                for item in overlay.get("lessons", [])
                if int(item.get("chapter_order") or 0) == order
                and item.get("title_fa") not in existing
            ]
            if pack_lessons:
                subs.append(("غنی‌سازی و اعتبارسنجی", pack_lessons))
                by[order] = (record[0], record[1], record[2], subs)
    except (OSError, ValueError, TypeError):
        # Keep the base curriculum available if an optional overlay is malformed.
        pass

    return [by[k] for k in sorted(by)]
