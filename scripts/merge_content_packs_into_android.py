#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""ادغام بسته‌های tools؛ فصل ۶۴=Git؛ امنیت→۶۵؛ OSPF/VPN→۶۶/۶۷؛ دستورات→۶۸."""
from __future__ import annotations
import gzip, json, sys, re
from pathlib import Path
from collections import defaultdict

ROOT = Path(__file__).resolve().parents[1]
GZ = ROOT / "android/app/src/main/assets/curriculum_index.json.gz"


def as_text(v):
    if v is None:
        return ""
    if isinstance(v, list):
        return "\n".join(str(x) for x in v)
    return str(v)


def load_json(p: Path):
    return json.loads(p.read_text(encoding="utf-8"))


def find_pack_files():
    """Use only canonical per-chapter packs; archived/original JSON files are not imported twice."""
    # Prefer the compiled numeric layout; retain a fallback while the migration runs.
    files = list(ROOT.glob("tools/chapters/[0-9]/build/chapter.json"))
    canonical_ch68_commands = ROOT / "tools/chapters/68/commands/commands.json"
    if canonical_ch68_commands.is_file():
        files.append(canonical_ch68_commands)
    # Additive technology pack; it is deliberately separate from the legacy archive.
    extra_ch68_technologies = ROOT / "tools/chapters/68/commands/sources/encyclopedia/commands_additional_technologies.json"
    if extra_ch68_technologies.is_file():
        files.append(extra_ch68_technologies)
    core_wave3_commands = ROOT / "tools/chapters/68/commands/sources/encyclopedia/commands_core_wave3.json"
    if core_wave3_commands.is_file():
        files.append(core_wave3_commands)
    multi_technology_wave4 = ROOT / "tools/chapters/68/commands/sources/encyclopedia/commands_multi_technology_wave4.json"
    if multi_technology_wave4.is_file():
        files.append(multi_technology_wave4)
    multi_technology_wave5 = ROOT / "tools/chapters/68/commands/sources/encyclopedia/commands_multi_technology_wave5.json"
    if multi_technology_wave5.is_file():
        files.append(multi_technology_wave5)
    multi_technology_wave6 = ROOT / "tools/chapters/68/commands/sources/encyclopedia/commands_multi_technology_wave6.json"
    if multi_technology_wave6.is_file():
        files.append(multi_technology_wave6)
    multi_technology_wave7 = ROOT / "tools/chapters/68/commands/sources/encyclopedia/commands_multi_technology_wave7.json"
    if multi_technology_wave7.is_file():
        files.append(multi_technology_wave7)
    files += list(ROOT.glob("tools/chapters/[0-9][0-9]/build/chapter.json"))
    files += list(ROOT.glob("tools/chapters/[0-9]/chapter.json"))
    files += list(ROOT.glob("tools/chapters/[0-9][0-9]/chapter.json"))
    if not files:
        files = list(ROOT.glob("tools/chapters/ch[0-9][0-9]_*/chapter.json"))
    uniq = []
    seen = set()
    for f in sorted(files):
        if f.is_file() and f.stat().st_size > 20:
            k = str(f.resolve())
            if k not in seen:
                seen.add(k)
                uniq.append(f)
    return uniq


