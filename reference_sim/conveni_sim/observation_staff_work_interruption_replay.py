from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass
from typing import Optional

from .observation_comparison import ObservationIdentityMapping
from .observation_day_adapter import ObservationDayCoverage
from .observations import GameplayObservation, GameplayObservationTimeline, ObservationKind
from .staff import StaffTask
from .staff_work_interruption import StaffWorkInterruptionContext, StaffWorkInterruptionPolicy


@dataclass(frozen=True)
class ObservationStaffWorkInterruptionReplayMapping:
    """Explicit permission to use work start->interrupt pairs as interruption timing."""

    staff_work_start_interrupt_pair_means_runtime_interruption: bool = False


@dataclass(frozen=True)
class ObservedStaffWorkInterruptionRule:
    staff_id: str
    task: StaffTask
    occurrence_index: int
    interrupt_after_game_minutes: int
    observed_fixture_id: Optional[str] = None

    def __post_init__(self) -> None:
        if not self.staff_id:
            raise ValueError("observed staff work interruption rule requires staff_id")
        if self.task not in (StaffTask.REPLENISH, StaffTask.CLEAN):
            raise ValueError("observed staff work interruption rule must be replenish/clean")
        if self.occurrence_index < 0:
            raise ValueError("occurrence_index must be >= 0")
        if self.interrupt_after_game_minutes < 0:
            raise ValueError("interrupt_after_game_minutes must be >= 0")


@dataclass(frozen=True)
class ObservationStaffWorkInterruptionReplayPlan:
    source_id: str
    coverage: ObservationDayCoverage
    rules: tuple[ObservedStaffWorkInterruptionRule, ...]
    unpaired_starts: tuple[GameplayObservation, ...]
    unpaired_interrupts: tuple[GameplayObservation, ...]


class ObservedStaffWorkInterruptionPolicy(StaffWorkInterruptionPolicy):
    """Replay only explicitly observed per-occurrence interruption timing.

    Occurrence indices count every observed/runtime assignment of the same
    staff/task family, including normally completed work. This allows, for
    example, occurrence 0 to finish normally and occurrence 1 to be interrupted
    without incorrectly applying the interruption rule to occurrence 0.

    The policy does not create checkout demand: the runtime interruption
    coordinator still requires a real waiting checkout customer before honoring
    True. Unobserved occurrences return None and remain unresolved.
    """

    def __init__(self, rules: tuple[ObservedStaffWorkInterruptionRule, ...]) -> None:
        self.rules = rules
        self._rule_by_occurrence: dict[
            tuple[str, StaffTask, int], ObservedStaffWorkInterruptionRule
        ] = {}
        for rule in rules:
            key = (rule.staff_id, rule.task, rule.occurrence_index)
            if key in self._rule_by_occurrence:
                raise ValueError(f"duplicate observed interruption occurrence: {key}")
            self._rule_by_occurrence[key] = rule
        self._next_occurrence: dict[tuple[str, StaffTask], int] = defaultdict(int)
        self._assignment_occurrence: dict[tuple[str, StaffTask, str, int], int] = {}

    def _rule_for(
        self,
        context: StaffWorkInterruptionContext,
    ) -> Optional[ObservedStaffWorkInterruptionRule]:
        work = context.work
        assignment_key = (
            work.staff_id,
            work.task,
            work.target_id,
            work.started_at_absolute_minute,
        )
        occurrence = self._assignment_occurrence.get(assignment_key)
        if occurrence is None:
            group_key = (work.staff_id, work.task)
            occurrence = self._next_occurrence[group_key]
            self._next_occurrence[group_key] = occurrence + 1
            self._assignment_occurrence[assignment_key] = occurrence
        return self._rule_by_occurrence.get((work.staff_id, work.task, occurrence))

    def should_interrupt(self, context: StaffWorkInterruptionContext) -> Optional[bool]:
        rule = self._rule_for(context)
        if rule is None:
            return None
        return context.work.elapsed_game_minutes >= rule.interrupt_after_game_minutes


