# MEGA-CHAPTER MAP — ساختار جدید هدف

**تاریخ ثبت:** 2026-10-18  
**درخواست کاربر:** شبکه یک فصل کامل، سیسکو یک فصل کامل، میکروتیک یک فصل کامل، و بقیه به همین شکل.

این سند **نقشه هدف** است. هنوز full_curriculum.py و DB را عوض نکرده‌ایم؛ اول نقشه را قفل می‌کنیم، بعد مهاجرت محتوا را مرحله‌به‌مرحله انجام می‌دهیم.

---

## اصول طراحی

1. **یک موضوع بزرگ = یک فصل اصلی** (نه ده‌ها فصل ریز).
2. داخل هر فصل اصلی، **زیر‌فصل (Level / Section)** و درس‌ها (L0–L4) می‌آید.
3. محتوا می‌تواند خیلی حجیم باشد (چند مگابایت در هر فصل). کیفیت و عدم هنگ مهم‌تر از تعداد فصل است.
4. پک‌های موجود (Cisco switching, MikroTik, FortiGate, Windows Server, VPN, Routing deep و ...) بدون دور ریختن، به فصل اصلی مربوطه منتقل می‌شوند.
5. uid درس‌ها تا حد ممکن حفظ می‌شود (compatibility).

---

## فهرست فصل‌های اصلی پیشنهادی (Mega Chapters)

| کد | عنوان فارسی | عنوان انگلیسی | پوشش اصلی |
|----|-------------|---------------|----------|
| **M01** | مبانی IT و سخت‌افزار | IT Fundamentals & Hardware | CPU, Motherboard, RAM, Storage, PSU, Assembly, Server HW, BIOS/UEFI |
| **M02** | سیستم‌عامل و فایل‌سیستم | Operating Systems & Filesystems | Windows/Linux basics, Process, FS, RAID, LVM, Boot |
| **M03** | مبانی شبکه (همه مطالب شبکه) | Network Fundamentals | OSI, TCP/IP, Ethernet, Switching basics, IPv4/IPv6, Subnetting, ARP, ICMP, TCP/UDP, DNS, DHCP, Cabling, Fiber, Packet Journey |
| **M04** | سیسکو (فصل کامل) | Cisco Complete | Switching (VLAN, STP, EtherChannel, ...), Routing (OSPF, EIGRP, BGP), MPLS, VXLAN/EVPN, Security, Automation, Troubleshooting |
| **M05** | میکروتیک (فصل کامل) | MikroTik Complete | RouterOS basics, Routing, Firewall, NAT, QoS, VPN, HA, Wireless, Scripting, Troubleshooting |
| **M06** | فایروال و امنیت لبه | Firewall & Edge Security | FortiGate, pfSense, OPNsense, Sophos, Policy design, IPS/IDS, VPN gateway |
| **M07** | وایرلس سازمانی | Enterprise Wireless | Wi-Fi design, Controller, PtP/PtMP, Security, Capacity, Troubleshooting |
| **M08** | ویندوز سرور و اکتیو دایرکتوری | Windows Server & AD | Server Core, AD DS, DNS/DHCP/NPS, File/Print/DFS, GPO, Endpoint security, Entra ID, M365, PowerShell |
| **M09** | لینوکس سازمانی | Linux Enterprise | Admin, Networking, Services (Web/DB), Security, Hardening, Automation |
| **M10** | مجازی‌سازی و کانتینر | Virtualization & Containers | VMware, Hyper-V, Proxmox, Docker, Kubernetes |
| **M11** | کلود و شبکه ابری | Cloud & Cloud Networking | AWS VPC, Azure VNet, Hybrid, IAM, CSPM, FinOps |
| **M12** | ذخیره‌سازی، Backup و DR | Storage, Backup & DR | SAN/NAS, iSCSI, Ceph, Backup strategies, Veeam, RPO/RTO |
| **M13** | دیتاسنتر، HA و مانیتورینگ | Data Center, HA & Monitoring | Leaf-Spine, HA/LB, SNMP, Zabbix, Prometheus, ELK, SIEM |
| **M14** | اتوماسیون و AI در IT | Automation & AI for IT | Python (Netmiko/NAPALM), Ansible, Terraform, CI, ChatOps, RAG, Ollama |
| **M15** | دیتابیس و امنیت آن | Database & DB Security | SQL Server, PostgreSQL, MySQL, MongoDB, Redis, TDE, Hardening |
| **M16** | VoIP، CCTV و IoT | VoIP, CCTV & IoT | SIP, Asterisk/Issabel, Panasonic, IP Camera, Access Control, IoT segmentation |
| **M17** | امنیت جامع (Zero Trust تا SOC) | Comprehensive Security | Zero Trust, ITIL, Network Sec, Endpoint/AppSec, DevSecOps, SOC, IR, Hunting, Forensics |
| **M18** | عیب‌یابی و لاب‌های سازمانی | Troubleshooting & Org Labs | Methodology, Tools, Ethical Lab (authorized only), 20+ Capstone Labs |
| **M19** | دانشنامه دستورات | Commands Encyclopedia | Chapter 68 style — multi-vendor command reference |
| **M20** | Git و ابزارهای مهندسی | Git & Engineering Tools | Git workflows, CI basics, documentation |

