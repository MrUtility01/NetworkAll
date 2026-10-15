#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Move chapter folders to numeric paths and split lesson fields into dedicated content-type files."""
from __future__ import annotations
import copy, hashlib, json, re, shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CHAPTERS = ROOT / "tools" / "chapters"
AUTHORING = ROOT / "tools" / "authoring"

CATEGORY_FIELDS = {
    "questions": ("questions", "question", "quiz", "quizzes", "exam", "exams", "tests",
                  "test_questions", "practice_questions", "assessment", "assessments", "exercises", "exercise"),
    "answers": ("answer_key", "answer_keys", "answers", "correct_answers", "solutions", "solution"),
    "examples": ("examples", "example", "worked_examples"),
    "commands": ("commands", "command", "cli_commands", "command_examples"),
    "labs": ("lab", "labs", "lab_exercises", "scenario", "scenarios"),
}
CATEGORY_FILES = {
    "questions": "questions.json", "answers": "answer_key.json",
    "examples": "examples.json", "commands": "commands.json", "labs": "labs.json",
}
READMES = {
    "lessons": "# درس‌ها و متن آموزشی\n\n- lessons.json: متن پایهٔ افزوده و اطلاعات هر درس.\n- base_curriculum.json: ساختار و درس‌های پایهٔ این فصل.\n",
    "questions": "# پرسش‌ها و آزمون‌ها\n\n- questions.json: پرسش‌ها و تمرین‌های استخراج‌شده با UID درس.\n- sources/: آزمون‌ها و فایل‌های پرسش‌نامهٔ اولیه.\n",
    "answers": "# پاسخ‌نامه‌ها\n\n- answer_key.json: پاسخ‌ها و راه‌حل‌های ساختاریافته با UID درس.\n- sources/: پاسخ‌نامه‌ها و کلیدهای اصلی آزمون.\n",
    "examples": "# مثال‌ها\n\n- examples.json: مثال‌ها و نمونه‌های عملی هر درس.\n- sources/: فایل‌های نمونهٔ قدیمی.\n",
    "commands": "# دستورات و CLI\n\n- commands.json: فرمان‌ها و نمونه‌فرمان‌های درس‌ها.\n- sources/: بسته‌ها و مستندات اولیهٔ دستورات.\n",
    "labs": "# لابراتوارها و سناریوها\n\n- labs.json: لاب‌ها و سناریوهای پیوندخورده به درس.\n- sources/: فایل‌های سناریو و لاب اولیه.\n",
    "android": "# یکپارچه‌سازی اندروید\n\nفقط تنظیمات و منابع ویژهٔ این فصل را اینجا نگه دارید. کد مشترک اندروید در مسیر اصلی android/ است و در فصل‌ها کپی نمی‌شود.\n",
    "windows": "# یکپارچه‌سازی ویندوز\n\nفقط تنظیمات و منابع ویژهٔ این فصل را اینجا نگه دارید. کد مشترک سرور در server/ و windows/ است و در فصل‌ها کپی نمی‌شود.\n",
    "build": "# بستهٔ تولیدشده\n\nchapter.json خروجی کامپایل‌شده برای سازگاری برنامه‌هاست. آن را مستقیم ویرایش نکنید؛ از lessons/, questions/, answers/, examples/, commands/ و labs/ استفاده کنید.\n",
}

def read_json(path: Path):
    try: return json.loads(path.read_text(encoding="utf-8"))
    except Exception: return None

def write_json(path: Path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

def digest(path: Path):
    h=hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda:f.read(1024*1024),b""): h.update(block)
    return h.hexdigest()

def move(src: Path, dst: Path):
    if not src.exists(): return
    dst.parent.mkdir(parents=True, exist_ok=True)
    if dst.exists():
        if src.is_file() and dst.is_file() and digest(src)==digest(dst):
            src.unlink(); return
        if src.is_dir() and dst.is_dir():
            for child in list(src.iterdir()): move(child, dst/child.name)
            try: src.rmdir()
            except OSError: pass
            return
        stem,suffix=dst.stem,dst.suffix
        base=dst; i=2
        while dst.exists():
            dst=base.with_name(f"{stem}__from_{src.parent.name}_{i}{suffix}"); i+=1
    shutil.move(str(src),str(dst))

