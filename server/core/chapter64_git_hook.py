# -*- coding: utf-8 -*-
"""Hook فصل ۶۴ Git — بارگذاری از tools/chapter_git_teacher.py"""
from __future__ import annotations
from pathlib import Path
import sys

def _load():
    try:
        from core import chapter_git_teacher as m
        return m
    except Exception:
        pass
    root = Path(__file__).resolve().parents[2]
    candidates = [
        root / "tools" / "chapter_git_teacher.py",
        root / "tools" / "chapters" / "ch64_git_github" / "authoring" / "chapter_git_teacher.py",
    ]
    for candidate in candidates:
        if not candidate.is_file():
            continue
        if str(candidate.parent) not in sys.path:
            sys.path.insert(0, str(candidate.parent))
        import importlib.util
        spec = importlib.util.spec_from_file_location("chapter_git_teacher", candidate)
        if spec is None or spec.loader is None:
            continue
        module = importlib.util.module_from_spec(spec)
        sys.modules["chapter_git_teacher"] = module
        spec.loader.exec_module(module)
        return module
    raise ImportError("chapter_git_teacher.py was not found in its canonical chapter folder")

def get_git_chapter_levels():
    return _load().get_git_chapter_levels()

def is_git_title(title: str) -> bool:
    return _load().is_git_title(title)

def build_git_lesson(title_fa: str, title_en: str = ""):
    return _load().build_git_lesson(title_fa, title_en)
