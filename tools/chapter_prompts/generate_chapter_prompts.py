#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""ایجاد پرامپت و قالب بارگذاری مستقل برای هر یک از ۶۸ فصل NetworkAll."""
from __future__ import annotations
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent
CHAPTERS = [
    [
        1,
        "مبانی IT و معماری کامپیوتر",
        "Architecture CPU RAM Bus"
    ],
    [
        2,
        "اسمبل، عیب‌یابی و سرورهای سازمانی",
        "Hardware assembly server"
    ],
    [
        3,
        "BIOS UEFI و بوت",
        "UEFI Secure Boot"
    ],
    [
        4,
        "سیستم‌عامل پایه",
        "OS process memory"
    ],
    [
        5,
        "فایل‌سیستم و Storage پایه",
        "FS RAID"
    ],
    [
        6,
        "مبانی شبکه",
        "OSI TCP/IP model"
    ],
    [
        7,
        "اترنت و سوییچینگ پایه",
        "VLAN STP"
    ],
    [
        8,
        "IPv4 IPv6 ساب‌نتینگ",
        "Subnetting routing intro"
    ],
    [
        9,
        "ARP ICMP TCP UDP",
        "L3 L4 protocols"
    ],
    [
        10,
        "DNS",
        "DNS records recursion"
    ],
    [
        11,
        "DHCP و IPAM",
        "DHCP failover IPAM"
    ],
    [
        12,
        "کابل‌کشی فیبر رک",
        "Structured cabling fiber"
    ],
    [
        13,
        "سوییچینگ سیسکو",
        "Cisco switching VTP EtherChannel"
    ],
    [
        14,
        "مسیریابی پیشرفته",
        "OSPF BGP Redistribution"
    ],
    [
        15,
        "MPLS VRF L3VPN",
        "MPLS L3VPN"
    ],
    [
        16,
        "Multicast",
        "PIM IGMP"
    ],
    [
        17,
        "EVPN VXLAN",
        "Leaf-Spine EVPN"
    ],
    [
        18,
        "SDN SD-WAN SASE",
        "SD-WAN overlay"
    ],
    [
        19,
        "MikroTik مبانی",
        "RouterOS basics"
    ],
    [
        20,
        "MikroTik Routing Firewall NAT",
        "MikroTik FW NAT"
    ],
    [
        21,
        "MikroTik QoS VPN HA",
        "MikroTik VPN HA"
    ],
    [
        22,
        "وایرلس سازمانی",
        "Enterprise WiFi"
    ],
    [
        23,
        "PtP PtMP",
        "Wireless backhaul"
    ],
    [
        24,
        "FortiGate",
        "FortiGate policy VPN"
    ],
    [
        25,
        "pfSense OPNsense Sophos",
        "Open-source firewalls"
    ],
    [
        26,
        "PKI TLS",
        "Certificates TLS"
    ],
    [
        27,
        "AAA NAC",
        "802.1X RADIUS"
    ],
    [
        28,
        "Windows Server Core",
        "Windows Server roles"
    ],
    [
        29,
        "Active Directory",
        "AD DS GPO"
    ],
    [
        30,
        "Windows DNS DHCP NPS",
        "MS network services"
    ],
    [
        31,
        "فایل چاپ DFS",
        "File server DFS"
    ],
    [
        32,
        "امنیت Endpoint ویندوز",
        "Windows hardening"
    ],
    [
        33,
        "Entra ID Hybrid",
        "Azure AD hybrid"
    ],
    [
        34,
        "M365 Intune ایمیل",
        "M365 Intune"
    ],
    [
        35,
        "PowerShell CMD",
        "PowerShell automation"
    ],
    [
        36,
        "مدیریت لینوکس",
        "Linux admin"
    ],
    [
        37,
        "شبکه لینوکس",
        "Linux networking"
    ],
    [
        38,
        "سرویس لینوکس وب",
        "Nginx Apache"
    ],
    [
        39,
        "امنیت لینوکس",
        "Linux security"
    ],
    [
        40,
        "VMware Hyper-V",
        "Virtualization"
    ],
    [
        41,
        "Proxmox Docker",
        "Proxmox containers"
    ],
    [
        42,
        "Kubernetes",
        "K8s networking"
    ],
    [
        43,
        "شبکه ابری",
        "VPC cloud networking"
    ],
    [
        44,
        "امنیت ابر Governance",
        "Cloud security"
    ],
    [
        45,
        "Storage سازمانی",
        "SAN NAS"
    ],
    [
        46,
        "Backup DR",
        "Backup DR"
    ],
    [
        47,
        "Data Center",
        "DC design"
    ],
    [
        48,
        "HA و Load Balancing",
        "HA LB"
    ],
    [
        49,
        "مانیتورینگ",
        "SNMP Prometheus"
    ],
    [
        50,
        "SIEM ELK",
        "SIEM SOC tools"
    ],
    [
        51,
        "اتوماسیون و AI در IT",
        "Ansible Python AIOps"
    ],
    [
        52,
        "مدیریت دیتابیس",
        "DBA basics"
    ],
    [
        53,
        "امنیت دیتابیس",
        "DB security"
    ],
    [
        54,
        "VoIP سانترال",
        "VoIP QoS"
    ],
    [
        55,
        "CCTV Access BMS IoT",
        "Physical security IoT"
    ],
    [
        56,
        "امنیت پایه Zero Trust ITIL",
        "Zero Trust ITIL"
    ],
    [
        57,
        "امنیت شبکه",
        "Network security"
    ],
    [
        58,
        "Endpoint AppSec DevSecOps",
        "AppSec"
    ],
    [
        59,
        "SOC IR Hunting",
        "SOC IR"
    ],
    [
        60,
        "عیب‌یابی هک اخلاقی لاب سازمانی",
        "Authorized labs only"
    ],
    [
        61,
        "معماری سازمانی Enterprise Architecture",
        "EA"
    ],
    [
        62,
        "عملیات IT و NOC",
        "NOC ops"
    ],
    [
        63,
        "مستندسازی Runbook و CMDB",
        "Runbook CMDB"
    ],
    [
        64,
        "Git و کنترل نسخه",
        "Git"
    ],
    [
        65,
        "امنیت سایبری و هک اخلاقی دفاعی + وایرلس",
        "Defensive security wireless"
    ],
    [
        66,
        "مسیریابی عمیق OSPF/BGP/Redistribution",
        "Deep routing"
    ],
    [
        67,
        "VPN سازمانی IPsec/SSL",
        "Enterprise VPN"
    ],
    [
        68,
        "دانشنامه جامع دستورات",
        "Cisco MikroTik FortiGate Issabel PowerShell"
    ]
]
COMMON = """حداقل 50 مثال مستقل، 50 سناریوی مستقل، 50 سؤال آزمون، answer_key جدا با ID مشترک، نمودار برای تمام مباحث اصلی، لاب امن، منابع رسمی دقیق، پوشش L0-L4 و rollback. محتوای موجود را حذف یا overwrite نکن؛ داده یا منبع ساختگی نساز."""