def move_contents(src: Path, dst: Path):
    if not src.is_dir(): return
    for child in list(src.iterdir()): move(child,dst/child.name)
    try: src.rmdir()
    except OSError: pass

def title_key(value):
    return re.sub(r"\s+"," ",str(value or "").strip()).casefold()

def merge_value(old,new):
    if old in (None,"",[],{}): return copy.deepcopy(new)
    if new in (None,"",[],{}) or old==new: return copy.deepcopy(old)
    if isinstance(old,str) and isinstance(new,str):
        if new in old: return old
        if old in new: return new
        return old+"\n\n---\n\n"+new
    if isinstance(old,list) and isinstance(new,list):
        out=copy.deepcopy(old); seen={json.dumps(x,ensure_ascii=False,sort_keys=True,default=str) for x in out}
        for item in new:
            key=json.dumps(item,ensure_ascii=False,sort_keys=True,default=str)
            if key not in seen: out.append(copy.deepcopy(item)); seen.add(key)
        return out
    if isinstance(old,dict) and isinstance(new,dict):
        out=copy.deepcopy(old)
        for key,value in new.items():
            out[key]=merge_value(out[key],value) if key in out else copy.deepcopy(value)
        return out
    return copy.deepcopy(old)

def merge_rows(current, old_rows):
    rows=[copy.deepcopy(x) for x in current if isinstance(x,dict)]
    by_uid={str(x.get("uid")):x for x in rows if x.get("uid")}
    by_title={title_key(x.get("title_fa") or x.get("title_en")):x for x in rows}
    for old in old_rows:
        if not isinstance(old,dict): continue
        uid=str(old.get("uid") or "")
        existing=by_uid.get(uid) if uid else None
        existing=existing or by_title.get(title_key(old.get("title_fa") or old.get("title_en")))
        if existing is None:
            clone=copy.deepcopy(old)
            if uid and uid in by_uid: clone["uid"]=f"{uid}:legacy-preserved"
            rows.append(clone)
            if clone.get("uid"): by_uid[str(clone["uid"])]=clone
            by_title[title_key(clone.get("title_fa") or clone.get("title_en"))]=clone
        else:
            if uid and str(existing.get("uid") or "") and uid != str(existing.get("uid")):
                meta=existing.get("meta") if isinstance(existing.get("meta"),dict) else {}
                source_uids=meta.get("source_uids") if isinstance(meta.get("source_uids"),list) else []
                if uid not in source_uids: source_uids.append(uid)
                meta["source_uids"]=source_uids
                existing["meta"]=meta
            for key,value in old.items():
                if key!="uid":
                    existing[key]=merge_value(existing[key],value) if key in existing else copy.deepcopy(value)
    used=set()
    for idx,row in enumerate(rows,1):
        uid=str(row.get("uid") or f"lesson:preserved:{idx:05d}")
        new=uid; suffix=2
        while new in used: new=f"{uid}:preserved:{suffix}"; suffix+=1
        row["uid"]=new; used.add(new)
    return rows

def classify_archive(chapter: Path):
    archive=chapter/"source_archive"
    if not archive.is_dir(): return
    for path in sorted(list(archive.rglob("*"))):
        if not path.is_file(): continue
        name=path.name.casefold(); suffix=path.suffix.casefold()
        if any(x in name for x in ("answer_key","answer-key","solutions","solution_key")):
            dst=chapter/"answers"/"sources"/path.relative_to(archive)
        elif any(x in name for x in ("question","quiz","exam","test_bank","test_questions")):
            dst=chapter/"questions"/"sources"/path.relative_to(archive)
        elif any(x in name for x in ("scenario","lab_","_lab","troubleshoot_lab")):
            dst=chapter/"labs"/"sources"/path.relative_to(archive)
        elif any(x in name for x in ("command","cli_","fortigate_cli","cisco_routing_1600","powershell","mikrotik")):
            dst=chapter/"commands"/"sources"/path.relative_to(archive)
        elif "example" in name or "worked_example" in name:
            dst=chapter/"examples"/"sources"/path.relative_to(archive)
        elif suffix in (".png",".jpg",".jpeg",".webp",".svg",".mmd",".drawio"):
            dst=chapter/"media"/"sources"/path.relative_to(archive)
        else: continue
        move(path,dst)

