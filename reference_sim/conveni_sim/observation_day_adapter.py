from __future__ import annotations

from dataclasses import dataclass

from .observations import GameplayObservationTimeline, ObservationKind
from .representative_day_metrics import (
    ObservedRepresentativeDayMetrics,
    ObservedStaffMinimum,
)


MINUTES_PER_DAY = 24 * 60


@dataclass(frozen=True)
class ObservationDayCoverage:
    year: int
    month: int
    day: int
    start_minute_inclusive: int = 0
    end_minute_exclusive: int = MINUTES_PER_DAY

    def __post_init__(self) -> None:
        if self.year < 1:
            raise ValueError("year must be >= 1")
        if not 1 <= self.month <= 12:
            raise ValueError("month must be within 1..12")
        if not 1 <= self.day <= 4:
            raise ValueError("representative day must be within 1..4")
        if not 0 <= self.start_minute_inclusive < MINUTES_PER_DAY:
            raise ValueError("coverage start must be within 0..1439")
        if not 1 <= self.end_minute_exclusive <= MINUTES_PER_DAY:
            raise ValueError("coverage end must be within 1..1440")
        if self.end_minute_exclusive <= self.start_minute_inclusive:
            raise ValueError("coverage end must be greater than coverage start")

    @property
    def covers_full_day(self) -> bool:
        return (
            self.start_minute_inclusive == 0
            and self.end_minute_exclusive == MINUTES_PER_DAY
        )


@dataclass(frozen=True)
class ObservationDayMetricMapping:
    """Explicit semantic assertions required before event counts become targets.

    A raw CUSTOMER_ARRIVAL sighting is not automatically an engine admission,
    and a CHECKOUT_SERVICE_END sighting is not automatically proven sale
    settlement. Researchers opt into those mappings only when their annotation
    convention/source supports them.
    """

    customer_arrival_means_admitted: bool = False
    checkout_service_end_means_completed_sale: bool = False


@dataclass(frozen=True)
class ObservationWindowStaffMinimum:
    staff_id: str
    minimum_stamina: int


@dataclass(frozen=True)
class ObservationDayMetricReduction:
    source_id: str
    coverage: ObservationDayCoverage
    mapping: ObservationDayMetricMapping
    window_arrival_count: int
    window_checkout_service_end_count: int
    window_staff_minimums: tuple[ObservationWindowStaffMinimum, ...]
    comparison_targets: ObservedRepresentativeDayMetrics


class ObservationDayMetricAdapter:
    """Bridge annotated gameplay observations to sparse full-day comparison targets.

    Partial windows are still summarized, but they never become full-day scalar
    targets or stamina minima. This prevents a 10-minute video segment from being
    compared against a complete autonomous representative day as if coverage were
    exhaustive.
    """

    def reduce(
        self,
        timeline: GameplayObservationTimeline,
        coverage: ObservationDayCoverage,
        *,
        mapping: ObservationDayMetricMapping = ObservationDayMetricMapping(),
    ) -> ObservationDayMetricReduction:
        events = tuple(
            event
            for event in timeline.events
            if (
                event.game_time.year == coverage.year
                and event.game_time.month == coverage.month
                and event.game_time.day == coverage.day
                and coverage.start_minute_inclusive
                <= event.game_time.minute_of_day
                < coverage.end_minute_exclusive
            )
        )

        arrival_count = sum(
            1 for event in events if event.kind is ObservationKind.CUSTOMER_ARRIVAL
        )
        checkout_end_count = sum(
            1
            for event in events
            if event.kind is ObservationKind.CHECKOUT_SERVICE_END
        )

        stamina_by_staff: dict[str, list[int]] = {}
        for event in events:
            if event.kind is not ObservationKind.STAMINA_SNAPSHOT:
                continue
            if event.staff_id is None or event.numeric_value is None:
                continue
            value = float(event.numeric_value)
            if not value.is_integer():
                raise ValueError("stamina snapshots must use integral values")
            stamina_by_staff.setdefault(event.staff_id, []).append(int(value))

        window_staff_minimums = tuple(
            ObservationWindowStaffMinimum(staff_id, min(values))
            for staff_id, values in sorted(stamina_by_staff.items())
        )

        if coverage.covers_full_day:
            staff_targets = tuple(
                ObservedStaffMinimum(item.staff_id, item.minimum_stamina)
                for item in window_staff_minimums
            )
            targets = ObservedRepresentativeDayMetrics(
                admitted_arrivals=(
                    arrival_count
                    if mapping.customer_arrival_means_admitted
                    else None
                ),
                completed_checkout_sales=(
                    checkout_end_count
                    if mapping.checkout_service_end_means_completed_sale
                    else None
                ),
                staff_minimums=staff_targets,
            )
        else:
            targets = ObservedRepresentativeDayMetrics()

        return ObservationDayMetricReduction(
            source_id=timeline.source_id,
            coverage=coverage,
            mapping=mapping,
            window_arrival_count=arrival_count,
            window_checkout_service_end_count=checkout_end_count,
            window_staff_minimums=window_staff_minimums,
            comparison_targets=targets,
        )
