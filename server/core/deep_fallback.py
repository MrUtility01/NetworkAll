# -*- coding: utf-8 -*-
"""موتور محتوای عمیق و ملموس برای هر درسی که teacher اختصاصی ندارد.
هر درس شامل: داستان واقعی سازمانی، معماری، فریم‌به‌فریم، دستورات چندوندر،
Lab عملی، جدول RCA، امنیت، چک‌لیست Production و جمع‌بندی استاد.
"""
from __future__ import annotations
import re
from typing import Any, Dict, List, Tuple
from core.rich_data import BANKS, COMMON, ERRORS, SCENARIO_HOOKS

_LEVEL_FA = {
    "L0": "آشنایی / تصویر ذهنی",
    "L1": "Junior — مشاهده و Lab ساده",
    "L2": "Administrator — پیکربندی + Verify + Rollback",
    "L3": "Engineer / Senior — طراحی و RCA",
    "L4": "Architect — سازمانی، چندسایت، Change Control",
}

_CATS: List[Tuple[str, List[str]]] = [
    ("powershell", ["powershell", "cmdlet", "psremoting", "winrm", "execution policy", "پاورشل"]),
    ("firmware", ["bios", "uefi", "secure boot", "tpm", "boot order", "grub", "pxe"]),
    ("hardware", ["cpu", "processor", "ram", "memory", "motherboard", "chipset", "esd", "post", "no power", "server hardware", "پردازنده", "مادربرد", "حافظه", "اسمبل", "سخت‌افزار", "خمیر حرارتی"]),
    ("git", ["git ", "github", "گیت", "repository", "rebase", "pull request", "merge request"]),
    ("cloud", ["azure", "aws", "cloud", "security group", "vpc", "vnet", "ابر"]),
    ("backup", ["backup", "restore", "recovery", "بکاپ", "پشتیبان‌گیری", "بازیابی"]),
    ("monitoring", ["monitoring", "zabbix", "prometheus", "grafana", "alert", "مانیتورینگ"]),
    ("voip", ["voip", "sip", "rtp", "تماس یک‌طرفه", "کیفیت تماس"]),
    ("soc", ["siem", "soc", "edr", "incident response", "همبستگی لاگ"]),
    ("vlan", ["vlan", "trunk", "access", "802.1q", "native vlan", "svi"]),
    ("stp", ["stp", "spanning", "rstp", "bpdu", "root bridge", "portfast", "loop"]),
    ("ospf", ["ospf", "area", "lsa", "neighbor", "dr", "bdr", "cost"]),
    ("bgp", ["bgp", "prefix-list", "route-map", "as number", "ebgp", "ibgp", "peering"]),
    ("acl", ["acl", "access-list", "extended", "standard", "named acl"]),
    ("nat", ["nat", "pat", "overload", "static nat", "port forward"]),
    ("vpn", ["vpn", "ipsec", "ike", "tunnel", "phase1", "phase2", "ssl vpn"]),
    ("dhcp", ["dhcp", "scope", "lease", "relay", "helper", "dora", "reservation"]),
    ("dns", ["dns", "resolver", "zone", "forwarder", "dnssec", "split-horizon"]),
    ("wireless", ["wifi", "wireless", "ssid", "wpa", "wlc", "roaming", "ap"]),
    ("firewall", ["firewall", "fortigate", "asa", "policy", "zone"]),
    ("ha", ["hsrp", "vrrp", "glbp", "failover", "active-standby"]),
    ("qos", ["qos", "dscp", "policing", "shaping", "priority"]),
    ("linux", ["linux", "iptables", "nftables", "systemd", "journalctl", "ss "]),
    ("windows", ["windows", "powershell", "gpo", "active directory", "kerberos"]),
    ("storage", ["raid", "nvme", "ssd", "san", "iscsi", "latency", "iops"]),
    ("virtualization", ["vmware", "esxi", "kubernetes", "docker", "pod", "hypervisor"]),
    ("security", ["aaa", "radius", "tacacs", "tls", "snmp", "802.1x", "port security"]),
    ("tcpip", ["tcp", "udp", "icmp", "handshake", "window", "retransmission"]),
    ("mpls", ["mpls", "ldp", "label", "vrf", "l3vpn", "pe ", "ce "]),
    ("multicast", ["multicast", "pim", "igmp", "ssm", "rendezvous"]),
    ("vxlan", ["vxlan", "vni", "vtep", "evpn", "overlay", "underlay"]),
    ("sql", ["sql", "postgres", "mysql", "elasticsearch"]),
    ("python", ["python", "paramiko", "netmiko", "scrapli"]),
    ("ansible", ["ansible", "playbook", "inventory"]),
    ("terraform", ["terraform", "iac", "provider"]),
]


def _level(title: str) -> str:
    m = re.match(r"\[(L[0-4])\]", title or "")
    return m.group(1) if m else "L0"


def _topic(title: str) -> str:
    t = re.sub(r"^\[L[0-4]\]\s*", "", title or "").strip()
    t = re.sub(
        r"\s*[—\-]\s*(آشنایی|مقدماتی|ادمین|مهندس|خبره|Intro|Junior|Admin|Senior|Architect).*$",
        "",
        t,
        flags=re.I,
    )
    return t.strip() or (title or "موضوع")


def _cat(topic: str) -> str:
    t = topic.lower()
    for c, keys in _CATS:
        if any(k in t for k in keys):
            return c
    return "general"


def _fmt(pairs: List[Tuple[str, str]]) -> str:
    return "\n".join(f"```\n{cmd}\n```\n→ {desc}\n" for cmd, desc in pairs)


def _story(topic: str, cat: str) -> str:
    specific = {
        "hardware": f"یک ایستگاه کاری دچار reboot تصادفی شده است. قبل از تعویض قطعه باید شواهد SMART، RAM، دما، firmware و Event Log جمع شود؛ تعویض حدسی هزینه و زمان را بالا می‌برد.",
        "firmware": f"پس از تغییر UEFI، دستگاه بوت نمی‌شود و BitLocker Recovery ظاهر می‌شود. مهندس باید ترتیب بوت، Secure Boot، TPM و recovery key را بدون پاک‌کردن داده بررسی کند.",
        "powershell": f"تیم پشتیبانی باید وضعیت صدها سیستم را تکرارپذیر جمع‌آوری کند؛ اسکریپت باید ورودی را اعتبارسنجی کند، خطاها را ثبت کند و روی سیستم واقعی تغییر ناخواسته ندهد.",
        "git": f"چند نفر هم‌زمان روی یک پروژه کار می‌کنند. هدف این است که تاریخچه تغییرات قابل بازبینی باشد، conflictها حل شوند و فایل محرمانه وارد commit نشود.",
        "cloud": f"یک سرویس ابری به‌دلیل IAM یا network rule در دسترس نیست. شواهد باید از policy، route، log و هزینه بررسی شود؛ تغییر مستقیم روی محیط production ممنوع است.",
        "backup": f"بعد از خرابی، فایل backup موجود است اما هنوز restore آن اثبات نشده. هدف، سنجش RPO/RTO و بررسی صحت داده در محیط جداگانه است.",
        "monitoring": f"هشدارهای زیاد باعث شده تیم NOC هشدار مهم را از دست بدهد. باید baseline، threshold، correlation و runbook سنجیده شود.",
        "voip": f"کاربر صدا را می‌شنود اما صدایش به طرف مقابل نمی‌رسد. signaling، مسیر RTP، NAT و ACL باید جداگانه با شواهد بررسی شوند.",
        "soc": f"چند رخداد امنیتی نزدیک به هم دیده شده‌اند. تحلیل‌گر باید timeline و evidence را حفظ کند و فرضیه را از واقعیت جدا کند.",
        "windows": f"یک سرویس Windows پس از تغییر GPO برای بخشی از کاربران از کار افتاده است. باید policy مؤثر، service state و Event Log را با یک میزبان سالم مقایسه کرد.",
        "linux": f"یک سرویس Linux بعد از به‌روزرسانی شروع نمی‌شود. مهندس باید dependency، systemd unit، journal و permission را بررسی کند و پیش از تغییر وضعیت اولیه را ثبت کند.",
        "python": f"یک اسکریپت مدیریتی در برخی ورودی‌ها شکست می‌خورد. باید خطا بازتولید، ورودی اعتبارسنجی، exception ثبت و رفتار با unit test اثبات شود.",
        "sql": f"گزارش پایگاه داده کند شده یا نتیجهٔ غیرمنتظره دارد. باید correctness، query plan، index و transaction جداگانه بررسی شوند.",
        "storage": f"سامانه با افزایش latency دیسک روبه‌رو شده است. فضای آزاد، سلامت رسانه، controller، queue و latency باید مستقل اندازه‌گیری شوند.",
        "virtualization": f"یک ماشین مجازی کند شده است. باید host contention، virtual switch، storage latency و وضعیت guest با هم مقایسه شوند.",
    }
    if cat in specific:
        return specific[cat]
    hooks = SCENARIO_HOOKS.get(cat, SCENARIO_HOOKS.get("general", []))
    if hooks:
        return hooks[0]
    return (
        f"یک تیم IT با مشکل مرتبط با «{topic}» روبه‌رو شده است. پیش از تغییر، "
        f"باید محدودهٔ اثر، زمان شروع، تغییرات اخیر و شواهد قابل تکرار را ثبت کند؛ "
        f"سپس فرضیه را در محیط آزمایشی بیازماید و معیار موفقیت و rollback داشته باشد."
    )


