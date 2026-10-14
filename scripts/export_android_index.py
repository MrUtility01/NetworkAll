#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from __future__ import annotations
import gzip, json, sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "server"))

from core.full_curriculum import get_full_curriculum
from core.rich_content import build_rich_lesson
from core.extra_chapters import ensure_chapters_1_to_68

CHAPTER_TITLES = {
    1: "فصل ۰۱: مبانی IT، اجزای رایانه و معماری سخت‌افزار",
    2: "فصل ۰۲: اسمبل رایانه، عیب‌یابی سخت‌افزار و سرور",
    3: "فصل ۰۳: BIOS، UEFI، بوت و بازیابی راه‌اندازی",
    4: "فصل ۰۴: مفاهیم پایه سیستم‌عامل و مدیریت دستگاه",
    5: "فصل ۰۵: فایل‌سیستم، دیسک و ذخیره‌سازی اطلاعات",
    6: "فصل ۰۶: مبانی شبکه؛ توپولوژی، Ethernet و مدل‌های ارتباطی",
    7: "فصل ۰۷: Ethernet، Switching، VLAN و شبکه محلی",
    8: "فصل ۰۸: IPv4، IPv6، Subnetting و طراحی آدرس‌دهی",
    9: "فصل ۰۹: تحلیل بسته و پروتکل‌های ARP، ICMP، TCP و UDP",
    10: "فصل ۱۰: DNS؛ تبدیل نام دامنه به آدرس IP",
    11: "فصل ۱۱: DHCP، تخصیص آدرس و مدیریت IP (IPAM)",
    12: "فصل ۱۲: کابل‌کشی مسی، فیبر نوری، رک و تست فیزیکی",
    13: "فصل ۱۳: پیکربندی و عیب‌یابی سوئیچ‌های Cisco",
    14: "فصل ۱۴: مسیریابی IP؛ Static Route و پروتکل‌های مسیریابی",
    15: "فصل ۱۵: MPLS، VRF و VPN لایه ۳",
    16: "فصل ۱۶: Multicast؛ عضویت گروه و مسیریابی چندپخشی",
    17: "فصل ۱۷: EVPN و VXLAN در شبکه مراکز داده",
    18: "فصل ۱۸: SDN، SD-WAN و معماری شبکه مبتنی بر سیاست",
    19: "فصل ۱۹: MikroTik RouterOS؛ پیکربندی و مدیریت پایه",
    20: "فصل ۲۰: MikroTik؛ Routing، Firewall و NAT",
    21: "فصل ۲۱: MikroTik؛ QoS، VPN و افزونگی (HA)",
    22: "فصل ۲۲: شبکه بی‌سیم سازمانی؛ Wi‑Fi، RF و کنترلر",
    23: "فصل ۲۳: لینک‌های بی‌سیم نقطه‌به‌نقطه (PtP) و چندنقطه‌ای (PtMP)",
    24: "فصل ۲۴: FortiGate؛ رابط‌ها، Policy، NAT و عیب‌یابی",
    25: "فصل ۲۵: فایروال‌های pfSense، OPNsense و Sophos",
    26: "فصل ۲۶: PKI، گواهی دیجیتال و امنیت TLS",
    27: "فصل ۲۷: احراز هویت، مجوزدهی، AAA و کنترل دسترسی شبکه (NAC)",
    28: "فصل ۲۸: Windows Server؛ نصب، نقش‌ها و سرویس‌های پایه",
    29: "فصل ۲۹: Active Directory؛ Domain، کاربر، گروه و Group Policy",
    30: "فصل ۳۰: سرویس‌های Windows؛ DNS، DHCP و NPS",
    31: "فصل ۳۱: Windows File Server، مجوزها، چاپ و DFS",
    32: "فصل ۳۲: امنیت Endpoint در Windows و کنترل دستگاه",
    33: "فصل ۳۳: Microsoft Entra ID و هویت ترکیبی",
    34: "فصل ۳۴: Microsoft 365، Intune و سرویس‌های سازمانی",
    35: "فصل ۳۵: مدیریت Windows با PowerShell، CMD و Batch",
    36: "فصل ۳۶: مدیریت Linux؛ کاربران، سرویس‌ها و فایل‌ها",
    37: "فصل ۳۷: شبکه در Linux؛ IP، Route، DNS و Firewall",
    38: "فصل ۳۸: سرویس‌های Linux؛ وب‌سرور، SSH و Reverse Proxy",
    39: "فصل ۳۹: امنیت Linux، سخت‌سازی و ثبت رویداد",
    40: "فصل ۴۰: مجازی‌سازی با VMware و Hyper‑V",
    41: "فصل ۴۱: Proxmox، ماشین مجازی و کانتینرهای Docker",
    42: "فصل ۴۲: Kubernetes؛ شبکه، سرویس و عیب‌یابی کلاستر",
    43: "فصل ۴۳: شبکه ابری؛ VPC/VNet، Route و اتصال Hybrid",
    44: "فصل ۴۴: امنیت ابر، سیاست‌گذاری و Governance",
    45: "فصل ۴۵: ذخیره‌سازی سازمانی، SAN/NAS و افزونگی",
    46: "فصل ۴۶: Backup، بازیابی فاجعه (DR) و آزمون Restore",
    47: "فصل ۴۷: معماری و عملیات مرکز داده (Data Center)",
    48: "فصل ۴۸: High Availability، Failover و Load Balancing",
    49: "فصل ۴۹: مانیتورینگ، متریک، لاگ و Observability",
    50: "فصل ۵۰: SIEM، تحلیل لاگ و همبستگی رخدادها",
    51: "فصل ۵۱: اتوماسیون IT و شبکه با Python، Ansible و AI",
    52: "فصل ۵۲: مدیریت پایگاه داده، SQL و عملیات پشتیبان‌گیری",
    53: "فصل ۵۳: امنیت پایگاه داده، دسترسی و Audit",
    54: "فصل ۵۴: VoIP، SIP/RTP و عیب‌یابی سانترال",
    55: "فصل ۵۵: دوربین مداربسته، کنترل تردد، BMS و IoT",
    56: "فصل ۵۶: مبانی امنیت، Zero Trust و فرایندهای ITIL",
    57: "فصل ۵۷: امنیت شبکه؛ Firewall، IDS/IPS و کنترل دسترسی",
    58: "فصل ۵۸: امنیت Endpoint، امنیت برنامه و DevSecOps",
    59: "فصل ۵۹: مرکز عملیات امنیت (SOC)، پاسخ به رخداد و Threat Hunting",
    60: "فصل ۶۰: آزمایشگاه مجاز تست نفوذ و عیب‌یابی امنیتی دفاعی",
    61: "فصل ۶۱: معماری سازمانی؛ استانداردها، وابستگی‌ها و طراحی کلان",
    62: "فصل ۶۲: عملیات پشتیبانی IT، مانیتورینگ و مرکز عملیات شبکه (NOC)",
    63: "فصل ۶۳: مستندسازی فنی، Runbook و مدیریت پیکربندی (CMDB)",
    64: "فصل ۶۴: کنترل نسخه و همکاری تیمی با Git و GitHub",
    65: "فصل ۶۵: امنیت سایبری دفاعی، تست نفوذ مجاز و امنیت شبکه بی‌سیم",
    66: "فصل ۶۶: مسیریابی پیشرفته؛ OSPF، BGP و بازتوزیع مسیرها",
    67: "فصل ۶۷: VPN سازمانی؛ IPsec، SSL VPN و عیب‌یابی تونل",
    68: "فصل ۶۸: دانشنامه کاربردی فرمان‌های شبکه و سیستم‌عامل؛ Cisco، MikroTik، FortiGate، Linux و Windows",
}