---

## نگاشت فصل‌های قدیمی → فصل‌های جدید

| فصل‌های قدیمی | فصل جدید |
|---------------|----------|
| 01, 02, 03 | **M01** مبانی IT و سخت‌افزار |
| 04, 05 | **M02** سیستم‌عامل و فایل‌سیستم |
| 06, 07, 08, 09, 10, 11, 12 | **M03** مبانی شبکه (همه مطالب شبکه) |
| 13, 14, 15, 16, 17 + بخش سیسکو routing deep | **M04** سیسکو کامل |
| 19, 20, 21 | **M05** میکروتیک کامل |
| 24, 25 | **M06** فایروال و امنیت لبه |
| 22, 23 | **M07** وایرلس |
| 28, 29, 30, 31, 32, 33, 34, 35 | **M08** ویندوز سرور و AD |
| 36, 37, 38, 39 | **M09** لینوکس |
| 40, 41, 42 | **M10** مجازی‌سازی و کانتینر |
| 43, 44 | **M11** کلود |
| 45, 46 | **M12** Storage / Backup / DR |
| 47, 48, 49, 50 | **M13** DC / HA / Monitoring |
| 51 | **M14** اتوماسیون و AI |
| 52, 53 | **M15** دیتابیس |
| 54, 55 | **M16** VoIP / CCTV / IoT |
| 26, 27, 56, 57, 58, 59 | **M17** امنیت جامع |
| 60 | **M18** عیب‌یابی و لاب |
| 68 | **M19** دانشنامه دستورات |
| 64 | **M20** Git |

---

## ساختار پوشه پیشنهادی (tools/packs)

```
tools/packs/
├── M03_network_fundamentals/
│   ├── README.md
│   ├── manifest.json
│   ├── lessons/
│   ├── scenarios/
│   ├── packet_journeys/
│   ├── diagrams/
│   ├── scripts/
│   └── notes/
├── M04_cisco_complete/
├── M05_mikrotik_complete/
├── M06_firewall_edge/
├── ...
└── M19_commands_encyclopedia/
```

هر فصل اصلی می‌تواند ده‌ها زیر‌بخش و صدها درس داشته باشد بدون اینکه UI هنگ کند (بارگذاری سطح‌به‌سطح).

---

## مزایای این مدل

- کاربر دقیقاً می‌داند کجا برود: «سیسکو» یک جا، «میکروتیک» یک جا، «شبکه» یک جا.
- تولید محتوا با AI خیلی تمیزتر می‌شود (یک پرامپت بزرگ برای یک فصل کامل).
- پک‌های حجیم موجود (۵–۱۰ مگابایتی) بدون شکستن، داخل فصل مربوطه جا می‌گیرند.
- تعداد فصل‌های سطح بالا کم می‌شود → مدیریت و ممیزی آسان‌تر.

---

## وضعیت اجرا

| مرحله | وضعیت |
|-------|--------|
| ثبت نقشه | انجام شد (همین فایل) |
| تأیید کاربر | در انتظار |
| به‌روزرسانی full_curriculum / seed | بعد از تأیید |
| مهاجرت پک‌های موجود | بعد از تأیید |
| ساخت پوشه‌های M0x | بعد از تأیید |

---

## درخواست از کاربر

لطفاً این نقشه را بررسی کن و بگو:

1. آیا تعداد و نام فصل‌های اصلی (M01–M20) مورد تأیید است؟
2. چیزی باید جدا یا ادغام شود؟ (مثلاً آیا وایرلس داخل شبکه برود یا جدا بماند؟)
3. آیا می‌خواهی از **M03 شبکه** یا **M04 سیسکو** یا **M05 میکروتیک** اول شروع کنیم؟