def commands_to_lessons(data: dict) -> list:
    ch = int(data.get("chapter_order") or 68)
    out = []
    sub_map = {
        "basics": 1, "interface": 2, "vlan": 3, "trunk": 3, "stp": 4, "spanning-tree": 4,
        "etherchannel": 5, "port-security": 6, "mac": 7, "cdp": 8, "lldp": 8,
        "troubleshoot": 9, "switching": 2, "general": 10,
        "ssh": 13, "telnet": 14, "ftp": 15, "voip": 16, "vmware_esxi": 17,
        "zabbix": 18, "wireshark": 19, "juniper": 20, "aruba": 21,
        "proxmox": 22, "ansible": 23, "terraform": 24, "kubernetes": 25,
        "powershell": 26, "hyperv": 27, "ftps": 28, "sftp": 29,
        "mikrotik": 30, "cisco": 31, "fortigate": 32,
        "windows_batch": 33, "windows_server": 34, "linux_bash": 35, "linux": 35,
        "docker": 36, "ubiquiti": 37, "snmp_syslog": 38, "dns_dhcp_ntp": 39,
        "web_tls": 40, "cloud": 41, "fortinet_management": 42,
        "security_ops": 43, "git": 44, "backup_recovery": 45,
    }
    for i, c in enumerate(data.get("commands") or [], 1):
        if not isinstance(c, dict):
            continue
        cmd = c.get("command") or c.get("title_en") or ""
        level = c.get("level") or "L1"
        title_fa = c.get("title_fa") or cmd
        if ch != 68 and not str(title_fa).startswith("[L"):
            title_fa = f"[{level}] {title_fa}"
        technology = str(c.get("technology_id") or c.get("category") or "").strip().lower()
        if technology == "linux":
            technology = "linux_bash"
        if technology not in sub_map:
            # Legacy command packs often use category for a topic (routing/ACL/etc.)
            # and store the actual technology in vendor/platform. Prefer a dedicated
            # technology section when that metadata is explicit.
            meta_text = " ".join(str(c.get(k) or "") for k in ("vendor", "platform", "product", "vendor_pack", "category")).lower()
            if "fortimanager" in meta_text or "fortianalyzer" in meta_text:
                technology = "fortinet_management"
            elif "powershell" in meta_text or "pwsh" in meta_text:
                technology = "powershell"
            elif "windows batch" in meta_text or "cmd.exe" in meta_text or "batch/cmd" in meta_text:
                technology = "windows_batch"
            elif "windows server" in meta_text or "active directory" in meta_text or "ad ds" in meta_text:
                technology = "windows_server"
            elif "mikrotik" in meta_text or "routeros" in meta_text:
                technology = "mikrotik"
            elif "cisco" in meta_text or "ios-xe" in meta_text or "ios xe" in meta_text:
                technology = "cisco"
            elif "fortigate" in meta_text or "fortios" in meta_text:
                technology = "fortigate"
            elif "docker" in meta_text or "compose" in meta_text:
                technology = "docker"
            elif "linux" in meta_text or "bash" in meta_text or "gnu utilities" in meta_text:
                technology = "linux_bash"
            elif "vmware" in meta_text or "esxi" in meta_text or "vsphere" in meta_text:
                technology = "vmware_esxi"
            elif "ubiquiti" in meta_text or "unifi" in meta_text or "edgeos" in meta_text:
                technology = "ubiquiti"
            elif "net-snmp" in meta_text or "snmp" in meta_text or "syslog" in meta_text or "netflow" in meta_text:
                technology = "snmp_syslog"
            elif "dns" in meta_text or "dhcp" in meta_text or "chrony" in meta_text or "ipam" in meta_text:
                technology = "dns_dhcp_ntp"
            elif "nginx" in meta_text or "apache" in meta_text or "openssl" in meta_text or "tls" in meta_text or "pki" in meta_text:
                technology = "web_tls"
            elif "aws" in meta_text or "azure" in meta_text:
                technology = "cloud"
            elif "sysmon" in meta_text or "siem" in meta_text or "soc" in meta_text or "osquery" in meta_text:
                technology = "security_ops"
            elif "git" in meta_text or "github" in meta_text:
                technology = "git"
            elif "restic" in meta_text or "borg" in meta_text or "backup" in meta_text or "recovery" in meta_text:
                technology = "backup_recovery"
            elif "voip" in meta_text or "sip" in meta_text or "pbx" in meta_text:
                technology = "voip"
            elif "zabbix" in meta_text:
                technology = "zabbix"
            elif "wireshark" in meta_text or "tshark" in meta_text or "tcpdump" in meta_text:
                technology = "wireshark"
            elif "juniper" in meta_text or "junos" in meta_text:
                technology = "juniper"
            elif "aruba" in meta_text or "aos-cx" in meta_text:
                technology = "aruba"
            elif "proxmox" in meta_text or "pve" in meta_text:
                technology = "proxmox"
            elif "hyper-v" in meta_text or "hyperv" in meta_text:
                technology = "hyperv"
            elif "ansible" in meta_text:
                technology = "ansible"
            elif "terraform" in meta_text:
                technology = "terraform"
            elif "kubernetes" in meta_text or "kubectl" in meta_text:
                technology = "kubernetes"
            elif "telnet" in meta_text:
                technology = "telnet"
            elif "sftp" in meta_text:
                technology = "sftp"
            elif "ftps" in meta_text:
                technology = "ftps"
            elif "ftp" in meta_text:
                technology = "ftp"
        if technology in sub_map:
            sub_order = sub_map[technology]
        else:
            sub = (c.get("subcategory") or c.get("category") or "general").strip().lower()
            sub_order = sub_map.get(sub, 10)
        args = c.get("arguments") or []
        arg_lines = []
        for a in args:
            if isinstance(a, dict):
                arg_lines.append(
                    f"- `{a.get('name', '')}`: {a.get('meaning_fa', '')} — مثال: `{a.get('example', '')}`"
                )
            else:
                arg_lines.append(f"- {a}")
        steps = c.get("steps_fa") or []
        if isinstance(steps, list):
            steps_txt = "\n".join(f"{idx}. {s}" for idx, s in enumerate(steps, 1))
        else:
            steps_txt = str(steps)
        out_fields = c.get("output_fields_fa") or []
        of_txt = "\n".join(
            f"- **{x.get('field', '')}**: {x.get('meaning', '')}" if isinstance(x, dict) else f"- {x}"
            for x in out_fields
        )
        related = c.get("related_commands") or []
        rel_txt = ", ".join(f"`{x}`" for x in related) if isinstance(related, list) else str(related)
        mistakes = c.get("common_mistakes_fa") or []
        mist_txt = "\n".join(f"- {m}" for m in mistakes) if isinstance(mistakes, list) else str(mistakes)
        kw = c.get("search_keywords") or []
        kw_txt = ", ".join(kw) if isinstance(kw, list) else str(kw)
        aliases = c.get("aliases") or []
        alias_txt = ", ".join(aliases) if isinstance(aliases, list) else str(aliases)
        prereq = c.get("prerequisites_fa") or []
        prereq_txt = "\n".join(f"- {x}" for x in prereq) if isinstance(prereq, list) else str(prereq)

        full = (
            f"# {c.get('title_fa') or cmd}\n\n"
            f"## دستور\n```text\n{cmd}\n```\n"
            f"**Aliases:** {alias_txt}\n\n**Syntax:** `{c.get('syntax') or cmd}`\n\n"
            f"## چه زمانی\n{c.get('when_to_use_fa') or ''}\n\n"
            f"## پیش‌نیاز\n{prereq_txt or '- —'}\n\n"
            f"## آرگومان‌ها\n{chr(10).join(arg_lines) if arg_lines else '- —'}\n\n"
            f"## مراحل\n{steps_txt or '- —'}\n\n"
            f"## نمونه خروجی\n```text\n{c.get('sample_output') or ''}\n```\n\n"
            f"## فیلدهای خروجی\n{of_txt or '- —'}\n\n"
            f"## دستورات مرتبط\n{rel_txt or '—'}\n\n"
            f"## اشتباهات رایج\n{mist_txt or '- —'}\n\n"
            f"## Lab\n{c.get('lab_hint_fa') or ''}\n\n"
            f"## امنیت\n{c.get('security_notes_fa') or ''}\n\n"
            f"## کلیدواژه جستجو\n{kw_txt}\n"
        )
        notes = ""
        flash = c.get("flashcards")
        assess = c.get("assessment")
        meta = {}
        if assess:
            meta["assessment"] = assess
            notes += "\n\n<!-- EJ_ASSESSMENT\n" + json.dumps(assess, ensure_ascii=False) + "\n-->\n"
        if flash:
            meta["flashcards"] = flash
            notes += "\n\n<!-- EJ_FLASHCARDS\n" + json.dumps(flash, ensure_ascii=False) + "\n-->\n"

        lesson_uid = c.get("uid") or f"lesson:ch{ch:02d}:cmd:{i:04d}"
        out.append({
            "uid": lesson_uid,
            "chapter_order": ch,
            "subchapter_order": sub_order,
            "lesson_order": i,
            "level": level,
            "title_fa": title_fa,
            "title_en": c.get("title_en") or cmd,
            "summary": (c.get("when_to_use_fa") or title_fa)[:220],
            "full_content": full,
            "commands": cmd + (("\n" + alias_txt) if alias_txt else ""),
            "examples": c.get("sample_output") or "",
            "notes": notes.strip(),
            "meta": meta,
            "source_status": "review_required",
        })
    return out


