#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Validate progressive supplementary curriculum packs and their infographic links.

This is a structural/content-contract check only. It does not prove the technical
labs have run; packs explicitly keep lab_status=designed_not_executed until evidence
from the target platform is recorded.
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parents[1]
LEVELS = ["L0", "L1", "L2", "L3", "L4"]
WORD_FLOORS = {"L0": 600, "L1": 800, "L2": 1200, "L3": 1600, "L4": 2200}
EXPECTED_QUESTIONS = {"L0": 5, "L1": 8, "L2": 10, "L3": 12, "L4": 15}
PACKS = [
    ("tools/packs/network_transport/tcp_transport_engineering_ch07_pack.json",
     "tcp-transport-engineering-ch09", 9),
    ("tools/packs/network_transport/udp_quic_engineering_ch08_pack.json",
     "udp-quic-engineering-ch09", 9),
    ("tools/packs/mikrotik/routeros_foundations_ch19_pack.json",
     "routeros-foundations", 19),
    ("tools/packs/mikrotik/routeros_routing_firewall_ch20_pack.json",
     "routeros-routing-firewall", 20),
    ("tools/packs/mikrotik/routeros_qos_vpn_ha_ch21_pack.json",
     "routeros-qos-vpn-ha", 21),
    ("tools/packs/mikrotik/routeros_monitoring_logging_zabbix_ch22_pack.json",
     "mikrotik-monitoring-logging-zabbix-ch49", 49),
    ("tools/packs/mikrotik/routeros_zabbix_operations_ch23_pack.json",
     "mikrotik-zabbix-operations-ch49", 49),
    ("tools/packs/chapter14/advanced_routing_engineering_ch14_pack.json",
     "advanced-routing-engineering-ch14", 14),
    ("tools/packs/chapter15/mpls_vrf_l3vpn_ch15_pack.json",
     "mpls-vrf-l3vpn-ch15", 15),
    ("tools/packs/network_services/multicast_network_engineering_ch16_pack.json",
     "multicast-engineering-ch16", 16),
    ("tools/packs/data_center/evpn_vxlan_engineering_ch17_pack.json",
     "evpn-vxlan-engineering-ch17", 17),
    ("tools/packs/wan_design/sdn_sdwan_sase_ch18_pack.json",
     "sdn-sdwan-sase-ch18", 18),
    ("tools/packs/windows_server/active_directory_domain_engineering_ch28_pack.json",
     "active-directory-domain-engineering-ch28", 28),
]
errors: list[str] = []
checked_lessons = 0
checked_questions = 0


def fail(message: str) -> None:
    errors.append(message)


def read_json(relative: str) -> dict:
    path = ROOT / relative
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:
        fail(f"{relative}: unable to parse JSON: {exc}")
        return {}


catalog = read_json("tools/packs/pack_catalog.json")
catalog_entries = {entry.get("id"): entry for entry in catalog.get("packs", [])}