def _arch_table(cat: str) -> str:
    specific = {
        "hardware": "| جزء | نقش |\n|---|---|\n| CPU | اجرای دستورها و پردازش |\n| RAM | حافظهٔ فرّار و working set |\n| Storage | دوام داده و I/O |\n| Firmware | POST، بوت و کنترل سخت‌افزار |\n| Thermal/Power | پایداری و محدودیت توان/دما |",
        "firmware": "| جزء | نقش |\n|---|---|\n| UEFI | رابط firmware و OS |\n| Secure Boot | زنجیره اعتماد بوت |\n| TPM | حفاظت کلید/اندازه‌گیری |\n| Boot Manager | انتخاب loader |\n| Recovery Key | بازیابی رمزگذاری |",
        "powershell": "| جزء | نقش |\n|---|---|\n| Pipeline | انتقال object بین cmdletها |\n| Provider | دسترسی به filesystem/registry |\n| Module | بستهٔ command/function |\n| Error stream | خطاهای terminating/non-terminating |\n| Remoting | اجرای مدیریت‌شده روی host دور |",
        "git": "| جزء | نقش |\n|---|---|\n| Working tree | فایل‌های در حال ویرایش |\n| Index | staging area |\n| Commit | snapshot تاریخچه |\n| Branch | مسیر مستقل تغییرات |\n| Remote | مخزن مشترک |",
        "cloud": "| جزء | نقش |\n|---|---|\n| IAM | هویت و مجوز |\n| VPC/VNet | مرز شبکه مجازی |\n| Security group | فیلتر ترافیک |\n| Control plane | ساخت/مدیریت resource |\n| Audit/Flow log | شواهد و حسابرسی |",
        "backup": "| جزء | نقش |\n|---|---|\n| Source | دادهٔ اصلی |\n| Backup set | نسخهٔ بازیابی |\n| Retention | نگهداری نسخه‌ها |\n| RPO/RTO | هدف نقطه/زمان بازیابی |\n| Restore test | اثبات قابلیت بازیابی |",
        "monitoring": "| جزء | نقش |\n|---|---|\n| Metric | عدد زمان‌مند |\n| Log | رخداد جزئی |\n| Trace | مسیر یک درخواست |\n| Threshold | شرط هشدار |\n| Runbook | اقدام استاندارد |",
        "voip": "| جزء | نقش |\n|---|---|\n| SIP | signaling تماس |\n| RTP/SRTP | media |\n| Codec | فشرده‌سازی صدا |\n| SBC/NAT | مرز و عبور رسانه |\n| QoS | اولویت‌دادن به voice |",
        "soc": "| جزء | نقش |\n|---|---|\n| SIEM | همبستگی رخدادها |\n| EDR | telemetry endpoint |\n| IOC | نشانه قابل جستجو |\n| Timeline | ترتیب شواهد |\n| Playbook | اقدام کنترل‌شده |",
        "windows": "| جزء | نقش |\\n|---|---|\\n| Service Control Manager | مدیریت سرویس‌ها |\\n| Event Log | شواهد رخداد |\\n| GPO | سیاست پیکربندی |\\n| Identity/ACL | هویت و مجوز |\\n| PowerShell | مشاهده و اتوماسیون |",
        "linux": "| جزء | نقش |\\n|---|---|\\n| Kernel | منابع و syscallها |\\n| systemd | مدیریت سرویس |\\n| journal | شواهد رخداد |\\n| filesystem/permissions | داده و مجوز |\\n| package manager | چرخهٔ نصب/به‌روزرسانی |",
        "python": "| جزء | نقش |\\n|---|---|\\n| Input contract | شکل ورودی |\\n| Function/module | منطق قابل آزمون |\\n| Exception | مدیریت شکست |\\n| Test suite | قرارداد رفتاری |\\n| Packaging/venv | محیط تکرارپذیر |",
        "sql": "| جزء | نقش |\\n|---|---|\\n| Schema/constraints | ساختار و صحت داده |\\n| Query planner | انتخاب مسیر اجرا |\\n| Index | مسیر دسترسی |\\n| Transaction | اتمی‌بودن تغییر |\\n| Backup/restore | بازیابی داده |",
        "storage": "| جزء | نقش |\\n|---|---|\\n| Media | نگهداری داده |\\n| Controller/path | مسیر I/O |\\n| Filesystem/volume | سازمان‌دهی داده |\\n| Queue/latency | عملکرد I/O |\\n| Backup/checksum | صحت و بازیابی |",
        "virtualization": "| جزء | نقش |\\n|---|---|\\n| Host/hypervisor | تخصیص منابع |\\n| Guest VM | سیستم‌عامل مهمان |\\n| vSwitch | شبکهٔ مجازی |\\n| Datastore | ذخیره‌سازی VM |\\n| Snapshot/backup | بازگشت و بازیابی |",
    }
    if cat in specific:
        return specific[cat]
    tables = {
        "vlan": "| جزء | نقش |\n|-----|-----|\n| Access Port | یک VLAN به کلاینت |\n| Trunk | چند VLAN با تگ 802.1Q |\n| Native VLAN | بدون تگ روی trunk |\n| SVI | gateway لایه ۳ همان VLAN |\n| VTP/Manual | توزیع یا مدیریت محلی VLAN |",
        "stp": "| جزء | نقش |\n|-----|-----|\n| Root Bridge | مرجع توپولوژی |\n| Root Port | نزدیک‌ترین به Root |\n| Designated Port | مسئول سگمنت |\n| Blocking/Alternate | جلوگیری از loop |\n| BPDU | سیگنال کنترل |",
        "ospf": "| جزء | نقش |\n|-----|-----|\n| Area 0 | Backbone |\n| Neighbor | adjacency |\n| LSA | تبلیغ توپولوژی |\n| DR/BDR | کاهش flooding در multi-access |\n| Cost | معیار مسیر |",
        "bgp": "| جزء | نقش |\n|-----|-----|\n| AS | دامنه سیاست |\n| eBGP / iBGP | بین/داخل AS |\n| Prefix-list | فیلتر پیشوند |\n| Route-map | سیاست |\n| Next-hop | مقصد بعدی |",
        "dhcp": "| جزء | نقش |\n|-----|-----|\n| DORA | Discover→Offer→Request→Ack |\n| Scope | محدوده آدرس |\n| Relay | عبور درخواست بین VLAN |\n| Reservation | آدرس ثابت برای دستگاه |\n| Lease | مدت اعتبار |",
        "dns": "| جزء | نقش |\n|-----|-----|\n| Resolver | کلاینت پرسشگر |\n| Recursive | جستجوی کامل |\n| Authoritative | منبع حقیقت zone |\n| Forwarder | هدایت به بالادست |\n| Split-Horizon | پاسخ متفاوت داخل/خارج |",
        "vpn": "| جزء | نقش |\n|-----|-----|\n| Phase 1 (IKE) | کانال امن کنترل |\n| Phase 2 (IPsec) | تونل داده |\n| SA | Security Association |\n| PSK / Cert | احراز هویت |\n| PFS | Perfect Forward Secrecy |",
        "firewall": "| جزء | نقش |\n|-----|-----|\n| Zone | گروه‌بندی امنیتی |\n| Policy | قانون عبور |\n| NAT | ترجمه آدرس |\n| Session | وضعیت اتصال |\n| Logging | ثبت رویداد |",
    }
    return tables.get(
        cat,
        "| جزء | نقش |\n|-----|-----|\n| Control plane | تصمیم و سیگنالینگ |\n| Data plane | عبور ترافیک |\n| Management plane | پیکربندی و لاگ |\n| Policy / AAA | مجوز و حسابرسی |",
    )


