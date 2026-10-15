# 02 — CONTENT SCHEMA

Canonical schemas for all content types. Every agent must follow these exactly.

## Package envelope

```json
{
  "package_schema_version": 1,
  "project": "ENGINEER JOKAR / NetworkAll",
  "generated_on": "YYYY-MM-DD",
  "purpose": "...",
  "compatibility": {
    "preserve_existing_records": true,
    "preserve_existing_uids": true,
    "questions_and_answers_separate": true
  },
  "content_type": "lessons|scenarios|packet_journeys|diagrams|scripts|notes",
  "items": []
}
```

## Lesson

Required + recommended powerful fields:

- uid, chapter_order, subchapter_order, lesson_order, level (L0–L4)
- title_fa, title_en, topic, summary
- full_content (Markdown, 10 sections, ≥2500 chars for L3/L4)
- commands[], examples[], notes[], learning_objectives[]
- diagrams[] (mermaid + ascii)
- packet_journey (optional object)
- related_scenarios[]
- scripts[] (embedded safe code)
- meta.assessment.questions + answer_key
- source_status: "review_required"

## Scenario (Break/Fix)

```json
{
  "uid": "scenario:cat18:s042",
  "code": "CAT18-S042",
  "title_fa": "...", "title_en": "...",
  "difficulty": "مبتدی|متوسط|خبره",
  "level": "L3",
  "business_context": "...",
  "incident": "...",
  "symptoms": [], "tasks": [], "hints": [],
  "solution": "...", "verification": [],
  "skills_required": [], "estimated_hours": 3,
  "vendors": [], "related_chapters": [],
  "lab_environment": "...",
  "safety_note": "فقط محیط آزمایشگاهی مجاز",
  "scripts": [], "diagrams": [],
  "packet_journey_id": "..."
}
```

## Packet Journey

```json
{
  "uid": "pj:ch40:vmotion:001",
  "title_fa": "...", "title_en": "...",
  "related_chapters": [],
  "scenario": "...",
  "layers": [
    {"hop": 1, "device": "...", "action": "...", "protocol": "...", "interface": "...", "notes": "..."}
  ],
  "packet_structure_mermaid": "packet\n  0-15: \"...\"",
  "common_failures": [],
  "verification_commands": [],
  "diagrams": []
}
```

## Diagram

```json
{
  "uid": "diag:ch40:ha-cluster:001",
  "title_fa": "...",
  "type": "architecture|topology|sequence|packet|flow",
  "mermaid": "flowchart TB\n ...",
  "ascii": "...",
  "description_fa": "...",
  "nodes": [],
  "edges": [{"from": "...", "to": "...", "label": "..."}]
}
```

## Script (Python / automation)

```json
{
  "uid": "script:ch51:netmiko:042",
  "name": "bulk_vlan_audit.py",
  "language": "python",
  "level": "L3",
  "description_fa": "...",
  "requirements": ["netmiko"],
  "code": "#!/usr/bin/env python3\n...",
  "usage": "...",
  "related_chapters": [],
  "safety_note": "فقط روی تجهیزات Lab"
}
```

## Knowledge / Note / Learning Card

```json
{
  "uid": "note:ch40:ha:001",
  "type": "tip|gotcha|checklist|command_card|concept",
  "title_fa": "...",
  "body_fa": "...",
  "related_lessons": [],
  "tags": []
}
```
