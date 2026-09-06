from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Optional, Protocol

from .cleaning import CleaningActionResult
from .staff import StaffCondition, StaffTask
from .store_grid import GridPoint
from .store_runtime import ReplenishAndChargeResult, StoreRuntimeHarness


TIMED_STAFF_WORK_TASKS = frozenset({StaffTask.REPLENISH, StaffTask.CLEAN})


@dataclass(frozen=True)
class StaffWorkTimingState:
    staff_id: str
    task: StaffTask
    target_id: str
    started_at_absolute_minute: int


@dataclass(frozen=True)
class StaffWorkTimingContext:
    staff_id: str
    task: StaffTask
    target_id: str
    started_at_absolute_minute: int
    current_absolute_minute: int
    elapsed_game_minutes: int
    stamina_current: Optional[int]
    stamina_max: Optional[int]
    inventory_units: Optional[int] = None
    inventory_capacity: Optional[int] = None
    inventory_free_capacity: Optional[int] = None
    unit_procurement_cost_yen: Optional[int] = None
    cleaning_cell: Optional[GridPoint] = None
    cleaning_cell_dirty: Optional[bool] = None

    @property
    def target_actionable(self) -> bool:
        if self.task is StaffTask.REPLENISH:
            return bool(self.inventory_free_capacity)
        if self.task is StaffTask.CLEAN:
            return self.cleaning_cell_dirty is True
        return False


@dataclass(frozen=True)
class StaffWorkCompletionDecision:
    """Explicit completion payload for unresolved replenish/clean work.

    Returning a decision means the supplied policy considers the work complete
    at the current game time. Replenishment requires an explicit quantity;
    cleaning must leave quantity as None. Stamina effects remain optional.
    """

    quantity: Optional[int] = None
    stamina_cost: Optional[int] = None
    break_room_target_id: Optional[str] = None

    def __post_init__(self) -> None:
        if self.quantity is not None and self.quantity <= 0:
            raise ValueError("quantity must be > 0 or None")
        if self.stamina_cost is not None and self.stamina_cost < 0:
            raise ValueError("stamina_cost must be >= 0 or None")


class StaffWorkCompletionPolicy(Protocol):
    """Replaceable completion policy for unresolved replenish/clean timing."""

    def completion(
        self,
        context: StaffWorkTimingContext,
    ) -> Optional[StaffWorkCompletionDecision]: ...


class StaffWorkTimingStatus(str, Enum):
    ACTIVE = "active"
    COMPLETED = "completed"
    TARGET_UNAVAILABLE = "target_unavailable"


@dataclass(frozen=True)
class StaffWorkCompletionResult:
    replenishment: Optional[ReplenishAndChargeResult] = None
    cleaning: Optional[CleaningActionResult] = None


@dataclass(frozen=True)
class StaffWorkTimingEvaluation:
    context: StaffWorkTimingContext
    status: StaffWorkTimingStatus
    decision: Optional[StaffWorkCompletionDecision] = None
    completion: Optional[StaffWorkCompletionResult] = None

    @property
    def completed(self) -> bool:
        return self.status is StaffWorkTimingStatus.COMPLETED


