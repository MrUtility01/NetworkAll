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
    }
    if cat in specific:
        return specific[cat]
    hooks = SCENARIO_HOOKS.get(cat, SCENARIO_HOOKS.get("general", []))
    if hooks:
        return hooks[0]
    return (
        f"سازمانی با چند سایت و حدود ۸۰۰ کاربر. تیم NOC گزارش می‌دهد که "
        f"«{topic}» باعث کندی یا قطع سرویس حیاتی شده. شما به عنوان مهندس شبکه "
        f"باید از لایه ۱ تا ۷ ایزوله کنید، شواهد جمع کنید و با حداقل قطعی رفع کنید."
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
        f"«{topic}» — سطح {level_fa}. "
        f"داستان سازمانی واقعی + معماری + فریم‌به‌فریم + دستورات چندوندر + "
        f"Lab عملی + جدول RCA + امنیت + چک‌لیست Production."
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

رانندگی در شهر شلوغ:
- قوانین ترافیک = پروتکل/استاندارد
- رانندگی در خیابان خلوت = Lab
- رانندگی در بزرگراه ساعت اوج = Production با چک‌لیست و Rollback

«{topic}» همان قطعه‌ای است که اگر اشتباه تنظیم شود، یا ترافیک گیر می‌کند یا تصادف (loop / blackhole / outage) رخ می‌دهد.

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

- [ ] Backup گرفته شده و قابل restore است
- [ ] Rollback نوشته و تست شده (حداقل روی کاغذ)
- [ ] دامنه تغییر مشخص است (کدام دستگاه / VLAN / VRF)
- [ ] پنجره Change و اطلاع‌رسانی انجام شده
- [ ] Monitoring بعد از change فعال است
- [ ] Runbook یک‌صفحه‌ای آماده است

---

## ۸) جمع‌بندی استاد

سه چیز را از بر باش، نه طوطی‌وار:
1. **سه دستور Verify اول** برای این موضوع
2. **مسیر RCA** وقتی علامت عجیب دیدی
3. **نقطه Rollback** قبل از هر change

«{topic}» را وقتی بلدی که بتوانی ساعت ۲ شب، با لاگ و یک کلاینت واقعی، سرویس را برگردانی.
"""

    lab = _lab_concrete(topic, cat, level)

    notes = f"""## نکات سریع عیب‌یابی — {topic}

{_rca_table(cat)}

### ترتیب ایزوله‌سازی پیشنهادی
1. لایه فیزیکی / لینک (up/down, errors, duplex)
2. لایه ۲ (VLAN, trunk, STP state)
3. لایه ۳ (gateway, route, ACL/NAT)
4. سرویس (DNS, DHCP, app)
5. کلاینت در برابر زیرساخت (مقایسه خوب/بد)

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
