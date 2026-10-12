# ماتریس پوشش جامع NetworkAll — از صفر تا طراحی فوق‌تخصصی

> **وضعیت این سند:** نقشهٔ کار و معیار پذیرش است؛ «وجود فصل» یا «وجود Pack» به معنی تکمیل یا تأیید علمی آن نیست. تا وقتی UIDهای پشتیبان، آزمون عملی و نتیجهٔ بازبینی ثبت نشوند، هیچ شایستگی‌ای `covered` اعلام نمی‌شود.

## ۱. تعریف وضعیت‌ها

- `covered`: درس‌های مشخص با UID، مثال/آزمایش اختصاصی، پاسخ‌نامهٔ منطبق، منبع معتبر و نتیجهٔ بررسی فنی ثبت شده‌اند.
- `in_progress`: منبع/Pack مرتبط هست، اما پوشش کامل یا اجرای آزمایش تأیید نشده است.
- `gap`: برای شایستگی، مدرک کافی در ماتریس وجود ندارد. این وضعیت **به معنی نبود قطعی همهٔ محتوا در کل مخزن نیست**؛ ابتدا باید inventory انجام شود.
- `quarantined`: منبع حفظ شده ولی فعلاً تا زمان بازنویسی از ادغام فعال خارج است.
- `audit_pending` و `review_required` وضعیت مدیریتی Packها هستند و معادل `covered` نیستند.

## ۲. مدل عمق برای هر حوزه

هر حوزه باید مسیر پیوستهٔ L0 تا L4 داشته باشد. عناوین سطوح، مجوز تکرار متن نیستند.

| سطح | خروجی قابل‌سنجش | حداقل عمق راهنما | ارزیابی پیشنهادی |
|---|---|---|---|
| L0 — مبانی | توضیح اصطلاحات با زبان ساده، ترسیم مدل ذهنی و پیش‌بینی رفتار ساده | ۶۰۰ واژهٔ مرتبط | حداقل ۵ سؤال مفهومی |
| L1 — اجرای پایه | اجرای مستقل وظیفهٔ استاندارد و تشخیص نتیجهٔ سالم | ۸۰۰ واژه | حداقل ۸ سؤال + تمرین |
| L2 — حرفه‌ای | کار با چند حالت، خروجی واقعی، لاگ و بازیابی خطا | ۱۲۰۰ واژه | حداقل ۱۰ سؤال + دو آزمایش برای مهارت پیچیده |
| L3 — خبره | تحلیل رفتار داخلی، تعامل زیرسیستم‌ها، failure mode و تفسیر trace | ۱۶۰۰ واژه | حداقل ۱۲ سؤال، edge case و عیب‌یابی چندمرحله‌ای |
| L4 — فوق‌متخصص | طراحی معماری، trade-off، ظرفیت، امنیت، interoperability و دفاع از تصمیم | ۲۲۰۰ واژه | حداقل ۱۵ سؤال، case study و آزمون شکست/کارایی در صورت موضوعیت |

این اعداد کف‌های راهنما برای درس مفهومی هستند، نه سقف حجم و نه معیار خودکار قبولی. مرجع فرمان، آزمایشگاه، سناریو و فلش‌کارت قرارداد اختصاصی دارند. هیچ تعداد کلی و ثابتی برای رکوردها تعیین نمی‌شود.

## ۳. ماتریس حوزه‌ها و شایستگی‌ها

برای هر ردیف باید UID درس‌ها، شناسهٔ Pack و وضعیت واقعی ممیزی در گزارش ماشین‌خوانده ثبت شود. وضعیت‌های زیر بر پایهٔ فهرست موجود Packها و نبود گزارش پوشش تأییدشده تنظیم شده‌اند؛ اجرای نهایی هنوز لازم است.

