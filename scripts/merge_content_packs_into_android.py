#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""ادغام بسته‌های tools؛ فصل ۶۴=Git؛ امنیت→۶۵؛ OSPF/VPN→۶۶/۶۷؛ دستورات→۶۸."""
from __future__ import annotations
import gzip, json, sys, re
from pathlib import Path
from collections import defaultdict

ROOT = Path(__file__).resolve().parents[1]
GZ = ROOT / "android/app/src/main/assets/curriculum_index.json.gz"


def as_text(v):
    if v is None:
        return ""
    if isinstance(v, list):
        return "\n".join(str(x) for x in v)
    return str(v)


def load_json(p: Path):
    return json.loads(p.read_text(encoding="utf-8"))


def find_pack_files():
    """فقط مسیرهای مجاز — prompts/ اسکن نمی‌شود (سرعت/پایداری)."""
    files = []
    files += list(ROOT.glob("tools/packs/**/*.json"))
    files += list(ROOT.glob("tools/engineer_jokar_*/*pack*.json"))
    files += list(ROOT.glob("tools/engineer_jokar_*/*curriculum*.json"))
    files += list(ROOT.glob("tools/ENGINEER_JOKAR_*.json"))
    uniq, seen = [], set()
    for f in files:
        name = f.name.lower()
        if name.endswith(".md") or name in ("readme.md", "readme_fa.md"):
            continue
        if " " in f.name:
            print(" skip spaced name:", f)
            continue
        if name.endswith(".json.json"):
            print(" skip double ext:", f)
            continue
        if "/prompts/" in str(f).replace("\\", "/").lower():
            continue
        k = str(f.resolve())
        if k not in seen and f.stat().st_size > 500:
            seen.add(k)
            uniq.append(f)
    return sorted(uniq)


