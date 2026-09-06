from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Optional


MINUTES_PER_REPRESENTATIVE_DAY = 24 * 60
REPRESENTATIVE_DAYS_PER_MONTH = 4
MONTHS_PER_YEAR = 12


class ObservationKind(str, Enum):
    CUSTOMER_ARRIVAL = "customer_arrival"
    CHECKOUT_QUEUE_ENTER = "checkout_queue_enter"
    CHECKOUT_SERVICE_START = "checkout_service_start"
    CHECKOUT_ANGER = "checkout_anger"
    CHECKOUT_SERVICE_END = "checkout_service_end"
    CHECKOUT_STAFF_RETURN_TO_BREAK_ROOM = "checkout_staff_return_to_break_room"
    STAMINA_SNAPSHOT = "stamina_snapshot"
    REPLENISH_START = "replenish_start"
    REPLENISH_INTERRUPT = "replenish_interrupt"
    REPLENISH_END = "replenish_end"
    CLEAN_START = "clean_start"
    CLEAN_INTERRUPT = "clean_interrupt"
    CLEAN_END = "clean_end"
    GAME_CLOCK_SAMPLE = "game_clock_sample"
    WEATHER_CHANGE = "weather_change"
    SHARE_SNAPSHOT = "share_snapshot"


@dataclass(frozen=True, order=True)
class GameTimestamp:
    """Timestamp on the recovered 4-representative-day calendar."""

    year: int
    month: int
    day: int
    minute_of_day: int

    def __post_init__(self) -> None:
        if self.year < 1:
            raise ValueError("year must be >= 1")
        if not 1 <= self.month <= MONTHS_PER_YEAR:
            raise ValueError("month must be 1..12")
        if not 1 <= self.day <= REPRESENTATIVE_DAYS_PER_MONTH:
            raise ValueError("representative day must be 1..4")
        if not 0 <= self.minute_of_day < MINUTES_PER_REPRESENTATIVE_DAY:
            raise ValueError("minute_of_day must be 0..1439")

    @classmethod
    def from_hm(cls, year: int, month: int, day: int, hour: int, minute: int) -> "GameTimestamp":
        if not 0 <= hour <= 23:
            raise ValueError("hour must be 0..23")
        if not 0 <= minute <= 59:
            raise ValueError("minute must be 0..59")
        return cls(year, month, day, hour * 60 + minute)

    @property
    def representative_ordinal_minute(self) -> int:
        month_index = (self.year - 1) * MONTHS_PER_YEAR + (self.month - 1)
        day_index = month_index * REPRESENTATIVE_DAYS_PER_MONTH + (self.day - 1)
        return day_index * MINUTES_PER_REPRESENTATIVE_DAY + self.minute_of_day

    def minutes_until(self, later: "GameTimestamp") -> int:
        delta = later.representative_ordinal_minute - self.representative_ordinal_minute
        if delta < 0:
            raise ValueError("later timestamp precedes this timestamp")
        return delta


@dataclass(frozen=True)
class GameplayObservation:
    sequence: int
    kind: ObservationKind
    game_time: GameTimestamp
    video_seconds: Optional[float] = None
    customer_id: Optional[str] = None
    staff_id: Optional[str] = None
    fixture_id: Optional[str] = None
    numeric_value: Optional[float] = None
    note: str = ""


@dataclass(frozen=True)
class DurationMeasurement:
    start: GameplayObservation
    end: GameplayObservation
    game_minutes: int
    video_seconds: Optional[float]


@dataclass(frozen=True)
class StaminaDeltaMeasurement:
    start: GameplayObservation
    end: GameplayObservation
    stamina_delta: float
    game_minutes: int


