from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class RepresentativeDayType(str, Enum):
    WEEKDAY = "weekday"
    HOLIDAY = "holiday"


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
        # SS direct-play evidence says 3 weekdays + 1 holiday. Keep this in the
        # reference harness so it can be replaced if the guidebook contradicts it.
        return RepresentativeDayType.HOLIDAY if self.day == 4 else RepresentativeDayType.WEEKDAY

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
