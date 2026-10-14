#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Regression tests for Persian/Jalali date parsing and formatting."""
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "server"))
from core.jalali_dates import (
    parse_jalali_due_date, jalali_date,
    _jalali_to_gregorian, _gregorian_to_jalali,
)

def main():
    assert parse_jalali_due_date("۱۴۰۵/۰۷/۲۲") == "2026-10-14"
    assert parse_jalali_due_date("1405-07-22") == "2026-10-14"
    assert jalali_date("2026-10-14") == "۱۴۰۵/۰۷/۲۲"
    assert parse_jalali_due_date("2026/10/14") == "2026-10-14"
    for j in ((1399, 1, 1), (1400, 1, 1), (1403, 1, 1), (1405, 7, 22)):
        assert _gregorian_to_jalali(_jalali_to_gregorian(*j)) == j
    try:
        parse_jalali_due_date("۱۴۰۵/۱۳/۴۰")
    except ValueError:
        pass
    else:
        raise AssertionError("Invalid Jalali date was accepted")
    print("Jalali date validation OK")

if __name__ == "__main__":
    main()
