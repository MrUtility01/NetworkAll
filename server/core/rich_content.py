# -*- coding: utf-8 -*-
"""محتوای عمیق: teacher اختصاصی + deep_fallback."""
from __future__ import annotations
import re
from typing import Any, Dict
from core.rich_data import BANKS, COMMON
from core.chapter_loader import load_chapter_authoring

def level_tag(title: str) -> str:
    m = re.match(r"\[(L[0-4])\]", title or "")
    return m.group(1) if m else "L0"

def clean_topic(title: str) -> str:
    t = re.sub(r"^\[L[0-4]\]\s*", "", title or "").strip()
    t = re.sub(r"\s*[—\-]\s*(آشنایی|مقدماتی|ادمین|مهندس|خبره).*$", "", t, flags=re.I)
    return t.strip() or (title or "موضوع")

def _fmt_cmds(pairs):
    return "\n".join(f"```\n{cmd}\n```\n→ {desc}\n" for cmd, desc in pairs)

def build_rich_lesson(title_fa: str, title_en: str = "", level: str | None = None) -> Dict[str, Any]:
    try:
        git_hook = load_chapter_authoring(64, "chapter64_git_hook")
        is_git_title = git_hook.is_git_title
        build_git_lesson = git_hook.build_git_lesson
        if is_git_title(title_fa or ""):
            c = build_git_lesson(title_fa, title_en)
            if c:
                return c
    except Exception:
        pass
    try:
        teacher17 = load_chapter_authoring(17, "chapter17_teacher")
        build_chapter17_lesson = teacher17.build_chapter17_lesson
        if any(k in (title_fa or "") for k in ("VXLAN", "VNI", "VTEP", "Overlay", "EVPN", "Control Plane", "Route Type", "Leaf", "Spine", "Underlay", "Anycast", "RT-2", "RT-3", "RT-5")):
            c = build_chapter17_lesson(title_fa, title_en)
            if c: return _ensure_dense(title_fa, title_en, level, c)
    except Exception:
        pass
    try:
        teacher16 = load_chapter_authoring(16, "chapter16_teacher")
        build_chapter16_lesson = teacher16.build_chapter16_lesson
        if any(k in (title_fa or "") for k in ("Multicast", "PIM", "IGMP", "Dense", "Sparse", "IPTV", "چرا Multicast", "Rendezvous", "MLD", "SSM")):
            c = build_chapter16_lesson(title_fa, title_en)
            if c: return _ensure_dense(title_fa, title_en, level, c)
    except Exception:
        pass
    try:
        teacher15 = load_chapter_authoring(15, "chapter15_teacher")
        build_chapter15_lesson = teacher15.build_chapter15_lesson
        if any(k in (title_fa or "") for k in ("VRF", "MPLS", "Label", "L3VPN", "PE P CE", "LDP", "LSP", "Route Target", "Route Distinguisher", "VPNv4", "Label Switching", "PHP")):
            c = build_chapter15_lesson(title_fa, title_en)
            if c: return _ensure_dense(title_fa, title_en, level, c)
    except Exception:
        pass
    try:
        teacher14 = load_chapter_authoring(14, "chapter14_teacher")
        build_chapter14_lesson = teacher14.build_chapter14_lesson
        if any(k in (title_fa or "") for k in ("Static Route", "OSPF", "Link-State", "EIGRP", "Metric مرکب", "BGP", "AS Number", "Prefix-list", "route-map", "Redistribut", "Floating", "LSA", "eBGP", "iBGP", "Administrative Distance", "next-hop")):
            c = build_chapter14_lesson(title_fa, title_en)
            if c: return _ensure_dense(title_fa, title_en, level, c)
    except Exception:
        pass
    try:
        teacher13 = load_chapter_authoring(13, "chapter13_teacher")
        build_chapter13_lesson = teacher13.build_chapter13_lesson
        if any(k in (title_fa or "") for k in ("VLAN", "مفهوم VLAN", "Trunk", "STP", "RSTP", "Loop", "Root Bridge", "EtherChannel", "LACP", "Port Security", "DHCP Snooping", "BPDU", "802.1X", "PortFast", "Native VLAN", "SVI", "Storm Control", "DAI")):
            c = build_chapter13_lesson(title_fa, title_en)
            if c: return _ensure_dense(title_fa, title_en, level, c)
    except Exception:
        pass
    try:
        teacher12 = load_chapter_authoring(12, "chapter12_teacher")
        build_chapter12_lesson = teacher12.build_chapter12_lesson
        if any(k in (title_fa or "") for k in ("Cat5", "Cat6", "Cat6A", "OM3", "OM4", "فیبر", "Fiber", "رک", "Rack", "Wiremap", "PDU", "PoE", "T568", "RJ45", "OTDR")):
            c = build_chapter12_lesson(title_fa, title_en)
            if c: return _ensure_dense(title_fa, title_en, level, c)
    except Exception:
        pass
    try:
        teacher11 = load_chapter_authoring(11, "chapter11_teacher")
        build_chapter11_lesson = teacher11.build_chapter11_lesson
        if any(k in (title_fa or "") for k in ("DHCP", "DORA", "Discover", "Offer", "Relay", "helper", "IPAM", "Lease", "Scope", "Reservation", "APIPA", "Renew")):
            c = build_chapter11_lesson(title_fa, title_en)
            if c: return _ensure_dense(title_fa, title_en, level, c)
    except Exception:
        pass
    try:
        teacher10 = load_chapter_authoring(10, "chapter10_teacher")
        build_chapter10_lesson = teacher10.build_chapter10_lesson
        if any(k in (title_fa or "") for k in ("DNS", "Resolver", "AAAA", "CNAME", "MX", "TXT", "SOA", "PTR", "SRV", "Forwarder", "DNSSEC", "رکورد", "TTL", "nslookup")):
            c = build_chapter10_lesson(title_fa, title_en)
            if c: return _ensure_dense(title_fa, title_en, level, c)
    except Exception:
        pass
    try:
        teacher09 = load_chapter_authoring(9, "chapter09_teacher")
        build_chapter09_lesson = teacher09.build_chapter09_lesson
        if any(k in (title_fa or "") for k in ("ARP", "ICMP", "Echo", "Three-way", "Handshake", "TCP", "UDP", "Sequence", "Window", "SYN", "FIN", "RST", "traceroute", "ویژگی‌ها")):
            c = build_chapter09_lesson(title_fa, title_en)
            if c: return _ensure_dense(title_fa, title_en, level, c)
    except Exception:
        pass
    try:
        teacher08 = load_chapter_authoring(8, "chapter08_teacher")
        build_chapter08_lesson = teacher08.build_chapter08_lesson
        if any(k in (title_fa or "") for k in ("IPv4", "IPv6", "Subnet", "ساب‌نت", "ماسک", "CIDR", "VLSM", "SLAAC", "fe80", "NDP", "RFC1918", "DMZ")):
            c = build_chapter08_lesson(title_fa, title_en)
            if c: return _ensure_dense(title_fa, title_en, level, c)
    except Exception:
        pass
    try:
        teacher07 = load_chapter_authoring(7, "chapter07_teacher")
        build_chapter07_lesson = teacher07.build_chapter07_lesson
        if any(k in (title_fa or "") for k in ("فریم", "Frame", "اترنت", "Ethernet", "MAC Table", "Learning", "Store-and-Forward", "سوییچ", "Switch", "Duplex", "FCS", "CRC", "CAM", "MTU", "SFP")):
            c = build_chapter07_lesson(title_fa, title_en)
            if c: return _ensure_dense(title_fa, title_en, level, c)
    except Exception:
        pass
    try:
        teacher06 = load_chapter_authoring(6, "chapter06_teacher")
        build_chapter06_lesson = teacher06.build_chapter06_lesson
        if any(k in (title_fa or "") for k in ("LAN", "WAN", "WLAN", "OSI", "TCP/IP", "Packet", "Encapsulation", "توپولوژی", "Broadcast", "Unicast", "Gateway", "مبانی شبکه")):
            if not any(k in (title_fa or "") for k in ("IPv4", "IPv6", "Subnet", "ARP", "ICMP", "DNS", "DHCP", "VLAN", "STP", "OSPF", "BGP", "MPLS", "Multicast", "VXLAN", "EVPN")):
                c = build_chapter06_lesson(title_fa, title_en)
                if c: return _ensure_dense(title_fa, title_en, level, c)
    except Exception:
        pass
    try:
        teacher03 = load_chapter_authoring(3, "chapter03_teacher")
        build_chapter03_lesson = teacher03.build_chapter03_lesson
        if any(k in (title_fa or "") for k in ("BIOS", "UEFI", "بوت", "Boot", "Secure Boot", "TPM", "CMOS", "GRUB", "PXE")):
            c = build_chapter03_lesson(title_fa, title_en)
            if c: return _ensure_dense(title_fa, title_en, level, c)
    except Exception:
        pass
    try:
        teacher05 = load_chapter_authoring(5, "chapter05_teacher")
        build_chapter05_lesson = teacher05.build_chapter05_lesson
        if any(k in (title_fa or "") for k in ("FAT", "NTFS", "ext4", "XFS", "MBR", "GPT", "پارتیشن", "RAID", "fsck", "mount", "mdadm")):
            c = build_chapter05_lesson(title_fa, title_en)
            if c: return _ensure_dense(title_fa, title_en, level, c)
    except Exception:
        pass
    try:
        teacher04 = load_chapter_authoring(4, "chapter04_teacher")
        build_chapter04_lesson = teacher04.build_chapter04_lesson
        if any(k in (title_fa or "") for k in ("Kernel", "هسته", "Registry", "ویندوز", "Windows", "لینوکس", "Linux", "systemd", "Process", "PowerShell", "Task Manager")):
            c = build_chapter04_lesson(title_fa, title_en)
            if c: return _ensure_dense(title_fa, title_en, level, c)
    except Exception:
        pass
    try:
        teacher02 = load_chapter_authoring(2, "chapter02_teacher")
        build_chapter02_lesson = teacher02.build_chapter02_lesson
        if any(k in (title_fa or "") for k in ("ESD", "ایمنی", "اسمبل", "Beep", "ProLiant", "iLO", "سرور HP")):
            c = build_chapter02_lesson(title_fa, title_en)
            if c: return _ensure_dense(title_fa, title_en, level, c)
    except Exception:
        pass
    try:
        teacher01 = load_chapter_authoring(1, "chapter01_teacher")
        build_chapter01_lesson = teacher01.build_chapter01_lesson
        _bucket = teacher01._bucket
        _topic = teacher01._topic
        topic0 = _topic(title_fa)
        if _bucket(topic0) in ("cpu", "ram", "storage", "mb", "psu") or any(k in (title_fa or "") for k in ("CPU", "ALU", "RAM", "DDR", "SSD", "HDD", "NVMe", "مادربرد", "Chipset", "PSU", "تغذیه")):
            if not any(k in (title_fa or "") for k in ("BIOS", "UEFI", "Boot", "CPU بالا", "RAID", "LAN", "IPv4", "TCP", "DNS", "DHCP", "VLAN", "OSPF", "MPLS", "Multicast", "VXLAN")):
                c = build_chapter01_lesson(title_fa, title_en)
                if c: return _ensure_dense(title_fa, title_en, level, c)
    except Exception:
        pass
    from core.deep_fallback import build_deep_fallback
    return build_deep_fallback(title_fa, title_en, level or level_tag(title_fa))


