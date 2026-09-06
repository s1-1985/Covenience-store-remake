from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Optional, Protocol

from .staff import StaffCondition
from .store_runtime import StoreRuntimeHarness


REST_LIFECYCLE_CONDITIONS = frozenset(
    {StaffCondition.RETURNING_TO_BREAK_ROOM, StaffCondition.RESTING}
)


@dataclass(frozen=True)
class StaffRestTimingState:
    staff_id: str
    condition: StaffCondition
    started_at_absolute_minute: int
    break_room_target_id: Optional[str]


@dataclass(frozen=True)
class StaffRestTimingContext:
    staff_id: str
    condition: StaffCondition
    started_at_absolute_minute: int
    current_absolute_minute: int
    elapsed_game_minutes: int
    break_room_target_id: Optional[str]
    stamina_current: Optional[int]
    stamina_max: Optional[int]


@dataclass(frozen=True)
class StaffRestTransitionDecision:
    """Explicit transition payload for the unresolved rest lifecycle.

    RETURNING_TO_BREAK_ROOM accepts `arrive_at_break_room=True` only. RESTING
    accepts a positive `recovery_amount` only. Returning None from the policy
    keeps the current state active.
    """

    arrive_at_break_room: bool = False
    recovery_amount: Optional[int] = None

    def __post_init__(self) -> None:
        if self.recovery_amount is not None and self.recovery_amount <= 0:
            raise ValueError("recovery_amount must be > 0 or None")
        if self.arrive_at_break_room and self.recovery_amount is not None:
            raise ValueError("arrival and recovery must be separate transitions")


class StaffRestTransitionPolicy(Protocol):
    """Replaceable policy for unknown break-room travel/recovery timing."""

    def transition(
        self,
        context: StaffRestTimingContext,
    ) -> Optional[StaffRestTransitionDecision]: ...


class StaffRestTimingStatus(str, Enum):
    ACTIVE = "active"
    ARRIVED_AT_BREAK_ROOM = "arrived_at_break_room"
    RECOVERED = "recovered"
    RECOVERY_COMPLETE = "recovery_complete"


@dataclass(frozen=True)
class StaffRestTimingEvaluation:
    context: StaffRestTimingContext
    status: StaffRestTimingStatus
    decision: Optional[StaffRestTransitionDecision] = None
    stamina_after: Optional[int] = None


class StaffRestTimingCoordinator:
    """Advance confirmed stamina/rest states without inventing rate constants.

    The roster already owns the state machine. This coordinator only timestamps
    RETURNING_TO_BREAK_ROOM / RESTING states and asks a caller-supplied policy
    when the next explicit transition should occur.
    """

    def __init__(self, runtime: StoreRuntimeHarness) -> None:
        self.runtime = runtime
        self._active: dict[str, StaffRestTimingState] = {}

    @property
    def active_states(self) -> tuple[StaffRestTimingState, ...]:
        return tuple(self._active.values())

    @property
    def active_staff_ids(self) -> tuple[str, ...]:
        return tuple(self._active)

    def register_staff(
        self,
        staff_id: str,
        *,
        started_at_absolute_minute: Optional[int] = None,
    ) -> StaffRestTimingState:
        staff = self.runtime.staff.staff_member(staff_id)
        if staff.condition not in REST_LIFECYCLE_CONDITIONS:
            raise ValueError("staff member is not in a rest lifecycle condition")
        start = (
            self.runtime.subday_clock.absolute_minutes
            if started_at_absolute_minute is None
            else started_at_absolute_minute
        )
        if start < 0:
            raise ValueError("started_at_absolute_minute must be >= 0")
        if start > self.runtime.subday_clock.absolute_minutes:
            raise ValueError("rest lifecycle cannot start in the future")
        state = StaffRestTimingState(
            staff_id=staff_id,
            condition=staff.condition,
            started_at_absolute_minute=start,
            break_room_target_id=staff.target_id,
        )
        self._active[staff_id] = state
        return state

    def sync_from_roster(self) -> tuple[StaffRestTimingState, ...]:
        """Track current unavailable rest states without advancing them."""
        registered: list[StaffRestTimingState] = []
        current_ids = {staff.id for staff in self.runtime.staff.staff}
        for staff_id in tuple(self._active):
            if staff_id not in current_ids:
                del self._active[staff_id]
                continue
            staff = self.runtime.staff.staff_member(staff_id)
            if staff.condition not in REST_LIFECYCLE_CONDITIONS:
                del self._active[staff_id]
                continue
            state = self._active[staff_id]
            if state.condition is not staff.condition:
                registered.append(self.register_staff(staff_id))

        for staff in self.runtime.staff.staff:
            if (
                staff.condition in REST_LIFECYCLE_CONDITIONS
                and staff.id not in self._active
            ):
                registered.append(self.register_staff(staff.id))
        return tuple(registered)

    def current_context(self, staff_id: str) -> StaffRestTimingContext:
        state = self._active[staff_id]
        staff = self.runtime.staff.staff_member(staff_id)
        if staff.condition is not state.condition:
            raise ValueError("registered rest condition no longer matches roster")
        current = self.runtime.subday_clock.absolute_minutes
        if current < state.started_at_absolute_minute:
            raise ValueError("runtime clock moved before rest lifecycle start")
        return StaffRestTimingContext(
            staff_id=staff_id,
            condition=state.condition,
            started_at_absolute_minute=state.started_at_absolute_minute,
            current_absolute_minute=current,
            elapsed_game_minutes=current - state.started_at_absolute_minute,
            break_room_target_id=state.break_room_target_id,
            stamina_current=staff.stamina_current,
            stamina_max=staff.stamina_max,
        )

    def evaluate_staff(
        self,
        staff_id: str,
        policy: StaffRestTransitionPolicy,
    ) -> StaffRestTimingEvaluation:
        context = self.current_context(staff_id)
        decision = policy.transition(context)
        if decision is None:
            return StaffRestTimingEvaluation(context, StaffRestTimingStatus.ACTIVE)

        if context.condition is StaffCondition.RETURNING_TO_BREAK_ROOM:
            if not decision.arrive_at_break_room or decision.recovery_amount is not None:
                raise ValueError("returning staff may only transition by arriving at break room")
            staff = self.runtime.staff.arrive_at_break_room(
                staff_id,
                break_room_target_id=context.break_room_target_id,
            )
            self.register_staff(staff_id)
            return StaffRestTimingEvaluation(
                context,
                StaffRestTimingStatus.ARRIVED_AT_BREAK_ROOM,
                decision,
                staff.stamina_current,
            )

        if decision.arrive_at_break_room or decision.recovery_amount is None:
            raise ValueError("resting staff require an explicit recovery_amount")
        staff = self.runtime.staff.recover_stamina(staff_id, decision.recovery_amount)
        if staff.condition is StaffCondition.AVAILABLE:
            del self._active[staff_id]
            status = StaffRestTimingStatus.RECOVERY_COMPLETE
        else:
            status = StaffRestTimingStatus.RECOVERED
        return StaffRestTimingEvaluation(
            context,
            status,
            decision,
            staff.stamina_current,
        )

    def evaluate_all(
        self,
        policy: StaffRestTransitionPolicy,
    ) -> tuple[StaffRestTimingEvaluation, ...]:
        return tuple(
            self.evaluate_staff(staff_id, policy)
            for staff_id in tuple(self._active)
        )
