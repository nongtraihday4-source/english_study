"""
Business hours utilities for SLA deadline calculation.

Working hours: Monday–Saturday, 08:00–17:00 Vietnam time.
Sundays and Vietnamese public holidays are non-working days.

Public holidays are fetched from the date.nager.at API and cached in Redis/locmem
for 30 days. A hardcoded fallback (2025-2027) is used if the API is unreachable.

Additional overrides can be added via settings.PUBLIC_HOLIDAYS_EXTRA:
    PUBLIC_HOLIDAYS_EXTRA = ["2026-05-04", "2026-05-05"]
"""
from __future__ import annotations

import json
import zoneinfo
from datetime import date, datetime, timedelta
from urllib import request as urllib_request
from urllib.error import URLError

from django.utils import timezone

VN_TZ = zoneinfo.ZoneInfo("Asia/Ho_Chi_Minh")

WORK_START = 8   # 08:00 inclusive
WORK_END = 17    # 17:00 exclusive — 9 working hours/day

# SLA hours per priority level (business hours, not calendar hours)
_SLA_HOURS: dict[str, int] = {
    "urgent": 4,    # ~4 biz-hours ≈ same business day
    "high":   8,    # ~8 biz-hours ≈ 1 full business day
    "medium": 24,   # 24 biz-hours ≈ 2–3 business days
    "low":    72,   # 72 biz-hours ≈ 1–2 business weeks
}

# Hardcoded fallback for 2025–2027
# (Tết âm lịch exact dates confirmed for each year + fixed national holidays)
_FALLBACK_HOLIDAYS: list[str] = [
    # ── 2025 ────────────────────────────────────────────────────────────────
    "2025-01-01",                                                            # Tết Dương lịch
    "2025-01-27", "2025-01-28", "2025-01-29", "2025-01-30",                # Tết Nguyên Đán (Ất Tỵ)
    "2025-01-31", "2025-02-02", "2025-02-03",                              # Tết + bù
    "2025-04-07",                                                            # Giỗ Tổ Hùng Vương (10/3 âm)
    "2025-04-30", "2025-05-01",                                             # 30/4 + QTLĐ 1/5
    "2025-09-02",                                                            # Quốc khánh 2/9

    # ── 2026 ────────────────────────────────────────────────────────────────
    "2026-01-01",                                                            # Tết Dương lịch
    "2026-01-27",                                                            # Giỗ Tổ Hùng Vương (bù)
    "2026-01-29", "2026-01-30", "2026-01-31",                              # Tết Nguyên Đán (Bính Ngọ)
    "2026-02-01", "2026-02-02", "2026-02-03", "2026-02-04",               # Tết (tiếp theo)
    "2026-04-27",                                                            # Giỗ Tổ Hùng Vương (10/3 âm)
    "2026-04-30", "2026-05-01",                                             # 30/4 + QTLĐ 1/5
    "2026-09-02", "2026-09-03",                                             # Quốc khánh + ngày bù

    # ── 2027 ────────────────────────────────────────────────────────────────
    "2027-01-01",                                                            # Tết Dương lịch
    "2027-02-15", "2027-02-16", "2027-02-17", "2027-02-18",               # Tết Nguyên Đán (Đinh Mùi)
    "2027-02-19", "2027-02-20",                                             # Tết (tiếp theo)
    "2027-04-16",                                                            # Giỗ Tổ Hùng Vương (10/3 âm)
    "2027-04-30", "2027-05-01",                                             # 30/4 + QTLĐ 1/5
    "2027-09-02",                                                            # Quốc khánh 2/9
]


# ─── Holiday data source ──────────────────────────────────────────────────────

def _fetch_holidays_api(year: int) -> list[str]:
    """Fetch Vietnamese public holidays from date.nager.at for *year*.

    Returns a list of "YYYY-MM-DD" strings.
    Raises URLError / ValueError on network or parse failure.
    """
    url = f"https://date.nager.at/api/v3/PublicHolidays/{year}/VN"
    req = urllib_request.Request(url, headers={"User-Agent": "EnglishStudy-SLA/1.0"})
    with urllib_request.urlopen(req, timeout=4) as resp:
        payload = json.loads(resp.read().decode("utf-8"))
    return [item["date"] for item in payload if isinstance(item, dict) and "date" in item]


