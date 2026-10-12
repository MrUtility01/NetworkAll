# -*- coding: utf-8 -*-
"""محتوای عمیق: teacher اختصاصی + deep_fallback."""
from __future__ import annotations
import re
from typing import Any, Dict
from core.rich_data import BANKS, COMMON

def level_tag(title: str) -> str:
    m = re.match(r"\[(L[0-4])\]", title or "")
    return m.group(1) if m else "L0"

def clean_topic(title: str) -> str:
    t = re.sub(r"^\[L[0-4]\]\s*", "", title or "").strip()
    t = re.sub(r"\s*[—\-]\s*(آشنایی|مقدماتی|ادمین|مهندس|خبره).*$", "", t, flags=re.I)
    return t.strip() or (title or "موضوع")

def _contains_any(title: str, terms: tuple[str, ...]) -> bool:
    """Case-insensitive topic dispatch without matching short acronyms inside unrelated words."""
    haystack = (title or "").casefold()
    for term in terms:
        needle = str(term).casefold().strip()
        if not needle:
            continue
        # Short Latin acronyms (TTL, ARP, AP, RAM, etc.) must be standalone tokens.
        # This prevents e.g. "TTL" from matching the letters inside "Bottleneck".
        if len(needle) <= 3 and needle.isascii() and needle.isalpha():
            if re.search(rf"(?<![a-z0-9]){re.escape(needle)}(?![a-z0-9])", haystack):
                return True
        elif needle in haystack:
            return True
    return False


def _fmt_cmds(pairs):
    return "\n".join(f"```\n{cmd}\n```\n→ {desc}\n" for cmd, desc in pairs)

