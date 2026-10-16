#!/usr/bin/env bash
# Extract ch68 command encyclopedia from zip into canonical path
set -euo pipefail
CH68="$(cd "$(dirname "$0")/../../.." && pwd)"
ZIP="$CH68/ch68_all_domains.zip"
DEST="$CH68/commands/sources/encyclopedia"

if [[ ! -f "$ZIP" ]]; then
  echo "ZIP not found: $ZIP" >&2
  exit 1
fi

mkdir -p "$DEST"
TMP=$(mktemp -d)
unzip -qo "$ZIP" -d "$TMP"
if [[ -d "$TMP/ch68_commands_encyclopedia" ]]; then
  cp -f "$TMP"/ch68_commands_encyclopedia/* "$DEST"/
else
  cp -f "$TMP"/* "$DEST"/ 2>/dev/null || true
fi
rm -rf "$TMP"

BAD="$CH68/commands/sources/tools"
if [[ -d "$BAD" ]]; then
  echo "Removing nested bad path: $BAD"
  rm -rf "$BAD"
fi

echo "Extracted to $DEST"
ls -la "$DEST" | head
