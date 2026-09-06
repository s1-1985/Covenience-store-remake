from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Mapping, Optional


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


class StaffSkill(str, Enum):
    EDUCATION = "education"
    REGISTER = "register"
    REPLENISHMENT = "replenishment"
    SECURITY = "security"
    CLEANING = "cleaning"
    SERVICE = "service"


WORK_TASKS = frozenset({StaffTask.CHECKOUT, StaffTask.REPLENISH, StaffTask.CLEAN})
WORK_GROWTH_SKILL = {
    StaffTask.CHECKOUT: StaffSkill.REGISTER,
    StaffTask.REPLENISH: StaffSkill.REPLENISHMENT,
    StaffTask.CLEAN: StaffSkill.CLEANING,
}


@dataclass
class StaffGrowthOpportunity:
    """One confirmed work-growth trigger with unresolved gain semantics."""

    sequence: int
    staff_id: str
    task: StaffTask
    skill: StaffSkill
    work_event_count: int
    before_value: Optional[int]
    base_cap: Optional[int]
    manager_staff_id: Optional[str]
    manager_education: Optional[int]
    resolved_after: Optional[int] = None

    @property
    def resolved(self) -> bool:
        return self.resolved_after is not None


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
    runtime_skills: dict[StaffSkill, int] = field(default_factory=dict)
    base_skill_caps: dict[StaffSkill, int] = field(default_factory=dict)

    @property
    def stamina_tracking_enabled(self) -> bool:
        return self.stamina_max is not None

    def completed_count(self, task: StaffTask) -> int:
        return self.completed_work_events.get(task, 0)

    def skill_value(self, skill: StaffSkill) -> Optional[int]:
        return self.runtime_skills.get(skill)

    def skill_cap(self, skill: StaffSkill) -> Optional[int]:
        return self.base_skill_caps.get(skill)


