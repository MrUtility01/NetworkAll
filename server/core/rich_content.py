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
        "## واژه‌نامهٔ تخصصی": ("## واژه‌نامهٔ تخصصی", "## glossary", "## اصطلاحات کلیدی"),
        "## خروجی مورد انتظار و معیار قبولی": ("## خروجی مورد انتظار", "## expected output"),
        "## سناریوی عملی و Lab acceptance": ("## سناریوی عملی", "## scenario"),
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



def _assessment_with_floor(candidate: Dict[str, Any] | None, fallback: Dict[str, Any] | None, level: str | None) -> Dict[str, Any]:
    """Keep lesson-specific MCQs and append answer-matched items to the L0-L4 floor."""
    floors = {"L0": 5, "L1": 8, "L2": 10, "L3": 12, "L4": 15}
    target = floors.get(str(level or "L0").upper(), 5)
    candidate = candidate if isinstance(candidate, dict) else {}
    fallback = fallback if isinstance(fallback, dict) else {}
    base_questions = fallback.get("questions") if isinstance(fallback.get("questions"), list) else []
    base_answers = fallback.get("answer_key") if isinstance(fallback.get("answer_key"), list) else []
    base_answer_by_id = {str(x.get("id") or x.get("question_id") or ""): x for x in base_answers if isinstance(x, dict)}
    fallback_pairs = []
    for q in base_questions:
        if not isinstance(q, dict):
            continue
        ans = base_answer_by_id.get(str(q.get("id") or ""))
        if ans is not None and isinstance(q.get("options"), list) and len(q["options"]) >= 2:
            fallback_pairs.append((dict(q), dict(ans)))

    qs = candidate.get("questions") if isinstance(candidate.get("questions"), list) else []
    raw_answers = candidate.get("answer_key")
    if isinstance(raw_answers, list):
        answer_by_id = {str(x.get("id") or x.get("question_id") or ""): x for x in raw_answers if isinstance(x, dict)}
    elif isinstance(raw_answers, dict):
        answer_by_id = {str(k): (v if isinstance(v, dict) else {"answer": v}) for k, v in raw_answers.items()}
    else:
        answer_by_id = {}
    out_q, out_a, used = [], [], set()
    for i, raw_q in enumerate(qs):
        if len(out_q) >= target or not isinstance(raw_q, dict):
            continue
        q = dict(raw_q)
        old_id = str(q.get("id") or f"question_{i + 1}")
        ans = answer_by_id.get(old_id)
        ci = q.get("correct_index")
        if isinstance(ans, dict):
            if ci is None:
                ci = ans.get("correct_index")
            if ci is None:
                val = ans.get("answer")
                if isinstance(val, int) or (isinstance(val, str) and val.strip().isdigit()):
                    ci = int(val)
        if not isinstance(q.get("options"), list) or len(q["options"]) < 2 or ci is None:
            continue
        try:
            ci = int(ci)
        except (TypeError, ValueError):
            continue
        if not 0 <= ci < len(q["options"]):
            continue
        qid = old_id if old_id not in used else f"lesson_q_{i + 1}"
        used.add(qid)
        q["id"] = qid
        out_q.append(q)
        out_a.append({"id": qid, "correct_index": ci, "explanation": str((ans or {}).get("explanation") or (ans or {}).get("rationale") or q.get("explanation") or "پاسخ با معیار پذیرش درس توجیه شود.")})

    for base_q, base_a in fallback_pairs:
        if len(out_q) >= target:
            break
        qid = f"support_{len(out_q) + 1}"
        while qid in used:
            qid += "_x"
        q = dict(base_q)
        q["id"] = qid
        used.add(qid)
        out_q.append(q)
        out_a.append({"id": qid, "correct_index": int(base_a.get("correct_index", 0)), "explanation": str(base_a.get("explanation") or "پاسخ با معیار پذیرش درس توجیه شود.")})
    if not out_q:
        return {"questions": list(base_questions[:target]), "answer_key": list(base_answers[:target])}
    return {"questions": out_q, "answer_key": out_a}


def _ensure_dense(title_fa: str, title_en: str, level: str | None, candidate: Dict[str, Any] | None) -> Dict[str, Any]:
    from core.deep_fallback import build_deep_fallback
    dense = build_deep_fallback(title_fa, title_en, level or level_tag(title_fa))
    if not candidate:
        return dense

    # Long specialist lessons remain primary, but the reading tab must also expose
    # missing self-tests/answer keys and source/checklist sections from the deep fallback.
    if _content_len(candidate) >= 4000:
        out = dict(candidate)
        candidate_body = str(out.get("full_content") or "").strip()
        support = _dense_support_sections(str(dense.get("full_content") or ""), candidate_body)
        if support:
            pieces = [candidate_body] if candidate_body else []
            pieces.extend(support)
            out["full_content"] = "\n\n---\n\n".join(pieces)
        out["assessment"] = _assessment_with_floor(out.get("assessment"), dense.get("assessment"), level or level_tag(title_fa))
        out["official_sources"] = out.get("official_sources") or dense.get("official_sources") or []
        out["lab_status"] = out.get("lab_status") or dense.get("lab_status") or "designed_not_executed"
        out["content_status"] = out.get("content_status") or dense.get("content_status") or "review_required"
        out["prerequisites"] = out.get("prerequisites") or dense.get("prerequisites") or []
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
    out["assessment"] = _assessment_with_floor(candidate.get("assessment"), dense.get("assessment"), level or level_tag(title_fa))
    out["learning_objectives"] = candidate.get("learning_objectives") or dense.get("learning_objectives") or []
    out["prerequisites"] = candidate.get("prerequisites") or dense.get("prerequisites") or []
    out["source_status"] = candidate.get("source_status") or dense.get("source_status") or "review_required"
    out["official_sources"] = candidate.get("official_sources") or dense.get("official_sources") or []
    out["lab_status"] = candidate.get("lab_status") or dense.get("lab_status") or "designed_not_executed"
    out["content_status"] = candidate.get("content_status") or dense.get("content_status") or "review_required"
    return out