MASTER_RULES = """حداقل‌های هر فصل: ۵۰ مثال مستقل، ۵۰ سناریوی کامل و مستقل، ۵۰ سؤال آزمون با answer_key مجزا، نمودار اختصاصی برای هر مبحث اصلی، پوشش L0 تا L4، منابع رسمی دقیق، UID پایدار، آزمایشگاه ایمن و روش rollback. هیچ محتوای فعلی حذف یا جایگزین نشود و منبع یا خروجی ساختگی تولید نشود."""

def body(n: int, title: str, kw: str) -> str:
    cid = f"{n:02d}"
    special = ""
    if n == 68:
        special = """
## الزامات اختصاصی فصل ۶۸
درخت جداگانه برای Linux، Bash، PowerShell، Windows CMD، Windows Batch، Cisco IOS/IOS-XE، MikroTik RouterOS، FortiGate/FortiOS و Issabel/Asterisk بساز. نحو پلتفرم‌ها را با هم مخلوط نکن. هر دستور باید نسخه و پلتفرم، سطح دسترسی، syntax، آرگومان‌ها، پیش‌نیاز، مراحل اجرا، خروجی نمونه و تفسیر، خطاهای متداول، امنیت، فرمان‌های مرتبط، لاب و ارزیابی داشته باشد.
"""
    return f"""# پرامپت قابل بارگذاری — فصل {cid}: {title}

مخزن هدف: https://github.com/MrUtility01/NetworkAll
شماره فصل: {n}
عنوان مطابق فهرست curriculum: {title}
کلیدواژه‌های شروع: {kw}

## مأموریت
محتوای فعلی فصل را از نظر ارتباط عنوان و متن، عمق، پوشش سطح‌های L0 تا L4، تکرار و شکاف‌ها ممیزی کن. ابتدا گزارش شکاف و طرح درس‌ها را تهیه کن؛ سپس فقط محتوای یکتا و افزایشی تولید کن. هیچ درس، UID، قابلیت برنامه یا دادهٔ فعلی حذف/بازنویسی نشود.

## معیارهای غنا
{MASTER_RULES}

- هر مثال شامل مسئله، ورودی/فرمان، مراحل، خروجی مورد انتظار و تفسیر نتیجه باشد.
- هر سناریو شامل محیط سازمانی، هدف یا علامت خرابی، محدودیت‌ها، شواهد، تحلیل، اصلاح، روش Verify و Rollback/درس‌آموخته باشد.
- حداقل ۵۰ سؤال متنوع برای کل فصل بساز؛ صورت سؤال و گزینه‌ها نباید پاسخ صحیح را لو بدهند. پاسخ‌نامه با همان IDهای پایدار و توضیح فارسی در فایل جدا باشد.
- برای هر مفهوم اصلی، نمودار اختصاصی و معنادار تولید کن: Mermaid source، SVG، manifest شامل شناسه/عنوان/lesson_uid و متن جایگزین. نمودار تکراری یا تزئینی ممنوع.
- برای هر مبحث اصلی لابراتوار قابل تکرار، پیش‌نیازها، دادهٔ آزمایش، گام‌ها، خروجی، اعتبارسنجی، پاک‌سازی و rollback بنویس.
- حداقل ۱۰ منبع رسمی و دقیق متناسب با حوزه و نسخه ثبت کن؛ URL، شماره نسخه، منبع یا خروجی ساختگی ممنوع.
- هر درس مثل فصل کتاب از صفر تا تخصص نوشته شود: مدل ذهنی، معماری، جریان اجرا، موارد کاربرد/عدم کاربرد، مثال حل‌شده، خطاهای رایج، RCA، امنیت، rollback، checklist، خلاصه و واژه‌نامه.
- آزمایشگاه فقط برای محیط مجاز و تحت مالکیت/اجازه باشد.
{special}
## قرارداد هر lesson
فیلدهای لازم: uid، chapter_order={n}، subchapter_order، lesson_order، level، title_fa، title_en، topic، summary، full_content، commands، examples، notes، learning_objectives، meta و source_status. محتوای جدید با source_status برابر review_required علامت‌گذاری شود تا پس از بازبینی انسانی تغییر کند.

## خروجی‌های اجباری
۱. ch{cid}_pack.json: package_schema_version=1، project=ENGINEER JOKAR / NetworkAll، chapter_order={n} و lessons سازگار با importer فعلی.
۲. ch{cid}_answer_key.json: پاسخ و دلیل پاسخ با ID یکسان با سؤال‌ها.
۳. ch{cid}_scenarios.json: حداقل ۵۰ سناریوی ساختاریافته و یکتا.
۴. diagrams/ch{cid}/manifest.json به همراه فایل‌های SVG و source.
۵. VALIDATION.md: شمار واقعی درس/مثال/سناریو/سؤال/پاسخ/نمودار، UIDهای یکتا، تطبیق سؤال/پاسخ، منابع و موارد نیازمند بازبینی.

بستهٔ اصلی در tools/packs/ch{cid}/ ذخیره شود. JSON ناقص، placeholder، سه‌نقطه، رکورد تکراری یا منبع جعلی تحویل نده. تا زمانی که loader سناریو/نمودار پیاده‌سازی و آزمایش نشده، این دارایی‌های جداگانه را به عنوان محتوای قابل مشاهده در UI معرفی نکن.
"""

