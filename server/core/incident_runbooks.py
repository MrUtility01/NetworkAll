# -*- coding: utf-8 -*-
"""Evidence-driven, lab-safe incident runbooks for NetworkAll's web learning center.

IP addresses and hostnames are illustrative lab values. Commands are read-only unless a
step is explicitly labelled as a controlled change; always save current configuration
and use the documented rollback in production.
"""
from __future__ import annotations

from copy import deepcopy

INCIDENT_RUNBOOKS = [
    {
        "id": "vlan30-trunk",
        "code": "INC-L2-001",
        "title_fa": "کاربران حسابداری پس از تغییر Trunk از Gateway جدا شده‌اند",
        "title_en": "VLAN 30 omitted from an 802.1Q trunk",
        "domain": "Switching / VLAN",
        "severity": "High",
        "duration": "۲۰ تا ۳۵ دقیقه",
        "environment": "لابراتوار نمونه: SW-CORE و SW-FLOOR-2؛ VLAN 30 = 10.30.30.0/24؛ Gateway = 10.30.30.1؛ کلاینت = 10.30.30.47؛ لینک بین دو سوئیچ = Gi1/0/48.",
        "impact": "فقط کلاینت‌های VLAN 30 در طبقهٔ دوم ارتباط شبکه ندارند؛ VLAN 10 و 20 و مدیریت سوئیچ‌ها سالم هستند.",
        "symptoms": [
            "کلاینت IP و Mask معتبر دارد، اما Gateway پاسخ نمی‌دهد.",
            "کاربران همان VLAN روی طبقات دیگر سالم هستند.",
            "مانیتورینگ در زمان Change، قطع ارتباط VLAN 30 روی uplink را ثبت کرده است."
        ],
        "timeline": "09:02 تغییر مجاز روی SW-CORE برای محدودکردن VLANهای trunk انجام شد. 09:04 اولین تماس کاربران ثبت شد. 09:08 معلوم شد VLANهای 10 و 20 سالم‌اند و فقط VLAN 30 در مسیر طبقهٔ دوم مشکل دارد.",
        "initial_state": "آخرین تغییر ثبت‌شده روی uplink، جایگزینی فهرست allowed VLAN با «10,20» بوده است. هنوز علت قطعی نیست؛ ابتدا باید خروجی عملی دستگاه بررسی شود.",
        "diagnostic_steps": [
            {
                "title": "۱. دامنه را از کلاینت ثابت کن",
                "purpose": "مشخص کن مشکل فقط یک کلاینت است یا تمام VLAN / طبقه.",
                "commands": "ipconfig /all\nping 10.30.30.1\narp -a",
                "expected": "IP=10.30.30.47/24 و Default Gateway=10.30.30.1؛ پینگ Gateway ناموفق و برای 10.30.30.1 ورودی ARP کامل دیده نمی‌شود.",
                "interpretation": "اگر IP از 169.254/16 است، قبل از trunk سراغ DHCP برو. اگر چند کلاینت VLAN 30 یکسان‌اند اما VLANهای دیگر سالم‌اند، دامنهٔ خرابی به VLAN 30 یا مسیر آن محدود می‌شود.",
                "if_match": "به مرحلهٔ ۲ برو و وضعیت VLAN و trunk را بخوان.",
                "if_not_match": "یک کلاینت دوم روی همان VLAN و یک کلاینت سالم از VLAN دیگر را مقایسه کن؛ هنوز تنظیم trunk را تغییر نده."
            },
            {
                "title": "۲. وجود VLAN و وضعیت پورت Access را تأیید کن",
                "purpose": "مطمئن شو VLAN روی هر دو سوئیچ موجود است و پورت کلاینت عضو درست آن است.",
                "commands": "show vlan id 30\nshow interfaces Gi1/0/17 switchport\nshow interfaces status",
                "expected": "VLAN 30 در حالت active و پورت کاربر operational با Access Mode و Access VLAN=30.",
                "interpretation": "اگر VLAN وجود ندارد یا پورت کاربر در VLAN دیگری است، علت در Access/VLAN database است نه لزوماً trunk. در این سناریو فرض بر درست‌بودن Access است و خروجی بعدی تعیین‌کننده خواهد بود.",
                "if_match": "مرحلهٔ ۳ را روی دو سر لینک اجرا کن.",
                "if_not_match": "خروجی قبل از Change و پورت سالم مشابه را مقایسه کن؛ پس از تأیید مالک پیکربندی، اصلاح همان VLAN/پورت را جداگانه برنامه‌ریزی کن."
            },
            {
                "title": "۳. فهرست VLANهای عبوری روی دو سر trunk را مقایسه کن",
                "purpose": "مهم‌ترین شاهد سناریو: VLAN باید در allowed list و در وضعیت forwarding باشد.",
                "commands": "show interfaces trunk\nshow running-config interface Gi1/0/48",
                "expected": "روی SW-CORE و SW-FLOOR-2، trunking و VLAN 30 در ستون «Vlans allowed and active» و «Vlans in spanning tree forwarding state» دیده شود. خروجی فعلی SW-CORE فقط VLANهای 10,20 را نشان می‌دهد.",
                "interpretation": "VLAN 30 در سوئیچ وجود دارد، اما در allowed list لینک عبور نمی‌کند؛ این شاهد مستقیم با زمان Change و دامنهٔ خرابی منطبق است. اگر VLAN در allowed list هست ولی forwarding نیست، STP، EtherChannel و native/tagging را جدا بررسی کن.",
                "if_match": "پیش از تغییر، running-config دو سر لینک را ذخیره کن؛ سپس فقط VLAN جاافتاده را به لیست فعلی اضافه کن.",
                "if_not_match": "به مسیر STP/EtherChannel، وضعیت فیزیکی، native VLAN و مسیر SVI برو؛ بر اساس یک ping ناموفق trunk را تغییر نده."
            },
            {
                "title": "۴. اصلاح کنترل‌شده روی پورت درست",
                "purpose": "تغییر حداقلی؛ فهرست VLANهای مجاز فعلی را حفظ کن.",
                "commands": "show running-config interface Gi1/0/48\nconfigure terminal\ninterface Gi1/0/48\nswitchport trunk allowed vlan add 30\nend",
                "expected": "فرمان add فقط VLAN 30 را به allowed list اضافه می‌کند؛ VLANهای 10 و 20 حذف نمی‌شوند.",
                "interpretation": "قبل از اجرا hostname و سمت لینک را دوباره چک کن. این فرمان نمونهٔ Cisco IOS است؛ روی تجهیزات دیگر syntax معادل لازم است. در محیط عملیاتی، تغییر باید مجوز و پنجرهٔ تغییر داشته باشد.",
                "if_match": "بلافاصله مرحلهٔ ۵ را برای تأیید لایهٔ ۲ و ۳ اجرا کن.",
                "if_not_match": "اگر فرمان با خطا مواجه شد یا پیکربندی با baseline تفاوت ناخواسته داشت، ادامه نده و به آخرین پیکربندی تأییدشده برگرد."
            },
            {
                "title": "۵. نتیجه را در هر دو جهت Verify کن",
                "purpose": "صرفاً «سبزشدن پورت» کافی نیست؛ عبور واقعی VLAN و Gateway را بسنج.",
                "commands": "show interfaces trunk\nshow mac address-table dynamic vlan 30\nshow ip interface brief\nping 10.30.30.47\n",
                "expected": "VLAN 30 در وضعیت forwarding دیده می‌شود؛ MAC کلاینت روی مسیر مورد انتظار یاد گرفته شده؛ Gateway و کلاینت تست پاسخ می‌دهند.",
                "interpretation": "اگر VLAN عبور می‌کند اما Gateway پاسخ نمی‌دهد، وضعیت SVI/ARP/ACL را بررسی کن. اگر یک جهت کار می‌کند، مسیر بازگشت و لایهٔ ۲ را هم بررسی کن.",
                "if_match": "از کلاینت واقعی DNS و سرویس برنامه را نیز تست کن و زمان/Change ID را ثبت کن.",
                "if_not_match": "پیکربندی را دوباره با دو سر trunk مقایسه کن؛ حذف VLAN، loop/STP، EtherChannel و SVI را با شواهد جدا کن."
            }
        ],
        "root_cause": "در مثال حاضر، تغییر فهرست allowed VLAN روی uplink، VLAN 30 را حذف کرده است. شواهد تأییدی: VLAN و Access port درست‌اند، خرابی محدود به همان VLAN است، و show interfaces trunk روی SW-CORE VLAN 30 را در فهرست عبوری نشان نمی‌دهد.",
        "fix_summary": "پس از ذخیرهٔ baseline، VLAN 30 را با فرمان افزایشی روی uplink صحیح اضافه کن؛ کل فهرست allowed VLAN را کورکورانه جایگزین نکن.",
        "verification": "تست از دو کلاینت VLAN 30؛ بررسی MAC learning؛ پینگ Gateway؛ سپس DNS و برنامهٔ واقعی؛ تأیید سالم‌ماندن VLANهای 10 و 20.",
        "rollback": "اگر اثر جانبی دیده شد، Change ID را متوقف کن و پیکربندی قبل از تغییر را طبق روش مدیریت تغییر سازمان بازیابی کن. «no switchport trunk allowed vlan ...» یا حذف کل allow-list را بدون ثبت دقیق وضعیت قبلی اجرا نکن.",
        "prevention": "Change template با diff قبل/بعد؛ کنترل خودکار VLANهای مجاز دو سر trunk؛ تست پس از تغییر از کلاینت‌های نماینده؛ هشدار برای حذف ناگهانی VLANهای فعال.",
        "related_diagrams": ["vlan", "trunk", "ethernet", "packet"]
    },
    {
        "id": "ad-dns-srv",
        "code": "INC-DNS-002",
        "title_fa": "کاربران به دامنه وارد نمی‌شوند و GPO اعمال نمی‌شود",
        "title_en": "Domain logon fails after client DNS change",
        "domain": "Windows / Active Directory / DNS",
        "severity": "High",
        "duration": "۱۵ تا ۳۰ دقیقه",
        "environment": "لابراتوار: دامنه corp.example؛ DC/DNS=10.20.10.10؛ کلاینت=10.20.12.44؛ DNS کلاینت پس از تغییر دستی روی 8.8.8.8 تنظیم شده است.",
        "impact": "ورود برخی کاربران دامنه، یافتن Domain Controller و Group Policy با خطا یا تأخیر روبه‌رو شده؛ اینترنت IPمحور هنوز کار می‌کند.",
        "symptoms": [
            "ping به 1.1.1.1 موفق است، اما ورود دامنه یا دسترسی به share مشکل دارد.",
            "gpupdate /force و DC Locator خطا می‌دهند.",
            "نام‌های عمومی resolve می‌شوند ولی رکوردهای SRV دامنه پیدا نمی‌شوند."
        ],
        "timeline": "08:45 برای رفع یک خطای اینترنت، DNS کلاینت دستی روی DNS عمومی گذاشته شد. 09:00 کاربران پس از logoff دیگر نتوانستند به‌درستی وارد دامنه شوند. کنترلر دامنه و سرویس DNS مرکزی سالم گزارش شده‌اند.",
        "initial_state": "اینترنت IPمحور سالم است؛ هنوز باید ثابت کنیم مشکل DNS کلاینت است یا دسترسی به سرور DNS/خود AD.",
        "diagnostic_steps": [
            {
                "title": "۱. DNS واقعی روی NIC را بخوان",
                "purpose": "از فرض‌کردن بر اساس تنظیمات DHCP پرهیز کن؛ DNS مؤثر همین لحظه را ببین.",
                "commands": "Get-NetIPConfiguration\nGet-DnsClientServerAddress -AddressFamily IPv4\nipconfig /all",
                "expected": "DNS Server کلاینت برابر 8.8.8.8 است؛ Gateway و IP کلاینت معتبرند.",
                "interpretation": "DNS عمومی برای resolve نام‌های اینترنت مفید است، اما زون خصوصی و رکوردهای SRV دامنه را نمی‌شناسد. بااین‌حال هنوز باید خود DNS داخلی را تست کنیم.",
                "if_match": "مرحلهٔ ۲ و ۳ را اجرا کن تا هم دسترسی شبکه و هم پاسخ SRV مشخص شود.",
                "if_not_match": "مقدار DNS را از NIC، VPN و سیاست‌های GPO بررسی کن؛ از یک کلاینت سالم در همان subnet مقایسه بگیر."
            },
            {
                "title": "۲. قابلیت دسترسی سرویس DNS داخلی را تست کن",
                "purpose": "خرابی Route/Firewall را از خرابی تنظیم Resolver تفکیک کن.",
                "commands": "Test-NetConnection 10.20.10.10 -Port 53\nResolve-DnsName www.microsoft.com -Server 10.20.10.10",
                "expected": "TCP/53 در دسترس است؛ DNS داخلی برای نام عمومی از forwarder یا recursion سازمانی پاسخ می‌دهد.",
                "interpretation": "Test-NetConnection فقط TCP را می‌سنجد و برای اثبات همهٔ رفتارهای DNS کافی نیست. اگر DNS داخلی قابل دسترسی نیست، مسیر VLAN/ACL/سرویس DNS را بررسی کن.",
                "if_match": "مرحلهٔ ۳ را با پرس‌وجوی SRV صریح به DNS داخلی انجام بده.",
                "if_not_match": "روی DC سرویس DNS، Windows Firewall، UDP/TCP 53 و مسیر رفت‌وبرگشت را بررسی کن؛ DNS کلاینت را تا روشن‌شدن دسترسی دست‌کاری نکن."
            },
            {
                "title": "۳. رکوردهای DC Locator را با DNS داخلی درخواست کن",
                "purpose": "اثبات کن خود Zone و SRV recordهای Active Directory پاسخ معتبر می‌دهند.",
                "commands": "Resolve-DnsName _ldap._tcp.dc._msdcs.corp.example -Type SRV -Server 10.20.10.10\nnltest /dsgetdc:corp.example",
                "expected": "پرس‌وجوی SRV یک یا چند DC معتبر را برمی‌گرداند و nltest بتواند DC را پیدا کند؛ مثال دامنه و آدرس برای لابراتوار است.",
                "interpretation": "اگر پرس‌وجوی صریح به DNS داخلی موفق است ولی پرس‌وجوی عادی کلاینت نه، مشکل به DNS مؤثر کلاینت/سیاست آن محدود می‌شود. اگر SRV وجود ندارد یا DNS داخلی پاسخ نمی‌دهد، زون، ثبت خودکار SRV و Netlogon را روی DC بررسی کن.",
                "if_match": "مقدار DNS را از منبع مدیریت‌شدهٔ شبکه اصلاح کن؛ ترجیحاً DHCP Option 006 یا GPO مطابق معماری.",
                "if_not_match": "روی DC رویدادهای DNS/Netlogon و ثبت SRV را بررسی کن؛ صرفاً Flush DNS علت را رفع نمی‌کند."
            },
            {
                "title": "۴. اصلاح DNS در منبع واقعی پیکربندی",
                "purpose": "تنظیم پایدار، نه یک workaround دستی روی یک کلاینت.",
                "commands": "Set-DnsClientServerAddress -InterfaceAlias \"Ethernet\" -ServerAddresses 10.20.10.10\nipconfig /flushdns\nipconfig /registerdns",
                "expected": "DNS کلاینت به Resolver داخلی مورد تأیید برمی‌گردد؛ cache قدیمی حذف می‌شود.",
                "interpretation": "فرمان PowerShell برای آزمایش روی کلاینت مجاز است؛ اگر DNS از DHCP/GPO مدیریت می‌شود، منبع اصلی را نیز اصلاح کن تا تنظیم بعدی آن را دوباره خراب نکند.",
                "if_match": "مرحلهٔ ۵ را اجرا کن و بعد از renew/reboot سیاست پایداربودن را بررسی کن.",
                "if_not_match": "Alias کارت شبکه و سیاست DNS/VPN را بررسی کن؛ در سازمان، تغییر گروهی را بدون Change approval انجام نده."
            },
            {
                "title": "۵. عملکرد کاربر را End-to-End تأیید کن",
                "purpose": "پاسخ DNS به‌تنهایی اثبات سلامت ورود و Group Policy نیست.",
                "commands": "Resolve-DnsName _kerberos._tcp.dc._msdcs.corp.example -Type SRV\nnltest /dsgetdc:corp.example\ngpupdate /force\ngpresult /r",
                "expected": "رکوردهای لازم پیدا شوند؛ DC locator موفق باشد؛ Group Policy بدون خطای مرتبط اعمال شود.",
                "interpretation": "اگر DNS درست شد اما Kerberos هنوز مشکل دارد، ساعت کلاینت/DC، دسترسی پورت‌های AD و replication را جدا بررسی کن.",
                "if_match": "نتیجه و DNS قبلی/جدید را در Change log ثبت کن.",
                "if_not_match": "Time skew، trust، replication و Windows Event Log را با شناسهٔ کاربر و زمان دقیق بررسی کن."
            }
        ],
        "root_cause": "کلاینت به DNS عمومی اشاره می‌کند؛ resolver عمومی رکوردهای خصوصی و SRV دامنه را ارائه نمی‌کند. موفقیت ping به IP فقط مسیر IP را نشان می‌دهد و سلامت DNS/AD را اثبات نمی‌کند.",
        "fix_summary": "DNS کلاینت را به DNS داخلی سازمان برگردان و Option 006 / GPO مرجع را اصلاح کن؛ سپس SRV، DC locator، GPO و ورود واقعی کاربر را Verify کن.",
        "verification": "SRVهای LDAP و Kerberos، nltest /dsgetdc، gpupdate /force، gpresult /r و ورود با حساب تست؛ سپس بررسی پایداری پس از renew.",
        "rollback": "مقادیر اصلی DNS را قبل از تغییر ثبت کن. اگر DNS داخلی دسترس‌پذیر نیست، تنظیم را به مقدار سازمانی قبلی بازگردان و incident شبکه/DNS را ارجاع بده؛ DNS عمومی را به‌عنوان راه‌حل پایدار AD قرار نده.",
        "prevention": "قفل تغییر دستی DNS در endpointهای مدیریت‌شده؛ مانیتور SRVهای AD؛ تست DNS داخلی از هر سایت؛ راهنمای پشتیبانی که ping IP را معادل سلامت ورود دامنه تلقی نکند.",
        "related_diagrams": ["dns", "dhcp", "tcp"]
    },
    {
        "id": "routeros-wan-nat",
        "code": "INC-MT-003",
        "title_fa": "روتر MikroTik اینترنت دارد اما کاربران LAN به سایت‌ها وصل نمی‌شوند",
        "title_en": "RouterOS WAN works but LAN clients cannot browse",
        "domain": "MikroTik / NAT / Firewall",
        "severity": "High",
        "duration": "۱۵ تا ۲۵ دقیقه",
        "environment": "لابراتوار: LAN=10.50.10.0/24؛ روتر=10.50.10.1؛ WAN=pppoe-out1؛ کلاینت=10.50.10.50؛ Rule خروجی NAT از out-interface-list=WAN استفاده می‌کند.",
        "impact": "خود روتر به IP عمومی ping دارد اما بیشتر کاربران پشت NAT اتصال اینترنت ندارند.",
        "symptoms": [
            "Gateway LAN در دسترس است.",
            "از RouterOS ping به 1.1.1.1 موفق، اما از کلاینت ping به IP عمومی ناموفق است.",
            "Rule مربوط به masquerade پس از تغییر نام اینترفیس یا مهاجرت به PPPoE، counter ندارد."
        ],
        "timeline": "پس از تعویض لینک فیزیکی WAN به PPPoE، WAN interface جدیدی به نام pppoe-out1 ساخته شد. route پیش‌فرض بالا است، اما گروه interface-list به‌روز نشده است.",
        "initial_state": "Default route و دسترسی خود روتر سالم‌اند؛ هنوز NAT، forward firewall و برگشت ترافیک کلاینت بررسی نشده‌اند.",
        "diagnostic_steps": [
            {
                "title": "۱. مسیر خود روتر و کلاینت را جدا کن",
                "purpose": "ثابت کن WAN زنده است ولی عیب در forwarding/NAT می‌تواند مستقل باشد.",
                "commands": "/ping 1.1.1.1 count=5\n/ip route print detail\n/ip address print",
                "expected": "default route active است و ping از خود روتر پاسخ می‌گیرد؛ آدرس LAN روی bridge یا اینترفیس صحیح قرار دارد.",
                "interpretation": "اگر خود روتر ping ندارد، ابتدا WAN/default route/ISP را بررسی کن؛ به NAT LAN نپرداز. در این نمونه مسیر خود روتر سالم است.",
                "if_match": "از کلاینت IPمحور و از counterهای firewall/NAT شواهد بگیر.",
                "if_not_match": "default route، PPPoE status و DNS بالادست را بررسی کن و سناریوی WAN outage را دنبال کن."
            },
            {
                "title": "۲. از کلاینت، IP را از نام جدا کن",
                "purpose": "DNS را از NAT و routing تفکیک کن.",
                "commands": "ping 10.50.10.1\nping 1.1.1.1\nnslookup example.com",
                "expected": "Gateway پاسخ دارد؛ ping به IP عمومی شکست می‌خورد؛ نتیجهٔ DNS به‌تنهایی تعیین‌کننده نیست تا دسترسی IP برقرار شود.",
                "interpretation": "وقتی Gateway سالم و RouterOS به اینترنت متصل است ولی forwarded client traffic عبور نمی‌کند، NAT/forward/routing را بررسی کن.",
                "if_match": "مرحلهٔ ۳ را اجرا کن و counter همان ruleهای مربوط را ثبت کن.",
                "if_not_match": "VLAN کلاینت، IP/Mask/Gateway و default route روتر را با یک کلاینت سالم مقایسه کن."
            },
            {
                "title": "۳. interface-list و NAT counter را بخوان",
                "purpose": "تنظیمات واقعی با نام رابط WAN جدید مطابقت داده شود.",
                "commands": "/interface/list/member/print detail\n/ip firewall nat print detail stats\n/ip firewall filter print detail stats\n/tool torch interface=pppoe-out1",
                "expected": "pppoe-out1 در لیست WAN نیست؛ Rule masquerade روی out-interface-list=WAN counter صفر دارد؛ ترافیک خروجی کلاینت روی PPPoE دیده می‌شود.",
                "interpretation": "این ترکیب شواهد توضیح می‌دهد چرا خود روتر ارتباط دارد ولی بسته‌های کلاینت با source خصوصی از WAN خارج می‌شوند. اگر counter NAT افزایش دارد، NAT-list علت اصلی این مورد نیست و route/forward/return path بررسی می‌شود.",
                "if_match": "پس از backup، membership رابط صحیح یا شرط NAT را مطابق استاندارد config اصلاح کن.",
                "if_not_match": "Ruleهای بالاتر، action=accept، ترتیب filter، connection tracking و مسیر برگشت را بررسی کن؛ counter صفر به‌تنهایی کافی نیست."
            },
            {
                "title": "۴. تغییر حداقلی و قابل برگشت",
                "purpose": "عضویت رابط واقعی را به لیست WAN اضافه کن، فقط اگر طراحی سازمان همین interface-list را مبنا قرار داده است.",
                "commands": "/export file=before-wan-list-fix\n/interface/list/member/add list=WAN interface=pppoe-out1 comment=\"incident INC-MT-003 approved fix\"",
                "expected": "رابط PPPoE در لیست WAN قرار می‌گیرد و Rule موجود NAT را match می‌کند.",
                "interpretation": "اگر سازمان از interface-list استفاده نمی‌کند، به‌جای این فرمان شرط Rule را مطابق design و baseline اصلاح کن. Rule جدید عمومی اضافه نکن و WAN interface را بدون بررسی نام واقعی فرض نکن.",
                "if_match": "مرحلهٔ ۵ را فوراً با کلاینت تست انجام بده.",
                "if_not_match": "اگر entry تکراری یا اشتباه ایجاد شد، فقط همان موردی را که در این Change اضافه شده حذف کن؛ سایر اعضای لیست را پاک نکن."
            },
            {
                "title": "۵. عبور ترافیک را با counter و تست سرویس اثبات کن",
                "purpose": "حل مشکل را با نتیجهٔ مشاهده‌پذیر ثبت کن.",
                "commands": "/ip firewall nat print stats\n/ip firewall filter print stats\n/tool torch interface=pppoe-out1",
                "expected": "counter قانون masquerade هنگام تست کلاینت افزایش یابد؛ کلاینت ping به IP عمومی و سپس Resolve نام و HTTPS را موفق انجام دهد.",
                "interpretation": "اگر NAT counter افزایش دارد ولی اتصال هنوز قطع است، packet capture سمت WAN و بررسی connection state، forward policy و return path را ادامه بده. فقط «ping از خود روتر» معیار قبولی کلاینت نیست.",
                "if_match": "تست HTTPS/DNS و یک کلاینت دوم را ثبت کن.",
                "if_not_match": "Ruleهای drop قبل از allow، FastTrack/mark، مسیر برگشت و MTU را بدون تغییر همزمان چند پارامتر بررسی کن."
            }
        ],
        "root_cause": "Rule موجود masquerade به interface-list=WAN متکی است، اما رابط PPPoE تازه‌ساخته‌شده عضو آن لیست نشده است؛ در نتیجه ترافیک کاربران روی آن Rule match نمی‌شود. این علت فقط وقتی تأیید است که membership و counterها همین رفتار را نشان دهند.",
        "fix_summary": "با backup، pppoe-out1 را به WAN list اضافه کن یا شرط NAT را مطابق طرح واقعی تنظیم کن؛ یک Rule عمومی دوم برای پنهان‌کردن علت نساز.",
        "verification": "هنگام تولید ترافیک آزمایشی، افزایش counter NAT، اتصال IPمحور، Resolve DNS و HTTPS از کلاینت و سلامت دسترسی مدیریت به روتر.",
        "rollback": "اگر رابط اشتباه به لیست اضافه شده، همان entry ایجادشده با comment/شناسهٔ همین Change را حذف کن. به Ruleهای موجود دست نزن و فایل export قبل از تغییر را نگه دار.",
        "prevention": "بعد از تغییر WAN نام interface و interface-list را تطبیق بده؛ smoke-test از یک کلاینت LAN؛ هشدار روی counterهای NAT صفر در صورت وجود ترافیک؛ ثبت baseline export.",
        "related_diagrams": ["nat", "firewall", "routing", "packet"]
    },
    {
        "id": "ospf-exstart-mtu",
        "code": "INC-RT-004",
        "title_fa": "همسایگی OSPF روی ExStart گیر کرده و Routeهای سایت نصب نمی‌شوند",
        "title_en": "OSPF adjacency stuck in EXSTART due to MTU mismatch",
        "domain": "Routing / OSPF",
        "severity": "High",
        "duration": "۲۰ تا ۴۰ دقیقه",
        "environment": "لابراتوار: R-HQ Gi0/0=172.16.0.1/30 و R-BR Gi0/0=172.16.0.2/30؛ OSPF Area 0؛ MTU دو سمت در این مثال 1500 و 1400.",
        "impact": "لینک IP و Helloها کار می‌کنند، اما adjacency به Full نمی‌رسد و شبکه‌های پشت روتر شعبه در routing table دیده نمی‌شوند.",
        "symptoms": [
            "پینگ دو آدرس روی لینک موفق است.",
            "show ip ospf neighbor وضعیت EXSTART/EXCHANGE را تکرار می‌کند.",
            "Route مربوط به 10.60.0.0/16 از OSPF وارد جدول نشده است."
        ],
        "timeline": "بعد از تغییر MTU در رابط WAN/overlay یکی از روترها، adjacency ناپایدار شده است. قبل از تغییر، OSPF Full و route شعبه موجود بود.",
        "initial_state": "IP reachability از روی لینک وجود دارد؛ مشکل احتمالاً بالاتر از IP است. باید MTU و پارامترهای adjacency با هم بررسی شوند.",
        "diagnostic_steps": [
            {
                "title": "۱. سلامت پایهٔ اینترفیس و IP را بررسی کن",
                "purpose": "مشکل فیزیکی یا subnet را با OSPF قاطی نکن.",
                "commands": "show ip interface brief\nshow interfaces Gi0/0\nping 172.16.0.2 source 172.16.0.1",
                "expected": "اینترفیس up/up است، آدرس‌ها هم‌زیرشبکه‌اند و ping همسایه موفق است.",
                "interpretation": "پینگ کوچک فقط ارتباط پایه را اثبات می‌کند؛ MTU بزرگ، adjacency و نصب Route را اثبات نمی‌کند.",
                "if_match": "پارامترهای OSPF و MTU دو سر لینک را در مرحلهٔ بعد مقایسه کن.",
                "if_not_match": "قبل از OSPF، VLAN/link/IP/mask/ACL را حل کن."
            },
            {
                "title": "۲. حالت همسایه و پارامترهای رابط را ثبت کن",
                "purpose": "EXSTART را به شاهد قابل آزمایش تبدیل کن.",
                "commands": "show ip ospf neighbor detail\nshow ip ospf interface Gi0/0\nshow interfaces Gi0/0 | include MTU",
                "expected": "Neighbor مکرراً در EXSTART/EXCHANGE می‌ماند؛ MTU سمت HQ برابر 1500 و سمت BR برابر 1400 است.",
                "interpretation": "اختلاف MTU در تبادل Database Description می‌تواند مانع تکمیل adjacency شود. این یک فرضیهٔ قوی است، اما OSPF authentication، area، network type و duplicate RID نیز باید با شواهد بررسی شوند.",
                "if_match": "با طراحی overlay/لینک و تیم WAN، MTU مجاز واقعی end-to-end را تعیین کن؛ هنوز MTU را تصادفی بالا نبر.",
                "if_not_match": "authentication، Area/area type، timer، network type، duplicate router ID و log را بررسی کن."
            },
            {
                "title": "۳. ظرفیت واقعی مسیر را بدون تغییر پیکربندی تست کن",
                "purpose": "بفهم MTU طراحی‌شده چه میزانی است؛ پینگ کوچک کافی نیست.",
                "commands": "ping 172.16.0.2 size 1472 df-bit source 172.16.0.1\nshow logging | include OSPF|MTU|ADJ",
                "expected": "در این لابراتوار، probe بزرگ ممکن است با MTU 1400 شکست بخورد و log هم با مسئلهٔ adjacency هم‌زمان باشد. syntax ping بسته به IOS release فرق می‌کند.",
                "interpretation": "پروب شکست‌خورده می‌تواند ناشی از MTU/fragmentation policy باشد، اما باید با MTU رابط، encapsulation overhead و log تطبیق داده شود.",
                "if_match": "یک مقدار MTU مشترک و تأییدشده برای مسیر overlay انتخاب و تغییر کنترل‌شده برنامه‌ریزی کن.",
                "if_not_match": "به فرضیهٔ MTU تکیه نکن؛ packet capture/log و پارامترهای OSPF را ادامه بده."
            },
            {
                "title": "۴. اصلاح MTU با Change و Rollback آماده",
                "purpose": "دو سر لینک باید با مقدار سازگار با مسیر واقعی تنظیم شوند؛ یک سمت را کورکورانه تغییر نده.",
                "commands": "show running-config interface Gi0/0\n! نمونهٔ تغییر فقط پس از تأیید MTU صحیح مسیر:\nconfigure terminal\ninterface Gi0/0\nip mtu 1400\nend",
                "expected": "MTU interface طبق طراحی مورد تأیید یکسان/سازگار می‌شود. عدد 1400 تنها مقدار نمونهٔ همین سناریو است و برای شبکهٔ دیگر نسخهٔ آمادهٔ اجرا نیست.",
                "interpretation": "قبل از اعمال، وضعیت peer، encapsulation، MTU مسیر و اثر بر سایر سرویس‌ها را بررسی کن. اگر استاندارد شبکه 1500 است، ممکن است درست‌کردن سمت 1400 به 1500 راه‌حل مناسب‌تری باشد.",
                "if_match": "Neighbor، route و تست end-to-end را در مرحلهٔ ۵ بررسی کن.",
                "if_not_match": "اگر adjacency بدتر شد، rollback کن و لایهٔ overlay/transport را با صاحب سرویس هماهنگ کن."
            },
            {
                "title": "۵. Full و جدول Route را Verify کن",
                "purpose": "تغییر فقط وقتی تمام است که control-plane و data-plane سالم باشند.",
                "commands": "show ip ospf neighbor\nshow ip route ospf\nshow ip route 10.60.0.0\ntraceroute 10.60.10.10",
                "expected": "Neighbor به FULL می‌رسد و Route شبکهٔ شعبه از OSPF نصب می‌شود؛ مسیر واقعی تا مقصد نمونه موفق است.",
                "interpretation": "FULL بودن به‌تنهایی انتقال ترافیک را اثبات نمی‌کند. اگر Route هست اما سرویس قطع است، CEF/FIB، ACL و مسیر برگشت را بررسی کن.",
                "if_match": "گراف adjacency/route و تست برنامه را در Change ثبت کن.",
                "if_not_match": "LSDB، انتخاب Best Route، prefix filtering و route برگشت را بررسی کن؛ هنوز پایان incident اعلام نکن."
            }
        ],
        "root_cause": "در این نمونه، MTU روی دو سر adjacency برابر نیست و پس از Change به وضعیت EXSTART منتهی شده است. تأیید نهایی نیازمند تطبیق خروجی هر دو رابط و log است؛ سایر علت‌های EXSTART باید حذف شوند.",
        "fix_summary": "MTU سازگار با end-to-end transport را پس از تأیید معماری تنظیم کن؛ از ip ospf mtu-ignore به‌عنوان وصلهٔ عمومی استفاده نکن، چون تفاوت ظرفیت واقعی مسیر را رفع نمی‌کند.",
        "verification": "Neighbor به FULL، Route دقیق در جدول، ping/trace از subnet منبع به مقصد و تست سرویس؛ پایش مجدد بعد از convergence.",
        "rollback": "مقادیر قبل از تغییر را ذخیره کن و همان‌ها را بازگردان؛ اگر tunnel MTU تعیین‌کننده است، تغییر را با تیم WAN هماهنگ و در یک سمت به‌تنهایی اعمال نکن.",
        "prevention": "پایش وضعیت adjacency و تعداد flap؛ ثبت MTU/MSS در LLD؛ تست MTU پس از تغییر encapsulation؛ change template برای دو سر لینک.",
        "related_diagrams": ["ospf", "routing", "mtu", "packet"]
    },
    {
        "id": "ipsec-route-wrong",
        "code": "INC-VPN-005",
        "title_fa": "تونل IPsec سبز است اما ترافیک شعبه وارد شبکهٔ مرکز نمی‌شود",
        "title_en": "IPsec control plane is up but route points traffic to WAN",
        "domain": "VPN / FortiGate / Routing",
        "severity": "High",
        "duration": "۲۰ تا ۴۵ دقیقه",
        "environment": "لابراتوار: LAN مرکز 10.10.10.0/24؛ LAN شعبه 10.20.20.0/24؛ VPN interface=HQ-BRANCH; branch host=10.20.20.10؛ server=10.10.10.20.",
        "impact": "IKE/IPsec ظاهر سالم دارد اما اپلیکیشن مرکز از شعبه در دسترس نیست. بعضی dashboardها فقط وضعیت phase 1 را نشان می‌دهند.",
        "symptoms": [
            "GUI یا get vpn status تونل را UP نشان می‌دهد.",
            "کاربر شعبه به Gateway محلی دسترسی دارد ولی مقصد مرکز timeout می‌شود.",
            "بسته‌های آزمایشی روی WAN خارج می‌شوند یا شمارندهٔ encaps/decaps با ترافیک مورد انتظار هم‌خوانی ندارد."
        ],
        "timeline": "در Change قبلی، static route شبکهٔ مرکز بازسازی شد. به‌جای interface VPN، next-hop پیش‌فرض WAN برای 10.10.10.0/24 انتخاب شده است؛ IKE SA قبلی همچنان UP مانده است.",
        "initial_state": "تونل UP فقط وضعیت control-plane را بیان می‌کند؛ route انتخابی و عبور واقعی داده هنوز معلوم نیست.",
        "diagnostic_steps": [
            {
                "title": "۱. از یک جریان مشخص و آدرس‌دار تست بگیر",
                "purpose": "تست تکرارپذیر با منبع و مقصد معلوم لازم است.",
                "commands": "ping 10.10.10.20\ntracert 10.10.10.20\n# فرمان‌ها از کلاینت 10.20.20.10 در شعبه اجرا می‌شوند",
                "expected": "از کلاینت شعبه، مقصد مرکز پاسخ نمی‌دهد؛ زمان و منبع تست ثبت می‌شود.",
                "interpretation": "قبل از rule change مشخص کن دقیقاً کدام subnet و پروتکل مشکل دارد؛ timeout ICMP به‌تنهایی ثابت نمی‌کند خود برنامه هم قطع است.",
                "if_match": "وضعیت SA و route انتخاب‌شده برای 10.10.10.0/24 را از روی FortiGate ببین.",
                "if_not_match": "از دستگاه/پروتکل واقعی تست بگیر؛ اگر مقصد سالم است دامنهٔ خرابی را دوباره تعریف کن."
            },
            {
                "title": "۲. وضعیت Phase 1/2 و شمارنده‌های واقعی را بخوان",
                "purpose": "UP در IKE را از برقرار بودن تبادل داده جدا کن.",
                "commands": "get vpn ipsec tunnel summary\ndiagnose vpn tunnel list name HQ-BRANCH",
                "expected": "SA مورد انتظار وجود دارد، اما با تکرار ترافیک آزمایشی شمارنده‌های مورد انتظار encaps/decaps ممکن است یک‌طرفه یا ثابت بمانند.",
                "interpretation": "نام فیلدهای counters وابسته به FortiOS نسخه است. صفرماندن تنها یک نشانه است؛ باید با route و packet capture تطبیق داده شود.",
                "if_match": "route دقیق مقصد را بررسی کن.",
                "if_not_match": "Phase 2 selectors, peer, proposal و lifetime را بررسی کن؛ مرحلهٔ route را همچنان انجام بده."
            },
            {
                "title": "۳. route lookup را برای مقصد مرکز انجام بده",
                "purpose": "ثابت کن packet forward واقعاً کدام خروجی را انتخاب می‌کند.",
                "commands": "get router info routing-table details 10.10.10.20\nget router info routing-table all",
                "expected": "در این سناریو، route خاص 10.10.10.0/24 به default gateway/WAN اشاره می‌کند نه interface تونل HQ-BRANCH.",
                "interpretation": "این شاهد با تغییر قبلی و مسیر خروجی اشتباه منطبق است. اگر route به تونل صحیح است، Phase 2 selectors، policy، NAT و return route را بررسی کن.",
                "if_match": "پس از backup، مسیر را از روی change approved به VPN interface برگردان.",
                "if_not_match": "debug flow و sniffer را برای تشخیص policy/selector/return path اجرا کن؛ تونل UP را اثبات کافی ندان."
            },
            {
                "title": "۴. اصلاح route با محدودهٔ دقیق",
                "purpose": "Route شبکهٔ خصوصی مرکز باید به interface تونل درست برود.",
                "commands": "show router static\nshow vpn ipsec phase2-interface\n# پس از تهیهٔ backup، ID مسیر اشتباه را از show router static بردار\nconfig router static\n edit <ROUTE_ID_FROM_SHOW>\n  set dst 10.10.10.0 255.255.255.0\n  set device \"HQ-BRANCH\"\n  unset gateway\n next\nend\nget router info routing-table details 10.10.10.20",
                "expected": "Static route با prefix درست و interface صحیح VPN نصب می‌شود؛ routeهای عمومی اینترنت تغییر نمی‌کنند.",
                "interpretation": "دستور نهایی add/edit بسته به نسخه و mode دستگاه فرق می‌کند؛ آن را بدون تأیید route table و backup در این runbook به فرمان کور تبدیل نکن. از UI/CLI تأییدشدهٔ همان FortiOS استفاده کن.",
                "if_match": "مرحلهٔ ۵ را برای encaps/decaps و سرویس انجام بده.",
                "if_not_match": "اگر route جدید نصب نشد یا route دیگری برنده شد، تغییر را متوقف و distance/priority/SD-WAN policy را بررسی کن."
            },
            {
                "title": "۵. data-plane، policy و برگشت را تأیید کن",
                "purpose": "اثبات end-to-end از LAN شعبه تا سرویس مرکز.",
                "commands": "diagnose sniffer packet any \"host 10.20.20.10 and host 10.10.10.20\" 4 20\ndiagnose debug flow filter saddr 10.20.20.10\ndiagnose debug flow filter daddr 10.10.10.20\ndiagnose debug flow trace start 20\n# بعد از بررسی: diagnose debug disable",
                "expected": "Packet از LAN وارد می‌شود، به interface تونل می‌رود، سمت مرکز به سرویس می‌رسد و پاسخ از تونل به شعبه برمی‌گردد.",
                "interpretation": "اگر SYN خارج می‌شود ولی پاسخ نیست، selector سمت مقابل، policy و return route را بررسی کن. Debug را پس از جمع‌آوری شواهد خاموش کن.",
                "if_match": "تست TCP port برنامه، logging و مانیتورینگ tunnel counters را ثبت کن.",
                "if_not_match": "محل ناپدیدشدن packet را روی ingress/egress دو طرف پیدا کن؛ چند policy را هم‌زمان تغییر نده."
            }
        ],
        "root_cause": "تونل IPsec برقرار است، اما route مقصد خصوصی مرکز پس از Change از مسیر default WAN عبور می‌کند. Control plane UP را نباید با data plane سالم یکی دانست.",
        "fix_summary": "Route اختصاصی subnet مرکز را با prefix، interface و distance درست به tunnel برگردان؛ هم‌زمان NAT exemption و selectors دو طرف را تطبیق بده، اما تغییر را بر اساس شواهد route شروع کن.",
        "verification": "افزایش encaps/decaps، مشاهدهٔ packet در دو سمت، موفقیت TCP به پورت سرویس، route برگشت به subnet شعبه و ثبت نتیجهٔ end-to-end.",
        "rollback": "قبل از تغییر route و distance را export کن؛ اگر مسیر جدید سرویس‌های دیگر را مختل کرد، route قبلی را با تأیید صاحب تغییر بازگردان و ترافیک را به مسیر تاییدشده برگردان.",
        "prevention": "مانیتور tunnel traffic counters جدا از IKE status؛ تست synthetic از هر LAN؛ کنترل static route/SD-WAN پس از change؛ نگهداری ماتریس subnet/selector/return route.",
        "related_diagrams": ["vpn", "ipsec", "routing", "nat", "packet"]
    },
    {
        "id": "dhcp-scope-full",
        "code": "INC-DHCP-006",
        "title_fa": "دستگاه‌های Wi-Fi وصل می‌شوند ولی IP نمی‌گیرند؛ Scope تمام شده است",
        "title_en": "Wireless clients associate but DHCP scope is exhausted",
        "domain": "Wi-Fi / DHCP / Windows Server",
        "severity": "Medium",
        "duration": "۲۰ تا ۴۰ دقیقه",
        "environment": "لابراتوار: SSID=Staff-WiFi؛ VLAN 40؛ subnet=10.40.20.0/24؛ DHCP scope روی DHCP01 از 10.40.20.100 تا 10.40.20.150؛ Gateway=10.40.20.1.",
        "impact": "کلاینت‌های جدید Wi-Fi Association موفق دارند اما آدرس IPv4 معتبر نمی‌گیرند؛ کاربران قدیمی ممکن است تا پایان lease کار کنند.",
        "symptoms": [
            "Wireless client در AP connected/associated است.",
            "بعضی کلاینت‌ها 169.254.x.x دارند یا آدرس قبلی را نگه داشته‌اند.",
            "کاربران قدیمی کار می‌کنند و مشکل برای joinهای جدید بیشتر است."
        ],
        "timeline": "جلسهٔ آموزشی با تعداد دستگاه بیشتر از معمول شروع شد؛ Scope محدود قبلی برای ۵۱ آدرس، با leaseهای فعال و رزروها پر شده است. هنوز باید exhaustion را از DHCP relay/VLAN/Server outage جدا کنیم.",
        "initial_state": "Association رادیویی موفق است اما این امر DHCP را ثابت نمی‌کند. ابتدا Lease، utilization و relay را بررسی کن.",
        "diagnostic_steps": [
            {
                "title": "۱. کلاینت و Wi-Fi association را جداگانه بررسی کن",
                "purpose": "خرابی 802.11 را از مرحلهٔ تخصیص IP تفکیک کن.",
                "commands": "ipconfig /all\nipconfig /release\nipconfig /renew",
                "expected": "Association باقی می‌ماند، اما Renew آدرس معتبر 10.40.20.x نمی‌گیرد یا خطا می‌دهد؛ ممکن است AP دستگاه را online نشان دهد.",
                "interpretation": "اگر کلاینت از Wi-Fi قطع است، اولویت با RF/auth است؛ در این سناریو Association سالم است و باید DHCP مسیر را بررسی کنیم.",
                "if_match": "Scope statistics و تعداد leaseهای فعال را روی DHCP01 بخوان.",
                "if_not_match": "Client isolation، SSID-to-VLAN mapping، WPA/EAP و AP logs را بررسی کن."
            },
            {
                "title": "۲. utilization و leaseهای Scope را بسنج",
                "purpose": "تعدادهای واقعی را ببین؛ به حدس یا فقط به AP status تکیه نکن.",
                "commands": "Get-DhcpServerv4ScopeStatistics -ComputerName DHCP01\nGet-DhcpServerv4Lease -ComputerName DHCP01 -ScopeId 10.40.20.0",
                "expected": "Scope utilization نزدیک 100٪ است و بسیاری از آدرس‌های 10.40.20.100–10.40.20.150 به leaseهای معتبر اختصاص دارند.",
                "interpretation": "اگر Scope ظرفیت دارد، Exhaustion علت نیست؛ relay/IP helper، authorization سرویس، VLAN یا dropهای UDP/67-68 را بررسی کن.",
                "if_match": "ظرفیت موردنیاز، leaseهای واقعی و آدرس‌های رزرو/static را محاسبه کن.",
                "if_not_match": "با packet capture یا DHCP server log بررسی کن Discover به سرور می‌رسد و Offer برمی‌گردد یا نه."
            },
            {
                "title": "۳. مسیر DHCP و Relay را بر اساس توپولوژی Verify کن",
                "purpose": "تضمین کن Discover کلاینت از VLAN 40 به Scope درست می‌رسد.",
                "commands": "Get-DhcpServerv4Binding -ComputerName DHCP01\nGet-DhcpServerv4Scope -ComputerName DHCP01\n# روی gateway Cisco در صورت وجود relay:\nshow running-config interface Vlan40\nshow ip interface Vlan40",
                "expected": "Scope برای 10.40.20.0/24 فعال است؛ relay/helper در Gateway درست و آدرس سرور مقصد 10.40.10.10 است (آدرس نمونهٔ لابراتوار).",
                "interpretation": "اگر Discover به سرور نمی‌رسد، exhaustion را علت نهایی اعلام نکن؛ VLAN/relay/firewall path را اصلاح کن.",
                "if_match": "پس از backup و approval، Scope را به بازه‌ای بزرگ‌تر افزایش بده که با IPهای static و reservation هم‌پوشانی نداشته باشد.",
                "if_not_match": "Capture روی VLAN و DHCP server را هم‌زمان بگیر و مراحل DORA را مشخص کن: Discover, Offer, Request, ACK."
            },
            {
                "title": "۴. ظرفیت را با برنامه و بدون overlap افزایش بده",
                "purpose": "دامنهٔ پویای مجاز را با تعداد client و reservationها متناسب کن.",
                "commands": "Get-DhcpServerv4Scope -ComputerName DHCP01 -ScopeId 10.40.20.0\nGet-DhcpServerv4Reservation -ComputerName DHCP01 -ScopeId 10.40.20.0\n# نمونهٔ تغییر range را پس از محاسبهٔ آدرس‌های آزاد و تأیید تغییر اجرا کن.",
                "expected": "بازهٔ جدید فقط به آدرس‌های آزاد گسترش می‌یابد؛ Gateway، DNS، exclusions و reservations درست باقی می‌مانند.",
                "interpretation": "عمداً فرمان تغییر range عمومی درج نشده: begin/end باید بر اساس IPAM و محدودهٔ واقعی انتخاب شود تا duplicate IP ایجاد نشود.",
                "if_match": "یک کلاینت جدید را Renew کن و DORA/lease را بررسی کن.",
                "if_not_match": "تغییر را متوقف کن؛ قبل از اضافه کردن آدرس، IPAM، scope options، exclusions و subnet mask را دوباره تطبیق بده."
            },
            {
                "title": "۵. Lease و دسترسی واقعی را Verify کن",
                "purpose": "گرفتن IP کافی نیست؛ Gateway و resolver نیز باید قابل استفاده باشند.",
                "commands": "Get-DhcpServerv4Lease -ComputerName DHCP01 -ScopeId 10.40.20.0\nipconfig /all\nping 10.40.20.1\nResolve-DnsName example.com",
                "expected": "کلاینت جدید lease معتبر از Scope درست، Gateway=10.40.20.1 و DNS سازمانی دریافت می‌کند؛ تست Gateway و DNS موفق است.",
                "interpretation": "اگر lease صادر شده اما اینترنت نیست، این incident را ببند فقط پس از تست Gateway/DNS و در صورت نیاز policy مربوط به guest/staff.",
                "if_match": "نرخ utilization را مانیتور و آدرس‌های رزرو/ثابت را مستند کن.",
                "if_not_match": "DHCP ACK، VLAN mapping، ACL و DNS option را جدا دنبال کن."
            }
        ],
        "root_cause": "در این مثال، DHCP scope فقط ۵۱ آدرس پویا دارد و utilization/lease log نشان می‌دهد ظرفیت تمام شده است. این علت تنها در صورت تطبیق آمار Scope و مشاهدهٔ مسیر DORA معتبر است.",
        "fix_summary": "پس از بررسی IPAM، exclusions و reservationها، Scope را در محدودهٔ آزاد بزرگ کن یا طراحی ظرفیت/lease را اصلاح کن. کاهش کورکورانهٔ Lease و پاک‌کردن leaseهای فعال راه‌حل ایمن نیست.",
        "verification": "کلاینت جدید IP معتبر و options صحیح بگیرد؛ DHCP server lease جدید نشان دهد؛ Gateway، DNS و برنامهٔ داخلی کار کنند؛ AP و relay logs خطای تازه ثبت نکنند.",
        "rollback": "بازهٔ قبلی، optionها، exclusions و reservations را ثبت کن. اگر رنج جدید overlap یا duplicate ایجاد کرد، change را متوقف و فقط با طرح IPAM تأییدشده به وضعیت سالم برگرد.",
        "prevention": "هشدار utilization در ۷۰/۸۵/۹۵ درصد؛ ظرفیت‌سنجی رویدادها؛ جداسازی guest/staff scopes؛ ثبت DORA failure و تست دوره‌ای از client تازه.",
        "related_diagrams": ["dhcp", "wireless", "vlan", "packet"]
    }
]


def list_incidents() -> list[dict]:
    """Small catalog only; large step-by-step procedure is fetched by ID."""
    fields = ("id", "code", "title_fa", "title_en", "domain", "severity", "duration",
              "impact", "symptoms", "environment")
    return [{key: deepcopy(item.get(key)) for key in fields} for item in INCIDENT_RUNBOOKS]


def get_incident(incident_id: str) -> dict | None:
    for item in INCIDENT_RUNBOOKS:
        if item["id"] == incident_id:
            return deepcopy(item)
    return None
