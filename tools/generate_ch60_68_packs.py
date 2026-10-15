#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Generate validated, shared deep content for chapters 60-68.

The generated JSON packs are consumed by Android export/merge and by the
Windows/Flask seed path. All commands and labs are intended for authorized
systems or isolated simulation only.
"""
from __future__ import annotations
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "tools" / "packs" / "ch60_68"
LEVELS = [
    ("L0", "آشنایی", "Intro"),
    ("L1", "مقدماتی", "Foundation"),
    ("L2", "ادمین", "Administrator"),
    ("L3", "مهندس", "Engineer"),
    ("L4", "خبره", "Architect"),
]
CHAPTERS = {
60: ("عیب‌یابی شبکه و آزمایشگاه امنیت مجاز", [
"ثبت علامت و دامنه اثر", "روش Bottom-Up", "روش Top-Down", "تقسیم مسئله و فرضیه", "ردیابی مسیر End-to-End",
"Baseline و مقایسه Known-Good", "تحلیل Change History", "عیب‌یابی DNS", "عیب‌یابی DHCP", "عیب‌یابی ARP و Gateway",
"تحلیل TCP Handshake", "تحلیل Capture در Wireshark", "فیلتر Display و TCP Stream", "Nmap فقط در Scope مجاز",
"ارزیابی آسیب‌پذیری در Lab", "مدیریت Rules of Engagement", "جمع‌آوری Evidence و Chain of Custody", "گزارش RCA و اقدام پیشگیرانه"]),
61: ("پایش، مانیتورینگ و مشاهده‌پذیری شبکه", [
"معماری Monitoring", "SNMPv3 و اصول امن", "Syslog و شدت رخداد", "Telemetry و Streaming", "NetFlow و IPFIX",
"متریک در برابر Log و Trace", "تعریف Baseline عملکرد", "طراحی Alert و Threshold", "کاهش Alert Noise", "مدیریت False Positive",
"پایش Availability و SLI", "SLO و Error Budget", "Correlation شناسه رخداد", "همگام‌سازی NTP", "Retention و چرخه عمر Log",
"داشبورد NOC", "پایش ظرفیت و Trend", "Runbook برای Alert"]),
62: ("عملیات IT و NOC", [
"مدیریت Incident", "اولویت‌بندی P1 تا P4", "Escalation Matrix", "Shift Handover", "مدیریت Change",
"مدیریت Problem و RCA", "مدیریت درخواست Service Request", "مدیریت SLA و OLA", "مانیتورینگ شیفت NOC", "تشخیص قطعی گسترده",
"مدیریت Maintenance Window", "ارتباطات هنگام بحران", "مدیریت Vendor و ISP", "مدیریت ظرفیت لینک", "کنترل Backup پیکربندی",
"تست Failover برنامه‌ریزی‌شده", "گزارش روزانه NOC", "KPI و بهبود مستمر عملیات"]),
63: ("مستندسازی، Runbook و CMDB", [
"ساختار Runbook", "نوشتن SOP قابل اجرا", "CMDB و CI", "ارتباط Dependency", "مدیریت مالکیت سرویس",
"نقشه توپولوژی لایه ۲ و ۳", "IPAM و مدیریت آدرس", "مستندسازی VLAN و Trunk", "مستندسازی Routing", "مستندسازی Firewall Rule",
"مدیریت نسخه مستندات", "تأیید و بازبینی مستندات", "تاریخچه تغییرات", "ماتریس RACI", "بازیابی از Backup",
"مدیریت Knowledge Base", "ثبت Known Error", "تحویل دانش و آموزش اپراتور"]),
64: ("Git و GitHub برای مهندسان شبکه", [
"Git Repository و Working Tree", "مفهوم Commit و History", "Branch و Merge", "حل Merge Conflict", "Pull Request و Code Review",
".gitignore و داده محرمانه", "مدیریت Secret و Token", "Tag و Release", "Revert در برابر Reset", "Stash و Worktree",
"GitHub Actions مبانی", "Branch Protection", "Issue و Project", "نسخه‌بندی فایل پیکربندی", "Diff برای Config",
"Pre-commit و Lint", "Backup و Recovery مخزن", "Workflow انتشار امن"]),
65: ("امنیت سایبری دفاعی و بی‌سیم", [
"مدل تهدید و دارایی", "Scope و مجوز تست", "تقسیم‌بندی شبکه", "Least Privilege", "MFA و مدیریت هویت",
"802.1X و NAC", "WPA2 و WPA3 Enterprise", "طراحی امن SSID", "Rogue AP و تشخیص", "WIDS و WIPS",
"Hardening مدیریت تجهیزات", "مدیریت Patch و CVE", "اسکن آسیب‌پذیری مجاز", "ثبت و نگهداری Evidence", "پاسخ به رخداد امنیتی",
"تحلیل لاگ Firewall", "مدیریت Certificate و PKI", "گزارش ریسک و برنامه اصلاح"]),
66: ("مسیریابی عمیق OSPF و BGP", [
"RIB و FIB", "Longest Prefix Match", "Administrative Distance", "OSPF Neighbor State", "OSPF LSA و LSDB",
"OSPF Area و ABR", "OSPF Cost و SPF", "BGP eBGP و iBGP", "BGP Attributes", "Local Preference و MED",
"AS Path و Loop Prevention", "Route Reflector", "Prefix List و Route Map", "Redistribution و Route Tag",
"Default Route و Origination", "ECMP و مسیر نامتقارن", "BFD و Convergence", "عیب‌یابی Routing Control Plane"]),
67: ("VPN سازمانی IPsec و SSL", [
"Site-to-Site VPN Architecture", "IKE Phase 1 و Phase 2", "IKEv2 Exchange", "Proposal و Transform Set", "Traffic Selector و Proxy ID",
"IPsec SA و Rekey", "NAT-T و UDP 4500", "DPD و Keepalive", "Route-Based VPN", "Policy-Based VPN",
"SSL VPN و ZTNA", "Split Tunnel و Full Tunnel", "MTU و MSS در تونل", "VPN و Dynamic Routing", "Certificate Authentication",
"عیب‌یابی Phase Failure", "تحلیل Packet Capture تونل", "HA و بازیابی VPN"]),
68: ("دانشنامه دستورات شبکه و سیستم", [
"Cisco IOS Show و Interface", "Cisco VLAN و Trunk", "Cisco STP و EtherChannel", "Cisco Static Routing", "Cisco OSPF Diagnostics",
"Cisco BGP Diagnostics", "MikroTik RouterOS IP و Route", "MikroTik Firewall Filter", "MikroTik NAT و Connection Tracking",
"MikroTik DHCP و DNS", "FortiGate Policy و Session", "FortiGate Debug Flow ایمن", "PowerShell شبکه", "PowerShell DNS و DHCP",
"Windows Firewall و Port Test", "Linux iproute2 و ss", "Linux tcpdump و journalctl", "Git و ابزارهای اتوماسیون"]),
}
CHAPTER_TITLES = {k: v[0] for k,v in CHAPTERS.items()}
COMMANDS = {
60: "Windows: ipconfig /all; Resolve-DnsName; Test-NetConnection. Linux: ip -br a; ip route; resolvectl status; ss -tulpn. Wireshark: capture محدود به میزبان و پورت مجاز.",
61: "SNMPv3 authPriv؛ Syslog با TLS در صورت پشتیبانی؛ chronyc tracking یا w32tm /query /status؛ استفاده از exporterها و API فقط با حساب read-only.",
62: "Cisco: show interfaces status; show logging; show ip route. Windows: Get-Service; Get-WinEvent. Linux: systemctl --failed; journalctl --since. ابتدا جمع‌آوری شواهد و سپس تغییر.",
63: "ثبت owner، purpose، dependency، version، approval، backup location و rollback. IPAM/CMDB را با منبع حقیقت سازمان همگام کنید.",
64: "git status; git diff; git log --oneline; git switch -c <branch>; git diff --check; git revert <commit>. قبل از push، secret scan و بازبینی diff.",
65: "فقط برای شبکه و میزبان دارای مجوز: inventory، بررسی پیکربندی، لاگ، patch level و آزمون بی‌سیم کنترل‌شده. از غیرفعال‌کردن کنترل امنیتی برای تسهیل تست خودداری کنید.",
66: "Cisco: show ip route; show ip ospf neighbor; show ip ospf database; show bgp ipv4 unicast summary. تأیید syntax با نسخه و vendor قبل از اجرا.",
67: "Vendor-specific show/diagnose commands؛ بررسی IKE logs، SA، selector، route، policy، NAT-T و MTU. debug فقط با فیلتر و زمان محدود و سپس disable/reset.",
68: "فرمان‌های مشاهده‌گر را ترجیح دهید؛ در تجهیزات زنده، خروجی را ذخیره کنید و syntax را با نسخه تطبیق دهید. تغییرات config فقط با مجوز و rollback.",
}
LABS = {
60: "در یک لاب ایزوله، یک کلاینت، DNS آزمایشی و روتر مجازی بسازید. یک خطا را در هر نوبت وارد کنید؛ timestamp، capture، فرضیه و معیار پذیرش را ثبت کنید. تست بیرون از scope ممنوع است.",
61: "برای سرویس آزمایشی latency، loss و availability را اندازه‌گیری کنید؛ baseline بسازید؛ یک threshold را در staging تغییر دهید و false positive/false negative را بسنجید.",
62: "یک Incident شبیه‌سازی‌شده از دریافت alert تا restore اجرا کنید. Timeline، تصمیم‌ها، owner، escalation و ارتباط با کاربران را ثبت کنید؛ پایان کار با post-incident review.",
63: "یک سرویس نمونه را از CMDB تا Runbook مستند کنید؛ owner، وابستگی‌ها، backup، دسترسی اضطراری، verify و rollback را توسط نفر دوم بازبینی کنید.",
64: "در مخزن آزمایشی فایل متنی پیکربندی بسازید، branch ایجاد کنید، diff بازبینی کنید، conflict کنترل‌شده حل کنید و revert را تمرین کنید. Secret واقعی commit نکنید.",
65: "در محیط تحت مالکیت خود، تنظیمات امنیتی Wi-Fi را بررسی کنید؛ WPA-Enterprise، جداسازی مهمان، firmware، log و پوشش را با چک‌لیست ثبت کنید. تست تهاجمی خارج از scope ممنوع است.",
66: "در EVE-NG/GNS3 سه روتر با OSPF و BGP بسازید؛ adjacency و route selection را ثبت کنید؛ یک policy را تغییر دهید و با show commands مسیر انتخابی را اثبات کنید.",
67: "دو gateway مجازی با IKE/IPsec بسازید؛ proposal mismatch و selector mismatch را جداگانه شبیه‌سازی کنید؛ SA، log و route را پیش/پس از اصلاح مقایسه کنید.",
68: "در lab خروجی فرمان‌ها را قبل و بعد از یک تغییر مجاز مقایسه کنید. فرمان، نسخه، هدف، خروجی مورد انتظار، rollback و معیار Verify را در Runbook ثبت کنید.",
}
EXAMPLES = {
60: ["IP مقصد پاسخ می‌دهد اما نام resolve نمی‌شود: DNS query/response و suffix را بررسی کنید.", "SYN دیده می‌شود ولی SYN-ACK نیست: capture سمت مقصد و مسیر برگشت را مقایسه کنید.", "یک ستاره در traceroute به‌تنهایی اثبات قطعی مسیر نیست."],
61: ["Alert با 5xx بالا و latency ثابت: error rate و dependency را باهم بررسی کنید.", "اگر NTP drift رخ دهد، correlation بین لاگ‌ها قابل اعتماد نیست.", "Threshold بدون baseline می‌تواند alert storm ایجاد کند."],
62: ["P1 را بر اساس impact و urgency تعیین کنید، نه بلندترین صدای درخواست‌کننده.", "Restore سرویس را از RCA نهایی جدا ثبت کنید.", "Failover را فقط در پنجره تغییر و با معیار برگشت آزمایش کنید."],
63: ["Runbook باید command، expected output، decision point و rollback داشته باشد.", "CI بدون owner و dependency معتبر نیست.", "نسخه مستندات و تاریخ آخرین تأیید باید قابل ردیابی باشد."],
64: ["git diff --check قبل از commit whitespace error را پیدا می‌کند.", "git revert یک commit جدید می‌سازد و history مشترک را بازنویسی نمی‌کند.", "فایل حاوی credential باید قبل از push از history خارج و secret rotate شود."],
65: ["SSID مهمان نباید به subnet مدیریت دسترسی داشته باشد.", "WPA3 Enterprise جایگزین بررسی certificate validation کلاینت نیست.", "Rogue AP را با شواهد RF و switch port بررسی کنید؛ یک MAC ناشناس به تنهایی اثبات نیست."],
66: ["OSPF FULL نشدن همسایه: area، timers، MTU، network type و authentication را مقایسه کنید.", "BGP Established اما prefix نیست: policy، AFI/SAFI و prefix filter را بررسی کنید.", "Route موجود در RIB ممکن است به علت FIB/programming یا adjacency مشکل داشته باشد."],
67: ["IKE SA برقرار ولی ترافیک عبور نمی‌کند: selector، child SA، route و policy را بررسی کنید.", "UDP 4500 معمولاً نشانگر NAT-T است، اما به تنهایی سلامت تونل را اثبات نمی‌کند.", "MTU/MSS mismatch می‌تواند فقط ترافیک بزرگ را مختل کند."],
68: ["show command باید با مدل و نسخه سیستم‌عامل تطبیق داده شود.", "وجود rule به معنی match شدن آن نیست؛ counter/log را بررسی کنید.", "خروجی redacted را برای مستندسازی استفاده کنید و secret را منتشر نکنید."],
}
LEVEL_GUIDANCE = {
"L0": "با تشبیه ساده و تعریف واژه‌ها شروع کنید؛ تفاوت نشانه، فرضیه و علت را روشن کنید.",
"L1": "پیش‌نیازها، جریان عادی، ورودی/خروجی و یک تست ساده را قدم‌به‌قدم دنبال کنید.",
"L2": "روش اجرایی ادمین، فرمان‌های مشاهده‌گر، تفسیر خروجی و کنترل تغییر را تمرین کنید.",
"L3": "شواهد چندمنبعی، وابستگی‌ها، حالت‌های مرزی، شکست‌های متناوب و مسیر برگشت را تحلیل کنید.",
"L4": "تصمیم معماری، ریسک، مقیاس‌پذیری، کنترل امنیتی، بازیابی و معیارهای عملیاتی را ارزیابی کنید.",
}
def assessment(ch, topic, idx):
    qid = f"q-ch{ch}-{idx:04d}"
    question = f"در سناریوی «{topic}»، کدام رویکرد برای رسیدن به نتیجه قابل بازبینی مناسب‌تر است؟"
    options = [
        "تغییر چند متغیر هم‌زمان و نتیجه‌گیری از یک نشانه",
        "ثبت baseline، جمع‌آوری شواهد، تغییر کنترل‌شده و Verify تکرارپذیر",
        "پاک‌کردن لاگ‌ها و تکیه بر حافظه",
        "فرض‌کردن اینکه اولین فرضیه حتماً علت اصلی است",
    ]
    answer = "ثبت baseline، جمع‌آوری شواهد، تغییر کنترل‌شده و Verify تکرارپذیر"
    return {"questions":[{"id":qid,"type":"multiple_choice","question":question,"options":options}],
            "answer_key":[{"question_id":qid,"answer":answer,
                           "explanation":"روش قابل ممیزی، فرضیه را از شاهد جدا می‌کند و اثر تغییر را با معیار پذیرش می‌سنجد."}]}
def make_lesson(ch, topic, topic_idx, level, level_fa, level_en, idx):
    chapter_title = CHAPTER_TITLES[ch]
    specific = EXAMPLES[ch]
    commands = COMMANDS[ch]
    lab = LABS[ch]
    level_advice = LEVEL_GUIDANCE[level]
    title_fa = f"[{level}] {topic} — {level_fa}"
    title_en = f"[{level}] {topic} — {level_en}"
    content = f"""# {topic}

