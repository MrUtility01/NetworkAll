# -*- coding: utf-8 -*-
"""فصل ۰۹ — ARP · ICMP · TCP · UDP"""
from __future__ import annotations
import re
from typing import Any, Dict, Tuple

def _level(title: str) -> str:
    m = re.match(r"\[(L[0-4])\]", title or "")
    return m.group(1) if m else "L0"

def _topic(title: str) -> str:
    t = re.sub(r"^\[L[0-4]\]\s*", "", title or "")
    t = re.sub(r"\s*[—\-]\s*(آشنایی|مقدماتی|ادمین|مهندس|خبره|Intro|Junior|Admin|Senior|Architect).*$", "", t, flags=re.I)
    return t.strip()

def _bucket(topic: str) -> str:
    t = (topic or "").lower()
    if any(k in t for k in ("udp", "ویژگی", "ویژگی‌ها", "datagram", "connectionless", "بدون اتصال")):
        return "udp"
    if any(k in t for k in ("tcp", "handshake", "three-way", "سه دست", "sequence", "window", "syn", "fin", "rst", "اتصال‌گرا")):
        return "tcp"
    if any(k in t for k in ("icmp", "echo", "ping", "unreachable", "ttl", "time exceeded")):
        return "icmp"
    if any(k in t for k in ("arp", "request", "reply", "gratuitous", "proxy arp")):
        return "arp"
    return "arp"

def _depth(level: str) -> str:
    return {"L0": "تصویر ذهنی", "L1": "فریم‌به‌فریم+Lab", "L2": "دستور و عیب‌یابی", "L3": "تحلیل پکت", "L4": "امنیت"}.get(level, "")

def _arp(topic, level):
    summary = f"«{topic}»: ARP می‌پرسد این IP کدام MAC است تا فریم Ethernet ساخته شود."
    full = f"""# {topic}

**سطح:** {level} — {_depth(level)}

## تشبیه
پرسیدن در راهرو: کی IP 192.168.1.10 را دارد؟

## Request / Reply
1) Request پخش (broadcast)
2) Reply با MAC (unicast)
3) کش ARP به‌روز می‌شود

## فریم‌به‌فریم قبل از ping
هم‌ساب‌نت؟ → کش خالی؟ → Request → Reply → فریم با Dest MAC

## خاص
Gratuitous ARP | Proxy ARP | Incomplete

## عیب‌یابی
ping LAN fail → ARP/VLAN/کابل | MAC اشتباه → تداخل IP/spoof
"""
    commands = """```
arp -a
```
```
ip neigh
```
```
ping -c 1 <gw>
ip neigh
```
"""
    lab = """# Lab ARP
قبل/بعد پینگ به GW جدول arp/neigh را ببین. IP خاموش → incomplete؟
"""
    return summary, full, commands, lab

def _icmp(topic, level):
    summary = f"«{topic}»: ICMP پیام کنترل/خطای لایه ۳ است؛ ping فقط Echo است."
    full = f"""# {topic}

**سطح:** {level} — {_depth(level)}

## Echo
Request → Reply | نبودن Reply ≠ همیشه میزبان مرده (فیلتر ICMP)

## پیام‌های رایج
Destination Unreachable | Time Exceeded (traceroute)

## فریم traceroute
TTL=1 → روتر اول Time Exceeded → TTL=2 → ...

## تفسیر ping
GW OK → LAN زنده | 8.8.8.8 OK → مسیر عمومی | IP OK نام نه → DNS
"""
    commands = """```
ping -c 4 8.8.8.8
```
```
ping -n 4 <gateway>
```
```
traceroute -n 8.8.8.8
```
```
tracert -d 8.8.8.8
```
"""
    lab = """# Lab ICMP
پینگ 127.0.0.1 و GW و 8.8.8.8 — جدول OK/Fail. traceroute کجا ستاره می‌دهد؟
"""
    return summary, full, commands, lab

