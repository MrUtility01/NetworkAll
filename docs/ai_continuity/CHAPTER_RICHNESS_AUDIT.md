# CHAPTER RICHNESS AUDIT

## Canonical audit policy — all 68 chapters (registered 2026-10-15)

**This section is the active specification. It is not evidence that the audit or enrichment has been completed.**

### Global defaults (Chapters 1–67, unless an explicit per-chapter exception is approved)

| Setting | Required target |
|---|---|
| Default expertise level | **فوق‌حرفه‌ای** |
| Target text/structured-content size | **2 MiB per chapter** (measure UTF-8 source files/JSON structure; report compressed and uncompressed separately where relevant) |
| Media allowance | **Maximum 5 MiB per chapter**; report separately from text/structured content |
| Independent practical examples | **100 per chapter** |
| Independent troubleshooting scenarios | **150 per chapter** |
| Exam questions | **100 per chapter** |
| Answer key | Separate file/data structure; never leak answers into question prompts |
| Explanations | Include deep explanations, worked solutions, command output, safe labs, troubleshooting evidence and verification unless a chapter-specific exception says otherwise |

These are targets, not permission to pad files. Content size is an accounting target, **not** a proxy for scientific correctness, depth, uniqueness, or professional quality. Do not create repeated/template-only records to hit a number. Every example, scenario and question must be meaningfully distinct, chapter-specific, technically accurate, testable and traceable to its learning objective.

### Approved exception — Chapter 68

| Setting | Chapter 68 requirement |
|---|---|
| Actual title/topic | دانشنامه جامع دستورات (verify the exact canonical title in source data during the audit) |
| Expertise level | **خبره** |
| Target text/structured-content size | **5 MiB** |
| Media allowance | **Maximum 5 MiB**, measured and reported separately from text/structured content |
| Independent practical examples | **100** |
| Independent troubleshooting scenarios | **150** |
| Exam questions | **100** |
| Answer key | Separate file/data structure; never leak answers into question prompts |
| Explanations | **ندارد** — explanations are not a required quota for this exception |
| Notes | **ندارد** |
| Status | **Policy recorded; audit and validation pending** |

This exception overrides the global defaults only for Chapter 68. The 5 MiB content target and 5 MiB media ceiling are separate measurements and must not be combined. Neither size target is evidence of scientific quality, uniqueness, completeness, or successful Android/Windows integration.

### Required audit for every chapter, before enrichment is marked complete

1. Read the canonical source and report the **exact title** (do not rely on approximate titles in older audit notes).
2. Measure text/structured source size and media size separately. Record raw bytes and MiB; distinguish source-pack size, compressed Android asset size and Windows runtime/database size.
3. Count unique lessons, examples, scenarios and exam questions; verify the separate answer-key count and references.
4. Detect exact and near duplicates (stable IDs, normalized titles/text, repeated boilerplate, duplicated scenarios/questions).
5. Review scientific coverage, missing prerequisite concepts, operational examples, command output, lab reproducibility, failure evidence, mitigation and verification.
6. Verify schema, required fields, stable unique IDs, valid references and parseability.
7. Verify Android and Windows consume the same intended canonical content; record any platform-specific exclusions, export/merge differences and test evidence.
8. Report gaps and proposed changes first. Enrichment is not complete until content checks and both platform build/integration checks pass.

### Audit status

**Not yet fully audited or validated.** The older tables below are a preliminary evidence-based inventory. Their approximate titles/status labels are not authoritative, and pack size alone does not establish content quality. The next pass must produce a 68-row inventory with exact titles, per-platform byte sizes, record counts, duplicate counts, coverage gaps and verification status. Do not claim completion until that evidence exists.

---

**Date:** 2026-10-15  
**Method (preliminary; not a full 68-chapter validation):** File size analysis of packs + docs/DENSE_CH21_40.md + ch60 VALIDATION.md + APP_STATUS_FA.md + curriculum structure  
**Caveat:** This older snapshot is not a completed 68-chapter audit. True deep/mid/thin requires running `tools/audit_content.py` against a live encyclopedia.db. This audit is based on available evidence in the repository.

---

## Legend

| Status | Meaning |
|--------|--------|
| **DEEP** | Substantial dense content exists (hundreds of KB+ of real teaching material) |
| **PARTIAL** | Some real content or early packs exist, but far from complete |
| **THIN / SKELETON** | Mostly titles from full_curriculum.py, little or no rich body |
| **UNKNOWN** | No dedicated pack found; may still have seed text from rich_content.py |

---

## Chapters 1–20

| Ch | Title (approx) | Status | Evidence |
|----|----------------|--------|----------|
| 01–07 | Hardware, OS, Ethernet, IPv4/6 basics | UNKNOWN / likely mixed | Core curriculum + possible early rich_content |
| 08 | IPv4/IPv6/Subnetting | Likely better | Critical chapter |
| 09–12 | ARP/ICMP/TCP, DNS, DHCP, Cabling | UNKNOWN | — |
| 13 | Cisco Switching | **DEEP** | cisco_switching.json ~5.0 MB |
| 14 | Advanced Routing | **DEEP** | switching_routing pack ~7.5 MB + OSPF/BGP deep packs |
| 15–17 | MPLS, Multicast, EVPN | UNKNOWN | — |
| 18 | SDN / SD-WAN | UNKNOWN | — |
| 19–21 | MikroTik | **PARTIAL → DEEP** | DENSE_CH21_40 lists ch21 ~759 KB; MikroTik json present |
| 22–23 | Wireless / PtP | **PARTIAL** | wireless_security pack ~0.36 MB |
| 24 | FortiGate | **DEEP** | DENSE ~898 KB |
| 25 | pfSense / OPNsense | UNKNOWN | — |

