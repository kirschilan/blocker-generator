"""Sprint / week / day calendar.

Per ARCHITECTURE.md "Notes for Code Implementation": Sprint 1 = weeks 1-2
(Jul 1-14, 2026); each subsequent sprint adds 2 weeks; Sprint 12 = weeks
23-24 (Oct 19-Nov 1, 2026).
"""
from __future__ import annotations

from datetime import date, timedelta

QUARTER_START = date(2026, 7, 1)
DAYS_PER_WEEK = 7
WEEKS_PER_SPRINT = 2
SPRINT_COUNT = 12


def week_day_to_date(week: int, day: int, start: date = QUARTER_START) -> date:
    """week is 1-indexed (week 1 = the first 7 days); day is 1-indexed within that week."""
    return start + timedelta(days=(week - 1) * DAYS_PER_WEEK + (day - 1))


def sprint_start_date(sprint: int, start: date = QUARTER_START) -> date:
    return start + timedelta(days=(sprint - 1) * WEEKS_PER_SPRINT * DAYS_PER_WEEK)


def sprint_for_date(d: date, start: date = QUARTER_START) -> int:
    day_offset = (d - start).days
    return day_offset // (WEEKS_PER_SPRINT * DAYS_PER_WEEK) + 1


def week_for_date(d: date, start: date = QUARTER_START) -> int:
    day_offset = (d - start).days
    return day_offset // DAYS_PER_WEEK + 1
