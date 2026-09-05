from __future__ import annotations

from dataclasses import dataclass

from .clock import MonthBoundary, RepresentativeDayType, SimulationClock
from .economy import DayEndResult


@dataclass(frozen=True)
class RepresentativeDayRecord:
    year: int
    month: int
    day: int
    day_type: RepresentativeDayType
    day_end: DayEndResult


@dataclass(frozen=True)
class RepresentativeMonthSample:
    """Observed/simulated representative-day records for one month boundary.

    The first-title evidence supports day 1..4 simulation followed by a skip to
    the next month, but the exact monthly aggregation formula is still
    unresolved. This object therefore preserves the four day-end samples and
    boundary without multiplying, averaging or fabricating day 5+ values.
    """

    year: int
    month: int
    records: tuple[RepresentativeDayRecord, ...]
    boundary: MonthBoundary

    @property
    def representative_days(self) -> tuple[int, ...]:
        return tuple(record.day for record in self.records)

    @property
    def complete_four_day_sample(self) -> bool:
        return self.representative_days == (1, 2, 3, 4)

    @property
    def weekday_records(self) -> tuple[RepresentativeDayRecord, ...]:
        return tuple(
            record
            for record in self.records
            if record.day_type is RepresentativeDayType.WEEKDAY
        )

    @property
    def holiday_records(self) -> tuple[RepresentativeDayRecord, ...]:
        return tuple(
            record
            for record in self.records
            if record.day_type is RepresentativeDayType.HOLIDAY
        )


class RepresentativeMonthRecorder:
    """Advance the recovered 4-day month while retaining raw day-end samples.

    `close_representative_day` is deliberately the only calendar-advancing
    operation here. It records the caller-supplied `DayEndResult`, advances the
    `SimulationClock`, and returns a month sample only when day 4 crosses the
    month boundary. No month-end extrapolation or skipped-day finance is
    generated.
    """

    def __init__(self, clock: SimulationClock | None = None) -> None:
        self.clock = clock if clock is not None else SimulationClock()
        self._records: list[RepresentativeDayRecord] = []

    @property
    def current_records(self) -> tuple[RepresentativeDayRecord, ...]:
        return tuple(self._records)

    def close_representative_day(
        self,
        day_end: DayEndResult,
    ) -> RepresentativeMonthSample | None:
        record = RepresentativeDayRecord(
            year=self.clock.year,
            month=self.clock.month,
            day=self.clock.day,
            day_type=self.clock.representative_day_type,
            day_end=day_end,
        )
        self._records.append(record)
        boundary = self.clock.advance_day()
        if boundary is None:
            return None

        records = tuple(self._records)
        self._records.clear()
        return RepresentativeMonthSample(
            year=boundary.previous_year,
            month=boundary.previous_month,
            records=records,
            boundary=boundary,
        )
