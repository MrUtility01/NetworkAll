#!/usr/bin/env bash
# Idempotent migration helper for old checkouts. New content goes directly to tools/packs/.
set -e
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

mkdir -p tools/packs/automation_python
mkdir -p tools/packs/security_ethical_hacking
mkdir -p tools/packs/wireless_security
mkdir -p tools/packs/routing_deep
mkdir -p tools/packs/vpn_enterprise
mkdir -p tools/packs/switching_routing
mkdir -p tools/packs/windows_server
mkdir -p tools/packs/git_chapter64
mkdir -p tools/packs/commands_encyclopedia
mkdir -p tools/engineer_jokar_automation_python
mkdir -p tools/engineer_jokar_security_ethical_hacking
mkdir -p tools/engineer_jokar_wireless_security
mkdir -p tools/_archive_zips

# Legacy loose files: move only if they still exist; never overwrite a canonical pack.
move_if_present() {
  src="$1"; dst="$2"
  if [ -f "$src" ]; then
    if [ -e "$dst" ]; then
      echo "KEEP legacy $src (canonical destination already exists: $dst)"
    else
      mv "$src" "$dst"
      echo "MOVED $src -> $dst"
    fi
  fi
}

move_if_present tools/ENGINEER_JOKAR_OSPF_BGP_Redistribution_deep_v1.json tools/packs/routing_deep/ospf_bgp_redistribution_deep_pack.json
move_if_present tools/ENGINEER_JOKAR_VPN_Enterprise_IPsec_SSL_Troubleshooting_deep_v1.json tools/packs/vpn_enterprise/vpn_enterprise_ipsec_ssl_troubleshooting_pack.json
move_if_present tools/engineer_jokar_automation_python/automation_python_curriculum_pack.json tools/packs/automation_python/automation_python_curriculum_pack.json
move_if_present tools/engineer_jokar_security_ethical_hacking/security_ethical_hacking_pack.json tools/packs/security_ethical_hacking/security_ethical_hacking_pack.json
move_if_present tools/engineer_jokar_wireless_security/wireless_security_pack.json tools/packs/wireless_security/wireless_security_pack.json
move_if_present tools/switching_routing_curriculum_pack.json tools/packs/switching_routing/switching_routing_curriculum_pack.json
move_if_present tools/windows_server_complete_curriculum_pack.json tools/packs/windows_server/windows_server_complete_curriculum_pack.json
move_if_present tools/wireless_security_pack.json tools/packs/wireless_security/wireless_security_pack.json
move_if_present tools/Git_Chapter_64_Full.md tools/packs/git_chapter64/Git_Chapter_64_Full.md

for z in tools/*.zip; do
  [ -f "$z" ] && mv "$z" tools/_archive_zips/ || true
done

echo "Canonical JSON files:"
find tools/packs -type f -name '*.json' | sort
