from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass
from typing import Optional

from .observation_comparison import ObservationIdentityMapping
from .observation_day_adapter import ObservationDayCoverage
from .observations import GameplayObservation, GameplayObservationTimeline, ObservationKind
from .staff import StaffTask
from .staff_work_timing import (
    StaffWorkCompletionDecision,
    StaffWorkCompletionPolicy,
    StaffWorkTimingContext,
)


@dataclass(frozen=True)
class ObservationStaffWorkDurationReplayMapping:
    """Explicit permission to use observed work start/end pairs as durations."""

    staff_work_pair_means_runtime_duration: bool = False


@dataclass(frozen=True)
class ObservedStaffWorkDurationRule:
    staff_id: str
    task: StaffTask
    occurrence_index: int
    required_game_minutes: int
    observed_fixture_id: Optional[str] = None
    observed_start_minute_of_day: Optional[int] = None

    def __post_init__(self) -> None:
        if not self.staff_id:
            raise ValueError("observed staff work duration rule requires staff_id")
        if self.task not in (StaffTask.REPLENISH, StaffTask.CLEAN):
            raise ValueError("observed staff work duration rule must be replenish/clean")
        if self.occurrence_index < 0:
            raise ValueError("occurrence_index must be >= 0")
        if self.required_game_minutes < 0:
            raise ValueError("required_game_minutes must be >= 0")


@dataclass(frozen=True)
class ObservationStaffWorkDurationReplayPlan:
    source_id: str
    coverage: ObservationDayCoverage
    rules: tuple[ObservedStaffWorkDurationRule, ...]
    unpaired_starts: tuple[GameplayObservation, ...]
    unpaired_ends: tuple[GameplayObservation, ...]


class ObservedStaffWorkDurationPolicy(StaffWorkCompletionPolicy):
    """Gate work completion by observed durations while keeping effects explicit.

    Rules are consumed chronologically per staff/task occurrence. Target choice is
    deliberately not inferred here. Replenishment quantity and stamina effects
    remain caller-supplied scenario inputs rather than observation-derived values.
    """

    def __init__(
        self,
        rules: tuple[ObservedStaffWorkDurationRule, ...],
        *,
        replenish_up_to_quantity: int,
        replenish_stamina_cost: Optional[int],
        clean_stamina_cost: Optional[int],
        break_room_target_id: Optional[str],
    ) -> None:
        if replenish_up_to_quantity <= 0:
            raise ValueError("replenish_up_to_quantity must be > 0")
        for value in (replenish_stamina_cost, clean_stamina_cost):
            if value is not None and value < 0:
                raise ValueError("stamina costs must be >= 0 or None")
        self.rules = rules
        self.replenish_up_to_quantity = replenish_up_to_quantity
        self.replenish_stamina_cost = replenish_stamina_cost
        self.clean_stamina_cost = clean_stamina_cost
        self.break_room_target_id = break_room_target_id
        self._rules_by_staff_task: dict[
            tuple[str, StaffTask], tuple[ObservedStaffWorkDurationRule, ...]
        ] = {}
        grouped: dict[tuple[str, StaffTask], list[ObservedStaffWorkDurationRule]] = defaultdict(list)
        for rule in rules:
            grouped[(rule.staff_id, rule.task)].append(rule)
        for key, items in grouped.items():
            ordered = tuple(sorted(items, key=lambda item: item.occurrence_index))
            expected = tuple(range(len(ordered)))
            actual = tuple(item.occurrence_index for item in ordered)
            if actual != expected:
                raise ValueError(f"observed staff work occurrence indices must be contiguous for {key}")
            self._rules_by_staff_task[key] = ordered
        self._assignment_rule: dict[
            tuple[str, StaffTask, str, int], ObservedStaffWorkDurationRule
        ] = {}
        self._next_occurrence: dict[tuple[str, StaffTask], int] = defaultdict(int)

    def _rule_for(self, context: StaffWorkTimingContext) -> Optional[ObservedStaffWorkDurationRule]:
        assignment_key = (
            context.staff_id,
            context.task,
            context.target_id,
            context.started_at_absolute_minute,
        )
        existing = self._assignment_rule.get(assignment_key)
        if existing is not None:
            return existing
        group_key = (context.staff_id, context.task)
        rules = self._rules_by_staff_task.get(group_key, ())
        index = self._next_occurrence[group_key]
        if index >= len(rules):
            return None
        rule = rules[index]
        self._next_occurrence[group_key] = index + 1
        self._assignment_rule[assignment_key] = rule
        return rule

    def completion(self, context: StaffWorkTimingContext) -> Optional[StaffWorkCompletionDecision]:
        rule = self._rule_for(context)
        if rule is None or context.elapsed_game_minutes < rule.required_game_minutes:
            return None
        if context.task is StaffTask.REPLENISH:
            free = context.inventory_free_capacity or 0
            if free <= 0:
                return None
            return StaffWorkCompletionDecision(
                quantity=min(self.replenish_up_to_quantity, free),
                stamina_cost=self.replenish_stamina_cost,
                break_room_target_id=self.break_room_target_id,
            )
        return StaffWorkCompletionDecision(
            stamina_cost=self.clean_stamina_cost,
            break_room_target_id=self.break_room_target_id,
        )


