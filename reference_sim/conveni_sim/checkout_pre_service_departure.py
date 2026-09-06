from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Optional, Protocol

from .staff import StaffCondition, StaffTask
from .store_runtime import StoreRuntimeHarness


class CheckoutPreServiceAction(str, Enum):
    PROCEED_TO_SERVICE = "proceed_to_service"
    RETURN_TO_BREAK_ROOM = "return_to_break_room"


@dataclass(frozen=True)
class CheckoutPreServiceDecision:
    action: CheckoutPreServiceAction
    break_room_target_id: Optional[str] = None

    def __post_init__(self) -> None:
        if (
            self.action is not CheckoutPreServiceAction.RETURN_TO_BREAK_ROOM
            and self.break_room_target_id is not None
        ):
            raise ValueError(
                "break_room_target_id is only valid for RETURN_TO_BREAK_ROOM"
            )


@dataclass(frozen=True)
class CheckoutPreServiceDepartureContext:
    staff_id: str
    checkout_fixture_id: str
    waiting_customer_ids: tuple[str, ...]
    active_service_count: int
    simultaneous_staff_capacity: int
    free_service_slots: int
    stamina_current: Optional[int]
    stamina_max: Optional[int]
    current_minute_of_day: int


class CheckoutPreServiceDeparturePolicy(Protocol):
    """Decide whether an assigned cashier proceeds or leaves before service.

    First-title B+ observations report that a low-stamina cashier can head back
    toward the break room after reacting to checkout demand. The original stamina
    threshold and exact timing are unknown, so this policy receives factual state
    and may return None to keep the decision unresolved.
    """

    def decide(
        self,
        context: CheckoutPreServiceDepartureContext,
    ) -> Optional[CheckoutPreServiceDecision]: ...


class CheckoutPreServiceDepartureStatus(str, Enum):
    NOT_APPLICABLE = "not_applicable"
    UNRESOLVED = "unresolved"
    PROCEED = "proceed"
    DEPARTED = "departed"


@dataclass(frozen=True)
class CheckoutPreServiceDepartureEvaluation:
    context: CheckoutPreServiceDepartureContext
    status: CheckoutPreServiceDepartureStatus
    decision: Optional[CheckoutPreServiceDecision] = None


class CheckoutPreServiceDepartureCoordinator:
    """Apply an explicit pre-service cashier departure decision.

    The coordinator is evaluated only for an AVAILABLE staff member already
    assigned to checkout and not already serving a customer. It does not infer a
    stamina threshold. If factual waiting demand or a free service slot is absent,
    the policy is not consulted.
    """

    def __init__(self, runtime: StoreRuntimeHarness) -> None:
        self.runtime = runtime

    def current_context(self, staff_id: str) -> CheckoutPreServiceDepartureContext:
        staff = self.runtime.staff.staff_member(staff_id)
        if staff.condition is not StaffCondition.AVAILABLE:
            raise ValueError("staff member is not available for checkout departure evaluation")
        if staff.task is not StaffTask.CHECKOUT or staff.target_id is None:
            raise ValueError("staff member is not assigned to a checkout")

        checkout = self.runtime.checkout(staff.target_id)
        if checkout.customer_being_served_by(staff_id) is not None:
            raise ValueError("staff member already has active checkout service")
        waiting = checkout.refresh_waiting()
        active_service_count = len(checkout.active_services)
        return CheckoutPreServiceDepartureContext(
            staff_id=staff_id,
            checkout_fixture_id=staff.target_id,
            waiting_customer_ids=waiting,
            active_service_count=active_service_count,
            simultaneous_staff_capacity=checkout.simultaneous_staff_capacity,
            free_service_slots=max(
                0,
                checkout.simultaneous_staff_capacity - active_service_count,
            ),
            stamina_current=staff.stamina_current,
            stamina_max=staff.stamina_max,
            current_minute_of_day=self.runtime.subday_clock.minute_of_day,
        )

    def evaluate_staff(
        self,
        staff_id: str,
        policy: CheckoutPreServiceDeparturePolicy,
    ) -> CheckoutPreServiceDepartureEvaluation:
        context = self.current_context(staff_id)
        if not context.waiting_customer_ids or context.free_service_slots <= 0:
            return CheckoutPreServiceDepartureEvaluation(
                context=context,
                status=CheckoutPreServiceDepartureStatus.NOT_APPLICABLE,
            )

        decision = policy.decide(context)
        if decision is None:
            return CheckoutPreServiceDepartureEvaluation(
                context=context,
                status=CheckoutPreServiceDepartureStatus.UNRESOLVED,
            )
        if decision.action is CheckoutPreServiceAction.PROCEED_TO_SERVICE:
            return CheckoutPreServiceDepartureEvaluation(
                context=context,
                status=CheckoutPreServiceDepartureStatus.PROCEED,
                decision=decision,
            )

        self.runtime.staff.begin_break_room_return(
            staff_id,
            break_room_target_id=decision.break_room_target_id,
        )
        return CheckoutPreServiceDepartureEvaluation(
            context=context,
            status=CheckoutPreServiceDepartureStatus.DEPARTED,
            decision=decision,
        )