def _frame_steps(cat: str) -> str:
    specific = {
        "hardware": "1. علائم و زمان وقوع را ثبت کن\n2. بررسی power/thermal و event log\n3. خواندن وضعیت RAM و SMART بدون تست مخرب\n4. یک قطعه/متغیر را در هر بار تغییر بده\n5. آزمون پایداری و مقایسه با baseline",
        "firmware": "1. وضعیت فعلی و Recovery Key را ثبت کن\n2. Boot mode و firmware version را بررسی کن\n3. یک گزینه را در محیط آزمایشی تغییر بده\n4. cold boot و OS boot را تأیید کن\n5. مقدار قبلی و مسیر recovery را مستند کن",
        "powershell": "1. پارامترها و permission را اعتبارسنجی کن\n2. cmdlet مشاهده‌ای را اجرا کن\n3. object pipeline را فیلتر و select کن\n4. خطاها و exit state را مدیریت کن\n5. خروجی قابل‌تکرار و transcript بساز",
        "git": "1. status و branch فعلی را ببین\n2. تغییر کوچک و diff را بررسی کن\n3. commit مستقل بساز\n4. branch را با base مقایسه کن\n5. conflict یا rollback را در Lab تمرین کن",
        "cloud": "1. scope، region و هزینه را مشخص کن\n2. IAM و network policy را بررسی کن\n3. plan را قبل از apply بازبینی کن\n4. log و دسترسی مجاز/غیرمجاز را تست کن\n5. منابع Lab را پاک کن",
        "backup": "1. baseline و checksum بساز\n2. backup را در محل جدا ایجاد کن\n3. integrity نسخه را بررسی کن\n4. restore را در محیط جدا انجام بده\n5. RPO/RTO و نتیجه را ثبت کن",
        "monitoring": "1. baseline جمع کن\n2. metric/log/trace مناسب انتخاب کن\n3. threshold و suppression را تنظیم کن\n4. failure کنترل‌شده بساز\n5. alert، evidence و runbook را تأیید کن",
        "voip": "1. endpoint و مسیر تماس را مشخص کن\n2. SIP registration و call setup را بررسی کن\n3. مسیر RTP و NAT را اندازه بگیر\n4. jitter/loss/latency را ثبت کن\n5. تماس دوطرفه و کیفیت را تأیید کن",
        "soc": "1. زمان‌ها را به UTC نرمال کن\n2. شواهد خام را حفظ و hash کن\n3. timeline و query correlation بساز\n4. hypothesis را با negative control تست کن\n5. containment و معیار خاتمه را مستند کن",
        "windows": "1. Service state و وابستگی‌ها را بخوان\\n2. Event Log را در بازهٔ زمانی رخداد بررسی کن\\n3. GPO مؤثر و دسترسی حساب را مقایسه کن\\n4. تغییر را روی میزبان آزمایشی اعمال کن\\n5. سرویس و سناریوی کاربر را دوباره تأیید کن",
        "linux": "1. systemctl status را بخوان\\n2. journalctl را برای همان بازه بررسی کن\\n3. dependency، permission و فضای دیسک را بررسی کن\\n4. یک تغییر کنترل‌شده اعمال کن\\n5. health check و log را پس از تغییر مقایسه کن",
        "python": "1. نسخه و dependencyها را ثبت کن\\n2. خطا را با ورودی حداقلی بازتولید کن\\n3. تابع و exception را بررسی کن\\n4. unit test برای حالت عادی/مرزی/نامعتبر اضافه کن\\n5. کل suite و compileall را اجرا کن",
        "sql": "1. query و پارامتر را ثبت کن\\n2. نتیجه و constraint را تأیید کن\\n3. EXPLAIN / query plan را بررسی کن\\n4. index یا migration را روی کپی بسنج\\n5. transaction rollback و integrity check را اجرا کن",
        "storage": "1. health status و فضای آزاد را بخوان\\n2. latency و queue را اندازه بگیر\\n3. controller/path و event log را بررسی کن\\n4. تست را فقط روی volume آزمایشی اجرا کن\\n5. checksum و سلامت داده را پس از restore تأیید کن",
        "virtualization": "1. host resource contention را بررسی کن\\n2. guest CPU/RAM و driverها را مقایسه کن\\n3. vSwitch و datastore latency را بررسی کن\\n4. یک تغییر در VM آزمایشی اعمال کن\\n5. workload و log را پیش/پس مقایسه کن",
    }
    if cat in specific:
        return specific[cat]
    steps = {
        "vlan": "1. تعریف VLAN روی سوییچ\n2. پورت access به VLAN اختصاص\n3. trunk بین سوییچ‌ها (allowed VLAN)\n4. SVI برای gateway (اگر L3)\n5. تست پینگ داخل VLAN و بین VLAN",
        "stp": "1. انتخاب Root Bridge (اولویت)\n2. محاسبه مسیر Root Port\n3. انتخاب Designated در هر سگمنت\n4. Block کردن لینک‌های اضافی\n5. در صورت تغییر توپولوژی: reconvergence",
        "ospf": "1. فعال‌سازی OSPF روی اینترفیس\n2. Hello → 2-Way → ExStart → Exchange → Full\n3. تبادل LSA\n4. محاسبه SPF\n5. نصب مسیر در جدول مسیریابی",
        "dhcp": "1. کلاینت Discover (broadcast)\n2. سرور Offer\n3. کلاینت Request\n4. سرور Ack + Lease\n5. Renewal در ۵۰٪ و ۸۷٫۵٪ عمر Lease",
        "dns": "1. کلاینت به Resolver محلی\n2. اگر cache نبود → Recursive به Root/TLD/Authoritative\n3. پاسخ + TTL\n4. ذخیره در cache\n5. در Split-Horizon: پاسخ بر اساس منبع پرسش",
        "vpn": "1. IKE Phase1 (Main/Aggressive) → ISAKMP SA\n2. IKE Phase2 → IPsec SA\n3. ترافیک جفت می‌شود (interesting traffic)\n4. رمزنگاری و ارسال\n5. Keepalive / DPD برای تشخیص قطع",
    }
    return steps.get(
        cat,
        "1. Backup پیکربندی فعلی\n2. تعیین دامنه تغییر (دستگاه / VLAN / VRF)\n3. پیکربندی حداقلی\n4. Verify محلی\n5. Verify End-to-End\n6. بررسی لاگ\n7. Rollback اگر شکست",
    )