def preserve_root_files(chapter: Path):
    lessons=chapter/"lessons"; lessons.mkdir(parents=True,exist_ok=True)
    old=chapter/"base_curriculum.json"; target=lessons/"base_curriculum.json"
    if old.is_file():
        if not target.exists(): move(old,target)
        elif digest(old)==digest(target): old.unlink()
        else: move(old,chapter/"source_archive"/"legacy_baselines"/"base_curriculum.json")
    book=chapter/"Git_Chapter_64_Full.md"
    if book.is_file(): move(book,lessons/"sources"/book.name)
    validation=chapter/"VALIDATION.md"
    if validation.is_file(): move(validation,chapter/"authoring"/"validation"/validation.name)
    for path in list(chapter.iterdir()):
        if not path.is_file() or path.name in ("README_FA.md","manifest.json","chapter.json"): continue
        if path.suffix.casefold() in (".png",".jpg",".jpeg",".webp",".svg",".mmd",".drawio"):
            move(path,chapter/"media"/"sources"/path.name)
        elif path.suffix.casefold()==".md":
            name=path.name.casefold()
            if any(k in name for k in ("question","quiz","exam","test_bank")):
                move(path,chapter/"questions"/"sources"/path.name)
            elif any(k in name for k in ("answer_key","answer-key","solution")):
                move(path,chapter/"answers"/"sources"/path.name)
            elif any(k in name for k in ("command","powershell","cli","cisco","mikrotik")):
                move(path,chapter/"commands"/"sources"/path.name)
            elif any(k in name for k in ("example","worked_example")):
                move(path,chapter/"examples"/"sources"/path.name)
            elif any(k in name for k in ("scenario","lab","troubleshoot")):
                move(path,chapter/"labs"/"sources"/path.name)
            elif any(k in name for k in ("full","handbook","curriculum","lesson","chapter","guide")):
                move(path,chapter/"lessons"/"sources"/path.name)
            else:
                move(path,chapter/"authoring"/"documents"/path.name)
        elif path.suffix.casefold()==".json":
            move(path,chapter/"source_archive"/path.name)

def handle_legacy_dirs(chapter: Path):
    for old,dest in [
        ("diagrams","media/diagrams"),("diagrams_shared","media/diagrams"),
        ("scenarios_200","labs/sources/scenarios_200"),
        ("routing_commands","commands/sources/routing_commands"),
        ("vpn_sources","source_archive/legacy_sections/vpn_sources"),
        ("security_ethical_hacking","source_archive/legacy_sections/security_ethical_hacking"),
        ("wireless_security","source_archive/legacy_sections/wireless_security"),
    ]:
        src=chapter/old
        if src.exists(): move_contents(src,chapter/dest)
    nested=chapter/"commands"/"source_archive"
    if nested.exists(): move_contents(nested,chapter/"commands"/"sources"/"legacy_command_archive")