class ObservationStaffWorkDurationReplayAdapter:
    """Build duration rules only from complete in-coverage replenish/clean pairs."""

    _START_TO_END = {
        ObservationKind.REPLENISH_START: ObservationKind.REPLENISH_END,
        ObservationKind.CLEAN_START: ObservationKind.CLEAN_END,
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
    def _pair_key(event: GameplayObservation) -> tuple[str, ObservationKind, Optional[str]]:
        if event.staff_id is None:
            raise ValueError("staff work duration replay requires explicit staff_id")
        if event.kind in (ObservationKind.REPLENISH_START, ObservationKind.REPLENISH_END):
            family = ObservationKind.REPLENISH_START
        elif event.kind in (ObservationKind.CLEAN_START, ObservationKind.CLEAN_END):
            family = ObservationKind.CLEAN_START
        else:
            raise ValueError("event is not a supported staff work observation")
        return event.staff_id, family, event.fixture_id

    def build_plan(
        self,
        timeline: GameplayObservationTimeline,
        coverage: ObservationDayCoverage,
        *,
        mapping: ObservationStaffWorkDurationReplayMapping = ObservationStaffWorkDurationReplayMapping(),
        identity_mapping: ObservationIdentityMapping = ObservationIdentityMapping(),
    ) -> ObservationStaffWorkDurationReplayPlan:
        if not mapping.staff_work_pair_means_runtime_duration:
            raise ValueError(
                "staff work duration replay requires explicit "
                "staff_work_pair_means_runtime_duration=True"
            )
        supported = frozenset(
            (
                ObservationKind.REPLENISH_START,
                ObservationKind.REPLENISH_END,
                ObservationKind.CLEAN_START,
                ObservationKind.CLEAN_END,
            )
        )
        events = tuple(
            event
            for event in timeline.events
            if self._in_coverage(event, coverage) and event.kind in supported
        )
        pending: dict[tuple[str, ObservationKind, Optional[str]], GameplayObservation] = {}
        unpaired_ends: list[GameplayObservation] = []
        rules: list[ObservedStaffWorkDurationRule] = []
        occurrence_counts: dict[tuple[str, StaffTask], int] = defaultdict(int)

        for event in events:
            raw_key = self._pair_key(event)
            family = raw_key[1]
            if event.kind is family:
                if raw_key in pending:
                    raise ValueError(f"duplicate staff work start without end inside coverage: {raw_key}")
                pending[raw_key] = event
                continue
            start = pending.pop(raw_key, None)
            if start is None:
                unpaired_ends.append(event)
                continue
            normalized_staff = identity_mapping.staff(raw_key[0])
            normalized_fixture = identity_mapping.fixture(raw_key[2])
            assert normalized_staff is not None
            task = self._KIND_TO_TASK[family]
            occurrence_key = (normalized_staff, task)
            occurrence_index = occurrence_counts[occurrence_key]
            occurrence_counts[occurrence_key] += 1
            rules.append(
                ObservedStaffWorkDurationRule(
                    staff_id=normalized_staff,
                    task=task,
                    occurrence_index=occurrence_index,
                    required_game_minutes=start.game_time.minutes_until(event.game_time),
                    observed_fixture_id=normalized_fixture,
                    observed_start_minute_of_day=start.game_time.minute_of_day,
                )
            )

        unpaired_starts = tuple(
            sorted(
                pending.values(),
                key=lambda item: (item.game_time.representative_ordinal_minute, item.sequence),
            )
        )
        return ObservationStaffWorkDurationReplayPlan(
            source_id=timeline.source_id,
            coverage=coverage,
            rules=tuple(rules),
            unpaired_starts=unpaired_starts,
            unpaired_ends=tuple(unpaired_ends),
        )

    @staticmethod
    def build_policy(
        plan: ObservationStaffWorkDurationReplayPlan,
        *,
        replenish_up_to_quantity: int,
        replenish_stamina_cost: Optional[int],
        clean_stamina_cost: Optional[int],
        break_room_target_id: Optional[str],
    ) -> ObservedStaffWorkDurationPolicy:
        return ObservedStaffWorkDurationPolicy(
            plan.rules,
            replenish_up_to_quantity=replenish_up_to_quantity,
            replenish_stamina_cost=replenish_stamina_cost,
            clean_stamina_cost=clean_stamina_cost,
            break_room_target_id=break_room_target_id,
        )