def _lab_concrete(topic: str, cat: str, level: str) -> str:
    if cat == "hardware":
        return f"""# آزمایشگاه سخت‌افزار — {topic}

- فقط از سیستم آزمایشی استفاده کن؛ قطعات را هنگام روشن‌بودن جابه‌جا نکن و ESD را رعایت کن.
- مشخصات CPU، RAM، دیسک، BIOS/UEFI و دمای idle را ثبت کن.
- در Windows اجرا کن:
  Get-CimInstance Win32_Processor | Select-Object Name,NumberOfCores,NumberOfLogicalProcessors
  Get-CimInstance Win32_PhysicalMemory | Select-Object Capacity,Speed,Manufacturer
  Get-PhysicalDisk | Select-Object FriendlyName,HealthStatus,OperationalStatus,Size
- یک تغییر واحد انجام بده و پیش/پس از تغییر را مقایسه کن.
- معیار قبولی: سخت‌افزار شناسایی شود، خطای جدید ثبت نشود و سلامت در محدوده سازنده باشد.
"""
    if cat == "firmware":
        return f"""# آزمایشگاه BIOS/UEFI — {topic}

- روی VM یا سیستم آزمایشی، Boot Order، Secure Boot، TPM و وضعیت BitLocker را ثبت کن.
- از msinfo32، Confirm-SecureBootUEFI، Get-Tpm و bcdedit /enum برای مشاهده استفاده کن.
- قبل از تغییر boot/TPM، Recovery Key را در محل امن و آفلاین نگه دار.
- فقط یک گزینه را تغییر بده و بوت سرد/گرم را آزمایش کن؛ در صورت شکست به مقدار ثبت‌شده برگرد.
"""
    if cat == "powershell":
        return f"""# PowerShell Lab — {topic}

- در VM یا محیط غیرتولیدی اجرا کن.
- ابتدا Get-Help Get-NetIPConfiguration -Examples و Get-Command *NetAdapter را بررسی کن.
- اجرا کن: Get-NetIPConfiguration; Get-NetAdapter; Get-Service; Test-NetConnection localhost -Port 135
- خروجی و خطاها را ثبت کن؛ معیار قبولی این است که دستورها فقط وضعیت را مشاهده کنند و تغییر ناخواسته ندهند.
"""
    if cat == "git":
        return f"""# Git Lab — {topic}

- یک پوشه آزمایشی خالی بساز؛ secrets یا فایل خصوصی را وارد مخزن نکن.
- git init، git status و git switch -c lab-topic را اجرا کن.
- یک فایل متنی بساز، git diff --check را بررسی و یک commit ثبت کن.
- تغییر بعدی را در branch جدا انجام بده و diff را قبل از merge بازبینی کن.
- برای undo از git restore یا git revert در Lab استفاده کن؛ reset --hard را روی کار واقعی اجرا نکن.
"""
    if cat == "cloud":
        return f"""# Cloud Lab — {topic}

- فقط از Sandbox/Free Tier استفاده کن؛ subscription سازمانی را تغییر نده.
- region، IAM role، network rule و هزینه مورد انتظار را قبل از ساخت ثبت کن.
- یک policy حداقلی بساز و دسترسی مجاز/غیرمجاز را آزمایش کن.
- audit log و flow log را بررسی و evidence ثبت کن؛ منابع آزمایش را در پایان پاک کن.
"""
    if cat == "backup":
        return f"""# Backup/Restore Lab — {topic}

- یک فایل یا دیتابیس آزمایشی با checksum اولیه بساز.
- backup را در مسیری جدا ذخیره و نسخه/زمان/اندازه را ثبت کن.
- به مسیر جداگانه restore کن؛ نسخه اصلی را overwrite نکن.
- checksum و قابلیت بازشدن داده را بررسی کن و زمان بازیابی را اندازه بگیر.
"""
    if cat == "monitoring":
        return f"""# Monitoring Lab — {topic}

- یک سرویس آزمایشی و baseline متریک‌ها را ثبت کن.
- threshold هشدار را تنظیم و دریافت notification را آزمایش کن.
- failure کنترل‌شده ایجاد و زمان detection و alert را اندازه بگیر.
- از alert به log/metric مربوط برو و Runbook رفع بنویس.
"""
    if cat == "voip":
        return f"""# VoIP Lab — {topic}

- دو endpoint آزمایشی در VLAN تست و یک تماس مشخص کن.
- SIP signaling و RTP media را جدا بررسی کن؛ capture تماس واقعی را ذخیره نکن.
- codec، packet loss، jitter، latency و NAT traversal را ثبت کن.
- یک ACL یا مسیر RTP آزمایشی را تغییر بده و با log/capture علت را ثابت کن.
"""
    if cat == "soc":
        return f"""# SOC / Incident Response Lab — {topic}

- فقط از logهای synthetic یا ماشین آزمایشی استفاده کن.
- timeline، منبع، زمان UTC، host/user و سطح اطمینان را ثبت کن.
- query جستجو را با رویداد مثبت و negative control آزمایش کن.
- alert را به evidence خام وصل کن؛ فرضیه را از واقعیت جدا نگه دار.
"""
    if cat == "windows":
        return f"""# Windows Administration Lab — {topic}

- در VM ویندوز آزمایش کن و پیش از تغییر snapshot بگیر.
- Get-Service، Get-WinEvent -LogName System -MaxEvents 50 و Get-NetIPConfiguration را اجرا کن.
- یک سرویس آزمایشی را restart کن، وضعیت و event log را قبل/بعد مقایسه کن.
- معیار قبولی: تغییر فقط روی سرویس هدف اثر بگذارد و روش rollback ثبت شده باشد.
"""
    if cat == "linux":
        return f"""# Linux Administration Lab — {topic}

- در VM لینوکس اجرا کن و از محیط production استفاده نکن.
- ip -br a، systemctl --failed، journalctl -p warning -n 50، df -h و free -h را بررسی کن.
- یک سرویس آزمایشی را stop/start و لاگ و وضعیت را مقایسه کن.
- تغییرات را با systemctl status و journalctl verify کن و snapshot را آماده نگه دار.
"""
    if cat == "python":
        return f"""# Python Lab — {topic}

- در یک virtual environment تازه کار کن.
- یک تابع کوچک با ورودی معتبر، ورودی مرزی و ورودی نامعتبر بنویس.
- برای هر سه حالت unit test بنویس؛ سپس python -m unittest و python -m compileall را اجرا کن.
- معیار قبولی: تست‌ها قابل تکرار باشند، exceptionها مشخص باشند و هیچ secret در خروجی/log نباشد.
"""
    if cat == "sql":
        return f"""# SQL Lab — {topic}

- یک SQLite database آزمایشی بساز و داده synthetic وارد کن.
- SELECT، JOIN، GROUP BY و یک transaction را اجرا کن.
- EXPLAIN QUERY PLAN را قبل/بعد از index بررسی و PRAGMA integrity_check را اجرا کن.
- معیار قبولی: خروجی درست باشد، transaction rollback قابل اثبات باشد و داده واقعی دستکاری نشود.
"""
    if cat == "storage":
        return f"""# Storage Lab — {topic}

- فقط از دیسک/فایل آزمایشی استفاده کن؛ عملیات format یا حذف روی دیسک واقعی ممنوع است.
- فضای آزاد، filesystem، SMART/HealthStatus و latency I/O را ثبت کن.
- یک فایل تست بساز، checksum بگیر، copy/restore را آزمایش کن و checksum را مقایسه کن.
- معیار قبولی: داده با checksum یکسان بازیابی شود و هیچ volume واقعی تغییر نکند.
"""
    base = f"""# آزمایشگاه عملی — {topic}

## توپولوژی پیشنهادی Lab
- ۲ سوییچ / ۱ روتر / ۲ کلاینت (یا GNS3/EVE-NG/Packet Tracer)
- یک لینک uplink و یک لینک backup (برای تست failover)

## مراحل اجرا

### مرحله ۱ — وضعیت پایه (قبل از تغییر)
| مورد | مقدار قبل | دستور مشاهده |
|------|-----------|--------------|
| وضعیت اینترفیس | | `show ip interface brief` / `ip -br a` |
| جدول مرتبط | | دستور تخصصی دسته |
| لاگ اخیر | | `show logging` / `journalctl -n 50` |

### مرحله ۲ — تغییر برگشت‌پذیر
1. **Backup اجباری** قبل از هر change:
```
copy running-config startup-config
! یا
show running-config | redirect flash:pre-lab.cfg
```
2. پیکربندی حداقلی مرتبط با «{topic}»
3. ذخیره موقت (نه لزوماً startup تا verify کامل نشود)

### مرحله ۳ — Verify
- [ ] Verify محلی (روی همان دستگاه)
- [ ] Verify از کلاینت واقعی (پینگ / curl / nslookup)
- [ ] لاگ بدون خطای جدید

### مرحله ۴ — شکست عمدی (Failure Injection)
عمداً یکی از این‌ها را بشکن و با جدول RCA پیدا کن:
- کابل uplink را بکش
- VLAN اشتباه روی access بگذار
- ACL deny اشتباه اعمال کن
- تایمر/اولویت را خراب کن

### مرحله ۵ — Rollback
```
configure terminal
! دستورات معکوس
end
copy startup-config running-config   ! اگر نیاز
```
"""
    if level in ("L3", "L4"):
        base += f"""
### مرحله ۶ — سطح سازمانی ({level})
- پنجره Change را تعریف کن (مثلاً ۲۲:۰۰–۲۳:۰۰)
- Runbook یک‌صفحه‌ای بنویس
- Monitoring بعد از change (حداقل ۳۰ دقیقه)
- Document: چه تغییری، چرا، نتیجه، درس‌آموخته
"""
    return base