def split_pack(chapter: Path, order: int, pack: dict):
    meta={k:copy.deepcopy(v) for k,v in pack.items() if k!="lessons"}
    meta["schema_version"]=int(meta.get("schema_version") or 1)
    meta["chapter_order"]=order
    meta["chapter_title_fa"]=str(pack.get("chapter_title_fa") or pack.get("title_fa") or f"فصل {order}")
    meta.setdefault("chapter_title_en",f"Chapter {order}")
    meta["merge_strategy"]="by_title"
    meta["preserve_existing_records"]=True

    rows=pack.get("lessons") if isinstance(pack.get("lessons"),list) else []
    old=read_json(chapter/"build"/"chapter.json")
    if isinstance(old,dict) and isinstance(old.get("lessons"),list):
        rows=merge_rows(rows,old["lessons"])
    rows=merge_rows(rows,[])
    core=[]
    categories={k:[] for k in CATEGORY_FIELDS}
    for row in rows:
        item=copy.deepcopy(row)
        for category,fields in CATEGORY_FIELDS.items():
            values={key:copy.deepcopy(row[key]) for key in fields if key in row}
            if values:
                categories[category].append({
                    "uid":str(row.get("uid") or ""),
                    "title_fa":str(row.get("title_fa") or row.get("title_en") or "درس"),
                    "title_en":str(row.get("title_en") or ""),
                    "fields":values,
                })
                for key in fields: item.pop(key,None)
        core.append(item)

    write_json(chapter/"lessons"/"lessons.json",{
        "schema_version":1,"chapter_order":order,"chapter_title_fa":meta["chapter_title_fa"],
        "source_of_truth":True,"pack_metadata":meta,"items":core,
    })
    for category,filename in CATEGORY_FILES.items():
        write_json(chapter/category/filename,{
            "schema_version":1,"chapter_order":order,"category":category,"source_of_truth":True,
            "items":categories[category],
        })
    return meta

CATEGORY_FILES={"questions":"questions.json","answers":"answer_key.json","examples":"examples.json","commands":"commands.json","labs":"labs.json"}