def main() -> None:
    curriculum = ensure_chapters_1_to_68(list(get_full_curriculum()))
    chapters = []
    lesson_count = 0
    for ch in curriculum:
        order, tfa, ten, subs = ch[0], ch[1], ch[2], ch[3]
        tfa = CHAPTER_TITLES.get(int(order), tfa)
        sub_out = []
        for si, sub in enumerate(subs):
            sname, lessons = sub[0], sub[1]
            les_out = []
            for li, les in enumerate(lessons):
                if isinstance(les, (list, tuple)) and len(les) >= 2:
                    lfa, len_ = les[0], les[1]
                else:
                    lfa, len_ = str(les), str(les)
                tag = lfa[1:3] if str(lfa).startswith("[L") else "L0"
                rich = build_rich_lesson(lfa, len_, level=tag)
                lesson_count += 1
                uid = f"lesson:ch{int(order):02d}:s{si:03d}:l{li:04d}"
                les_out.append({
                    "uid": uid, "title_fa": lfa, "title_en": len_, "level": tag,
                    "summary": rich.get("summary") or "",
                    "full_content": rich.get("full_content") or "",
                    "commands": rich.get("commands") or "",
                    "examples": rich.get("examples") or "",
                    "notes": rich.get("notes") or "",
                    "meta": rich.get("meta") or {},
                    "learning_objectives": rich.get("learning_objectives") or [],
                    "search_keywords": rich.get("search_keywords") or [],
                    "search_query": rich.get("search_query") or "",
                    "source_status": rich.get("source_status") or "review_required",
                    "subchapter_order": si + 1,
                    "lesson_order": li + 1,
                })
            sub_out.append({"title_fa": sname, "lessons": les_out})
        chapters.append({"order": int(order), "title_fa": tfa, "title_en": ten, "subchapters": sub_out})
    chapters.sort(key=lambda c: c["order"])
    payload = {
        "version": 11,
        "generated_at": datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z"),
        "project": "NetworkAll",
        "release_version": "1.0.0",
        "chapters": chapters,
        "lesson_count": lesson_count,
    }
    raw = json.dumps(payload, ensure_ascii=False, separators=(",", ":")).encode("utf-8")
    out_dir = ROOT / "android" / "app" / "src" / "main" / "assets"
    out_dir.mkdir(parents=True, exist_ok=True)
    out = out_dir / "curriculum_index.json.gz"
    out.write_bytes(gzip.compress(raw, 9))
    print(f"wrote {out} chapters={len(chapters)} lessons={lesson_count} gz={out.stat().st_size}")
    print("orders", [c["order"] for c in chapters[-6:]])


if __name__ == "__main__":
    main()
