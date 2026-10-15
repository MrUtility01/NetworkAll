# -*- coding: utf-8 -*-
"""Load chapter-specific lesson builders from each chapter's own authoring folder."""
from __future__ import annotations

import importlib
import importlib.util
import sys
from functools import lru_cache
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
CHAPTERS_DIR = ROOT / "tools" / "chapters"


@lru_cache(maxsize=68)
def _authoring_package(chapter_order: int) -> str:
    if not 1 <= int(chapter_order) <= 68:
        raise ValueError(f"Invalid chapter number: {chapter_order}")
    matches = list(CHAPTERS_DIR.glob(f"ch{int(chapter_order):02d}_*/authoring"))
    if len(matches) != 1:
        raise ImportError(
            f"Expected one authoring folder for chapter {chapter_order}; found {len(matches)}"
        )
    folder = matches[0]
    initializer = folder / "__init__.py"
    if not initializer.is_file():
        raise ImportError(f"Chapter authoring package initializer is missing: {initializer}")
    package_name = f"_networkall_ch{int(chapter_order):02d}_authoring"
    if package_name not in sys.modules:
        spec = importlib.util.spec_from_file_location(
            package_name,
            initializer,
            submodule_search_locations=[str(folder)],
        )
        if spec is None or spec.loader is None:
            raise ImportError(f"Cannot load chapter authoring package: {folder}")
        package = importlib.util.module_from_spec(spec)
        sys.modules[package_name] = package
        spec.loader.exec_module(package)
    return package_name


@lru_cache(maxsize=128)
def load_chapter_authoring(chapter_order: int, module_name: str):
    """Import a named helper module from the selected chapter's authoring directory."""
    if not module_name or "/" in module_name or "\\" in module_name or module_name.endswith(".py"):
        raise ValueError(f"Invalid chapter module name: {module_name!r}")
    package = _authoring_package(int(chapter_order))
    return importlib.import_module(f"{package}.{module_name}")
