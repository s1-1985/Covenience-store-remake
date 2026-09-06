from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass
from typing import Optional

from .checkout_pre_service_departure import (
    CheckoutPreServiceAction,
    CheckoutPreServiceDecision,
    CheckoutPreServiceDepartureContext,
    CheckoutPreServiceDeparturePolicy,
)
from .observation_comparison import ObservationIdentityMapping
from .observation_day_adapter import ObservationDayCoverage
from .observations import GameplayObservation, GameplayObservationTimeline, ObservationKind


@dataclass(frozen=True)
class ObservationCheckoutPreServiceDepartureReplayMapping:
    """Explicitly interpret a cause-neutral checkout return as pre-service departure."""

    checkout_staff_return_means_pre_service_departure: bool = False


@dataclass(frozen=True)
class ObservedCheckoutPreServiceDepartureRule:
    staff_id: str
    checkout_fixture_id: str
    occurrence_index: int
    return_minute_of_day: int

    def __post_init__(self) -> None:
        if not self.staff_id:
            raise ValueError("observed checkout departure rule requires staff_id")
        if not self.checkout_fixture_id:
            raise ValueError("observed checkout departure rule requires checkout_fixture_id")
        if self.occurrence_index < 0:
            raise ValueError("occurrence_index must be >= 0")
        if not 0 <= self.return_minute_of_day < 24 * 60:
            raise ValueError("return_minute_of_day must be 0..1439")


@dataclass(frozen=True)
class ObservationCheckoutPreServiceDepartureReplayPlan:
    source_id: str
    coverage: ObservationDayCoverage
    rules: tuple[ObservedCheckoutPreServiceDepartureRule, ...]
    source_events: tuple[GameplayObservation, ...]


class ObservedCheckoutPreServiceDeparturePolicy(CheckoutPreServiceDeparturePolicy):
    """Replay only explicitly selected checkout-return observations.

    Before the next observed return minute, the decision remains unresolved so
    the replay layer does not invent an earlier service start. At or after the
    observed minute, the next matching staff/checkout occurrence returns toward
    the break room. If factual checkout demand or capacity is absent, the runtime
    coordinator does not consult this policy, so the observation cannot create
    demand or a free service slot.

    If runtime conditions make the departure happen later than the observed
    minute, normal event comparison exposes that signed timing delta.
    """

    def __init__(
        self,
        rules: tuple[ObservedCheckoutPreServiceDepartureRule, ...],
        *,
        break_room_target_id: Optional[str] = None,
    ) -> None:
        self.rules = rules
        self.break_room_target_id = break_room_target_id
        self._rules_by_key: dict[
            tuple[str, str], tuple[ObservedCheckoutPreServiceDepartureRule, ...]
        ] = {}
        grouped: dict[
            tuple[str, str], list[ObservedCheckoutPreServiceDepartureRule]
        ] = defaultdict(list)
        for rule in rules:
            grouped[(rule.staff_id, rule.checkout_fixture_id)].append(rule)
        for key, items in grouped.items():
            ordered = tuple(sorted(items, key=lambda item: item.occurrence_index))
            expected = tuple(range(len(ordered)))
            actual = tuple(item.occurrence_index for item in ordered)
            if actual != expected:
                raise ValueError(f"checkout departure occurrences must be contiguous for {key}")
            self._rules_by_key[key] = ordered
        self._next_occurrence: dict[tuple[str, str], int] = defaultdict(int)

    def decide(
        self,
        context: CheckoutPreServiceDepartureContext,
    ) -> Optional[CheckoutPreServiceDecision]:
        key = (context.staff_id, context.checkout_fixture_id)
        occurrence = self._next_occurrence[key]
        rules = self._rules_by_key.get(key, ())
        if occurrence >= len(rules):
            return None
        rule = rules[occurrence]
        if context.current_minute_of_day < rule.return_minute_of_day:
            return None

        self._next_occurrence[key] = occurrence + 1
        return CheckoutPreServiceDecision(
            CheckoutPreServiceAction.RETURN_TO_BREAK_ROOM,
            break_room_target_id=self.break_room_target_id,
        )


class ObservationCheckoutPreServiceDepartureReplayAdapter:
    """Build pre-service departure rules from explicitly interpreted return events."""

    @staticmethod
    def _in_coverage(event: GameplayObservation, coverage: ObservationDayCoverage) -> bool:
        return (
            event.game_time.year == coverage.year
            and event.game_time.month == coverage.month
            and event.game_time.day == coverage.day
            and coverage.start_minute_inclusive
            <= event.game_time.minute_of_day
            < coverage.end_minute_exclusive
        )

    def build_plan(
        self,
        timeline: GameplayObservationTimeline,
        coverage: ObservationDayCoverage,
        *,
        mapping: ObservationCheckoutPreServiceDepartureReplayMapping = ObservationCheckoutPreServiceDepartureReplayMapping(),
        identity_mapping: ObservationIdentityMapping = ObservationIdentityMapping(),
    ) -> ObservationCheckoutPreServiceDepartureReplayPlan:
        if not mapping.checkout_staff_return_means_pre_service_departure:
            raise ValueError(
                "checkout pre-service departure replay requires explicit "
                "checkout_staff_return_means_pre_service_departure=True"
            )

        source_events = tuple(
            event
            for event in timeline.events
            if self._in_coverage(event, coverage)
            and event.kind is ObservationKind.CHECKOUT_STAFF_RETURN_TO_BREAK_ROOM
        )
        occurrence_counts: dict[tuple[str, str], int] = defaultdict(int)
        rules: list[ObservedCheckoutPreServiceDepartureRule] = []
        for event in source_events:
            if event.staff_id is None or event.fixture_id is None:
                raise ValueError(
                    "checkout staff return replay requires explicit staff_id and fixture_id"
                )
            staff_id = identity_mapping.staff(event.staff_id)
            fixture_id = identity_mapping.fixture(event.fixture_id)
            assert staff_id is not None
            assert fixture_id is not None
            key = (staff_id, fixture_id)
            occurrence_index = occurrence_counts[key]
            occurrence_counts[key] = occurrence_index + 1
            rules.append(
                ObservedCheckoutPreServiceDepartureRule(
                    staff_id=staff_id,
                    checkout_fixture_id=fixture_id,
                    occurrence_index=occurrence_index,
                    return_minute_of_day=event.game_time.minute_of_day,
                )
            )

        return ObservationCheckoutPreServiceDepartureReplayPlan(
            source_id=timeline.source_id,
            coverage=coverage,
            rules=tuple(rules),
            source_events=source_events,
        )

    @staticmethod
    def build_policy(
        plan: ObservationCheckoutPreServiceDepartureReplayPlan,
        *,
        break_room_target_id: Optional[str] = None,
    ) -> ObservedCheckoutPreServiceDeparturePolicy:
        return ObservedCheckoutPreServiceDeparturePolicy(
            plan.rules,
            break_room_target_id=break_room_target_id,
        )