def build_rich_lesson(title_fa: str, title_en: str = "", level: str | None = None) -> Dict[str, Any]:
    try:
        from core.chapter64_git_hook import is_git_title, build_git_lesson
        if is_git_title(title_fa or ""):
            c = build_git_lesson(title_fa, title_en)
            if c:
                return _ensure_dense(title_fa, title_en, level, c)
    except Exception:
        pass
    try:
        from core.chapter17_teacher import build_chapter17_lesson
        if _contains_any(title_fa, ("VXLAN", "VNI", "VTEP", "Overlay", "EVPN", "Control Plane", "Route Type", "Leaf", "Spine", "Underlay", "Anycast", "RT-2", "RT-3", "RT-5")):
            c = build_chapter17_lesson(title_fa, title_en)
            if c: return _ensure_dense(title_fa, title_en, level, c)
    except Exception:
        pass
    try:
        from core.chapter16_teacher import build_chapter16_lesson
        if _contains_any(title_fa, ("Multicast", "PIM", "IGMP", "Dense", "Sparse", "IPTV", "چرا Multicast", "Rendezvous", "MLD", "SSM")):
            c = build_chapter16_lesson(title_fa, title_en)
            if c: return _ensure_dense(title_fa, title_en, level, c)
    except Exception:
        pass
    try:
        from core.chapter15_teacher import build_chapter15_lesson
        if _contains_any(title_fa, ("VRF", "MPLS", "Label", "L3VPN", "PE P CE", "LDP", "LSP", "Route Target", "Route Distinguisher", "VPNv4", "Label Switching", "PHP")):
            c = build_chapter15_lesson(title_fa, title_en)
            if c: return _ensure_dense(title_fa, title_en, level, c)
    except Exception:
        pass
    try:
        from core.chapter14_teacher import build_chapter14_lesson
        if _contains_any(title_fa, ("Static Route", "OSPF", "Link-State", "EIGRP", "Metric مرکب", "BGP", "AS Number", "Prefix-list", "route-map", "Redistribut", "Floating", "LSA", "eBGP", "iBGP", "Administrative Distance", "next-hop")):
            c = build_chapter14_lesson(title_fa, title_en)
            if c: return _ensure_dense(title_fa, title_en, level, c)
    except Exception:
        pass
    try:
        from core.chapter13_teacher import build_chapter13_lesson
        if _contains_any(title_fa, ("VLAN", "مفهوم VLAN", "Trunk", "STP", "RSTP", "Loop", "Root Bridge", "EtherChannel", "LACP", "Port Security", "DHCP Snooping", "BPDU", "802.1X", "PortFast", "Native VLAN", "SVI", "Storm Control", "DAI")):
            c = build_chapter13_lesson(title_fa, title_en)
            if c: return _ensure_dense(title_fa, title_en, level, c)
    except Exception:
        pass
    try:
        from core.chapter12_teacher import build_chapter12_lesson
        if _contains_any(title_fa, ("Cat5", "Cat6", "Cat6A", "OM3", "OM4", "فیبر", "Fiber", "رک", "Rack", "Wiremap", "PDU", "PoE", "T568", "RJ45", "OTDR")):
            c = build_chapter12_lesson(title_fa, title_en)
            if c: return _ensure_dense(title_fa, title_en, level, c)
    except Exception:
        pass
    try:
        from core.chapter11_teacher import build_chapter11_lesson
        if _contains_any(title_fa, ("DHCP", "DORA", "Discover", "Offer", "Relay", "helper", "IPAM", "Lease", "Scope", "Reservation", "APIPA", "Renew")):
            c = build_chapter11_lesson(title_fa, title_en)
            if c: return _ensure_dense(title_fa, title_en, level, c)
    except Exception:
        pass
    try:
        from core.chapter10_teacher import build_chapter10_lesson
        if _contains_any(title_fa, ("DNS", "Resolver", "AAAA", "CNAME", "MX", "TXT", "SOA", "PTR", "SRV", "Forwarder", "DNSSEC", "رکورد", "TTL", "nslookup")):
            c = build_chapter10_lesson(title_fa, title_en)
            if c: return _ensure_dense(title_fa, title_en, level, c)
    except Exception:
        pass
    try:
        from core.chapter09_teacher import build_chapter09_lesson
        if _contains_any(title_fa, ("ARP", "ICMP", "Echo", "Three-way", "Handshake", "TCP", "UDP", "Sequence", "Window", "SYN", "FIN", "RST", "traceroute", "ویژگی‌ها")):
            c = build_chapter09_lesson(title_fa, title_en)
            if c: return _ensure_dense(title_fa, title_en, level, c)
    except Exception:
        pass
    try:
        from core.chapter08_teacher import build_chapter08_lesson
        if _contains_any(title_fa, ("IPv4", "IPv6", "Subnet", "ساب‌نت", "ماسک", "CIDR", "VLSM", "SLAAC", "fe80", "NDP", "RFC1918", "DMZ")):
            c = build_chapter08_lesson(title_fa, title_en)
            if c: return _ensure_dense(title_fa, title_en, level, c)
    except Exception:
        pass
    try:
        from core.chapter07_teacher import build_chapter07_lesson
        if _contains_any(title_fa, ("فریم", "Frame", "اترنت", "Ethernet", "MAC Table", "Learning", "Store-and-Forward", "سوییچ", "Switch", "Duplex", "FCS", "CRC", "CAM", "MTU", "SFP")):
            c = build_chapter07_lesson(title_fa, title_en)
            if c: return _ensure_dense(title_fa, title_en, level, c)
    except Exception:
        pass
    try:
        from core.chapter06_teacher import build_chapter06_lesson
        if _contains_any(title_fa, ("LAN", "WAN", "WLAN", "OSI", "TCP/IP", "Packet", "Encapsulation", "توپولوژی", "Broadcast", "Unicast", "Gateway", "مبانی شبکه")):
            if not _contains_any(title_fa, ("IPv4", "IPv6", "Subnet", "ARP", "ICMP", "DNS", "DHCP", "VLAN", "STP", "OSPF", "BGP", "MPLS", "Multicast", "VXLAN", "EVPN")):
                c = build_chapter06_lesson(title_fa, title_en)
                if c: return _ensure_dense(title_fa, title_en, level, c)
    except Exception:
        pass
    try:
        from core.chapter03_teacher import build_chapter03_lesson
        if _contains_any(title_fa, ("BIOS", "UEFI", "بوت", "Boot", "Secure Boot", "TPM", "CMOS", "GRUB", "PXE", "systemd-boot", "bootloader")):
            c = build_chapter03_lesson(title_fa, title_en)
            if c: return _ensure_dense(title_fa, title_en, level, c)
    except Exception:
        pass
    try:
        from core.chapter05_teacher import build_chapter05_lesson
        if _contains_any(title_fa, ("FAT", "NTFS", "ext4", "XFS", "Btrfs", "Snapshot", "ZFS", "MBR", "GPT", "پارتیشن", "RAID", "fsck", "mount", "mdadm")):
            c = build_chapter05_lesson(title_fa, title_en)
            if c: return _ensure_dense(title_fa, title_en, level, c)
    except Exception:
        pass
    try:
        from core.chapter04_teacher import build_chapter04_lesson
        if _contains_any(title_fa, ("Kernel", "هسته", "Registry", "ویندوز", "Windows", "لینوکس", "Linux", "systemd", "journalctl", "FHS", "filesystem", "file system", "سلسله‌مراتب", "inode", "chmod", "swap", "resource", "bottleneck", "iostat", "گلوگاه", "Process", "PowerShell", "Task Manager")):
            c = build_chapter04_lesson(title_fa, title_en)
            if c: return _ensure_dense(title_fa, title_en, level, c)
    except Exception:
        pass
    try:
        from core.chapter02_teacher import build_chapter02_lesson
        if _contains_any(title_fa, ("ESD", "ایمنی", "اسمبل", "Beep", "ProLiant", "iLO", "سرور HP")):
            c = build_chapter02_lesson(title_fa, title_en)
            if c: return _ensure_dense(title_fa, title_en, level, c)
    except Exception:
        pass
    try:
        from core.chapter01_teacher import build_chapter01_lesson, _bucket, _topic
        topic0 = _topic(title_fa)
        if _bucket(topic0) in ("cpu", "ram", "storage", "mb", "psu") or _contains_any(title_fa, ("CPU", "ALU", "RAM", "DDR", "SSD", "HDD", "NVMe", "مادربرد", "Chipset", "PSU", "تغذیه")):
            if not _contains_any(title_fa, ("BIOS", "UEFI", "Boot", "CPU بالا", "RAID", "LAN", "IPv4", "TCP", "DNS", "DHCP", "VLAN", "OSPF", "MPLS", "Multicast", "VXLAN")):
                c = build_chapter01_lesson(title_fa, title_en)
                if c: return _ensure_dense(title_fa, title_en, level, c)
    except Exception:
        pass
    from core.deep_fallback import build_deep_fallback
    return build_deep_fallback(title_fa, title_en, level or level_tag(title_fa))


