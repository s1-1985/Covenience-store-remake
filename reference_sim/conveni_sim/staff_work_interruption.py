from __future__ import annotations

from dataclasses import dataclass
from typing import Optional, Protocol

from .staff import StaffCondition
from .staff_work_timing import StaffWorkTimingContext, StaffWorkTimingCoordinator, StaffWorkTimingState
from .store_runtime import StoreRuntimeHarness


@dataclass(frozen=True)
class StaffWorkInterruptionContext:
    """Factual context for deciding whether active non-checkout work may be released."""

    work: StaffWorkTimingContext
    checkout_waiting_by_fixture: tuple[tuple[str, int], ...]

    @property
    def total_waiting_checkout_customers(self) -> int:
        return sum(count for _, count in self.checkout_waiting_by_fixture)

    @property
    def checkout_demand_present(self) -> bool:
        return self.total_waiting_checkout_customers > 0


class StaffWorkInterruptionPolicy(Protocol):
    """Replaceable boundary for unresolved checkout interruption timing."""

    def should_interrupt(self, context: StaffWorkInterruptionContext) -> Optional[bool]: ...


@dataclass(frozen=True)
class StaffWorkInterruptionEvaluation:
    context: StaffWorkInterruptionContext
    requested: Optional[bool]
    interrupted: bool
    released_state: Optional[StaffWorkTimingState] = None


class StaffWorkInterruptionCoordinator:
    """Release active replenish/clean work only after an explicit policy request.

    The coordinator does not decide when checkout demand is urgent enough. It
    exposes factual queue counts and elapsed work time to a supplied policy. A
    true request is honored only while checkout demand actually exists. The
    interrupted work is unregistered and the still-matching staff assignment is
    released to idle so ordinary task selection may choose a checkout in the same
    store step.

    No resume semantics are invented. The original target remains objectively
    actionable and may be selected again later by whatever staff-task policy is
    active.
    """

    def __init__(self, runtime: StoreRuntimeHarness, work_timing: StaffWorkTimingCoordinator) -> None:
        if work_timing.runtime is not runtime:
            raise ValueError("staff work interruption must use the same runtime")
        self.runtime = runtime
        self.work_timing = work_timing

    def _checkout_waiting(self) -> tuple[tuple[str, int], ...]:
        rows: list[tuple[str, int]] = []
        for fixture_id in sorted(self.runtime.checkout_fixture_ids):
            rows.append((fixture_id, len(self.runtime.checkout(fixture_id).refresh_waiting())))
        return tuple(rows)

    def current_context(self, staff_id: str) -> StaffWorkInterruptionContext:
        return StaffWorkInterruptionContext(
            work=self.work_timing.current_context(staff_id),
            checkout_waiting_by_fixture=self._checkout_waiting(),
        )

    def evaluate_staff(
        self,
        staff_id: str,
        policy: StaffWorkInterruptionPolicy,
    ) -> StaffWorkInterruptionEvaluation:
        context = self.current_context(staff_id)
        requested = policy.should_interrupt(context)
        if requested is not True or not context.checkout_demand_present:
            return StaffWorkInterruptionEvaluation(context, requested, False, None)

        state = self.work_timing.unregister_staff(staff_id)
        if state is None:
            raise ValueError("active staff work disappeared during interruption")
        staff = self.runtime.staff.staff_member(staff_id)
        if (
            staff.condition is StaffCondition.AVAILABLE
            and staff.task is state.task
            and staff.target_id == state.target_id
        ):
            self.runtime.staff.release_to_idle(staff_id)
        return StaffWorkInterruptionEvaluation(context, True, True, state)

    def evaluate_all(
        self,
        policy: StaffWorkInterruptionPolicy,
    ) -> tuple[StaffWorkInterruptionEvaluation, ...]:
        return tuple(
            self.evaluate_staff(staff_id, policy)
            for staff_id in tuple(self.work_timing.active_staff_ids)
        )