for relative, pack_id, chapter in PACKS:
    pack = read_json(relative)
    if not pack:
        continue
    if pack.get("project") != "NetworkAll":
        fail(f"{relative}: project should be NetworkAll")
    if pack.get("content_quality", {}).get("status") != "review_required":
        fail(f"{relative}: status must remain review_required until technical review")
    if pack.get("scope", {}).get("chapter_order") != chapter:
        fail(f"{relative}: scope.chapter_order should be {chapter}")
    lessons = pack.get("lessons")
    if not isinstance(lessons, list) or len(lessons) != 5:
        fail(f"{relative}: expected exactly five progressive L0–L4 lessons")
        continue
    if [lesson.get("level") for lesson in lessons] != LEVELS:
        fail(f"{relative}: lessons must be ordered L0, L1, L2, L3, L4")

    uids: list[str] = []
    all_question_ids: list[str] = []
    for lesson in lessons:
        checked_lessons += 1
        level = lesson.get("level")
        uid = lesson.get("uid", "")
        uids.append(uid)
        if not uid:
            fail(f"{relative}: lesson has an empty UID")
        if lesson.get("chapter_order") != chapter:
            fail(f"{relative}: {uid}: chapter_order mismatch")
        if not str(lesson.get("subchapter_title_fa") or "").strip():
            fail(f"{relative}: {uid}: missing descriptive subchapter_title_fa")
        if not str(lesson.get("full_content") or "").strip():
            fail(f"{relative}: {uid}: full_content is empty")
        words = len(re.findall(r"\S+", lesson.get("full_content", "")))
        if words < WORD_FLOORS.get(level, 10**9):
            fail(f"{relative}: {uid}: {words} words below floor {WORD_FLOORS.get(level)}")

        try:
            meta = json.loads(lesson.get("meta_json") or "{}")
        except Exception as exc:
            fail(f"{relative}: {uid}: meta_json is invalid: {exc}")
            meta = {}
        assessment = meta.get("assessment", {})
        questions = assessment.get("questions", [])
        answers = assessment.get("answer_key", [])
        expected = EXPECTED_QUESTIONS.get(level, 0)
        if len(questions) < expected:
            fail(f"{relative}: {uid}: expected at least {expected} questions, found {len(questions)}")
        if len(answers) != len(questions):
            fail(f"{relative}: {uid}: answer count differs from question count")
        question_ids = [q.get("id") for q in questions]
        answer_ids = [a.get("id") for a in answers]
        if question_ids != answer_ids:
            fail(f"{relative}: {uid}: answer-key IDs/order do not match questions")
        if any(not str(qid or "").strip() for qid in question_ids):
            fail(f"{relative}: {uid}: question with empty ID")
        if len(set(question_ids)) != len(question_ids):
            fail(f"{relative}: {uid}: duplicate question IDs within lesson")
        all_question_ids.extend(question_ids)
        checked_questions += len(questions)

        if meta.get("lab_status") != "designed_not_executed":
            fail(f"{relative}: {uid}: do not claim lab execution without evidence")
        if lesson.get("source_status") != "review_required":
            fail(f"{relative}: {uid}: source_status must remain review_required")
        sources = lesson.get("official_sources", [])
        if not sources:
            fail(f"{relative}: {uid}: no official/standards sources listed")
        for source in sources:
            parsed = urlparse(str(source.get("url") or ""))
            if parsed.scheme not in ("https", "http") or not parsed.netloc:
                fail(f"{relative}: {uid}: invalid source URL {source.get('url')!r}")

    if len(set(uids)) != len(uids):
        fail(f"{relative}: duplicate lesson UIDs")
    if len(set(all_question_ids)) != len(all_question_ids):
        fail(f"{relative}: question IDs are not unique within the pack")

    entry = catalog_entries.get(pack_id)
    if not entry:
        fail(f"{relative}: missing catalog entry {pack_id}")
    else:
        if entry.get("path") != relative:
            fail(f"{relative}: catalog path mismatch for {pack_id}")
        if chapter not in entry.get("chapter_targets", []):
            fail(f"{relative}: catalog chapter target mismatch for {pack_id}")
        if entry.get("quality_status") != "review_required":
            fail(f"{relative}: catalog status must remain review_required")

gallery_path = ROOT / "shared/infographics/index.html"
gallery = gallery_path.read_text(encoding="utf-8") if gallery_path.exists() else ""
if not gallery:
    fail("shared/infographics/index.html is missing or empty")
else:
    articles = len(re.findall(r"<article>", gallery))
    image_refs = re.findall(r'<img\s+src="([^"]+)"', gallery)
    if articles < 22:
        fail(f"infographic gallery: expected at least 22 articles, found {articles}")
    if len(image_refs) != articles:
        fail(f"infographic gallery: {articles} articles but {len(image_refs)} image references")
    if len(set(image_refs)) != len(image_refs):
        fail("infographic gallery: duplicate image references found")
    required_svgs = {
        "evpn_vxlan_fabric.svg",
        "sdwan_sase_path.svg",
        "dns_lookup.svg",
        "dhcp_dora.svg",
    }
    missing_refs = required_svgs - set(image_refs)
    if missing_refs:
        fail(f"infographic gallery: required images not linked: {sorted(missing_refs)}")
    for image_name in required_svgs:
        svg_path = ROOT / "shared/infographics" / image_name
        if not svg_path.exists():
            fail(f"infographic file missing: shared/infographics/{image_name}")
            continue
        svg = svg_path.read_text(encoding="utf-8")
        if not svg.lstrip().startswith("<svg ") or "</svg>" not in svg:
            fail(f"infographic SVG boundaries invalid: shared/infographics/{image_name}")

merge_script = (ROOT / "scripts/merge_content_packs_into_android.py").read_text(encoding="utf-8")
if '"subchapter_title_fa": src.get("subchapter_title_fa") or meta.get("subchapter_title_fa") or ""' not in merge_script:
    fail("merge script does not preserve subchapter_title_fa through normalization")
if 'and "/chapter15/" not in name' not in merge_script:
    fail("merge script can remap the chapter-scoped MPLS/VPN supplement away from chapter 15")

if errors:
    print("Curriculum pack validation FAILED")
    for error in errors:
        print(" -", error)
    sys.exit(1)

print("Curriculum pack validation PASSED")
print(f"Validated {checked_lessons} lessons across {len(PACKS)} packs.")
print(f"Validated {checked_questions} assessment questions with matching answer-key IDs.")
print("Depth floors, source links, catalog entries, subchapter titles and required SVG links are structurally valid.")
print("Reminder: this check is not a substitute for executing the technical labs on target platforms.")