def commands_to_lessons(data: dict, source_key: str = "pack") -> list:
    ch = int(data.get("chapter_order") or 68)
    out = []
    # Stable, human-readable collection buckets for Chapter 68.
    collection_map = {
        "linux": ("Linux", 101), "bash": ("Bash", 102),
        "powershell": ("PowerShell", 103), "power_shell": ("PowerShell", 103),
        "cmd": ("Windows CMD", 104), "batch": ("Windows Batch", 105),
        "windows_batch": ("Windows Batch", 105), "windows_cmd": ("Windows CMD", 104),
        "cisco": ("Cisco IOS/IOS-XE", 106), "routeros": ("MikroTik RouterOS", 107),
        "mikrotik": ("MikroTik RouterOS", 107), "fortigate": ("FortiGate", 108),
        "issabel": ("Issabel / Asterisk", 109),
    }
    sub_map = {
        "basics": 1, "interface": 2, "vlan": 3, "trunk": 3, "stp": 4, "spanning-tree": 4,
        "etherchannel": 5, "port-security": 6, "mac": 7, "cdp": 8, "lldp": 8,
        "troubleshoot": 9, "switching": 2, "general": 10,
        "routing": 11, "ospf": 12, "bgp": 13, "acl": 14, "nat": 15,
        "prefix-list": 16, "route-map": 17, "redistribution": 18, "verification": 19,
        "networking": 20, "files": 21, "process": 22, "services": 23, "dns": 24,
        "api": 25, "logs": 26, "storage": 27, "scripting": 28, "variables": 29,
        "loops": 30, "environment": 31, "errors": 32,
    }
    for i, c in enumerate(data.get("commands") or [], 1):
        if not isinstance(c, dict):
            continue
        cmd = c.get("command") or c.get("title_en") or ""
        level = c.get("level") or "L1"
        category_raw = str(c.get("category") or data.get("platform") or "general").strip().lower().replace("-", "_").replace("/", "_")
        # category is usually a functional area (routing/VLAN/firewall), not
        # the vendor/platform. Resolve the collection from record, pack
        # metadata and source filename before using a generic fallback.
        vendor_blob = " ".join(str(v or "") for v in (
            c.get("vendor"), c.get("platform"), data.get("vendor_pack"),
            data.get("vendor"), data.get("platform"), source_key
        )).lower().replace("_", " ").replace("-", " ")
        raw_title = str(c.get("title_fa") or cmd)
        shell_collection = {
            "linux": ("Linux", 101),
            "bash": ("Bash", 102),
            "powershell": ("PowerShell", 103),
            "power_shell": ("PowerShell", 103),
            "cmd": ("Windows CMD", 104),
            "windows_cmd": ("Windows CMD", 104),
            "batch": ("Windows Batch", 105),
            "windows_batch": ("Windows Batch", 105),
        }
        if category_raw in shell_collection:
            collection, collection_order = shell_collection[category_raw]
        elif "windows batch" in vendor_blob or "win batch" in vendor_blob:
            collection, collection_order = ("Windows Batch", 105)
        elif "windows cmd" in vendor_blob or "command prompt" in vendor_blob or "cmd" in vendor_blob:
            collection, collection_order = ("Windows CMD", 104)
        elif "powershell" in vendor_blob or "power shell" in vendor_blob:
            collection, collection_order = ("PowerShell", 103)
        elif "bash" in vendor_blob:
            collection, collection_order = ("Bash", 102)
        elif "linux" in vendor_blob:
            collection, collection_order = ("Linux", 101)
        elif any(k in vendor_blob for k in ("mikrotik", "routeros", "ros7")):
            collection, collection_order = ("MikroTik RouterOS", 107)
        elif any(k in vendor_blob for k in ("cisco", "ios xe", "ios-xe")):
            collection, collection_order = ("Cisco IOS/IOS-XE", 106)
        elif any(k in vendor_blob for k in ("fortigate", "fortios")):
            collection, collection_order = ("FortiGate", 108)
        elif any(k in vendor_blob for k in ("issabel", "asterisk")):
            collection, collection_order = ("Issabel / Asterisk", 109)
        else:
            collection, collection_order = (
                str(c.get("platform") or data.get("platform") or category_raw).strip() or "عمومی",
                199,
            )
        if category_raw in ("cmd", "windows_cmd") and any(token in (raw_title + " " + cmd).lower() for token in ("batch", "errorlevel", "delayed expansion", "setlocal", "goto ", "@echo off", "for /f", "if errorlevel")):
            collection, collection_order = ("Windows Batch", 105)
        title_fa = c.get("title_fa") or cmd
        if not str(title_fa).startswith("[L"):
            title_fa = f"[{level}] {title_fa}"
        # Put the collection in every lesson title so it remains identifiable
        # in flat search results and screens that do not display the tree path.
        if not str(title_fa).startswith(f"[{collection}]"):
            title_fa = f"[{collection}] {title_fa}"
        sub = (c.get("subcategory") or c.get("category") or "general").strip().lower()
        sub_order = collection_order * 100 + sub_map.get(sub, 10)
        args = c.get("arguments") or []
        arg_lines = []
        for a in args:
            if isinstance(a, dict):
                arg_lines.append(
                    f"- `{a.get('name', '')}`: {a.get('meaning_fa', '')} — مثال: `{a.get('example', '')}`"
                )
            else:
                arg_lines.append(f"- {a}")
        steps = c.get("steps_fa") or []
        if isinstance(steps, list):
            steps_txt = "\n".join(f"{idx}. {s}" for idx, s in enumerate(steps, 1))
        else:
            steps_txt = str(steps)
        out_fields = c.get("output_fields_fa") or []
        of_txt = "\n".join(
            f"- **{x.get('field', '')}**: {x.get('meaning', '')}" if isinstance(x, dict) else f"- {x}"
            for x in out_fields
        )
        related = c.get("related_commands") or []
        rel_txt = ", ".join(f"`{x}`" for x in related) if isinstance(related, list) else str(related)
        mistakes = c.get("common_mistakes_fa") or []
        mist_txt = "\n".join(f"- {m}" for m in mistakes) if isinstance(mistakes, list) else str(mistakes)
        kw = c.get("search_keywords") or []
        kw_txt = ", ".join(kw) if isinstance(kw, list) else str(kw)
        aliases = c.get("aliases") or []
        alias_txt = ", ".join(aliases) if isinstance(aliases, list) else str(aliases)
        prereq = c.get("prerequisites_fa") or []
        prereq_txt = "\n".join(f"- {x}" for x in prereq) if isinstance(prereq, list) else str(prereq)

        full = (
            f"# {c.get('title_fa') or cmd}\n\n"
            f"## دستور\n```text\n{cmd}\n```\n"
            f"**Aliases:** {alias_txt}\n\n**Syntax:** `{c.get('syntax') or cmd}`\n\n"
            f"## چه زمانی\n{c.get('when_to_use_fa') or ''}\n\n"
            f"## پیش‌نیاز\n{prereq_txt or '- —'}\n\n"
            f"## آرگومان‌ها\n{chr(10).join(arg_lines) if arg_lines else '- —'}\n\n"
            f"## مراحل\n{steps_txt or '- —'}\n\n"
            f"## نمونه خروجی\n```text\n{c.get('sample_output') or ''}\n```\n\n"
            f"## فیلدهای خروجی\n{of_txt or '- —'}\n\n"
            f"## دستورات مرتبط\n{rel_txt or '—'}\n\n"
            f"## اشتباهات رایج\n{mist_txt or '- —'}\n\n"
            f"## Lab\n{c.get('lab_hint_fa') or ''}\n\n"
            f"## امنیت\n{c.get('security_notes_fa') or ''}\n\n"
            f"## کلیدواژه جستجو\n{kw_txt}\n"
        )
        tip_items = c.get("tips_fa") or c.get("key_points_fa") or c.get("tips") or []
        if not isinstance(tip_items, list):
            tip_items = [str(tip_items)]
        note_sections = []
        if tip_items:
            note_sections.append("## نکات کلیدی\n" + "\n".join(f"- {x}" for x in tip_items))
        if mistakes:
            note_sections.append("## خطاهای رایج\n" + mist_txt)
        security_tip = c.get("security_notes_fa") or ""
        if security_tip:
            note_sections.append("## نکات امنیتی\n" + str(security_tip))
        lab_tip = c.get("lab_hint_fa") or ""
        if lab_tip:
            note_sections.append("## معیار تمرین / آزمایشگاه\n" + str(lab_tip))
        notes = "\n\n".join(note_sections)
        flash = c.get("flashcards")
        assess = c.get("assessment")
        meta = {}
        if assess:
            meta["assessment"] = assess
            notes += "\n\n<!-- EJ_ASSESSMENT\n" + json.dumps(assess, ensure_ascii=False) + "\n-->\n"
        if flash:
            meta["flashcards"] = flash
            notes += "\n\n<!-- EJ_FLASHCARDS\n" + json.dumps(flash, ensure_ascii=False) + "\n-->\n"

        source_slug = re.sub(r"[^a-zA-Z0-9_-]+", "_", source_key.lower()).strip("_")[:32] or "pack"
        lesson_uid = f"lesson:ch{ch:02d}:cmd:{source_slug}:{i:04d}"
        out.append({
            "uid": lesson_uid,
            "chapter_order": ch,
            "subchapter_order": sub_order,
            "subchapter_title_fa": f"{collection} — {sub.replace('_', ' ').title()}",
            "collection": collection,
            "platform": str(data.get("platform") or collection),
            "vendor": str(data.get("vendor") or collection),
            "lesson_order": i,
            "level": level,
            "title_fa": title_fa,
            "title_en": c.get("title_en") or cmd,
            "summary": (c.get("when_to_use_fa") or title_fa)[:220],
            "full_content": full,
            "commands": cmd + (("\n" + alias_txt) if alias_txt else ""),
            "examples": c.get("sample_output") or "",
            "notes": notes.strip(),
            "meta": meta,
            "source_status": "review_required",
        })
    return out


