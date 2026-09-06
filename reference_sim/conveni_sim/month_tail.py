from __future__ import annotations

from dataclasses import dataclass

from .clock import MonthBoundary
from .month_cycle import RepresentativeMonthSample
from .promotion import StorePopularityRuntime


@dataclass(frozen=True)
class MonthTailTransition:
    """Explicit day-5-to-month-end transition for one completed representative month.

    The first-title evidence supports a compressed calendar tail after day 4,
    but does not recover finance, AI, growth, construction, or other aggregation
    rules for that interval.  This record therefore exposes the transition as a
    boundary event and only links the one effect currently evidenced here:
    exactly one day-equivalent popularity-decay opportunity per selected store.
    """

    year: int
    month: int
    boundary: MonthBoundary
    popularity_decay_sequences: tuple[int, ...]


class MonthTailTransitionRuntime:
    """Record compressed month-tail boundaries without simulating skipped days."""

    def __init__(self) -> None:
        self._transitions: list[MonthTailTransition] = []
        self._recorded_months: set[tuple[int, int]] = set()

    @property
    def transitions(self) -> tuple[MonthTailTransition, ...]:
        return tuple(self._transitions)

    def record_transition(
        self,
        sample: RepresentativeMonthSample,
        *,
        popularity: StorePopularityRuntime | None = None,
        popularity_store_ids: tuple[str, ...] = (),
    ) -> MonthTailTransition:
        if not sample.complete_four_day_sample:
            raise ValueError("month-tail transition requires a complete day 1..4 sample")
        if (sample.boundary.previous_year, sample.boundary.previous_month) != (
            sample.year,
            sample.month,
        ):
            raise ValueError("sample month does not match its month boundary")

        key = (sample.year, sample.month)
        if key in self._recorded_months:
            raise ValueError("month-tail transition is already recorded for this month")

        if popularity is None and popularity_store_ids:
            raise ValueError("popularity runtime is required when decay targets are supplied")

        targets = tuple(dict.fromkeys(popularity_store_ids))
        if popularity is not None:
            known = set(popularity.store_ids)
            unknown = tuple(store_id for store_id in targets if store_id not in known)
            if unknown:
                raise KeyError(f"unknown popularity store ids: {unknown}")

        sequences: list[int] = []
        if popularity is not None:
            for store_id in targets:
                opportunity = popularity.record_month_skip_decay(
                    store_id,
                    source=(
                        "first-title PS/SS month-tail evidence: day 5 through month end "
                        "is compressed and popularity receives one day-equivalent decay"
                    ),
                )
                sequences.append(opportunity.sequence)

        transition = MonthTailTransition(
            year=sample.year,
            month=sample.month,
            boundary=sample.boundary,
            popularity_decay_sequences=tuple(sequences),
        )
        self._recorded_months.add(key)
        self._transitions.append(transition)
        return transition
