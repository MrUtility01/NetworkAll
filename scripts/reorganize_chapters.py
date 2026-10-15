#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Reorganize chapter content into one canonical folder per chapter, retaining all sources."""
from __future__ import annotations
import copy, hashlib, importlib.util, json, re, shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CHAPTERS = ROOT / "tools" / "chapters"
SHARED = CHAPTERS / "_shared_sources"
AUTHORING = ROOT / "tools" / "authoring"
SLUGS = {
1:"it_architecture",2:"hardware_servers",3:"bios_uefi_boot",4:"operating_systems",5:"filesystem_storage",
6:"network_fundamentals",7:"ethernet_switching",8:"ipv4_ipv6_subnetting",9:"arp_icmp_tcp_udp",10:"dns",
11:"dhcp_ipam",12:"cabling_fiber_rack",13:"cisco_switching",14:"advanced_routing",15:"mpls_vrf_l3vpn",
16:"multicast",17:"evpn_vxlan",18:"sdn_sdwan_sase",19:"mikrotik_basics",20:"mikrotik_routing_firewall_nat",
21:"mikrotik_qos_vpn_ha",22:"enterprise_wireless",23:"ptp_ptmp",24:"fortigate_firewall",25:"pfsense_opnsense_sophos",
26:"pki_tls",27:"aaa_nac",28:"windows_server_core",29:"active_directory",30:"windows_dns_dhcp_nps",
31:"file_print_dfs",32:"windows_endpoint_security",33:"entra_id_hybrid",34:"m365_intune_email",35:"powershell_cmd",
36:"linux_administration",37:"linux_networking",38:"linux_web_services",39:"linux_security",40:"vmware_hyperv",
41:"proxmox_docker",42:"kubernetes",43:"cloud_networking",44:"cloud_security_governance",45:"enterprise_storage",
46:"backup_disaster_recovery",47:"datacenter",48:"high_availability_load_balancing",49:"monitoring",50:"siem_elk",
51:"it_automation_ai",52:"database_administration",53:"database_security",54:"voip_pbx",55:"cctv_access_bms_iot",
56:"zero_trust_itil",57:"network_security",58:"endpoint_appsec_devsecops",59:"soc_ir_hunting",60:"ethical_hacking_lab_troubleshooting",
61:"enterprise_architecture",62:"it_operations_noc",63:"documentation_runbooks_cmdb",64:"git_github",
65:"cybersecurity_ethical_hacking_wireless",66:"ospf_bgp_redistribution",67:"enterprise_vpn_ipsec_ssl",68:"commands_encyclopedia"}
TITLES_OVERRIDE = {40:"VMware Hyper-V",51:"اتوماسیون و AI در IT",60:"عیب‌یابی هک اخلاقی لاب سازمانی",
63:"مستندسازی Runbook و CMDB",64:"Git و GitHub",65:"امنیت سایبری و هک اخلاقی (دفاعی) + بی‌سیم",
66:"مسیریابی عمیق OSPF/BGP/Redistribution",67:"VPN سازمانی IPsec/SSL و عیب‌یابی",68:"دانشنامه جامع دستورات"}

def folder(n): return CHAPTERS / f"ch{n:02d}_{SLUGS[n]}"
def digest(p):
    h=hashlib.sha256()
    with p.open("rb") as f:
        for b in iter(lambda:f.read(1024*1024),b""): h.update(b)
    return h.hexdigest()
def move(src,dst):
    if not src.exists(): return
    dst.parent.mkdir(parents=True,exist_ok=True)
    if dst.exists():
        if src.is_file() and dst.is_file() and digest(src)==digest(dst):
            src.unlink(); return
        if src.is_dir() and dst.is_dir():
            for x in list(src.iterdir()): move(x,dst/x.name)
            try: src.rmdir()
            except OSError: pass
            return
        base=dst; i=2
        while dst.exists():
            dst=base.with_name(f"{base.stem}__{src.parent.name}_{i}{base.suffix}"); i+=1
    shutil.move(str(src),str(dst))
def move_contents(src,dst):
    if not src.is_dir(): return
    for x in list(src.iterdir()): move(x,dst/x.name)
    try: src.rmdir()
    except OSError: pass