def blueprint_to_lessons(d, focus_keywords, default_ch):
    out, li = [], 0
    for ch in (d.get("curriculum") or {}).get("chapters") or []:
        ch_title = ch.get("title_fa") or ""
        for ci, col in enumerate(ch.get("collections") or [], 1):
            for les in col.get("lessons") or []:
                for sub in les.get("sub_lessons") or []:
                    title = sub.get("title_fa") or les.get("title_fa") or "درس"
                    content = sub.get("content") or ""
                    status = sub.get("status") or ""
                    blob = (title + " " + content + " " + ch_title).upper()
                    if focus_keywords and not any(k.upper() in blob for k in focus_keywords):
                        continue
                    if status == "seeded" and len(content) < 350:
                        continue
                    if len(content) < 350 and status not in ("reviewed_content", "developed"):
                        continue
                    li += 1
                    target = default_ch
                    if any(k in blob for k in ("OSPF", "BGP", "REDIS", "EIGRP", "ROUTE-MAP")):
                        target = 14
                    if any(k in blob for k in ("IPSEC", "IKE", "SSL VPN", "PHASE", "TUNNEL", "VPN")):
                        target = 57
                    full = content
                    if sub.get("commands"):
                        full += "\n\n## دستورات\n\n" + str(sub.get("commands"))
                    out.append({
                        "uid": f"lesson:ch{target:02d}:bp:{li:04d}",
                        "title_fa": title if str(title).startswith("[L") else f"[L2] {title}",
                        "chapter_order": target,
                        "subchapter_order": ci,
                        "level": "L2",
                        "summary": (sub.get("summary") or content[:180]).strip(),
                        "full_content": full,
                        "commands": sub.get("commands") or "",
                        "examples": sub.get("examples") or "",
                        "notes": f"blueprint status={status}",
                    })
    return out


