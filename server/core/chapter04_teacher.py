# -*- coding: utf-8 -*-
"""فصل ۰۴ — سیستم‌عامل پایه: Kernel · ویندوز · لینوکس · عیب‌یابی منابع"""
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
    if any(k in t for k in ("kernel", "هسته", "process", "thread", "scheduler", "syscall", "user mode", "مفهوم", "virtual memory")):
        return "kernel"
    if any(k in t for k in ("registry", "ویندوز", "windows", "powershell", "event viewer", "task manager", "services", "ntfs")):
        return "windows"
    if any(k in t for k in ("لینوکس", "linux", "سلسله", "filesystem", "systemd", "chmod", "journalctl", "fhs", "ext4", "inode")):
        return "linux"
    if any(k in t for k in ("cpu بالا", "منابع", "resource", "swap", "گلوگاه", "iostat", "bottleneck", "load", "عیب")):
        return "resource"
    return "kernel"

def _depth(level: str) -> str:
    return {"L0": "تصویر ذهنی", "L1": "مثال+Lab", "L2": "دستور ادمین", "L3": "تحلیل گلوگاه", "L4": "استاندارد سازمانی"}.get(level, "")

def _kernel(topic, level):
    summary = f"«{topic}»: هسته (Kernel) واسط سخت‌افزار و برنامه‌هاست؛ برنامه مستقیم به دیسک/رم دست نمی‌زند."
    full = f"""# {topic}

**سطح:** {level} — {_depth(level)}

## تشبیه
برنامه = مشتری رستوران | Kernel = آشپزخانه | سخت‌افزار = اجاق و مواد

## User Mode در برابر Kernel Mode
| | User | Kernel |
|--|------|--------|
| دسترسی | غیرمستقیم | مستقیم |
| خرابی | معمولاً همان برنامه | ممکن است کل سیستم |

## Process و Thread
Process = برنامه در حال اجرا با حافظه جدا | Thread = مسیر اجرا داخل همان process

## فریم‌به‌فریم read فایل
1) برنامه read می‌زند 2) Syscall وارد Kernel 3) مجوز و مسیر 4) Cache یا دیسک 5) بازگشت به User

## Scheduler و حافظه مجازی
نوبت CPU را Kernel می‌دهد. صفحه (page) به RAM یا swap نگاشت می‌شود. کمبود RAM → فشار swap → کندی.

## خلاصه
Kernel نگهبان منابع است.
"""
    commands = f"""# — {topic}
## ویندوز
```
tasklist
```
```
Get-Process | Sort-Object CPU -Descending | Select-Object -First 10
```
## لینوکس
```
ps aux --sort=-%cpu | head
```
```
top
```
```
free -h
```
```
uname -r
```
"""
    lab = f"""# آزمایشگاه — {topic}

## آزمایش ۱: دیدن processها
Task Manager یا `ps aux | head`

## آزمایش ۲: بار CPU
Idle را ببین → کار سنگین → کدام process بالا است؟

## آزمایش ۳: نسخه Kernel/OS
```
uname -a
```
یا winver

| رخداد | معنی |
|--------|------|
| Syscall | ورود به Kernel |
| Context switch | عوض شدن نوبت |
| Page fault | صفحه در RAM نبود |
"""
    return summary, full, commands, lab