## Chapters 21–40 (from DENSE_CH21_40.md)

Documented as having produced ~9.3 MB total dense content for the range, with explicit samples:

| Ch | Topic | Approx size | Status |
|----|-------|-------------|--------|
| 21 | MikroTik QoS VPN HA | ~759 KB | **DEEP** |
| 24 | FortiGate | ~898 KB | **DEEP** |
| 29 | Active Directory | ~726 KB | **DEEP** |
| 35 | PowerShell | ~520 KB | **DEEP** |
| 40 | VMware Hyper-V | ~485 KB (old) | **PARTIAL** (old dense exists, new canonical folder empty) |

Android asset claims **5185 complete lessons** in curriculum_index.json.gz — this is strong evidence that many chapters already have full bodies seeded, even if not all are “deep” by the 2000+ char audit rule.

## Chapters 41–60

| Ch | Title | Status | Evidence |
|----|-------|--------|----------|
| 41 | Proxmox Docker | **THIN / SKELETON** | No dedicated pack |
| 42 | Kubernetes | **THIN / SKELETON** | No dedicated pack |
| 43 | Cloud Networking | **THIN / SKELETON** | No dedicated pack |
| 44 | Cloud Security | **THIN / SKELETON** | No dedicated pack |
| 45 | Enterprise Storage | **THIN / SKELETON** | No dedicated pack |
| 46 | Backup / DR | **THIN / SKELETON** | No dedicated pack |
| 47 | Data Center | **THIN / SKELETON** | No dedicated pack |
| 48 | HA & Load Balancing | **THIN / SKELETON** | No dedicated pack |
| 49 | Monitoring | **THIN / SKELETON** | No dedicated pack |
| 50 | SIEM / ELK | **THIN / SKELETON** | No dedicated pack |
| 51 | Automation & AI | **PARTIAL** | automation_python pack ~2.9 MB (good base) |
| 52 | Database Admin | **THIN / SKELETON** | No dedicated pack |
| 53 | DB Security | **THIN / SKELETON** | No dedicated pack |
| 54 | VoIP | **THIN / SKELETON** | No dedicated pack |
| 55 | CCTV / IoT | **THIN / SKELETON** | No dedicated pack |
| 56 | Zero Trust / ITIL | **THIN / SKELETON** | No dedicated pack |
| 57 | Network Security | **PARTIAL** | security_ethical_hacking pack ~1.3 MB |
| 58 | Endpoint / AppSec | **THIN / SKELETON** | — |
| 59 | SOC / IR | **THIN / SKELETON** | — |
| 60 | Troubleshooting Labs | **PARTIAL** | ch60 pack exists (8 lessons + 10 scenarios + Q&A). VALIDATION says ~230 lessons still missing |

## Extra / Extension chapters

| Ch / Pack | Status | Size / Notes |
|-----------|--------|--------------|
| 64 Git | **DEEP** | Git_Chapter_64_Full.md ~2.1 MB |
| 66/68 Routing deep | **DEEP** | chapter_68_cisco_routing ~9.7 MB |
| 67 VPN Enterprise | **DEEP** | ~5.2 MB deep pack |
| Windows Server pack | **DEEP** | ~7.2 MB |
| Commands encyclopedia | **DEEP** | cisco_switching ~5 MB + mikrotik |

---

## Summary ranking (priority for enrichment)

### Already strong (protect & only improve)
- 13, 14, 21, 24, 29, 35, 64, 66/68, 67, Windows Server, Commands

### Partial — high value to finish
- **40** (VMware) — old dense exists, new structure empty → finish properly
- **51** (Automation) — good base pack, needs expansion + AI parts
- **60** (Labs) — only stage 1 done, needs massive expansion
- 57 (Security) — base pack exists

### Thin / Skeleton — need full production (especially 41–50, 52–56, 58–59)
These currently have almost no dedicated rich packs under the new architecture.

---

## Important caveats

1. `curriculum_index.json.gz` claims 5185 complete lessons → many chapters already have *some* body text from earlier seed/rich_content runs.
2. True deep/mid/thin counts require running:
   ```bash
   python tools/audit_content.py --db server/data/encyclopedia.db
   ```
3. Large packs (5–10 MB) are strong evidence of deep content for their topics, but may not map 1:1 to every subchapter.
4. Chapter 40 old dense (~485 KB) is valuable but should be migrated/expanded into the new `tools/packs/ch40_vmware_hyperv/` structure.


## Per-chapter target selection form

The user requested a one-time, chapter-by-chapter choice of expertise level, text/structured-content target, media ceiling, independent examples, independent scenarios, exam questions, and whether explanations are required. The complete 68-row prefilled selection table is maintained at [CHAPTER_TARGET_SELECTION.md](CHAPTER_TARGET_SELECTION.md).

**Selection status: awaiting user choices.** The global defaults remain in force for Chapters 1–67 until the user specifies exceptions. Chapter 68 retains its explicit exception: خبره; 5 MiB text/structured target; 5 MiB media ceiling; 100 examples; 150 scenarios; 100 exam questions; explanations not required. This is a policy entry only, not an audit or completion claim.