def normalize_pack(path: Path, data: dict):
    if data.get("commands"):
        return commands_to_lessons(data, path.stem)
    if data.get("lessons"):
        lessons = data.get("lessons") or []
        if int(data.get("chapter_order") or 0) == 68 or "chapter_68" in path.name.lower():
            stem = path.stem.lower()
            if "mikrotik" in stem or "routeros" in stem:
                collection, group_order = "MikroTik RouterOS", 107
            elif "cisco" in stem:
                collection, group_order = "Cisco IOS/IOS-XE", 106
            elif "powershell" in stem:
                collection, group_order = "PowerShell", 103
            elif "linux" in stem:
                collection, group_order = "Linux", 101
            elif "bash" in stem:
                collection, group_order = "Bash", 102
            elif "batch" in stem:
                collection, group_order = "Windows Batch", 105
            elif "cmd" in stem:
                collection, group_order = "Windows CMD", 104
            else:
                collection, group_order = path.stem.replace("_", " ").title(), 199
            for idx, lesson in enumerate(lessons, 1):
                if not isinstance(lesson, dict):
                    continue
                title = str(lesson.get("title_fa") or lesson.get("title") or "درس").strip()
                prefix = f"[{collection}]"
                if not title.startswith(prefix):
                    # Source packs often prefix titles with [L1] or a vendor
                    # alias. Keep the collection as the first visible label.
                    title = re.sub(r"^\[[^\]]+\]\s*", "", title).strip()
                    lesson["title_fa"] = f"{prefix} {title}"
                lesson["chapter_order"] = 68
                try:
                    old_sub_order = int(lesson.get("subchapter_order") or 10)
                except (TypeError, ValueError):
                    old_sub_order = 10
                local_order = old_sub_order if 1 <= old_sub_order <= 99 else 10
                lesson["subchapter_order"] = group_order * 100 + local_order
                old_sub_title = str(lesson.get("subchapter_title_fa") or lesson.get("category") or "عمومی").strip()
                if "—" in old_sub_title:
                    old_sub_title = old_sub_title.split("—", 1)[-1].strip()
                lesson["subchapter_title_fa"] = f"{collection} — {old_sub_title or 'عمومی'}"
                lesson["collection"] = collection
                lesson.setdefault("lesson_order", idx)
        return lessons
    name = path.name.upper()
    if "curriculum" in data:
        if any(k in name for k in ("OSPF", "BGP", "REDIS")):
            return blueprint_to_lessons(data, ["OSPF", "BGP", "Redistribution", "Adjacency", "eBGP", "iBGP", "SPF"], 14)
        if "VPN" in name or "IPSEC" in name:
            return blueprint_to_lessons(data, ["IPsec", "IKEv", "SSL VPN", "Phase", "Tunnel", "VPN"], 57)
        return blueprint_to_lessons(data, [], 1)
    return []