def _rca_table(cat: str) -> str:
    custom = {
        "hardware": [
            ("Reboot یا خاموشی ناگهانی", "دما، PSU یا خطای سخت‌افزار", "Event Viewer، SMART، دما"),
            ("کندی پس از مدتی", "thermal throttling یا فشار RAM", "دما، حافظه، perf counters"),
            ("دیسک unhealthy", "خطای media یا controller", "SMART/vendor diagnostic"),
        ],
        "firmware": [
            ("بوت نشدن OS", "Boot Order یا loader", "UEFI setup، bcdedit"),
            ("BitLocker Recovery", "تغییر TPM/Secure Boot", "Recovery key و TPM state"),
            ("دستگاه ناشناخته", "firmware/driver ناسازگار", "vendor release notes، Device Manager"),
        ],
        "powershell": [
            ("Access denied", "ACL یا سطح دسترسی", "Get-Acl، $Error[0]"),
            ("خروجی خالی", "فیلتر یا pipeline اشتباه", "متغیرهای میانی، Measure-Object"),
            ("فقط بعضی hostها شکست می‌خورند", "WinRM/firewall/credential", "Test-WSMan، Test-NetConnection"),
        ],
        "git": [
            ("فایل ناخواسته در commit", "staging بیش از حد", "git diff --cached"),
            ("merge conflict", "تغییر هم‌زمان یک ناحیه", "git status، conflict markers"),
            ("تغییر گم‌شده", "branch یا working tree اشتباه", "git log --all، git reflog"),
        ],
        "cloud": [
            ("403/AccessDenied", "IAM policy یا trust", "effective policy، audit log"),
            ("resource unreachable", "route/security group/NACL", "flow logs، route table"),
            ("هزینه غیرمنتظره", "resource/region فراموش‌شده", "billing tags، inventory"),
        ],
        "backup": [
            ("backup موجود ولی restore شکست می‌خورد", "نسخه خراب یا وابستگی جاافتاده", "checksum، restore log"),
            ("RPO رعایت نشده", "فاصله jobها زیاد است", "backup timestamps"),
            ("فضا تمام می‌شود", "retention نامناسب", "repository usage، retention policy"),
        ],
        "monitoring": [
            ("alert storm", "threshold یا grouping نامناسب", "alert history، labels"),
            ("رخداد دیده نمی‌شود", "agent/collector یا query", "raw logs، scrape status"),
            ("false positive", "baseline یا suppression ضعیف", "نمونه مثبت/منفی"),
        ],
        "voip": [
            ("صدای یک‌طرفه", "مسیر RTP/NAT/ACL", "SIP و RTP capture"),
            ("jitter بالا", "congestion یا Wi-Fi", "jitter/loss/queue metrics"),
            ("تماس برقرار نمی‌شود", "SIP auth/routing", "SIP response code، registrar log"),
        ],
        "soc": [
            ("alert بدون evidence", "source integration یا query", "raw event و ingestion status"),
            ("زمان‌بندی ناسازگار", "timezone/clock skew", "UTC timestamp، NTP status"),
            ("false positive", "rule/context ناکافی", "negative controls و entity context"),
        ],
    }
    rows = custom.get(cat, ERRORS.get(cat, [
        ("سرویس قطع کامل", "لایه فیزیکی یا gateway", "show interface / ping gateway"),
        ("فقط بعضی کلاینت‌ها", "VLAN / ACL / DNS خاص", "مقایسه کلاینت خوب و بد"),
        ("بعد از reboot برگشت", "startup ≠ running", "show startup-config"),
        ("کندی نه قطعی", "QoS / congestion / duplex", "show interface counters / perf"),
        ("قطع متناوب", "flapping / STP reconvergence", "log | include UPDOWN|SPANTREE"),
    ]))
    header = "| علامت (Symptom) | علت محتمل | دستور شواهد | اقدام اول |\n|---|---|---|---|"
    body = "\n".join(
        f"| {a} | {b} | `{c}` | ایزوله + backup |" for a, b, c in rows
    )
    return f"{header}\n{body}"


def _security_block(cat: str, level: str) -> str:
    common = """- حداقل دسترسی (least privilege) روی management
- لاگ تغییرات (who / when / what)
- جداسازی management plane از data plane
- قبل از expose به اینترنت: threat model کوتاه"""
    extra = {
        "vlan": "\n- Native VLAN را از VLAN کاربران جدا کن\n- Trunk را به allowed VLAN محدود کن\n- Port-security روی access",
        "stp": "\n- BPDU Guard روی پورت‌های access\n- Root Guard روی لبه‌های دامنه\n- PortFast فقط روی کلاینت نه uplink",
        "dhcp": "\n- DHCP Snooping + Trust فقط روی uplink سرور\n- محدودیت rate روی untrusted\n- Reservation برای زیرساخت حیاتی",
        "dns": "\n- DNSSEC در صورت امکان\n- محدود کردن recursion\n- جداسازی internal/external (Split-Horizon)",
        "vpn": "\n- الگوریتم‌های قوی (AES-GCM، SHA2)\n- PFS فعال\n- محدود کردن interesting traffic\n- مانیتور Phase1/Phase2",
        "firewall": "\n- Policy از specific به general\n- Default deny\n- لاگ sessionهای deny\n- جداسازی zone",
        "hardware": "\n- از ESD و برق ایمن پیروی کن\n- Firmware فقط از منبع رسمی\n- پیش از تعویض قطعه، شواهد جمع کن",
        "firmware": "\n- Recovery Key را پیش از تغییر TPM/Secure Boot آماده کن\n- firmware را بدون نیاز و برق پایدار تغییر نده",
        "powershell": "\n- Execution Policy را بی‌دلیل دور نزن\n- secrets را در command history/log ننویس\n- Least privilege و transcript",
        "git": "\n- secrets را در commit نگذار\n- بازبینی diff پیش از push\n- branch protection و least privilege",
        "cloud": "\n- IAM least privilege\n- budget alert و resource cleanup\n- audit log را فعال نگه دار",
        "backup": "\n- نسخه آفلاین/جداگانه نگه دار\n- restore test زمان‌بندی‌شده\n- دسترسی به backup محدود باشد",
        "monitoring": "\n- log حاوی اطلاعات حساس را ماسک کن\n- دسترسی dashboard محدود\n- alert باید actionable باشد",
        "voip": "\n- capture صدا/شماره‌ها را نگه‌داری نکن\n- SRTP/TLS را در صورت پشتیبانی فعال کن",
        "soc": "\n- chain of custody را حفظ کن\n- شواهد را تغییر نده\n- دسترسی و export را ثبت کن",
    }
    return common + extra.get(cat, "")


def _level_guidance(level: str) -> str:
    return {
        "L0": "فقط تصویر ذهنی و تشبیه. هنوز دستور حفظ نکن؛ بفهم «چرا».",
        "L1": "مشاهده کن + یک Lab ساده. دستورات show را اجرا و خروجی را بخوان.",
        "L2": "پیکربندی کامل + Verify + Rollback. بدون backup تغییر نده.",
        "L3": "طراحی برای چند سگمنت، RCA سیستماتیک، تأثیر روی سرویس‌های دیگر.",
        "L4": "معماری سازمانی، Change Control، HA، مستندسازی و Runbook قابل تحویل به تیم.",
    }.get(level, "")


def _base_commands(cat: str):
    network_cats = {"vlan","stp","ospf","bgp","acl","nat","vpn","dhcp","dns","wireless","firewall","ha","qos","security","tcpip","mpls","multicast","vxlan"}
    if cat in network_cats:
        return COMMON[:8]
    if cat in BANKS and cat != "general":
        return BANKS[cat][:8]
    return [("record baseline", "ثبت وضعیت اولیه"), ("verify expected result", "تأیید نتیجه"), ("review logs", "بررسی لاگ")]


