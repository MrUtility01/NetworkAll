#!/usr/bin/env bash
# One-shot: extract New/*.zip into chapter folders and commit.
# Requires: git write access to origin (CI deploy key or local machine).
set -euo pipefail
cd "$(git rev-parse --show-toplevel)"
bash tools/chapters/New/INTEGRATE.sh
git add tools/chapters/
if git diff --cached --quiet; then
  echo "No changes to commit"
  exit 0
fi
git commit -m "content: integrate enrichment packs from tools/chapters/New (ch22-24,32-33,52,60-67,69-71)"
git push origin HEAD
echo "Pushed successfully"
