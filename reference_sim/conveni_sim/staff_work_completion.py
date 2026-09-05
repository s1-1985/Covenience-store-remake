from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from .cleaning import CleaningActionResult
from .staff import StaffCondition, StaffTask
from .staff_work_candidates import StaffWorkCandidateDiscovery
from .store_grid import GridPoint
from .store_runtime import ReplenishAndChargeResult, StoreRuntimeHarness


@dataclass(frozen=True)
class ReplenishmentCompletionCommand:
    quantity: int
    stamina_cost: Optional[int] = None
    break_room_target_id: Optional[str] = None

    def __post_init__(self) -> None:
        if self.quantity <= 0:
            raise ValueError("replenishment quantity must be > 0")
        if self.stamina_cost is not None and self.stamina_cost < 0:
            raise ValueError("stamina_cost must be >= 0 or None")


@dataclass(frozen=True)
class CleaningCompletionCommand:
    stamina_cost: Optional[int] = None
    break_room_target_id: Optional[str] = None

    def __post_init__(self) -> None:
        if self.stamina_cost is not None and self.stamina_cost < 0:
            raise ValueError("stamina_cost must be >= 0 or None")


@dataclass(frozen=True)
class StaffWorkCompletionResult:
    staff_id: str
    task: StaffTask
    target_id: str
    replenishment: Optional[ReplenishAndChargeResult] = None
    cleaning: Optional[CleaningActionResult] = None


class StaffWorkCompletionCoordinator:
    """Complete an already-assigned non-checkout task only when explicitly told.

    Task choice and completion remain separate because the first-title work
    duration, replenishment amount, stamina cost and movement timing are not yet
    recovered. Checkout uses its own service-start/service-finish lifecycle.
    """

    def __init__(self, runtime: StoreRuntimeHarness) -> None:
        self.runtime = runtime

    @staticmethod
    def _cleaning_cell(target_id: str) -> GridPoint:
        prefix = StaffWorkCandidateDiscovery.CLEAN_TARGET_PREFIX
        if not target_id.startswith(prefix):
            raise ValueError("cleaning target is not a floor-cell target")
        payload = target_id[len(prefix) :]
        parts = payload.split(":")
        if len(parts) != 2:
            raise ValueError("invalid cleaning target id")
        try:
            x, y = (int(part) for part in parts)
        except ValueError as exc:
            raise ValueError("invalid cleaning target id") from exc
        return GridPoint(x, y)

    def _assigned_state(self, staff_id: str, expected_task: StaffTask):
        state = self.runtime.staff.staff_member(staff_id)
        if state.condition is not StaffCondition.AVAILABLE:
            raise ValueError("staff member is not available to complete work")
        if state.task is not expected_task:
            raise ValueError(f"staff member is not assigned to {expected_task.value}")
        if state.target_id is None:
            raise ValueError("assigned work has no target")
        return state

    def complete_replenishment(
        self,
        staff_id: str,
        command: ReplenishmentCompletionCommand,
    ) -> StaffWorkCompletionResult:
        state = self._assigned_state(staff_id, StaffTask.REPLENISH)
        target_id = state.target_id
        slot = self.runtime.inventory.slot(target_id)
        if command.quantity > slot.free_capacity:
            raise ValueError("replenishment quantity exceeds current free capacity")

        result = self.runtime.replenish_and_charge(
            target_id,
            command.quantity,
            staff_id=staff_id,
            stamina_cost=command.stamina_cost,
            break_room_target_id=command.break_room_target_id,
        )
        self.runtime.staff.release_to_idle(staff_id)
        return StaffWorkCompletionResult(
            staff_id=staff_id,
            task=StaffTask.REPLENISH,
            target_id=target_id,
            replenishment=result,
        )

    def complete_cleaning(
        self,
        staff_id: str,
        command: CleaningCompletionCommand = CleaningCompletionCommand(),
    ) -> StaffWorkCompletionResult:
        state = self._assigned_state(staff_id, StaffTask.CLEAN)
        target_id = state.target_id
        cell = self._cleaning_cell(target_id)
        if cell not in self.runtime.cleaning.dirty_cells:
            raise ValueError("assigned cleaning target is no longer dirty")

        result = self.runtime.cleaning.clean(
            (cell,),
            staff_roster=self.runtime.staff,
            staff_id=staff_id,
            stamina_cost=command.stamina_cost,
            break_room_target_id=command.break_room_target_id,
        )
        self.runtime.staff.release_to_idle(staff_id)
        return StaffWorkCompletionResult(
            staff_id=staff_id,
            task=StaffTask.CLEAN,
            target_id=target_id,
            cleaning=result,
        )
