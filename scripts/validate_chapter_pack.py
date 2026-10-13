#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from __future__ import annotations
import gzip,json,sys
from pathlib import Path
import xml.etree.ElementTree as ET
ROOT=Path(__file__).resolve().parents[1]; PACK=ROOT/"tools/packs/ch01"; ASSET=ROOT/"android/app/src/main/assets/curriculum_index.json.gz"
def fail(msg):
 print("ERROR:",msg,file=sys.stderr); raise SystemExit(1)
def load(path):
 try: return json.loads(path.read_text(encoding="utf-8"))
 except Exception as exc: fail("invalid JSON "+str(path)+": "+str(exc))
def main():
 if not ASSET.is_file(): fail("merged curriculum asset missing")
 p=load(PACK/"ch01_pack.json"); e=load(PACK/"ch01_examples.json").get("examples",[]); s=load(PACK/"ch01_scenarios.json").get("scenarios",[])
 q=load(PACK/"ch01_questions.json").get("questions",[]); a=load(PACK/"ch01_answer_key.json").get("answer_key",[]); refs=load(PACK/"ch01_sources.json").get("sources",[]); m=load(PACK/"diagrams/manifest.json"); lessons=p.get("lessons")
 if p.get("package_schema_version")!=1 or p.get("chapter_order")!=1: fail("wrong pack schema/chapter")
 if not isinstance(lessons,list) or len(lessons)!=205: fail("expected 205 lessons")
 if len({x.get("uid") for x in lessons})!=205 or len({x.get("title_fa") for x in lessons})!=205: fail("duplicate lesson UID/title")
 if any(x.get("source_status")!="review_required" for x in lessons): fail("content must remain review_required")
 if min(len(str(x.get("full_content") or "")) for x in lessons)<1800: fail("lesson body too short")
 if (len(e),len(s),len(q),len(a))!=(60,60,60,60): fail("expected 60 sidecar records each")
 for label,rows in (("examples",e),("scenarios",s),("questions",q)):
  ids=[str(x.get("id") or "") for x in rows]
  if any(not x for x in ids) or len(ids)!=len(set(ids)): fail(label+" IDs invalid")
 if {x.get("id") for x in q}!={x.get("question_id") for x in a}: fail("question/answer IDs mismatch")
 if any(any(k in x for k in ("answer","correct","correct_option_id","correct_option_text")) for x in q): fail("answer leaked into questions")
 ids={x.get("uid") for x in lessons}
 if any(x.get("lesson_uid") not in ids for rows in (e,s,q) for x in rows): fail("sidecar UID reference invalid")
 if len(refs)<10 or any(not str(x.get("url") or "").startswith("https://") for x in refs): fail("need ten HTTPS references")
 ds=m.get("diagrams",[])
 if m.get("diagram_count")!=41 or len(ds)!=41 or len({x.get("diagram_id") for x in ds})!=41: fail("diagram manifest invalid")
 for d in ds:
  svg=PACK/"diagrams"/str(d.get("asset_source_file") or ""); mmd=PACK/"diagrams"/str(d.get("source_file") or "")
  if not svg.is_file() or not mmd.is_file(): fail("diagram files missing")
  try:
   if not ET.parse(svg).getroot().tag.endswith("svg"): fail("invalid SVG")
  except Exception as exc: fail("invalid SVG: "+str(exc))
  if not mmd.read_text(encoding="utf-8").strip().startswith("flowchart"): fail("invalid Mermaid")
 with gzip.open(ASSET,"rt",encoding="utf-8") as f: data=json.load(f)
 ch=next((c for c in data.get("chapters",[]) if int(c.get("order",-1))==1),None)
 if not ch: fail("curriculum misses chapter 1")
 by={}
 for sub in ch.get("subchapters",[]):
  for row in sub.get("lessons",[]): by.setdefault(row.get("title_fa"),[]).append(row)
 for src in lessons:
  matches=by.get(src.get("title_fa"),[])
  if len(matches)!=1: fail("title mapping not one-to-one: "+str(src.get("title_fa")))
  dst=matches[0]
  if dst.get("uid")!=src.get("uid"): fail("UID changed: "+str(src.get("title_fa")))
  for field in ("summary","full_content","commands","examples","notes","learning_objectives","search_keywords","search_query","source_status"):
   if dst.get(field)!=src.get(field): fail("merged field mismatch: "+field)
  dm=dst.get("meta") if isinstance(dst.get("meta"),dict) else {}; sm=src.get("meta") if isinstance(src.get("meta"),dict) else {}
  de=dm.get("chapter_enrichment") if isinstance(dm.get("chapter_enrichment"),dict) else {}; se=sm.get("chapter_enrichment") if isinstance(sm.get("chapter_enrichment"),dict) else {}
  if de.get("topic_slug")!=se.get("topic_slug"): fail("metadata not merged")
  assess=dm.get("assessment") if isinstance(dm.get("assessment"),dict) else {}
  if any(any(k in row for k in ("answer","correct","correct_option_id")) for row in assess.get("questions",[])): fail("answer leaked into app quiz")
 print(json.dumps({"ok":True,"chapter":1,"concepts":41,"lessons":205,"examples":60,"scenarios":60,"questions":60,"answer_keys":60,"diagrams":41,"sources":len(refs),"status":"review_required"},ensure_ascii=False))
if __name__=="__main__": main()
