from __future__ import annotations

from dataclasses import dataclass, replace
from typing import Optional

from .checkout_anger_timing import CheckoutAngerTriggerPolicy
from .minimal_day_scenario import MinimalRepresentativeDayScenarioConfig
from .observation_comparison import ObservationIdentityMapping
from .observation_day_adapter import (
    ObservationDayCoverage,
    ObservationDayMetricMapping,
)
from .observations import GameplayObservationTimeline, ObservationKind
from .representative_day_validation import (
    EventComparedObservationBackedMinimalDayValidationResult,
    validate_minimal_day_with_event_comparison,
)
from .scenario_policies import ScheduledScenarioCustomer
from .simulation_observations import SimulationObservationExportOptions


@dataclass(frozen=True)
class ObservationArrivalReplayMapping:
    """Explicit permission to reinterpret arrival annotations as demand intents."""

    customer_arrival_means_demand_intent: bool = False


@dataclass(frozen=True)
class ObservationArrivalReplayPlan:
    source_id: str
    coverage: ObservationDayCoverage
    schedule: tuple[ScheduledScenarioCustomer, ...]

    @property
    def arrival_count(self) -> int:
        return len(self.schedule)


@dataclass
class ObservedArrivalReplayValidationResult:
    replay_plan: ObservationArrivalReplayPlan
    replay_config: MinimalRepresentativeDayScenarioConfig
    validation: EventComparedObservationBackedMinimalDayValidationResult


class ObservationArrivalReplayAdapter:
    """Turn explicit arrival annotations into a deterministic scenario schedule.

    This adapter does not estimate missing customers, infer ids, extrapolate a
    partial clip or fit a demand rate. Replaying arrivals is opt-in because a raw
    `CUSTOMER_ARRIVAL` annotation is not automatically equivalent to an engine
    demand/admission event.
    """

    @staticmethod
    def _in_coverage(event, coverage: ObservationDayCoverage) -> bool:
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
        mapping: ObservationArrivalReplayMapping = ObservationArrivalReplayMapping(),
    ) -> ObservationArrivalReplayPlan:
        if not mapping.customer_arrival_means_demand_intent:
            raise ValueError(
                "arrival replay requires explicit customer_arrival_means_demand_intent=True"
            )

        arrivals = [
            event
            for event in timeline.events
            if event.kind is ObservationKind.CUSTOMER_ARRIVAL
            and self._in_coverage(event, coverage)
        ]
        schedule: list[ScheduledScenarioCustomer] = []
        seen_ids: set[str] = set()
        for event in arrivals:
            if event.customer_id is None:
                raise ValueError("replayed customer arrival requires an explicit customer_id")
            if event.customer_id in seen_ids:
                raise ValueError(
                    f"duplicate replayed customer id inside coverage: {event.customer_id}"
                )
            seen_ids.add(event.customer_id)
            schedule.append(
                ScheduledScenarioCustomer(
                    minute_of_day=event.game_time.minute_of_day,
                    customer_id=event.customer_id,
                )
            )

        return ObservationArrivalReplayPlan(
            source_id=timeline.source_id,
            coverage=coverage,
            schedule=tuple(schedule),
        )

    def apply_to_config(
        self,
        config: MinimalRepresentativeDayScenarioConfig,
        plan: ObservationArrivalReplayPlan,
    ) -> MinimalRepresentativeDayScenarioConfig:
        if (config.year, config.month, config.day) != (
            plan.coverage.year,
            plan.coverage.month,
            plan.coverage.day,
        ):
            raise ValueError("replay coverage must target the configured representative day")

        start_minute = config.start_hour * 60 + config.start_minute
        early = [item for item in plan.schedule if item.minute_of_day < start_minute]
        if early:
            raise ValueError(
                "replayed arrival precedes the configured simulation start; "
                "extend the run instead of silently dropping it"
            )

        return replace(config, arrivals=plan.schedule)


def validate_minimal_day_replaying_observed_arrivals(
    config: MinimalRepresentativeDayScenarioConfig,
    timeline: GameplayObservationTimeline,
    coverage: ObservationDayCoverage,
    *,
    replay_mapping: ObservationArrivalReplayMapping,
    metric_mapping: ObservationDayMetricMapping = ObservationDayMetricMapping(),
    identity_mapping: ObservationIdentityMapping = ObservationIdentityMapping(),
    checkout_anger_policy: Optional[CheckoutAngerTriggerPolicy] = None,
    export_options: SimulationObservationExportOptions = SimulationObservationExportOptions(),
) -> ObservedArrivalReplayValidationResult:
    """Replay observed arrival timing, then compare downstream runtime behavior.

    The caller still supplies purchase, staff, checkout, stamina, congestion and
    anger behavior through the scenario config/policy seams. Only the arrival
    schedule is replaced by explicitly annotated source events.
    """

    adapter = ObservationArrivalReplayAdapter()
    plan = adapter.build_plan(
        timeline,
        coverage,
        mapping=replay_mapping,
    )
    replay_config = adapter.apply_to_config(config, plan)
    validation = validate_minimal_day_with_event_comparison(
        replay_config,
        timeline,
        coverage,
        mapping=metric_mapping,
        identity_mapping=identity_mapping,
        checkout_anger_policy=checkout_anger_policy,
        export_options=export_options,
    )
    return ObservedArrivalReplayValidationResult(
        replay_plan=plan,
        replay_config=replay_config,
        validation=validation,
    )