class GameplayObservationTimeline:
    """Ordered observation log and reducers for video-derived measurements.

    Reducers only subtract explicitly annotated timestamps. Queue wait, service,
    total checkout and anger timing require matching identifiers; missing events
    never become inferred measurements.
    """

    def __init__(self, source_id: str) -> None:
        if not source_id:
            raise ValueError("source_id is required")
        self.source_id = source_id
        self._events: list[GameplayObservation] = []

    @property
    def events(self) -> tuple[GameplayObservation, ...]:
        return tuple(self._events)

    def add(
        self,
        kind: ObservationKind,
        game_time: GameTimestamp,
        *,
        video_seconds: Optional[float] = None,
        customer_id: Optional[str] = None,
        staff_id: Optional[str] = None,
        fixture_id: Optional[str] = None,
        numeric_value: Optional[float] = None,
        note: str = "",
    ) -> GameplayObservation:
        if video_seconds is not None and video_seconds < 0:
            raise ValueError("video_seconds must be >= 0")
        if self._events and game_time < self._events[-1].game_time:
            raise ValueError("game observations must be added in nondecreasing game-time order")
        event = GameplayObservation(
            sequence=len(self._events),
            kind=kind,
            game_time=game_time,
            video_seconds=video_seconds,
            customer_id=customer_id,
            staff_id=staff_id,
            fixture_id=fixture_id,
            numeric_value=numeric_value,
            note=note,
        )
        self._events.append(event)
        return event

    def customer_arrival_intervals(self) -> tuple[DurationMeasurement, ...]:
        arrivals = [e for e in self._events if e.kind is ObservationKind.CUSTOMER_ARRIVAL]
        return tuple(self._duration_between(a, b) for a, b in zip(arrivals, arrivals[1:]))

    def checkout_queue_wait_durations(self) -> tuple[DurationMeasurement, ...]:
        pending: dict[tuple[str, Optional[str]], GameplayObservation] = {}
        results: list[DurationMeasurement] = []
        for event in self._events:
            if event.customer_id is None:
                continue
            key = (event.customer_id, event.fixture_id)
            if event.kind is ObservationKind.CHECKOUT_QUEUE_ENTER:
                if key in pending:
                    raise ValueError(f"duplicate checkout queue enter without service start for {key}")
                pending[key] = event
            elif event.kind is ObservationKind.CHECKOUT_SERVICE_START:
                start = pending.pop(key, None)
                if start is not None:
                    results.append(self._duration_between(start, event))
        return tuple(results)

    def checkout_service_durations(self) -> tuple[DurationMeasurement, ...]:
        pending: dict[tuple[Optional[str], Optional[str], Optional[str]], GameplayObservation] = {}
        results: list[DurationMeasurement] = []
        for event in self._events:
            key = (event.customer_id, event.staff_id, event.fixture_id)
            if event.kind is ObservationKind.CHECKOUT_SERVICE_START:
                if key in pending:
                    raise ValueError(f"duplicate checkout start without end for {key}")
                pending[key] = event
            elif event.kind is ObservationKind.CHECKOUT_SERVICE_END:
                start = pending.pop(key, None)
                if start is None:
                    raise ValueError(f"checkout end without matching start for {key}")
                results.append(self._duration_between(start, event))
        return tuple(results)

    def checkout_total_durations(self) -> tuple[DurationMeasurement, ...]:
        pending: dict[tuple[str, Optional[str]], GameplayObservation] = {}
        results: list[DurationMeasurement] = []
        for event in self._events:
            if event.customer_id is None:
                continue
            key = (event.customer_id, event.fixture_id)
            if event.kind is ObservationKind.CHECKOUT_QUEUE_ENTER:
                if key in pending:
                    raise ValueError(f"duplicate checkout queue enter without service end for {key}")
                pending[key] = event
            elif event.kind is ObservationKind.CHECKOUT_SERVICE_END:
                start = pending.pop(key, None)
                if start is not None:
                    results.append(self._duration_between(start, event))
        return tuple(results)

    def checkout_queue_to_first_anger_durations(self) -> tuple[DurationMeasurement, ...]:
        """Measure queue-entry to the first explicitly annotated anger event."""
        pending: dict[tuple[str, Optional[str]], GameplayObservation] = {}
        results: list[DurationMeasurement] = []
        for event in self._events:
            if event.customer_id is None:
                continue
            key = (event.customer_id, event.fixture_id)
            if event.kind is ObservationKind.CHECKOUT_QUEUE_ENTER:
                if key in pending:
                    raise ValueError(f"duplicate checkout queue enter before anger for {key}")
                pending[key] = event
            elif event.kind is ObservationKind.CHECKOUT_ANGER:
                start = pending.pop(key, None)
                if start is not None:
                    results.append(self._duration_between(start, event))
        return tuple(results)

    def checkout_service_to_first_anger_durations(self) -> tuple[DurationMeasurement, ...]:
        """Measure service-start to first anger when the serving staff is identified."""
        pending: dict[tuple[str, str, Optional[str]], GameplayObservation] = {}
        results: list[DurationMeasurement] = []
        for event in self._events:
            if event.customer_id is None or event.staff_id is None:
                continue
            key = (event.customer_id, event.staff_id, event.fixture_id)
            if event.kind is ObservationKind.CHECKOUT_SERVICE_START:
                if key in pending:
                    raise ValueError(f"duplicate checkout service start before anger for {key}")
                pending[key] = event
            elif event.kind is ObservationKind.CHECKOUT_ANGER:
                start = pending.pop(key, None)
                if start is not None:
                    results.append(self._duration_between(start, event))
        return tuple(results)

    def stamina_deltas(self, staff_id: Optional[str] = None) -> tuple[StaminaDeltaMeasurement, ...]:
        snapshots = [
            e
            for e in self._events
            if e.kind is ObservationKind.STAMINA_SNAPSHOT
            and e.numeric_value is not None
            and (staff_id is None or e.staff_id == staff_id)
        ]
        by_staff: dict[Optional[str], list[GameplayObservation]] = {}
        for event in snapshots:
            by_staff.setdefault(event.staff_id, []).append(event)

        results: list[StaminaDeltaMeasurement] = []
        for events in by_staff.values():
            for start, end in zip(events, events[1:]):
                results.append(
                    StaminaDeltaMeasurement(
                        start=start,
                        end=end,
                        stamina_delta=end.numeric_value - start.numeric_value,
                        game_minutes=start.game_time.minutes_until(end.game_time),
                    )
                )
        results.sort(key=lambda m: m.start.sequence)
        return tuple(results)

    def count_arrivals(self, start: GameTimestamp, end: GameTimestamp) -> int:
        if end < start:
            raise ValueError("end must be >= start")
        return sum(
            1
            for event in self._events
            if event.kind is ObservationKind.CUSTOMER_ARRIVAL and start <= event.game_time < end
        )

    @staticmethod
    def _duration_between(start: GameplayObservation, end: GameplayObservation) -> DurationMeasurement:
        video_delta: Optional[float]
        if start.video_seconds is None or end.video_seconds is None:
            video_delta = None
        else:
            video_delta = end.video_seconds - start.video_seconds
            if video_delta < 0:
                raise ValueError("video timestamps must not go backwards within a paired measurement")
        return DurationMeasurement(
            start=start,
            end=end,
            game_minutes=start.game_time.minutes_until(end.game_time),
            video_seconds=video_delta,
        )
