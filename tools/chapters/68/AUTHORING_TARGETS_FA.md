# فصل ۶۸ — قرارداد محتوایی و برنامهٔ غنی‌سازی عمیق

وضعیت: **target_specification / نیازمند تولید و اعتبارسنجی**. این سند معیار پذیرش است؛ وجود این سند به معنی تولید شدن همهٔ رکوردهای هدف نیست.

## اصل‌های غیرقابل‌مذاکره

1. محتوای فعلی فصل ۶۸ و بسته‌های ZIP/JSON حفظ شود؛ هیچ فایل یا رکوردی صرفاً برای کم‌کردن حجم حذف نشود.
2. دستهٔ اصلی با نام فناوری نمایش داده شود؛ نمونه: «MikroTik RouterOS»، «Cisco IOS/IOS-XE»، «Windows Batch»، «PowerShell»، «VoIP»، «FortiGate FortiOS»، «VMware ESXi/vSphere»، «SSH»، «Telnet»، «FTP»، «FTPS»، «SFTP».
3. جستجو باید در نام فناوری، نام بخش، عنوان، نام/الگوی دستور، آرگومان‌ها، توضیح فارسی، واژه‌های انگلیسی، کاربرد، نسخه و برچسب‌ها انجام شود.
4. UID پایدار و یکتا باشد. تکرار همان دستور با توضیح متفاوت، رکورد دستور تازه محسوب نمی‌شود؛ تفاوت نسخه/سیستم‌عامل/حالت اجرا باید صریح ثبت شود.
5. برای هر دستور، صحت syntax، جای اجرا، سطح دسترسی، نسخه/پلتفرم، اثر جانبی، خطر و روش تأیید نتیجه مشخص شود. دستورات مخرب باید هشدار و روش rollback داشته باشند.
6. تعدادها از فایل‌های JSON واقعی و خروجی validator محاسبه شوند، نه از اعداد ثابت در manifest. رکوردهای placeholder و تکراری در شمارش محتوای کامل پذیرفته نیستند.

## حداقل هدف محتوایی هر فناوری

برای هر یک از ۳۳ حوزهٔ مستقل زیر، هدف پایه ۵۰۰ مرجع/ورودی دستوری معتبر، ۱۰۰ مثال اجرایی، ۱۰۰ سناریوی عیب‌یابی یا پیاده‌سازی و ۵۰۰ واحد یادگیری است. این‌ها چهار نوع محتوا هستند و نباید با هم جمع زده شوند یا یکی به‌جای دیگری شمرده شود.

| شناسه | نام نمایشی | پوشش فنی ضروری |
|---|---|---|
| mikrotik | MikroTik RouterOS | CLI و مسیرها، interfaces/bridge/VLAN, IP, DHCP/DNS, routing, firewall/filter/NAT, queues/QoS, VPN, wireless, logs, backup, RouterOS v6/v7 |
| cisco | Cisco IOS / IOS-XE | EXEC/config modes, interface, VLAN/STP, EtherChannel, routing, OSPF/BGP, ACL, NAT, DHCP, FHRP, VPN, AAA, telemetry/troubleshooting |
| windows_batch | Windows Batch / CMD | دستورها، متغیرها، quoting، errorlevel، حلقه‌ها، شرط‌ها، فایل و سرویس، شبکه، logging، task scheduler، encoding، مدیریت خطا |
| powershell | PowerShell | cmdlet و parameter sets، pipeline، objects، providers، remoting، CIM/WMI، networking، services/processes، files، security، modules، error handling، نسخه 5.1 و 7+ |
| voip | VoIP / SIP / PBX | SIP methods/responses، SDP، RTP/RTCP، codecs، dial plan، extensions/trunks، NAT/SBC، QoS, TLS/SRTP، packet capture، Asterisk/FreePBX و پلتفرم‌های مشخص با برچسب جدا |
| fortigate | FortiGate / FortiOS | CLI config/diagnose/execute، interfaces/VLAN، policy، objects، routing، SD-WAN، NAT، IPsec/SSL VPN، HA، UTM، logs، debug flow؛ وابسته به نسخه |
| vmware_esxi | VMware ESXi / vSphere | ESXCLI namespaces، esxcli/vim-cmd، networking/vSwitch/vDS، storage/datastore، VM lifecycle، snapshots، services، logs، certificates، permissions، lifecycle/patching؛ نسخه‌بندی دقیق |
| ssh | SSH / OpenSSH | ssh/scp/sftp/ssh-keygen/ssh-agent/ssh-add/sshd، config directives، keys/certificates، ProxyJump/tunnels، host keys، hardening، troubleshooting؛ تفکیک client/server و OS |
| telnet | Telnet | کلاینت‌های سیستم‌عامل، گزینه‌ها، RFC/negotiation basics، تست پورت TCP، تشخیص سرویس؛ هشدار روشن که Telnet انتقال رمزنگاری‌نشده است و برای مدیریت امن توصیه نمی‌شود |
| ftp | FTP | ftp/lftp/curl و سرورهای FTP منتخب، active/passive، ports/NAT، مجوزها و عیب‌یابی؛ انتقال بدون TLS ناامن است |
| ftps | FTPS | FTP over TLS، implicit/explicit TLS، گواهی، trust chain، passive ports، عیب‌یابی handshake و certificate |
| sftp | SFTP | انتقال فایل روی SSH، کلیدها، known_hosts، batch mode، chroot و مجوز فایل؛ مستقل از FTP/FTPS |
| linux_bash | Linux Bash / GNU utilities | shell built-ins، coreutils، grep/sed/awk/find/xargs، pipes/redirection، process/service، networking، package، permissions، scripting/testing، distro notes |

