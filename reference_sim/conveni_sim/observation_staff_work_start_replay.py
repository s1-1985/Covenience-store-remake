from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from .observation_comparison import ObservationIdentityMapping
from .observation_day_adapter import ObservationDayCoverage
from .observations import GameplayObservation, GameplayObservationTimeline, ObservationKind
from .staff import StaffTask
from .staff_task_policy import StaffTaskDecision, StaffTaskDecisionContext, StaffTaskPolicy


@dataclass(frozen=True)
class ObservationStaffWorkStartReplayMapping:
    """Explicit semantic and target mapping for observed replenish/clean starts."""

    staff_work_start_means_runtime_assignment: bool = False
    replenish_fixture_targets: tuple[tuple[str, str], ...] = ()
    clean_note_targets: tuple[tuple[str, str], ...] = ()

    def __post_init__(self) -> None:
        for label, pairs in (
            ("replenish fixture", self.replenish_fixture_targets),
            ("clean note", self.clean_note_targets),
        ):
            observed = [item[0] for item in pairs]
            targets = [item[1] for item in pairs]
            if any(not value for value in (*observed, *targets)):
                raise ValueError(f"{label} target mappings require non-empty ids")
            if len(observed) != len(set(observed)):
                raise ValueError(f"duplicate observed {label} mapping")


@dataclass(frozen=True)
class ObservedStaffWorkStartRule:
    staff_id: str
    task: StaffTask
    minute_of_day: int
    target_id: str
    observed_sequence: int

    def __post_init__(self) -> None:
        if not self.staff_id or not self.target_id:
            raise ValueError("observed staff work start rule requires staff and target ids")
        if self.task not in (StaffTask.REPLENISH, StaffTask.CLEAN):
            raise ValueError("observed staff work start rule must be replenish/clean")
        if not 0 <= self.minute_of_day < 24 * 60:
            raise ValueError("minute_of_day must be 0..1439")
        if self.observed_sequence < 0:
            raise ValueError("observed_sequence must be >= 0")


@dataclass(frozen=True)
class ObservationStaffWorkStartReplayPlan:
    source_id: str
    coverage: ObservationDayCoverage
    rules: tuple[ObservedStaffWorkStartRule, ...]


class ObservedStaffWorkStartPolicy(StaffTaskPolicy):
    """Replay only explicitly observed replenish/clean assignments.

    The next observed rule for each staff member blocks unobserved task choices.
    A rule is never started before its observed minute. If its explicit runtime
    target is not currently a factual work candidate, the rule stays pending
    rather than falling back to a different target or task.
    """

    def __init__(self, rules: tuple[ObservedStaffWorkStartRule, ...]) -> None:
        grouped: dict[str, list[ObservedStaffWorkStartRule]] = {}
        for rule in rules:
            grouped.setdefault(rule.staff_id, []).append(rule)
        self._rules_by_staff = {
            staff_id: tuple(
                sorted(items, key=lambda item: (item.minute_of_day, item.observed_sequence))
            )
            for staff_id, items in grouped.items()
        }
        self._next_index: dict[str, int] = {}

    def choose_task(self, context: StaffTaskDecisionContext) -> Optional[StaffTaskDecision]:
        if context.current_minute_of_day is None:
            raise ValueError("observed staff work replay requires current_minute_of_day")
        rules = self._rules_by_staff.get(context.staff_id, ())
        index = self._next_index.get(context.staff_id, 0)
        if index >= len(rules):
            return None
        rule = rules[index]
        if context.current_minute_of_day < rule.minute_of_day:
            return None
        if not any(
            candidate.task is rule.task and candidate.target_id == rule.target_id
            for candidate in context.candidates
        ):
            return None
        self._next_index[context.staff_id] = index + 1
        return StaffTaskDecision(rule.task, target_id=rule.target_id)


class ObservationStaffWorkStartReplayAdapter:
    """Translate explicit observed work starts into strict assignment rules."""

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
    def _lookup(value: str, pairs: tuple[tuple[str, str], ...], label: str) -> str:
        for observed, target in pairs:
            if observed == value:
                return target
        raise ValueError(f"no explicit runtime target mapping for observed {label}: {value}")

    def build_plan(
        self,
        timeline: GameplayObservationTimeline,
        coverage: ObservationDayCoverage,
        *,
        mapping: ObservationStaffWorkStartReplayMapping = ObservationStaffWorkStartReplayMapping(),
        identity_mapping: ObservationIdentityMapping = ObservationIdentityMapping(),
    ) -> ObservationStaffWorkStartReplayPlan:
        if not mapping.staff_work_start_means_runtime_assignment:
            raise ValueError(
                "staff work start replay requires explicit "
                "staff_work_start_means_runtime_assignment=True"
            )
        rules: list[ObservedStaffWorkStartRule] = []
        for event in timeline.events:
            if not self._in_coverage(event, coverage):
                continue
            if event.kind not in (ObservationKind.REPLENISH_START, ObservationKind.CLEAN_START):
                continue
            if event.staff_id is None:
                raise ValueError("staff work start replay requires explicit staff_id")
            staff_id = identity_mapping.staff(event.staff_id)
            assert staff_id is not None
            if event.kind is ObservationKind.REPLENISH_START:
                if event.fixture_id is None:
                    raise ValueError("replenish start replay requires explicit fixture_id")
                fixture_id = identity_mapping.fixture(event.fixture_id)
                assert fixture_id is not None
                target_id = self._lookup(
                    fixture_id,
                    mapping.replenish_fixture_targets,
                    "replenish fixture",
                )
                task = StaffTask.REPLENISH
            else:
                if not event.note:
                    raise ValueError("clean start replay requires an explicit target note")
                target_id = self._lookup(event.note, mapping.clean_note_targets, "clean note")
                task = StaffTask.CLEAN
            rules.append(
                ObservedStaffWorkStartRule(
                    staff_id=staff_id,
                    task=task,
                    minute_of_day=event.game_time.minute_of_day,
                    target_id=target_id,
                    observed_sequence=event.sequence,
                )
            )
        return ObservationStaffWorkStartReplayPlan(
            source_id=timeline.source_id,
            coverage=coverage,
            rules=tuple(rules),
        )

    @staticmethod
    def build_policy(plan: ObservationStaffWorkStartReplayPlan) -> ObservedStaffWorkStartPolicy:
        return ObservedStaffWorkStartPolicy(plan.rules)
