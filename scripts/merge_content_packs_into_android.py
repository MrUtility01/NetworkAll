#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""ادغام بسته‌های tools؛ فصل ۶۴=Git؛ امنیت→۶۵؛ OSPF/VPN→۶۶/۶۷؛ دستورات→۶۸."""
from __future__ import annotations
import gzip, json, sys, re, hashlib
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
    files += list(ROOT.glob("tools/packs/git_chapter64/Git_Chapter_64_Full.md"))
    files += list(ROOT.glob("tools/engineer_jokar_*/*pack*.json"))
    files += list(ROOT.glob("tools/engineer_jokar_*/*curriculum*.json"))
    files += list(ROOT.glob("tools/ENGINEER_JOKAR_*.json"))
    uniq, seen = [], set()
    for f in files:
        name = f.name.lower()
        if (name.endswith(".md") and f.name != "Git_Chapter_64_Full.md") or name in ("readme.md", "readme_fa.md", "manifest.json"):
            continue
        rel = f.relative_to(ROOT).as_posix()
        quarantined = {
            "tools/ENGINEER_JOKAR_OSPF_BGP_Redistribution_deep_v1.json":
                "wrong-topic duplicate hardware blueprint; not OSPF/BGP content",
            "tools/ENGINEER_JOKAR_VPN_Enterprise_IPsec_SSL_Troubleshooting_deep_v1.json":
                "wrong-topic duplicate hardware blueprint; not VPN content",
            "tools/engineer_jokar_security_ethical_hacking/security_ethical_hacking_pack.json":
                "template-heavy security lessons pending deep rewrite",
        }
        if rel in quarantined:
            print(" quarantine source-only:", rel, "—", quarantined[rel])
            continue
        if rel == "tools/commands_encyclopedia/mikrotik.json" and (ROOT / "tools/packs/commands_encyclopedia/mikrotik.json").exists():
            print(" skip legacy duplicate pack:", rel)
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