| حوزه | پوشش لازم از L0 تا L4 | وضعیت اولیه | منابع/اقدام |
|---|---|---|---|
| مبانی کامپیوتر و سخت‌افزار | CPU، RAM، cache، bus، ذخیره‌سازی، UEFI/BIOS، POST، firmware، درایور، عیب‌یابی قطعه و performance | in_progress — نیازمند inventory | فصل‌های پایه را با ماتریس قطعه/علائم/آزمون/نتیجه تطبیق بده |
| مبانی شبکه و مدل‌های مرجع | OSI و TCP/IP، encapsulation، MTU، broadcast/collision domain، Ethernet، NIC، duplex، latency/jitter/loss | in_progress — Pack مسیر Packet Journey سطح L0-L4 اضافه شد؛ Lab هنوز اجرا نشده | `tools/packs/network_foundations/packet_path_deep_pack.json`؛ برای ادعای covered باید اجرا، بازبینی فنی و report نتیجه ثبت شود |
| IPv4/IPv6 و subnetting | binary math، CIDR، VLSM، route aggregation، ARP/NDP، SLAAC/DHCPv6، ICMP، PMTUD و آدرس‌های ویژه | in_progress — نیازمند inventory | برای هر مهارت مثال محاسباتی با answer key و آزمون مرزی داشته باشد |
| Switching و VLAN | MAC/CAM، unknown unicast flooding، access/trunk، 802.1Q، native VLAN، STP/RSTP, LACP/EtherChannel، port security، L2 loop | in_progress | Pack سوئیچینگ و فرمان‌ها به تفکیک سازنده، نسخه و خروجی ممیزی شوند |
| Routing و پروتکل‌ها | static/default route، longest-prefix match، administrative distance، OSPF، BGP، redistribution، ECMP، convergence و route leak | in_progress — Pack تکمیلی L0-L4 ساخته شد | `tools/packs/chapter14/advanced_routing_engineering_ch14_pack.json` و Packهای قبلی؛ Labها هنوز اجرا نشده‌اند |
| سرویس‌های شبکه | DHCP/DORA/relay، DNS/recursive-authoritative/cache، NTP، NAT/PAT، ICMP، proxy، QoS و MTU/MSS | in_progress — Packهای عمیق DNS و DHCP و همچنین RouterOS Firewall/NAT/QoS ثبت شدند؛ Labها هنوز اجرا نشده‌اند | `tools/packs/network_services/dns_recursive_deep_pack.json`، `tools/packs/network_services/dhcp_dora_deep_pack.json`، `tools/packs/mikrotik/routeros_routing_firewall_ch20_pack.json`، `tools/packs/mikrotik/routeros_qos_vpn_ha_ch21_pack.json`؛ NTP/proxy و آزمون‌های عملی هنوز نیازمند تکمیل‌اند |
| MPLS، VRF و L3VPN | VRF، RD/RT، MPLS labels، LDP، MP-BGP VPNv4/VPNv6، route leaking، tenant isolation و ظرفیت | in_progress — Pack تکمیلی L0-L4 ساخته شد | `tools/packs/chapter15/mpls_vrf_l3vpn_ch15_pack.json`؛ Labها اجرا نشده‌اند |
| Multicast | IGMP/MLD، snooping، querier، PIM، RP، RPF، ASM/SSM، IPTV و عیب‌یابی چندنقطه‌ای | in_progress — Pack تکمیلی L0-L4 ساخته شد | `tools/packs/network_services/multicast_network_engineering_ch16_pack.json`؛ Labها اجرا نشده‌اند |
| EVPN/VXLAN و Data Center Fabric | underlay/overlay، VTEP/VNI، EVPN route types، anycast gateway، multi-homing و tenant isolation | in_progress — Pack تکمیلی L0-L4 ساخته شد | `tools/packs/data_center/evpn_vxlan_engineering_ch17_pack.json`؛ Labها اجرا نشده‌اند |
| SDN، SD-WAN و SASE | control/data plane، SLA/path selection، controller resilience، ZTNA، SWG/CASB/FWaaS، privacy و rollback | in_progress — Pack تکمیلی L0-L4 ساخته شد | `tools/packs/wan_design/sdn_sdwan_sase_ch18_pack.json`؛ Labها اجرا نشده‌اند |
| Wireless | RF basics، کانال/پهنای کانال، dBm/SNR، interference، roaming، association، WPA2/WPA3، 802.1X/RADIUS و طراحی پوشش | in_progress | Pack امنیت بی‌سیم و آموزش وایرلس باید با آزمایش مجاز و hardware/version note بازبینی شوند |
| ISP، مودم/ONT و WAN | bridge/router mode، PPPoE، DHCP WAN، CGNAT/double NAT، VLAN ISP، optical basics، radio links، failover و SLA | gap — مدرک پوشش نیازمند استخراج | نمودارهای نقش تجهیزات و سناریوهای تشخیص خطا افزوده شوند |
| Cisco IOS/IOS-XE و سایر CLIها | mode/privilege، syntax، show/debug، config/commit/save، backup/restore، ACL، VLAN، routing و rollback | in_progress | هر فرمان دارای پیش‌شرط، syntax، خروجی معتبر، تفسیر، اثر، نسخه و منبع رسمی باشد |
| MikroTik RouterOS | WinBox/CLI، bridge/VLAN filtering، DHCP/DNS، firewall chains/conntrack، NAT، routes/OSPF/BGP، queues، VPN/VRRP، backup/export | in_progress — بسته‌های فصل ۱۹، ۲۰ و ۲۱ با پنج سطح L0-L4 ثبت شدند؛ Labهای release-target هنوز اجرا نشده‌اند | `tools/packs/mikrotik/routeros_foundations_ch19_pack.json`، `tools/packs/mikrotik/routeros_routing_firewall_ch20_pack.json`، `tools/packs/mikrotik/routeros_qos_vpn_ha_ch21_pack.json`؛ اجرای عملی، peer review و validation روی release هدف لازم است |
| Windows Client/Server | نصب، boot, services, Event Viewer, AD DS, DNS/DHCP, GPO, NTFS/SMB, certificates, RDP, patching, HA, recovery | in_progress | Pack ویندوز موجود است؛ پوشش role-by-role و نسخه‌ها هنوز باید ممیزی شود |
| PowerShell و batch | pipeline objects، parameters، functions/modules، remoting، CIM/WMI، jobs، error handling، signing، tests، idempotency، logging و security | in_progress | دستورها، اسکریپت‌های عملی و سناریوهای خطا به جای boilerplate عمومی |
| Linux | boot/systemd، process، permissions/ACL، filesystem/mount، storage، networking، nftables، logs، SSH، package mgmt، containers و recovery | gap — مدرک پوشش نیازمند استخراج | فصل‌ها به مسیر admin → services → performance → incident → architecture متصل شوند |
| Git/GitHub | object graph، refs/index/working tree، branching، merge/rebase، conflict، revert/reflog، tags/releases، PR، CI و secret hygiene | in_progress | فصل Git موجود است؛ map هر مفهوم به سناریو و recovery و راستی‌آزمایی |
| Python و اتوماسیون | data model، exceptions، I/O، HTTP/API، concurrency، types، packaging، logging، pytest، mocks، security، profiling و deployment | in_progress | Pack اتوماسیون موجود است؛ نمونه‌ها باید اجراشدنی و testable باشند |
| پایگاه‌داده و SQL | schema/keys/indexes، transactions/ACID، query plans، isolation، migrations، backup/restore، integrity و concurrency | gap — مدرک پوشش نیازمند استخراج | نیازمند دورهٔ SQL/SQLite و سناریوهای data recovery با دادهٔ مصنوعی |
| امنیت دفاعی و حریم خصوصی | threat modeling، IAM/least privilege، hardening، PKI/TLS، logs, vuln mgmt، segmentation، backup، incident response و safe lab | in_progress / یک Pack قرنطینه | منبع حفظ شود؛ مطالب قالبی تا بازنویسی اختصاصی وارد کتاب نهایی نشوند |
| مجازی‌سازی و container | hypervisor، virtual switch، snapshot vs backup، images/layers، network/storage, isolation و troubleshooting | gap — مدرک پوشش نیازمند استخراج | دورهٔ مستقل با توپولوژی و سناریوی خرابی لازم است |
| مانیتورینگ و observability | SNMP، syslog، metrics, logs, traces, baselines, SLI/SLO, alert fatigue، capacity planning و root-cause analysis | gap — مدرک پوشش نیازمند استخراج | سناریوهای مبتنی بر شواهد و threshold rationale اضافه شوند |
| برنامه‌ریزی، یادآوری و همگام‌سازی | local persistence، time zone، due/remind، notifications، retries، tombstones، conflicts، offline edits، reconciliation و recovery | in_progress | یادآوری Windows/Android و sync باید در پایان با ساعت واقعی و restart تست شوند |
| مستندسازی، آموزش و capstone | runbook، diagram-as-code، change plan، acceptance tests، incident report، design review و دفاع از trade-off | gap — مدرک پوشش نیازمند استخراج | برای هر حوزه پروژهٔ نهایی end-to-end و rubric مستقل تعریف شود |

