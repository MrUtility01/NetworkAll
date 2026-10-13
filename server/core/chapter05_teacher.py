# -*- coding: utf-8 -*-
"""فصل ۰۵ — فایل‌سیستم و Storage: FAT/NTFS · ext4 · MBR/GPT · RAID"""
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
    if any(k in t for k in ("raid", "mirror", "stripe", "parity", "rebuild", "hot spare")):
        return "raid"
    if any(k in t for k in ("mbr", "gpt", "پارتیشن", "partition", "volume", "esp")):
        return "partition"
    if any(k in t for k in ("ext4", "ext3", "xfs", "btrfs", "inode", "fsck", "mount", "fstab", "journal")):
        return "linux_fs"
    if any(k in t for k in ("fat", "exfat", "ntfs", "refs", "bitlocker", "allocation")):
        return "windows_fs"
    if "linux" in t or "لینوکس" in t:
        return "linux_fs"
    if "windows" in t or "ویندوز" in t:
        return "windows_fs"
    return "partition"

def _depth(level: str) -> str:
    return {"L0": "تصویر ذهنی", "L1": "مثال+Lab", "L2": "دستور ادمین", "L3": "طراحی", "L4": "سازمانی"}.get(level, "")

def _windows_fs(topic, level):
    summary = f"«{topic}»: FAT32/exFAT برای جابه‌جایی؛ NTFS برای سیستم و سهم‌ها."
    full = f"""# {topic}

**سطح:** {level} — {_depth(level)}

## تشبیه
دیسک = کتابخانه | فایل‌سیستم = قفسه‌بندی

## FAT32 · exFAT · NTFS
| | FAT32 | exFAT | NTFS |
|--|-------|-------|------|
| فایل خیلی بزرگ | محدودیت ~4GB | مناسب | عالی |
| مجوز | ضعیف | ضعیف | ACL قوی |
| کاربرد | USB قدیمی | فلش/تبادل | سیستم و Share |

C: → NTFS | فلش چندسیستمی → exFAT

## فریم‌به‌فریم Write روی NTFS
WriteFile → Cache → متادیتای NTFS → کلاستر دیسک → ژورنال

## خلاصه
انتخاب FS = سازگاری + اندازه + امنیت + پایداری
"""
    commands = """```
Get-Volume | Format-Table DriveLetter, FileSystem, SizeRemaining, Size
```
```
fsutil fsinfo volumeinfo C:
```
```
chkdsk C: /scan
```
```
icacls C:\\Windows
```
"""
    lab = """# Lab ویندوز FS
Get-Volume را ببین. برای ویدیو ۸گیگ FAT32 مناسب است؟ چرا؟
"""
    return summary, full, commands, lab