## ماتریس اجباری سهمیه برای تمام فناوری‌های فصل ۶۸ (۳۳ حوزهٔ مستقل)

سهمیه برای **هر فناوری به‌صورت مستقل** اعمال می‌شود؛ اعداد بین فناوری‌ها قابل تجمیع نیستند. هر ردیف باید به چهار مجموعهٔ واقعی و جداگانه برسد: **۵۰۰ مرجع دستور/گزینه + ۱۰۰ مثال + ۱۰۰ سناریو + ۵۰۰ واحد یادگیری**. فایل‌های موجود با شمار کمتر (از جمله Docker و Windows Server) هنوز ناقص‌اند و باید تکمیل شوند.

| شناسه | فناوری/محصول | حداقل دستور | مثال | سناریو | واحد یادگیری |
|---|---|---:|---:|---:|---:|
| mikrotik | MikroTik RouterOS v6/v7 | 500 | 100 | 100 | 500 |
| cisco | Cisco IOS/IOS-XE | 500 | 100 | 100 | 500 |
| fortigate | FortiGate / FortiOS | 500 | 100 | 100 | 500 |
| windows_batch | Windows Batch / CMD | 500 | 100 | 100 | 500 |
| powershell | PowerShell 5.1 و 7+ | 500 | 100 | 100 | 500 |
| windows_server | Windows Server / AD DS / GPO | 500 | 100 | 100 | 500 |
| linux_bash | Linux / Bash / GNU utilities | 500 | 100 | 100 | 500 |
| docker | Docker / Compose | 500 | 100 | 100 | 500 |
| voip | VoIP / SIP / RTP / PBX | 500 | 100 | 100 | 500 |
| vmware_esxi | VMware ESXi / vSphere | 500 | 100 | 100 | 500 |
| ssh | SSH / OpenSSH | 500 | 100 | 100 | 500 |
| telnet | Telnet / TCP diagnostic | 500 | 100 | 100 | 500 |
| ftp | FTP | 500 | 100 | 100 | 500 |
| ftps | FTPS | 500 | 100 | 100 | 500 |
| sftp | SFTP (SSH File Transfer Protocol) | 500 | 100 | 100 | 500 |
| zabbix | Zabbix monitoring/API | 500 | 100 | 100 | 500 |
| wireshark | Wireshark / TShark / tcpdump | 500 | 100 | 100 | 500 |
| juniper | Juniper Junos | 500 | 100 | 100 | 500 |
| aruba | Aruba AOS-CX / HPE networking | 500 | 100 | 100 | 500 |
| proxmox | Proxmox VE | 500 | 100 | 100 | 500 |
| hyperv | Microsoft Hyper-V | 500 | 100 | 100 | 500 |
| ansible | Ansible / Ansible CLI | 500 | 100 | 100 | 500 |
| terraform | Terraform / IaC | 500 | 100 | 100 | 500 |
| kubernetes | Kubernetes / kubectl | 500 | 100 | 100 | 500 |
| ubiquiti | Ubiquiti UniFi / EdgeOS (تفکیک‌شده) | 500 | 100 | 100 | 500 |
| snmp_syslog | SNMP / Syslog / NetFlow / IPFIX | 500 | 100 | 100 | 500 |
| dns_dhcp_ntp | DNS / DHCP / NTP / IPAM | 500 | 100 | 100 | 500 |
| web_tls | Nginx / Apache / HTTP(S) / TLS / PKI | 500 | 100 | 100 | 500 |
| cloud | AWS / Azure (هر ارائه‌دهنده با برچسب مستقل) | 500 | 100 | 100 | 500 |
| fortinet_management | FortiManager / FortiAnalyzer | 500 | 100 | 100 | 500 |
| security_ops | Sysmon / SIEM / SOC / incident response | 500 | 100 | 100 | 500 |
| git | Git / GitHub / release workflows | 500 | 100 | 100 | 500 |
| backup_recovery | Backup / restore / disaster recovery | 500 | 100 | 100 | 500 |