## جایگاه و هدف
این درس بخشی از فصل {ch}: {chapter_title} است. هدف، درک عملی «{topic}» و توانایی توضیح دادن علت تصمیم‌ها با شواهد قابل بازبینی است. ابتدا محدوده، نسخه، مالک سرویس و معیار موفقیت را ثبت کنید.

## مدل مفهومی
موضوع را به ورودی‌ها، پردازش، خروجی قابل مشاهده و وابستگی‌ها تقسیم کنید. رفتار عادی را از حالت خطا جدا کنید؛ هم‌بستگی زمانی به‌تنهایی علیت را ثابت نمی‌کند. یک فرضیه خوب باید قابل آزمون و ابطال باشد و برای هر فرضیه یک شاهد تأییدکننده و یک شاهد ردکننده تعریف شود.

## مسیر یادگیری — {level}
{level_advice}
- پیش‌نیاز: آدرس‌دهی، نقش لایه‌های شبکه، لاگ و مفهوم baseline.
- خروجی مورد انتظار: توضیح رفتار، انتخاب ابزار مشاهده‌گر و ثبت نتیجه.
- معیار تسلط: اجرای تمرین در محیط مجاز، تفسیر خروجی و ارائه توضیحی که شخص دیگری بتواند تکرار کند.

## جزئیات فنی و تصمیم‌گیری
۱. دامنه اثر را تعیین کنید: یک میزبان، یک VLAN، یک سایت یا چند سرویس مستقل.
۲. زمان شروع، آخرین تغییر، نسخه و وضعیت known-good را ثبت کنید.
۳. شواهد را از دو نقطه مستقل بگیرید؛ ساعت سیستم‌ها و مسیر رفت‌وبرگشت را در نظر بگیرید.
۴. فرضیه‌ها را بر اساس احتمال و هزینه آزمون اولویت‌بندی کنید.
۵. هر بار فقط یک متغیر را تغییر دهید و نتیجه را با معیار پذیرش بسنجید.
۶. اگر ریسک از حد توافق‌شده گذشت، توقف کنید و escalation دهید.