def finish_chapter(chapter: Path, order: int):
    root_pack=chapter/"chapter.json"
    pack=read_json(root_pack)
    if not isinstance(pack,dict): pack=read_json(chapter/"build"/"chapter.json")
    if not isinstance(pack,dict):
        raise RuntimeError(f"No source chapter pack available for {order}")
    preserve_root_files(chapter)
    handle_legacy_dirs(chapter)
    classify_archive(chapter)
    meta=split_pack(chapter,order,pack)
    if root_pack.exists(): root_pack.unlink()

    title=meta["chapter_title_fa"]
    for name,filename in {**CATEGORY_FILES,"lessons":"lessons.json"}.items():
        folder=chapter/name; folder.mkdir(parents=True,exist_ok=True)
        readme=folder/"README_FA.md"
        if not readme.exists():
            readme.write_text({
                "lessons":"# درس‌ها و متن آموزشی\n\nlessons.json متن درس‌های افزوده و base_curriculum.json محتوای پایه را نگه می‌دارد.\n",
                "questions":"# سؤال‌ها و آزمون‌ها\n\nquestions.json شامل سؤال‌های پیوندخورده به UID درس است؛ sources/ فایل‌های اولیه را حفظ می‌کند.\n",
                "answers":"# پاسخ‌نامه‌ها\n\nanswer_key.json پاسخ‌های ساختاریافته و sources/ کلیدهای اصلی را نگه می‌دارد.\n",
                "examples":"# مثال‌ها\n\nexamples.json مثال‌های هر درس را با UID نگه می‌دارد.\n",
                "commands":"# دستورات\n\ncommands.json فرمان‌های هر درس را با UID نگه می‌دارد؛ sources/ بسته‌های اولیه است.\n",
                "labs":"# لابراتوارها\n\nlabs.json آزمایش‌ها و سناریوهای پیوندخورده را نگه می‌دارد.\n",
            }.get(name,"# محتوا\n"),encoding="utf-8")

    for kind in ("lessons","questions","answers","examples","commands","labs"):
        (chapter/kind/"sources").mkdir(parents=True,exist_ok=True)
        source_readme=chapter/kind/"sources"/"README_FA.md"
        if not source_readme.exists():
            source_readme.write_text(
                "این پوشه فایل‌های اولیه و منابع همان نوع محتوا را با حفظ نام و ساختار قبلی نگه می‌دارد. "
                "فایل‌های اصلی حذف نشده‌اند و این منابع جدا از فایل ساختاریافتهٔ اصلی هستند.\n",
                encoding="utf-8",
            )
    for kind,summary in (
        ("media","تصاویر، دیاگرام‌ها و منابع تصویری این فصل."),
        ("authoring","اسکریپت‌ها، راهنماها و ابزارهای تألیف اختصاصی فصل."),
        ("source_archive","بایگانی منابعی که هنوز به دادهٔ ساختاریافته تبدیل نشده‌اند."),
    ):
        (chapter/kind).mkdir(parents=True,exist_ok=True)
        rp=chapter/kind/"README_FA.md"
        if not rp.exists(): rp.write_text(summary+"\n",encoding="utf-8")

    for kind,summary in (
        ("media","تصاویر، دیاگرام‌ها و منابع تصویری مربوط به این فصل."),
        ("authoring","اسکریپت‌ها، پرامپت‌ها و ابزارهای تألیف اختصاصی فصل."),
        ("source_archive","بایگانی منابعی که هنوز به ساختار دادهٔ اصلی تبدیل نشده‌اند."),
    ):
        (chapter/kind).mkdir(parents=True,exist_ok=True)
        rp=chapter/kind/"README_FA.md"
        if not rp.exists(): rp.write_text(summary+"\n",encoding="utf-8")

    for platform,runtime in (("android","android/app/src/main"),("windows","server/")):
        p=chapter/platform; p.mkdir(parents=True,exist_ok=True)
        if not (p/"README_FA.md").exists():
            p.joinpath("README_FA.md").write_text(
                "# یکپارچه‌سازی "+platform+"\n\n"
                "فقط تنظیمات و منابع مخصوص این فصل را اینجا قرار دهید. کد مشترک برنامه در مسیر "+runtime+" است و تکرار نمی‌شود.\n",
                encoding="utf-8")
        write_json(p/"manifest.json",{
            "schema_version":1,"chapter_order":order,"chapter_title_fa":title,
            "platform":platform,"shared_runtime":runtime,"chapter_source":f"tools/chapters/{order}/",
        })
    (chapter/"build").mkdir(parents=True,exist_ok=True)
    if not (chapter/"build"/"README_FA.md").exists():
        (chapter/"build"/"README_FA.md").write_text(
            "# بستهٔ سازگاری تولیدشده\n\nchapter.json خروجی assemble_chapter_packs.py است؛ آن را مستقیم ویرایش نکنید. منبع اصلی در پوشه‌های نوع محتواست.\n",
            encoding="utf-8")

    base=read_json(chapter/"lessons"/"base_curriculum.json") or {}
    core=read_json(chapter/"lessons"/"lessons.json") or {}
    cat_counts={c:len((read_json(chapter/c/f) or {}).get("items") or []) for c,f in CATEGORY_FILES.items()}
    source_files=[]
    for p in sorted(chapter.rglob("*")):
        if p.is_file() and p != chapter/"build"/"chapter.json":
            source_files.append(p.relative_to(chapter).as_posix())
    previous=read_json(chapter/"manifest.json") or {}
    manifest={
        "schema_version":2,"chapter_order":order,"slug":str(previous.get("slug") or order),
        "title_fa":title,"folder":f"tools/chapters/{order}",
        "canonical_content":[
            "lessons/base_curriculum.json","lessons/lessons.json","questions/questions.json",
            "answers/answer_key.json","examples/examples.json","commands/commands.json","labs/labs.json",
            "build/chapter.json (generated; do not edit directly)",
        ],
        "source_files":source_files,
        "counts":{
            "baseline_lessons":(base.get("counts") or {}).get("lessons",0),
            "addon_lessons":len(core.get("items") or []),"category_records":cat_counts,
            "source_files_in_archives":sum(1 for p in chapter.rglob("*") if p.is_file() and any(x in p.parts for x in ("sources","source_archive"))),
            "media_files":sum(1 for p in chapter.rglob("*") if p.is_file() and p.suffix.casefold() in (".png",".jpg",".jpeg",".webp",".svg",".mmd",".drawio")),
        },
        "status":"review_required" if core.get("items") else "base_from_runtime_source",
        "last_updated":"2026-10-15",
    }
    write_json(chapter/"manifest.json",manifest)
    readme_path=chapter/"README_FA.md"
    previous_text=readme_path.read_text(encoding="utf-8") if readme_path.exists() else f"# فصل {order}: {title}\n"
    marker="## ساختار پوشه‌های فصل"
    if marker not in previous_text:
        previous_text += (
            f"\n\n## ساختار پوشه‌های فصل\n\n"
            f"مسیر فصل: tools/chapters/{order}/\n\n"
            "متن درس در lessons/، سؤال‌ها در questions/، پاسخ‌نامه در answers/، مثال‌ها در examples/، "
            "دستورات در commands/ و لابراتوارها در labs/ قرار دارد. android/ و windows/ فقط منابع مخصوص همان بستر را دارند. "
            "build/chapter.json خروجی تولیدشده برای سازگاری برنامه‌هاست و نباید دستی ویرایش شود.\n"
        )
        readme_path.write_text(previous_text,encoding="utf-8")

