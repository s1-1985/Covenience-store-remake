from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from .minimal_day_scenario import MinimalRepresentativeDayScenarioConfig
from .observation_anger_replay import (
    ObservationAngerReplayAdapter,
    ObservationAngerReplayMapping,
    ObservationAngerReplayPlan,
    ObservedAngerBasis,
)
from .observation_checkout_pre_service_departure_replay import (
    ObservationCheckoutPreServiceDepartureReplayAdapter,
    ObservationCheckoutPreServiceDepartureReplayMapping,
    ObservationCheckoutPreServiceDepartureReplayPlan,
)
from .observation_checkout_replay import (
    ObservationCheckoutDurationReplayAdapter,
    ObservationCheckoutDurationReplayMapping,
    ObservationCheckoutDurationReplayPlan,
)
from .observation_checkout_selection_replay import (
    ObservationCheckoutSelectionReplayAdapter,
    ObservationCheckoutSelectionReplayMapping,
    ObservationCheckoutSelectionReplayPlan,
)
from .observation_comparison import ObservationIdentityMapping
from .observation_day_adapter import ObservationDayCoverage, ObservationDayMetricMapping
from .observation_replay import (
    ObservationArrivalReplayAdapter,
    ObservationArrivalReplayMapping,
    ObservationArrivalReplayPlan,
)
from .observation_staff_work_interruption_replay import (
    ObservationStaffWorkInterruptionReplayAdapter,
    ObservationStaffWorkInterruptionReplayMapping,
    ObservationStaffWorkInterruptionReplayPlan,
)
from .observation_staff_work_replay import (
    ObservationStaffWorkDurationReplayAdapter,
    ObservationStaffWorkDurationReplayMapping,
    ObservationStaffWorkDurationReplayPlan,
)
from .observation_staff_work_start_replay import (
    ObservationStaffWorkStartReplayAdapter,
    ObservationStaffWorkStartReplayMapping,
    ObservationStaffWorkStartReplayPlan,
)
from .observations import GameplayObservationTimeline
from .representative_day_validation import (
    EventComparedObservationBackedMinimalDayValidationResult,
    validate_minimal_day_with_event_comparison,
)
from .simulation_observations import SimulationObservationExportOptions


@dataclass(frozen=True)
class ComposedObservationReplaySelection:
    """Explicitly select which observation-backed seams replace synthetic inputs."""

    arrivals: Optional[ObservationArrivalReplayMapping] = None
    checkout_durations: Optional[ObservationCheckoutDurationReplayMapping] = None
    checkout_selection: Optional[ObservationCheckoutSelectionReplayMapping] = None
    checkout_pre_service_departures: Optional[
        ObservationCheckoutPreServiceDepartureReplayMapping
    ] = None
    staff_work_starts: Optional[ObservationStaffWorkStartReplayMapping] = None
    staff_work_durations: Optional[ObservationStaffWorkDurationReplayMapping] = None
    staff_work_interruptions: Optional[ObservationStaffWorkInterruptionReplayMapping] = None
    anger: Optional[ObservationAngerReplayMapping] = None
    anger_basis: Optional[ObservedAngerBasis] = None

    def __post_init__(self) -> None:
        if (self.anger is None) != (self.anger_basis is None):
            raise ValueError("anger replay mapping and anger_basis must be supplied together")
        if (
            self.arrivals is None
            and self.checkout_durations is None
            and self.checkout_selection is None
            and self.checkout_pre_service_departures is None
            and self.staff_work_starts is None
            and self.staff_work_durations is None
            and self.staff_work_interruptions is None
            and self.anger is None
        ):
            raise ValueError("at least one observation replay seam must be selected")


@dataclass
class ComposedObservationReplayValidationResult:
    selection: ComposedObservationReplaySelection
    replay_config: MinimalRepresentativeDayScenarioConfig
    arrival_plan: Optional[ObservationArrivalReplayPlan]
    checkout_duration_plan: Optional[ObservationCheckoutDurationReplayPlan]
    checkout_selection_plan: Optional[ObservationCheckoutSelectionReplayPlan]
    checkout_pre_service_departure_plan: Optional[
        ObservationCheckoutPreServiceDepartureReplayPlan
    ]
    staff_work_start_plan: Optional[ObservationStaffWorkStartReplayPlan]
    staff_work_duration_plan: Optional[ObservationStaffWorkDurationReplayPlan]
    staff_work_interruption_plan: Optional[ObservationStaffWorkInterruptionReplayPlan]
    anger_plan: Optional[ObservationAngerReplayPlan]
    validation: EventComparedObservationBackedMinimalDayValidationResult


