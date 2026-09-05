from __future__ import annotations

from dataclasses import dataclass


MINUTES_PER_DAY = 24 * 60


@dataclass(frozen=True)
class ClockAdvanceResult:
    previous_minute_of_day: int
    current_minute_of_day: int
    days_crossed: int


class SubdayClock:
    """Explicit in-game time-of-day clock with no wall-clock speed assumption.

    The uploaded first-title videos visibly expose a 24-hour clock, but the
    mapping between one real video second and in-game minutes can vary with
    speed/pause/menu state. This reference layer therefore advances only when
    callers explicitly supply an in-game minute delta.
    """

    def __init__(self, hour: int = 0, minute: int = 0) -> None:
        if not 0 <= hour <= 23:
            raise ValueError("hour must be 0..23")
        if not 0 <= minute <= 59:
            raise ValueError("minute must be 0..59")
        self._absolute_minutes = hour * 60 + minute

    @property
    def absolute_minutes(self) -> int:
        return self._absolute_minutes

    @property
    def minute_of_day(self) -> int:
        return self._absolute_minutes % MINUTES_PER_DAY

    @property
    def hour(self) -> int:
        return self.minute_of_day // 60

    @property
    def minute(self) -> int:
        return self.minute_of_day % 60

    @property
    def elapsed_days(self) -> int:
        return self._absolute_minutes // MINUTES_PER_DAY

    def advance_minutes(self, minutes: int) -> ClockAdvanceResult:
        if minutes < 0:
            raise ValueError("minutes must be >= 0")
        previous = self.minute_of_day
        previous_day = self.elapsed_days
        self._absolute_minutes += minutes
        return ClockAdvanceResult(
            previous_minute_of_day=previous,
            current_minute_of_day=self.minute_of_day,
            days_crossed=self.elapsed_days - previous_day,
        )


@dataclass(frozen=True)
class OperatingHours:
    """Daily opening interval independent from any salary or demand formula.

    `open_minute` and `close_minute` are minutes since 00:00. When
    `always_open` is true the interval fields are ignored. When false, equal
    open/close minutes represent an empty interval rather than silently being
    interpreted as 24-hour operation.
    """

    open_minute: int = 0
    close_minute: int = 0
    always_open: bool = False

    def __post_init__(self) -> None:
        for value, name in (
            (self.open_minute, "open_minute"),
            (self.close_minute, "close_minute"),
        ):
            if not 0 <= value < MINUTES_PER_DAY:
                raise ValueError(f"{name} must be 0..1439")

    @classmethod
    def from_hm(
        cls,
        open_hour: int,
        open_minute: int,
        close_hour: int,
        close_minute: int,
    ) -> "OperatingHours":
        for hour, name in ((open_hour, "open_hour"), (close_hour, "close_hour")):
            if not 0 <= hour <= 23:
                raise ValueError(f"{name} must be 0..23")
        for minute, name in (
            (open_minute, "open_minute"),
            (close_minute, "close_minute"),
        ):
            if not 0 <= minute <= 59:
                raise ValueError(f"{name} must be 0..59")
        return cls(
            open_minute=open_hour * 60 + open_minute,
            close_minute=close_hour * 60 + close_minute,
        )

    @classmethod
    def twenty_four_hours(cls) -> "OperatingHours":
        return cls(always_open=True)

    def is_open_at(self, minute_of_day: int) -> bool:
        if not 0 <= minute_of_day < MINUTES_PER_DAY:
            raise ValueError("minute_of_day must be 0..1439")
        if self.always_open:
            return True
        if self.open_minute == self.close_minute:
            return False
        if self.open_minute < self.close_minute:
            return self.open_minute <= minute_of_day < self.close_minute
        # Overnight opening, e.g. 20:00 -> 04:00.
        return minute_of_day >= self.open_minute or minute_of_day < self.close_minute

    def is_open_clock(self, clock: SubdayClock) -> bool:
        return self.is_open_at(clock.minute_of_day)
