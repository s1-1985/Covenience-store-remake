from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from .checkout_anger_timing import CheckoutAngerTriggerPolicy
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
) -> MinimalRepresentativeDayValidationResult:
    """Build, run, measure and compare one parameter-driven representative day."""

    scenario = build_minimal_representative_day_scenario(
        config,
        checkout_anger_policy=checkout_anger_policy,
    )
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
) -> ObservationBackedMinimalDayValidationResult:
    """Bridge annotated observations directly into the autonomous-day loop.

    Coverage and semantic mapping remain explicit. Partial observations therefore
    produce only window summaries and an empty/sparse full-day target set rather
    than being extrapolated to a complete day.
    """

    observation = ObservationDayMetricAdapter().reduce(
        timeline,
        coverage,
        mapping=mapping,
    )
    validation = validate_minimal_representative_day(
        config,
        observation.comparison_targets,
        checkout_anger_policy=checkout_anger_policy,
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
    export_options: SimulationObservationExportOptions = SimulationObservationExportOptions(),
) -> EventComparedObservationBackedMinimalDayValidationResult:
    """Run metric and event-level validation without inventing correspondence.

    The observed timeline is first reduced through the existing coverage-aware
    metric adapter. The same scenario run is then exported back into the shared
    observation vocabulary and compared only inside the supplied coverage.
    Different observed/simulated entity ids require `identity_mapping`; no
    nearest-time or nearest-entity matching is attempted.
    """

    observation = ObservationDayMetricAdapter().reduce(
        timeline,
        coverage,
        mapping=mapping,
    )
    validation = validate_minimal_representative_day(
        config,
        observation.comparison_targets,
        checkout_anger_policy=checkout_anger_policy,
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
