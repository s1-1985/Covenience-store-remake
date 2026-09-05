from __future__ import annotations

from dataclasses import dataclass
from typing import Optional, Protocol

from .checkout import CheckoutServiceRecord
from .staff import StaffTask
from .store_runtime import StoreRuntimeHarness


@dataclass(frozen=True)
class CheckoutSelectionContext:
    staff_id: str
    checkout_fixture_id: str
    waiting_customer_ids: tuple[str, ...]
    active_service_count: int
    simultaneous_staff_capacity: int

    @property
    def free_service_slots(self) -> int:
        return self.simultaneous_staff_capacity - self.active_service_count


class CheckoutCustomerSelectionPolicy(Protocol):
    """Replaceable policy for unresolved first-title checkout customer choice."""

    def choose_customer(self, context: CheckoutSelectionContext) -> Optional[str]: ...


@dataclass(frozen=True)
class CheckoutSelectionEvaluation:
    context: CheckoutSelectionContext
    selected_customer_id: Optional[str]
    service_started: Optional[CheckoutServiceRecord]


class CheckoutSelectionCoordinator:
    """Start service for a checkout-assigned staff member without assuming FIFO.

    The first-title FAQ reports non-strict checkout order, so any currently
    waiting customer at the assigned checkout may be chosen. Service completion
    and duration remain explicit and are not handled here.
    """

    def __init__(self, runtime: StoreRuntimeHarness) -> None:
        self.runtime = runtime

    def current_context(self, staff_id: str) -> CheckoutSelectionContext:
        staff = self.runtime.staff.staff_member(staff_id)
        if staff.task is not StaffTask.CHECKOUT or staff.target_id is None:
            raise ValueError("staff member is not assigned to a checkout")
        checkout = self.runtime.checkout(staff.target_id)
        waiting = checkout.refresh_waiting()
        return CheckoutSelectionContext(
            staff_id=staff_id,
            checkout_fixture_id=staff.target_id,
            waiting_customer_ids=waiting,
            active_service_count=len(checkout.active_services),
            simultaneous_staff_capacity=checkout.simultaneous_staff_capacity,
        )

    def evaluate(
        self,
        staff_id: str,
        policy: CheckoutCustomerSelectionPolicy,
    ) -> CheckoutSelectionEvaluation:
        context = self.current_context(staff_id)
        if context.free_service_slots <= 0:
            return CheckoutSelectionEvaluation(context, None, None)

        selected = policy.choose_customer(context)
        if selected is None:
            return CheckoutSelectionEvaluation(context, None, None)
        if selected not in context.waiting_customer_ids:
            raise ValueError("policy selected a customer who is not waiting at this checkout")

        started = self.runtime.begin_checkout_service(
            context.checkout_fixture_id,
            staff_id=staff_id,
            customer_id=selected,
        )
        return CheckoutSelectionEvaluation(context, selected, started)