## ۴. چطور تعداد رکورد واقعی را تعیین می‌کنیم؟

حجم بر اساس واحدهای شایستگی تعیین می‌شود، نه عدد رُند یا پرکردن سهمیه. برای هر حوزه باید این شمارش ساخته شود:

1. مفاهیم مستقل و رابطه‌های پیش‌نیاز.
2. مهارت‌های اجرایی و هر خانوادهٔ ابزار/سازنده/نسخه که رفتار متفاوت دارد.
3. شاخه‌های عیب‌یابی که تصمیم یا شواهد متفاوت می‌خواهند.
4. آزمایش‌های پایه، حرفه‌ای، شکست کنترل‌شده و کارایی/ظرفیت در موضوع مرتبط.
5. case studyهای واقعی‌نما با دادهٔ مصنوعی، قیود و معیار موفقیت متفاوت.
6. سؤال‌های مفهومی، تحلیل خروجی، محاسبه، تصمیم‌گیری و edge case؛ پاسخ تشریحی هر سؤال جدا.
7. واژه‌نامه، مرجع فرمان/API، checklists و runbookهای کوچک اتمی.

اگر یک فرمان فقط alias همان رفتار در نسخهٔ دیگر است، رکورد تکراری نسازید. اگر خروجی/پارامتر/خطر بین دو نسخه فرق مهم دارد، تفاوت نسخه را با مرجع معتبر مستند کنید. متن طولانی ولی تکراری، «رکورد عمیق» محسوب نمی‌شود.

