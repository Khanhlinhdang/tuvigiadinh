"""
Vietnamese Lunar/Solar calendar conversion.

Implementation based on the algorithm published by Hồ Ngọc Đức
(https://www.informatik.uni-leipzig.de/~duc/amlich/), which is the
de-facto reference used by official Vietnamese lunar-calendar libraries.
The algorithm uses the meridian for Vietnam (timezone UTC+7) so the
result matches the printed Vietnamese lunar calendars.

Public helpers:
- solar_to_lunar(year, month, day) -> dict
- lunar_to_solar(year, month, day, is_leap_month=False) -> dict
- get_lunar_year_from_solar_date(year, month, day) -> int

All functions are pure-Python and have no external dependencies.
"""
from __future__ import annotations

import math
from typing import Tuple

TIMEZONE_VN = 7.0  # GMT+7 (Vietnam)

# ----- Julian day helpers ---------------------------------------------------

def _jd_from_date(dd: int, mm: int, yy: int) -> int:
    """Convert a Gregorian date to a Julian Day Number (integer)."""
    a = (14 - mm) // 12
    y = yy + 4800 - a
    m = mm + 12 * a - 3
    jd = dd + (153 * m + 2) // 5 + 365 * y + y // 4 - y // 100 + y // 400 - 32045
    if jd < 2299161:
        # Julian calendar before 1582-10-15
        jd = dd + (153 * m + 2) // 5 + 365 * y + y // 4 - 32083
    return jd


