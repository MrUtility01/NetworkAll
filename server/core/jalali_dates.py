# -*- coding: utf-8 -*-
"""Pure Persian/Jalali calendar conversion helpers (no web dependencies)."""
from datetime import datetime

_DIGIT_TO_ASCII = str.maketrans("۰۱۲۳۴۵۶۷۸۹٠١٢٣٤٥٦٧٨٩", "01234567890123456789")
_ASCII_TO_PERSIAN = str.maketrans("0123456789", "۰۱۲۳۴۵۶۷۸۹")

def _normalize_date_digits(value):
    return str(value or "").translate(_DIGIT_TO_ASCII).strip()

def _jalali_to_gregorian(year, month, day):
    jy = year + 1595
    days = -355668 + 365 * jy + (jy // 33) * 8 + ((jy % 33 + 3) // 4) + day
    days += (month - 1) * 31 if month < 7 else (month - 7) * 30 + 186
    gy = 400 * (days // 146097)
    days %= 146097
    if days > 36524:
        gy += 100 * ((days - 1) // 36524)
        days = (days - 1) % 36524
        if days >= 365:
            days += 1
    gy += 4 * (days // 1461)
    days %= 1461
    if days > 365:
        gy += (days - 1) // 365
        days = (days - 1) % 365
    gd = days + 1
    leap = gy % 4 == 0 and (gy % 100 != 0 or gy % 400 == 0)
    month_lengths = [31, 29 if leap else 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
    gm = 1
    while gm <= 12 and gd > month_lengths[gm - 1]:
        gd -= month_lengths[gm - 1]
        gm += 1
    return datetime(gy, gm, gd).date()

def _jalali_days_in_month(year, month):
    if month < 1 or month > 12:
        return 0
    if month <= 6:
        return 31
    if month <= 11:
        return 30
    return 30 if (_jalali_to_gregorian(year + 1, 1, 1) - _jalali_to_gregorian(year, 1, 1)).days == 366 else 29

def _gregorian_to_jalali(date_value):
    offsets = (0, 31, 59, 90, 120, 151, 181, 212, 243, 273, 304, 334)
    gy, gm, gd = date_value.year, date_value.month, date_value.day
    if gy > 1600:
        jy, gy = 979, gy - 1600
    else:
        jy, gy = 0, gy - 621
    gy2 = gy + 1 if gm > 2 else gy
    days = 365 * gy + (gy2 + 3) // 4 - (gy2 + 99) // 100 + (gy2 + 399) // 400 - 80 + gd + offsets[gm - 1]
    jy += 33 * (days // 12053)
    days %= 12053
    jy += 4 * (days // 1461)
    days %= 1461
    if days > 365:
        jy += (days - 1) // 365
        days = (days - 1) % 365
    if days < 186:
        jm, jd = 1 + days // 31, 1 + days % 31
    else:
        jm, jd = 7 + (days - 186) // 30, 1 + (days - 186) % 30
    return jy, jm, jd

def jalali_date(value):
    if not value:
        return ""
    try:
        day = datetime.strptime(str(value)[:10], "%Y-%m-%d").date()
        y, m, d = _gregorian_to_jalali(day)
        return f"{y:04d}/{m:02d}/{d:02d}".translate(_ASCII_TO_PERSIAN)
    except Exception:
        return str(value)

def jalali_datetime(value):
    if not value:
        return ""
    try:
        dt = datetime.fromisoformat(str(value).replace("Z", "+00:00"))
        if dt.tzinfo is not None:
            dt = dt.astimezone()
        return (jalali_date(dt.date().isoformat()) + " " + dt.strftime("%H:%M")).strip()
    except Exception:
        return str(value)

def parse_jalali_due_date(value):
    normalized = _normalize_date_digits(value).replace("-", "/")
    if not normalized:
        return ""
    parts = normalized.split("/")
    if len(parts) != 3:
        raise ValueError("تاریخ را به‌شکل ۱۴۰۵/۰۷/۲۲ وارد کنید.")
    try:
        year, month, day = map(int, parts)
        if year >= 1700:  # accept old Gregorian values from existing installs
            parsed = datetime(year, month, day).date()
        else:
            if not 1 <= month <= 12 or not 1 <= day <= _jalali_days_in_month(year, month):
                raise ValueError
            parsed = _jalali_to_gregorian(year, month, day)
        return parsed.isoformat()
    except Exception:
        raise ValueError("تاریخ شمسی معتبر نیست؛ نمونهٔ درست: ۱۴۰۵/۰۷/۲۲.")
