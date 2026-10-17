#!/usr/bin/env bash
# Extract ZIPs from tools/chapters/New into proper chapter folders.
set -euo pipefail
CHROOT="$(cd "$(dirname "$0")/.." && pwd)"
NEW="$(cd "$(dirname "$0")" && pwd)"
WORKDIR=$(mktemp -d)
trap 'rm -rf "$WORKDIR"' EXIT

echo "CHROOT=$CHROOT"
echo "NEW=$NEW"

copy_pack() {
  local ch="$1"
  local src="$2"
  if [[ ! -d "$src" ]]; then
    echo "SKIP $ch (missing $src)"
    return 0
  fi
  echo "=== Integrating chapter $ch ==="
  mkdir -p "$CHROOT/$ch/lessons" "$CHROOT/$ch/questions" "$CHROOT/$ch/answers" \
           "$CHROOT/$ch/labs" "$CHROOT/$ch/examples" "$CHROOT/$ch/commands"
  for f in lessons/lessons.json questions/questions.json answers/answer_key.json \
           labs/labs.json examples/examples.json commands/commands.json; do
    if [[ -f "$src/$f" ]]; then
      cp -f "$src/$f" "$CHROOT/$ch/$f"
      echo "  + $f"
    fi
  done
  if [[ -f "$src/lessons/base_curriculum.json" ]]; then
    cp -f "$src/lessons/base_curriculum.json" "$CHROOT/$ch/lessons/base_curriculum.json"
    echo "  + base_curriculum.json"
  fi
  if [[ -f "$src/VALIDATION.md" ]]; then
    cp -f "$src/VALIDATION.md" "$CHROOT/$ch/VALIDATION_ENRICHMENT.md"
  fi
  if [[ "$ch" -ge 69 ]]; then
    mkdir -p "$CHROOT/$ch"
    cp -a "$src/." "$CHROOT/$ch/"
    echo "  + full tree (new chapter)"
  fi
}

unzip_one() {
  local zippath="$1"
  if [[ -f "$zippath" ]]; then
    echo "Unzip: $zippath"
    unzip -qo "$zippath" -d "$WORKDIR"
  fi
}

cd "$WORKDIR"
unzip_one "$NEW/ch22_wifi_enrichment.zip"
unzip_one "$NEW/ch23_ptp_ptmp_enrichment.zip"
unzip_one "$NEW/ch24_fortigate_enrichment.zip"
unzip_one "$NEW/ch32_endpoint_sec_enrichment.zip"
unzip_one "$NEW/ch33_entra_hybrid_enrichment.zip"
unzip_one "$NEW/ch52_dba_10x.zip"
for z in "$NEW"/ch60_67_enrichment_all*.zip; do [[ -f "$z" ]] && unzip_one "$z"; done
unzip_one "$NEW/ch69_70_all.zip"
for z in "$NEW"/ch69_web_coding*.zip "$NEW"/ch70_ai_web_coding*.zip "$NEW"/ch71*.zip; do
  [[ -f "$z" ]] && unzip_one "$z"
done

copy_pack 22 "$WORKDIR/ch22_wifi_enrichment"
copy_pack 23 "$WORKDIR/ch23_ptp_ptmp_enrichment"
copy_pack 24 "$WORKDIR/ch24_fortigate_enrichment"
copy_pack 32 "$WORKDIR/ch32_endpoint_sec_enrichment"
copy_pack 33 "$WORKDIR/ch33_entra_hybrid_enrichment"
copy_pack 52 "$WORKDIR/ch52_dba_10x"
copy_pack 60 "$WORKDIR/ch60_ethical_lab_enrichment"
copy_pack 61 "$WORKDIR/ch61_ent_arch_enrichment"
copy_pack 62 "$WORKDIR/ch62_it_noc_enrichment"
copy_pack 63 "$WORKDIR/ch63_runbook_cmdb_enrichment"
copy_pack 64 "$WORKDIR/ch64_git_enrichment"
copy_pack 65 "$WORKDIR/ch65_cyber_def_enrichment"
copy_pack 66 "$WORKDIR/ch66_ospf_bgp_enrichment"
copy_pack 67 "$WORKDIR/ch67_vpn_enrichment"
copy_pack 69 "$WORKDIR/ch69_web_coding"
copy_pack 70 "$WORKDIR/ch70_ai_web_coding"
copy_pack 71 "$WORKDIR/ch71_ai_leadership_it"

echo "DONE. Run: git add tools/chapters && git status"
