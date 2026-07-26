"""
utils.py — Timezone and Jalali conversion helpers.

All functions are pure (no Flask imports, no side effects).
The input/output pipelines are strictly defined in the project spec.

Delta 2.6: Added to_persian_digits(), to_latin_digits(), and extended
utc_naive_to_display_str() to support Gregorian display when date_format='gregorian'.
The storage pipeline (jalali_str_to_utc_naive) is UNCHANGED.
"""

# =====================================================================
# FILE: utils.py
# PURPOSE: Shared utility functions for internationalized date/time formatting, task-status logic, time-range filter boundaries, and data export helpers.
# =====================================================================

from datetime import datetime, timezone, timedelta
from typing import Optional, Tuple

import jdatetime
import pytz

# Tehran timezone object (IANA)
TEHRAN_TZ = pytz.timezone("Asia/Tehran")
UTC_TZ = pytz.UTC

# Persian digit map
_FA_DIGITS = str.maketrans("0123456789", "۰۱۲۳۴۵۶۷۸۹")
_EN_DIGITS = str.maketrans("۰۱۲۳۴۵۶۷۸۹", "0123456789")

# ---------------------------------------------------------------------
# ⬛ DIGIT LOCALE HELPERS: Persian and Latin digit conversion
# ---------------------------------------------------------------------

def to_persian_digits(text: str) -> str:
    """Convert all ASCII digits in text to Persian (Eastern Arabic) digits."""
    return str(text).translate(_FA_DIGITS)


def to_latin_digits(text: str) -> str:
    """Convert all Persian digits in text to ASCII (Latin) digits."""
    return str(text).translate(_EN_DIGITS)


def localize_digits(text: str, language: str = "fa") -> str:
    """
    Apply digit localization based on the user's language preference.

    Args:
        text: String potentially containing digits.
        language: 'fa' → Persian digits, 'en' → Latin digits.

    Returns:
        String with digits converted appropriately.
    """
    if language == "fa":
        return to_persian_digits(text)
    return to_latin_digits(text)


# ---------------------------------------------------------------------
# ⬛ INPUT PIPELINE: Jalali date string to naive UTC datetime for DB storage
# UNCHANGED — do not alter this function's signature or contract.
# ---------------------------------------------------------------------

# --- ▷ Jalali-to-UTC Converter ---
def jalali_str_to_utc_naive(jalali_str: str) -> datetime:
    """
    Convert a Jalali date/datetime string to a naive UTC datetime for DB storage.

    Accepts:
        - "1403-01-15"           → uses 23:59:59 Tehran wall-clock time (end of day)
        - "1403-01-15 14:30"     → uses the provided time as Tehran wall-clock time
        - "1403-01-15 14:30:00"  → same as above

    Pipeline:
        1. Parse Jalali string → jdatetime
        2. jdatetime.togregorian() → naive datetime (Tehran wall-clock)
        3. tehran.localize(dt)    → aware Tehran datetime
        4. .astimezone(UTC)       → aware UTC datetime
        5. .replace(tzinfo=None)  → naive UTC for DB storage

    Raises:
        ValueError: if the string cannot be parsed.
    """
    jalali_str = jalali_str.strip()
    # Normalize Persian digits to Latin before parsing
    jalali_str = to_latin_digits(jalali_str)

    # Try to parse with time component first, then date-only
    jdt = None
    for fmt in ("%Y-%m-%d %H:%M:%S", "%Y-%m-%d %H:%M", "%Y-%m-%d"):
        try:
            jdt = jdatetime.datetime.strptime(jalali_str, fmt)
            if fmt == "%Y-%m-%d":
                # End-of-day rule: 23:59:59 Tehran wall-clock
                jdt = jdt.replace(hour=23, minute=59, second=59)
            break
        except (ValueError, AttributeError):
            continue

    if jdt is None:
        raise ValueError(f"تاریخ شمسی نامعتبر است: '{jalali_str}'")

    # Convert to Gregorian naive datetime (wall-clock in Tehran)
    # strip tzinfo in case jdatetime.strptime produced an aware result
    greg_naive: datetime = jdt.togregorian().replace(tzinfo=None)

    # Localize as Tehran time
    tehran_aware: datetime = TEHRAN_TZ.localize(greg_naive)

    # Convert to UTC
    utc_aware: datetime = tehran_aware.astimezone(UTC_TZ)

    # Strip timezone info for DB storage
    return utc_aware.replace(tzinfo=None)