def validate_minimal_day_with_composed_observation_replay(
    config: MinimalRepresentativeDayScenarioConfig,
    timeline: GameplayObservationTimeline,
    coverage: ObservationDayCoverage,
    *,
    selection: ComposedObservationReplaySelection,
    metric_mapping: ObservationDayMetricMapping = ObservationDayMetricMapping(),
    identity_mapping: ObservationIdentityMapping = ObservationIdentityMapping(),
    export_options: SimulationObservationExportOptions = SimulationObservationExportOptions(),
) -> ComposedObservationReplayValidationResult:
    """Hold selected observed timings/selection fixed and compare one autonomous run."""

    if selection.arrivals is not None and identity_mapping.customer_ids:
        raise ValueError(
            "arrival replay preserves observed customer ids as runtime ids; "
            "customer identity mapping must be empty when arrivals are replayed"
        )

    replay_config = config
    arrival_plan: Optional[ObservationArrivalReplayPlan] = None
    if selection.arrivals is not None:
        arrival_adapter = ObservationArrivalReplayAdapter()
        arrival_plan = arrival_adapter.build_plan(
            timeline,
            coverage,
            mapping=selection.arrivals,
        )
        replay_config = arrival_adapter.apply_to_config(replay_config, arrival_plan)

    checkout_duration_plan: Optional[ObservationCheckoutDurationReplayPlan] = None
    checkout_duration_policy = None
    if selection.checkout_durations is not None:
        checkout_adapter = ObservationCheckoutDurationReplayAdapter()
        checkout_duration_plan = checkout_adapter.build_plan(
            timeline,
            coverage,
            mapping=selection.checkout_durations,
            identity_mapping=identity_mapping,
        )
        checkout_duration_policy = checkout_adapter.build_policy(checkout_duration_plan)

    checkout_selection_plan: Optional[ObservationCheckoutSelectionReplayPlan] = None
    checkout_selection_policy = None
    if selection.checkout_selection is not None:
        selection_adapter = ObservationCheckoutSelectionReplayAdapter()
        checkout_selection_plan = selection_adapter.build_plan(
            timeline,
            coverage,
            mapping=selection.checkout_selection,
            identity_mapping=identity_mapping,
        )
        checkout_selection_policy = selection_adapter.build_policy(checkout_selection_plan)

    checkout_pre_service_departure_plan: Optional[
        ObservationCheckoutPreServiceDepartureReplayPlan
    ] = None
    checkout_pre_service_departure_policy = None
    if selection.checkout_pre_service_departures is not None:
        departure_adapter = ObservationCheckoutPreServiceDepartureReplayAdapter()
        checkout_pre_service_departure_plan = departure_adapter.build_plan(
            timeline,
            coverage,
            mapping=selection.checkout_pre_service_departures,
            identity_mapping=identity_mapping,
        )
        checkout_pre_service_departure_policy = departure_adapter.build_policy(
            checkout_pre_service_departure_plan,
            break_room_target_id=replay_config.timing.break_room_target_id,
        )

    staff_work_start_plan: Optional[ObservationStaffWorkStartReplayPlan] = None
    staff_task_policy = None
    if selection.staff_work_starts is not None:
        start_adapter = ObservationStaffWorkStartReplayAdapter()
        staff_work_start_plan = start_adapter.build_plan(
            timeline,
            coverage,
            mapping=selection.staff_work_starts,
            identity_mapping=identity_mapping,
        )
        staff_task_policy = start_adapter.build_policy(staff_work_start_plan)

    staff_work_duration_plan: Optional[ObservationStaffWorkDurationReplayPlan] = None
    staff_work_completion_policy = None
    if selection.staff_work_durations is not None:
        work_adapter = ObservationStaffWorkDurationReplayAdapter()
        staff_work_duration_plan = work_adapter.build_plan(
            timeline,
            coverage,
            mapping=selection.staff_work_durations,
            identity_mapping=identity_mapping,
        )
        staff_work_completion_policy = work_adapter.build_policy(
            staff_work_duration_plan,
            replenish_up_to_quantity=replay_config.timing.replenish_up_to_quantity,
            replenish_stamina_cost=replay_config.timing.replenish_stamina_cost,
            clean_stamina_cost=replay_config.timing.clean_stamina_cost,
            break_room_target_id=replay_config.timing.break_room_target_id,
        )

    staff_work_interruption_plan: Optional[ObservationStaffWorkInterruptionReplayPlan] = None
    staff_work_interruption_policy = None
    if selection.staff_work_interruptions is not None:
        interruption_adapter = ObservationStaffWorkInterruptionReplayAdapter()
        staff_work_interruption_plan = interruption_adapter.build_plan(
            timeline,
            coverage,
            mapping=selection.staff_work_interruptions,
            identity_mapping=identity_mapping,
        )
        staff_work_interruption_policy = interruption_adapter.build_policy(
            staff_work_interruption_plan
        )

    anger_plan: Optional[ObservationAngerReplayPlan] = None
    checkout_anger_policy = None
    if selection.anger is not None:
        assert selection.anger_basis is not None
        anger_adapter = ObservationAngerReplayAdapter()
        anger_plan = anger_adapter.build_plan(
            timeline,
            coverage,
            basis=selection.anger_basis,
            mapping=selection.anger,
            identity_mapping=identity_mapping,
        )
        checkout_anger_policy = anger_adapter.build_policy(anger_plan)

    validation = validate_minimal_day_with_event_comparison(
        replay_config,
        timeline,
        coverage,
        mapping=metric_mapping,
        identity_mapping=identity_mapping,
        checkout_anger_policy=checkout_anger_policy,
        checkout_duration_policy=checkout_duration_policy,
        checkout_selection_policy=checkout_selection_policy,
        checkout_pre_service_departure_policy=checkout_pre_service_departure_policy,
        staff_task_policy=staff_task_policy,
        staff_work_completion_policy=staff_work_completion_policy,
        staff_work_interruption_policy=staff_work_interruption_policy,
        export_options=export_options,
    )
    return ComposedObservationReplayValidationResult(
        selection=selection,
        replay_config=replay_config,
        arrival_plan=arrival_plan,
        checkout_duration_plan=checkout_duration_plan,
        checkout_selection_plan=checkout_selection_plan,
        checkout_pre_service_departure_plan=checkout_pre_service_departure_plan,
        staff_work_start_plan=staff_work_start_plan,
        staff_work_duration_plan=staff_work_duration_plan,
        staff_work_interruption_plan=staff_work_interruption_plan,
        anger_plan=anger_plan,
        validation=validation,
    )
