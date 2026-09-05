from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from .customer import CustomerLifecycleHarness, CustomerState
from .staff import StaffTask, StoreStaffRoster


class CheckoutCapacityError(RuntimeError):
    pass


@dataclass(frozen=True)
class CheckoutServiceRecord:
    customer_id: str
    staff_id: str
    fixture_id: str


class CheckoutStationRuntime:
    """Logical checkout waiting/service layer without inventing queue timing.

    Arrival order is recorded for observation, but service selection is explicit
    and is intentionally *not* forced to FIFO. First-title FAQ evidence reports
    that a later-arriving customer can sometimes be served before an earlier
    one. Service duration is also unknown, so checkout finishes only when the
    caller explicitly invokes `finish_service`.
    """

    def __init__(
        self,
        fixture_id: str,
        customers: CustomerLifecycleHarness,
        staff: StoreStaffRoster,
        *,
        simultaneous_staff_capacity: int,
    ) -> None:
        if simultaneous_staff_capacity < 1:
            raise ValueError("simultaneous_staff_capacity must be >= 1")
        self.fixture_id = fixture_id
        self.customers = customers
        self.staff = staff
        self.simultaneous_staff_capacity = simultaneous_staff_capacity
        self._waiting: list[str] = []
        self._active_by_staff: dict[str, str] = {}
        self._service_history: list[CheckoutServiceRecord] = []

    @property
    def waiting_customer_ids(self) -> tuple[str, ...]:
        return tuple(self._waiting)

    @property
    def active_services(self) -> tuple[CheckoutServiceRecord, ...]:
        return tuple(
            CheckoutServiceRecord(customer_id, staff_id, self.fixture_id)
            for staff_id, customer_id in self._active_by_staff.items()
        )

    @property
    def service_history(self) -> tuple[CheckoutServiceRecord, ...]:
        return tuple(self._service_history)

    def customer_being_served_by(self, staff_id: str) -> Optional[str]:
        return self._active_by_staff.get(staff_id)

    def refresh_waiting(self) -> tuple[str, ...]:
        """Enroll newly arrived customers and remove no-longer-waiting entries."""
        active_customers = set(self._active_by_staff.values())
        eligible: list[str] = []
        for session in self.customers.customers:
            if (
                session.checkout_fixture_id == self.fixture_id
                and session.state is CustomerState.WAITING_CHECKOUT
                and session.id not in active_customers
            ):
                eligible.append(session.id)

        eligible_set = set(eligible)
        self._waiting = [customer_id for customer_id in self._waiting if customer_id in eligible_set]
        for customer_id in eligible:
            if customer_id not in self._waiting:
                self._waiting.append(customer_id)
        return self.waiting_customer_ids

    def begin_service(self, staff_id: str, customer_id: str) -> CheckoutServiceRecord:
        self.refresh_waiting()
        if customer_id not in self._waiting:
            raise ValueError("customer is not waiting at this checkout")
        if staff_id in self._active_by_staff:
            raise ValueError("staff member is already serving a customer at this checkout")
        if customer_id in self._active_by_staff.values():
            raise ValueError("customer is already being served")
        if len(self._active_by_staff) >= self.simultaneous_staff_capacity:
            raise CheckoutCapacityError("checkout has no free staff service slot")

        staff_state = self.staff.staff_member(staff_id)
        if staff_state.task is StaffTask.CHECKOUT:
            if staff_state.target_id not in (None, self.fixture_id):
                raise ValueError("staff member is already assigned to another checkout")
        elif staff_state.task is not StaffTask.IDLE:
            # Starting checkout is not itself a task-reassignment policy.  If a
            # staff member is replenishing, cleaning, resting, or otherwise
            # assigned, the caller/policy must explicitly release/reassign that
            # work before checkout service may begin.
            raise ValueError("staff member is already assigned to another task")

        self._waiting.remove(customer_id)
        self._active_by_staff[staff_id] = customer_id
        self.staff.assign_task(staff_id, StaffTask.CHECKOUT, target_id=self.fixture_id)
        return CheckoutServiceRecord(customer_id, staff_id, self.fixture_id)

    def finish_service(self, staff_id: str) -> CheckoutServiceRecord:
        try:
            customer_id = self._active_by_staff.pop(staff_id)
        except KeyError as exc:
            raise KeyError(f"staff member {staff_id!r} has no active checkout service") from exc

        session = self.customers.customer(customer_id)
        if session.state is not CustomerState.WAITING_CHECKOUT:
            self.staff.release_to_idle(staff_id)
            raise ValueError("active checkout customer is no longer waiting")

        self.customers.complete_checkout(customer_id)
        # Completing one checkout is a confirmed register-work event. It is
        # counted for future skill-growth reconstruction, but no stamina cost or
        # skill delta is invented here.
        self.staff.record_completed_work(staff_id, StaffTask.CHECKOUT)
        self.staff.release_to_idle(staff_id)
        record = CheckoutServiceRecord(customer_id, staff_id, self.fixture_id)
        self._service_history.append(record)
        return record

    def cancel_customer(self, customer_id: str) -> bool:
        """Detach an ejected/abandoned customer without guessing consequences."""
        removed = False
        if customer_id in self._waiting:
            self._waiting.remove(customer_id)
            removed = True

        serving_staff = next(
            (staff_id for staff_id, active_customer in self._active_by_staff.items() if active_customer == customer_id),
            None,
        )
        if serving_staff is not None:
            del self._active_by_staff[serving_staff]
            self.staff.release_to_idle(serving_staff)
            removed = True
        return removed