def _windows(topic, level):
    summary = f"«{topic}»: ویندوز ادمین = Services + Event Log + Registry (با احتیاط) + PowerShell."
    full = f"""# {topic}

**سطح:** {level} — {_depth(level)}

## Registry
HKLM = کل سیستم | HKCU = کاربر جاری
**قانون:** قبل از تغییر Export/بکاپ. روی Production بدون Change دست نزن.

## Services
برنامه پس‌زمینه با عمر طولانی. services.msc یا Get-Service

## Event Viewer
لاگ System/Application/Security برای RCA زمانی.

## فریم‌به‌فریم لاگین دامنه (مفهوم)
رمز → DC (Kerberos) → Profile/GPO → Desktop
ساعت کج → Kerberos می‌شکند.

## NTFS
Share + NTFS؛ سخت‌گیرانه‌تر برنده است. Inheritance را بفهم.

## امنیت
UAC را بی‌دلیل خاموش نکن؛ ادمین محلی فقط وقتی لازم است.
"""
    commands = f"""# — {topic}
```
winver
```
```
systeminfo
```
```
Get-Service | Where-Object Status -ne 'Running' | Select -First 20
```
```
Get-WinEvent -LogName System -MaxEvents 15
```
```
Get-Process | Sort CPU -Desc | Select -First 8
```
```
reg query HKLM\SOFTWARE\Microsoft\Windows\CurrentVersion /v ProgramFilesDir
```
"""
    lab = f"""# آزمایشگاه ویندوز — {topic}

1) winver + systeminfo — نسخه را یادداشت کن
2) services.msc — فقط مشاهده Startup Type
3) Event Viewer → System → خطاهای ۲۴ساعت — یک Event ID یادداشت کن
4) Task Manager → Sort by CPU/Memory

| ابزار | کاربرد |
|--------|--------|
| Task Manager | نمای سریع |
| Event Viewer | RCA |
| services.msc | سرویس‌ها |
| regedit | خطرناک |
"""
    return summary, full, commands, lab