def _tcp(topic, level):
    summary = f"«{topic}»: تحلیل TCP شامل چرخهٔ عمر اتصال، شمارهٔ توالی بایت، ACK تجمعی، پنجرهٔ دریافت، کنترل ازدحام و شواهد packet capture است."
    level_focus = {
        "L0": "تصویر ذهنی: TCP اتصال منطقی میان دو endpoint می‌سازد؛ این اتصال مدار فیزیکی اختصاصی نیست. IP بسته را حمل می‌کند و پورت، برنامهٔ مقصد را مشخص می‌کند.",
        "L1": "عملی: در capture، SYN، SYN-ACK و ACK را پیدا کنید و تفاوت Sequence Number با Acknowledgment Number را با مثال عددی توضیح دهید.",
        "L2": "ادمین: وضعیت socket، listener، timeout، خطای اتصال و retransmission را با ابزارهای سیستم‌عامل از هم تفکیک کنید.",
        "L3": "مهندسی: RTT، duplicate ACK، SACK، advertised receive window و MSS را در capture تحلیل کنید؛ reordering و محل capture را نیز در نظر بگیرید.",
        "L4": "معماری: TCP را در کنار NAT، load balancer، firewall state table، TLS، backlog، timeout و الگوریتم کنترل ازدحام ارزیابی کنید."
    }.get(level, "")
    full = f"""# {topic}

**سطح:** {level} — {_depth(level)}

## نقشهٔ راه
TCP (Transmission Control Protocol) در لایهٔ انتقال، جریان بایت مرتب و قابل اتکا در اختیار برنامه قرار می‌دهد. TCP مرز پیام‌های برنامه را حفظ نمی‌کند و به‌تنهایی محرمانگی یا احراز هویت رمزنگاری‌شده ندارد. هدف درس، توضیح handshake، خواندن SEQ/ACK، تفکیک FIN از RST و ساخت فرضیهٔ عیب‌یابی بر اساس شواهد است.

## آموزش از صفر
اتصال TCP یک وضعیت نرم‌افزاری در دو endpoint است، نه مسیر فیزیکی رزروشده. اتصال معمولاً با چهار‌تایی آدرس IP مبدأ، پورت مبدأ، IP مقصد و پورت مقصد شناخته می‌شود. به همین دلیل، یک سرور می‌تواند چند اتصال هم‌زمان به یک پورت مقصد داشته باشد: آدرس یا پورت مبدأ کلاینت‌ها متفاوت است.

{level_focus}

## سه‌مرحله‌ای بودن handshake
1. کلاینت SYN می‌فرستد و شمارهٔ توالی اولیهٔ خود را اعلام می‌کند.
2. سرور SYN-ACK می‌فرستد؛ شمارهٔ توالی خودش و تأیید SYN کلاینت را در بر دارد.
3. کلاینت ACK می‌فرستد و اتصال وارد حالت Established می‌شود.
این تبادل آمادگی دو TCP endpoint را هماهنگ می‌کند؛ تضمین نمی‌کند که برنامهٔ کاربردی سالم است یا درخواست بعدی حتماً موفق می‌شود.

## مثال حل‌شده: شمارهٔ توالی
فرض کنید A یک segment با SEQ=1000 و payload برابر 500 بایت می‌فرستد. اگر بایت‌ها پیوسته دریافت شوند، B معمولاً ACK=1500 می‌فرستد؛ ACK شمارهٔ بایت بعدی مورد انتظار است، نه شمارندهٔ بسته‌ها. SYN و FIN هرکدام یک شمارهٔ توالی مصرف می‌کنند، حتی اگر payload نداشته باشند. اگر segment بعدی خارج از ترتیب برسد، گیرنده ممکن است ACK تجمعی قبلی را تکرار کند. این علامت به‌تنهایی ثابت نمی‌کند بسته در شبکه گم شده؛ جابه‌جایی ترتیب و capture ناقص نیز ممکن است.

## کنترل جریان در برابر کنترل ازدحام
- Receive Window (rwnd): فضای بافر اعلام‌شده از سوی گیرنده را بازتاب می‌دهد تا فرستنده گیرنده را سرریز نکند.
- Congestion Window (cwnd): محدودیت فرستنده بر مبنای الگوریتم کنترل ازدحام و نشانه‌های شبکه است.
- Flight Size: دادهٔ ارسال‌شده اما هنوز تأییدنشده.
rwnd و cwnd یکی نیستند. نرخ قابل ارسال به پنجره‌ها، دادهٔ تأییدنشده، MSS، RTT و شرایط پیاده‌سازی وابسته است.

## Loss، retransmission و RTT
TCP ممکن است پس از timeout یا نشانه‌های ACK/SACK داده را دوباره ارسال کند. retransmission زیاد می‌تواند از loss، ازدحام، reordering، مسیر نامتقارن یا نقطهٔ capture نامناسب ناشی شود. RTT زمان رفت‌وبرگشت است و timeout باید تغییرپذیری RTT را لحاظ کند. برچسب تحلیلی Wireshark مانند TCP Retransmission را با توالی بسته‌ها و ACKها بررسی کنید؛ برچسب ابزار به‌تنهایی علت ریشه‌ای نیست.

## پایان اتصال: FIN در برابر RST
- FIN: یک سمت اعلام می‌کند دادهٔ بیشتری برای ارسال ندارد؛ جریان دوطرفه می‌تواند نیمه‌بسته شود و پایان مرتب معمولاً تأییدهای متقابل دارد.
- RST: اتصال یا تلاش اتصال را reset می‌کند؛ ممکن است به نبود listener، وضعیت نامعتبر یا سیاست یک واسط میانی مرتبط باشد.
- SYN بدون پاسخ با RST یکسان نیست. نبود پاسخ می‌تواند ناشی از drop، مسیر برگشت یا مقصد خاموش باشد؛ RST یعنی reset مشاهده شده، اما منبع آن نیز باید بررسی شود.

## دستورات و تفسیر
Linux:
    ss -lntp
    ss -tan state established
    ss -ti

Windows PowerShell:
    Get-NetTCPConnection | Sort-Object State,LocalPort
    Test-NetConnection -ComputerName example.com -Port 443 -InformationLevel Detailed

Wireshark روی capture مجاز:
    tcp.flags.syn == 1
    tcp.analysis.retransmission
    tcp.stream eq N

N باید از همان capture انتخاب شود؛ شمارهٔ stream شناسهٔ سراسری یا مقدار ثابتی نیست. گزینه‌ها و خروجی‌ها ممکن است با نسخهٔ ابزار فرق داشته باشند.

## آزمایشگاه ایمن و تکرارپذیر
**هدف:** تشخیص listener فعال، پورت بدون listener و timeout، فقط روی VM یا میزبان تحت کنترل خودتان.

1. یک سرویس آزمایشی محلی اجرا کنید و وضعیت listener را با ss یا Get-NetTCPConnection ثبت کنید.
2. از کلاینت خود به پورت باز وصل شوید و خروجی آزمون را ذخیره کنید.
3. سرویس را متوقف و همان آزمون را تکرار کنید؛ connection refused/RST را با timeout یکی نگیرید.
4. اگر مجاز و ممکن است، capture کوتاهی روی رابط VM خود بگیرید و SYN، SYN-ACK، ACK و پایان اتصال را بیابید.
5. سرویس را دوباره راه‌اندازی کنید و نتیجه را اعتبارسنجی کنید؛ محیط را به حالت اولیه برگردانید.

**انتظار:** پورت شنونده معمولاً اتصال را می‌پذیرد؛ پورت بدون listener ممکن است با RST رد شود؛ فایروال یا مسیر drop‌کننده می‌تواند timeout بسازد. این الگوها رایج‌اند، نه تضمین مطلق؛ سیستم‌عامل و سیاست شبکه نتیجه را تغییر می‌دهند.

## عیب‌یابی مبتنی بر شواهد
| نشانه | فرضیه‌ها | آزمون تفکیک‌کننده |
|---|---|---|
| SYN بدون پاسخ | drop مسیر، فایروال، route برگشت، مقصد خاموش، capture نامناسب | بررسی route و log مجاز؛ capture در دو سر |
| RST پس از SYN | listener نیست، پورت اشتباه، reset واسط میانی | بررسی listener و capture نزدیک مقصد |
| handshake موفق اما برنامه کند | RTT بالا، loss، پنجره محدود، تأخیر برنامه یا صف سرور | زمان‌بندی درخواست، ss -ti و capture هم‌زمان |
| retransmission زیاد | loss، ازدحام، reordering یا capture ناقص | مقایسهٔ دو نقطهٔ capture و شمارنده‌های رابط |
| اتصال‌های نیمه‌باز فراوان | backlog، کلاینت کند، فشار منابع یا سوءاستفاده | بررسی queue، نرخ SYN، log و ظرفیت |

روش ثابت: Symptom → Scope → Evidence → Hypothesis → Test → Fix → Verify → Document. پیش از تغییر فایروال یا پارامترهای kernel، baseline بگیرید و rollback روشن داشته باشید.

## امنیت و محدودیت‌ها
TCP رمزنگاری‌شده نیست؛ برای محرمانگی و احراز هویت از TLS یا پروتکل امن مناسب استفاده کنید. SYN flood، مصرف منابع اتصال، افشای پورت مدیریتی و timeout نامناسب ریسک عملیاتی‌اند. فایروال را بی‌دلیل خاموش نکنید و پارامترهای kernel را بدون سنجش بار و روش بازگشت تغییر ندهید. Capture ممکن است دادهٔ حساس داشته باشد؛ دسترسی و زمان نگهداری آن را محدود کنید.

## خلاصه
TCP جریان بایت مرتب و قابل اتکا فراهم می‌کند؛ handshake اتصال را هماهنگ می‌کند، SEQ/ACK دریافت داده را پیگیری می‌کنند، rwnd کنترل جریان و cwnd کنترل ازدحام را پشتیبانی می‌کند، و FIN با RST تفاوت دارد. برای عیب‌یابی، وضعیت socket و capture را همراه شواهد دو سر ارتباط تحلیل کنید؛ یک علامت منفرد برای نتیجه‌گیری کافی نیست.

## واژه‌نامه
- SYN: آغاز هماهنگی اتصال.
- ACK: شمارهٔ بایت بعدی مورد انتظار.
- MSS: بیشینهٔ payload TCP در یک segment.
- RTT: زمان رفت‌وبرگشت.
- rwnd: پنجرهٔ اعلام‌شده توسط گیرنده.
- cwnd: پنجرهٔ کنترل ازدحام فرستنده.
- SACK: گزارش بلوک‌های دادهٔ دریافت‌شده خارج از محدودهٔ تجمعی.
- RTO: زمان انتظار پیش از ارسال مجدد مبتنی بر timeout.
- TIME-WAIT: وضعیت انتهایی برای کمک به تخلیهٔ segmentهای قدیمی و پایان قابل اتکا.
"""
    commands = """Linux:
    ss -lntp
    ss -tan state established
    ss -ti

Windows PowerShell:
    Get-NetTCPConnection | Sort-Object State,LocalPort
    Test-NetConnection -ComputerName example.com -Port 443 -InformationLevel Detailed

Wireshark:
    tcp.flags.syn == 1
    tcp.analysis.retransmission
    tcp.stream eq N
"""
    lab = """# Lab TCP — فقط میزبان یا VM تحت کنترل شما
1. یک listener محلی اجرا و وضعیت آن را ثبت کنید.
2. به پورت باز وصل شوید؛ سرویس را متوقف و همان آزمون را تکرار کنید.
3. تفاوت connection refused/RST با timeout را توضیح دهید.
4. در صورت وجود capture، SYN/SYN-ACK/ACK و FIN یا RST را بیابید.
5. سرویس را بازگردانید و نتیجه را دوباره اعتبارسنجی کنید.
معیار قبولی: توضیح مبتنی بر شواهد، تفکیک فرضیه از واقعیت و پاک‌سازی محیط آزمایش.
"""
    return summary, full, commands, lab

