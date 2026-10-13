#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Fail the release if runtime-facing project identity, port, or token defaults regress."""
from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ERRORS: list[str] = []


def read(rel: str) -> str:
    path = ROOT / rel
    if not path.is_file():
        ERRORS.append(f"missing required file: {rel}")
        return ""
    return path.read_text(encoding="utf-8")


def require(condition: bool, message: str) -> None:
    if not condition:
        ERRORS.append(message)


readme = read("README.md")
version = read("VERSION.txt")
gradle = read("android/app/build.gradle.kts")
settings = read("android/settings.gradle.kts")
manifest = read("android/app/src/main/AndroidManifest.xml")
server = read("server/app.py")
launcher = read("windows/start.bat")
android_settings = read("android/app/src/main/java/com/netenc/app/SettingsActivity.kt")

require("# NetworkAll" in readme and "NetworkAll v1.0.0" in readme, "README.md does not declare NetworkAll v1.0.0")
require("Version: 1.0.0" in version and "Port: 86" in version, "VERSION.txt version/port mismatch")
require('versionName = "1.0.0"' in gradle and re.search(r"versionCode = \d+", gradle), "Android Gradle version metadata missing")
require('rootProject.name = "NetworkAll"' in settings, "Gradle root project name is not NetworkAll")
require('android:label="NetworkAll"' in manifest, "Android launcher label is not NetworkAll")
require('os.environ.get("PORT", "86")' in server, "Flask default port is not TCP/86")
require('set NETENC_PORT=86' in launcher, "Windows launcher does not default to TCP/86")
require('const val DEFAULT_TOKEN = ""' in android_settings, "Android must not ship a hard-coded API token")

runtime_paths = [
    "server/app.py",
    "server/static/sync_ui.js",
    "server/templates/index.html",
    "windows/start.bat",
    "android/app/src/main/java/com/netenc/app/SettingsActivity.kt",
    "android/app/src/main/java/com/netenc/app/MainActivity.kt",
    "android/app/src/main/res/layout/activity_main.xml",
]
for rel in runtime_paths:
    text = read(rel)
    if "09136555866" in text:
        ERRORS.append(f"{rel} embeds the retired fixed token")
    if "5050" in text:
        ERRORS.append(f"{rel} contains the retired port 5050")

public_docs = [
    "README.md", "README_FA.txt", "INSTALL_FA.md", "windows/README.md",
    "android/README.md", "server/README.md", "docs/REPO_LAYOUT_FA.md",
]
for rel in public_docs:
    text = read(rel)
    if "MrUtility01/NetworkEncyclopedia" in text or "NetworkEncyclopedia.git" in text:
        ERRORS.append(f"{rel} still points users at the old repository")
    if "127.0.0.1:5050" in text or "IP-ویندوز:5050" in text:
        ERRORS.append(f"{rel} still instructs users to use port 5050")

workflow = read(".github/workflows/build-apk.yml")
require("NetworkAll-Android-v1.0.0" in workflow, "workflow does not publish the versioned Android artifact")
require("NetworkAll-Windows-v1.0.0" in workflow, "workflow does not publish the versioned Windows artifact")

if ERRORS:
    print("RELEASE METADATA VALIDATION FAILED")
    for err in ERRORS:
        print(" -", err)
    raise SystemExit(1)
print("RELEASE METADATA VALID: NetworkAll v1.0.0, TCP/86, no fixed sync-token defaults, versioned dual-platform artifacts")
