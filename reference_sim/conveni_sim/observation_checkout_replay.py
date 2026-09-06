from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from .checkout_service_timing import (
    CheckoutServiceDurationPolicy,
    CheckoutServiceTimingContext,
)
from .minimal_day_scenario import MinimalRepresentativeDayScenario
from .observation_comparison import ObservationIdentityMapping
from .observation_day_adapter import ObservationDayCoverage
from .observations import GameplayObservation, GameplayObservationTimeline, ObservationKind


@dataclass(frozen=True)
class ObservationCheckoutDurationReplayMapping:
    """Explicit permission to use paired service observations as runtime duration."""

    checkout_service_pair_means_runtime_duration: bool = False


@dataclass(frozen=True)
class ObservedCheckoutDurationRule:
    customer_id: str
    staff_id: str
    fixture_id: str
    required_game_minutes: int

    def __post_init__(self) -> None:
        if not self.customer_id or not self.staff_id or not self.fixture_id:
            raise ValueError("observed checkout duration rule requires all entity ids")
        if self.required_game_minutes < 0:
            raise ValueError("required_game_minutes must be >= 0")


@dataclass(frozen=True)
class ObservationCheckoutDurationReplayPlan:
    source_id: str
    coverage: ObservationDayCoverage
    rules: tuple[ObservedCheckoutDurationRule, ...]
    unpaired_starts: tuple[GameplayObservation, ...]
    unpaired_ends: tuple[GameplayObservation, ...]


class ObservedCheckoutDurationPolicy(CheckoutServiceDurationPolicy):
    """Return only explicitly observed per-service durations; unknown stays None."""

    def __init__(self, rules: tuple[ObservedCheckoutDurationRule, ...]) -> None:
        self.rules = rules
        self._durations: dict[tuple[str, str, str], int] = {}
        for rule in rules:
            key = (rule.customer_id, rule.staff_id, rule.fixture_id)
            if key in self._durations:
                raise ValueError(f"duplicate observed checkout duration rule: {key}")
            self._durations[key] = rule.required_game_minutes

    def required_game_minutes(
        self,
        context: CheckoutServiceTimingContext,
    ) -> Optional[int]:
        return self._durations.get(
            (context.customer_id, context.staff_id, context.checkout_fixture_id)
        )


class ObservationCheckoutDurationReplayAdapter:
    """Build evidence-only checkout duration rules from explicit event pairs.

    Start/end events are paired only inside one comparison coverage window and
    only when customer, staff and fixture ids are all explicit. Ends whose starts
    fall outside the window and starts whose ends fall outside it remain listed
    as unpaired rather than being assigned guessed durations.
    """

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
    def _raw_key(event: GameplayObservation) -> tuple[str, str, str]:
        if event.customer_id is None or event.staff_id is None or event.fixture_id is None:
            raise ValueError(
                "checkout duration replay requires explicit customer, staff and fixture ids"
            )
        return (event.customer_id, event.staff_id, event.fixture_id)

    @staticmethod
    def _normalized_key(
        raw_key: tuple[str, str, str],
        identity_mapping: ObservationIdentityMapping,
    ) -> tuple[str, str, str]:
        customer = identity_mapping.customer(raw_key[0])
        staff = identity_mapping.staff(raw_key[1])
        fixture = identity_mapping.fixture(raw_key[2])
        assert customer is not None and staff is not None and fixture is not None
        return customer, staff, fixture

    def build_plan(
        self,
        timeline: GameplayObservationTimeline,
        coverage: ObservationDayCoverage,
        *,
        mapping: ObservationCheckoutDurationReplayMapping = ObservationCheckoutDurationReplayMapping(),
        identity_mapping: ObservationIdentityMapping = ObservationIdentityMapping(),
    ) -> ObservationCheckoutDurationReplayPlan:
        if not mapping.checkout_service_pair_means_runtime_duration:
            raise ValueError(
                "checkout duration replay requires explicit "
                "checkout_service_pair_means_runtime_duration=True"
            )

        events = tuple(
            event
            for event in timeline.events
            if self._in_coverage(event, coverage)
            and event.kind
            in (ObservationKind.CHECKOUT_SERVICE_START, ObservationKind.CHECKOUT_SERVICE_END)
        )
        pending: dict[tuple[str, str, str], GameplayObservation] = {}
        unpaired_ends: list[GameplayObservation] = []
        rules: list[ObservedCheckoutDurationRule] = []
        normalized_rule_keys: set[tuple[str, str, str]] = set()

        for event in events:
            raw_key = self._raw_key(event)
            if event.kind is ObservationKind.CHECKOUT_SERVICE_START:
                if raw_key in pending:
                    raise ValueError(
                        f"duplicate checkout service start without end inside coverage: {raw_key}"
                    )
                pending[raw_key] = event
                continue

            start = pending.pop(raw_key, None)
            if start is None:
                unpaired_ends.append(event)
                continue
            normalized = self._normalized_key(raw_key, identity_mapping)
            if normalized in normalized_rule_keys:
                raise ValueError(
                    "multiple observed services normalize to the same checkout duration rule: "
                    f"{normalized}"
                )
            normalized_rule_keys.add(normalized)
            rules.append(
                ObservedCheckoutDurationRule(
                    customer_id=normalized[0],
                    staff_id=normalized[1],
                    fixture_id=normalized[2],
                    required_game_minutes=start.game_time.minutes_until(event.game_time),
                )
            )

        unpaired_starts = tuple(
            sorted(
                pending.values(),
                key=lambda item: (
                    item.game_time.representative_ordinal_minute,
                    item.sequence,
                ),
            )
        )
        return ObservationCheckoutDurationReplayPlan(
            source_id=timeline.source_id,
            coverage=coverage,
            rules=tuple(rules),
            unpaired_starts=unpaired_starts,
            unpaired_ends=tuple(unpaired_ends),
        )

    @staticmethod
    def build_policy(
        plan: ObservationCheckoutDurationReplayPlan,
    ) -> ObservedCheckoutDurationPolicy:
        return ObservedCheckoutDurationPolicy(plan.rules)

    @staticmethod
    def install_policy(
        scenario: MinimalRepresentativeDayScenario,
        policy: ObservedCheckoutDurationPolicy,
    ) -> None:
        if scenario.orchestrator.checkout_timing is None:
            raise ValueError("scenario does not have checkout timing enabled")
        scenario.orchestrator.checkout_duration_policy = policy