def _jd_to_date(jd: int) -> Tuple[int, int, int]:
    """Convert Julian Day Number back to Gregorian (day, month, year)."""
    if jd > 2299160:
        a = jd + 32044
        b = (4 * a + 3) // 146097
        c = a - (146097 * b) // 4
    else:
        b = 0
        c = jd + 32082
    d = (4 * c + 3) // 1461
    e = c - (1461 * d) // 4
    m = (5 * e + 2) // 153
    day = e - (153 * m + 2) // 5 + 1
    month = m + 3 - 12 * (m // 10)
    year = b * 100 + d - 4800 + m // 10
    return day, month, year


# ----- Astronomical functions ----------------------------------------------

def _new_moon(k: int) -> float:
    """Compute the time of the k-th new moon after the new moon of
    1900-01-01 (JDE)."""
    T = k / 1236.85
    T2 = T * T
    T3 = T2 * T
    dr = math.pi / 180.0
    Jd1 = (
        2415020.75933 + 29.53058868 * k + 0.0001178 * T2 - 0.000000155 * T3
    )
    Jd1 += 0.00033 * math.sin(
        (166.56 + 132.87 * T - 0.009173 * T2) * dr
    )
    M = 359.2242 + 29.10535608 * k - 0.0000333 * T2 - 0.00000347 * T3
    Mpr = 306.0253 + 385.81691806 * k + 0.0107306 * T2 + 0.00001236 * T3
    F = 21.2964 + 390.67050646 * k - 0.0016528 * T2 - 0.00000239 * T3
    C1 = (
        (0.1734 - 0.000393 * T) * math.sin(M * dr)
        + 0.0021 * math.sin(2 * dr * M)
    )
    C1 -= 0.4068 * math.sin(Mpr * dr) + 0.0161 * math.sin(dr * 2 * Mpr)
    C1 -= 0.0004 * math.sin(dr * 3 * Mpr)
    C1 += 0.0104 * math.sin(dr * 2 * F) - 0.0051 * math.sin(dr * (M + Mpr))
    C1 -= 0.0074 * math.sin(dr * (M - Mpr)) + 0.0004 * math.sin(
        dr * (2 * F + M)
    )
    C1 -= 0.0004 * math.sin(dr * (2 * F - M)) - 0.0006 * math.sin(
        dr * (2 * F + Mpr)
    )
    C1 += 0.0010 * math.sin(dr * (2 * F - Mpr)) + 0.0005 * math.sin(
        dr * (2 * Mpr + M)
    )
    if T < -11:
        deltat = (
            0.001
            + 0.000839 * T
            + 0.0002261 * T2
            - 0.00000845 * T3
            - 0.000000081 * T * T3
        )
    else:
        deltat = -0.000278 + 0.000265 * T + 0.000262 * T2
    JdNew = Jd1 + C1 - deltat
    return JdNew


def _sun_longitude(jdn: float) -> float:
    """Sun's geocentric longitude in radians (0..2π) at the given JD."""
    T = (jdn - 2451545.0) / 36525.0
    T2 = T * T
    dr = math.pi / 180.0
    M = 357.52910 + 35999.05030 * T - 0.0001559 * T2 - 0.00000048 * T * T2
    L0 = 280.46645 + 36000.76983 * T + 0.0003032 * T2
    DL = (1.914600 - 0.004817 * T - 0.000014 * T2) * math.sin(dr * M)
    DL += (0.019993 - 0.000101 * T) * math.sin(dr * 2 * M) + 0.000290 * math.sin(
        dr * 3 * M
    )
    L = L0 + DL
    L = L * dr
    L = L - math.pi * 2 * (int(L / (math.pi * 2)))
    return L


def _get_sun_longitude(day_number: int, timezone: float) -> int:
    """Return the sun longitude code (0..11) at the start of the given JD
    in the requested timezone. Each unit corresponds to 30°."""
    return int(_sun_longitude(day_number - 0.5 - timezone / 24) / math.pi * 6)


def _get_new_moon_day(k: int, timezone: float) -> int:
    """Return the Julian day number of the k-th new moon in local time."""
    return int(_new_moon(k) + 0.5 + timezone / 24)


def _get_lunar_month_11(yy: int, timezone: float) -> int:
    """JD of the new moon starting lunar month 11 of solar year yy
    (the month that contains the winter solstice)."""
    off = _jd_from_date(31, 12, yy) - 2415021
    k = int(off / 29.530588853)
    nm = _get_new_moon_day(k, timezone)
    sun_long = _get_sun_longitude(nm, timezone)
    if sun_long >= 9:
        nm = _get_new_moon_day(k - 1, timezone)
    return nm


def _get_leap_month_offset(a11: int, timezone: float) -> int:
    """Return the offset (in lunar months) of the leap month from month 11
    of the preceding year."""
    k = int((a11 - 2415021.076998695) / 29.530588853 + 0.5)
    last = 0
    i = 1
    arc = _get_sun_longitude(_get_new_moon_day(k + i, timezone), timezone)
    while True:
        last = arc
        i += 1
        arc = _get_sun_longitude(_get_new_moon_day(k + i, timezone), timezone)
        if arc == last or i >= 14:
            break
    return i - 1


# ----- Public conversion API ------------------------------------------------

def solar_to_lunar(year: int, month: int, day: int, timezone: float = TIMEZONE_VN) -> dict:
    """Convert a solar date (Gregorian) to Vietnamese lunar date.

    Returns dict with keys: lunar_year, lunar_month, lunar_day, is_leap_month.
    """
    day_number = _jd_from_date(day, month, year)
    k = int((day_number - 2415021.076998695) / 29.530588853)
    month_start = _get_new_moon_day(k + 1, timezone)
    if month_start > day_number:
        month_start = _get_new_moon_day(k, timezone)
    a11 = _get_lunar_month_11(year, timezone)
    b11 = a11
    if a11 >= month_start:
        lunar_year = year
        a11 = _get_lunar_month_11(year - 1, timezone)
    else:
        lunar_year = year + 1
        b11 = _get_lunar_month_11(year + 1, timezone)
    lunar_day = day_number - month_start + 1
    diff = int((month_start - a11) / 29)
    leap_month = False
    lunar_month = diff + 11
    if b11 - a11 > 365:
        leap_month_diff = _get_leap_month_offset(a11, timezone)
        if diff >= leap_month_diff:
            lunar_month = diff + 10
            if diff == leap_month_diff:
                leap_month = True
    if lunar_month > 12:
        lunar_month = lunar_month - 12
    if lunar_month >= 11 and diff < 4:
        lunar_year -= 1
    return {
        "lunar_year": lunar_year,
        "lunar_month": lunar_month,
        "lunar_day": lunar_day,
        "is_leap_month": leap_month,
    }


def lunar_to_solar(
    year: int,
    month: int,
    day: int,
    is_leap_month: bool = False,
    timezone: float = TIMEZONE_VN,
) -> dict:
    """Convert a Vietnamese lunar date to solar date.

    Returns dict with keys: solar_year, solar_month, solar_day.
    """
    if month < 11:
        a11 = _get_lunar_month_11(year - 1, timezone)
        b11 = _get_lunar_month_11(year, timezone)
    else:
        a11 = _get_lunar_month_11(year, timezone)
        b11 = _get_lunar_month_11(year + 1, timezone)
    k = int(0.5 + (a11 - 2415021.076998695) / 29.530588853)
    off = month - 11
    if off < 0:
        off += 12
    if b11 - a11 > 365:
        leap_off = _get_leap_month_offset(a11, timezone)
        leap_month = leap_off - 2
        if leap_month < 0:
            leap_month += 12
        if is_leap_month and month != leap_month:
            # Treat as non-leap if mismatch.
            pass
        elif is_leap_month or off >= leap_off:
            off += 1
    month_start = _get_new_moon_day(k + off, timezone)
    sd, sm, sy = _jd_to_date(month_start + day - 1)
    return {"solar_year": sy, "solar_month": sm, "solar_day": sd}


def get_lunar_year_from_solar_date(year: int, month: int, day: int) -> int:
    """Return the lunar year corresponding to a solar date.

    This is the year used to determine Can Chi (Heavenly Stem / Earthly
    Branch) since the sexagenary cycle is based on the lunar year.
    """
    return solar_to_lunar(year, month, day)["lunar_year"]
