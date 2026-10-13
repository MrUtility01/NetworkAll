#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Generate 100 compact, topic-labelled SVG learning diagrams for the Android offline app."""
from __future__ import annotations
import json
from html import escape
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "android/app/src/main/assets/diagrams"
WEB_OUT = ROOT / "server/static/diagrams"
TOPICS = [
("Ethernet و Switching", ["Frame ورودی", "بررسی MAC", "جدول CAM", "Forward / Flood"]),
("VLAN و Trunk", ["Access Port", "802.1Q Tag", "Allowed VLANs", "VLAN مقصد"]),
("STP و Redundancy", ["BPDU", "انتخاب Root", "محاسبه Cost", "Forward / Block"]),
("IPv4 و Subnetting", ["IPv4 Address", "Subnet Mask", "Network ID", "Host / Broadcast"]),
("IPv6", ["Global / Link-local", "Prefix", "Neighbor Discovery", "Route Selection"]),
("ARP و Neighbor", ["بررسی Cache", "ARP Request", "ARP Reply", "ارسال Frame"]),
("DHCP", ["Discover", "Offer", "Request", "ACK / Lease"]),
("DNS", ["Stub Resolver", "Recursive Query", "Authoritative NS", "Answer / Cache"]),
("Routing و Forwarding", ["Ingress Interface", "Longest Prefix", "Next Hop", "Egress Interface"]),
("OSPF", ["Hello", "Neighbor State", "LSDB Sync", "SPF / Route"]),
("BGP", ["TCP/179", "OPEN / KEEPALIVE", "UPDATE", "Policy / Best Path"]),
("NAT و PAT", ["Inside Local", "ACL / Rule Match", "Translation Table", "Outside Global"]),
("Firewall", ["Ingress Policy", "State Table", "Rule Evaluation", "Allow / Deny"]),
("VPN و IPsec", ["IKE SA", "Authentication", "Child SA", "Encrypted Tunnel"]),
("Wi-Fi", ["Client Scan", "Authentication", "Association", "Data / Roaming"]),
("PoE و VoIP", ["PoE Budget", "VLAN Voice", "SIP Signaling", "RTP Media"]),
("Linux Networking", ["ip addr", "ip route", "ss / nft", "journalctl"]),
("Bash Automation", ["Validate Input", "set -Eeuo pipefail", "Trap / Cleanup", "Exit Code"]),
("PowerShell", ["Get-NetIPConfiguration", "Resolve-DnsName", "Test-NetConnection", "Event / Report"]),
("Windows CMD/Batch", ["Validate Args", "ipconfig / netstat", "errorlevel", "Log / Exit"]),
]
OUT.mkdir(parents=True, exist_ok=True)
WEB_OUT.mkdir(parents=True, exist_ok=True)
items=[]
for gi,(group,stages) in enumerate(TOPICS):
    for variant in range(5):
        num=gi*5+variant+1
        title=f"{group} — {['مسیر پردازش','مراحل عیب‌یابی','نقاط تصمیم','جریان کنترل','راستی‌آزمایی'][variant]}"
        nodes=[]
        for j,base in enumerate(stages):
            label=base
            if variant==1:
                label=["جمع‌آوری شواهد", "ساخت فرضیه", "آزمون کم‌خطر", "تأیید / Rollback"][j]
            elif variant==2:
                label=["ورودی و پیش‌شرط", "تصمیم / Policy", "حالت یا جدول", "نتیجه و استثنا"][j]
            elif variant==3:
                label=["Trigger", "Processing", "State Change", "Output / Log"][j]
            elif variant==4:
                label=["Baseline", "Command / Probe", "Expected Result", "Evidence / Pass"][j]
            nodes.append(label)
        svg=['<svg xmlns="http://www.w3.org/2000/svg" width="1200" height="420" viewBox="0 0 1200 420">']
        svg += ['<rect width="1200" height="420" rx="24" fill="#f8fafc"/>',
                '<text x="600" y="48" text-anchor="middle" font-family="sans-serif" font-size="25" font-weight="700" fill="#0f172a">'+escape(f"{num:03d} · {title}")+'</text>',
                '<text x="600" y="78" text-anchor="middle" font-family="sans-serif" font-size="15" fill="#475569">'+escape(group)+' · NetworkAll Learning Diagram</text>']
        xs=[70,355,640,925]
        for j,label in enumerate(nodes):
            svg.append(f'<rect x="{xs[j]}" y="145" width="205" height="100" rx="14" fill="{["#dbeafe","#dcfce7","#fef3c7","#ede9fe"][j]}" stroke="#64748b" stroke-width="2"/>')
            svg.append(f'<text x="{xs[j]+102}" y="188" text-anchor="middle" font-family="sans-serif" font-size="17" font-weight="600" fill="#0f172a">'+escape(label)+'</text>')
            svg.append(f'<text x="{xs[j]+102}" y="215" text-anchor="middle" font-family="sans-serif" font-size="13" fill="#334155">مرحله {j+1}</text>')
            if j<3:
                svg.append(f'<path d="M {xs[j]+205} 195 H {xs[j+1]-12} l -10 -7 m 10 7 l -10 7" fill="none" stroke="#334155" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"/>')
        svg += ['<rect x="70" y="292" width="1060" height="70" rx="12" fill="#e2e8f0"/>',
                '<text x="600" y="320" text-anchor="middle" font-family="sans-serif" font-size="16" font-weight="600" fill="#0f172a">معیار صحت</text>',
                '<text x="600" y="345" text-anchor="middle" font-family="sans-serif" font-size="14" fill="#334155">ورودی، تصمیم، خروجی و شواهد را ثبت کنید؛ نتیجه را با وضعیت مورد انتظار مقایسه کنید.</text>',
                '</svg>']
        filename=f"diagram_{num:03d}.svg"
        (OUT/filename).write_text("\n".join(svg),encoding="utf-8")
        (WEB_OUT/filename).write_text("\n".join(svg),encoding="utf-8")
        items.append({"id":num,"title_fa":title,"collection":group,"asset":filename,"stages":nodes})
index_text = json.dumps({"version": 1, "count": len(items), "diagrams": items}, ensure_ascii=False, indent=2)
(OUT / "index.json").write_text(index_text, encoding="utf-8")
(WEB_OUT / "index.json").write_text(index_text, encoding="utf-8")
assert len(items) == 100
assert all((OUT / x["asset"]).is_file() for x in items)
assert all((WEB_OUT / x["asset"]).is_file() for x in items)
print(
    f"Generated {len(items)} NetworkAll diagrams for Android + Windows web; "
    f"Android SVG bytes={sum(p.stat().st_size for p in OUT.glob('*.svg'))}; "
    f"web SVG bytes={sum(p.stat().st_size for p in WEB_OUT.glob('*.svg'))}"
)
