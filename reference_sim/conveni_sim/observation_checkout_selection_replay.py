from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from .checkout_selection_policy import (
    CheckoutCustomerSelectionPolicy,
    CheckoutSelectionContext,
)
from .observation_comparison import ObservationIdentityMapping
from .observation_day_adapter import ObservationDayCoverage
from .observations import GameplayObservation, GameplayObservationTimeline, ObservationKind


@dataclass(frozen=True)
class ObservationCheckoutSelectionReplayMapping:
    """Explicit permission to treat service-start observations as selection rules."""

    checkout_service_start_means_selection: bool = False


@dataclass(frozen=True)
class ObservedCheckoutSelectionRule:
    customer_id: str
    staff_id: str
    fixture_id: str
    start_minute_of_day: int
    observed_sequence: int

    def __post_init__(self) -> None:
        if not self.customer_id or not self.staff_id or not self.fixture_id:
            raise ValueError("checkout selection rule requires customer, staff and fixture ids")
        if not 0 <= self.start_minute_of_day < 24 * 60:
            raise ValueError("start_minute_of_day must be within 0..1439")
        if self.observed_sequence < 0:
            raise ValueError("observed_sequence must be >= 0")


@dataclass(frozen=True)
class ObservationCheckoutSelectionReplayPlan:
    source_id: str
    coverage: ObservationDayCoverage
    rules: tuple[ObservedCheckoutSelectionRule, ...]


class ObservedCheckoutSelectionPolicy(CheckoutCustomerSelectionPolicy):
    """Replay explicit service-start order/timing without a FIFO fallback.

    For each staff/checkout pair, the next observed customer is the only customer
    that may be selected. The policy does not select them before the observed
    game minute. If that customer is not yet waiting when the minute is reached,
    the rule stays pending rather than skipping to another waiting customer.
    """

    def __init__(self, plan: ObservationCheckoutSelectionReplayPlan) -> None:
        self.plan = plan
        self._rules_by_staff_fixture: dict[
            tuple[str, str], tuple[ObservedCheckoutSelectionRule, ...]
        ] = {}
        grouped: dict[tuple[str, str], list[ObservedCheckoutSelectionRule]] = {}
        for rule in plan.rules:
            grouped.setdefault((rule.staff_id, rule.fixture_id), []).append(rule)
        for key, rules in grouped.items():
            rules.sort(key=lambda item: (item.start_minute_of_day, item.observed_sequence))
            self._rules_by_staff_fixture[key] = tuple(rules)
        self._next_index: dict[tuple[str, str], int] = {
            key: 0 for key in self._rules_by_staff_fixture
        }

    def choose_customer(self, context: CheckoutSelectionContext) -> Optional[str]:
        key = (context.staff_id, context.checkout_fixture_id)
        rules = self._rules_by_staff_fixture.get(key)
        if not rules:
            return None
        index = self._next_index[key]
        if index >= len(rules):
            return None
        rule = rules[index]
        if context.current_minute_of_day < rule.start_minute_of_day:
            return None
        if rule.customer_id not in context.waiting_customer_ids:
            return None
        self._next_index[key] = index + 1
        return rule.customer_id

    def pending_rule(
        self,
        staff_id: str,
        fixture_id: str,
    ) -> Optional[ObservedCheckoutSelectionRule]:
        key = (staff_id, fixture_id)
        rules = self._rules_by_staff_fixture.get(key)
        if not rules:
            return None
        index = self._next_index[key]
        return rules[index] if index < len(rules) else None


class ObservationCheckoutSelectionReplayAdapter:
    """Project explicit in-window checkout service starts into replay rules."""

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
    def _normalized_ids(
        event: GameplayObservation,
        identity_mapping: ObservationIdentityMapping,
    ) -> tuple[str, str, str]:
        if event.customer_id is None or event.staff_id is None or event.fixture_id is None:
            raise ValueError(
                "checkout selection replay requires explicit customer, staff and fixture ids"
            )
        customer = identity_mapping.customer(event.customer_id)
        staff = identity_mapping.staff(event.staff_id)
        fixture = identity_mapping.fixture(event.fixture_id)
        assert customer is not None and staff is not None and fixture is not None
        return customer, staff, fixture

    def build_plan(
        self,
        timeline: GameplayObservationTimeline,
        coverage: ObservationDayCoverage,
        *,
        mapping: ObservationCheckoutSelectionReplayMapping = ObservationCheckoutSelectionReplayMapping(),
        identity_mapping: ObservationIdentityMapping = ObservationIdentityMapping(),
    ) -> ObservationCheckoutSelectionReplayPlan:
        if not mapping.checkout_service_start_means_selection:
            raise ValueError(
                "checkout selection replay requires explicit "
                "checkout_service_start_means_selection=True"
            )

        rules: list[ObservedCheckoutSelectionRule] = []
        for event in timeline.events:
            if event.kind is not ObservationKind.CHECKOUT_SERVICE_START:
                continue
            if not self._in_coverage(event, coverage):
                continue
            customer, staff, fixture = self._normalized_ids(event, identity_mapping)
            rules.append(
                ObservedCheckoutSelectionRule(
                    customer_id=customer,
                    staff_id=staff,
                    fixture_id=fixture,
                    start_minute_of_day=event.game_time.minute_of_day,
                    observed_sequence=event.sequence,
                )
            )

        rules.sort(key=lambda item: (item.start_minute_of_day, item.observed_sequence))
        return ObservationCheckoutSelectionReplayPlan(
            source_id=timeline.source_id,
            coverage=coverage,
            rules=tuple(rules),
        )

    @staticmethod
    def build_policy(
        plan: ObservationCheckoutSelectionReplayPlan,
    ) -> ObservedCheckoutSelectionPolicy:
        return ObservedCheckoutSelectionPolicy(plan)
