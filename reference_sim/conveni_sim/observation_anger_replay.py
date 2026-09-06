from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Optional

from .checkout_anger_timing import CheckoutAngerTimingContext, CheckoutAngerTriggerPolicy
from .observation_comparison import ObservationIdentityMapping
from .observation_day_adapter import ObservationDayCoverage
from .observations import GameplayObservation, GameplayObservationTimeline, ObservationKind


class ObservedAngerBasis(str, Enum):
    """Caller-selected elapsed-time basis; this choice is not inferred from footage."""

    QUEUE_ELAPSED = "queue_elapsed"
    SERVICE_ELAPSED = "service_elapsed"


@dataclass(frozen=True)
class ObservationAngerReplayMapping:
    """Explicit permission to use an observed anchor->anger pair as a trigger rule."""

    anger_pair_means_runtime_trigger: bool = False


@dataclass(frozen=True)
class ObservedAngerTriggerRule:
    basis: ObservedAngerBasis
    customer_id: str
    fixture_id: str
    trigger_after_game_minutes: int
    staff_id: Optional[str] = None

    def __post_init__(self) -> None:
        if not self.customer_id or not self.fixture_id:
            raise ValueError("observed anger rule requires customer and fixture ids")
        if self.trigger_after_game_minutes < 0:
            raise ValueError("trigger_after_game_minutes must be >= 0")
        if self.basis is ObservedAngerBasis.SERVICE_ELAPSED and not self.staff_id:
            raise ValueError("service-elapsed anger rule requires an explicit staff id")
        if self.basis is ObservedAngerBasis.QUEUE_ELAPSED and self.staff_id is not None:
            raise ValueError("queue-elapsed anger rule must not bind a staff id")


@dataclass(frozen=True)
class ObservationAngerReplayPlan:
    source_id: str
    coverage: ObservationDayCoverage
    basis: ObservedAngerBasis
    rules: tuple[ObservedAngerTriggerRule, ...]
    unpaired_anchors: tuple[GameplayObservation, ...]
    unpaired_angers: tuple[GameplayObservation, ...]


class ObservedCheckoutAngerPolicy(CheckoutAngerTriggerPolicy):
    """Trigger only from explicit observed per-customer anger thresholds.

    `None` means that no rule was recovered for the current runtime service.
    The existing anger coordinator still owns the staff-specific consequence and
    may defer a queue-based request until an active checkout staff member exists.
    """

    def __init__(self, plan: ObservationAngerReplayPlan) -> None:
        self.basis = plan.basis
        self.rules = plan.rules
        self._queue_thresholds: dict[tuple[str, str], int] = {}
        self._service_thresholds: dict[tuple[str, str, str], int] = {}
        for rule in plan.rules:
            if rule.basis is not self.basis:
                raise ValueError("anger replay plan contains a mixed timing basis")
            if self.basis is ObservedAngerBasis.QUEUE_ELAPSED:
                key = (rule.customer_id, rule.fixture_id)
                if key in self._queue_thresholds:
                    raise ValueError(f"duplicate queue anger rule: {key}")
                self._queue_thresholds[key] = rule.trigger_after_game_minutes
            else:
                assert rule.staff_id is not None
                key = (rule.customer_id, rule.staff_id, rule.fixture_id)
                if key in self._service_thresholds:
                    raise ValueError(f"duplicate service anger rule: {key}")
                self._service_thresholds[key] = rule.trigger_after_game_minutes

    def should_trigger(self, context: CheckoutAngerTimingContext) -> Optional[bool]:
        if self.basis is ObservedAngerBasis.QUEUE_ELAPSED:
            threshold = self._queue_thresholds.get(
                (context.customer_id, context.checkout_fixture_id)
            )
            if threshold is None:
                return None
            return context.total_checkout_elapsed_game_minutes >= threshold

        if context.active_staff_id is None or context.service_elapsed_game_minutes is None:
            return None
        threshold = self._service_thresholds.get(
            (
                context.customer_id,
                context.active_staff_id,
                context.checkout_fixture_id,
            )
        )
        if threshold is None:
            return None
        return context.service_elapsed_game_minutes >= threshold