def blueprint_to_lessons(d, focus_keywords, default_ch):
    out, li = [], 0
    for ch in (d.get("curriculum") or {}).get("chapters") or []:
        ch_title = ch.get("title_fa") or ""
        for ci, col in enumerate(ch.get("collections") or [], 1):
            for les in col.get("lessons") or []:
                for sub in les.get("sub_lessons") or []:
                    title = sub.get("title_fa") or les.get("title_fa") or "درس"
                    content = sub.get("content") or ""
                    status = sub.get("status") or ""
                    blob = (title + " " + content + " " + ch_title).upper()
                    if focus_keywords and not any(k.upper() in blob for k in focus_keywords):
                        continue
                    if status == "seeded" and len(content) < 350:
                        continue
                    if len(content) < 350 and status not in ("reviewed_content", "developed"):
                        continue
                    li += 1
                    target = default_ch
                    if any(k in blob for k in ("OSPF", "BGP", "REDIS", "EIGRP", "ROUTE-MAP")):
                        target = 14
                    if any(k in blob for k in ("IPSEC", "IKE", "SSL VPN", "PHASE", "TUNNEL", "VPN")):
                        target = 57
                    full = content
                    if sub.get("commands"):
                        full += "\n\n## دستورات\n\n" + str(sub.get("commands"))
                    out.append({
                        "uid": f"lesson:ch{target:02d}:bp:{li:04d}",
                        "title_fa": title if str(title).startswith("[L") else f"[L2] {title}",
                        "chapter_order": target,
                        "subchapter_order": ci,
                        "level": "L2",
                        "summary": (sub.get("summary") or content[:180]).strip(),
                        "full_content": full,
                        "commands": sub.get("commands") or "",
                        "examples": sub.get("examples") or "",
                        "notes": f"blueprint status={status}",
                    })
    return out


CH68_SECTION_TITLES = {
    1: "مبانی و اطلاعات دستگاه",
    2: "رابط‌ها و وضعیت پورت‌ها",
    3: "VLAN و Switching",
    4: "Routing و جدول مسیریابی",
    5: "ACL و کنترل دسترسی",
    6: "NAT و ترجمه آدرس",
    7: "DHCP و DNS",
    8: "VPN و تونل‌ها",
    9: "لاگ، مانیتورینگ و عیب‌یابی",
    10: "پیکربندی، ذخیره‌سازی و مدیریت تغییر",
    11: "امنیت و کاربران",
    12: "سایر دستورات و ابزارها",
    13: "SSH / OpenSSH",
    14: "Telnet و آزمون TCP",
    15: "FTP",
    16: "VoIP / SIP / PBX",
    17: "VMware ESXi / vSphere",
    18: "Zabbix Monitoring",
    19: "Wireshark / TShark",
    20: "Juniper Junos",
    21: "Aruba AOS-CX",
    22: "Proxmox VE",
    23: "Ansible Automation",
    24: "Terraform / Infrastructure as Code",
    25: "Kubernetes / kubectl",
    26: "PowerShell",
    27: "Microsoft Hyper-V",
    28: "FTPS / FTP over TLS",
    29: "SFTP / SSH File Transfer",
    30: "MikroTik RouterOS",
    31: "Cisco IOS / IOS-XE",
    32: "FortiGate / FortiOS",
    33: "Windows Batch / CMD",
    34: "Windows Server / Active Directory",
    35: "Linux / Bash",
    36: "Docker / Compose",
    37: "Ubiquiti UniFi / EdgeOS",
    38: "SNMP / Syslog / NetFlow",
    39: "DNS / DHCP / NTP / IPAM",
    40: "Web Servers / TLS / PKI",
    41: "Cloud CLI / AWS / Azure",
    42: "FortiManager / FortiAnalyzer",
    43: "Security Operations / SIEM / SOC",
    44: "Git / GitHub",
    45: "Backup / Recovery / DR",
}