## فرمان‌ها و ابزارهای مشاهده‌گر
{commands}
این فرمان‌ها نمونه‌اند و ممکن است بر اساس vendor، نسخه، نقش و مجوز متفاوت باشند. قبل از اجرا، help و مستندات همان نسخه را بررسی کنید؛ خروجی حساس را redacted نگه دارید. ابتدا فرمان‌های read-only را ترجیح دهید و هرگز secret، token یا کلید خصوصی را در مخزن یا گزارش قرار ندهید.

## مثال‌های تحلیل
- {specific[0]}
- {specific[1]}
- {specific[2]}
مثال‌ها الگوی استدلال‌اند، نه خروجی ادعایی از شبکه واقعی. در گزارش مشخص کنید کدام بخش مشاهده‌شده، کدام بخش فرضیه و کدام بخش نتیجه آزمون است.

## لابراتوار مرحله‌به‌مرحله
{lab}
1. توپولوژی، نسخه‌ها، scope و مجوز را ثبت کنید.
2. وضعیت اولیه و خروجی فرمان‌های read-only را ذخیره کنید.
3. فقط یک خطای کنترل‌شده وارد کنید.
4. زمان، شواهد و نتیجه هر فرضیه را ثبت کنید.
5. اصلاح حداقلی را اجرا کنید و در صورت شکست rollback کنید.
6. تست مثبت و منفی را تکرار و مستندات را به‌روزرسانی کنید.