def _get_holidays(year: int) -> frozenset[str]:
    """Return set of 'YYYY-MM-DD' holiday strings for *year*.

    Cache strategy: Django cache (Redis in prod, locmem in dev) with 30-day TTL.
    Fallback: hardcoded _FALLBACK_HOLIDAYS if API is unreachable.
    """
    cache_key = f"es:holidays:VN:{year}"

    # Try cache first
    try:
        from django.core.cache import cache as dj_cache
        cached = dj_cache.get(cache_key)
        if cached is not None:
            return frozenset(cached)
    except Exception:
        dj_cache = None  # type: ignore[assignment]
    else:
        dj_cache = dj_cache  # type: ignore[assignment]

    # Fetch from API
    try:
        days = _fetch_holidays_api(year)

        # Merge settings-level extras
        try:
            from django.conf import settings as cfg
            for d in getattr(cfg, "PUBLIC_HOLIDAYS_EXTRA", []):
                d = d.strip()
                if d:
                    days.append(d)
        except Exception:
            pass

        # Persist to cache
        try:
            from django.core.cache import cache as dj_cache2
            dj_cache2.set(cache_key, days, timeout=86400 * 30)
        except Exception:
            pass

        return frozenset(days)

    except (URLError, OSError, ValueError, Exception):
        # Fall back to hardcoded list for this year
        fallback: set[str] = {d for d in _FALLBACK_HOLIDAYS if d.startswith(str(year))}

        try:
            from django.conf import settings as cfg
            for d in getattr(cfg, "PUBLIC_HOLIDAYS_EXTRA", []):
                d = d.strip()
                if d and d.startswith(str(year)):
                    fallback.add(d)
        except Exception:
            pass

        return frozenset(fallback)


# ─── Core business-hours logic ────────────────────────────────────────────────

def is_working_day(d: date) -> bool:
    """Return True iff *d* is a regular business day (Mon–Sat, not a public holiday)."""
    if d.weekday() == 6:        # Sunday = 6
        return False
    return d.strftime("%Y-%m-%d") not in _get_holidays(d.year)


def _next_biz_day_start(dt: datetime) -> datetime:
    """Return 08:00 VN time of the next working day after *dt*."""
    candidate = (dt + timedelta(days=1)).replace(
        hour=WORK_START, minute=0, second=0, microsecond=0
    )
    while not is_working_day(candidate.date()):
        candidate = (candidate + timedelta(days=1)).replace(
            hour=WORK_START, minute=0, second=0, microsecond=0
        )
    return candidate


def add_business_hours(start_dt: datetime, hours: float) -> datetime:
    """Return the datetime *hours* working-hours after *start_dt*.

    Computation done in VN_TZ so weekday/hour boundaries are correct.
    Working hours: Mon–Sat 08:00–17:00. Sundays and holidays are skipped.
    """
    dt = start_dt.astimezone(VN_TZ)
    remaining = float(hours)

    while remaining > 0:
        # Skip non-working days
        if not is_working_day(dt.date()):
            dt = _next_biz_day_start(dt)
            continue

        day_start = dt.replace(hour=WORK_START, minute=0, second=0, microsecond=0)
        day_end   = dt.replace(hour=WORK_END,   minute=0, second=0, microsecond=0)

        # Past end-of-day → advance to next working day
        if dt >= day_end:
            dt = _next_biz_day_start(dt)
            continue

        # Before start-of-day → clamp to 08:00
        if dt < day_start:
            dt = day_start

        available = (day_end - dt).total_seconds() / 3600.0

        if available >= remaining:
            dt = dt + timedelta(hours=remaining)
            remaining = 0.0
        else:
            remaining -= available
            dt = _next_biz_day_start(dt)

    return dt


def business_sla_deadline(priority: str) -> datetime:
    """Return the SLA deadline for a ticket created now, measured in business hours.

    Priority → business-hours:
        urgent → 4 h  (~same business day)
        high   → 8 h  (~1 full business day)
        medium → 24 h (~2-3 business days)
        low    → 72 h (~1-2 business weeks)
    """
    hours = _SLA_HOURS.get(priority, 24)
    return add_business_hours(timezone.now(), hours)
