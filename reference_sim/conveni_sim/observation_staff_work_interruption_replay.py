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

    A rule is bound when an active staff/task assignment is first evaluated. The
    policy does not create checkout demand: the runtime interruption coordinator
    still requires a real waiting checkout customer before honoring True.
    Unobserved active work returns None and remains unresolved.
    """

    def __init__(self, rules: tuple[ObservedStaffWorkInterruptionRule, ...]) -> None:
        grouped: dict[tuple[str, StaffTask], list[ObservedStaffWorkInterruptionRule]] = defaultdict(list)
        for rule in rules:
            grouped[(rule.staff_id, rule.task)].append(rule)
        self._rules_by_staff_task: dict[
            tuple[str, StaffTask], tuple[ObservedStaffWorkInterruptionRule, ...]
        ] = {}
        for key, items in grouped.items():
            ordered = tuple(sorted(items, key=lambda item: item.occurrence_index))
            actual = tuple(item.occurrence_index for item in ordered)
            if actual != tuple(range(len(ordered))):
                raise ValueError(f"observed interruption occurrence indices must be contiguous for {key}")
            self._rules_by_staff_task[key] = ordered
        self._next_occurrence: dict[tuple[str, StaffTask], int] = defaultdict(int)
        self._assignment_rule: dict[
            tuple[str, StaffTask, str, int], ObservedStaffWorkInterruptionRule
        ] = {}

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
        existing = self._assignment_rule.get(assignment_key)
        if existing is not None:
            return existing
        group_key = (work.staff_id, work.task)
        rules = self._rules_by_staff_task.get(group_key, ())
        index = self._next_occurrence[group_key]
        if index >= len(rules):
            return None
        rule = rules[index]
        self._next_occurrence[group_key] = index + 1
        self._assignment_rule[assignment_key] = rule
        return rule

    def should_interrupt(self, context: StaffWorkInterruptionContext) -> Optional[bool]:
        rule = self._rule_for(context)
        if rule is None:
            return None
        return context.work.elapsed_game_minutes >= rule.interrupt_after_game_minutes


class ObservationStaffWorkInterruptionReplayAdapter:
    """Build evidence-only interruption rules from explicit start/interrupt pairs."""

    _START_TO_INTERRUPT = {
        ObservationKind.REPLENISH_START: ObservationKind.REPLENISH_INTERRUPT,
        ObservationKind.CLEAN_START: ObservationKind.CLEAN_INTERRUPT,
    }
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
        if event.kind in (ObservationKind.REPLENISH_START, ObservationKind.REPLENISH_INTERRUPT):
            return ObservationKind.REPLENISH_START
        if event.kind in (ObservationKind.CLEAN_START, ObservationKind.CLEAN_INTERRUPT):
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
                ObservationKind.CLEAN_START,
                ObservationKind.CLEAN_INTERRUPT,
            )
        )
        events = tuple(
            event
            for event in timeline.events
            if self._in_coverage(event, coverage) and event.kind in supported
        )
        pending: dict[tuple[str, ObservationKind, Optional[str]], GameplayObservation] = {}
        unpaired_interrupts: list[GameplayObservation] = []
        rules: list[ObservedStaffWorkInterruptionRule] = []
        occurrence_counts: dict[tuple[str, StaffTask], int] = defaultdict(int)

        for event in events:
            raw_key = self._raw_key(event)
            family = raw_key[1]
            if event.kind is family:
                if raw_key in pending:
                    raise ValueError(
                        f"duplicate staff work start without interrupt inside coverage: {raw_key}"
                    )
                pending[raw_key] = event
                continue
            start = pending.pop(raw_key, None)
            if start is None:
                unpaired_interrupts.append(event)
                continue
            normalized_staff = identity_mapping.staff(raw_key[0])
            normalized_fixture = identity_mapping.fixture(raw_key[2])
            assert normalized_staff is not None
            task = self._KIND_TO_TASK[family]
            occurrence_key = (normalized_staff, task)
            occurrence_index = occurrence_counts[occurrence_key]
            occurrence_counts[occurrence_key] += 1
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
                    pending.values(),
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