def _linux_fs(topic, level):
    topic_folded = (topic or "").casefold()
    if "btrfs" in topic_folded and "snapshot" in topic_folded:
        summary = f"«{topic}»: snapshot در Btrfs مبتنی بر subvolume و copy-on-write است؛ snapshot پشتیبان مستقل از خرابی همان فایل‌سیستم نیست."
        fence = chr(96) * 3
        full = f"""# {topic}

**سطح:** {level} — {_depth(level)}

## مدل ذهنی: subvolume و snapshot
Btrfs فایل‌سیستم را به درختی از metadata و extents سازمان می‌دهد. Subvolume یک درخت مستقل درون همان Btrfs filesystem است؛ snapshot یک subvolume جدید است که در ابتدا extentهای مشترک دارد و هنگام تغییر، به‌واسطهٔ copy-on-write به‌تدریج از مبدأ فاصله می‌گیرد.

| مفهوم | معنی عملیاتی | پیامد |
|---|---|---|
| Subvolume | مرز منطقی برای یک درخت فایل | می‌تواند مبنای snapshot و mount جدا باشد |
| Read-write snapshot | snapshot قابل تغییر | تغییراتش دیگر صرفاً مشاهده‌ای نیست |
| Read-only snapshot | تصویر ثابت برای مقایسه/بازیابی | از تغییر اتفاقی snapshot جلوگیری می‌کند |
| Copy-on-write | اشتراک بلوک‌ها تا زمان تغییر | مصرف فضا ممکن است با تغییرات و نگهداری snapshotها رشد کند |

## نحو و محدودیت‌ها
{fence}text
btrfs subvolume snapshot [-r] SOURCE DESTINATION
{fence}
SOURCE باید subvolume باشد و DESTINATION نباید از قبل وجود داشته باشد. مبدأ و مقصد باید روی همان Btrfs filesystem باشند. نام و مسیرهای رایج مانند @ و @snapshots قرارداد توزیع لینوکس‌اند و نام استاندارد تضمین‌شده نیستند.

## روش عیب‌یابی مبتنی بر شواهد
1. نوع فایل‌سیستم و منبع mount را با findmnt تأیید کن.
2. فهرست subvolumeها و رابطهٔ parent/top-level را ثبت کن.
3. قبل از ساخت snapshot، فضای آزاد و سیاست نگهداری را بررسی کن.
4. پس از snapshot، مقصد، نوع read-only و محتوای نمونه را verify کن.
5. برای rollback، mount layout، bootloader و سرویس‌هایی را که به subvolume وابسته‌اند جداگانه بررسی کن؛ ساخت snapshot به‌تنهایی rollback بوت‌پذیر ایجاد نمی‌کند.

## امنیت، نگهداری و محدودیت بازیابی
- snapshot روی همان فایل‌سیستم قرار دارد؛ خرابی دیسک، حذف فایل‌سیستم یا خطای مدیریتی می‌تواند مبدأ و snapshot را هم‌زمان از بین ببرد. snapshot جایگزین backup روی رسانه/سیستم جدا نیست.
- snapshotهای قدیمی ممکن است extentهای حذف‌شده را زنده نگه دارند و فضا مصرف کنند. ظرفیت را با btrfs filesystem usage بررسی کن.
- قبل از حذف snapshot، شناسه/مسیر دقیق، وابستگی‌های boot و سیاست retention را تأیید کن. از glob یا حذف گروهیِ بدون فهرست استفاده نکن.

## معیار قبولی
فهرست subvolumeها قابل توضیح است؛ snapshot در مسیر مقصد دیده می‌شود؛ -r روی snapshot اعمال شده؛ محتوای snapshot با مبدأ هنگام ساخت برابر است؛ و گزارش آزمایش شامل منبع mount، فضای آزاد، مسیر snapshot و محدودیت‌های rollback است.
"""
        commands = f"""# بررسی فقط‌خواندنی
{fence}text
findmnt -no SOURCE,FSTYPE,OPTIONS /
sudo btrfs filesystem usage /
sudo btrfs subvolume list -t /
sudo btrfs subvolume show /PATH/TO/SUBVOLUME
{fence}

# فقط در فایل‌سیستم آزمایشگاهیِ جدا و تأییدشده
{fence}text
sudo btrfs subvolume create /mnt/btrfs-lab/source
sudo btrfs subvolume snapshot -r /mnt/btrfs-lab/source /mnt/btrfs-lab/snap-source
sudo btrfs subvolume show /mnt/btrfs-lab/snap-source
{fence}
"""
        lab = """# آزمایشگاه ایزوله — Btrfs Snapshot

## شرط شروع
در VM یا دیسک آزمایشگاهی کار کن. ابتدا findmnt -no SOURCE,FSTYPE,OPTIONS /mnt/btrfs-lab را اجرا کن؛ اگر مسیر روی Btrfs نیست یا filesystem مشترک با دادهٔ واقعی است، متوقف شو. مسیرهای این Lab را بدون بررسی روی / جایگزین نکن.

## اجرا و شاهد
1. خروجی btrfs filesystem usage /mnt/btrfs-lab را baseline بگیر.
2. btrfs subvolume create /mnt/btrfs-lab/source را فقط پس از تأیید مسیر Lab اجرا کن.
3. یک فایل آزمایشی بساز و وجودش را ثبت کن.
4. btrfs subvolume snapshot -r /mnt/btrfs-lab/source /mnt/btrfs-lab/snap-source را اجرا کن.
5. btrfs subvolume list -t /mnt/btrfs-lab و btrfs subvolume show /mnt/btrfs-lab/snap-source را ثبت کن.
6. محتوای نمونه را بین مبدأ و snapshot مقایسه کن و read-only بودن snapshot را در خروجی verify کن.

## پاک‌سازی
فقط بعد از بررسی دقیق مسیر و اطمینان از آزمایشگاهی بودن داده‌ها، snapshot آزمایشی را حذف کن. این کار را روی snapshotهای عملیاتی یا مسیری که هویت آن معلوم نیست اجرا نکن.
"""
        return summary, full, commands, lab

    summary = f"«{topic}»: پارتیشن با mount زیر مسیر می‌آید؛ ext4 رایج است."
    full = f"""# {topic}

**سطح:** {level} — {_depth(level)}

## mount
/dev/sda1 --mount--> /

## ext4
ژورنال + inode (متادیتای فایل). XFS برای داده بزرگ سرور رایج است.

## فریم‌به‌فریم نوشتن
write → page cache → flush دیسک → ژورنال/متادیتا

## fstab و fsck
fstab اشتباه = emergency mode. fsck روی FS mount‌شده معمولاً نه.
"""
    commands = """```
lsblk -f
```
```
df -hT
```
```
findmnt
```
```
sudo blkid
```
```
cat /etc/fstab
```
```
stat /etc/hostname
```
"""
    lab = """# Lab لینوکس FS
lsblk -f و df -hT | stat یک فایل | cat fstab فقط خواندن
"""
    return summary, full, commands, lab

