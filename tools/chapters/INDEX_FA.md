# فهرست فصل‌ها — NetworkAll

ساختار عددی: هر فصل یک پوشه از ۱ تا ۶۸ دارد؛ متن، سؤال، پاسخ، مثال، دستور و لاب پوشهٔ مستقل دارند.

**راهنمای ممیزی کامل بودن و علت نام‌گذاری نامشخص:**  
[`docs/CHAPTER_COMPLETENESS_AUDIT_FA.md`](../../docs/CHAPTER_COMPLETENESS_AUDIT_FA.md)

### نکته دربارهٔ ستون‌ها

- **درس پایه (baseline):** اسکلت عناوین در `lessons/base_curriculum.json` با الگوی `[L0]…[L4]`
- **درس افزوده (addon):** رکوردهای غنی در `lessons/lessons.json` — اگر ۰ باشد، نام درس‌ها در UI عمدتاً اسکلت سطح‌بندی‌شده است
- نسخهٔ ماشینی: [`index.json`](index.json)

| شماره | عنوان | درس افزوده | درس پایه | وضعیت محتوا | مسیر |
|---:|---|---:|---:|---|---|
| 1 | مبانی IT و معماری کامپیوتر | 0 | 205 | فقط baseline | tools/chapters/1/ |
| 2 | اسمبل، عیب‌یابی و سرورهای سازمانی | 0 | 140 | فقط baseline | tools/chapters/2/ |
| 3 | BIOS UEFI و بوت | 0 | 80 | فقط baseline | tools/chapters/3/ |
| 4 | سیستم‌عامل پایه | 0 | 105 | فقط baseline | tools/chapters/4/ |
| 5 | فایل‌سیستم و Storage پایه | 0 | 105 | فقط baseline | tools/chapters/5/ |
| 6 | مبانی شبکه | 0 | 140 | فقط baseline | tools/chapters/6/ |
| 7 | اترنت و سوییچینگ پایه | 85 | 85 | افزوده دارد | tools/chapters/7/ |
| 8 | IPv4 IPv6 ساب‌نتینگ | 0 | 135 | فقط baseline — حیاتی | tools/chapters/8/ |
| 9 | ARP ICMP TCP UDP | 0 | 115 | فقط baseline | tools/chapters/9/ |
| 10 | DNS | 0 | 115 | فقط baseline | tools/chapters/10/ |
| 11 | DHCP و IPAM | 0 | 80 | فقط baseline | tools/chapters/11/ |
| 12 | کابل‌کشی فیبر رک | 0 | 110 | فقط baseline | tools/chapters/12/ |
| 13 | سوییچینگ سیسکو | 145 | 145 | افزوده دارد | tools/chapters/13/ |
| 14 | مسیریابی پیشرفته | 140 | 140 | افزوده دارد | tools/chapters/14/ |
| 15 | MPLS VRF L3VPN | 0 | 55 | فقط baseline | tools/chapters/15/ |
| 16 | Multicast | 0 | 55 | فقط baseline | tools/chapters/16/ |
| 17 | EVPN VXLAN | 0 | 50 | فقط baseline | tools/chapters/17/ |
| 18 | SDN SD-WAN SASE | 0 | 65 | فقط baseline | tools/chapters/18/ |
| 19 | MikroTik مبانی | 0 | 105 | فقط baseline | tools/chapters/19/ |
| 20 | MikroTik Routing Firewall NAT | 100 | 100 | افزوده دارد | tools/chapters/20/ |
| 21 | MikroTik QoS VPN HA | 35 | 110 | نیمه‌غنی | tools/chapters/21/ |
| 22 | وایرلس سازمانی | 0 | 105 | فقط baseline | tools/chapters/22/ |
| 23 | PtP PtMP | 0 | 60 | فقط baseline | tools/chapters/23/ |
| 24 | FortiGate | 0 | 130 | فقط baseline — حیاتی | tools/chapters/24/ |
| 25 | pfSense OPNsense Sophos | 0 | 65 | فقط baseline | tools/chapters/25/ |
| 26 | PKI TLS | 0 | 100 | فقط baseline | tools/chapters/26/ |
| 27 | AAA NAC | 0 | 60 | فقط baseline | tools/chapters/27/ |
| 28 | Windows Server Core | 40 | 40 | افزوده دارد | tools/chapters/28/ |
| 29 | Active Directory | 105 | 105 | افزوده دارد | tools/chapters/29/ |
| 30 | Windows DNS DHCP NPS | 55 | 55 | افزوده دارد | tools/chapters/30/ |
| 31 | فایل چاپ DFS | 50 | 50 | افزوده دارد | tools/chapters/31/ |
| 32 | امنیت Endpoint ویندوز | 40 | 40 | افزوده دارد | tools/chapters/32/ |
| 33 | Entra ID Hybrid | 0 | 50 | فقط baseline | tools/chapters/33/ |
| 34 | M365 Intune ایمیل | 0 | 60 | فقط baseline | tools/chapters/34/ |
| 35 | PowerShell CMD | 75 | 75 | افزوده دارد | tools/chapters/35/ |
| 36 | مدیریت لینوکس | 0 | 45 | فقط baseline — نازک | tools/chapters/36/ |
| 37 | شبکه لینوکس | 0 | 45 | فقط baseline — نازک | tools/chapters/37/ |
| 38 | سرویس لینوکس وب | 0 | 40 | فقط baseline — نازک | tools/chapters/38/ |
| 39 | امنیت لینوکس | 0 | 45 | فقط baseline — نازک | tools/chapters/39/ |
| 40 | VMware Hyper-V | 0 | 70 | فقط baseline | tools/chapters/40/ |
| 41 | Proxmox Docker | 0 | 55 | فقط baseline | tools/chapters/41/ |
| 42 | Kubernetes | 0 | 65 | فقط baseline | tools/chapters/42/ |
| 43 | شبکه ابری | 0 | 80 | فقط baseline | tools/chapters/43/ |
| 44 | امنیت ابر Governance | 0 | 45 | فقط baseline — نازک | tools/chapters/44/ |
| 45 | Storage سازمانی | 0 | 45 | فقط baseline — نازک | tools/chapters/45/ |
| 46 | Backup DR | 0 | 45 | فقط baseline — نازک | tools/chapters/46/ |
| 47 | Data Center | 0 | 40 | فقط baseline — نازک | tools/chapters/47/ |
| 48 | HA و Load Balancing | 0 | 50 | فقط baseline | tools/chapters/48/ |
| 49 | مانیتورینگ | 0 | 65 | فقط baseline | tools/chapters/49/ |
| 50 | SIEM ELK | 0 | 45 | فقط baseline — نازک | tools/chapters/50/ |
| 51 | اتوماسیون و AI در IT | 75 | 75 | افزوده دارد | tools/chapters/51/ |
| 52 | مدیریت دیتابیس | 0 | 60 | فقط baseline | tools/chapters/52/ |
| 53 | امنیت دیتابیس | 0 | 45 | فقط baseline — نازک | tools/chapters/53/ |
| 54 | VoIP سانترال | 0 | 85 | فقط baseline | tools/chapters/54/ |
| 55 | CCTV Access BMS IoT | 0 | 70 | فقط baseline | tools/chapters/55/ |
| 56 | امنیت پایه Zero Trust ITIL | 0 | 70 | فقط baseline | tools/chapters/56/ |
| 57 | امنیت شبکه | 0 | 45 | فقط baseline — نازک | tools/chapters/57/ |
| 58 | Endpoint AppSec DevSecOps | 0 | 55 | فقط baseline | tools/chapters/58/ |
| 59 | SOC IR Hunting | 0 | 70 | فقط baseline | tools/chapters/59/ |
| 60 | عیب‌یابی هک اخلاقی لاب سازمانی | 18 | 240 | نیمه‌غنی | tools/chapters/60/ |
| 61 | معماری سازمانی Enterprise Architecture | 0 | 145 | فقط baseline | tools/chapters/61/ |
| 62 | عملیات IT و NOC | 0 | 100 | فقط baseline | tools/chapters/62/ |
| 63 | مستندسازی Runbook و CMDB | 0 | 110 | فقط baseline | tools/chapters/63/ |
| 64 | Git و GitHub | 0 | 300 | فقط baseline | tools/chapters/64/ |
| 65 | امنیت سایبری و هک اخلاقی (دفاعی) + بی‌سیم | 135 | 3 | افزوده دارد | tools/chapters/65/ |
| 66 | مسیریابی عمیق OSPF/BGP/Redistribution | 9 | 3 | افزوده کم | tools/chapters/66/ |
| 67 | VPN سازمانی IPsec/SSL و عیب‌یابی | 15 | 3 | افزوده کم | tools/chapters/67/ |
| 68 | دانشنامه جامع دستورات | 2963 | 3 | افزوده زیاد | tools/chapters/68/ |

### خلاصه وضعیت

- **۱۷ فصل** با درس افزوده
- **۵۱ فصل** فقط اسکلت baseline (نام‌ها بیشتر `[L0]…[L4]`)
- تقریباً همه فصل‌ها: `questions` / `answers` / `labs` canonical هنوز خالی
- جزئیات کامل: `docs/CHAPTER_COMPLETENESS_AUDIT_FA.md`