def _classify_ch68_command(command: str, title: str = ""):
    text = (str(command or "") + " " + str(title or "")).strip().lower()
    rules = [
        (["show version", "show inventory", "show platform", "show clock", "show license", "show environment", "show module"], 1, "مبانی و اطلاعات دستگاه"),
        (["interface", "interfaces", "show ip interface", "show interfaces", "show controllers", "show line"], 2, "رابط‌ها و وضعیت پورت‌ها"),
        (["vlan", "switchport", "spanning-tree", "etherchannel", "port-channel", "mac address-table", "show mac"], 3, "VLAN و Switching"),
        (["ip route", "ipv6 route", "router ospf", "router bgp", "show ip ospf", "show ip bgp", "show ip route", "neighbor", "redistribute"], 4, "Routing و جدول مسیریابی"),
        (["access-list", "access-class", "ip access-group", "ipv6 traffic-filter", "prefix-list", "route-map", "aaa ", "tacacs", "radius"], 5, "ACL و کنترل دسترسی"),
        (["ip nat", "nat ", "overload", "inside source", "inside destination", "show ip nat"], 6, "NAT و ترجمه آدرس"),
        (["dhcp", "dns", "ip helper-address", "domain-name", "name-server"], 7, "DHCP و DNS"),
        (["crypto ike", "crypto ipsec", "tunnel", "vpn", "wireguard", "ipsec"], 8, "VPN و تونل‌ها"),
        (["logging", "syslog", "snmp", "netflow", "show processes", "debug ", "ping ", "traceroute", "show logging", "show tech"], 9, "لاگ، مانیتورینگ و عیب‌یابی"),
        (["copy ", "write memory", "startup-config", "running-config", "archive", "configure terminal", "reload", "boot system", "install "], 10, "پیکربندی، ذخیره‌سازی و مدیریت تغییر"),
        (["username", "enable secret", "password", "crypto key", "ssh", "line vty", "login", "port-security", "storm-control"], 11, "امنیت و کاربران"),
    ]
    for needles, order, label in rules:
        if any(n in text for n in needles):
            return order, label
    return 12, CH68_SECTION_TITLES[12]

def _describe_ch68_command(command: str, section: str) -> str:
    c = str(command or "").strip().lower()
    exact = {
        "show version": "نسخه نرم‌افزار، مدل پلتفرم و اطلاعات پایه دستگاه را نشان می‌دهد؛ برای ثبت وضعیت اولیه و تطبیق قابلیت‌ها استفاده می‌شود.",
        "show running-config": "پیکربندی فعال فعلی را نمایش می‌دهد؛ برای بازبینی تغییرات اعمال‌شده و بررسی تنظیمات جاری به‌کار می‌رود.",
        "show startup-config": "پیکربندی ذخیره‌شده برای راه‌اندازی بعدی را نشان می‌دهد و برای مقایسه با تنظیمات فعال مفید است.",
        "show ip interface brief": "وضعیت و آدرس IP رابط‌ها را به‌صورت خلاصه نشان می‌دهد و برای یافتن رابط‌های down یا بدون آدرس مناسب است.",
        "show interfaces status": "وضعیت پورت‌های سوئیچ، VLAN، سرعت و Duplex را خلاصه می‌کند.",
        "show ip route": "جدول مسیریابی IPv4 و مسیرهای متصل، ایستا و آموخته‌شده را نمایش می‌دهد.",
        "show ipv6 route": "جدول مسیریابی IPv6 را برای بررسی مسیرهای فعال و next-hop نمایش می‌دهد.",
        "show logging": "پیام‌های ثبت‌شده دستگاه را برای بررسی خطاها، رخدادهای رابط و تغییرات اخیر نمایش می‌دهد.",
        "show clock": "زمان و تاریخ فعلی دستگاه را نشان می‌دهد؛ برای تطبیق timestamp لاگ‌ها و رخدادها مهم است.",
        "show vlan brief": "فهرست VLANها و پورت‌های عضو را به‌صورت خلاصه نمایش می‌دهد.",
        "show mac address-table": "آدرس‌های MAC یادگرفته‌شده و پورت مربوط به آن‌ها را برای عیب‌یابی لایه ۲ نمایش می‌دهد.",
        "show spanning-tree": "وضعیت Spanning Tree، نقش پورت‌ها و وضعیت جلوگیری از حلقه لایه ۲ را نشان می‌دهد.",
        "show ip ospf neighbor": "همسایه‌های OSPF و وضعیت مجاورت آن‌ها را برای عیب‌یابی همگرایی بررسی می‌کند.",
        "show ip bgp summary": "وضعیت همسایه‌های BGP، زمان اتصال و شمار پیشوندهای دریافتی را خلاصه می‌کند.",
        "show access-lists": "ACLها و شمارنده تطبیق قوانین را نشان می‌دهد و برای بررسی ترتیب و اثر فیلترها مفید است.",
        "show ip nat translations": "نگاشت‌های فعال NAT را نمایش می‌دهد تا ترجمه آدرس و پورت قابل بررسی باشد.",
        "show ip nat statistics": "آمار عملکرد NAT و شمار ترجمه‌ها را نشان می‌دهد.",
        "show inventory": "شناسه سخت‌افزار، قطعات و شماره سریال اجزای پشتیبانی‌شده را نمایش می‌دهد.",
        "show processes cpu sorted": "فرایندها را بر اساس مصرف CPU مرتب می‌کند تا عامل بار پردازشی بالا شناسایی شود.",
    }
    if c in exact:
        return exact[c]
    if c.startswith("show ") and "route" in c:
        return "اطلاعات جدول مسیریابی را نمایش می‌دهد؛ مسیر مقصد، next-hop و رابط خروجی را بررسی کنید."
    if c.startswith("show ") and ("interface" in c or "interfaces" in c):
        return "وضعیت، آمار یا جزئیات رابط‌های شبکه را نشان می‌دهد؛ خطاها، شمارنده‌ها و وضعیت عملیاتی را بررسی کنید."
    if c.startswith("show ") and ("ospf" in c or "bgp" in c or "eigrp" in c):
        return "وضعیت پروتکل مسیریابی و همسایه‌ها را برای تشخیص مشکل مجاورت یا تبادل مسیر بررسی می‌کند."
    if c.startswith("show ") and ("vlan" in c or "switchport" in c or "spanning-tree" in c):
        return "اطلاعات Switching و VLAN را برای بررسی عضویت پورت، trunk و جلوگیری از حلقه لایه ۲ نمایش می‌دهد."
    if c.startswith("show ") and ("crypto" in c or "ike" in c or "ipsec" in c or "vpn" in c):
        return "وضعیت مؤلفه‌های رمزنگاری یا تونل را نشان می‌دهد؛ مذاکره، همتا و وضعیت SA را بررسی کنید."
    if c.startswith("show "):
        return f"اطلاعات عملیاتی مرتبط با بخش «{section}» را نمایش می‌دهد؛ خروجی را با وضعیت مورد انتظار و لاگ‌های هم‌زمان تطبیق دهید."
    if c.startswith(("configure ", "set ", "ip ", "ipv6 ", "router ", "interface ", "username ", "access-list ", "crypto ", "write ", "copy ", "no ")):
        return f"برای پیکربندی یا تغییر وضعیت در بخش «{section}» استفاده می‌شود. پیش از اجرا، اثر تغییر و امکان بازگشت را در محیط آزمایشگاهی بررسی کنید."
    if c.startswith(("ping ", "traceroute", "tracepath")):
        return "برای بررسی دسترس‌پذیری مقصد یا مسیر عبور بسته‌ها استفاده می‌شود؛ شکست ICMP به‌تنهایی اثبات‌کننده قطعی سرویس نیست."
    return f"دستور مرتبط با بخش «{section}» است. پیش‌نیازها، سطح دسترسی و اثر اجرا را بررسی کرده و نتیجه را در خروجی و لاگ‌ها اعتبارسنجی کنید."