def apply_fields(les, src):
    # Preserve stable UIDs and chapter hierarchy; only merge fields into an exact title match.
    content_fields = (
        "summary", "full_content", "commands", "examples", "notes",
        "learning_objectives", "search_keywords", "search_query", "source_status",
    )
    for field in content_fields:
        if field in src and src[field] is not None:
            les[field] = src[field]
    # Merge metadata without discarding existing AI prompts or other metadata.
    incoming_meta = src.get("meta")
    if isinstance(incoming_meta, dict):
        previous_meta = les.get("meta")
        if not isinstance(previous_meta, dict):
            previous_meta = {}
        merged_meta = dict(previous_meta)
        for key, value in incoming_meta.items():
            if isinstance(value, dict) and isinstance(merged_meta.get(key), dict):
                nested = dict(merged_meta[key])
                nested.update(value)
                merged_meta[key] = nested
            else:
                merged_meta[key] = value
        les["meta"] = merged_meta

def merge_by_title(data, lessons):
    by = {}
    for src in lessons:
        title = (src.get("title_fa") or "").strip()
        by[(src.get("chapter_order"), title)] = src
        bare = re.sub(r"^\[L[0-4]\]\s*", "", title)
        by[(src.get("chapter_order"), bare)] = src
    n = 0
    for ch in data["chapters"]:
        for sub in ch.get("subchapters", []):
            for les in sub.get("lessons", []):
                t = (les.get("title_fa") or "").strip()
                src = by.get((ch.get("order"), t))
                if not src:
                    bare = re.sub(r"^\[L[0-4]\]\s*", "", t)
                    src = by.get((ch.get("order"), bare))
                if src:
                    apply_fields(les, src)
                    n += 1
    return n


def append_unmatched_as_extra(data, lessons, order, title_fa, title_en):
    if not lessons:
        return 0
    data["chapters"] = [c for c in data["chapters"] if c.get("order") != order]
    subs = defaultdict(list)
    sub_titles = {}
    for src in lessons:
        si = int(src.get("subchapter_order") or 1)
        subs[si].append(src)
        label = str(src.get("subchapter_title_fa") or src.get("collection") or "").strip()
        if not label:
            label = f"گروه دستورات {si}"
        sub_titles[si] = label
    out_subs = []
    for si in sorted(subs):
        les_out = []
        for src in sorted(subs[si], key=lambda x: (x.get("lesson_order") or 0)):
            notes = as_text(src.get("notes"))
            ass = (src.get("meta") or {}).get("assessment")
            if ass and "EJ_ASSESSMENT" not in notes:
                notes += "\n\n<!-- EJ_ASSESSMENT\n" + json.dumps(ass, ensure_ascii=False) + "\n-->\n"
            les_out.append({
                "uid": src.get("uid") or f"lesson:ch{order:02d}:s{int(si):03d}:l{len(les_out):04d}",
                "title_fa": src.get("title_fa") or "",
                "title_en": src.get("title_en") or "",
                "level": src.get("level") or "L0",
                "summary": src.get("summary") or "",
                "full_content": src.get("full_content") or "",
                "commands": as_text(src.get("commands")),
                "examples": as_text(src.get("examples")),
                "notes": notes,
                "meta": src.get("meta") if isinstance(src.get("meta"), dict) else {},
                "learning_objectives": src.get("learning_objectives") or [],
                "search_keywords": src.get("search_keywords") or [],
                "search_query": src.get("search_query") or "",
                "source_status": src.get("source_status") or "review_required",
                "collection": src.get("collection") or sub_titles.get(si, f"زیرفصل {si}"),
            })
        out_subs.append({"title_fa": sub_titles.get(si, f"گروه دستورات {si}"), "lessons": les_out})
    data["chapters"].append({
        "order": order,
        "title_fa": title_fa,
        "title_en": title_en,
        "subchapters": out_subs,
    })
    return sum(len(s["lessons"]) for s in out_subs)