def _content_len(d: Dict[str, Any]) -> int:
    return sum(len(str(d.get(k) or "")) for k in ("summary", "full_content", "commands", "examples", "notes"))


def _ensure_dense(title_fa: str, title_en: str, level: str | None, candidate: Dict[str, Any] | None) -> Dict[str, Any]:
    from core.deep_fallback import build_deep_fallback
    dense = build_deep_fallback(title_fa, title_en, level or level_tag(title_fa))
    if not candidate:
        return dense
    if _content_len(candidate) >= 4000:
        return candidate
    out = dict(dense)
    for k in ("commands", "examples", "notes", "lab"):
        cv = str(candidate.get(k) or "")
        if len(cv) > len(str(out.get(k) or "")):
            out[k] = cv
    cs = str(candidate.get("summary") or "").strip()
    if cs and cs not in str(out.get("summary") or ""):
        out["summary"] = cs + " | " + str(out.get("summary") or "")
    cf = str(candidate.get("full_content") or "").strip()
    if cf and len(cf) > 80:
        out["full_content"] = str(out.get("full_content") or "") + "\n\n---\n## یادداشت تخصصی Teacher\n\n" + cf
    out["level"] = candidate.get("level") or out.get("level")
    out["topic"] = candidate.get("topic") or out.get("topic")
    out["category"] = candidate.get("category") or out.get("category")
    return out
