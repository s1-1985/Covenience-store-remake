from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from .checkout_anger_timing import CheckoutAngerTriggerPolicy
from .checkout_selection_policy import CheckoutCustomerSelectionPolicy
from .checkout_service_timing import CheckoutServiceDurationPolicy
from .minimal_day_scenario import (
    MinimalRepresentativeDayScenario,
    MinimalRepresentativeDayScenarioConfig,
    build_minimal_representative_day_scenario,
)
from .observation_comparison import (
    ObservationIdentityMapping,
    ObservationTimelineComparator,
    ObservationTimelineComparison,
)
from .observation_day_adapter import (
    ObservationDayCoverage,
    ObservationDayMetricAdapter,
    ObservationDayMetricMapping,
    ObservationDayMetricReduction,
)
from .observations import GameplayObservationTimeline
from .representative_day_metrics import (
    ObservedRepresentativeDayMetrics,
    RepresentativeDayComparison,
    RepresentativeDayMetrics,
    compare_representative_day_metrics,
    derive_representative_day_metrics,
)
from .representative_day_runner import RepresentativeDayRunResult
from .simulation_observations import (
    RepresentativeDayObservationExporter,
    SimulationObservationExportOptions,
)
from .staff_task_policy import StaffTaskPolicy
from .staff_work_timing import StaffWorkCompletionPolicy


@dataclass
class MinimalRepresentativeDayValidationResult:
    """One fully composed scenario run plus factual metrics and sparse comparison."""

    scenario: MinimalRepresentativeDayScenario
    run: RepresentativeDayRunResult
    metrics: RepresentativeDayMetrics
    comparison: RepresentativeDayComparison


@dataclass
class ObservationBackedMinimalDayValidationResult:
    """Validation result plus the explicit observation-window reduction used."""

    observation: ObservationDayMetricReduction
    validation: MinimalRepresentativeDayValidationResult


@dataclass
class EventComparedObservationBackedMinimalDayValidationResult:
    """Metric validation plus a same-vocabulary event-by-event comparison."""

    observation: ObservationDayMetricReduction
    validation: MinimalRepresentativeDayValidationResult
    simulated_timeline: GameplayObservationTimeline
    event_comparison: ObservationTimelineComparison


def validate_minimal_representative_day(
    config: MinimalRepresentativeDayScenarioConfig,
    observed: ObservedRepresentativeDayMetrics,
    *,
    checkout_anger_policy: Optional[CheckoutAngerTriggerPolicy] = None,
    checkout_duration_policy: Optional[CheckoutServiceDurationPolicy] = None,
    checkout_selection_policy: Optional[CheckoutCustomerSelectionPolicy] = None,
    staff_task_policy: Optional[StaffTaskPolicy] = None,
    staff_work_completion_policy: Optional[StaffWorkCompletionPolicy] = None,
) -> MinimalRepresentativeDayValidationResult:
    """Build, optionally override policies, run, measure and compare one day."""

    scenario = build_minimal_representative_day_scenario(
        config,
        checkout_anger_policy=checkout_anger_policy,
    )
    if checkout_duration_policy is not None:
        if scenario.orchestrator.checkout_timing is None:
            raise ValueError("checkout duration override requires checkout timing")
        scenario.orchestrator.checkout_duration_policy = checkout_duration_policy
    if checkout_selection_policy is not None:
        if scenario.orchestrator.checkout_policy is None:
            raise ValueError("checkout selection override requires checkout selection")
        scenario.orchestrator.checkout_policy = checkout_selection_policy
    if staff_task_policy is not None:
        if scenario.orchestrator.staff_policy is None:
            raise ValueError("staff task override requires staff task selection")
        scenario.orchestrator.staff_policy = staff_task_policy
    if staff_work_completion_policy is not None:
        if scenario.orchestrator.staff_work_timing is None:
            raise ValueError("staff work completion override requires staff work timing")
        scenario.orchestrator.staff_work_completion_policy = staff_work_completion_policy
    run = scenario.run()
    metrics = derive_representative_day_metrics(run)
    comparison = compare_representative_day_metrics(metrics, observed)
    return MinimalRepresentativeDayValidationResult(
        scenario=scenario,
        run=run,
        metrics=metrics,
        comparison=comparison,
    )


def validate_minimal_day_from_observation_timeline(
    config: MinimalRepresentativeDayScenarioConfig,
    timeline: GameplayObservationTimeline,
    coverage: ObservationDayCoverage,
    *,
    mapping: ObservationDayMetricMapping = ObservationDayMetricMapping(),
    checkout_anger_policy: Optional[CheckoutAngerTriggerPolicy] = None,
    checkout_duration_policy: Optional[CheckoutServiceDurationPolicy] = None,
    checkout_selection_policy: Optional[CheckoutCustomerSelectionPolicy] = None,
    staff_task_policy: Optional[StaffTaskPolicy] = None,
    staff_work_completion_policy: Optional[StaffWorkCompletionPolicy] = None,
) -> ObservationBackedMinimalDayValidationResult:
    """Bridge annotated observations directly into the autonomous-day loop."""

    observation = ObservationDayMetricAdapter().reduce(
        timeline,
        coverage,
        mapping=mapping,
    )
    validation = validate_minimal_representative_day(
        config,
        observation.comparison_targets,
        checkout_anger_policy=checkout_anger_policy,
        checkout_duration_policy=checkout_duration_policy,
        checkout_selection_policy=checkout_selection_policy,
        staff_task_policy=staff_task_policy,
        staff_work_completion_policy=staff_work_completion_policy,
    )
    return ObservationBackedMinimalDayValidationResult(
        observation=observation,
        validation=validation,
    )


def validate_minimal_day_with_event_comparison(
    config: MinimalRepresentativeDayScenarioConfig,
    timeline: GameplayObservationTimeline,
    coverage: ObservationDayCoverage,
    *,
    mapping: ObservationDayMetricMapping = ObservationDayMetricMapping(),
    identity_mapping: ObservationIdentityMapping = ObservationIdentityMapping(),
    checkout_anger_policy: Optional[CheckoutAngerTriggerPolicy] = None,
    checkout_duration_policy: Optional[CheckoutServiceDurationPolicy] = None,
    checkout_selection_policy: Optional[CheckoutCustomerSelectionPolicy] = None,
    staff_task_policy: Optional[StaffTaskPolicy] = None,
    staff_work_completion_policy: Optional[StaffWorkCompletionPolicy] = None,
    export_options: SimulationObservationExportOptions = SimulationObservationExportOptions(),
) -> EventComparedObservationBackedMinimalDayValidationResult:
    """Run metric and event-level validation without inventing correspondence."""

    observation = ObservationDayMetricAdapter().reduce(
        timeline,
        coverage,
        mapping=mapping,
    )
    validation = validate_minimal_representative_day(
        config,
        observation.comparison_targets,
        checkout_anger_policy=checkout_anger_policy,
        checkout_duration_policy=checkout_duration_policy,
        checkout_selection_policy=checkout_selection_policy,
        staff_task_policy=staff_task_policy,
        staff_work_completion_policy=staff_work_completion_policy,
    )
    simulated_timeline = RepresentativeDayObservationExporter().export(
        validation.run,
        validation.scenario.runtime,
        source_id="reference-simulation-validation",
        options=export_options,
    )
    event_comparison = ObservationTimelineComparator().compare(
        timeline,
        simulated_timeline,
        coverage,
        identity_mapping=identity_mapping,
    )
    return EventComparedObservationBackedMinimalDayValidationResult(
        observation=observation,
        validation=validation,
        simulated_timeline=simulated_timeline,
        event_comparison=event_comparison,
    )