def _udp(topic, level):
    summary = f"«{topic}»: UDP دیتاگرام‌محور و بدون handshake انتقال است؛ قابلیت اطمینان، ترتیب و کنترل ازدحامِ برنامه‌محور را نباید به‌صورت خودکار از آن فرض کرد."
    level_focus = {
        "L0": "UDP را مانند ارسال بسته‌های مستقل تصور کنید؛ هر دیتاگرام جداگانه حمل می‌شود و شبکه تضمین نمی‌کند حتماً برسد یا به همان ترتیب برسد.",
        "L1": "پورت مبدأ/مقصد، طول دیتاگرام و checksum را بشناسید و تفاوت UDP با جریان بایت TCP را با مثال DNS و صوت زنده توضیح دهید.",
        "L2": "socketهای UDP، قواعد فایروال، MTU و تفاوت خطای DNS با خطای transport را با ابزارهای سیستم‌عامل بررسی کنید.",
        "L3": "در capture، query/response، retransmission سطح برنامه، fragmentation و اثر loss/jitter را از هم جدا کنید.",
        "L4": "برای سامانهٔ UDP، طراحی timeout/retry، rate limiting، کنترل ازدحام برنامه، amplification risk و مشاهده‌پذیری را ارزیابی کنید."
    }.get(level, "")
    full = f"""# {topic}

**سطح:** {level} — {_depth(level)}

## مدل ذهنی و هدف
UDP (User Datagram Protocol) یک پروتکل دیتاگرام‌محور در لایهٔ انتقال است. برخلاف TCP، handshake اتصال ندارد و به‌خودی‌خود تضمین تحویل، ترتیب یا حذف تکرار را فراهم نمی‌کند. این سادگی برای تأخیر کم و برنامه‌هایی که خودشان سیاست بازیابی را مدیریت می‌کنند مفید است؛ اما به معنای «همیشه سریع‌تر» یا «بدون خطا» نیست.

{level_focus}

## ساختار و رفتار
UDP header ساده‌ای شامل پورت مبدأ، پورت مقصد، طول و checksum دارد. هر فراخوانی ارسال معمولاً یک دیتاگرام مستقل تولید می‌کند؛ مرز پیام در UDP حفظ می‌شود، اما ممکن است دیتاگرام گم، تکرار یا خارج از ترتیب برسد. checksum برای تشخیص برخی خطاهاست، نه تضمین تحویل یا اصالت رمزنگاری‌شده. در IPv4 checksum می‌تواند صفر باشد؛ در IPv6 عموماً checksum اجباری است، با استثناهای محدود در برخی تونل‌ها.

## مثال: DNS
یک resolver ممکن است query را با UDP به پورت 53 سرور DNS بفرستد. اگر پاسخ نرسد، کلاینت یا کتابخانهٔ DNS ممکن است پس از timeout دوباره تلاش کند؛ این retry رفتار برنامه است، نه تضمین UDP. بعضی پاسخ‌ها به‌دلیل اندازه، سیاست یا نیازهای پروتکل از TCP نیز استفاده می‌کنند. بنابراین «DNS همیشه UDP است» گزارهٔ نادرستی است.

## UDP در برابر TCP
- TCP: جریان بایت مرتب، ACK و ارسال مجدد در transport؛ سربار و وضعیت اتصال بیشتر.
- UDP: دیتاگرام مستقل و بدون handshake؛ مسئولیت retry، ترتیب و تشخیص ازدست‌رفتن در صورت نیاز بر عهدهٔ برنامه است.
- صوت/ویدئوی بلادرنگ گاهی ترجیح می‌دهند دادهٔ قدیمی را به‌جای انتظار برای ارسال مجدد کنار بگذارند؛ برنامه باید jitter buffer، نرخ ارسال و افت بسته را مدیریت کند.
- QUIC روی UDP ساخته شده، اما قابلیت‌های قابلیت‌اطمینان، امنیت TLS و کنترل ازدحام را در لایهٔ بالاتر پیاده‌سازی می‌کند؛ پس UDP به‌تنهایی معادل QUIC نیست.

## MTU، fragmentation و اندازهٔ دیتاگرام
دیتاگرام بزرگ می‌تواند با MTU مسیر ناسازگار باشد. در IPv4 fragmentation ممکن است رخ دهد، اما از دست رفتن یک fragment می‌تواند کل دیتاگرام را غیرقابل استفاده کند؛ در IPv6 روترهای میانی fragment نمی‌کنند و میزبان مبدأ باید سازوکار مناسب را به کار گیرد. در طراحی جدید، اندازهٔ payload و Path MTU را در نظر بگیرید و از اتکا به دیتاگرام‌های بزرگِ بدون آزمون خودداری کنید.

## دستورات و مشاهده‌پذیری
Linux:
    ss -uln
    ss -uap
    ip route get 192.0.2.10

Windows PowerShell:
    Get-NetUDPEndpoint
    Resolve-DnsName example.com -Type A

Wireshark در capture مجاز:
    udp
    udp.port == 53
    dns

IP نمونهٔ 192.0.2.10 برای مستندسازی است؛ در لابراتوار، مقصد تحت کنترل خود را جایگزین کنید. وجود socket محلی به‌تنهایی ثابت نمی‌کند که بسته به مقصد می‌رسد یا پاسخ برمی‌گردد.

## آزمایشگاه ایمن
**هدف:** مشاهدهٔ تفاوت socket محلی، درخواست DNS و پاسخ واقعی.

1. با ss -uln یا Get-NetUDPEndpoint endpointهای محلی را فهرست کنید.
2. یک query DNS مجاز با Resolve-DnsName یا ابزار موجود اجرا کنید.
3. اگر امکان دارد capture کوتاهی فقط روی میزبان خود بگیرید و پورت مبدأ/مقصد، طول و پاسخ را ثبت کنید.
4. یک نام دامنهٔ ناموجود را با دقت انتخاب کنید و پاسخ خطای DNS را از timeout شبکه جدا کنید.
5. نتیجه را در دو حالت شبکهٔ سالم و محیط آزمایش کنترل‌شده ثبت کنید؛ هیچ flood یا ارسال انبوه دیتاگرام اجرا نکنید.

**انتظار:** query و پاسخ معمولاً با پورت‌های UDP قابل مشاهده‌اند، اما استفاده از TCP یا resolver رمزگذاری‌شده بسته به محیط ممکن است. نتیجهٔ یک ابزار را به همهٔ مسیرها تعمیم ندهید.

## عیب‌یابی
| نشانه | فرضیه‌ها | بررسی |
|---|---|---|
| query می‌رود، پاسخی دیده نمی‌شود | مقصد/route، ACL، پاسخ دیررس، capture یک‌طرفه | capture دو سمت و بررسی resolver/فایروال |
| DNS روی یک شبکه کار می‌کند و دیگری نه | سیاست UDP/TCP 53، captive portal، resolver متفاوت | مقایسهٔ سرور مقصد، پاسخ و log مجاز |
| صوت دچار قطع‌ووصلی است | loss، jitter، صف، نرخ ارسال یا jitter buffer | آمار برنامه، شمارندهٔ رابط و capture زمان‌دار |
| دیتاگرام‌های بزرگ شکست می‌خورند | MTU، fragmentation یا فیلتر fragment | بررسی اندازه و مسیر؛ آزمون کنترل‌شدهٔ PMTU |
| پاسخ‌ها تکراری یا خارج از ترتیب‌اند | رفتار برنامه یا شبکه | شناسهٔ پیام/sequence در پروتکل کاربردی و capture |

## امنیت
UDP هم برای سرویس‌های عادی و هم برای حملات reflection/amplification قابل استفاده است. سرویس عمومی باید پاسخ‌دهی را به درخواست معتبر محدود کند، اندازه و نرخ پاسخ را کنترل کند و از باز بودن resolverهای ناخواسته جلوگیری کند. rate limit و retry باید با ظرفیت سرویس هماهنگ باشند؛ retry تهاجمی می‌تواند ازدحام را تشدید کند. هیچ آزمایش حجمی را روی سرویس ثالث انجام ندهید.

## خلاصه و واژه‌نامه
UDP دیتاگرام مستقل حمل می‌کند و در transport تحویل، ترتیب و retry را تضمین نمی‌کند. برنامه باید متناسب با نیاز خود timeout، retry، sequence، jitter و کنترل ازدحام را طراحی کند.
- Datagram: واحد مستقل داده در UDP.
- Jitter: تغییرپذیری تأخیر بسته‌ها.
- Loss: از دست رفتن داده.
- MTU: بیشینهٔ اندازهٔ بستهٔ قابل حمل در یک پیوند.
- Amplification: بزرگ‌تر شدن پاسخ نسبت به درخواست و امکان سوءاستفاده در بازتاب ترافیک.
"""
    commands = """Linux:
    ss -uln
    ss -uap
    ip route get 192.0.2.10

Windows PowerShell:
    Get-NetUDPEndpoint
    Resolve-DnsName example.com -Type A

Wireshark:
    udp
    udp.port == 53
    dns
"""
    lab = """# Lab UDP — فقط میزبان و resolver مجاز
1. endpointهای UDP محلی را فهرست کنید.
2. یک DNS query مجاز اجرا و نتیجه را ثبت کنید.
3. در صورت امکان capture محدود بگیرید و query/response را شناسایی کنید.
4. پاسخ خطای DNS را از timeout و نبود پاسخ transport جدا کنید.
5. زمان، مقصد و نتیجه را ثبت کنید؛ از flood یا ترافیک حجمی خودداری کنید.
"""
    return summary, full, commands, lab

_BUILDERS = {"arp": _arp, "icmp": _icmp, "tcp": _tcp, "udp": _udp}

def build_chapter09_lesson(title_fa: str, title_en: str = "") -> Dict[str, Any] | None:
    topic, level = _topic(title_fa), _level(title_fa)
    b = _bucket(topic)
    summary, full, commands, lab = _BUILDERS[b](topic, level)
    return {
        "summary": summary, "full_content": full, "commands": commands,
        "examples": lab, "notes": f"فصل۰۹ · {b} · {level}", "lab": lab,
        "level": level, "topic": topic, "category": b, "chapter": 9,
    }