**مجموع هدف این ماتریس (۳۳ فناوری/خانواده):** ۱۵٬۵۰۰ مرجع دستوری، ۳٬۱۰۰ مثال، ۳٬۱۰۰ سناریو و ۱۵٬۵۰۰ واحد یادگیری. این‌ها هدف تولید هستند، نه شمار محتوای موجود. فناوری‌های دارای چند محصول یا سیستم‌عامل باید در زیرگروه‌های جداگانه طبقه‌بندی شوند؛ سهمیهٔ یک محصول را نمی‌توان با محصول دیگر پر کرد.

## ترتیب اجرا و گزارش پیشرفت

1. ابتدا هر بستهٔ موجود را بدون حذف داده ممیزی می‌کنیم؛ رکوردهای واقعی، مثال‌ها، سناریوها و واحدهای یادگیری جداگانه شمرده می‌شوند.
2. فناوری‌های فعلی با کمبود، از جمله Docker و Windows Server، به هدف می‌رسند؛ PowerShell از CMD جدا می‌ماند.
3. سپس بسته‌های مستقل جدید به ترتیب شبکه/دسترسی، مجازی‌سازی، پایش/عیب‌یابی، اتوماسیون، سرویس‌های زیرساخت و امنیت تکمیل می‌شوند.
4. هر بسته تا گذر از JSON/schema، UID، duplicate معنایی، answer key، بررسی syntax/نسخه، جستجو و تست ادغام، وضعیت `in_progress` یا `review_required` دارد؛ فقط پس از عبور از تمام گیت‌ها `validated` می‌شود.
5. هیچ تعداد هدفی در `INDEX.json` به‌عنوان تعداد واقعی گزارش نمی‌شود مگر از فایل‌های واقعی و خروجی validator محاسبه شده باشد.

## تعریف «مرجع/ورودی دستوری معتبر»

هر رکورد دستور باید حداقل این فیلدهای معنایی را داشته باشد (نام کلیدهای JSON نهایی باید با schema فعلی مخزن تطبیق داده شود):

- شناسهٔ یکتا، فناوری/محصول، بخش قابل نمایش، عنوان روشن
- دستور/الگوی syntax و شرح آرگومان‌ها: اجباری، اختیاری، نوع، مقدار نمونه و پیش‌فرض در صورت معلوم بودن
- حالت اجرا و سطح دسترسی لازم؛ دستگاه/سیستم و نسخه‌های پشتیبانی‌شده
- کاربرد و زمان استفاده، پیش‌نیازها، خروجی مورد انتظار و روش بررسی
- مثال عملی با مقادیر نمونهٔ غیرحساس
- خطاهای رایج، محدودیت‌ها و ملاحظات امنیتی
- کلیدواژه‌های فارسی/انگلیسی برای جستجو، برچسب‌ها و منبع مرجع/تاریخ بازبینی
- برای تغییرات مخرب: impact، backup/rollback و هشدار پیش از اجرا

اگر یک فرمان در چند نسخه رفتار متفاوت دارد، تفاوت نسخه به‌عنوان variant ثبت شود؛ نه این‌که رکورد تکراری بی‌توضیح ساخته شود.

## تعریف انواع محتوای آموزشی