## ۵. قرارداد ساخت هر درس

هر درس در حد تناسب موضوع باید این بخش‌ها را داشته باشد:

- هویت: UID پایدار، domain، سطح L0-L4، کلیدواژه انگلیسی، نسخه/سازنده و وضعیت تأیید.
- نقشهٔ یادگیری: اهداف قابل‌سنجش، پیش‌نیاز، واژه‌نامه و لینک درس قبل/بعد.
- مدل ذهنی و سازوکار دقیق: ترتیب رخدادها، مرزهای اعتماد، حالت‌های سیستم و علت‌ومعلول.
- مثال گام‌به‌گام: ورودی، استدلال، فرمان/کد، خروجی نمونه و تفسیر.
- آزمایشگاه: محیط و توپولوژی، وضعیت آغازین، مراحل، cleanup، معیار قبولی و نتیجهٔ واقعی یا برچسب «اجرا نشده».
- عیب‌یابی: symptom → evidence → candidate causes → discriminating test → root cause → remediation → verification.
- ایمنی و عملیات: حد دسترسی، side effects، backup، rollback، ریسک نسخه/تجهیزات و سناریوی عدم موفقیت.
- ارزیابی: سؤال‌ها و پاسخ‌نامه با IDهای دقیقاً منطبق؛ پاسخ شامل دلیل و توضیح گزینه‌های غلط باشد.
- منابع: مستند رسمی/RFC/استاندارد/سازنده؛ ادعاهای تغییرپذیر به نسخه مرتبط شوند.

## ۶. اینفوگرافیک‌ها به‌عنوان دارایی‌های مشترک

دارایی مرجع در `shared/infographics/` است و در ویندوز و اندروید از همان SVG/HTML استفاده می‌شود. هر تصویر باید:
- یک مفهوم یا مسیر مشخص را نشان دهد، نه فقط تزئین درس باشد.
- نقش دستگاه/پروتکل، جهت جریان، نقطهٔ تصمیم و محل تغییر encapsulation/state را نشان دهد.
- متن جایگزین (alt)، caption، محدودیت‌های مدل و آزمایش را داشته باشد.
- با یک درس مرجع و حداقل یک لابراتوار/روش تأیید مرتبط شود.
- SVG معتبر، آفلاین، قابل‌مقیاس و بدون وابستگی اینترنتی باشد.

نمودارهای مسیر packet، ARP/NDP، VLAN، TCP، NAT/PAT، Stateful Firewall، OSPF، packet capture و مسیر عیب‌یابی به‌تدریج تکمیل می‌شوند. هیچ نمودار به‌تنهایی جایگزین توضیح عمیق یا lab نیست.

## ۷. دروازهٔ انتشار محتوا

یک Pack فقط زمانی می‌تواند `verified` شود که:
- JSON/schema/UID و ارجاعات ساختاری سالم باشند؛
- بررسی تکرار و پاسخ‌نامهٔ مستقل پاس شود؛
- فرمان‌ها/اسکریپت‌ها در محیط کنترل‌شده اجرا شده باشند یا صریحاً «اجرا نشده» بمانند؛
- خروجی و معیار قبولی برای هر lab ثبت شوند؛
- منابع و نسخه بررسی شوند؛
- گزارش قبل/بعد و دلیل هر حذف/جایگزینی نگه‌داری شود؛
- واردکردن محتوای بزرگ به دیتابیس backup، تراکنش، گزارش خطا و عدم حذف دادهٔ شخصی را اثبات کند.

## ۸. اولویت اجرا

1. inventory تمام فصل‌ها، Packها، UIDها، schema و حجم فشرده/غیرفشرده.
2. گزارش خودکار پوشش و رتبه‌بندی شکاف‌ها؛ بدون حذف خودکار.
3. تکمیل پیش‌نیازهای L0/L1 قبل از L3/L4؛ جلوگیری از شکاف آموزشی.
4. بازنویسی محتوا بر اساس موضوع، نه افزودن رکوردهای قالبی.
5. تکمیل دارایی‌های دیداری و اتصال آن‌ها به درس و آزمایشگاه.
6. پایش یادآوری‌ها، sync و migration در حین توسعه، اما اجرای مجموعهٔ تست نهایی در آخرین مرحله.
7. در پایان: تست واحد/قرارداد، ممیزی محتوا، ساخت اندروید و ویندوز، تست migration/backup، test notifications با deadline واقعی و آزمایش شبکهٔ LAN دوطرفه. فقط نتیجه‌های ثبت‌شده اجازهٔ اعلام آمادگی انتشار می‌دهند.