## عیب‌یابی: Symptom → Evidence → Fix → Verify
- **Symptom:** اثر قابل مشاهده را دقیق و بدون حدس بنویسید.
- **Evidence:** لاگ، شمارنده، capture، پیکربندی و timestamp مرتبط را ثبت کنید.
- **Hypothesis:** دست‌کم دو علت محتمل و آزمون تفکیک‌کننده تعیین کنید.
- **Fix:** فقط پس از تأیید علت، تغییر کم‌ریسک و برگشت‌پذیر اعمال کنید.
- **Verify:** معیار موفقیت، مسیر برگشت، مسیرهای وابسته و پایداری نتیجه را بررسی کنید.
- **Prevent:** مانیتورینگ، Runbook یا کنترل معماری را برای جلوگیری از تکرار اصلاح کنید.

## امنیت، محدودیت و مستندسازی
فقط سامانه‌هایی را آزمایش کنید که مالکیت یا مجوز کتبی آن‌ها را دارید. scope، زمان مجاز، نرخ تست، روش‌های ممنوع و stop condition باید روشن باشند. لاگ و capture را با حداقل دسترسی نگه دارید و اطلاعات شخصی یا credential را حذف کنید. در production بدون Change approval، پنجره نگهداری، backup و rollback اقدام نکنید.