def _linux(topic, level):
    topic_folded = (topic or "").casefold()
    if any(term in topic_folded for term in ("سلسله‌مراتب fs", "filesystem hierarchy", "hierarchy fs", "fhs", "سلسله مراتب فایل")):
        summary = f"«{topic}»: FHS نقشهٔ معنایی مسیرهای لینوکس است؛ مسیر فایل، فضای دیسک و mount واقعی سه مفهوم جدا هستند."
        full = f"""# {topic}

**سطح:** {level} — {_depth(level)}

## مدل ذهنی
Filesystem Hierarchy Standard (FHS) قرارداد مشترکِ محل قرارگیری فایل‌هاست؛ چیدمان دقیق می‌تواند میان توزیع‌ها تفاوت داشته باشد. ریشهٔ فضای نام / است. هر پارتیشن یا شبکه‌فایل‌سیستم پس از mount زیر یک مسیر ظاهر می‌شود. بنابراین نام /var به‌تنهایی نمی‌گوید داده روی کدام دیسک است؛ findmnt این رابطه را نشان می‌دهد.

## مسیرهای مهم
| مسیر | محتوای معمول | نکتهٔ عملیاتی |
|---|---|---|
| /etc | پیکربندی سراسری | قبل/بعد تغییر diff و backup داشته باش |
| /usr/bin و /usr/sbin | ابزارها و برنامه‌های توزیع | در بسیاری از توزیع‌ها /bin و /sbin به /usr لینک شده‌اند |
| /var/log | لاگ سرویس‌ها | rotation و فضای مصرفی را بررسی کن |
| /var/lib | state سرویس‌ها | حذف دستی ممکن است دیتابیس یا سرویس را خراب کند |
| /home | داده و تنظیمات کاربران | ممکن است filesystem جدا باشد |
| /root | خانهٔ root | با ریشهٔ / اشتباه نشود |
| /tmp | دادهٔ موقت | ماندگاری بعد reboot تضمین نیست |
| /run | PID و socketهای زمان اجرا | معمولاً tmpfs و پس از reboot بازسازی می‌شود |
| /proc | نمای مجازی process و kernel | مصرف آن را با اندازهٔ فایل روی دیسک یکی نگیر |
| /sys | نمای دستگاه و kernel | نوشتن روی بعضی attributeها تنظیم زنده را تغییر می‌دهد |
| /dev | device node | با فایل معمولی فرق دارد؛ روی آن rm یا echo آزمایشی اجرا نکن |
| /boot و /boot/efi | kernel، initramfs و EFI System Partition | تغییر اشتباه می‌تواند بوت را مختل کند |
| /mnt و /media | mountهای دستی و رسانهٔ جداشدنی | وضعیت واقعی را با findmnt بررسی کن |
| /opt و /srv | برنامه‌های افزوده و دادهٔ سرویس‌ها | به طراحی توزیع و سازمان وابسته‌اند |

## فرق مسیر، mount، فضا و مجوز
- مسیر: نامی در فضای نام فایل‌ها مانند /var/log.
- mount point: محل اتصال یک filesystem؛ با findmnt -T /var/log منبع واقعی را ببین.
- df -hT ظرفیت و نوع filesystem را نشان می‌دهد؛ du -xhd1 /var مصرف شاخه‌ها را در همان filesystem برآورد می‌کند.
- df -i وضعیت inode را نشان می‌دهد؛ تمام‌شدن inode می‌تواند ساخت فایل را متوقف کند حتی اگر فضا باقی باشد.
- namei -l /etc/ssh/sshd_config مجوز تک‌تک اجزای مسیر را نشان می‌دهد؛ ACL و mount options هم مهم‌اند.

## RCA: فضای دیسک تمام شده
1. با df -hT mountهای پر را پیدا کن.
2. df -i را هم بررسی کن؛ بین کمبود block و کمبود inode تفاوت بگذار.
3. اگر /var پر است، du -xhd1 /var را برای یافتن شاخهٔ بزرگ اجرا کن.
4. اگر df مصرف نشان می‌دهد ولی du همان اندازه را نمی‌یابد، فایل حذف‌شده‌ای که یک process باز نگه داشته یا reserved blocks را بررسی کن؛ lsof +L1 می‌تواند سرنخ بدهد.
5. قبل از پاک‌کردن لاگ یا داده، مالک سرویس، retention و الزامات ممیزی را تعیین کن. صرف بزرگ‌بودن /var/lib دلیل حذف آن نیست.

## امنیت و معیار قبولی
روی /proc، /sys، /dev، /boot و /var/lib آزمایش تغییردهنده اجرا نکن. درس زمانی تکمیل است که بتوانی منبع mount مسیر /var/log را با شاهد نشان بدهی، تفاوت df و du و inode را توضیح بدهی و برای filesystem پر یک اقدام ایمن و قابل بازگشت پیشنهاد کنی.
"""
        fence = chr(96) * 3
        commands = f"""# بررسی‌های فقط‌خواندنی
{fence}bash
findmnt -T /var/log
findmnt -o TARGET,SOURCE,FSTYPE,OPTIONS
df -hT
df -i
du -xhd1 /var 2>/dev/null | sort -h
namei -l /etc/ssh/sshd_config
stat /etc/hostname
{fence}
"""
        lab = """# آزمایشگاه فقط‌خواندنی — FHS

1. findmnt -T /var/log را اجرا و TARGET/SOURCE/FSTYPE را ثبت کن.
2. df -hT و df -i را مقایسه کن؛ محدودیت bytes است یا inode؟
3. du -xhd1 /var را اجرا کن؛ خروجی باید روی همان filesystem بماند و سطح اول را خلاصه کند.
4. namei -l /etc/ssh/sshd_config را بخوان و نخستین جزء مسیر با مجوز محدود را مشخص کن.
5. هیچ فایل سیستمی را حذف یا ویرایش نکن.

معیار قبولی: گزارش شامل منبع mount، درصد استفادهٔ block و inode، بزرگ‌ترین شاخهٔ قابل مشاهده و یک اقدام بررسی‌شده بدون حذف داده باشد.
"""
        return summary, full, commands, lab

    summary = f"«{topic}»: لینوکس = همه‌چیز فایل + process + permission + systemd."
    full = f"""# {topic}

**سطح:** {level} — {_depth(level)}

## FHS خلاصه
| مسیر | نقش |
|------|-----|
| / | ریشه |
| /etc | تنظیمات |
| /var | لاگ و داده متغیر |
| /home | کاربران |
| /proc | نمای Kernel |
| /boot | کرنل و بوت |

## مجوز rwx
User Group Other — chmod/chown با احتیاط روی Production

## systemd
systemctl status/start/stop | journalctl -u نام -n 50

## فریم‌به‌فریم اجرای دستور
Shell → PATH → fork+exec → ps → کد خروج $?

## خلاصه
اول مسیرها، بعد مجوز، بعد سرویس، بعد لاگ.
"""
    commands = f"""# — {topic}
```
uname -a
```
```
cat /etc/os-release
```
```
ls /
```
```
df -h
```
```
ps aux | head
```
```
systemctl list-units --failed
```
```
journalctl -p err -n 20 --no-pager
```
```
free -h && uptime
```
```
ip -br a
```
"""
    lab = f"""# آزمایشگاه لینوکس — {topic}

## ۱ گردش FHS
```
ls /etc | head; ls /var/log | head; ls /proc | head
```
/proc دیسک واقعی نیست.

## ۲ یک سرویس
```
systemctl status systemd-journald
```

## ۳ لاگ خطا
```
journalctl -p err -n 30 --no-pager
```

## ۴ مجوز
```
ls -l /etc/hostname
```
"""
    return summary, full, commands, lab