def _partition(topic, level):
    summary = f"«{topic}»: MBR قدیمی؛ GPT مدرن با UEFI و ESP."
    full = f"""# {topic}

**سطح:** {level} — {_depth(level)}

## MBR در برابر GPT
| | MBR | GPT |
|--|-----|-----|
| بوت | BIOS Legacy | UEFI |
| دیسک بزرگ | محدودیت | مناسب |
| بازیابی جدول | ضعیف | هدر پشتیبان |

ترکیب رایج: UEFI + GPT + ESP + root/NTFS

## فریم‌به‌فریم بوت GPT
UEFI جدول را می‌خواند → ESP → Bootloader → OS

## احتیاط
diskpart/fdisk می‌توانند همه را پاک کنند. دو بار lsblk بخوان.
"""
    commands = """```
Get-Disk | Format-Table Number, FriendlyName, PartitionStyle, Size
```
```
Get-Partition
```
```
lsblk -o NAME,SIZE,TYPE,FSTYPE,MOUNTPOINT
```
```
sudo fdisk -l
```
```
sudo blkid
```
"""
    lab = """# Lab پارتیشن
PartitionStyle را ببین (GPT/MBR). ESP را پیدا کن. دیسک ۲TB ویندوز جدید: GPT چرا؟
"""
    return summary, full, commands, lab

def _raid(topic, level):
    summary = f"«{topic}»: RAID سرعت یا افزونگی می‌دهد — پشتیبان‌گیری نیست."
    full = f"""# {topic}

**سطح:** {level} — {_depth(level)}

## قانون
RAID ≠ Backup

## سطوح
| سطح | ایده | حداقل دیسک |
|------|------|------------|
| 0 | Stripe سرعت | 2 |
| 1 | Mirror | 2 |
| 5 | Stripe+parity | 3 |
| 6 | دو parity | 4 |
| 10 | Mirror+Stripe | 4 |

## فریم RAID1
write روی هر دو دیسک؛ fail یکی → ادامه از روی دیگر؛ دیسک جدید → rebuild

## مانیتورینگ
Optimal / Degraded / Rebuild + SMART + آلارم
"""
    commands = """```
cat /proc/mdstat
```
```
sudo mdadm --detail /dev/md0 2>/dev/null
```
```
Get-PhysicalDisk | Format-Table FriendlyName, HealthStatus, Size
```
```
Get-StoragePool
```
"""
    lab = """# Lab RAID
سناریو کاغذی: دو دیسک فقط سرعت؟ دو دیسک سیستم مهم؟ چهار دیسک DB؟
وضعیت mdstat یا PhysicalDisk را ببین.
"""
    return summary, full, commands, lab

_BUILDERS = {"windows_fs": _windows_fs, "linux_fs": _linux_fs, "partition": _partition, "raid": _raid}

def build_chapter05_lesson(title_fa: str, title_en: str = "") -> Dict[str, Any] | None:
    topic, level = _topic(title_fa), _level(title_fa)
    b = _bucket(topic)
    summary, full, commands, lab = _BUILDERS[b](topic, level)
    return {
        "summary": summary, "full_content": full, "commands": commands,
        "examples": lab, "notes": f"فصل۰۵ · {b} · {level} · RAID≠Backup", "lab": lab,
        "level": level, "topic": topic, "category": b, "chapter": 5,
    }
