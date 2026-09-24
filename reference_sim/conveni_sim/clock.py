from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from .baseline_data import ANNUAL_CALENDAR


class RepresentativeDayType(str, Enum):
    WEEKDAY = "weekday"
    HOLIDAY = "holiday"


_DAY_TYPE_BY_MONTH_DAY: dict[tuple[int, int], RepresentativeDayType] = {
    (entry.month, day_index + 1): RepresentativeDayType(day_type)
    for entry in ANNUAL_CALENDAR
    for day_index, day_type in enumerate(entry.day_types.value)
}


@dataclass(frozen=True)
class MonthBoundary:
    previous_year: int
    previous_month: int
    next_year: int
    next_month: int


class SimulationClock:
    """Reference clock for the first-title four-representative-day month.

    This intentionally does *not* implement the unresolved month-end sales/cost
    aggregation formula. It only models the observed calendar boundary.
    """

    def __init__(self, year: int = 1, month: int = 1, day: int = 1) -> None:
        if not 1 <= month <= 12:
            raise ValueError("month must be 1..12")
        if not 1 <= day <= 4:
            raise ValueError("simulated day must be 1..4")
        self.year = year
        self.month = month
        self.day = day

    @property
    def representative_day_type(self) -> RepresentativeDayType:
        # Previously a "day==4 is the only holiday" simplification, kept only
        # because SS direct-play evidence showed 3 weekdays + 1 holiday and the
        # code invited replacement "if the guidebook contradicts it" -- it now
        # does: baseline_data.ANNUAL_CALENDAR (CONFIRMED_OFFICIAL, quick
        # reference book page 3) gives the exact weekday/holiday flag per
        # (month, day) -- January/May/August/December each carry one extra
        # 休日, so the fourth representative day is not always the sole
        # holiday (see decision 0132).
        return _DAY_TYPE_BY_MONTH_DAY[(self.month, self.day)]

    def advance_day(self) -> MonthBoundary | None:
        if self.day < 4:
            self.day += 1
            return None

        previous_year = self.year
        previous_month = self.month
        self.day = 1
        if self.month == 12:
            self.month = 1
            self.year += 1
        else:
            self.month += 1
        return MonthBoundary(previous_year, previous_month, self.year, self.month)