def command_items_to_lessons(data: dict) -> list:
    """Convert chapter-68 command records into categorized, searchable lessons."""
    out = []
    for i, item in enumerate(data.get("items") or [], 1):
        if not isinstance(item, dict):
            continue
        fields = item.get("fields") or {}
        command = str(fields.get("commands") or item.get("title_en") or "").strip()
        title_en = str(item.get("title_en") or command).strip()
        title_fa = re.sub(r"^\[L[0-4]\]\s*", "", str(item.get("title_fa") or title_en)).strip()
        order, section = _classify_ch68_command(command, title_en)
        keywords = sorted(set([command, title_en, title_fa, section, "فصل ۶۸", "دستور شبکه", "عیب‌یابی"]))
        description = _describe_ch68_command(command, section)
        summary = f"{section}: {description}"
        full = (
            f"# {title_fa}\n\n"
            f"بخش: {section}\n\n"
            f"## دستور\n{command}\n\n"
            f"## توضیح و کاربرد\n{description}\n\n"
            f"## روش بررسی\n1. دستگاه، سیستم‌عامل و سطح دسترسی را تأیید کنید.\n"
            f"2. دستور را اجرا کنید: {command}\n"
            f"3. خروجی، پیام خطا و زمان اجرا را ثبت کنید.\n"
            f"4. در صورت تغییر پیکربندی، قبل از ذخیره‌سازی اثر آن را بررسی کنید.\n\n"
            f"## کلیدواژه‌های جستجو\n{', '.join(keywords)}\n\n"
            "## نکته ایمنی\nدستورات تغییردهنده یا مخرب را فقط در محیط مجاز و پس از تهیه نسخه پشتیبان اجرا کنید."
        )
        out.append({
            "uid": item.get("uid") or f"lesson:ch68:cmdsrc:{i:05d}",
            "chapter_order": 68,
            "subchapter_order": order,
            "subchapter_title_fa": section,
            "lesson_order": i,
            "level": "L1",
            "title_fa": title_fa,
            "title_en": title_en,
            "summary": summary,
            "full_content": full,
            "commands": command,
            "examples": "",
            "notes": f"بخش: {section}\nکلیدواژه‌ها: {', '.join(keywords)}",
            "meta": {"category_fa": section, "search_keywords": keywords, "source_uid": item.get("uid")},
            "source_status": "review_required",
        })
    return out


def normalize_pack(path: Path, data: dict):
    if data.get("category") == "commands" and data.get("items"):
        return command_items_to_lessons(data)
    if data.get("commands"):
        return commands_to_lessons(data)
    if data.get("lessons"):
        return data.get("lessons") or []
    name = path.name.upper()
    if "curriculum" in data:
        if any(k in name for k in ("OSPF", "BGP", "REDIS")):
            return blueprint_to_lessons(data, ["OSPF", "BGP", "Redistribution", "Adjacency", "eBGP", "iBGP", "SPF"], 14)
        if "VPN" in name or "IPSEC" in name:
            return blueprint_to_lessons(data, ["IPsec", "IKEv", "SSL VPN", "Phase", "Tunnel", "VPN"], 57)
        return blueprint_to_lessons(data, [], 1)
    return []