def template(n: int, title: str) -> dict:
    if n == 68:
        return {
            "package_schema_version": 1,
            "project": "ENGINEER JOKAR / NetworkAll",
            "generated_on": "YYYY-MM-DD",
            "purpose": "دانشنامه فرمان فصل ۶۸ بر اساس پلتفرم و سازنده",
            "chapter_order": 68,
            "chapter_title_fa": title,
            "commands": [],
            "compatibility": {"preserve_existing_records": True, "preserve_existing_uids": True}
        }
    return {
        "package_schema_version": 1,
        "project": "ENGINEER JOKAR / NetworkAll",
        "generated_on": "YYYY-MM-DD",
        "purpose": f"بستهٔ افزایشی آموزشی فصل {n}: {title}",
        "scope": [{"chapter_order": n, "subchapter_order": 1, "title": title, "topics": []}],
        "compatibility": {
            "preserve_existing_records": True,
            "preserve_existing_uids": True,
            "questions_and_answers_separate": True
        },
        "lessons": []
    }

def main() -> None:
    rows = [
        "# فهرست درختی پرامپت‌های فصل NetworkAll",
        "",
        "| فصل | عنوان | پرامپت قابل بارگذاری | قالب JSON |",
        "|---:|---|---|---|"
    ]
    for n, title, kw in CHAPTERS:
        cid = f"{n:02d}"
        folder = ROOT / f"ch{cid}"
        folder.mkdir(parents=True, exist_ok=True)
        (folder / "PROMPT.md").write_text(body(n, title, kw), encoding="utf-8")
        (folder / "README.md").write_text(
            f"# فصل {cid} — {title}\n\n"
            f"پرامپت قابل بارگذاری: [PROMPT.md](PROMPT.md)\n\n"
            f"قالب اولیه: [PACK_TEMPLATE.json](PACK_TEMPLATE.json)\n\n"
            f"بستهٔ واقعی را پس از بازبینی زیر tools/packs/ch{cid}/ ذخیره کن.\n",
            encoding="utf-8"
        )
        (folder / "PACK_TEMPLATE.json").write_text(
            json.dumps(template(n, title), ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8"
        )
        rows.append(
            f"| {n} | {title} | [PROMPT.md](ch{cid}/PROMPT.md) | "
            f"[PACK_TEMPLATE.json](ch{cid}/PACK_TEMPLATE.json) |"
        )
    (ROOT / "INDEX.md").write_text("\n".join(rows) + "\n", encoding="utf-8")
    print(f"تولید شد: {len(CHAPTERS)} پوشهٔ مستقل فصل‌ها")

if __name__ == "__main__":
    main()