def main():
    CHAPTERS.mkdir(parents=True,exist_ok=True); AUTHORING.mkdir(parents=True,exist_ok=True)
    old_shared=CHAPTERS/"_shared_sources"
    if old_shared.exists():
        move_contents(old_shared,AUTHORING/"shared_chapter_sources")
        try: old_shared.rmdir()
        except OSError: pass
    for legacy in sorted(CHAPTERS.glob("ch[0-9][0-9]_*")):
        m=re.match(r"^ch(\d{2})_",legacy.name)
        if m and 1<=int(m.group(1))<=68:
            order=int(m.group(1)); dest=CHAPTERS/str(order); dest.mkdir(parents=True,exist_ok=True)
            move_contents(legacy,dest)
    for order in range(1,69):
        chapter=CHAPTERS/str(order); chapter.mkdir(parents=True,exist_ok=True)
        pack=read_json(chapter/"chapter.json")
        if not isinstance(pack,dict): pack=read_json(chapter/"build"/"chapter.json")
        if not isinstance(pack,dict):
            raise RuntimeError(f"Chapter {order} has no chapter pack to split")
        finish_chapter(chapter,order)
    # Preserve unexpected old directories outside the numeric chapter root.
    for item in list(CHAPTERS.iterdir()):
        if item.is_dir() and not item.name.isdigit():
            move_contents(item,AUTHORING/"legacy_chapter_layout"/item.name)
            try: item.rmdir()
            except OSError: pass
    numbers={int(p.name) for p in CHAPTERS.iterdir() if p.is_dir() and p.name.isdigit()}
    if numbers!=set(range(1,69)): raise RuntimeError(f"Numeric folder invariant failed: {sorted(numbers)}")
    write_root_readme()
    write_index()
    print("[chapter-layout] numeric folders 1..68; lesson fields split by type")