def _backup_commands(cat: str):
    commands = {
        "hardware": [("Get-CimInstance Win32_Processor", "مشخصات CPU"), ("Get-CimInstance Win32_PhysicalMemory", "مشخصات RAM"), ("Get-PhysicalDisk", "سلامت دیسک")],
        "firmware": [("msinfo32", "BIOS Mode / Secure Boot"), ("Confirm-SecureBootUEFI", "وضعیت Secure Boot"), ("Get-Tpm", "وضعیت TPM")],
        "powershell": [("Start-Transcript -Path lab-transcript.txt", "ثبت transcript"), ("Get-History", "تاریخچه نشست"), ("Get-Error | Select-Object -First 5", "خطاهای اخیر")],
        "windows": [("Get-NetIPConfiguration", "وضعیت شبکه"), ("Get-WinEvent -LogName System -MaxEvents 50", "رویدادهای سیستم")],
        "linux": [("ip -br a", "رابط‌ها"), ("journalctl -p warning -n 50", "هشدارها"), ("df -h", "فضای دیسک")],
        "git": [("git status --short", "وضعیت working tree"), ("git diff --check", "بررسی diff"), ("git log -5 --oneline", "تاریخچه")],
        "cloud": [("terraform plan", "بازبینی قبل از apply"), ("terraform state list", "فهرست منابع")],
        "backup": [("Get-FileHash backup.bin -Algorithm SHA256", "checksum"), ("robocopy source restore-test /E /L", "dry-run کپی")],
        "monitoring": [("Get-Counter CPU", "baseline CPU"), ("Get-WinEvent -LogName System -MaxEvents 30", "رویدادها")],
        "voip": [("Wireshark filter: sip || rtp", "مشاهده signaling/media"), ("ping -n 20 peer", "baseline loss/latency")],
        "soc": [("Get-WinEvent -LogName Security -MaxEvents 50", "رویدادهای احراز هویت"), ("Get-FileHash evidence.log -Algorithm SHA256", "integrity شواهد")],
        "sql": [("PRAGMA integrity_check;", "سلامت SQLite"), ("EXPLAIN QUERY PLAN SELECT ...", "طرح query")],
        "python": [("python --version", "نسخه runtime"), ("python -m compileall .", "بررسی syntax"), ("python -m unittest discover -s tests", "تست‌ها")],
    }
    return commands.get(cat, [("record baseline", "ثبت وضعیت اولیه"), ("verify expected result", "تأیید نتیجه"), ("review logs", "بررسی لاگ")])


def _rollback_block(cat: str) -> str:
    blocks = {
        "hardware": "قطعه/تنظیم را به وضعیت ثبت‌شده برگردان؛ firmware downgrade فقط طبق دستورالعمل سازنده.",
        "firmware": "مقادیر BIOS/UEFI را به مقدار ثبت‌شده برگردان و Recovery Key را در اختیار داشته باش.",
        "powershell": "از VM snapshot یا پیکربندی قبلی استفاده کن؛ تغییرات را با transcript ثبت کن.",
        "git": "در Lab از git revert برای commit ثبت‌شده استفاده کن؛ reset --hard را روی کار واقعی اجرا نکن.",
        "cloud": "از plan/diff و state استفاده کن؛ منابع ایجادشده را طبق change plan حذف یا restore کن.",
        "backup": "restore را در مسیر جدا انجام بده؛ منبع را تا تأیید سلامت overwrite نکن.",
        "monitoring": "rule/threshold قبلی را restore کن و alert آزمایشی را پاک کن.",
        "voip": "ACL/QoS/NAT را به snapshot قبلی برگردان و تماس دوطرفه را تست کن.",
        "soc": "شواهد را حفظ کن؛ containment را طبق playbook مجاز و ثبت‌شده بازگردان.",
    }
    if cat in blocks:
        return blocks[cat]
    if cat in {"vlan","stp","ospf","bgp","acl","nat","vpn","dhcp","dns","wireless","firewall","ha","qos","security","tcpip","mpls","multicast","vxlan"}:
        return "configure terminal; apply the documented reverse commands; verify"
    return "تغییر را از backup/snapshot برگردان، سپس نتیجه را با آزمون تکرارپذیر Verify کن."


def _analogy(cat: str, topic: str) -> str:
    analogies = {
        "hardware": "یک رایانه را مثل کارگاه در نظر بگیر: CPU کار را اجرا می‌کند، RAM میز کار است، Storage انبار پایدار و سیستم خنک‌کننده کنترل دماست. عیب‌یابی با تعویض حدسی قطعه، مثل تعویض ابزار بدون اندازه‌گیری است.",
        "firmware": "Firmware مثل دستورالعمل آغاز به کار دستگاه است؛ پیش از رسیدن کنترل به سیستم‌عامل، سخت‌افزار و زنجیرهٔ بوت را آماده می‌کند. یک تغییر کوچک می‌تواند مسیر بوت یا اعتماد امنیتی را عوض کند.",
        "powershell": "PowerShell را مثل خط تولید داده ببین: cmdletها object تولید می‌کنند، pipeline آن‌ها را منتقل می‌کند و فیلترها فقط نتیجهٔ موردنیاز را نگه می‌دارند. خروجی متنی و object را با هم اشتباه نگیر.",
        "windows": "Windows را مثل یک سامانهٔ چندلایه ببین: سرویس، حساب کاربری، policy، شبکه و Event Log هرکدام شواهد جداگانه دارند؛ قبل از تغییر، لایهٔ خراب را مشخص کن.",
        "linux": "در Linux، process، systemd، kernel، filesystem و network هرکدام منبع شواهد متفاوتی دارند. ابتدا مشاهده کن و بعد فقط یک متغیر را تغییر بده.",
        "python": "برنامه را مثل زنجیره‌ای از قراردادها ببین: ورودی اعتبارسنجی می‌شود، تابع تبدیل انجام می‌دهد، خطا مدیریت می‌شود و تست، رفتار مورد انتظار را اثبات می‌کند.",
        "sql": "پایگاه داده مثل دفتر ثبت تراکنش است: schema قرارداد داده، transaction مرز اتمی و index مسیر دسترسی است. نتیجهٔ درست و عملکرد مناسب را جداگانه اندازه بگیر.",
        "git": "Git مثل دفتر تاریخچهٔ تغییرات است: working tree محل کار، index فهرست تغییرات آمادهٔ ثبت و commit یک snapshot قابل بازبینی است. پیش از هر عملیات، وضعیت و diff را بخوان.",
        "cloud": "زیرساخت ابری از هویت، policy، شبکه و resource تشکیل شده است. خطای دسترسی را با شواهد مجوز و audit log جدا از خطای مسیر شبکه بررسی کن.",
        "backup": "Backup تا وقتی restore آزمایش نشده فقط یک فایل است. موفقیت یعنی دادهٔ قابل‌استفاده در زمان هدف بازیابی شود و RPO/RTO اندازه‌گیری شده باشد.",
        "monitoring": "سامانهٔ پایش مثل سیستم هشدار ساختمان است: metric وضعیت را نشان می‌دهد، log جزئیات رخداد و trace مسیر درخواست را. هشدار خوب باید به اقدام مشخص منتهی شود.",
        "soc": "تحلیل رخداد مانند بازسازی یک حادثه از شواهد است: زمان‌ها را یکسان کن، دادهٔ خام را حفظ کن، فرضیه را جدا بنویس و آن را با شواهد مخالف هم آزمایش کن.",
        "storage": "Storage را با سه معیار جدا بررسی کن: سلامت رسانه، مسیر I/O و تأخیر. فضای آزاد زیاد به‌تنهایی سلامت یا کارایی را ثابت نمی‌کند.",
        "virtualization": "در مجازی‌سازی، host، hypervisor، virtual switch، guest و storage وابستگی‌های متفاوت دارند. مشکل ماشین مجازی را با مقایسهٔ host و guest محدود کن.",
        "voip": "تماس VoIP دو مسیر دارد: signaling برای برقرارشدن تماس و media برای صدا. موفقیت SIP لزوماً به معنی سالم‌بودن RTP نیست.",
    }
    return analogies.get(cat, f"برای «{topic}» از مدل مشاهده → فرضیه → آزمایش کنترل‌شده → راستی‌آزمایی استفاده کن. هر نتیجه باید به شواهد قابل تکرار وصل باشد؛ تغییر بدون baseline و rollback قابل اتکا نیست.")