def _merge_preserving_text(old, new):
    old = as_text(old).strip()
    new = as_text(new).strip()
    if not old:
        return new
    if not new or new == old or new in old:
        return old
    if old in new:
        return new
    return old + "\n\n---\n\n" + new


def _normalized_title(value):
    value = re.sub(r"^\[L[0-4]\]\s*", "", str(value or "").strip())
    return re.sub(r"\s+", " ", value).casefold()


def apply_fields(les, src):
    for k in ("full_content", "commands", "examples", "notes"):
        if src.get(k):
            les[k] = _merge_preserving_text(les.get(k), src.get(k))
    if src.get("summary"):
        old_summary = as_text(les.get("summary"))
        new_summary = as_text(src.get("summary"))
        les["summary"] = new_summary if len(new_summary) > len(old_summary) else old_summary


def merge_by_title(data, lessons):
    by = {}
    for src in lessons:
        title = (src.get("title_fa") or "").strip()
        by[(src.get("chapter_order"), title)] = src
        bare = re.sub(r"^\[L[0-4]\]\s*", "", title)
        by[(src.get("chapter_order"), bare)] = src
    n = 0
    for ch in data["chapters"]:
        for sub in ch.get("subchapters", []):
            for les in sub.get("lessons", []):
                t = (les.get("title_fa") or "").strip()
                src = by.get((ch.get("order"), t))
                if not src:
                    bare = re.sub(r"^\[L[0-4]\]\s*", "", t)
                    src = by.get((ch.get("order"), bare))
                if src:
                    apply_fields(les, src)
                    n += 1
    return n


def append_unmatched_as_extra(data, lessons, order, title_fa, title_en):
    if not lessons:
        return 0
    data["chapters"] = [c for c in data["chapters"] if c.get("order") != order]
    subs = defaultdict(list)
    for src in lessons:
        subs[src.get("subchapter_order") or 1].append(src)
    out_subs = []
    for si in sorted(subs):
        les_out = []
        for src in sorted(subs[si], key=lambda x: (x.get("lesson_order") or 0)):
            notes = as_text(src.get("notes"))
            ass = (src.get("meta") or {}).get("assessment")
            if ass and "EJ_ASSESSMENT" not in notes:
                notes += "\n\n<!-- EJ_ASSESSMENT\n" + json.dumps(ass, ensure_ascii=False) + "\n-->\n"
            les_out.append({
                "uid": src.get("uid") or f"lesson:ch{order:02d}:s{int(si):03d}:l{len(les_out):04d}",
                "title_fa": src.get("title_fa") or "",
                "title_en": src.get("title_en") or "",
                "level": src.get("level") or "L0",
                "summary": src.get("summary") or "",
                "full_content": src.get("full_content") or "",
                "commands": as_text(src.get("commands")),
                "examples": as_text(src.get("examples")),
                "notes": notes,
            })
        section_title = CH68_SECTION_TITLES.get(int(si), f"بخش {si}") if int(order) == 68 else f"زیرفصل {si}"
        out_subs.append({"title_fa": section_title, "lessons": les_out})
    data["chapters"].append({
        "order": order,
        "title_fa": title_fa,
        "title_en": title_en,
        "subchapters": out_subs,
    })
    return sum(len(s["lessons"]) for s in out_subs)


def append_modular_chapter(data, lessons, order, title_fa, title_en):
    """Append modular lessons without replacing any existing chapter content."""
    if not lessons:
        return 0
    chapter = next((c for c in data["chapters"] if int(c.get("order") or 0) == order), None)
    if chapter is None:
        return append_unmatched_as_extra(data, lessons, order, title_fa, title_en)

    existing_uids = {
        lesson.get("uid")
        for ch in data["chapters"]
        for sub in ch.get("subchapters", [])
        for lesson in sub.get("lessons", [])
        if lesson.get("uid")
    }
    grouped = defaultdict(list)
    for lesson in lessons:
        grouped[int(lesson.get("subchapter_order") or 1)].append(lesson)

    added = 0
    for sub_order in sorted(grouped):
        out = []
        for src in sorted(grouped[sub_order], key=lambda x: int(x.get("lesson_order") or 0)):
            uid = src.get("uid") or f"lesson:ch{order:02d}:mod:{sub_order:03d}:{len(out)+1:05d}"
            if uid in existing_uids:
                base_uid = uid
                uid = f"{base_uid}:moddup:{order:02d}:{int(sub_order):03d}:{len(out)+1:05d}"
                suffix = 2
                while uid in existing_uids:
                    uid = f"{base_uid}:moddup:{order:02d}:{int(sub_order):03d}:{len(out)+1:05d}:{suffix}"
                    suffix += 1
            existing_uids.add(uid)
            src["uid"] = uid
            notes = as_text(src.get("notes"))
            meta = src.get("meta") or {}
            assessment = meta.get("assessment") if isinstance(meta, dict) else None
            if assessment and "EJ_ASSESSMENT" not in notes:
                notes += "\n\n<!-- EJ_ASSESSMENT\n" + json.dumps(assessment, ensure_ascii=False) + "\n-->\n"
            questions = src.get("questions")
            if questions and "EJ_QUESTIONS" not in notes:
                notes += "\n\n<!-- EJ_QUESTIONS\n" + as_text(questions) + "\n-->\n"
            answer_key = src.get("answer_key")
            if answer_key and "EJ_ANSWER_KEY" not in notes:
                notes += "\n\n<!-- EJ_ANSWER_KEY\n" + as_text(answer_key) + "\n-->\n"
            out.append({
                "uid": uid,
                "title_fa": src.get("title_fa") or "",
                "title_en": src.get("title_en") or "",
                "level": src.get("level") or "L0",
                "summary": as_text(src.get("summary")),
                "full_content": as_text(src.get("full_content")),
                "commands": as_text(src.get("commands")),
                "examples": as_text(src.get("examples")),
                "notes": notes,
            })
        if out:
            section_title = CH68_SECTION_TITLES.get(int(sub_order), f"بخش {sub_order}") if int(order) == 68 else f"محتوای افزوده — زیرفصل {sub_order}"
            chapter.setdefault("subchapters", []).append({
                "title_fa": section_title,
                "lessons": out,
            })
            added += len(out)
    return added