class ObservationStaffWorkInterruptionReplayAdapter:
    """Build evidence-only interruption rules from explicit work episodes."""

    _KIND_TO_TASK = {
        ObservationKind.REPLENISH_START: StaffTask.REPLENISH,
        ObservationKind.CLEAN_START: StaffTask.CLEAN,
    }

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
    def _family(event: GameplayObservation) -> ObservationKind:
        if event.kind in (
            ObservationKind.REPLENISH_START,
            ObservationKind.REPLENISH_INTERRUPT,
            ObservationKind.REPLENISH_END,
        ):
            return ObservationKind.REPLENISH_START
        if event.kind in (
            ObservationKind.CLEAN_START,
            ObservationKind.CLEAN_INTERRUPT,
            ObservationKind.CLEAN_END,
        ):
            return ObservationKind.CLEAN_START
        raise ValueError("event is not a supported staff-work interruption observation")

    @classmethod
    def _raw_key(
        cls,
        event: GameplayObservation,
    ) -> tuple[str, ObservationKind, Optional[str]]:
        if event.staff_id is None:
            raise ValueError("staff work interruption replay requires explicit staff_id")
        return event.staff_id, cls._family(event), event.fixture_id

    def build_plan(
        self,
        timeline: GameplayObservationTimeline,
        coverage: ObservationDayCoverage,
        *,
        mapping: ObservationStaffWorkInterruptionReplayMapping = ObservationStaffWorkInterruptionReplayMapping(),
        identity_mapping: ObservationIdentityMapping = ObservationIdentityMapping(),
    ) -> ObservationStaffWorkInterruptionReplayPlan:
        if not mapping.staff_work_start_interrupt_pair_means_runtime_interruption:
            raise ValueError(
                "staff work interruption replay requires explicit "
                "staff_work_start_interrupt_pair_means_runtime_interruption=True"
            )
        supported = frozenset(
            (
                ObservationKind.REPLENISH_START,
                ObservationKind.REPLENISH_INTERRUPT,
                ObservationKind.REPLENISH_END,
                ObservationKind.CLEAN_START,
                ObservationKind.CLEAN_INTERRUPT,
                ObservationKind.CLEAN_END,
            )
        )
        events = tuple(
            event
            for event in timeline.events
            if self._in_coverage(event, coverage) and event.kind in supported
        )
        pending: dict[
            tuple[str, ObservationKind, Optional[str]], tuple[GameplayObservation, int]
        ] = {}
        unpaired_interrupts: list[GameplayObservation] = []
        rules: list[ObservedStaffWorkInterruptionRule] = []
        occurrence_counts: dict[tuple[str, StaffTask], int] = defaultdict(int)

        for event in events:
            raw_key = self._raw_key(event)
            family = raw_key[1]
            task = self._KIND_TO_TASK[family]
            normalized_staff = identity_mapping.staff(raw_key[0])
            assert normalized_staff is not None

            if event.kind is family:
                if raw_key in pending:
                    raise ValueError(
                        f"duplicate staff work start before terminal event inside coverage: {raw_key}"
                    )
                occurrence_key = (normalized_staff, task)
                occurrence_index = occurrence_counts[occurrence_key]
                occurrence_counts[occurrence_key] = occurrence_index + 1
                pending[raw_key] = (event, occurrence_index)
                continue

            start_pair = pending.pop(raw_key, None)
            is_interrupt = event.kind in (
                ObservationKind.REPLENISH_INTERRUPT,
                ObservationKind.CLEAN_INTERRUPT,
            )
            if start_pair is None:
                if is_interrupt:
                    unpaired_interrupts.append(event)
                # A normal END with its START outside coverage is not interruption
                # evidence and therefore needs no synthetic pairing.
                continue
            start, occurrence_index = start_pair
            if not is_interrupt:
                # Normal completion closes this observed occurrence so a later
                # start of the same staff/task/fixture is a new occurrence.
                continue

            normalized_fixture = identity_mapping.fixture(raw_key[2])
            rules.append(
                ObservedStaffWorkInterruptionRule(
                    staff_id=normalized_staff,
                    task=task,
                    occurrence_index=occurrence_index,
                    interrupt_after_game_minutes=start.game_time.minutes_until(event.game_time),
                    observed_fixture_id=normalized_fixture,
                )
            )

        return ObservationStaffWorkInterruptionReplayPlan(
            source_id=timeline.source_id,
            coverage=coverage,
            rules=tuple(rules),
            unpaired_starts=tuple(
                sorted(
                    (item[0] for item in pending.values()),
                    key=lambda item: (
                        item.game_time.representative_ordinal_minute,
                        item.sequence,
                    ),
                )
            ),
            unpaired_interrupts=tuple(unpaired_interrupts),
        )

    @staticmethod
    def build_policy(
        plan: ObservationStaffWorkInterruptionReplayPlan,
    ) -> ObservedStaffWorkInterruptionPolicy:
        return ObservedStaffWorkInterruptionPolicy(plan.rules)