def commands_to_lessons(data: dict, source_path: Path | None = None) -> list:
    ch = int(data.get("chapter_order") or 68)
    source_name = source_path.relative_to(ROOT).with_suffix("").as_posix() if source_path else "legacy"
    source_slug = re.sub(r"[^a-z0-9]+", "-", source_name.lower()).strip("-")[:42].rstrip("-") or "pack"
    out = []
    sub_map = {
        "basics": 1, "interface": 2, "vlan": 3, "trunk": 3, "stp": 4, "spanning-tree": 4,
        "etherchannel": 5, "port-security": 6, "mac": 7, "cdp": 8, "lldp": 8,
        "troubleshoot": 9, "switching": 2, "general": 10,
    }
    for i, c in enumerate(data.get("commands") or [], 1):
        if not isinstance(c, dict):
            continue
        cmd = c.get("command") or c.get("title_en") or ""
        level = c.get("level") or "L1"
        title_fa = c.get("title_fa") or cmd
        if not str(title_fa).startswith("[L"):
            title_fa = f"[{level}] {title_fa}"
        sub = (c.get("subcategory") or c.get("category") or "general").strip().lower()
        sub_order = sub_map.get(sub, 10)
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
        notes = ""
        flash = c.get("flashcards")
        assess = c.get("assessment")
        meta = {}
        if assess:
            meta["assessment"] = assess
            notes += "\n\n<!-- EJ_ASSESSMENT\n" + json.dumps(assess, ensure_ascii=False) + "\n-->\n"
        if flash:
            meta["flashcards"] = flash
            notes += "\n\n<!-- EJ_FLASHCARDS\n" + json.dumps(flash, ensure_ascii=False) + "\n-->\n"

        lesson_uid = f"lesson:ch{ch:02d}:cmd:{source_slug}:{i:04d}"
        out.append({
            "uid": lesson_uid,
            "chapter_order": ch,
            "subchapter_order": sub_order,
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


def _ascii_digits(value: str) -> str:
    trans = str.maketrans("۰۱۲۳۴۵۶۷۸۹٠١٢٣٤٥٦٧٨٩", "01234567890123456789")
    return value.translate(trans)


def git_markdown_to_lessons(path: Path) -> list:
    """Parse the chapter-64 Markdown book into stable lesson records."""
    text = path.read_text(encoding="utf-8-sig")
    matches = list(re.finditer(r"(?m)^###\s+(.+?\s+[—-]\s*L[0-4])\s*$", text))
    if not matches:
        return []
    lessons = []
    current_sub = 1
    sub_titles = {}
    for line in text[:matches[0].start()].splitlines():
        m = re.match(r"^##\s+۶۴[.．](\d+)\s+(.+)$", line.strip())
        if m:
            current_sub = int(_ascii_digits(m.group(1)))
            sub_titles[current_sub] = m.group(2).strip()
    fence = chr(96) * 3
    for idx, match in enumerate(matches):
        heading = match.group(1).strip()
        level_match = re.search(r"[—-]\s*L([0-4])\s*$", heading)
        if not level_match:
            continue
        level = "L" + level_match.group(1)
        bare_title = re.sub(r"\s*[—-]\s*L[0-4]\s*$", "", heading).strip()
        body_start = match.start()
        body_end = matches[idx + 1].start() if idx + 1 < len(matches) else len(text)
        body = text[body_start:body_end].strip()
        preceding = text[:body_start].splitlines()
        for line in reversed(preceding):
            m = re.match(r"^##\s+۶۴[.．](\d+)\s+(.+)$", line.strip())
            if m:
                current_sub = int(_ascii_digits(m.group(1)))
                sub_titles[current_sub] = m.group(2).strip()
                break
        summary_match = re.search(r"(?m)^\*\*خلاصه(?: فصل)?:?\*\*\s*(.+)$", body)
        summary = summary_match.group(1).strip() if summary_match else body[:240].replace("\n", " ").strip()
        scenario_match = re.search(r"(?ms)^##\s+(?:4|۴)[.、 ]*سناریوی عملی.*?(?=^##\s+(?:5|۵)[.、 ]|\Z)", body)
        examples = scenario_match.group(0).strip() if scenario_match else ""
        code_blocks = re.findall(re.escape(fence) + r"[^\n]*\n(.*?)" + re.escape(fence), body, flags=re.S)
        commands = "\n".join(code_blocks).strip()
        uid_hash = hashlib.sha1(f"{current_sub}|{bare_title}|{level}".encode("utf-8")).hexdigest()[:12]
        uid = f"lesson:ch64:git:s{current_sub:02d}:{uid_hash}"
        lessons.append({
            "uid": uid,
            "chapter_order": 64,
            "subchapter_order": current_sub,
            "lesson_order": idx + 1,
            "level": level,
            "title_fa": f"[{level}] {bare_title}",
            "title_en": "",
            "summary": summary[:500],
            "full_content": body,
            "commands": "",
            "examples": examples,
            "notes": f"source=tools/packs/git_chapter64/Git_Chapter_64_Full.md; subchapter={sub_titles.get(current_sub, '')}; status=review_required",
            "source_status": "review_required",
        })
    return lessons


def normalize_pack(path: Path, data: dict):
    if path.suffix.lower() == ".md":
        return git_markdown_to_lessons(path)
    if data.get("commands"):
        return commands_to_lessons(data, path)
    if data.get("lessons"):
        return data.get("lessons") or []
    name = path.name.upper()
    if "curriculum" in data:
        if any(k in name for k in ("OSPF", "BGP", "REDIS")):
            return blueprint_to_lessons(data, ["OSPF", "BGP", "Redistribution", "Adjacency", "eBGP", "iBGP", "SPF"], 14)
        if "VPN" in name or "IPSEC" in name:
            return blueprint_to_lessons(data, ["IPsec", "IKEv", "SSL VPN", "Phase", "Tunnel", "VPN"], 57)
        return blueprint_to_lessons(data, [], 1)
    return []


def apply_fields(les, src):
    for k in ("summary", "full_content", "commands", "examples", "notes"):
        if src.get(k):
            les[k] = as_text(src.get(k)) if k != "full_content" else (src.get(k) or "")


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


def prune_placeholder_lessons(data):
    """Remove only obvious generated placeholders from the active curriculum."""
    marker = re.compile(r"seed.{0,40}ایجاد|place to develop|placeholder|coming soon|TODO|محل توسعه محتوای تأییدشده", re.I)
    removed = 0
    for chapter in data.get("chapters", []):
        for sub in chapter.get("subchapters", []):
            kept = []
            for lesson in sub.get("lessons", []):
                content = "\n".join(str(lesson.get(k) or "") for k in ("title_fa", "summary", "full_content", "examples", "notes"))
                if len(str(lesson.get("full_content") or "")) < 3500 and marker.search(content):
                    removed += 1
                    continue
                kept.append(lesson)
            sub["lessons"] = kept
        chapter["subchapters"] = [s for s in chapter.get("subchapters", []) if s.get("lessons")]
    return removed


def prune_legacy_command_uids(data):
    """Drop only command IDs produced by the old colliding index-only UID scheme."""
    removed = 0
    for chapter in data.get("chapters", []):
        if int(chapter.get("order") or 0) != 68:
            continue
        for sub in chapter.get("subchapters", []):
            before = sub.get("lessons", [])
            sub["lessons"] = [x for x in before if not re.fullmatch(r"lesson:ch68:cmd:\d{4}", str(x.get("uid") or ""))]
            removed += len(before) - len(sub["lessons"])
        chapter["subchapters"] = [s for s in chapter.get("subchapters", []) if s.get("lessons")]
    return removed


def prune_legacy_security_uids(data):
    """Remove old chapter-64 security pack IDs misplaced under chapter 65."""
    removed = 0
    for chapter in data.get("chapters", []):
        if int(chapter.get("order") or 0) != 65:
            continue
        for sub in chapter.get("subchapters", []):
            before = sub.get("lessons", [])
            sub["lessons"] = [
                x for x in before
                if not str(x.get("uid") or "").startswith("lesson:ch64:lv")
                and not str(x.get("uid") or "").startswith("lesson:ch64:wireless:")
            ]
            removed += len(before) - len(sub["lessons"])
        chapter["subchapters"] = [s for s in chapter.get("subchapters", []) if s.get("lessons")]
    return removed


def remap_lessons_to_chapter(lessons, target_chapter):
    out = []
    for source in lessons:
        item = dict(source)
        item["chapter_order"] = target_chapter
        uid = str(item.get("uid") or "")
        if uid.startswith("lesson:ch"):
            uid = re.sub(r"^lesson:ch\d{2}:", f"lesson:ch{target_chapter:02d}:", uid)
        item["uid"] = uid
        if not item.get("subchapter_order"):
            m = re.search(r":lv(\d+):", uid)
            if m:
                item["subchapter_order"] = int(m.group(1))
        out.append(item)
    return out


def append_unmatched_as_extra(data, lessons, order, title_fa, title_en):
    """Merge pack lessons into a chapter without ever deleting existing chapter content.

    Older versions removed the whole chapter before appending pack lessons. That made
    a pack containing only *new/unmatched* lessons capable of erasing the existing
    curriculum chapter. Merge by stable UID and preserve all existing subchapters.
    """
    if not lessons:
        return 0

    chapter = next((c for c in data["chapters"] if c.get("order") == order), None)
    if chapter is None:
        chapter = {
            "order": order,
            "title_fa": title_fa,
            "title_en": title_en,
            "subchapters": [],
        }
        data["chapters"].append(chapter)
    else:
        # Keep established chapter metadata; only fill missing values.
        chapter.setdefault("title_fa", title_fa)
        chapter.setdefault("title_en", title_en)
        chapter.setdefault("subchapters", [])

    subs = defaultdict(list)
    for src in lessons:
        subs[src.get("subchapter_order") or 1].append(src)

    existing_uids = {
        str(les.get("uid"))
        for sub in chapter.get("subchapters", [])
        for les in (sub.get("lessons") or [])
        if les.get("uid")
    }
    def identity(lesson):
        title = str(lesson.get("title_fa") or "").strip().casefold()
        return title
    existing_identities = {
        identity(les)
        for sub in chapter.get("subchapters", [])
        for les in (sub.get("lessons") or [])
    }
    added = 0
    for si in sorted(subs):
        incoming = []
        for src in sorted(subs[si], key=lambda x: (x.get("lesson_order") or 0)):
            uid = src.get("uid") or f"lesson:ch{order:02d}:s{int(si):03d}:l{len(incoming):04d}"
            identity_key = identity(src)
            if uid in existing_uids or identity_key in existing_identities:
                continue
            notes = as_text(src.get("notes"))
            ass = (src.get("meta") or {}).get("assessment")
            if ass and "EJ_ASSESSMENT" not in notes:
                notes += "\n\n<!-- EJ_ASSESSMENT\n" + json.dumps(ass, ensure_ascii=False) + "\n-->\n"
            incoming.append({
                "uid": uid,
                "title_fa": src.get("title_fa") or "",
                "title_en": src.get("title_en") or "",
                "level": src.get("level") or "L0",
                "summary": src.get("summary") or "",
                "full_content": src.get("full_content") or "",
                "commands": as_text(src.get("commands")),
                "examples": as_text(src.get("examples")),
                "notes": notes,
                "source_status": src.get("source_status") or "review_required",
            })
            existing_uids.add(uid)
            existing_identities.add(identity_key)
            added += 1

        if not incoming:
            continue
        target_sub = next(
            (sub for sub in chapter["subchapters"]
             if sub.get("order") == si or sub.get("order_index") == si
             or sub.get("title_fa") == f"زیرفصل {si}"),
            None,
        )
        if target_sub is None:
            target_sub = {"order": si, "title_fa": f"زیرفصل {si}", "lessons": []}
            chapter["subchapters"].append(target_sub)
        target_sub.setdefault("lessons", []).extend(incoming)

    chapter["subchapters"].sort(
        key=lambda sub: int(sub.get("order", sub.get("order_index", 10**9)) or 10**9)
    )
    return added


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
    pruned_stubs = prune_placeholder_lessons(data)
    pruned_cmd_uids = prune_legacy_command_uids(data)
    pruned_sec_uids = prune_legacy_security_uids(data)
    print("pruned obvious placeholders", pruned_stubs, "legacy command IDs", pruned_cmd_uids, "misplaced security IDs", pruned_sec_uids)

    packs = find_pack_files()
    print("packs", len(packs))
    wireless = []
    routing_extra, vpn_extra, cmd_extra, git_extra = [], [], [], []
    general_extra = defaultdict(list)
    for p in packs:
        try:
            d = {} if p.suffix.lower() == ".md" else load_json(p)
            lessons = normalize_pack(p, d)
        except Exception as e:
            print(" skip", p.name, e)
            continue
        name = str(p).replace("\\", "/").lower()
        print(" ", p.name, "lessons", len(lessons))
        if not lessons:
            continue

        # This pack is a generated template, not a chapter-ready security textbook.
        # Keep the source file for future rewriting, but do not publish its repeated
        # generic lessons into the active Android curriculum.
        if "security_ethical" in name:
            print("   quarantine: template-heavy pack remains source-only pending deep rewrite")
            continue

        if "wireless" in name and "vpn" not in name:
            for source in lessons:
                item = dict(source)
                item["chapter_order"] = 65
                item["uid"] = re.sub(r"^lesson:ch64:", "lesson:ch65:", str(item.get("uid") or ""))
                m = re.search(r":lv(\\d+):", str(item.get("uid") or ""))
                sub = int(item.get("subchapter_order") or (m.group(1) if m else 1))
                item["subchapter_order"] = 100 + sub
                wireless.append(item)
            continue

        if "git_chapter64" in name:
            n = merge_by_title(data, lessons)
            print("   git title-merge", n)
            git_extra.extend(lessons)
            continue

        if d.get("commands") or "commands_encyclopedia" in name:
            n = merge_by_title(data, lessons)
            print("   command title-merge", n)
            cmd_extra.extend(lessons)
            continue

        n = merge_by_title(data, lessons)
        print("   title-merge", n)
        if "ospf" in name or "bgp" in name or "redistribution" in name or "routing_deep" in name:
            routing_extra.extend(remap_lessons_to_chapter(lessons, 66))
            continue
        if "vpn" in name or "ipsec" in name:
            vpn_extra.extend(remap_lessons_to_chapter(lessons, 67))
            continue

        for source in lessons:
            try:
                chapter_order = int(source.get("chapter_order") or 1)
            except (TypeError, ValueError):
                chapter_order = 1
            if not source.get("subchapter_order"):
                m = re.search(r":lv(\d+):", str(source.get("uid") or ""))
                if m:
                    source["subchapter_order"] = int(m.group(1))
            general_extra[chapter_order].append(source)

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
    if git_extra:
        n = append_unmatched_as_extra(
            data, git_extra, 64,
            "فصل ۶۴: Git و GitHub از صفر تا مهندسی حرفه‌ای",
            "Ch64 Git and GitHub",
        )
        print("ch64 Git", n)

    if wireless:
        n_added = append_unmatched_as_extra(
            data, wireless, 65,
            "فصل ۶۵: امنیت بی‌سیم و دفاع شبکه",
            "Ch65 Wireless Security",
        )
        ch65 = next((ch for ch in data["chapters"] if ch.get("order") == 65), {})
        total65 = sum(len(sub.get("lessons", [])) for sub in ch65.get("subchapters", []))
        print("ch65 wireless added", n_added, "total", total65)

    for chapter_order in sorted(general_extra):
        chapter = next((ch for ch in data["chapters"] if int(ch.get("order") or 0) == chapter_order), None)
        title_fa = chapter.get("title_fa") if chapter else f"فصل {chapter_order}: محتوای تکمیلی"
        title_en = chapter.get("title_en") if chapter else f"Chapter {chapter_order} supplementary content"
        added = append_unmatched_as_extra(data, general_extra[chapter_order], chapter_order, title_fa, title_en)
        if added:
            print("chapter", chapter_order, "supplementary lessons added", added)

    data["chapters"].sort(key=lambda ch: int(ch.get("order") or 0))
    total = sum(len(sub.get("lessons", [])) for ch in data["chapters"] for sub in ch.get("subchapters", []))
    data["lesson_count"] = total
    data["version"] = int(data.get("version") or 7) + 1
    GZ.write_bytes(
        gzip.compress(json.dumps(data, ensure_ascii=False, separators=(",", ":")).encode("utf-8"), 9)
    )
    print("FINAL chapters", len(data["chapters"]), "lessons", total, "version", data["version"])
    for ch in data["chapters"][-8:]:
        print(" ", ch["order"], ch["title_fa"][:52], sum(len(sub["lessons"]) for sub in ch["subchapters"]))




if __name__ == "__main__":
    main()