class StaffWorkTimingCoordinator:
    """Track replenish/clean work without inventing duration or quantity rules.

    A work assignment is registered after the generic staff policy assigns
    REPLENISH or CLEAN. A supplied completion policy can inspect elapsed in-game
    minutes and factual target state. Returning None keeps the work active.
    Returning a decision performs the already-existing inventory/cleaning action.

    If another staff member makes the target no longer actionable first, the
    stale assignment is released without recording a completed work event.
    """

    CLEAN_TARGET_PREFIX = "floor:"

    def __init__(self, runtime: StoreRuntimeHarness) -> None:
        self.runtime = runtime
        self._active: dict[str, StaffWorkTimingState] = {}

    @property
    def active_states(self) -> tuple[StaffWorkTimingState, ...]:
        return tuple(self._active.values())

    @property
    def active_staff_ids(self) -> tuple[str, ...]:
        return tuple(self._active)

    @classmethod
    def _cleaning_cell(cls, target_id: str) -> GridPoint:
        parts = target_id.split(":")
        if len(parts) != 3 or parts[0] != cls.CLEAN_TARGET_PREFIX[:-1]:
            raise ValueError(f"invalid cleaning target id: {target_id}")
        try:
            return GridPoint(int(parts[1]), int(parts[2]))
        except ValueError as exc:
            raise ValueError(f"invalid cleaning target id: {target_id}") from exc

    def register_assigned(
        self,
        staff_id: str,
        *,
        started_at_absolute_minute: Optional[int] = None,
    ) -> StaffWorkTimingState:
        if staff_id in self._active:
            raise ValueError("staff member already has registered non-checkout work")
        staff = self.runtime.staff.staff_member(staff_id)
        if staff.task not in TIMED_STAFF_WORK_TASKS or staff.target_id is None:
            raise ValueError("staff member is not assigned to replenish/clean work")
        start = (
            self.runtime.subday_clock.absolute_minutes
            if started_at_absolute_minute is None
            else started_at_absolute_minute
        )
        if start < 0:
            raise ValueError("started_at_absolute_minute must be >= 0")
        if start > self.runtime.subday_clock.absolute_minutes:
            raise ValueError("staff work cannot start in the future")
        state = StaffWorkTimingState(
            staff_id=staff_id,
            task=staff.task,
            target_id=staff.target_id,
            started_at_absolute_minute=start,
        )
        self._active[staff_id] = state
        return state

    def unregister_staff(self, staff_id: str) -> Optional[StaffWorkTimingState]:
        return self._active.pop(staff_id, None)

    def current_context(self, staff_id: str) -> StaffWorkTimingContext:
        state = self._active[staff_id]
        staff = self.runtime.staff.staff_member(staff_id)
        if staff.task is not state.task or staff.target_id != state.target_id:
            raise ValueError("registered staff work is no longer the current assignment")
        current = self.runtime.subday_clock.absolute_minutes
        if current < state.started_at_absolute_minute:
            raise ValueError("runtime clock moved before staff work start")

        common = dict(
            staff_id=staff_id,
            task=state.task,
            target_id=state.target_id,
            started_at_absolute_minute=state.started_at_absolute_minute,
            current_absolute_minute=current,
            elapsed_game_minutes=current - state.started_at_absolute_minute,
            stamina_current=staff.stamina_current,
            stamina_max=staff.stamina_max,
        )
        if state.task is StaffTask.REPLENISH:
            slot = self.runtime.inventory.slot(state.target_id)
            return StaffWorkTimingContext(
                **common,
                inventory_units=slot.units,
                inventory_capacity=slot.capacity_units,
                inventory_free_capacity=slot.free_capacity,
                unit_procurement_cost_yen=slot.unit_procurement_cost_yen,
            )

        cell = self._cleaning_cell(state.target_id)
        return StaffWorkTimingContext(
            **common,
            cleaning_cell=cell,
            cleaning_cell_dirty=cell in self.runtime.cleaning.dirty_cells,
        )

    def _release_if_still_assigned(self, state: StaffWorkTimingState) -> None:
        staff = self.runtime.staff.staff_member(state.staff_id)
        if (
            staff.condition is StaffCondition.AVAILABLE
            and staff.task is state.task
            and staff.target_id == state.target_id
        ):
            self.runtime.staff.release_to_idle(state.staff_id)

    def evaluate_staff(
        self,
        staff_id: str,
        policy: StaffWorkCompletionPolicy,
    ) -> StaffWorkTimingEvaluation:
        state = self._active[staff_id]
        context = self.current_context(staff_id)

        if not context.target_actionable:
            del self._active[staff_id]
            self._release_if_still_assigned(state)
            return StaffWorkTimingEvaluation(
                context=context,
                status=StaffWorkTimingStatus.TARGET_UNAVAILABLE,
            )

        decision = policy.completion(context)
        if decision is None:
            return StaffWorkTimingEvaluation(
                context=context,
                status=StaffWorkTimingStatus.ACTIVE,
            )

        if state.task is StaffTask.REPLENISH:
            if decision.quantity is None:
                raise ValueError("replenishment completion requires an explicit quantity")
            if (
                context.inventory_free_capacity is not None
                and decision.quantity > context.inventory_free_capacity
            ):
                raise ValueError("replenishment completion exceeds current free capacity")
            replenishment = self.runtime.replenish_and_charge(
                state.target_id,
                decision.quantity,
                staff_id=staff_id,
                stamina_cost=decision.stamina_cost,
                break_room_target_id=decision.break_room_target_id,
            )
            completion = StaffWorkCompletionResult(replenishment=replenishment)
        else:
            if decision.quantity is not None:
                raise ValueError("cleaning completion must not supply a quantity")
            assert context.cleaning_cell is not None
            cleaning = self.runtime.cleaning.clean(
                (context.cleaning_cell,),
                staff_roster=self.runtime.staff,
                staff_id=staff_id,
                stamina_cost=decision.stamina_cost,
                break_room_target_id=decision.break_room_target_id,
            )
            completion = StaffWorkCompletionResult(cleaning=cleaning)

        del self._active[staff_id]
        self._release_if_still_assigned(state)
        return StaffWorkTimingEvaluation(
            context=context,
            status=StaffWorkTimingStatus.COMPLETED,
            decision=decision,
            completion=completion,
        )

    def evaluate_all(
        self,
        policy: StaffWorkCompletionPolicy,
    ) -> tuple[StaffWorkTimingEvaluation, ...]:
        # Snapshot ids because completion and stale-target cleanup mutate `_active`.
        return tuple(
            self.evaluate_staff(staff_id, policy)
            for staff_id in tuple(self._active)
        )