def build_ch65(lessons):
    subs = defaultdict(list)
    for les in lessons:
        subs[les.get("subchapter_order") or 1].append(les)
    out = []
    for si in sorted(subs):
        items = sorted(subs[si], key=lambda x: (x.get("lesson_order") or 0, x.get("level") or ""))
        seen, les_out = set(), []
        for src in items:
            uid = src.get("uid") or f"lesson:ch65:s{int(si):03d}:l{len(les_out):04d}"
            if uid in seen:
                continue
            seen.add(uid)
            notes = as_text(src.get("notes"))
            ass = (src.get("meta") or {}).get("assessment")
            if ass and "EJ_ASSESSMENT" not in notes:
                notes += "\n\n<!-- EJ_ASSESSMENT\n" + json.dumps(ass, ensure_ascii=False) + "\n-->\n"
            les_out.append({
                "uid": uid,
                "title_fa": src.get("title_fa") or "",
                "title_en": src.get("title_en") or "",
                "level": src.get("level") or "L0",
                "summary": src.get("summary") or "",
                "full_content": src.get("full_content") or "",
                "commands": as_text(src.get("commands")),
                "examples": as_text(src.get("examples")),
                "notes": notes,
            })
        out.append({"title_fa": f"زیرفصل {si}", "lessons": les_out})
    return {
        "order": 65,
        "title_fa": "فصل ۶۵: امنیت سایبری و هک اخلاقی (دفاعی) + بی‌سیم",
        "title_en": "Ch65 Security Ethical Hacking Wireless",
        "subchapters": out,
    }


def main():
    if not GZ.is_file():
        print("ERROR missing", GZ)
        sys.exit(1)
    data = json.loads(gzip.open(GZ, "rt", encoding="utf-8").read())
    packs = find_pack_files()
    print("packs", len(packs))
    sec, wireless = [], []
    routing_extra, vpn_extra, cmd_extra = [], [], []
    for p in packs:
        try:
            d = load_json(p)
        except Exception as e:
            print(" skip", p.name, e)
            continue
        name = str(p).replace("\\", "/").lower()
        lessons = normalize_pack(p, d)
        print(" ", p.name, "lessons", len(lessons))
        if not lessons:
            continue
        if "security_ethical" in name:
            sec.extend(lessons)
            continue
        if "wireless" in name and "vpn" not in name:
            wireless.extend(lessons)
            continue
        if d.get("commands") or "commands_encyclopedia" in name:
            cmd_extra.extend(lessons)
            continue
        n = merge_by_title(data, lessons)
        print("   title-merge", n)
        if "ospf" in name or "bgp" in name or "redistribution" in name or "routing_deep" in name:
            routing_extra.extend(lessons)
        if "vpn" in name or "ipsec" in name:
            vpn_extra.extend(lessons)

    if routing_extra:
        n = append_unmatched_as_extra(
            data, routing_extra, 66,
            "فصل ۶۶: مسیریابی عمیق OSPF/BGP/Redistribution",
            "Ch66 Routing Deep OSPF BGP",
        )
        print("ch66 routing", n)
    if vpn_extra:
        n = append_unmatched_as_extra(
            data, vpn_extra, 67,
            "فصل ۶۷: VPN سازمانی IPsec/SSL و عیب‌یابی",
            "Ch67 Enterprise VPN",
        )
        print("ch67 vpn", n)
    if cmd_extra:
        n = append_unmatched_as_extra(
            data, cmd_extra, 68,
            "فصل ۶۸: دانشنامه جامع دستورات",
            "Ch68 Commands Encyclopedia",
        )
        print("ch68 commands", n)

    data["chapters"] = [c for c in data["chapters"] if c.get("order") != 65]
    extra = list(sec)
    for w in wireless:
        w = dict(w)
        w["subchapter_order"] = 100 + int(w.get("subchapter_order") or 8)
        extra.append(w)
    if extra:
        data["chapters"].append(build_ch65(extra))
        print("ch65", sum(len(s["lessons"]) for s in data["chapters"][-1]["subchapters"]))

    data["chapters"].sort(key=lambda c: int(c.get("order") or 0))
    n = sum(len(s.get("lessons", [])) for c in data["chapters"] for s in c.get("subchapters", []))
    data["lesson_count"] = n
    data["version"] = int(data.get("version") or 7) + 1
    GZ.write_bytes(
        gzip.compress(json.dumps(data, ensure_ascii=False, separators=(",", ":")).encode("utf-8"), 9)
    )
    print("FINAL chapters", len(data["chapters"]), "lessons", n, "version", data["version"])
    for c in data["chapters"][-6:]:
        print(" ", c["order"], c["title_fa"][:52], sum(len(s["lessons"]) for s in c["subchapters"]))


if __name__ == "__main__":
    main()