def _troubleshooting(cat: str) -> str:
    paths = {
        "hardware": "1. علائم، زمان وقوع و تغییر اخیر را ثبت کن\n2. برق، دما و کابل را بررسی کن\n3. SMART، memory diagnostics و Event Log را بخوان\n4. در صورت نیاز فقط یک قطعه را در محیط امن آزمایش کن\n5. آزمون پایداری و مقایسه با baseline انجام بده",
        "firmware": "1. مدل دستگاه و نسخهٔ firmware را ثبت کن\n2. Boot mode، Secure Boot و TPM را فقط مشاهده کن\n3. Recovery Key و راه برگشت را آماده کن\n4. یک گزینه را در دستگاه آزمایشی تغییر بده\n5. cold boot و سلامت OS را بررسی کن",
        "powershell": "1. ورودی، نوع object و مجوز را اعتبارسنجی کن\n2. فرمان مشاهده‌ای را جدا اجرا کن\n3. خروجی هر مرحلهٔ pipeline را بررسی کن\n4. خطاهای terminating و non-terminating را تفکیک کن\n5. نتیجه را با تست و transcript قابل تکرار تأیید کن",
        "windows": "1. دامنهٔ اثر و کاربر/میزبان را مشخص کن\n2. سرویس و وضعیت شبکه را مشاهده کن\n3. Event Viewer و policy مؤثر را بررسی کن\n4. تغییر حداقلی را روی میزبان آزمایشی اعمال کن\n5. رویدادها، سرویس و سناریوی کاربر را دوباره تست کن",
        "linux": "1. زمان و scope رخداد را ثبت کن\n2. systemctl، journalctl و منابع CPU/RAM/disk را بررسی کن\n3. وابستگی سرویس و permission را بررسی کن\n4. یک تغییر کنترل‌شده اعمال کن\n5. status و log را پس از تغییر مقایسه کن",
        "python": "1. ورودی و نسخهٔ runtime را ثبت کن\n2. خطا را با کوچک‌ترین مثال بازتولید کن\n3. stack trace و مرز تابع را بررسی کن\n4. اصلاح را با unit test و edge case بیازمای\n5. کل تست‌ها و compileall را اجرا کن",
        "sql": "1. query، پارامتر و transaction را ثبت کن\n2. صحت نتیجه و constraintها را بررسی کن\n3. EXPLAIN / query plan را بخوان\n4. تغییر schema یا index را روی کپی آزمایش کن\n5. integrity check و تست rollback را اجرا کن",
        "git": "1. git status و branch فعلی را بررسی کن\n2. diff و staging را بازبینی کن\n3. تاریخچه و merge base را پیدا کن\n4. conflict را در branch آزمایشی حل کن\n5. diff نهایی و تست‌ها را قبل از push تأیید کن",
        "backup": "1. منبع و RPO/RTO را مشخص کن\n2. صحت و checksum نسخه را بررسی کن\n3. restore را در مقصد جدا اجرا کن\n4. دادهٔ بازیابی‌شده را با نمونهٔ مورد انتظار مقایسه کن\n5. زمان واقعی و نتیجه را ثبت کن",
        "monitoring": "1. زمان و دامنهٔ هشدار را مشخص کن\n2. raw metric/log/trace را بررسی کن\n3. ingestion و سلامت collector را تأیید کن\n4. positive و negative control اجرا کن\n5. alert و runbook را با رخداد کنترل‌شده تأیید کن",
        "soc": "1. شواهد خام را حفظ و hash کن\n2. زمان‌ها را به UTC نرمال کن\n3. timeline و ارتباط هویت/میزبان بساز\n4. فرضیه را با شواهد مخالف و negative control بیازمای\n5. containment و معیار پایان را ثبت کن",
        "storage": "1. فضای آزاد و سلامت device را بخوان\n2. latency و I/O queue را اندازه بگیر\n3. کابل/controller/path را بررسی کن\n4. تست فقط روی volume آزمایشی اجرا کن\n5. checksum داده و سلامت بعد از بازیابی را تأیید کن",
        "voip": "1. زمان، دو endpoint و مسیر تماس را ثبت کن\n2. SIP registration و response code را بررسی کن\n3. مسیر RTP، NAT و ACL را جدا بررسی کن\n4. loss، jitter و latency را اندازه بگیر\n5. صدای دوطرفه و کیفیت را از هر دو سمت تأیید کن",
    }
    return paths.get(cat, "1. دامنه و زمان رخداد را مشخص کن\n2. baseline و شواهد خام را جمع کن\n3. فرضیهٔ قابل آزمون بساز\n4. یک تغییر حداقلی در محیط آزمایشی انجام بده\n5. نتیجه را verify کن و rollback را مستند کن")


def _production_checklist(cat: str) -> str:
    checks = {
        "hardware": ["مدل/سریال و وضعیت اولیه ثبت شده", "داده‌های مهم backup شده‌اند", "قطعهٔ جایگزین سازگار و ESD رعایت شده", "تست پایداری پس از تعمیر تعریف شده", "نتیجه و قطعهٔ تعویض‌شده ثبت می‌شود"],
        "firmware": ["مدل و نسخهٔ فعلی ثبت شده", "Recovery Key و مسیر recovery آماده است", "یادداشت انتشار سازنده بررسی شده", "برق پایدار و پنجرهٔ نگهداری فراهم است", "بوت و سلامت OS پس از تغییر تأیید می‌شود"],
        "powershell": ["اسکریپت ابتدا در حالت read-only اجرا شده", "ورودی و مجوزها اعتبارسنجی می‌شوند", "خطاها و exit code ثبت می‌شوند", "secret در log یا command line قرار نمی‌گیرد", "تست idempotency و rollback تعریف شده"],
        "windows": ["scope و حساب اجرا مشخص است", "GPO/Service baseline ثبت شده", "تغییر در گروه آزمایشی انجام شده", "Event Log و دسترسی کاربر بررسی می‌شود", "روش بازگشت و زمان‌بندی مستند است"],
        "linux": ["snapshot یا backup قابل بازیابی است", "سرویس و dependencyها ثبت شده‌اند", "تغییر با least privilege انجام می‌شود", "journal و health check بررسی می‌شوند", "rollback و owner تغییر مشخص است"],
        "python": ["virtual environment و dependencyها قفل شده‌اند", "ورودی نامعتبر و edge case تست شده", "secret در کد یا log نیست", "unit/integration test اجرا شده", "نسخه و روش rollback ثبت شده"],
        "sql": ["backup و restore آزمایش شده", "migration در transaction/نسخهٔ کپی آزموده شده", "plan و lock impact بررسی شده", "constraint و integrity test اجرا شده", "روش rollback و سازگاری نسخه ثبت شده"],
        "git": ["working tree و diff بازبینی شده", "secret scan انجام شده", "branch و commit کوچک و معنادارند", "تست‌ها پیش از merge سبز هستند", "revert plan روشن است"],
        "backup": ["نسخهٔ مستقل و retention مشخص است", "checksum/integrity تأیید شده", "restore در مقصد جدا آزمایش شده", "RPO/RTO واقعی اندازه‌گیری شده", "دسترسی و کلیدها به‌صورت امن نگهداری می‌شوند"],
        "soc": ["محدودهٔ مجاز و مالک رخداد مشخص است", "شواهد خام و chain of custody حفظ شده", "زمان‌ها و منبع‌ها نرمال شده‌اند", "فرضیه و سطح اطمینان جدا ثبت شده", "containment و معیار خاتمه تأیید شده"],
        "storage": ["backup پیش از عملیات مخرب تأیید شده", "دیسک و volume هدف دقیق شناسایی شده", "format/delete فقط در Lab مجاز است", "checksum و سلامت پس از تغییر بررسی می‌شود", "مسیر بازگشت مستند است"],
    }
    items = checks.get(cat, ["Backup/snapshot قابل بازیابی است", "دامنهٔ تغییر و owner مشخص است", "تغییر در Lab یا canary تأیید شده", "معیار موفقیت و monitoring تعریف شده", "Rollback و مستندسازی آماده است"])
    return "\\n".join(f"- [ ] {item}" for item in items)


