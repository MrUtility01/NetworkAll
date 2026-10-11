#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from __future__ import annotations
import gzip, json, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "server"))

from core.full_curriculum import get_full_curriculum
from core.rich_content import build_rich_lesson


def _ensure_chapter_64(curriculum: list) -> list:
    if any(c[0] == 64 for c in curriculum):
        return curriculum
    levels = None
    try:
        from core.chapter64_git_hook import get_git_chapter_levels

        levels = get_git_chapter_levels()
        print("injected chapter 64 Git (full teacher)")
    except Exception as e:
        print("WARN full ch64 teacher:", e)
    if not levels:
        # حداقل یک زیرفصل تا assert و UI خالی نمانند
        levels = [
            (
                "مقدمه Git",
                [
                    ("[L0] Git چیست و چرا مهم است", "What is Git"),
                    ("[L1] نصب و تنظیم اولیه", "Install and config"),
                    ("[L2] commit و branch", "Commit and branch"),
                ],
            )
        ]
        print("injected chapter 64 Git (minimal stub)")
    curriculum.append((64, "فصل ۶۴: Git و GitHub", "Ch64 Git GitHub", levels))
    return curriculum


def main() -> None:
    curriculum = list(get_full_curriculum())
    curriculum = _ensure_chapter_64(curriculum)
    chapters = []
    lesson_count = 0
    for ch in curriculum:
        order, tfa, ten, subs = ch[0], ch[1], ch[2], ch[3]
        sub_out = []
        for si, sub in enumerate(subs):
            sname, lessons = sub[0], sub[1]
            les_out = []
            for li, les in enumerate(lessons):
                if isinstance(les, (list, tuple)) and len(les) >= 2:
                    lfa, len_ = les[0], les[1]
                else:
                    lfa, len_ = str(les), str(les)
                tag = lfa[1:3] if str(lfa).startswith("[L") else "L0"
                rich = build_rich_lesson(lfa, len_, level=tag)
                lesson_count += 1
                uid = f"lesson:ch{int(order):02d}:s{si:03d}:l{li:04d}"
                les_out.append(
                    {
                        "uid": uid,
                        "title_fa": lfa,
                        "title_en": len_,
                        "level": tag,
                        "summary": rich.get("summary") or "",
                        "full_content": rich.get("full_content") or "",
                        "commands": rich.get("commands") or "",
                        "examples": rich.get("examples") or "",
                        "notes": rich.get("notes") or "",
                    }
                )
            sub_out.append({"title_fa": sname, "lessons": les_out})
        chapters.append(
            {"order": int(order), "title_fa": tfa, "title_en": ten, "subchapters": sub_out}
        )
    chapters.sort(key=lambda c: c["order"])
    payload = {"version": 8, "chapters": chapters, "lesson_count": lesson_count}
    raw = json.dumps(payload, ensure_ascii=False, separators=(",", ":")).encode("utf-8")
    out_dir = ROOT / "android" / "app" / "src" / "main" / "assets"
    out_dir.mkdir(parents=True, exist_ok=True)
    out = out_dir / "curriculum_index.json.gz"
    out.write_bytes(gzip.compress(raw, 9))
    print(f"wrote {out} chapters={len(chapters)} lessons={lesson_count} gz={out.stat().st_size}")


if __name__ == "__main__":
    main()
