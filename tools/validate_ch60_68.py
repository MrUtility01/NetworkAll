#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""اعتبارسنجی ساختاری محتوای فصل‌های ۶۰ تا ۶۸."""
import json, sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
PACK=ROOT/"tools/packs/ch60_68/chapter_60_68_deep_pack.json"
KEY=ROOT/"tools/packs/ch60_68/chapter_60_68_answer_key.json"
def main():
    d=json.loads(PACK.read_text(encoding="utf-8"))
    k=json.loads(KEY.read_text(encoding="utf-8"))
    lessons=d.get("lessons",[]); scenarios=d.get("scenarios",[]); questions=d.get("questions",[]); answers=k.get("answers",[])
    assert [x["chapter_order"] for x in d["chapters"]]==list(range(60,69)), "chapter range must be 60..68"
    assert len(lessons)>=250, f"expected >=250 lessons, got {len(lessons)}"
    uids=[x.get("uid") for x in lessons]
    assert all(uids) and len(uids)==len(set(uids)), "missing or duplicate lesson uid"
    assert all(60<=int(x.get("chapter_order",0))<=68 for x in lessons), "lesson outside target chapters"
    for x in lessons:
        for field in ("title_fa","summary","full_content","commands","examples"):
            assert str(x.get(field,"")).strip(), f"lesson {x.get('uid')} missing {field}"
        assert len(x["full_content"])>=900, f"lesson content too short: {x['uid']}"
        assert (x.get("meta") or {}).get("assessment"), f"assessment missing: {x['uid']}"
    assert len(scenarios)>=90, f"expected >=90 scenarios, got {len(scenarios)}"
    codes=[x.get("code") for x in scenarios]
    assert all(codes) and len(codes)==len(set(codes)), "scenario codes missing/duplicated"
    req=("title_fa","incident","symptoms","tasks","solution","verification")
    for s in scenarios:
        assert all(str(s.get(f,"")).strip() for f in req), f"scenario incomplete: {s.get('code')}"
    qids=[x.get("id") for x in questions]; aids=[x.get("id") for x in answers]
    assert len(qids)==len(set(qids)) and len(aids)==len(set(aids)), "duplicate quiz ids"
    assert set(qids)==set(aids), "question and answer key IDs differ"
    assert len(answers)==len(questions), "question/answer counts differ"
    # Runtime integration smoke test for Windows/Flask and Android export.
    sys.path.insert(0,str(ROOT/"server"))
    from core.extra_chapters import ensure_chapters_1_to_68
    from core.full_curriculum import get_full_curriculum
    curriculum=ensure_chapters_1_to_68(list(get_full_curriculum()))
    by={int(c[0]):c for c in curriculum}
    assert all(i in by for i in range(60,69)), "chapter missing from shared curriculum"
    for ch in d["chapters"]:
        order=ch["chapter_order"]
        titles={title for sub in by[order][3] for title,_ in sub[1]}
        expected=[x["title_fa"] for x in lessons if x["chapter_order"]==order]
        assert all(t in titles for t in expected), f"chapter {order} shared index missing lessons"
    from core.rich_content import build_rich_lesson
    sample=lessons[len(lessons)//2]
    got=build_rich_lesson(sample["title_fa"],sample["title_en"],sample["level"])
    assert got.get("full_content")==sample["full_content"], "shared content overlay mismatch"
    print(f"VALID chapters=9 lessons={len(lessons)} scenarios={len(scenarios)} questions={len(questions)} answer_keys={len(answers)}")
if __name__=="__main__": main()