def _assessment_block(cat: str, topic: str) -> str:
    assessments = {
        "hardware": [("برای reboot تصادفی چه شواهدی را پیش از تعویض قطعه جمع می‌کنی؟", "Event Log، دما، SMART، RAM و منبع تغذیه؛ با ثبت زمان و baseline."), ("چرا تعویض هم‌زمان چند قطعه تشخیص را دشوار می‌کند؟", "چون رابطهٔ علت و معلول و امکان مقایسهٔ قبل/بعد از بین می‌رود.")],
        "powershell": [("چرا pipeline در PowerShell با pipe متنی در CMD یکسان نیست؟", "PowerShell objectهای .NET را عبور می‌دهد؛ propertyها را می‌توان فیلتر و انتخاب کرد."), ("چه زمانی باید -WhatIf یا حالت read-only را ترجیح داد؟", "پیش از تغییر گروهی یا هر عملیات پراثر، برای مشاهدهٔ دامنهٔ تغییر بدون اعمال آن.")],
        "python": [("سه نوع تست لازم برای تابع ورودی‌محور چیست؟", "حالت عادی، مرزی و ورودی نامعتبر؛ هرکدام باید خروجی یا exception مورد انتظار داشته باشد."), ("چرا خطا را نباید بی‌صدا با except: pass حذف کرد؟", "چون شکست پنهان می‌شود و عیب‌یابی، retry و صحت داده قابل اعتماد نیست.")],
        "sql": [("چرا قبل از افزودن index باید query plan را بررسی کرد؟", "تا مشخص شود bottleneck واقعی چیست و هزینهٔ write/storage index توجیه دارد."), ("چطور اتمی‌بودن تغییر را می‌آزمایی؟", "با transaction آزمایشی و اثبات commit/rollback و اجرای integrity check.")],
        "git": [("قبل از commit چه چیزی را باید بررسی کرد؟", "git status، diff، diff --cached و فایل‌های محرمانه/تولیدشده."), ("چه تفاوتی بین revert و reset --hard در کار مشترک وجود دارد؟", "revert تغییر معکوس جدید می‌سازد؛ reset --hard تاریخچه/working tree را جابه‌جا یا پاک می‌کند.")],
        "backup": [("چه چیزی restore test را معتبر می‌کند؟", "بازیابی واقعی به مقصد جدا، اعتبارسنجی داده و ثبت زمان نسبت به RPO/RTO.")],
        "soc": [("چرا timeline باید بر اساس UTC ساخته شود؟", "برای هم‌ترازکردن رخدادهای منابع با timezone و clock skew متفاوت."), ("negative control چه کمکی می‌کند؟", "نشان می‌دهد query یا rule بی‌دلیل برای دادهٔ سالم هم alert تولید نمی‌کند.")],
        "windows": [("از کجا تشخیص می‌دهی سرویس واقعاً fail شده یا فقط کلاینت مشکل دارد؟", "وضعیت سرویس و Event Log را با یک کلاینت سالم و درخواست کنترل‌شده مقایسه می‌کنم.")],
        "linux": [("چرا باید systemctl status و journalctl را با هم دید؟", "اولی وضعیت سرویس را نشان می‌دهد و دومی شواهد زمانی خطا را.")],
        "storage": [("چرا فضای آزاد به‌تنهایی سلامت دیسک را ثابت نمی‌کند؟", "چون media error، controller/path failure و latency مستقل از ظرفیت آزادند.")],
    }
    rows = assessments.get(cat, [
        (f"برای «{topic}» چه شواهدی را پیش از تغییر ثبت می‌کنی؟", "وضعیت اولیه، لاگ/خروجی قابل تکرار، دامنهٔ اثر و زمان رخداد."),
        (f"چطور نتیجهٔ تغییر «{topic}» را اثبات می‌کنی؟", "با معیار موفقیت از پیش تعریف‌شده، آزمون مثبت/منفی و مقایسهٔ قبل/بعد."),
    ])
    body = "\\n".join(f"{i}. **پرسش:** {q}\\n   **پاسخ:** {a}" for i, (q, a) in enumerate(rows, 1))
    return f"### پرسش و پاسخ / Answer Key\\n{body}"


def build_deep_fallback(
    title_fa: str, title_en: str = "", level: str | None = None
) -> Dict[str, Any]:
    level = level or _level(title_fa)
    topic = _topic(title_fa)
    cat = _cat(topic)
    level_fa = _LEVEL_FA.get(level, level)
    bank = BANKS.get(cat)
    if not bank or cat == "general":
        bank = [("record baseline", "ثبت وضعیت اولیه"), ("verify expected result", "تأیید نتیجه"), ("review logs", "بررسی لاگ")]
    story = _story(topic, cat)

    summary = (
        f"«{topic}» — سطح {level_fa}. شامل مدل مفهومی، معماری، مراحل اجرا، "
        f"مثال قابل تکرار، لابراتوار، راهنمای عیب‌یابی، معیار Verify، rollback، "
        f"چک‌لیست عملیاتی و آزمون با پاسخ‌نامه."
    )

    commands = "\n".join(
        [
            f"# بانک دستورات عملی — {topic} | {level} | دسته: {cat}",
            "",
            "## پایه و Verify (همیشه اول این‌ها)",
            _fmt(_base_commands(cat)),
            f"## تخصصی دسته «{cat}»",
            _fmt(bank[:18] if len(bank) > 18 else bank),
            "## Backup / Evidence",
            _fmt(_backup_commands(cat)),
            "## Rollback / Recovery",
            _rollback_block(cat),
        ]
    )

    full = f"""# {topic}

**سطح:** {level} — {level_fa}
**EN:** {title_en or topic}
**دسته عملیاتی:** {cat}

---

## ۰) داستان واقعی سازمانی (چرا این درس مهم است؟)

{story}

اگر فقط تئوری بخوانی، در لحظه قطعی سرویس گیج می‌شوی.
این درس تو را از «دانستن اسم» به «بلد بودن رفع» می‌رساند.

---

## ۱) تشبیه ساده (برای ماندن در ذهن)

{_analogy(cat, topic)}

---

## ۲) معماری (Control / Data / Management)

{_arch_table(cat)}

---

## ۳) فریم‌به‌فریم (چه اتفاقی پشت صحنه می‌افتد؟)

{_frame_steps(cat)}

---

## ۴) سطح‌به‌سطح — تو الان کجایی؟

{_level_guidance(level)}

| سطح | انتظار از تو |
|-----|-------------|
| L0–L1 | مفهوم + مشاهده + Lab ساده |
| L2 | پیکربندی + Verify + Rollback مطمئن |
| L3–L4 | طراحی، RCA، تأثیر سازمانی، Runbook |

---

## ۵) امنیت (حتی در Lab هم عادت کن)

{_security_block(cat, level)}

---

## ۶) جدول عیب‌یابی سریع (RCA)

{_rca_table(cat)}

**مسیر RCA استاندارد:**
Symptom → Scope (کجا؟) → Evidence (دستور) → Hypothesis → Test → Fix → Verify → Document

---

## ۷) چک‌لیست Production (قبل از Apply در سازمان)

{_production_checklist(cat)}

---

## ۸) جمع‌بندی استاد

سه چیز را از بر باش، نه طوطی‌وار:
1. **سه دستور Verify اول** برای این موضوع
2. **مسیر RCA** وقتی علامت عجیب دیدی
3. **نقطه Rollback** قبل از هر change

«{topic}» را وقتی بلدی که بتوانی ساعت ۲ شب، با لاگ و یک کلاینت واقعی، سرویس را برگردانی.

---

## ۹) خودآزمایی و پاسخ‌نامه

{_assessment_block(cat, topic)}
"""

    lab = _lab_concrete(topic, cat, level)

    notes = f"""## نکات سریع عیب‌یابی — {topic}

{_rca_table(cat)}

### ترتیب عیب‌یابی پیشنهادی
{_troubleshooting(cat)}

### یادداشت سطح {level}
{_level_guidance(level)}
"""

    return {
        "summary": summary,
        "full_content": full,
        "commands": commands,
        "examples": lab,
        "notes": notes,
        "level": level,
        "topic": topic,
        "category": cat,
    }