class ObservationAngerReplayAdapter:
    """Build first-anger trigger rules only from explicit in-window event pairs."""

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

    @staticmethod
    def _queue_key(event: GameplayObservation) -> tuple[str, str]:
        if event.customer_id is None or event.fixture_id is None:
            raise ValueError("queue-based anger replay requires customer and fixture ids")
        return event.customer_id, event.fixture_id

    @staticmethod
    def _service_key(event: GameplayObservation) -> tuple[str, str, str]:
        if event.customer_id is None or event.staff_id is None or event.fixture_id is None:
            raise ValueError(
                "service-based anger replay requires customer, staff and fixture ids"
            )
        return event.customer_id, event.staff_id, event.fixture_id

    @staticmethod
    def _normalized_queue_key(
        raw: tuple[str, str],
        identity_mapping: ObservationIdentityMapping,
    ) -> tuple[str, str]:
        customer = identity_mapping.customer(raw[0])
        fixture = identity_mapping.fixture(raw[1])
        assert customer is not None and fixture is not None
        return customer, fixture

    @staticmethod
    def _normalized_service_key(
        raw: tuple[str, str, str],
        identity_mapping: ObservationIdentityMapping,
    ) -> tuple[str, str, str]:
        customer = identity_mapping.customer(raw[0])
        staff = identity_mapping.staff(raw[1])
        fixture = identity_mapping.fixture(raw[2])
        assert customer is not None and staff is not None and fixture is not None
        return customer, staff, fixture

    def build_plan(
        self,
        timeline: GameplayObservationTimeline,
        coverage: ObservationDayCoverage,
        *,
        basis: ObservedAngerBasis,
        mapping: ObservationAngerReplayMapping = ObservationAngerReplayMapping(),
        identity_mapping: ObservationIdentityMapping = ObservationIdentityMapping(),
    ) -> ObservationAngerReplayPlan:
        if not mapping.anger_pair_means_runtime_trigger:
            raise ValueError(
                "anger replay requires explicit anger_pair_means_runtime_trigger=True"
            )

        anchor_kind = (
            ObservationKind.CHECKOUT_QUEUE_ENTER
            if basis is ObservedAngerBasis.QUEUE_ELAPSED
            else ObservationKind.CHECKOUT_SERVICE_START
        )
        events = tuple(
            event
            for event in timeline.events
            if self._in_coverage(event, coverage)
            and event.kind in (anchor_kind, ObservationKind.CHECKOUT_ANGER)
        )

        pending: dict[object, GameplayObservation] = {}
        unpaired_angers: list[GameplayObservation] = []
        rules: list[ObservedAngerTriggerRule] = []
        normalized_rule_keys: set[object] = set()

        for event in events:
            raw_key: object
            if basis is ObservedAngerBasis.QUEUE_ELAPSED:
                raw_key = self._queue_key(event)
            else:
                raw_key = self._service_key(event)

            if event.kind is anchor_kind:
                if raw_key in pending:
                    raise ValueError(
                        f"duplicate anger timing anchor without anger inside coverage: {raw_key}"
                    )
                pending[raw_key] = event
                continue

            anchor = pending.pop(raw_key, None)
            if anchor is None:
                unpaired_angers.append(event)
                continue

            if basis is ObservedAngerBasis.QUEUE_ELAPSED:
                normalized = self._normalized_queue_key(raw_key, identity_mapping)  # type: ignore[arg-type]
                rule_key: object = normalized
                if rule_key in normalized_rule_keys:
                    raise ValueError(
                        f"multiple observations normalize to the same queue anger rule: {normalized}"
                    )
                normalized_rule_keys.add(rule_key)
                rules.append(
                    ObservedAngerTriggerRule(
                        basis=basis,
                        customer_id=normalized[0],
                        fixture_id=normalized[1],
                        trigger_after_game_minutes=anchor.game_time.minutes_until(event.game_time),
                    )
                )
            else:
                normalized = self._normalized_service_key(raw_key, identity_mapping)  # type: ignore[arg-type]
                rule_key = normalized
                if rule_key in normalized_rule_keys:
                    raise ValueError(
                        f"multiple observations normalize to the same service anger rule: {normalized}"
                    )
                normalized_rule_keys.add(rule_key)
                rules.append(
                    ObservedAngerTriggerRule(
                        basis=basis,
                        customer_id=normalized[0],
                        staff_id=normalized[1],
                        fixture_id=normalized[2],
                        trigger_after_game_minutes=anchor.game_time.minutes_until(event.game_time),
                    )
                )

        unpaired_anchors = tuple(
            sorted(
                pending.values(),
                key=lambda item: (
                    item.game_time.representative_ordinal_minute,
                    item.sequence,
                ),
            )
        )
        return ObservationAngerReplayPlan(
            source_id=timeline.source_id,
            coverage=coverage,
            basis=basis,
            rules=tuple(rules),
            unpaired_anchors=unpaired_anchors,
            unpaired_angers=tuple(unpaired_angers),
        )

    @staticmethod
    def build_policy(plan: ObservationAngerReplayPlan) -> ObservedCheckoutAngerPolicy:
        return ObservedCheckoutAngerPolicy(plan)
