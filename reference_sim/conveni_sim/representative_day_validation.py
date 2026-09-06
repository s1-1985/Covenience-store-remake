from __future__ import annotations

from dataclasses import dataclass

from .minimal_day_scenario import (
    MinimalRepresentativeDayScenario,
    MinimalRepresentativeDayScenarioConfig,
    build_minimal_representative_day_scenario,
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


def validate_minimal_representative_day(
    config: MinimalRepresentativeDayScenarioConfig,
    observed: ObservedRepresentativeDayMetrics,
) -> MinimalRepresentativeDayValidationResult:
    """Build, run, measure and compare one parameter-driven representative day."""

    scenario = build_minimal_representative_day_scenario(config)
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
    )
    return ObservationBackedMinimalDayValidationResult(
        observation=observation,
        validation=validation,
    )