def write_root_readme():
    lines = [
        "# ساختار محتوای فصل‌های NetworkAll",
        "",
        "زیر tools/chapters دقیقاً ۶۸ پوشه با نام عددی 1 تا 68 وجود دارد. نام پوشه شمارهٔ فصل است؛ پوشهٔ chXX یا نام مستعار فصل نسازید.",
        "",
        "## درخت استاندارد هر فصل",
        "",
        "tools/chapters/1/  (همین ساختار برای 2 تا 68)",
        "├── manifest.json",
        "├── README_FA.md",
        "├── lessons/",
        "│   ├── base_curriculum.json   ← درس‌های پایه",
        "│   ├── lessons.json           ← متن درس‌های افزوده",
        "│   └── sources/               ← متن‌های اولیهٔ همان فصل",
        "├── questions/",
        "│   ├── questions.json",
        "│   └── sources/               ← آزمون‌ها و بانک سؤال اصلی",
        "├── answers/",
        "│   ├── answer_key.json",
        "│   └── sources/               ← پاسخ‌نامه‌ها و کلیدهای اصلی",
        "├── examples/examples.json",
        "├── commands/commands.json",
        "├── labs/labs.json",
        "├── media/                    ← تصویر و دیاگرام",
        "├── authoring/                ← ابزار و پرامپت مختص فصل",
        "├── android/manifest.json",
        "├── windows/manifest.json",
        "├── source_archive/           ← منبع‌هایی که هنوز نرمال نشده‌اند",
        "└── build/chapter.json        ← خروجی خودکار؛ ویرایش دستی ممنوع",
        "",
        "## فایل مرجع هر نوع محتوا",
        "",
        "- lessons/base_curriculum.json و lessons/lessons.json: درس‌ها و متن آموزشی.",
        "- questions/questions.json: سؤال‌های ساختاریافته؛ فایل‌های اولیه در questions/sources/ حفظ می‌شوند.",
        "- answers/answer_key.json: پاسخ ساختاریافته؛ اصل پاسخ‌نامه در answers/sources/ می‌ماند.",
        "- examples/examples.json: مثال‌ها و راه‌حل‌های نمونه.",
        "- commands/commands.json: فرمان‌ها و مثال‌های CLI.",
        "- labs/labs.json: سناریوهای آزمایش و عیب‌یابی.",
        "- android/ و windows/: فقط پیکربندی/منبع مختص همان بستر؛ کد مشترک تکثیر نمی‌شود.",
        "",
        "خالی بودن items در یک بانک یعنی برای آن فصل هنوز رکورد ساختاریافته‌ای در منبع پیدا نشده؛ فایل‌های اصلی در sources/ یا source_archive/ حذف نمی‌شوند.",
        "",
        "## افزودن محتوا",
        "",
        "درس جدید را در lessons/lessons.json و با UID پایدار و یکتا اضافه کنید. سؤال، پاسخ، مثال، فرمان و لاب را در فایل همان نوع و با همان UID درس ثبت کنید؛ در هر رکورد، fields باید فقط فیلدهای مربوط به همان نوع را داشته باشد.",
        "",
        "build/chapter.json خروجی تولیدی assemble_chapter_packs.py است و در Git نگهداری نمی‌شود. ساخت اندروید و اجرای windows/start.bat آن را از فایل‌های مرجع می‌سازند.",
        "",
        "برای بازتولید و اعتبارسنجی از ریشهٔ مخزن اجرا کنید:",
        "",
        "    python scripts/assemble_chapter_packs.py --strict",
        "    python scripts/merge_content_packs_into_android.py",
        "",
        "فهرست شماره‌ها و شمار رکوردهای پایه/افزوده در INDEX_FA.md است.",
    ]
    (CHAPTERS / "README_FA.md").write_text("\n".join(lines) + "\n", encoding="utf-8")

def write_index():
    rows=[]
    for order in range(1,69):
        d=CHAPTERS/str(order); manifest=read_json(d/"manifest.json") or {}
        counts=manifest.get("counts") or {}
        rows.append((order,manifest.get("title_fa") or f"فصل {order}",counts.get("addon_lessons",0),
                     counts.get("baseline_lessons",0),d.relative_to(ROOT).as_posix()))
    lines=[
        "# فهرست فصل‌ها — NetworkAll","",
        "ساختار عددی: هر فصل یک پوشه از 1 تا 68 دارد؛ متن، سؤال، پاسخ، مثال، دستور و لاب پوشهٔ مستقل دارند.","",
        "| شماره | عنوان | درس افزوده | درس پایه | مسیر |","|---:|---|---:|---:|---|",
    ]
    lines.extend(f"| {n} | {title} | {addon} | {base} | {path}/ |" for n,title,addon,base,path in rows)
    (CHAPTERS/"INDEX_FA.md").write_text("\n".join(lines)+"\n",encoding="utf-8")

if __name__=="__main__": main()
