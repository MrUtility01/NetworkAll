# -*- coding: utf-8 -*-
"""فصل ۶۴: پل سازگاری به موتور درس Git مستقر در پوشهٔ فصل ۶۴."""
from __future__ import annotations


def _load():
    from core.chapter_loader import load_chapter_authoring
    return load_chapter_authoring(64, "chapter_git_teacher")


def get_git_chapter_levels():
    return _load().get_git_chapter_levels()


def is_git_title(title: str) -> bool:
    return _load().is_git_title(title)


def build_git_lesson(title_fa: str, title_en: str = ""):
    return _load().build_git_lesson(title_fa, title_en)