def _resource(topic, level):
    summary = f"«{topic}»: کندی همیشه CPU نیست؛ گلوگاه CPU / RAM / Disk / Network را جدا کن."
    full = f"""# {topic}

**سطح:** {level} — {_depth(level)}

## چهار گلوگاه
1) CPU 2) Memory/swap 3) Disk I/O 4) Network

## فریم‌به‌فریم «سیستم کند است»
1) همه جا یا یک اپ؟ 2) Load/Task Manager 3) CPU کدام process؟ 4) RAM/swap؟ 5) دیسک 100%؟ 6) DNS/شبکه؟

## نشانه‌ها
CPU 100% یک process = حلقه/تک‌نخی | Disk util بالا + CPU پایین = I/O | swap زیاد = کمبود RAM

## خلاصه
سوال: کدام منبع تمام شده؟
"""
    commands = f"""# — {topic}
## ویندوز
```
Get-Process | Sort CPU -Desc | Select -First 10
```
```
Get-Process | Sort WorkingSet64 -Desc | Select -First 10
```
## لینوکس
```
uptime
```
```
mpstat 1 5
```
```
free -h
```
```
vmstat 1 5
```
```
iostat -xz 1 5
```
```
ss -s
```
"""
    lab = f"""# آزمایشگاه منابع — {topic}

1) Baseline در حالت آرام
2) بار بده (فشرده‌سازی / کپی بزرگ / تب زیاد)
3) همزمان CPU و RAM و Disk را ببین
4) یک جمله RCA: «کندی از X بود چون Y دیدم»

| نشانه | گلوگاه |
|--------|--------|
| CPU 100% یک process | محاسبه |
| Disk 100% | I/O |
| RAM پر + swap | حافظه |
| DNS/ping کند | شبکه |
"""
    return summary, full, commands, lab

_BUILDERS = {"kernel": _kernel, "windows": _windows, "linux": _linux, "resource": _resource}

def build_chapter04_lesson(title_fa: str, title_en: str = "") -> Dict[str, Any] | None:
    topic, level = _topic(title_fa), _level(title_fa)
    b = _bucket(topic)
    summary, full, commands, lab = _BUILDERS[b](topic, level)
    return {
        "summary": summary, "full_content": full, "commands": commands,
        "examples": lab, "notes": f"فصل۰۴ · {b} · {level}", "lab": lab,
        "level": level, "topic": topic, "category": b, "chapter": 4,
    }
