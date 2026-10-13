#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Generate uploadable prompt folders and starter templates for NetworkAll chapters."""
from __future__ import annotations
import json
from pathlib import Path
ROOT = Path(__file__).resolve().parent
CHAPTERS = [
    [
        1,
        "مبانی IT و معماری کامپیوتر",
        "Architecture CPU RAM Bus"
    ],
    [
        2,
        "اسمبل، عیب‌یابی و سرورهای سازمانی",
        "Hardware assembly server"
    ],
    [
        3,
        "BIOS UEFI و بوت",
        "UEFI Secure Boot"
    ],
    [
        4,
        "سیستم‌عامل پایه",
        "OS process memory"
    ],
    [
        5,
        "فایل‌سیستم و Storage پایه",
        "FS RAID"
    ],
    [
        6,
        "مبانی شبکه",
        "OSI TCP/IP model"
    ],
    [
        7,
        "اترنت و سوییچینگ پایه",
        "VLAN STP"
    ],
    [
        8,
        "IPv4 IPv6 ساب‌نتینگ",
        "Subnetting routing intro"
    ],
    [
        9,
        "ARP ICMP TCP UDP",
        "L3 L4 protocols"
    ],
    [
        10,
        "DNS",
        "DNS records recursion"
    ],
    [
        11,
        "DHCP و IPAM",
        "DHCP failover IPAM"
    ],
    [
        12,
        "کابل‌کشی فیبر رک",
        "Structured cabling fiber"
    ],
    [
        13,
        "سوییچینگ سیسکو",
        "Cisco switching VTP EtherChannel"
    ],
    [
        14,
        "مسیریابی پیشرفته",
        "OSPF BGP Redistribution"
    ],
    [
        15,
        "MPLS VRF L3VPN",
        "MPLS L3VPN"
    ],
    [
        16,
        "Multicast",
        "PIM IGMP"
    ],
    [
        17,
        "EVPN VXLAN",
        "Leaf-Spine EVPN"
    ],
    [
        18,
        "SDN SD-WAN SASE",
        "SD-WAN overlay"
    ],
    [
        19,
        "MikroTik مبانی",
        "RouterOS basics"
    ],
    [
        20,
        "MikroTik Routing Firewall NAT",
        "MikroTik FW NAT"
    ],
    [
        21,
        "MikroTik QoS VPN HA",
        "MikroTik VPN HA"
    ],
    [
        22,
        "وایرلس سازمانی",
        "Enterprise WiFi"
    ],
    [
        23,
        "PtP PtMP",
        "Wireless backhaul"
    ],
    [
        24,
        "FortiGate",
        "FortiGate policy VPN"
    ],
    [
        25,
        "pfSense OPNsense Sophos",
        "Open-source firewalls"
    ],
    [
        26,
        "PKI TLS",
        "Certificates TLS"
    ],
    [
        27,
        "AAA NAC",
        "802.1X RADIUS"
    ],
    [
        28,
        "Windows Server Core",
        "Windows Server roles"
    ],
    [
        29,
        "Active Directory",
        "AD DS GPO"
    ],
    [
        30,
        "Windows DNS DHCP NPS",
        "MS network services"
    ],
    [
        31,
        "فایل چاپ DFS",
        "File server DFS"
    ],
    [
        32,
        "امنیت Endpoint ویندوز",
        "Windows hardening"
    ],
    [
        33,
        "Entra ID Hybrid",
        "Azure AD hybrid"
    ],
    [
        34,
        "M365 Intune ایمیل",
        "M365 Intune"
    ],
    [
        35,
        "PowerShell CMD",
        "PowerShell automation"
    ],
    [
        36,
        "مدیریت لینوکس",
        "Linux admin"
    ],
    [
        37,
        "شبکه لینوکس",
        "Linux networking"
    ],
    [
        38,
        "سرویس لینوکس وب",
        "Nginx Apache"
    ],
    [
        39,
        "امنیت لینوکس",
        "Linux security"
    ],
    [
        40,
        "VMware Hyper-V",
        "Virtualization"
    ],
    [
        41,
        "Proxmox Docker",
        "Proxmox containers"
    ],
    [
        42,
        "Kubernetes",
        "K8s networking"
    ],
    [
        43,
        "شبکه ابری",
        "VPC cloud networking"
    ],
    [
        44,
        "امنیت ابر Governance",
        "Cloud security"
    ],
    [
        45,
        "Storage سازمانی",
        "SAN NAS"
    ],
    [
        46,
        "Backup DR",
        "Backup DR"
    ],
    [
        47,
        "Data Center",
        "DC design"
    ],
    [
        48,
        "HA و Load Balancing",
        "HA LB"
    ],
    [
        49,
        "مانیتورینگ",
        "SNMP Prometheus"
    ],
    [
        50,
        "SIEM ELK",
        "SIEM SOC tools"
    ],
    [
        51,
        "اتوماسیون و AI در IT",
        "Ansible Python AIOps"
    ],
    [
        52,
        "مدیریت دیتابیس",
        "DBA basics"
    ],
    [
        53,
        "امنیت دیتابیس",
        "DB security"
    ],
    [
        54,
        "VoIP سانترال",
        "VoIP QoS"
    ],
    [
        55,
        "CCTV Access BMS IoT",
        "Physical security IoT"
    ],
    [
        56,
        "امنیت پایه Zero Trust ITIL",
        "Zero Trust ITIL"
    ],
    [
        57,
        "امنیت شبکه",
        "Network security"
    ],
    [
        58,
        "Endpoint AppSec DevSecOps",
        "AppSec"
    ],
    [
        59,
        "SOC IR Hunting",
        "SOC IR"
    ],
    [
        60,
        "عیب‌یابی هک اخلاقی لاب سازمانی",
        "Authorized labs only"
    ],
    [
        61,
        "معماری سازمانی Enterprise Architecture",
        "EA"
    ],
    [
        62,
        "عملیات IT و NOC",
        "NOC ops"
    ],
    [
        63,
        "مستندسازی Runbook و CMDB",
        "Runbook CMDB"
    ],
    [
        64,
        "Git و کنترل نسخه",
        "Git"
    ],
    [
        65,
        "امنیت سایبری و هک اخلاقی دفاعی + وایرلس",
        "Defensive security wireless"
    ],
    [
        66,
        "مسیریابی عمیق OSPF/BGP/Redistribution",
        "Deep routing"
    ],
    [
        67,
        "VPN سازمانی IPsec/SSL",
        "Enterprise VPN"
    ],
    [
        68,
        "دانشنامه جامع دستورات",
        "Cisco MikroTik FortiGate Issabel PowerShell"
    ]
]
COMMON = """حداقل 50 مثال مستقل، 50 سناریوی مستقل، 50 سؤال آزمون، answer_key جدا با ID مشترک، نمودار برای تمام مباحث اصلی، لاب امن، منابع رسمی دقیق، پوشش L0-L4 و rollback. محتوای موجود را حذف یا overwrite نکن؛ داده یا منبع ساختگی نساز."""

