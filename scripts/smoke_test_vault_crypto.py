#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Self-contained AES-GCM vault regression smoke test."""
from __future__ import annotations

import base64
import hashlib
import os
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "server"))
import workspace_routes as vault  # noqa: E402


def legacy_enc1(plain: str, token: str) -> str:
    key = hashlib.sha256(token.encode("utf-8")).digest()
    raw = plain.encode("utf-8")
    cipher = bytes(b ^ key[i % len(key)] for i, b in enumerate(raw))
    return "enc1:" + base64.urlsafe_b64encode(cipher).decode("ascii")


def main() -> None:
    with tempfile.TemporaryDirectory(prefix="networkall-vault-test-") as td:
        db_path = Path(td) / "test.db"
        vault._db_path = lambda: db_path
        vault._sync_token = "test-sync-token"
        secret = "NetworkAll vault secret — اختبار التشفير"
        sealed = vault._seal(secret)
        if not sealed.startswith("enc2:") or secret in sealed:
            raise SystemExit("Vault output does not look encrypted")
        if vault._unseal(sealed) != secret:
            raise SystemExit("AES-GCM round trip failed")

        raw = bytearray(base64.urlsafe_b64decode(sealed[5:].encode("ascii")))
        raw[-1] ^= 0x01
        tampered = "enc2:" + base64.urlsafe_b64encode(bytes(raw)).decode("ascii")
        if vault._unseal(tampered) != "••••":
            raise SystemExit("tampered ciphertext was not rejected")

        legacy = legacy_enc1("legacy-secret", vault._sync_token)
        if vault._unseal(legacy) != "legacy-secret":
            raise SystemExit("legacy enc1 compatibility decrypt failed")

        key_file = Path(td) / "networkall.vaultkey"
        key_file.unlink()
        missing = vault._unseal(sealed)
        if "networkall.vaultkey" not in missing or key_file.exists():
            raise SystemExit("missing-key path must warn without silently regenerating a key")

        print("VAULT CRYPTO SMOKE OK: AES-GCM round-trip, tamper rejection, legacy decode, key-loss warning")


if __name__ == "__main__":
    main()