# ---------------------------------------------------------------------
# ⬛ OUTPUT PIPELINE: Naive UTC datetime to localized display string
# Delta 2.6: added date_format and language parameters for Gregorian/Jalali
# and Persian/Latin digit switching. Default behaviour is unchanged.
# ---------------------------------------------------------------------

# --- ▷ UTC-to-Display Formatter ---
def utc_naive_to_jalali_str(
    dt_utc_naive: Optional[datetime],
    fmt: Optional[str] = None,
    date_format: str = "jalali",
    language: str = "fa",
    date_style: str = "text",
) -> str:
    """
    تبدیل تاریخ دیتابیس به رشته نمایشی با پشتیبانی از استایل متنی/عددی.
    """
    if dt_utc_naive is None:
        return ""

    utc_aware: datetime = UTC_TZ.localize(dt_utc_naive)
    tehran_aware: datetime = utc_aware.astimezone(TEHRAN_TZ)

    # اگر فرمت خاصی (مثل کارت ویرایش '%Y-%m-%d') درخواست شده، همان را اعمال کن
    if fmt:
        if date_format == "gregorian":
            result = tehran_aware.strftime(fmt)
        else:
            jalali_dt = jdatetime.datetime.fromgregorian(datetime=tehran_aware)
            result = jalali_dt.strftime(fmt)
        return localize_digits(result, language)

    # در غیر این صورت، فرمت هوشمند را بر اساس تنظیمات کاربر بساز
    time_str = f"{tehran_aware.hour:02d}:{tehran_aware.minute:02d}"

    if date_style == "numeric":
        if date_format == "gregorian":
            result = f"{tehran_aware.year}/{tehran_aware.month:02d}/{tehran_aware.day:02d} - {time_str}"
        else:
            j = jdatetime.datetime.fromgregorian(datetime=tehran_aware)
            result = f"{j.year}/{j.month:02d}/{j.day:02d} - {time_str}"
    else:
        JALALI_MONTHS_FA = ['فروردین','اردیبهشت','خرداد','تیر','مرداد','شهریور','مهر','آبان','آذر','دی','بهمن','اسفند']
        JALALI_MONTHS_EN = ['Farvardin', 'Ordibehesht', 'Khordad', 'Tir', 'Mordad', 'Shahrivar','Mehr', 'Aban', 'Azar', 'Dey', 'Bahman', 'Esfand']
        GREG_MONTHS_EN   = ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec']
        GREG_MONTHS_FA   = ['ژانویه','فوریه','مارس','آوریل','مه','ژوئن','ژوئیه','اوت','سپتامبر','اکتبر','نوامبر','دسامبر']

        if date_format == "gregorian":
            y, m, d = tehran_aware.year, tehran_aware.month, tehran_aware.day
            m_str = GREG_MONTHS_FA[m-1] if language == "fa" else GREG_MONTHS_EN[m-1]
            result = f"{d} {m_str} {y} - {time_str}"
        else:
            j = jdatetime.datetime.fromgregorian(datetime=tehran_aware)
            y, m, d = j.year, j.month, j.day
            m_str = JALALI_MONTHS_FA[m-1] if language == "fa" else JALALI_MONTHS_EN[m-1]
            result = f"{d} {m_str} {y} - {time_str}"

    return localize_digits(result, language)


# ---------------------------------------------------------------------
# ⬛ FILTER HELPERS: Time-range boundaries as naive UTC for DB queries
# ---------------------------------------------------------------------