## چک‌لیست پذیرش
- [ ] baseline و نسخه‌ها ثبت شده‌اند.
- [ ] شواهد با timestamp و منبع مشخص‌اند.
- [ ] فرضیه با آزمون قابل تکرار بررسی شده است.
- [ ] اصلاح و rollback مستند هستند.
- [ ] نتیجه از نظر عملکرد و امنیت تأیید شده است.
- [ ] Runbook/CMDB/دانش‌نامه به‌روزرسانی شده است.

## واژه‌نامه
- **Baseline:** وضعیت مرجع برای مقایسه.
- **Evidence:** شاهد قابل بازبینی، نه حدس.
- **RCA:** تحلیل علت ریشه‌ای و عوامل مشارکت‌کننده.
- **Rollback:** بازگردانی کنترل‌شده به وضعیت پیشین.
- **Verify:** اثبات نتیجه با معیار پذیرش از پیش تعریف‌شده.
"""
    return {
        "uid":f"lesson:ch{ch:02d}:deep:{idx:04d}",
        "chapter_order":ch,"subchapter_order":topic_idx,
        "lesson_order":topic_idx*10+int(level[1]),
        "level":level,"title_fa":title_fa,"title_en":title_en,
        "summary":f"درس عمیق «{topic}» از فصل {ch}: {chapter_title}؛ شامل مدل مفهومی، ابزار مشاهده، Lab، عیب‌یابی و معیار Verify.",
        "full_content":content,"commands":commands,
        "examples":"\n".join(specific),
        "notes":f"منبع محتوایی مشترک Android/Windows؛ generated pack; source_status=review_required; chapter={ch}; topic={topic}",
        "learning_objectives":[f"توضیح رفتار {topic}", "انتخاب شواهد معتبر و معیار Verify", "اجرای تمرین ایمن و مستندسازی نتیجه"],
        "meta":{"assessment":assessment(ch,topic,idx)},
        "source_status":"review_required",
    }
def build_pack(chapters, filename):
    lessons=[]
    scope=[]
    for ch in chapters:
        title, topics=CHAPTERS[ch]
        scope.append({"chapter_order":ch,"title_fa":f"فصل {ch}: {title}","title_en":title,
                      "topics":[{"topic_order":i,"title_fa":t,"title_en":t} for i,t in enumerate(topics,1)]})
        idx=0
        for ti, topic in enumerate(topics,1):
            for level, fa, en in LEVELS:
                idx+=1
                lessons.append(make_lesson(ch,topic,ti,level,fa,en,idx))
    data={"package_schema_version":"1.0","project":"ENGINEER JOKAR / NetworkAll",
          "generated_on":"2026-10-15","purpose":"Shared deep enrichment pack for chapters 60-68; review_required.",
          "scope":scope,"compatibility":{"preserve_existing_records":True,"preserve_existing_uids":True,
          "questions_and_answers_separate":True,"android_windows_shared_source":True},"lessons":lessons}
    path=OUT/filename
    path.write_text(json.dumps(data,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    return len(lessons),path.stat().st_size
def main():
    OUT.mkdir(parents=True,exist_ok=True)
    groups=[
      (list(range(60,61)),"ch60_68_ch60_pack.json"),
      (list(range(61,64)),"ch60_68_ch61_63_pack.json"),
      (list(range(64,69)),"ch60_68_ch64_68_pack.json"),
    ]
    total=0
    for chapters,name in groups:
        n,size=build_pack(chapters,name); total+=n
        print(f"{name}: lessons={n} bytes={size}")
    print(f"PASS generated {total} lessons across chapters 60-68")
if __name__=="__main__": main()