def _content_len(d: Dict[str, Any]) -> int:
    return sum(len(str(d.get(k) or "")) for k in ("summary", "full_content", "commands", "examples", "notes"))


def _dense_support_sections(dense_content: str, candidate_content: str) -> list[str]:
    """Select operational depth from fallback without replacing specialist prose with generic boilerplate."""
    support = {
        "## اهداف یادگیری": ("اهداف یادگیری", "learning objectives"),
        "## پیش‌نیازها": ("پیش‌نیاز", "prerequisite"),
        "## ۵) امنیت": ("## امنیت", "## security", "hardening"),
        "## ۶) جدول عیب‌یابی سریع": ("عیب‌یابی", "troubleshooting", "root cause", "rca"),
        "## ۷) چک‌لیست Production": ("چک‌لیست production", "production checklist", "قبل از apply"),
        "## ۹) خودآزمایی و پاسخ‌نامه": ("پاسخ‌نامه", "answer key", "self assessment", "خودآزمایی", "assessment"),
        "## ۱۰) منابع رسمی و مراجع": ("منابع رسمی", "official sources", "مراجع", "references"),
    }
    body_lower = (candidate_content or "").casefold()
    blocks: list[str] = []
    current: list[str] = []
    for line in (dense_content or "").splitlines():
        if line.startswith("## "):
            if current:
                blocks.append("\n".join(current).strip())
            current = [line]
        elif current:
            current.append(line)
    if current:
        blocks.append("\n".join(current).strip())

    chosen = []
    for block in blocks:
        heading = block.splitlines()[0].strip()
        rule = next((markers for prefix, markers in support.items() if heading.startswith(prefix)), None)
        if not rule:
            continue
        if any(marker.casefold() in body_lower for marker in rule):
            continue
        chosen.append(block)
    return chosen