# --- ▷ Tehran Time Helper ---
def _tehran_now() -> datetime:
    """Return the current aware datetime in Tehran timezone."""
    return datetime.now(TEHRAN_TZ)


# --- ▷ Naive UTC Converter ---
def _tehran_to_utc_naive(tehran_aware: datetime) -> datetime:
    """Convert an aware Tehran datetime to naive UTC."""
    return tehran_aware.astimezone(UTC_TZ).replace(tzinfo=None)


# --- ▷ Daily Range Boundary ---
def get_daily_range_utc() -> Tuple[datetime, datetime]:
    """
    Return (start_utc_naive, end_utc_naive) covering today in Tehran time.
    Start: 00:00:00 Tehran today
    End:   23:59:59 Tehran today
    """
    now_tehran = _tehran_now()
    start_tehran = now_tehran.replace(hour=0, minute=0, second=0, microsecond=0)
    end_tehran = now_tehran.replace(hour=23, minute=59, second=59, microsecond=999999)
    return _tehran_to_utc_naive(start_tehran), _tehran_to_utc_naive(end_tehran)


# --- ▷ Weekly Range Boundary ---
def get_weekly_range_utc() -> Tuple[datetime, datetime]:
    """
    Return (start_utc_naive, end_utc_naive) covering the current Jalali week.
    Jalali weeks start on Saturday (weekday index 0 in jdatetime).
    Start: Saturday 00:00:00 Tehran
    End:   Friday   23:59:59 Tehran
    """
    now_tehran = _tehran_now()
    jalali_now = jdatetime.datetime.fromgregorian(datetime=now_tehran)

    # jdatetime weekday(): Saturday=0, Sunday=1, ..., Friday=6
    current_weekday = jalali_now.weekday()

    # Start of week: go back 'current_weekday' days to Saturday
    start_jalali = jalali_now - jdatetime.timedelta(days=current_weekday)
    start_jalali = start_jalali.replace(hour=0, minute=0, second=0, microsecond=0)

    # End of week: Saturday + 6 days = Friday
    end_jalali = start_jalali + jdatetime.timedelta(days=6)
    end_jalali = end_jalali.replace(hour=23, minute=59, second=59, microsecond=999999)

    # Convert back to Gregorian aware Tehran, then to naive UTC
    # .replace(tzinfo=None) is required because jdatetime propagates tzinfo
    # through arithmetic when initialized from an aware datetime.
    start_greg_naive = start_jalali.togregorian().replace(tzinfo=None)
    end_greg_naive = end_jalali.togregorian().replace(tzinfo=None)

    start_tehran = TEHRAN_TZ.localize(start_greg_naive)
    end_tehran = TEHRAN_TZ.localize(end_greg_naive)

    return _tehran_to_utc_naive(start_tehran), _tehran_to_utc_naive(end_tehran)


# --- ▷ Monthly Range Boundary ---
def get_monthly_range_utc() -> Tuple[datetime, datetime]:
    """
    Return (start_utc_naive, end_utc_naive) covering the current Jalali month.
    Start: 1st of current Jalali month, 00:00:00 Tehran
    End:   Last day of current Jalali month, 23:59:59 Tehran
    """
    now_tehran = _tehran_now()
    jalali_now = jdatetime.datetime.fromgregorian(datetime=now_tehran)

    year = jalali_now.year
    month = jalali_now.month

    # Months 1-6: 31 days, months 7-11: 30 days, month 12: 29 (or 30 in leap)
    if month <= 6:
        days_in_month = 31
    elif month <= 11:
        days_in_month = 30
    else:
        days_in_month = 30 if jdatetime.date(year, 1, 1).isleap() else 29

    start_jalali = jdatetime.datetime(year, month, 1, 0, 0, 0)
    end_jalali = jdatetime.datetime(year, month, days_in_month, 23, 59, 59)

    start_greg = start_jalali.togregorian().replace(tzinfo=None)
    end_greg = end_jalali.togregorian().replace(tzinfo=None)

    start_tehran = TEHRAN_TZ.localize(start_greg)
    end_tehran = TEHRAN_TZ.localize(end_greg)

    return _tehran_to_utc_naive(start_tehran), _tehran_to_utc_naive(end_tehran)