def ensure_unique_uids(data):
    """Keep every lesson while repairing UID collisions deterministically."""
    seen = set()
    fixed = 0
    for chapter in data.get("chapters", []):
        order = int(chapter.get("order") or 0)
        for sub_index, sub in enumerate(chapter.get("subchapters", []), 1):
            for lesson_index, lesson in enumerate(sub.get("lessons", []), 1):
                base = str(lesson.get("uid") or f"lesson:ch{order:02d}:s{sub_index:03d}:l{lesson_index:05d}")
                candidate = base
                if candidate in seen:
                    candidate = f"{base}:dedup:{order:02d}:{sub_index:03d}:{lesson_index:05d}"
                    suffix = 2
                    while candidate in seen:
                        candidate = f"{base}:dedup:{order:02d}:{sub_index:03d}:{lesson_index:05d}:{suffix}"
                        suffix += 1
                    lesson["uid"] = candidate
                    fixed += 1
                else:
                    lesson["uid"] = candidate
                seen.add(candidate)
    if fixed:
        print("UID collisions repaired without dropping lessons:", fixed)
    return fixed


def build_ch65(lessons):
    subs = defaultdict(list)
    for les in lessons:
        subs[les.get("subchapter_order") or 1].append(les)
    out = []
    for si in sorted(subs):
        items = sorted(subs[si], key=lambda x: (x.get("lesson_order") or 0, x.get("level") or ""))
        seen, les_out = set(), []
        for src in items:
            uid = src.get("uid") or f"lesson:ch65:s{int(si):03d}:l{len(les_out):04d}"
            if uid in seen:
                continue
            seen.add(uid)
            notes = as_text(src.get("notes"))
            ass = (src.get("meta") or {}).get("assessment")
            if ass and "EJ_ASSESSMENT" not in notes:
                notes += "\n\n<!-- EJ_ASSESSMENT\n" + json.dumps(ass, ensure_ascii=False) + "\n-->\n"
            les_out.append({
                "uid": uid,
                "title_fa": src.get("title_fa") or "",
                "title_en": src.get("title_en") or "",
                "level": src.get("level") or "L0",
                "summary": src.get("summary") or "",
                "full_content": src.get("full_content") or "",
                "commands": as_text(src.get("commands")),
                "examples": as_text(src.get("examples")),
                "notes": notes,
            })
        out.append({"title_fa": f"زیرفصل {si}", "lessons": les_out})
    return {
        "order": 65,
        "title_fa": "فصل ۶۵: امنیت سایبری و هک اخلاقی (دفاعی) + بی‌سیم",
        "title_en": "Ch65 Security Ethical Hacking Wireless",
        "subchapters": out,
    }