def _ensure_dense(title_fa: str, title_en: str, level: str | None, candidate: Dict[str, Any] | None) -> Dict[str, Any]:
    from core.deep_fallback import build_deep_fallback
    dense = build_deep_fallback(title_fa, title_en, level or level_tag(title_fa))
    if not candidate:
        return dense

    # Long specialist lessons keep their own body; fallback fills structured fields only.
    if _content_len(candidate) >= 4000:
        out = dict(candidate)
        if not isinstance(out.get("assessment"), dict) or not out["assessment"].get("questions") or not out["assessment"].get("answer_key"):
            out["assessment"] = dense.get("assessment") or {}
        if not out.get("learning_objectives"):
            out["learning_objectives"] = dense.get("learning_objectives") or []
        if not out.get("prerequisites"):
            out["prerequisites"] = dense.get("prerequisites") or []
        if not out.get("source_status"):
            out["source_status"] = "review_required"
        return out

    # For shorter specialist lessons, make the specialist explanation the primary
    # text and append only missing safety/RCA/checklist/assessment/source sections.
    out = dict(dense)
    candidate_body = str(candidate.get("full_content") or "").strip()
    if len(candidate_body) > 80:
        support = _dense_support_sections(str(dense.get("full_content") or ""), candidate_body)
        pieces = [candidate_body]
        if support:
            pieces.append("\n\n---\n\n".join(support))
        out["full_content"] = "\n\n---\n\n".join(pieces)

    specialist_category = str(candidate.get("category") or "").strip()
    dense_category = str(dense.get("category") or "").strip()
    category_differs = bool(specialist_category and specialist_category != dense_category)

    for key in ("commands", "examples", "lab"):
        cv = str(candidate.get(key) or "").strip()
        dv = str(dense.get(key) or "").strip()
        if cv and (category_differs or len(cv) > len(dv)):
            out[key] = cv

    candidate_notes = str(candidate.get("notes") or "").strip()
    dense_notes = str(dense.get("notes") or "").strip()
    if candidate_notes and candidate_notes not in dense_notes:
        out["notes"] = "\n\n".join(x for x in (dense_notes, candidate_notes) if x)

    candidate_summary = str(candidate.get("summary") or "").strip()
    dense_summary = str(dense.get("summary") or "").strip()
    if candidate_summary and candidate_summary not in dense_summary:
        out["summary"] = " | ".join(x for x in (candidate_summary, dense_summary) if x)

    out["level"] = candidate.get("level") or out.get("level")
    out["topic"] = candidate.get("topic") or out.get("topic")
    out["category"] = specialist_category or out.get("category")
    if not isinstance(candidate.get("assessment"), dict) or not candidate["assessment"].get("questions") or not candidate["assessment"].get("answer_key"):
        out["assessment"] = dense.get("assessment") or {}
    else:
        out["assessment"] = candidate["assessment"]
    out["learning_objectives"] = candidate.get("learning_objectives") or dense.get("learning_objectives") or []
    out["prerequisites"] = candidate.get("prerequisites") or dense.get("prerequisites") or []
    out["source_status"] = candidate.get("source_status") or dense.get("source_status") or "review_required"
    return out