class StoreStaffRoster:
    """Minimal staff runtime/assignment surface for one store."""

    def __init__(self, *, max_staff: int = FIRST_TITLE_MAX_STAFF_PER_STORE) -> None:
        if max_staff < 1:
            raise ValueError("max_staff must be >= 1")
        self.max_staff = max_staff
        self._staff: dict[str, StaffRuntimeState] = {}
        self._manager_staff_id: Optional[str] = None
        self._growth_opportunities: list[StaffGrowthOpportunity] = []
        self._next_growth_sequence = 1

    @property
    def staff(self) -> tuple[StaffRuntimeState, ...]:
        return tuple(self._staff.values())

    @property
    def manager_staff_id(self) -> Optional[str]:
        return self._manager_staff_id

    @property
    def growth_opportunities(self) -> tuple[StaffGrowthOpportunity, ...]:
        return tuple(self._growth_opportunities)

    @property
    def unresolved_growth_opportunities(self) -> tuple[StaffGrowthOpportunity, ...]:
        return tuple(opportunity for opportunity in self._growth_opportunities if not opportunity.resolved)

    def staff_member(self, staff_id: str) -> StaffRuntimeState:
        return self._staff[staff_id]

    def growth_opportunity(self, sequence: int) -> StaffGrowthOpportunity:
        for opportunity in self._growth_opportunities:
            if opportunity.sequence == sequence:
                return opportunity
        raise KeyError(f"unknown growth opportunity sequence: {sequence}")

    @staticmethod
    def _validated_skill_mapping(
        values: Optional[Mapping[StaffSkill, int]],
        *,
        label: str,
    ) -> dict[StaffSkill, int]:
        result: dict[StaffSkill, int] = {}
        for skill, value in (values or {}).items():
            if not isinstance(skill, StaffSkill):
                raise TypeError(f"{label} keys must be StaffSkill")
            if value < 0:
                raise ValueError(f"{label} values must be >= 0")
            result[skill] = value
        return result

    def add_staff(
        self,
        staff_id: str,
        *,
        manager: bool = False,
        stamina_max: Optional[int] = None,
        runtime_skills: Optional[Mapping[StaffSkill, int]] = None,
        base_skill_caps: Optional[Mapping[StaffSkill, int]] = None,
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
            runtime_skills=self._validated_skill_mapping(runtime_skills, label="runtime_skills"),
            base_skill_caps=self._validated_skill_mapping(base_skill_caps, label="base_skill_caps"),
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

    def begin_break_room_return(
        self,
        staff_id: str,
        *,
        break_room_target_id: Optional[str] = None,
    ) -> StaffRuntimeState:
        """Begin an explicitly requested break-room return without changing stamina.

        Stamina exhaustion is one confirmed reason for this transition, but
        first-title observations also report checkout-assignment conflict losers
        returning to the break room. This method expresses the transition only;
        it does not claim a stamina cause, recovery duration, or recovery amount.
        """
        state = self._staff[staff_id]
        if state.condition is not StaffCondition.AVAILABLE:
            raise ValueError("staff member is not available to begin break-room return")
        changed = (
            state.condition is not StaffCondition.RETURNING_TO_BREAK_ROOM
            or state.task is not StaffTask.RETURN_TO_BREAK_ROOM
            or state.target_id != break_room_target_id
        )
        state.condition = StaffCondition.RETURNING_TO_BREAK_ROOM
        state.task = StaffTask.RETURN_TO_BREAK_ROOM
        state.target_id = break_room_target_id
        if changed:
            state.task_switch_count += 1
        return state

    def _record_growth_opportunity(
        self,
        staff_id: str,
        task: StaffTask,
        *,
        work_event_count: int,
    ) -> StaffGrowthOpportunity:
        skill = WORK_GROWTH_SKILL[task]
        state = self._staff[staff_id]
        manager_staff_id = self._manager_staff_id
        if manager_staff_id == staff_id:
            manager_staff_id = None
        manager_education: Optional[int] = None
        if manager_staff_id is not None:
            manager_education = self._staff[manager_staff_id].skill_value(StaffSkill.EDUCATION)
        opportunity = StaffGrowthOpportunity(
            sequence=self._next_growth_sequence,
            staff_id=staff_id,
            task=task,
            skill=skill,
            work_event_count=work_event_count,
            before_value=state.skill_value(skill),
            base_cap=state.skill_cap(skill),
            manager_staff_id=manager_staff_id,
            manager_education=manager_education,
        )
        self._next_growth_sequence += 1
        self._growth_opportunities.append(opportunity)
        return opportunity

    def record_completed_work(
        self,
        staff_id: str,
        task: StaffTask,
        *,
        stamina_cost: Optional[int] = None,
        break_room_target_id: Optional[str] = None,
    ) -> StaffRuntimeState:
        if task not in WORK_TASKS:
            raise ValueError("only checkout/replenish/clean are work events")
        state = self._staff[staff_id]
        work_event_count = state.completed_count(task) + 1
        state.completed_work_events[task] = work_event_count
        self._record_growth_opportunity(
            staff_id,
            task,
            work_event_count=work_event_count,
        )
        if stamina_cost is not None:
            self.consume_stamina(
                staff_id,
                stamina_cost,
                break_room_target_id=break_room_target_id,
            )
        return state

    def resolve_growth_opportunity(
        self,
        sequence: int,
        *,
        after_value: int,
    ) -> StaffGrowthOpportunity:
        if after_value < 0:
            raise ValueError("after_value must be >= 0")
        opportunity = self.growth_opportunity(sequence)
        if opportunity.resolved:
            raise ValueError("growth opportunity is already resolved")
        if opportunity.before_value is not None and after_value < opportunity.before_value:
            raise ValueError("work growth cannot reduce the corresponding skill")
        if opportunity.base_cap is not None and after_value > opportunity.base_cap:
            raise ValueError("normal work growth cannot exceed the known base skill cap")
        state = self._staff[opportunity.staff_id]
        state.runtime_skills[opportunity.skill] = after_value
        opportunity.resolved_after = after_value
        return opportunity

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
