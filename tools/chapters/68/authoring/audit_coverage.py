#!/usr/bin/env python3
"""Audit Chapter 68 quotas from canonical JSON packs.

Counts unique command records by technology and standalone example/lab/lesson
records only when attribution can be established from structured metadata,
lesson_uid, title, or an explicit **حوزه:** marker in the record body.
Writes authoring/coverage_report.json. --strict returns non-zero for any deficit.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TARGETS = {
    "mikrotik": "MikroTik RouterOS",
    "cisco": "Cisco IOS / IOS-XE",
    "fortigate": "FortiGate / FortiOS",
    "windows_batch": "Windows Batch / CMD",
    "powershell": "PowerShell 5.1 / 7+",
    "windows_server": "Windows Server / Active Directory",
    "linux_bash": "Linux / Bash / GNU utilities",
    "docker": "Docker / Compose",
    "voip": "VoIP / SIP / PBX",
    "vmware_esxi": "VMware ESXi / vSphere",
    "ssh": "SSH / OpenSSH",
    "telnet": "Telnet / TCP diagnostics",
    "ftp": "FTP (plain FTP)",
    "ftps": "FTPS (FTP over TLS)",
    "sftp": "SFTP (SSH File Transfer Protocol)",
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
    "windows_batch": "commands_windows_batch.json",
    "windows_server": "commands_windows_server.json",
    "linux_bash": "commands_linux.json",
    "docker": "commands_docker.json",
}
ADDITIONAL_FILE = Path("commands/sources/encyclopedia/commands_additional_technologies.json")
ALIASES = {
    "routeros": "mikrotik", "mikrotik_routeros": "mikrotik",
    "cisco_ios": "cisco", "ios_xe": "cisco", "cisco_ios_xe": "cisco",
    "fortios": "fortigate", "fortigate_fortios": "fortigate",
    "powershell_5_1": "powershell", "powershell_7": "powershell",
    "cmd": "windows_batch", "batch": "windows_batch", "windows_cmd": "windows_batch",
    "bash": "linux_bash", "linux": "linux_bash", "linux_bash": "linux_bash",
    "windows_server_ad": "windows_server", "openssh": "ssh",
    "wireshark_tshark": "wireshark", "vmware": "vmware_esxi",
    "ftp_ftps_sftp": "ftp",
}

def load_json(path: Path):
    with path.open("r", encoding="utf-8-sig") as handle:
        return json.load(handle)

def records_from(obj, preferred=()):
    if isinstance(obj, list):
        return obj
    if not isinstance(obj, dict):
        return []
    for key in (*preferred, "commands", "examples", "scenarios", "lessons", "items", "questions", "labs", "records"):
        value = obj.get(key)
        if isinstance(value, list):
            return value
    # baseline_curriculum stores lessons under levels[].lessons[].
    levels = obj.get("levels")
    if isinstance(levels, list):
        return [lesson for level in levels if isinstance(level, dict)
                for lesson in level.get("lessons", []) if isinstance(lesson, dict)]
    return []

def strings_in(value):
    if isinstance(value, str):
        yield value
    elif isinstance(value, dict):
        for child in value.values():
            yield from strings_in(child)
    elif isinstance(value, list):
        for child in value:
            yield from strings_in(child)

def ftp_subtype(record):
    # Classify from the actual command/syntax, not descriptive metadata; this
    # prevents unrelated tools in a transfer pack from being credited as FTP.
    text = str(record.get("command") or record.get("syntax") or "").strip().lower()
    if re.search(r"\bsftp\b|sftp://", text):
        return "sftp"
    if "ftps://" in text or "--ssl-reqd" in text or "--ftp-ssl" in text:
        return "ftps"
    if "ftp://" in text or re.search(r"(?:^|\s)ftp(?:\s|$)", text):
        return "ftp"
    return None

def technology_of(record, source_kind=None):
    if not isinstance(record, dict):
        return None
    # Structured metadata takes precedence.
    for key in ("technology_id", "technology", "domain", "vendor_pack", "category", "platform", "vendor", "product"):
        value = record.get(key)
        if not isinstance(value, str) or not value.strip():
            continue
        raw = value.strip().lower()
        slug = raw.replace(" ", "_").replace("/", "_").replace("-", "_")
        if slug in TARGETS:
            return slug
        if slug in ALIASES:
            return ALIASES[slug]
        # Mixed Windows legacy records often carry a human-readable category.
        if "powershell" in raw or "pwsh" in raw:
            return "powershell"
        if "windows-cmd" in raw or "batch" in raw or re.search(r"\bcmd\b", raw):
            return "windows_batch"
        if "windows server" in raw or "active directory" in raw or re.search(r"\bad_ds\b", raw):
            return "windows_server"
        if "linux" in raw or "bash" in raw or "gnu utilities" in raw:
            return "linux_bash"
        if "mikrotik" in raw or "routeros" in raw:
            return "mikrotik"
        if "cisco" in raw or "ios-xe" in raw:
            return "cisco"
        if "fortigate" in raw or "fortios" in raw:
            return "fortigate"
        if "docker" in raw or "compose" in raw:
            return "docker"
        if "vmware" in raw or "esxi" in raw or "vsphere" in raw:
            return "vmware_esxi"
        if "open ssh" in raw or "openssh" in raw or raw == "ssh":
            return "ssh"
        if "telnet" in raw:
            return "telnet"
        if "zabbix" in raw:
            return "zabbix"
        if "wireshark" in raw or "tshark" in raw or "tcpdump" in raw:
            return "wireshark"
        if "juniper" in raw or "junos" in raw:
            return "juniper"
        if "aruba" in raw or "aos-cx" in raw:
            return "aruba"
        if "proxmox" in raw or "pve" == raw:
            return "proxmox"
        if "hyper-v" in raw or "hyperv" in raw:
            return "hyperv"
        if "ansible" in raw:
            return "ansible"
        if "terraform" in raw:
            return "terraform"
        if "kubernetes" in raw or "kubectl" in raw:
            return "kubernetes"
        if "ubiquiti" in raw or "unifi" in raw or "edgeos" in raw:
            return "ubiquiti"
        if "snmp" in raw or "syslog" in raw or "netflow" in raw or "ipfix" in raw:
            return "snmp_syslog"
        if "dns" in raw or "dhcp" in raw or "ntp" in raw or "ipam" in raw:
            return "dns_dhcp_ntp"
        if "nginx" in raw or "apache" in raw or "tls" in raw or "http" in raw or "pki" in raw:
            return "web_tls"
        if "aws" in raw or "azure" in raw or "cloud" in raw:
            return "cloud"
        if "fortimanager" in raw or "fortianalyzer" in raw:
            return "fortinet_management"
        if "sysmon" in raw or "siem" in raw or "soc" in raw or "incident response" in raw:
            return "security_ops"
        if re.search(r"\bgit\b|github", raw):
            return "git"
        if "backup" in raw or "restore" in raw or "disaster recovery" in raw:
            return "backup_recovery"

    # Attribute learning content through canonical lesson UID, explicit labels,
    # or descriptive title/body. This does not inspect generic hints in commands.
    text = " ".join(strings_in(record)).lower()
    uid = str(record.get("lesson_uid") or record.get("uid") or "").lower()
    # Many legacy canonical packs encode the technology in stable UIDs rather
    # than top-level metadata. Treat only explicit UID tokens as attribution.
    uid_aliases = [
        (("mikrotik", "routeros"), "mikrotik"), (("cisco",), "cisco"),
        (("fortigate", "fortios"), "fortigate"), (("windows_batch", "batch"), "windows_batch"),
        (("powershell", "pwsh"), "powershell"), (("windows_server", "active_directory"), "windows_server"),
        (("linux", "linux_bash", "bash"), "linux_bash"), (("docker",), "docker"),
        (("voip", "sip", "pbx"), "voip"), (("vmware_esxi", "vmware", "esxi"), "vmware_esxi"),
        (("ssh", "openssh"), "ssh"), (("telnet",), "telnet"), (("ftps",), "ftps"),
        (("sftp",), "sftp"), (("ftp",), "ftp"), (("zabbix",), "zabbix"),
        (("wireshark", "tshark", "tcpdump"), "wireshark"), (("juniper", "junos"), "juniper"),
        (("aruba",), "aruba"), (("proxmox", "pve"), "proxmox"), (("hyperv", "hyper_v"), "hyperv"),
        (("ansible",), "ansible"), (("terraform",), "terraform"), (("kubernetes", "kubectl"), "kubernetes"),
        (("ubiquiti", "unifi", "edgeos"), "ubiquiti"), (("snmp_syslog", "snmp", "syslog", "netflow", "ipfix"), "snmp_syslog"),
        (("dns_dhcp_ntp", "ipam"), "dns_dhcp_ntp"), (("web_tls", "nginx", "apache", "pki"), "web_tls"),
        (("cloud", "aws", "azure"), "cloud"), (("fortinet_management", "fortimanager", "fortianalyzer"), "fortinet_management"),
        (("security_ops", "sysmon", "siem", "soc"), "security_ops"), (("git", "github"), "git"),
        (("backup_recovery", "backup", "restore"), "backup_recovery"),
    ]
    uid_tokens = set(re.split(r"[:/_-]+", uid))
    for tokens, mapped in uid_aliases:
        if uid_tokens.intersection(tokens):
            return mapped
    if uid.startswith("lesson:ch68:ps:") or "**حوزه:** powershell" in text:
        return "powershell"
    if uid.startswith("lesson:ch68:linux:") or "**حوزه:** linux" in text or "**حوزه:** bash" in text:
        return "linux_bash"
    if uid.startswith("lesson:ch68:windows:") or "**حوزه:** windows batch" in text or "**حوزه:** cmd" in text:
        return "windows_batch"
    if "**حوزه:**" in text:
        marker = text.split("**حوزه:**", 1)[1].splitlines()[0]
        return technology_of({"technology": marker})
    return None

def unique_id(record):
    if not isinstance(record, dict):
        return None
    return record.get("uid") or record.get("id")

def command_kind(record, default_slug=None):
    slug = technology_of(record)
    if slug in ("ftp", "ftps", "sftp"):
        return ftp_subtype(record)
    if slug:
        return slug
    if default_slug == "ftp":
        return ftp_subtype(record)
    return default_slug

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--strict", action="store_true", help="exit 1 if any quota is below target")
    args = parser.parse_args()
    counts = {slug: Counter() for slug in TARGETS}
    seen_command_uids = {slug: set() for slug in TARGETS}
    seen_command_text = {slug: set() for slug in TARGETS}
    missing_files, malformed, source_stats = [], [], {}

    def count_command_file(path, default_slug=None):
        if not path.exists():
            missing_files.append(str(path.relative_to(ROOT)))
            return
        try:
            records = records_from(load_json(path), preferred=("commands",))
            valid = 0
            for rec in records:
                slug = command_kind(rec, default_slug)
                if slug not in TARGETS:
                    continue
                uid = unique_id(rec)
                cmd = str(rec.get("command") or rec.get("syntax") or "").strip().lower() if isinstance(rec, dict) else ""
                # Count only records with a stable identifier and a non-empty command.
                if not uid or not cmd or uid in seen_command_uids[slug] or cmd in seen_command_text[slug]:
                    continue
                seen_command_uids[slug].add(uid)
                seen_command_text[slug].add(cmd)
                counts[slug]["commands"] += 1
                valid += 1
            source_stats[str(path.relative_to(ROOT))] = {"records": len(records), "unique_valid_commands": valid}
        except Exception as exc:
            malformed.append(f"{path.relative_to(ROOT)}: {type(exc).__name__}: {exc}")

    for slug, filename in COMMAND_FILES.items():
        count_command_file(ROOT / filename, slug)

    additional = ROOT / ADDITIONAL_FILE
    if additional.exists():
        try:
            data = load_json(additional)
            records = records_from(data, preferred=("commands",))
            for rec in records:
                slug = command_kind(rec, rec.get("category") if isinstance(rec, dict) else None)
                if slug not in TARGETS:
                    continue
                uid = unique_id(rec)
                cmd = str(rec.get("command") or rec.get("syntax") or "").strip().lower()
                if not uid or not cmd or uid in seen_command_uids[slug] or cmd in seen_command_text[slug]:
                    continue
                seen_command_uids[slug].add(uid)
                seen_command_text[slug].add(cmd)
                counts[slug]["commands"] += 1
            source_stats[str(ADDITIONAL_FILE)] = {"records": len(records)}
        except Exception as exc:
            malformed.append(f"{ADDITIONAL_FILE}: {type(exc).__name__}: {exc}")
    else:
        missing_files.append(str(ADDITIONAL_FILE))

    # Additive wave 3 command pack for the seven core platform families.
    count_command_file(ROOT / "commands" / "sources" / "encyclopedia" / "commands_core_wave3.json")
    # Additive wave 4 command pack spans all 33 tracked technology domains.
    count_command_file(ROOT / "commands" / "sources" / "encyclopedia" / "commands_multi_technology_wave4.json")
    # Additive wave 5 command pack adds three distinct entries per tracked domain.
    count_command_file(ROOT / "commands" / "sources" / "encyclopedia" / "commands_multi_technology_wave5.json")
    # Additive wave 6 command pack adds two additional read-only references per tracked domain.
    count_command_file(ROOT / "commands" / "sources" / "encyclopedia" / "commands_multi_technology_wave6.json")
    # Additive wave 7 command pack adds three operational references per tracked domain.
    count_command_file(ROOT / "commands" / "sources" / "encyclopedia" / "commands_multi_technology_wave7.json")
    # Additive wave 8 command pack adds two additional operational references per tracked domain.
    count_command_file(ROOT / "commands" / "sources" / "encyclopedia" / "commands_multi_technology_wave8.json")
    # Additive wave 9 command pack adds three domain-specific operational references per tracked domain.
    count_command_file(ROOT / "commands" / "sources" / "encyclopedia" / "commands_multi_technology_wave9.json")
    # Additive wave 10 adds five targeted references to twelve underfilled technology domains.
    count_command_file(ROOT / "commands" / "sources" / "encyclopedia" / "commands_multi_technology_wave10.json")
    # Additive wave 11: focused vendor-specific operational references.
    count_command_file(ROOT / "commands" / "sources" / "encyclopedia" / "commands_multi_technology_wave11.json")

    # Legacy mixed Windows pack: classify per record, never credit the full pack
    # to both technologies. Exact command duplication is excluded.
    count_command_file(ROOT / "commands_windows.json")

    content_files = {
        "examples": [ROOT / "examples" / "examples.json"],
        "scenarios": [ROOT / "labs" / "labs.json"],
        "learning_units": [ROOT / "lessons" / "lessons.json", ROOT / "lessons" / "base_curriculum.json"],
        "exam_questions": [ROOT / "questions" / "questions.json"],
    }
    seen_content_uids = {metric: set() for metric in content_files}
    for metric, base_paths in content_files.items():
        paths = []
        for base_path in base_paths:
            paths.append(base_path)
            source_dir = base_path.parent / "sources" / "encyclopedia"
            if source_dir.is_dir():
                paths.extend(sorted(source_dir.glob("*.json")))
        for path in paths:
            if not path.exists():
                if path == base_paths[0] and metric in ("examples", "scenarios", "learning_units"):
                    missing_files.append(str(path.relative_to(ROOT)))
                continue
            try:
                records = records_from(load_json(path))
                attributed = Counter()
                for rec in records:
                    slug = technology_of(rec, metric)
                    if not slug or slug not in TARGETS:
                        continue
                    uid = unique_id(rec)
                    if not uid:
                        continue
                    key = (slug, str(uid))
                    if key in seen_content_uids[metric]:
                        continue
                    seen_content_uids[metric].add(key)
                    counts[slug][metric] += 1 if metric != "exam_questions" else 0
                    attributed[slug] += 1
                    if metric == "exam_questions":
                        counts[slug][metric] += 1
                source_stats[str(path.relative_to(ROOT))] = {
                    "records": len(records),
                    "attributed_" + metric: sum(attributed.values()),
                }
            except Exception as exc:
                malformed.append(f"{path.relative_to(ROOT)}: {type(exc).__name__}: {exc}")

    # Count answer keys across canonical and additive sources, deduplicated by question UID.
    answer_base = ROOT / "answers" / "answer_key.json"
    answer_source_dir = ROOT / "answers" / "sources" / "encyclopedia"
    answer_paths = [answer_base] + (sorted(answer_source_dir.glob("*_wave*.json")) if answer_source_dir.is_dir() else [])
    answer_key_count = 0
    answer_key_uids = set()
    answer_key_by_technology = Counter()
    answer_source_stats = {}
    for answer_path in answer_paths:
        if not answer_path.exists():
            continue
        try:
            answer_data = load_json(answer_path)
            answer_records = records_from(answer_data, preferred=("answers", "items", "answer_key"))
            local_count = 0
            for record in answer_records:
                uid = unique_id(record)
                if not uid or uid in answer_key_uids:
                    continue
                answer_text = record.get("answer_key") if isinstance(record, dict) else None
                if not answer_text and isinstance(record, dict):
                    answer_text = (record.get("fields") or {}).get("answer_key")
                if not answer_text:
                    continue
                answer_key_uids.add(uid)
                answer_key_count += 1
                local_count += 1
                slug = technology_of(record)
                if slug in TARGETS:
                    answer_key_by_technology[slug] += 1
            answer_source_stats[str(answer_path.relative_to(ROOT))] = {
                "records": len(answer_records),
                "unique_answer_keys": local_count,
            }
        except Exception as exc:
            malformed.append(f"{answer_path.relative_to(ROOT)}: {type(exc).__name__}: {exc}")

    report = {
        "chapter": 68,
        "status": "review_required",
        "technology_count": len(TARGETS),
        "quotas_per_technology": QUOTAS,
        "technologies": {},
        "source_files": source_stats,
        "missing_source_files": sorted(set(missing_files)),
        "parse_errors": malformed,
        "answer_key_entries_total": answer_key_count,
        "answer_key_entries_by_technology": dict(answer_key_by_technology),
        "answer_key_sources": answer_source_stats,
        "counting_policy": "Unique non-empty command+UID records count as commands. Examples, scenarios and lessons count only when standalone records can be attributed through metadata, lesson_uid, title, or explicit technology marker. Embedded flashcards, command hints and embedded assessment questions do not count as standalone units.",
    }
    incomplete = []
    for slug, title in TARGETS.items():
        row = {"title": title}
        deficits = {}
        for kind, quota in QUOTAS.items():
            actual = counts[slug][kind]
            row[kind] = actual
            row[kind + "_target"] = quota
            row[kind + "_missing"] = max(0, quota - actual)
            if actual < quota:
                deficits[kind] = quota - actual
        row["exam_questions"] = counts[slug]["exam_questions"]
        row["status"] = "target_met_by_count_only_review_required" if not deficits else "in_progress"
        if deficits:
            incomplete.append(slug)
        report["technologies"][slug] = row
    report["incomplete_technology_count"] = len(incomplete)
    report["incomplete_technologies"] = incomplete
    out = ROOT / "authoring" / "coverage_report.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, ensure_ascii=False, indent=2))
    if malformed or (args.strict and incomplete):
        return 1
    return 0

if __name__ == "__main__":
    sys.exit(main())
