from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Optional


FIRST_TITLE_MAX_STAFF_PER_STORE = 3


class StaffTask(str, Enum):
    IDLE = "idle"
    CHECKOUT = "checkout"
    REPLENISH = "replenish"
    CLEAN = "clean"
    REST = "rest"


@dataclass
class StaffRuntimeState:
    id: str
    task: StaffTask = StaffTask.IDLE
    target_id: Optional[str] = None
    task_switch_count: int = 0


class StoreStaffRoster:
    """Minimal staff runtime/assignment surface for one store.

    The first-title evidence supports at most three assigned staff and explicit
    runtime work such as checkout, replenishment, cleaning and resting. Exact
    autonomous task priority, travel behavior, stamina consumption/recovery and
    task durations are deliberately not implemented here.
    """

    def __init__(self, *, max_staff: int = FIRST_TITLE_MAX_STAFF_PER_STORE) -> None:
        if max_staff < 1:
            raise ValueError("max_staff must be >= 1")
        self.max_staff = max_staff
        self._staff: dict[str, StaffRuntimeState] = {}
        self._manager_staff_id: Optional[str] = None

    @property
    def staff(self) -> tuple[StaffRuntimeState, ...]:
        return tuple(self._staff.values())

    @property
    def manager_staff_id(self) -> Optional[str]:
        return self._manager_staff_id

    def staff_member(self, staff_id: str) -> StaffRuntimeState:
        return self._staff[staff_id]

    def add_staff(self, staff_id: str, *, manager: bool = False) -> StaffRuntimeState:
        if staff_id in self._staff:
            raise ValueError(f"duplicate staff id: {staff_id}")
        if len(self._staff) >= self.max_staff:
            raise ValueError(f"store staff capacity exceeded: {self.max_staff}")
        state = StaffRuntimeState(staff_id)
        self._staff[staff_id] = state
        if manager:
            self.set_manager(staff_id)
        return state

    def remove_staff(self, staff_id: str) -> StaffRuntimeState:
        state = self._staff.pop(staff_id)
        if self._manager_staff_id == staff_id:
            self._manager_staff_id = None
        return state

    def set_manager(self, staff_id: Optional[str]) -> None:
        if staff_id is not None and staff_id not in self._staff:
            raise KeyError(f"unknown staff id: {staff_id}")
        self._manager_staff_id = staff_id

    def assign_task(
        self,
        staff_id: str,
        task: StaffTask,
        *,
        target_id: Optional[str] = None,
    ) -> StaffRuntimeState:
        state = self._staff[staff_id]
        changed = state.task is not task or state.target_id != target_id
        state.task = task
        state.target_id = target_id
        if changed:
            state.task_switch_count += 1
        return state

    def release_to_idle(self, staff_id: str) -> StaffRuntimeState:
        return self.assign_task(staff_id, StaffTask.IDLE, target_id=None)