- **۵۰۰ مرجع دستور/گزینه:** ورودی‌های متمایز و قابل جستجو. برای ابزارهای مبتنی بر آرگومان، گزینه‌ها فقط وقتی جداگانه شمرده شوند که کاربرد، نوع یا رفتار متمایز و مستند داشته باشند.
- **۱۰۰ مثال:** ورودی/فرمان، توضیح خط‌به‌خط، خروجی نمونه یا نتیجهٔ قابل انتظار، پیش‌نیاز و روش راستی‌آزمایی.
- **۱۰۰ سناریو:** مسئله، نشانه‌ها، فرضیه‌ها، مراحل تشخیص، راه‌حل، تأیید، rollback و نکتهٔ پیشگیری.
- **۵۰۰ واحد یادگیری:** هدف آموزشی مستقل، توضیح مفهومی، پیش‌نیاز، مثال، تمرین یا سؤال و معیار پاسخ. بازنویسی یک توضیح با واژگان متفاوت واحد یادگیری جدید نیست.
- **آزمون و پاسخ‌نامه:** سؤال‌ها و answer key در فایل‌های جداگانه؛ پاسخ‌ها با شناسهٔ سؤال متناظر، توضیح علت درستی پاسخ و بازبینی خودکار index/UID.

## نام‌گذاری و طبقه‌بندی در رابط

- عنوان فناوری، عنوان دستهٔ قابل‌فهم و عنوان رکورد جدا از هم باشند.
- slug فنی مانند `routing/ospf` برای فیلتر داخلی مجاز است، اما عنوان UI باید «Cisco IOS-XE — OSPF» یا نام روشن مشابه باشد.
- «زیرفصل ۱»، «سایر»، «عمومی» فقط در صورت نیاز واقعی و پس از طبقه‌بندی همهٔ موارد استفاده شود.
- فیلترهای پیشنهادی: فناوری، بخش، نسخه، سطح، نوع محتوا، خطر، نیاز به دسترسی مدیر.
- جستجو باید فارسی و انگلیسی، نام دستور، آرگومان، alias و کاربرد را ایندکس کند؛ نتایج هر فناوری نباید با فناوری دیگر مخلوط شوند مگر کاربر «همهٔ فناوری‌ها» را انتخاب کند.

## گیت‌های پذیرش قبل از ادعای تکمیل

1. JSON parse و schema validation برای تمام فایل‌های مرجع.
2. شمارش خودکار کل رکوردها، یکتایی UIDها، ارجاع‌های معتبر و پاسخ‌نامه‌های بدون orphan.
3. گزارش duplicate معنایی بر اساس فناوری + syntax نرمال‌شده + نسخه/variant.
4. בדיקה/بازبینی فنی برای syntax و آرگومان‌ها؛ نمونهٔ دستورات از منبع رسمی vendor/protocol و نسخهٔ مرجع ثبت شود.
5. تست جستجو با عبارت فارسی، انگلیسی، syntax، آرگومان و نام بخش.
6. اجرای importer/build برای Windows و Android و تأیید نمایش تعداد/نام دسته‌ها و جستجو در خود برنامه.
7. مقایسهٔ قبل/بعد برای اطمینان از حفظ بسته‌ها و رکوردهای قدیمی؛ ثبت گزارش در `VALIDATION.md`.
8. وضعیت فقط یکی از این مقادیر باشد: `planned`, `in_progress`, `review_required`, `validated`. فقط پس از عبور از تمام گیت‌ها وضعیت `validated` شود.

## ترتیب اجرای پیشنهادی

1. استخراج inventory واقعی و ارزیابی عمق فایل‌های موجود؛ نگه‌داشتن تمام فایل‌های فعلی.
2. اصلاح schema/mapper و UI category/search پیش از تولید انبوه.
3. تکمیل هر فناوری در بسته‌های کوچک قابل بازبینی، ابتدا دستورهای پرکاربرد و پرریسک‌نبودن syntax.
4. ساخت مثال‌ها و سناریوها از روی دستورهای تأییدشده؛ نه تولید متن‌های عمومی یکسان برای رسیدن به سهمیه.
5. تولید واحدهای یادگیری و آزمون با پاسخ‌نامهٔ جداگانه.
6. اجرای validator و تست واقعی Windows/Android؛ ثبت اعداد واقعی و موارد باقیمانده.

**محدودیت مهم:** این سند هدف و معیار کیفیت را تعریف می‌کند؛ به‌تنهایی هیچ سهمیه‌ای را تکمیل نمی‌کند. شمار نهایی باید از رکوردهای واقعی، متمایز، مستند و اعتبارسنجی‌شده به دست آید.