def body(n: int, title: str, kw: str) -> str:
    cid = f"{n:02d}"
    return f"""# Standalone uploadable prompt — Chapter {cid}: {title}

Repository: https://github.com/MrUtility01/NetworkAll
Chapter: {n}; curriculum title: {title}; starter keywords: {kw}

Audit current lesson titles, relevance, depth, L0-L4 coverage and duplicates. Report gaps, then create unique additive content only. Do not remove current lessons or UIDs.

Requirements: {COMMON}
Each lesson must include uid, chapter_order={n}, subchapter_order, lesson_order, level, title_fa, title_en, topic, summary, full_content, commands, examples, notes, learning_objectives, meta and source_status. Teach from fundamentals through advanced practice with architecture, worked examples, labs, output interpretation, RCA, security, rollback, checklist and glossary.

Minimum per chapter: 50 distinct examples; 50 complete independent scenarios; 50 test questions with separate answer key and matching IDs; a meaningful diagram for every major concept with Mermaid source, SVG, manifest and alt text; labs for major topics; at least 10 accurate official sources. Each scenario includes environment, goal/symptom, constraints, evidence, diagnosis, remedy, verification and rollback.
If chapter 68, separate Linux, Bash, PowerShell, Windows CMD, Windows Batch, Cisco IOS/IOS-XE, MikroTik RouterOS, FortiGate/FortiOS and Issabel/Asterisk; never mix syntax.

Deliver ch{cid}_pack.json, ch{cid}_answer_key.json, ch{cid}_scenarios.json, diagrams/ch{cid}/manifest.json + SVG/source and VALIDATION.md with real counts and UID/key checks. Store main pack under tools/packs/ch{cid}/. New content uses source_status=review_required. Until tested loader support exists, do not claim separate scenario/diagram assets are visible in the app.
"""

def template(n: int, title: str) -> dict:
    if n == 68:
        return {"package_schema_version":1,"project":"ENGINEER JOKAR / NetworkAll",
                "generated_on":"YYYY-MM-DD","purpose":"Chapter 68 commands grouped by vendor/platform",
                "chapter_order":68,"chapter_title_fa":title,"commands":[],
                "compatibility":{"preserve_existing_records":True,"preserve_existing_uids":True}}
    return {"package_schema_version":1,"project":"ENGINEER JOKAR / NetworkAll",
            "generated_on":"YYYY-MM-DD","purpose":f"Chapter {n}: {title}",
            "scope":[{"chapter_order":n,"subchapter_order":1,"title":title,"topics":[]}],
            "compatibility":{"preserve_existing_records":True,"preserve_existing_uids":True,
                             "questions_and_answers_separate":True},"lessons":[]}

def main():
    rows = ["# NetworkAll chapter prompts", "", "| Chapter | Title | Prompt |"]
    for n,title,kw in CHAPTERS:
        cid=f"{n:02d}"
        folder=ROOT/f"ch{cid}"
        folder.mkdir(parents=True,exist_ok=True)
        (folder/"PROMPT.md").write_text(body(n,title,kw),encoding="utf-8")
        (folder/"README.md").write_text(
            f"# Chapter {cid} — {title}\n\nUpload PROMPT.md to your AI tool.\n"
            f"Save the finished pack under tools/packs/ch{cid}/.\n",encoding="utf-8")
        (folder/"PACK_TEMPLATE.json").write_text(
            json.dumps(template(n,title),ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
        rows.append(f"| {n} | {title} | [ch{cid}/PROMPT.md](ch{cid}/PROMPT.md) |")
    (ROOT/"INDEX.md").write_text("\n".join(rows)+"\n",encoding="utf-8")
    print(f"Generated {len(CHAPTERS)} chapter prompt folders")

if __name__ == "__main__":
    main()
