from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Optional


FIRST_TITLE_MAX_STAFF_PER_STORE = 3


class StaffTask(str, Enum):
    IDLE = "idle"
    CHECKOUT = "checkout"
    REPLENISH = "replenish"
    CLEAN = "clean"
    RETURN_TO_BREAK_ROOM = "return_to_break_room"
    REST = "rest"


class StaffCondition(str, Enum):
    AVAILABLE = "available"
    RETURNING_TO_BREAK_ROOM = "returning_to_break_room"
    RESTING = "resting"


WORK_TASKS = frozenset({StaffTask.CHECKOUT, StaffTask.REPLENISH, StaffTask.CLEAN})


@dataclass
class StaffRuntimeState:
    id: str
    task: StaffTask = StaffTask.IDLE
    target_id: Optional[str] = None
    task_switch_count: int = 0
    condition: StaffCondition = StaffCondition.AVAILABLE
    stamina_max: Optional[int] = None
    stamina_current: Optional[int] = None
    completed_work_events: dict[StaffTask, int] = field(default_factory=dict)

    @property
    def stamina_tracking_enabled(self) -> bool:
        return self.stamina_max is not None

    def completed_count(self, task: StaffTask) -> int:
        return self.completed_work_events.get(task, 0)


class StoreStaffRoster:
    """Minimal staff runtime/assignment surface for one store.

    The first-title evidence supports at most three assigned staff and explicit
    runtime work such as checkout, replenishment, cleaning and resting. Exact
    autonomous task priority, travel behavior, stamina consumption/recovery and
    task durations remain caller-supplied/unknown.
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

    def add_staff(
        self,
        staff_id: str,
        *,
        manager: bool = False,
        stamina_max: Optional[int] = None,
    ) -> StaffRuntimeState:
        if staff_id in self._staff:
            raise ValueError(f"duplicate staff id: {staff_id}")
        if len(self._staff) >= self.max_staff:
            raise ValueError(f"store staff capacity exceeded: {self.max_staff}")
        if stamina_max is not None and stamina_max < 0:
            raise ValueError("stamina_max must be >= 0 or None")
        state = StaffRuntimeState(
            staff_id,
            stamina_max=stamina_max,
            stamina_current=stamina_max,
        )
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
        if state.condition is not StaffCondition.AVAILABLE and task in WORK_TASKS:
            raise ValueError("staff member is not available for work")
        changed = state.task is not task or state.target_id != target_id
        state.task = task
        state.target_id = target_id
        if changed:
            state.task_switch_count += 1
        return state

    def release_to_idle(self, staff_id: str) -> StaffRuntimeState:
        state = self._staff[staff_id]
        if state.condition is StaffCondition.AVAILABLE:
            return self.assign_task(staff_id, StaffTask.IDLE, target_id=None)
        state.target_id = None
        return state

    def record_completed_work(
        self,
        staff_id: str,
        task: StaffTask,
        *,
        stamina_cost: Optional[int] = None,
        break_room_target_id: Optional[str] = None,
    ) -> StaffRuntimeState:
        """Record a work event without inventing a default stamina cost.

        Work-event counts can later drive evidence-backed skill growth. If a
        caller supplies a stamina cost, the known `stamina -> 0 -> break room`
        transition is applied; otherwise stamina is left untouched.
        """
        if task not in WORK_TASKS:
            raise ValueError("only checkout/replenish/clean are work events")
        state = self._staff[staff_id]
        state.completed_work_events[task] = state.completed_count(task) + 1
        if stamina_cost is not None:
            self.consume_stamina(
                staff_id,
                stamina_cost,
                break_room_target_id=break_room_target_id,
            )
        return state

    def consume_stamina(
        self,
        staff_id: str,
        amount: int,
        *,
        break_room_target_id: Optional[str] = None,
    ) -> StaffRuntimeState:
        if amount < 0:
            raise ValueError("stamina consumption must be >= 0")
        state = self._staff[staff_id]
        if not state.stamina_tracking_enabled or state.stamina_current is None:
            raise ValueError("stamina value is unknown for this staff member")
        state.stamina_current = max(0, state.stamina_current - amount)
        if state.stamina_current == 0:
            state.condition = StaffCondition.RETURNING_TO_BREAK_ROOM
            state.task = StaffTask.RETURN_TO_BREAK_ROOM
            state.target_id = break_room_target_id
            state.task_switch_count += 1
        return state

    def arrive_at_break_room(
        self,
        staff_id: str,
        *,
        break_room_target_id: Optional[str] = None,
    ) -> StaffRuntimeState:
        state = self._staff[staff_id]
        if state.condition is not StaffCondition.RETURNING_TO_BREAK_ROOM:
            raise ValueError("staff member is not returning to the break room")
        state.condition = StaffCondition.RESTING
        state.task = StaffTask.REST
        if break_room_target_id is not None:
            state.target_id = break_room_target_id
        state.task_switch_count += 1
        return state

    def recover_stamina(self, staff_id: str, amount: int) -> StaffRuntimeState:
        if amount <= 0:
            raise ValueError("stamina recovery must be > 0")
        state = self._staff[staff_id]
        if state.condition is not StaffCondition.RESTING:
            raise ValueError("staff member is not resting")
        if not state.stamina_tracking_enabled or state.stamina_current is None or state.stamina_max is None:
            raise ValueError("stamina value is unknown for this staff member")
        state.stamina_current = min(state.stamina_max, state.stamina_current + amount)
        if state.stamina_current == state.stamina_max:
            state.condition = StaffCondition.AVAILABLE
            state.task = StaffTask.IDLE
            state.target_id = None
            state.task_switch_count += 1
        return state