def main():
    if not GZ.is_file():
        print("ERROR missing", GZ)
        sys.exit(1)
    data = json.loads(gzip.open(GZ, "rt", encoding="utf-8").read())
    packs = find_pack_files()
    print("packs", len(packs))
    sec, wireless = [], []
    routing_extra, vpn_extra, cmd_extra = [], [], []
    modular_chapters = {}
    for p in packs:
        try:
            d = load_json(p)
        except Exception as e:
            print(" skip", p.name, e)
            continue
        name = str(p).replace("\\", "/").lower()
        lessons = normalize_pack(p, d)
        print(" ", p.name, "lessons", len(lessons))
        if not lessons:
            continue
        if "commands_additional_technologies.json" in name:
            # Process this additive pack before the generic chapter-pack branch.
            # Do not replace Chapter 68 or duplicate stable UIDs on repeated builds.
            existing_uids = {
                lesson.get("uid")
                for chapter in data.get("chapters", [])
                for sub in chapter.get("subchapters", [])
                for lesson in sub.get("lessons", [])
                if lesson.get("uid")
            }
            entry = modular_chapters.setdefault(68, {
                "title_fa": "فصل ۶۸: دانشنامه جامع دستورات",
                "title_en": "Ch68 Commands Encyclopedia",
                "lessons": [],
            })
            staged_uids = {lesson.get("uid") for lesson in entry["lessons"] if lesson.get("uid")}
            added_from_pack = 0
            for idx, lesson in enumerate(lessons, 1):
                lesson = dict(lesson)
                lesson.setdefault("chapter_order", 68)
                lesson.setdefault("lesson_order", idx)
                uid = lesson.get("uid")
                if uid and (uid in existing_uids or uid in staged_uids):
                    continue
                entry["lessons"].append(lesson)
                if uid:
                    staged_uids.add(uid)
                added_from_pack += 1
            print("ch68 additional technology lessons", added_from_pack)
            continue
        if "tools/chapters/" in name and d.get("chapter_order") is not None:
            order = int(d["chapter_order"])
            chapter_title_fa = d.get("chapter_title_fa") or d.get("title_fa") or ("فصل " + str(order))
            chapter_title_en = d.get("chapter_title_en") or d.get("title_en") or ("Chapter " + str(order))
            if d.get("merge_strategy") == "by_title":
                existing_titles = {
                    _normalized_title(lesson.get("title_fa"))
                    for ch in data.get("chapters", []) if int(ch.get("order") or 0) == order
                    for sub in ch.get("subchapters", []) for lesson in sub.get("lessons", [])
                }
                matched, unmatched = [], []
                for idx, original in enumerate(lessons, 1):
                    lesson = dict(original)
                    lesson["chapter_order"] = order
                    lesson.setdefault("subchapter_order", 1)
                    lesson.setdefault("lesson_order", idx)
                    lesson.setdefault("uid", f"lesson:ch{order:02d}:pack:{idx:05d}")
                    if _normalized_title(lesson.get("title_fa")) in existing_titles:
                        matched.append(lesson)
                    else:
                        unmatched.append(lesson)
                merged_count = merge_by_title(data, matched) if matched else 0
                added_count = append_modular_chapter(
                    data, unmatched, order, chapter_title_fa, chapter_title_en
                ) if unmatched else 0
                print("canonical chapter pack", order, "title-merged", merged_count, "new", added_count)
                continue
            entry = modular_chapters.setdefault(order, {
                "title_fa": chapter_title_fa,
                "title_en": chapter_title_en,
                "lessons": [],
            })
            pack_id = str(p.relative_to(ROOT / "tools" / "chapters").with_suffix(""))
            pack_id = re.sub(r"[^a-zA-Z0-9_-]+", "-", pack_id.replace("\\", "/").replace("/", "-")).strip("-") or "pack"
            for idx, lesson in enumerate(lessons, 1):
                lesson = dict(lesson)
                lesson.setdefault("chapter_order", order)
                lesson.setdefault("subchapter_order", 1)
                lesson.setdefault("lesson_order", idx)
                lesson.setdefault("uid", f"lesson:ch{order:02d}:mod:{pack_id}:{idx:05d}")
                entry["lessons"].append(lesson)
            continue
        if "security_ethical" in name:
            sec.extend(lessons)
            continue
        if "wireless" in name and "vpn" not in name:
            wireless.extend(lessons)
            continue
        if d.get("commands") or "commands_encyclopedia" in name:
            cmd_extra.extend(lessons)
            continue
        n = merge_by_title(data, lessons)
        print("   title-merge", n)
        if "ospf" in name or "bgp" in name or "redistribution" in name or "routing_deep" in name:
            routing_extra.extend(lessons)
        if "vpn" in name or "ipsec" in name:
            vpn_extra.extend(lessons)

    for order, chapter in sorted(modular_chapters.items()):
        n = append_modular_chapter(data, chapter["lessons"], order, chapter["title_fa"], chapter["title_en"])
        print("modular chapter", order, n)

    if routing_extra:
        n = append_unmatched_as_extra(
            data, routing_extra, 66,
            "فصل ۶۶: مسیریابی عمیق OSPF/BGP/Redistribution",
            "Ch66 Routing Deep OSPF BGP",
        )
        print("ch66 routing", n)
    if vpn_extra:
        n = append_unmatched_as_extra(
            data, vpn_extra, 67,
            "فصل ۶۷: VPN سازمانی IPsec/SSL و عیب‌یابی",
            "Ch67 Enterprise VPN",
        )
        print("ch67 vpn", n)
    if cmd_extra:
        n = append_unmatched_as_extra(
            data, cmd_extra, 68,
            "فصل ۶۸: دانشنامه جامع دستورات",
            "Ch68 Commands Encyclopedia",
        )
        print("ch68 commands", n)

    # Preserve the canonical Chapter 65 already populated from tools/chapters/ch65_*/chapter.json.
    # Only append legacy security/wireless records if an older source format supplied them;
    # never replace or drop the baseline chapter or its canonical additions.
    extra = list(sec)
    for w in wireless:
        w = dict(w)
        w["subchapter_order"] = 100 + int(w.get("subchapter_order") or 8)
        extra.append(w)
    if extra:
        n = append_modular_chapter(
            data,
            extra,
            65,
            "فصل ۶۵: امنیت سایبری و هک اخلاقی (دفاعی) + بی‌سیم",
            "Ch65 Security Ethical Hacking Wireless",
        )
        print("ch65 legacy additions", n)

    ensure_unique_uids(data)
    data["chapters"].sort(key=lambda c: int(c.get("order") or 0))
    n = sum(len(s.get("lessons", [])) for c in data["chapters"] for s in c.get("subchapters", []))
    data["lesson_count"] = n
    data["version"] = int(data.get("version") or 7) + 1
    GZ.write_bytes(
        gzip.compress(json.dumps(data, ensure_ascii=False, separators=(",", ":")).encode("utf-8"), 9)
    )
    print("FINAL chapters", len(data["chapters"]), "lessons", n, "version", data["version"])
    for c in data["chapters"][-6:]:
        print(" ", c["order"], c["title_fa"][:52], sum(len(s["lessons"]) for s in c["subchapters"]))


if __name__ == "__main__":
    main()
