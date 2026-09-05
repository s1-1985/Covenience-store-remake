from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Iterable, Optional

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
    applied: bool = False


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


class PopularityDecayContext(str, Enum):
    ORDINARY_DAY = "ordinary_day"
    MONTH_SKIP = "month_skip"


@dataclass
class PopularityDecayOpportunity:
    """One evidence-backed decay application whose numeric amount is unresolved."""

    sequence: int
    store_id: str
    context: PopularityDecayContext
    before: int
    rating_snapshot: Optional[int]
    source: str
    resolved_after: Optional[int] = None

    @property
    def resolved(self) -> bool:
        return self.resolved_after is not None

    @property
    def applied_loss(self) -> Optional[int]:
        if self.resolved_after is None:
            return None
        return self.before - self.resolved_after


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
    """Per-store popularity with explicit gains and unresolved decay opportunities.

    Confirmed promotion gains can be applied immediately. Daily popularity loss
    is structurally supported, and the month-skip period applies only one
    day-equivalent loss, but the exact rating-dependent decay formula is not yet
    recovered. Decay is therefore recorded first and resolved only by an
    evidence-backed policy, direct observation or explicit caller result.
    """

    def __init__(self) -> None:
        self._popularity: dict[str, int] = {}
        self._ratings: dict[str, Optional[int]] = {}
        self._decay_opportunities: list[PopularityDecayOpportunity] = []
        self._next_decay_sequence = 1

    @property
    def store_ids(self) -> tuple[str, ...]:
        return tuple(self._popularity)

    @property
    def decay_opportunities(self) -> tuple[PopularityDecayOpportunity, ...]:
        return tuple(self._decay_opportunities)

    @property
    def unresolved_decay_opportunities(self) -> tuple[PopularityDecayOpportunity, ...]:
        return tuple(item for item in self._decay_opportunities if not item.resolved)

    def add_store(
        self,
        store_id: str,
        *,
        popularity: int,
        rating: Optional[int] = None,
    ) -> None:
        if not store_id:
            raise ValueError("store_id must be non-empty")
        if store_id in self._popularity:
            raise ValueError(f"duplicate store id: {store_id}")
        if not 0 <= popularity <= 100:
            raise ValueError("popularity must be 0..100")
        if rating is not None and rating < 0:
            raise ValueError("rating must be >= 0 or None")
        self._popularity[store_id] = popularity
        self._ratings[store_id] = rating

    def popularity(self, store_id: str) -> int:
        return self._popularity[store_id]

    def rating(self, store_id: str) -> Optional[int]:
        return self._ratings[store_id]

    def set_rating(self, store_id: str, rating: Optional[int]) -> None:
        if rating is not None and rating < 0:
            raise ValueError("rating must be >= 0 or None")
        if store_id not in self._popularity:
            raise KeyError(f"unknown store id: {store_id}")
        self._ratings[store_id] = rating

    def decay_opportunity(self, sequence: int) -> PopularityDecayOpportunity:
        for opportunity in self._decay_opportunities:
            if opportunity.sequence == sequence:
                return opportunity
        raise KeyError(f"unknown popularity decay opportunity: {sequence}")

    def record_decay_opportunity(
        self,
        store_id: str,
        *,
        context: PopularityDecayContext,
        source: str,
    ) -> PopularityDecayOpportunity:
        if store_id not in self._popularity:
            raise KeyError(f"unknown store id: {store_id}")
        if not source:
            raise ValueError("source must be non-empty")
        opportunity = PopularityDecayOpportunity(
            sequence=self._next_decay_sequence,
            store_id=store_id,
            context=context,
            before=self._popularity[store_id],
            rating_snapshot=self._ratings[store_id],
            source=source,
        )
        self._next_decay_sequence += 1
        self._decay_opportunities.append(opportunity)
        return opportunity

    def record_ordinary_daily_decay(
        self,
        store_id: str,
        *,
        source: str = "DIRECT-PLAY-SS: popularity decays daily according to store rating",
    ) -> PopularityDecayOpportunity:
        return self.record_decay_opportunity(
            store_id,
            context=PopularityDecayContext.ORDINARY_DAY,
            source=source,
        )

    def record_month_skip_decay(
        self,
        store_id: str,
        *,
        source: str = "first-title PS/SS FAQ: skipped period applies one day-equivalent popularity loss",
    ) -> PopularityDecayOpportunity:
        """Record exactly one decay application for day5-to-month-end skipping."""
        return self.record_decay_opportunity(
            store_id,
            context=PopularityDecayContext.MONTH_SKIP,
            source=source,
        )

    def resolve_decay_opportunity(
        self,
        sequence: int,
        *,
        after: int,
    ) -> PopularityDecayOpportunity:
        if not 0 <= after <= 100:
            raise ValueError("after must be 0..100")
        opportunity = self.decay_opportunity(sequence)
        if opportunity.resolved:
            raise ValueError("popularity decay opportunity is already resolved")
        if after > opportunity.before:
            raise ValueError("popularity decay cannot increase popularity")
        if self._popularity[opportunity.store_id] != opportunity.before:
            raise ValueError("popularity changed after decay opportunity was recorded")
        self._popularity[opportunity.store_id] = after
        opportunity.resolved_after = after
        return opportunity

    def apply_promotion(
        self,
        scheduled: ScheduledPromotion,
        scheduler: PromotionScheduler,
        *,
        target_store_ids: Iterable[str],
    ) -> PromotionApplication:
        if not scheduled.fired:
            raise ValueError("promotion event has not fired")
        if scheduled.applied:
            raise ValueError("promotion event has already been applied")

        definition = scheduler.definition(scheduled.promotion_id)
        gain = definition.popularity_gain.value

        # Validate the complete target set before mutating anything.  This keeps
        # an invalid caller-provided store id from applying the event to only a
        # prefix of stores and leaving an unrecoverable partial state.
        targets: list[str] = []
        seen: set[str] = set()
        for store_id in target_store_ids:
            if store_id in seen:
                continue
            seen.add(store_id)
            if store_id not in self._popularity:
                raise KeyError(f"unknown store id: {store_id}")
            targets.append(store_id)

        changes: list[PopularityChange] = []
        for store_id in targets:
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

        scheduled.applied = True
        return PromotionApplication(
            promotion_id=scheduled.promotion_id,
            popularity_gain=gain,
            changes=tuple(changes),
        )
