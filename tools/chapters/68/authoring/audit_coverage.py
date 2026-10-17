#!/usr/bin/env python3
"""Audit Chapter 68 per-technology content quotas without modifying source files.

Usage:
  python tools/chapters/68/authoring/audit_coverage.py
  python tools/chapters/68/authoring/audit_coverage.py --strict

The audit deliberately does not count command flashcards, lab hints, embedded
assessment prompts, or generic descriptions as standalone examples/scenarios/
learning units. Only dedicated records explicitly attributable to a technology
are counted. This prevents inflated or misleading completion claims.
"""
from __future__ import annotations

import argparse
import json
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TARGETS = {
    "mikrotik": "MikroTik RouterOS",
    "cisco": "Cisco IOS / IOS-XE",
    "fortigate": "FortiGate / FortiOS",
    "windows_batch": "Windows Batch / CMD",
    "powershell": "PowerShell",
    "windows_server": "Windows Server / Active Directory",
    "linux": "Linux / Bash",
    "docker": "Docker / Compose",
    "voip": "VoIP / SIP / PBX",
    "vmware_esxi": "VMware ESXi / vSphere",
    "ssh": "SSH / OpenSSH",
    "telnet": "Telnet / TCP diagnostics",
    "ftp": "FTP / FTPS / SFTP",
    "zabbix": "Zabbix",
    "wireshark": "Wireshark / TShark / tcpdump",
    "juniper": "Juniper Junos",
    "aruba": "Aruba AOS-CX",
    "proxmox": "Proxmox VE",
    "hyperv": "Microsoft Hyper-V",
    "ansible": "Ansible",
    "terraform": "Terraform",
    "kubernetes": "Kubernetes / kubectl",
    "ubiquiti": "Ubiquiti UniFi / EdgeOS",
    "snmp_syslog": "SNMP / Syslog / NetFlow / IPFIX",
    "dns_dhcp_ntp": "DNS / DHCP / NTP / IPAM",
    "web_tls": "Nginx / Apache / HTTP(S) / TLS / PKI",
    "cloud": "AWS / Azure",
    "fortinet_management": "FortiManager / FortiAnalyzer",
    "security_ops": "Sysmon / SIEM / SOC",
    "git": "Git / GitHub",
    "backup_recovery": "Backup / Restore / DR",
}
QUOTAS = {"commands": 500, "examples": 100, "scenarios": 100, "learning_units": 500}
COMMAND_FILES = {
    "mikrotik": "commands_mikrotik.json",
    "cisco": "commands_cisco.json",
    "fortigate": "commands_fortigate.json",
    "windows": "commands_windows.json",
    "windows_batch": "commands_windows_batch.json",
    "windows_server": "commands_windows_server.json",
    "linux": "commands_linux.json",
    "docker": "commands_docker.json",
}
ADDITIONAL_FILE = Path("commands/sources/encyclopedia/commands_additional_technologies.json")


def load_json(path: Path):
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def records_from(obj):
    if isinstance(obj, list):
        return obj
    if isinstance(obj, dict):
        for key in ("commands", "examples", "scenarios", "lessons", "items", "questions", "labs", "records"):
            value = obj.get(key)
            if isinstance(value, list):
                return value
    return []


def technology_of(record):
    if not isinstance(record, dict):
        return None
    for key in ("technology_id", "technology", "domain", "vendor_pack", "vendor", "product"):
        value = record.get(key)
        if isinstance(value, str) and value.strip():
            slug = value.strip().lower().replace(" ", "_").replace("/", "_").replace("-", "_")
            if slug in TARGETS:
                return slug
            aliases = {
                "mikrotik_routeros": "mikrotik", "routeros": "mikrotik",
                "cisco_ios": "cisco", "ios_xe": "cisco", "cisco_ios_xe": "cisco",
                "fortios": "fortigate", "fortigate_fortios": "fortigate",
                "powershell_5_1": "powershell", "powershell_7": "powershell",
                "bash": "linux", "linux_bash": "linux",
                "ftp_ftps_sftp": "ftp", "openssh": "ssh",
                "wireshark_tshark": "wireshark", "vmware": "vmware_esxi",
                "windows_server_ad": "windows_server", "cmd": "windows_batch",
                "batch": "windows_batch",
            }
            if slug in aliases:
                return aliases[slug]
    return None


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--strict", action="store_true", help="exit 1 if any technology misses a quota")
    args = parser.parse_args()

    counts = {slug: Counter() for slug in TARGETS}
    missing_files = []
    malformed = []
    command_paths = dict(COMMAND_FILES)
    additional = ROOT / ADDITIONAL_FILE

    for slug, filename in command_paths.items():
        path = ROOT / filename
        if not path.exists():
            missing_files.append(str(path.relative_to(ROOT)))
            continue
        try:
            records = records_from(load_json(path))
            counts[slug]["commands"] += len(records)
        except Exception as exc:
            malformed.append(f"{path.relative_to(ROOT)}: {exc}")

    if additional.exists():
        try:
            for record in records_from(load_json(additional)):
                slug = technology_of(record)
                if slug:
                    counts[slug]["commands"] += 1
        except Exception as exc:
            malformed.append(f"{ADDITIONAL_FILE}: {exc}")
    else:
        missing_files.append(str(ADDITIONAL_FILE))

    # Count only dedicated records with an explicit technology identifier.
    # Embedded flashcards/assessment/lab hints are intentionally not inferred.
    typed_paths = [
        ROOT / "examples" / "examples.json",
        ROOT / "labs" / "labs.json",
        ROOT / "lessons" / "lessons.json",
        ROOT / "lessons" / "base_curriculum.json",
        ROOT / "questions" / "questions.json",
    ]
    for path in typed_paths:
        if not path.exists():
            continue
        try:
            for record in records_from(load_json(path)):
                slug = technology_of(record)
                if not slug:
                    continue
                name = path.parent.name
                if name == "examples":
                    counts[slug]["examples"] += 1
                elif name == "labs":
                    counts[slug]["scenarios"] += 1
                elif name == "lessons":
                    counts[slug]["learning_units"] += 1
        except Exception as exc:
            malformed.append(f"{path.relative_to(ROOT)}: {exc}")

    report = {
        "chapter": 68,
        "status": "review_required",
        "quotas_per_technology": QUOTAS,
        "technology_count": len(TARGETS),
        "technologies": {},
        "missing_source_files": missing_files,
        "parse_errors": malformed,
        "counting_policy": (
            "Only standalone records attributed to a technology count. "
            "Flashcards, embedded assessments, generic hints and duplicated variants do not count as examples/scenarios/learning units."
        ),
    }
    incomplete = []
    for slug, title in TARGETS.items():
        row = {"title": title}
        deficits = {}
        for kind, quota in QUOTAS.items():
            actual = counts[slug][kind]
            row[kind] = actual
            row[f"{kind}_target"] = quota
            row[f"{kind}_missing"] = max(0, quota - actual)
            if actual < quota:
                deficits[kind] = quota - actual
        row["status"] = "target_met_by_count_only_review_required" if not deficits else "in_progress"
        if deficits:
            incomplete.append(slug)
        report["technologies"][slug] = row

    report["incomplete_technology_count"] = len(incomplete)
    report["incomplete_technologies"] = incomplete
    out = ROOT / "authoring" / "coverage_report.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({
        "report": str(out.relative_to(ROOT)),
        "technology_count": len(TARGETS),
        "incomplete_technology_count": len(incomplete),
        "missing_source_files": missing_files,
        "parse_errors": malformed,
    }, ensure_ascii=False, indent=2))
    if malformed or (args.strict and incomplete):
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
