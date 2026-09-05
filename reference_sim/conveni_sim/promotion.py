from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

from .models import PromotionDefinition


@dataclass(frozen=True, order=True)
class PromotionMoment:
    """Representative-month timestamp used by first-title promotion events."""

    year: int
    month: int
    day: int
    hour: int

    def __post_init__(self) -> None:
        if self.year < 1:
            raise ValueError("year must be >= 1")
        if not 1 <= self.month <= 12:
            raise ValueError("month must be 1..12")
        if not 1 <= self.day <= 4:
            raise ValueError("representative day must be 1..4")
        if not 0 <= self.hour <= 23:
            raise ValueError("hour must be 0..23")


@dataclass
class ScheduledPromotion:
    promotion_id: str
    target_year: int
    target_month: int
    scheduled_at: PromotionMoment
    trigger_at: PromotionMoment
    fired: bool = False


@dataclass(frozen=True)
class PopularityChange:
    store_id: str
    before: int
    after: int
    applied_gain: int


@dataclass(frozen=True)
class PromotionApplication:
    promotion_id: str
    popularity_gain: int
    changes: tuple[PopularityChange, ...]


class PromotionScheduler:
    """Fixed first-title promotion timing without guessed payment semantics.

    Evidence supports one use per promotion method per month, fixed event
    timestamps, all-owned-store popularity gain and a popularity cap of 100.
    Payment timing and late same-month scheduling behavior are unresolved, so
    this scheduler does not debit cash and rejects scheduling after the known
    event timestamp instead of inventing a rule.
    """

    def __init__(self, definitions: Iterable[PromotionDefinition]) -> None:
        self._definitions = {definition.id: definition for definition in definitions}
        if not self._definitions:
            raise ValueError("at least one promotion definition is required")
        self._scheduled: dict[tuple[int, int, str], ScheduledPromotion] = {}

    @property
    def scheduled(self) -> tuple[ScheduledPromotion, ...]:
        return tuple(
            sorted(
                self._scheduled.values(),
                key=lambda item: (item.trigger_at, item.promotion_id),
            )
        )

    def definition(self, promotion_id: str) -> PromotionDefinition:
        return self._definitions[promotion_id]

    def schedule(
        self,
        promotion_id: str,
        *,
        target_year: int,
        target_month: int,
        scheduled_at: PromotionMoment,
    ) -> ScheduledPromotion:
        definition = self.definition(promotion_id)
        if (scheduled_at.year, scheduled_at.month) != (target_year, target_month):
            raise ValueError("cross-month advance booking is unresolved")

        trigger_at = PromotionMoment(
            target_year,
            target_month,
            definition.trigger_day.value,
            definition.trigger_hour.value,
        )
        if scheduled_at > trigger_at:
            raise ValueError("scheduling after the known event time is unresolved")

        key = (target_year, target_month, promotion_id)
        if key in self._scheduled:
            raise ValueError("promotion method is already scheduled for this month")

        record = ScheduledPromotion(
            promotion_id=promotion_id,
            target_year=target_year,
            target_month=target_month,
            scheduled_at=scheduled_at,
            trigger_at=trigger_at,
        )
        self._scheduled[key] = record
        return record

    def pop_due(self, now: PromotionMoment) -> tuple[ScheduledPromotion, ...]:
        due: list[ScheduledPromotion] = []
        for record in self.scheduled:
            if record.fired:
                continue
            if (record.target_year, record.target_month) != (now.year, now.month):
                continue
            if record.trigger_at <= now:
                record.fired = True
                due.append(record)
        return tuple(due)


class StorePopularityRuntime:
    """Per-store popularity values with only the confirmed 0..100 cap rule."""

    def __init__(self) -> None:
        self._popularity: dict[str, int] = {}

    @property
    def store_ids(self) -> tuple[str, ...]:
        return tuple(self._popularity)

    def add_store(self, store_id: str, *, popularity: int) -> None:
        if not store_id:
            raise ValueError("store_id must be non-empty")
        if store_id in self._popularity:
            raise ValueError(f"duplicate store id: {store_id}")
        if not 0 <= popularity <= 100:
            raise ValueError("popularity must be 0..100")
        self._popularity[store_id] = popularity

    def popularity(self, store_id: str) -> int:
        return self._popularity[store_id]

    def apply_promotion(
        self,
        scheduled: ScheduledPromotion,
        scheduler: PromotionScheduler,
        *,
        target_store_ids: Iterable[str],
    ) -> PromotionApplication:
        if not scheduled.fired:
            raise ValueError("promotion event has not fired")
        definition = scheduler.definition(scheduled.promotion_id)
        gain = definition.popularity_gain.value
        changes: list[PopularityChange] = []
        seen: set[str] = set()
        for store_id in target_store_ids:
            if store_id in seen:
                continue
            seen.add(store_id)
            before = self._popularity[store_id]
            after = min(100, before + gain)
            self._popularity[store_id] = after
            changes.append(
                PopularityChange(
                    store_id=store_id,
                    before=before,
                    after=after,
                    applied_gain=after - before,
                )
            )
        return PromotionApplication(
            promotion_id=scheduled.promotion_id,
            popularity_gain=gain,
            changes=tuple(changes),
        )