def read_json(p):
    try: return json.loads(p.read_text(encoding="utf-8"))
    except Exception: return None
def write_json(p,obj):
    p.parent.mkdir(parents=True,exist_ok=True)
    p.write_text(json.dumps(obj,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
def titles():
    out=dict(TITLES_OVERRIDE)
    p=ROOT/"docs/ai_continuity/CHAPTER_TARGET_SELECTION.md"
    if p.exists():
        for line in p.read_text(encoding="utf-8").splitlines():
            m=re.match(r"^\|\s*(\d{1,2})\s*\|\s*([^|]+?)\s*\|",line)
            if m: out.setdefault(int(m.group(1)),m.group(2).strip())
    for n in range(1,69): out.setdefault(n,f"فصل {n}")
    return out
def ensure_folders():
    CHAPTERS.mkdir(parents=True,exist_ok=True)
    return {n:folder(n) for n in range(1,69)}
def normalizer_module():
    p=ROOT/"scripts/merge_content_packs_into_android.py"
    spec=importlib.util.spec_from_file_location("networkall_merger",p)
    if spec is None or spec.loader is None: raise RuntimeError("Cannot load existing pack normalizer")
    m=importlib.util.module_from_spec(spec); spec.loader.exec_module(m); return m
def as_text(x):
    if x is None: return ""
    if isinstance(x,list): return "\n".join(str(y) for y in x)
    if isinstance(x,dict): return json.dumps(x,ensure_ascii=False,sort_keys=True)
    return str(x)
def chapter_num(x):
    if isinstance(x, int) and 1 <= x <= 68:
        return x
    if isinstance(x, str):
        digits = x.translate(str.maketrans("۰۱۲۳۴۵۶۷۸۹", "0123456789"))
        m = re.match(r"^\s*(?:(?:chapter|ch|فصل)\s*)?0?(\d{1,2})(?=\s|[.:_/-]|$)", digits, re.IGNORECASE)
        if m and 1 <= int(m.group(1)) <= 68:
            return int(m.group(1))
    return None
def infer_order(ch,payload,name,blob=""):
    for k in ("chapter_order","order_index","chapter_no","chapter_number","number"):
        n=chapter_num(ch.get(k))
        if n: return n
    text=(name+" "+" ".join(str(ch.get(k) or "") for k in ("title_fa","title_en","title","name","slug","id"))+" "+blob).lower()
    if "automation_python" in text or "اتوماسیون و ai در it" in text: return 51
    if "ospf_bgp" in text or "redistribution_deep" in text: return 66
    if "vpn_enterprise" in text or "ipsec_ssl" in text: return 67
    if "git_chapter64" in text or "git and github" in text: return 64
    if "wireless_security" in text or "security_ethical_hacking" in text: return 65
    if "windows_server" in text:
        if any(k in text for k in ("active directory","active_directory","ad ds","ldap")): return 29
        if any(k in text for k in ("powershell","power shell","cmd.exe","cmdlet")): return 35
        if any(k in text for k in ("entra id","azure ad","hybrid identity")): return 33
        if any(k in text for k in ("intune","microsoft 365","m365","exchange online")): return 34
        if any(k in text for k in ("dns","dhcp","nps","radius")): return 30
        if any(k in text for k in ("group policy","gpo","print server","dfs","file server","smb")): return 31
        if any(k in text for k in ("endpoint security","defender","attack surface")): return 32
        return 28
    if "switching_routing" in name:
        topic = (" ".join(str(ch.get(k) or "") for k in ("title_fa","title_en","title","name","slug")) + " " + blob).lower()
        if any(k in topic for k in ("mikrotik","routeros")):
            if any(k in topic for k in ("qos","queue","netwatch","wireguard","high availability")): return 21
            if any(k in topic for k in ("firewall","nat","ospf","bgp","routing")): return 20
            return 19
        if any(k in topic for k in ("ospf","bgp","eigrp","redistribution","route-map","advanced routing")): return 14
        if any(k in topic for k in ("ethernet","stp","vlan","trunk","etherchannel","switching","cisco ios")): return 13
        raise ValueError(f"Switching/routing chapter title needs explicit mapping: {topic[:250]}")
    for n,keys in [
      (65,("ethical hacking","هک اخلاقی","cybersecurity","wireless security","security_ethical")),
      (67,("ipsec","ssl vpn","vpn enterprise","ike phase")),
      (66,("ospf","bgp","redistribution","route-map")),
      (51,("automation","اتوماسیون","netmiko","paramiko","ansible","terraform")),
      (64,("git","github","gitflow","pull request")),
      (68,("command encyclopedia","دستورات","cli command","fortigate commands")),
      (24,("fortigate","fortios","firewall policy")),
      (14,("routing","مسیریابی","eigrp","ospf","bgp")),
      (13,("cisco switching","vlan","etherchannel","spanning tree"))]:
        if any(k in text for k in keys): return n
    raise ValueError(f"Unclassifiable source chapter: {name}; title={text[:300]}")
def split_multi_curriculum(p,payload):
    curr=payload.get("curriculum"); rows=curr.get("chapters") if isinstance(curr,dict) else None
    if not isinstance(rows,list): return False
    if not rows: return True
    if len(rows)==1:
        n=chapter_num(payload.get("chapter_order"))
        if n is None: n=infer_order(rows[0],payload,p.name,json.dumps(rows[0],ensure_ascii=False)[:6000])
        dest=folder(n)/"source_archive"/p.name
        payload=copy.deepcopy(payload); payload["chapter_order"]=n
        payload["split_provenance"]={"original_file":p.name,"original_sha256":digest(p)}
        write_json(dest,payload); p.unlink(); return True
    SHARED.mkdir(parents=True,exist_ok=True)
    if not (SHARED/p.name).exists(): shutil.copy2(p,SHARED/p.name)
    for idx,ch in enumerate(rows,1):
        title=json.dumps(ch,ensure_ascii=False)
        n=infer_order(ch,payload,p.name,title[:9000])
        part=copy.deepcopy(payload); part["curriculum"]=copy.deepcopy(curr); part["curriculum"]["chapters"]=[copy.deepcopy(ch)]
        part["chapter_order"]=n
        part["split_provenance"]={"original_file":p.name,"original_sha256":digest(p),"source_chapter_index":idx,
                                  "source_chapter_title":ch.get("title_fa") or ch.get("title_en") or ch.get("title") or ""}
        write_json(folder(n)/"source_archive"/f"{p.stem}__ch{n:02d}{p.suffix}",part)
    p.unlink(); return True
def split_lessons(p,payload,forced=None):
    lessons=payload.get("lessons")
    if not isinstance(lessons,list): return False
    groups={}
    for row in lessons:
        if not isinstance(row,dict): continue
        n=forced or chapter_num(row.get("chapter_order")) or chapter_num(payload.get("chapter_order"))
        if n is None: n=infer_order({},payload,p.name,json.dumps(row,ensure_ascii=False)[:5000])
        groups.setdefault(n,[]).append(copy.deepcopy(row))
    if not groups: return True
    if len(groups)>1:
        SHARED.mkdir(parents=True,exist_ok=True)
        if not (SHARED/p.name).exists(): shutil.copy2(p,SHARED/p.name)
    for n,rows in groups.items():
        sub=copy.deepcopy(payload); sub["chapter_order"]=n; sub["lessons"]=rows
        sub["split_provenance"]={"original_file":p.name,"original_sha256":digest(p)}
        for row in sub["lessons"]:
            old=chapter_num(row.get("chapter_order"))
            row["source_chapter_order"]=old
            row["chapter_order"]=n
        write_json(folder(n)/"source_archive"/p.name,sub)
    p.unlink(); return True
def merge_text(old,new):
    old,new=as_text(old).strip(),as_text(new).strip()
    if not old: return new
    if not new or new==old or new in old: return old
    if old in new: return new
    return old+"\n\n---\n\n"+new
def title_key(s):
    return re.sub(r"\s+"," ",re.sub(r"^\[L[0-4]\]\s*","",str(s or "").strip())).casefold()
def consolidate(rows):
    out=[]; indexed={}
    for row in rows:
        if not isinstance(row,dict): continue
        row=copy.deepcopy(row)
        title=str(row.get("title_fa") or row.get("title_en") or "درس").strip()
        k=title_key(title)
        if k not in indexed:
            row["title_fa"]=title; indexed[k]=row; out.append(row); continue
        old=indexed[k]
        for f in ("full_content","commands","examples","notes"): old[f]=merge_text(old.get(f),row.get(f))
        for f in ("summary","title_en"):
            if len(as_text(row.get(f)))>len(as_text(old.get(f))): old[f]=row[f]
        meta=old.get("meta") if isinstance(old.get("meta"),dict) else {}
        other=row.get("meta") if isinstance(row.get("meta"),dict) else {}
        for mk,mv in other.items():
            if mk not in meta: meta[mk]=mv
            elif meta[mk]!=mv: meta["source_"+mk]=mv
        old["meta"]=meta
    return out
def move_loose_jsons_into_archive(d):
    for p in sorted(d.rglob("*.json")):
        if "source_archive" in p.parts or "_shared_sources" in p.parts: continue
        if p.name in ("chapter.json","base_curriculum.json","manifest.json"): continue
        obj=read_json(p)
        if isinstance(obj,dict) and any(k in obj for k in ("lessons","commands","curriculum","scope","questions","scenarios","answer_key")):
            move(p,d/"source_archive"/p.relative_to(d))
def collect_lessons(d,n,normalizer):
    rows=[]; archive=d/"source_archive"
    if not archive.exists(): return rows
    for p in sorted(archive.rglob("*.json")):
        if any(k in p.name.lower() for k in ("answer_key","questions","scenarios","manifest")): continue
        obj=read_json(p)
        if not isinstance(obj,dict): continue
        try: got=normalizer.normalize_pack(p,obj) or []
        except Exception as e:
            print(f"[organize] converter warning {p.relative_to(ROOT)}: {e}"); got=[]
        if not got and isinstance(obj.get("curriculum"),dict):
            try: got=normalizer.blueprint_to_lessons(obj,[],n)
            except Exception: got=[]
        if not got and isinstance(obj.get("commands"),list):
            try: got=normalizer.commands_to_lessons(obj)
            except Exception: got=[]
        for idx,item in enumerate(got,1):
            if not isinstance(item,dict): continue
            row=copy.deepcopy(item); row["chapter_order"]=n
            row.setdefault("subchapter_order",1); row.setdefault("lesson_order",idx)
            original_uid = str(row.get("uid") or "")
            if not original_uid:
                slug=re.sub(r"[^a-zA-Z0-9_-]+","-",p.stem).strip("-") or "source"
                original_uid=f"lesson:ch{n:02d}:pack:{slug}:{idx:05d}"
            new_uid=re.sub(r"^lesson:ch[0-9]{2,3}:", f"lesson:ch{n:02d}:", original_uid)
            if not new_uid.startswith(f"lesson:ch{n:02d}:"):
                slug = re.sub(r"[^a-zA-Z0-9_-]+","-",p.stem).strip("-") or "source"
                new_uid=f"lesson:ch{n:02d}:pack:{slug}:{idx:05d}"
            if new_uid != original_uid:
                meta=row.get("meta") if isinstance(row.get("meta"),dict) else {}
                meta.setdefault("source_uid",original_uid)
                row["meta"]=meta
            row["uid"]=new_uid
            row["title_fa"]=str(row.get("title_fa") or row.get("title_en") or f"درس {idx}")
            for f in ("summary","full_content","commands","examples","notes"): row[f]=as_text(row.get(f))
            meta=row.get("meta") if isinstance(row.get("meta"),dict) else {}
            meta.setdefault("source_file",str(p.relative_to(d))); row["meta"]=meta
            row["source_status"]=row.get("source_status") or "review_required"
            rows.append(row)
    return consolidate(rows)
def write_indexes(folders):
    titlemap=titles(); normalizer=normalizer_module(); result=[]
    for n,d in folders.items():
        # Preserve old pack manifests before making one canonical manifest per chapter.
        oldmanifest=d/"manifest.json"
        if oldmanifest.exists() and not (d/"source_archive"/"legacy_manifest.json").exists():
            move(oldmanifest,d/"source_archive"/"legacy_manifest.json")
        move_loose_jsons_into_archive(d)
    for n,d in folders.items():
        rows=collect_lessons(d,n,normalizer); seen=set()
        for i,row in enumerate(rows,1):
            uid=str(row.get("uid") or f"lesson:ch{n:02d}:pack:{i:05d}"); new=uid; suffix=2
            while new in seen: new=f"{uid}:folderdup:{suffix}"; suffix+=1
            row["uid"]=new; seen.add(new); row["lesson_order"]=i
        title=titlemap.get(n,f"فصل {n}")
        pack={"schema_version":1,"chapter_order":n,"chapter_title_fa":title,
              "chapter_title_en":f"Chapter {n:02d} — {SLUGS[n].replace('_',' ').title()}",
              "merge_strategy":"by_title","preserve_existing_records":True,
              "source_of_truth_note":"Base lesson definitions live in base_curriculum.json; chapter.json contains normalized add-on content; original sources remain in source_archive/.",
              "lessons":rows}
        write_json(d/"chapter.json",pack)
        if not (d/"README_FA.md").exists():
            (d/"README_FA.md").write_text(
              f"# فصل {n:02d}: {title}\n\n"
              f"مسیر اصلی: {d.relative_to(ROOT).as_posix()}/\n\n"
              "chapter.json بسته استاندارد افزایشی برای اندروید و ویندوز است. فایل‌های اولیه، آزمون‌ها، پاسخ‌نامه‌ها و نسخه‌های قبلی در source_archive نگهداری شده‌اند. محتوای پایه هنوز از منبع runtime پروژه ساخته می‌شود؛ این پوشه محل محتوای اختصاصی و افزودهٔ همین فصل است.\n",
              encoding="utf-8")
        readme = d/"README_FA.md"
        readme_text = readme.read_text(encoding="utf-8") if readme.exists() else ""
        marker = "## فایل‌های اصلی فصل"
        if marker not in readme_text:
            readme_text += (
                "\n\n## فایل‌های اصلی فصل\n\n"
                "- base_curriculum.json: تعریف درس‌های پایهٔ همین فصل.\n"
                "- chapter.json: بستهٔ استاندارد محتوای افزوده و نرمال‌شده.\n"
                "- manifest.json: فهرست فایل‌ها و شمار رکوردها.\n"
                "- source_archive/: منابع اولیه، آزمون‌ها و پاسخ‌نامه؛ در build اسکن نمی‌شود.\n"
            )
            readme.write_text(readme_text, encoding="utf-8")
        listing=sorted(str(p.relative_to(d)).replace("\\","/") for p in d.rglob("*") if p.is_file() and p.name!="manifest.json")
        sourcejson=sum(1 for p in (d/"source_archive").rglob("*.json")) if (d/"source_archive").exists() else 0
        media=sum(1 for p in d.rglob("*") if p.is_file() and p.suffix.lower() in (".png",".jpg",".jpeg",".webp",".svg",".mmd") and "source_archive" not in p.parts)
        manifest={"schema_version":1,"chapter_order":n,"slug":SLUGS[n],"title_fa":title,
          "folder":d.relative_to(ROOT).as_posix(),"canonical_content":["base_curriculum.json","chapter.json"],
          "source_files":listing,"counts":{"addon_lessons":len(rows),"baseline_lessons":(read_json(d/"base_curriculum.json") or {}).get("counts",{}).get("lessons",0),"source_json_files":sourcejson,"media_files":media},
          "status":"review_required" if rows or listing else "base_from_runtime_source","last_updated":"2026-10-15"}
        write_json(d/"manifest.json",manifest)
        result.append((n,title,len(rows),len(listing),d.relative_to(ROOT).as_posix()))
    lines=["# فهرست فصل‌ها — NetworkAll","","هر فصل یک پوشه اصلی دارد. chapter.json بسته استاندارد افزایشی است؛ manifest.json موجودی و وضعیت را ثبت می‌کند و source_archive منبع اولیه، آزمون‌ها و پاسخ‌نامه‌ها را نگه می‌دارد.","",
           "| فصل | عنوان | درس افزوده | تعداد فایل | پوشه |","|---:|---|---:|---:|---|"]
    lines += [f"| {n:02d} | {t} | {lessons} | {files} | {path}/ |" for n,t,lessons,files,path in result]
    (CHAPTERS/"INDEX_FA.md").write_text("\n".join(lines)+"\n",encoding="utf-8")

def main():
    folders=ensure_folders()
    # Move existing chapter-scoped packs into their single canonical chapter directory.
    mappings=[
      ("tools/packs/ch40_vmware_hyperv",40,""),
      ("tools/packs/ch60",60,""),
      ("tools/packs/ch63_documentation_cmdb",63,""),
      ("tools/packs/git_chapter64",64,""),
      ("tools/packs/commands_encyclopedia",68,"commands"),
      ("tools/packs/routing_deep",68,"routing_commands"),
      ("tools/packs/vpn_enterprise",67,"vpn_sources"),
      ("tools/engineer_jokar_security_ethical_hacking",65,"security_ethical_hacking"),
      ("tools/engineer_jokar_wireless_security",65,"wireless_security"),
      ("tools/scenarios_200",60,"scenarios_200")]
    for rel,n,sub in mappings:
        src=ROOT/rel
        if src.exists(): move_contents(src,folder(n)/sub if sub else folder(n))

    # Preserve originals of multi-chapter packs centrally, and split runnable copies per chapter.
    SHARED.mkdir(parents=True,exist_ok=True)
    multi=[
      ("tools/packs/switching_routing/switching_routing_curriculum_pack.json","curriculum"),
      ("tools/packs/windows_server/windows_server_complete_curriculum_pack.json","curriculum"),
      ("tools/engineer_jokar_automation_python/automation_python_curriculum_pack.json","lessons")]
    for rel,kind in multi:
        p=ROOT/rel
        if not p.exists(): continue
        payload=read_json(p)
        if not isinstance(payload,dict): raise ValueError(f"Cannot parse {rel}")
        if kind=="lessons": split_lessons(p,payload)
        elif not split_multi_curriculum(p,payload):
            # Support packs that encode chapter_order directly on their lesson records.
            if not split_lessons(p,payload): raise ValueError(f"Unknown multi-chapter schema: {rel}")
    automation=ROOT/"tools/engineer_jokar_automation_python"
    if automation.exists(): move_contents(automation,AUTHORING/"automation_python")

    # Single-chapter source packs whose previous location/title was misleading.
    moves=[
      ("tools/ENGINEER_JOKAR_OSPF_BGP_Redistribution_deep_v1.json",66,"source_archive/ospf_bgp_redistribution_deep_v1.json"),
      ("tools/ENGINEER_JOKAR_VPN_Enterprise_IPsec_SSL_Troubleshooting_deep_v1.json",67,"source_archive/vpn_enterprise_ipsec_ssl_deep_v1.json"),
      ("chapter_68_fortigate.json.json",68,"commands/fortigate_cli.json")]
    for rel,n,tail in moves:
        p=ROOT/rel
        if not p.exists(): continue
        obj=read_json(p)
        if isinstance(obj,dict) and n in (65,68) and isinstance(obj.get("lessons"),list):
            obj["source_chapter_order"]=chapter_num(obj.get("chapter_order")); obj["chapter_order"]=n
            for row in obj["lessons"]:
                if isinstance(row,dict):
                    row["source_chapter_order"]=chapter_num(row.get("chapter_order")); row["chapter_order"]=n
            write_json(p,obj)
        move(p,folder(n)/tail)

    # The root Cisco routing JSON is a duplicate of the pack already assigned to chapter 68.
    rootroute=ROOT/"chapter_68_cisco_routing_1600.json"
    if rootroute.exists():
        target=folder(68)/"routing_commands/chapter_68_cisco_routing_1600.json"
        if target.exists() and digest(rootroute)==digest(target): rootroute.unlink()
        else: move(rootroute,target)

    diagramdir=ROOT/"tools/packs/diagrams"
    if diagramdir.exists(): move_contents(diagramdir,folder(60)/"diagrams_shared")

    # The staged Chapter 60 tree contains duplicates plus one longer diagram; preserve unique files.
    staging=ROOT/"tree/content/ch60-enrichment-stage1-2"
    if staging.exists():
        for p in sorted(staging.rglob("*")):
            if not p.is_file(): continue
            dup=False
            for q in folder(60).rglob("*"):
                if q.is_file() and digest(p)==digest(q): dup=True; break
            if not dup: move(p,folder(60)/"source_archive/staging_unique"/p.relative_to(staging))
        shutil.rmtree(staging,ignore_errors=True)
        try: (ROOT/"tree/content").rmdir(); (ROOT/"tree").rmdir()
        except OSError: pass

    ziproot=ROOT/"tools/_archive_zips"
    zipmap={"engineer_jokar_switching_routing.zip":13,"engineer_jokar_windows_server.zip":28,
            "engineer_jokar_wireless_security.zip":65,"NetworkEncyclopedia_Git_Chapter64.zip":64}
    if ziproot.exists():
        for p in list(ziproot.iterdir()):
            if p.is_file() and p.name in zipmap: move(p,folder(zipmap[p.name])/"source_archive/legacy_zips"/p.name)
            else: move(p,AUTHORING/"archives"/p.name)
        try: ziproot.rmdir()
        except OSError: pass

    # Chapter-specific authoring materials go beside their chapter; global authoring utilities stay grouped.
    gitteacher=ROOT/"tools/chapter_git_teacher.py"
    if gitteacher.exists(): move(gitteacher,folder(64)/"authoring"/gitteacher.name)
    commandauthor=ROOT/"tools/commands_encyclopedia"
    if commandauthor.exists(): move_contents(commandauthor,folder(68)/"authoring/commands_encyclopedia")
    promptroot=ROOT/"tools/chapter_prompts"
    if promptroot.exists():
        for rel,n in [("priority/01_ospf_bgp_redistribution.md",66),("priority/02_vpn_ipsec_ssl.md",67),
                      ("priority/03_firewall_practical.md",24),("priority/04_network_troubleshooting.md",60)]:
            p=promptroot/rel
            if p.exists(): move(p,folder(n)/"authoring/prompts"/p.name)
        move_contents(promptroot,AUTHORING/"chapter_prompts")
    for rel in ("tools/packs/README_FA.md","tools/packs/README.md","tools/packs/_templates"):
        p=ROOT/rel
        if p.exists(): move(p,AUTHORING/"packs"/p.name)

    refs=ROOT/"docs/reference_materials"; refs.mkdir(parents=True,exist_ok=True)
    for rel,name in [("جزوه_جامع_شبکه_300_صفحه.docx","network_comprehensive_handbook.docx"),
                     ("مسیر کامل یک پکت شبکه تا سرور.png","network_packet_path.png")]:
        p=ROOT/rel
        if p.exists(): move(p,refs/name)
    info=ROOT/"info.txt"
    if info.exists(): move(info,ROOT/"docs/PROJECT_INFO.txt")

    # Normalize all importable add-on material into one chapter.json; raw JSON remains archived.
    write_indexes(folders)

    # Remaining files under tools/packs were shared authoring assets, not canonical lessons.
    packroot=ROOT/"tools/packs"
    if packroot.exists():
        for p in list(packroot.iterdir()):
            if p.is_dir(): move_contents(p,AUTHORING/"packs"/p.name)
            else: move(p,AUTHORING/"packs"/p.name)
        try: packroot.rmdir()
        except OSError: pass

    dirs=sorted(CHAPTERS.glob("ch[0-9][0-9]_*"))
    assert len(dirs)==68, f"Expected 68 chapter folders, got {len(dirs)}"
    count=0
    for n,d in folders.items():
        obj=read_json(d/"chapter.json")
        assert isinstance(obj,dict) and obj.get("chapter_order")==n and isinstance(obj.get("lessons"),list), f"Bad chapter.json: {d}"
        uids=[x.get("uid") for x in obj["lessons"]]
        assert len(uids)==len(set(uids)), f"Duplicate UIDs in {d}"
        count += len(uids)
    print(f"[organize] 68 chapter folders; {count} normalized add-on lessons")
    print(f"[organize] shared original sources: {len(list(SHARED.glob('*.json')))}")
    print("[organize] source files preserved in chapter-local source_archive or the shared original-source register")

if __name__=="__main__":
    main()