# --- ▷ Yearly Range Boundary ---
def get_yearly_range_utc() -> Tuple[datetime, datetime]:
    """
    Return (start_utc_naive, end_utc_naive) covering the current Jalali year.
    Start: 1 Farvardin 00:00:00 Tehran
    End:   29 or 30 Esfand 23:59:59 Tehran
    """
    now_tehran = _tehran_now()
    jalali_now = jdatetime.datetime.fromgregorian(datetime=now_tehran)
    year = jalali_now.year

    start_jalali = jdatetime.datetime(year, 1, 1, 0, 0, 0)
    # Esfand is month 12; last day is 29 or 30
    esfand_days = 30 if jdatetime.date(year, 1, 1).isleap() else 29
    end_jalali = jdatetime.datetime(year, 12, esfand_days, 23, 59, 59)

    start_greg = start_jalali.togregorian().replace(tzinfo=None)
    end_greg = end_jalali.togregorian().replace(tzinfo=None)

    start_tehran = TEHRAN_TZ.localize(start_greg)
    end_tehran = TEHRAN_TZ.localize(end_greg)

    return _tehran_to_utc_naive(start_tehran), _tehran_to_utc_naive(end_tehran)


# --- ▷ Custom Range Boundary ---
def get_custom_range_utc(start_str: str, end_str: str) -> Tuple[datetime, datetime]:
    """
    Return (start_utc_naive, end_utc_naive) for a custom Jalali date range.

    start_jalali_str uses 00:00:00 if no time provided.
    end_jalali_str uses 23:59:59 if no time provided.

    Raises ValueError if parsing fails or start > end.
    """
    start_str = to_latin_digits(start_jalali_str.strip())
    end_str = to_latin_digits(end_jalali_str.strip())

    # For start, override end-of-day default to beginning of day
    start_jdt = None
    for fmt in ("%Y-%m-%d %H:%M:%S", "%Y-%m-%d %H:%M", "%Y-%m-%d"):
        try:
            start_jdt = jdatetime.datetime.strptime(start_str, fmt)
            if fmt == "%Y-%m-%d":
                start_jdt = start_jdt.replace(hour=0, minute=0, second=0)
            break
        except (ValueError, AttributeError):
            continue

    if start_jdt is None:
        raise ValueError("val_date_start_invalid")

    # End date uses end-of-day rule (23:59:59) via jalali_str_to_utc_naive
    end_utc = jalali_str_to_utc_naive(end_str)

    start_greg = start_jdt.togregorian().replace(tzinfo=None)
    start_tehran = TEHRAN_TZ.localize(start_greg)
    start_utc = _tehran_to_utc_naive(start_tehran)

    if start_utc > end_utc:
        raise ValueError("val_date_start_after_end")

    return start_utc, end_utc


# --- ▷ Task Status Logic ---
def get_task_status_python(is_done: bool, expires_at: Optional[datetime]) -> str:
    """
    Compute task status in Python after reading from DB.

    Args:
        is_done: The task's is_done flag.
        expires_at: Naive UTC datetime from DB, or None.

    Returns:
        'done' | 'expired' | 'pending'
    """
    if is_done:
        return "done"
    if expires_at is None:
        return "pending"
    now_utc_naive = datetime.now(timezone.utc).replace(tzinfo=None)
    if expires_at < now_utc_naive:
        return "expired"
    return "pending"


# ---------------------------------------------------------------------
# ⬛ STATUS AND PRIORITY CONSTANTS: Label mappings and default priority levels
# ---------------------------------------------------------------------

# Mapping status strings to Persian labels
STATUS_LABELS = {
    "pending": "در انتظار",
    "done": "انجام شد",
    "expired": "منقضی شد",
}

# Default priority levels (Persian)
DEFAULT_PRIORITIES = ["کم", "متوسط", "زیاد"]
