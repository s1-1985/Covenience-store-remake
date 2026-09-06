from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from .customer import CustomerState
from .staff import StaffCondition, StaffTask
from .store_runtime import StoreRuntimeHarness


@dataclass(frozen=True)
class CheckoutTelemetry:
    fixture_id: str
    waiting_customer_ids: tuple[str, ...]
    active_customer_ids: tuple[str, ...]
    active_staff_ids: tuple[str, ...]


@dataclass(frozen=True)
class StaffTelemetry:
    staff_id: str
    condition: StaffCondition
    task: StaffTask
    target_id: Optional[str]
    stamina_current: Optional[int]
    stamina_max: Optional[int]


@dataclass(frozen=True)
class InventoryTelemetry:
    slot_id: str
    fixture_id: str
    product_id: str
    units: int
    capacity_units: int


@dataclass(frozen=True)
class StoreTelemetrySnapshot:
    absolute_game_minute: int
    minute_of_day: int
    total_customer_sessions: int
    customer_state_counts: tuple[tuple[CustomerState, int], ...]
    checkouts: tuple[CheckoutTelemetry, ...]
    staff: tuple[StaffTelemetry, ...]
    inventory: tuple[InventoryTelemetry, ...]
    known_cash_yen: int
    cash_is_exact: bool

    def customer_count(self, state: CustomerState) -> int:
        return dict(self.customer_state_counts)[state]

    @property
    def waiting_checkout_customers(self) -> int:
        return sum(len(checkout.waiting_customer_ids) for checkout in self.checkouts)

    @property
    def active_checkout_services(self) -> int:
        return sum(len(checkout.active_customer_ids) for checkout in self.checkouts)


class StoreTelemetryRecorder:
    """Capture factual runtime state without fitting or inferring game rules."""

    def snapshot(self, runtime: StoreRuntimeHarness) -> StoreTelemetrySnapshot:
        customers = runtime.customers.customers
        state_counts = tuple(
            (
                state,
                sum(1 for customer in customers if customer.state is state),
            )
            for state in CustomerState
        )

        checkouts: list[CheckoutTelemetry] = []
        for fixture_id in sorted(runtime.checkout_fixture_ids):
            checkout = runtime.checkout(fixture_id)
            active = checkout.active_services
            active_customer_ids = tuple(record.customer_id for record in active)
            active_customer_set = set(active_customer_ids)
            waiting = tuple(
                sorted(
                    customer.id
                    for customer in customers
                    if (
                        customer.checkout_fixture_id == fixture_id
                        and customer.state is CustomerState.WAITING_CHECKOUT
                        and customer.id not in active_customer_set
                    )
                )
            )
            checkouts.append(
                CheckoutTelemetry(
                    fixture_id=fixture_id,
                    waiting_customer_ids=waiting,
                    active_customer_ids=active_customer_ids,
                    active_staff_ids=tuple(record.staff_id for record in active),
                )
            )

        staff = tuple(
            StaffTelemetry(
                staff_id=member.id,
                condition=member.condition,
                task=member.task,
                target_id=member.target_id,
                stamina_current=member.stamina_current,
                stamina_max=member.stamina_max,
            )
            for member in sorted(runtime.staff.staff, key=lambda item: item.id)
        )

        inventory = tuple(
            InventoryTelemetry(
                slot_id=slot.id,
                fixture_id=slot.fixture_id,
                product_id=slot.product_id,
                units=slot.units,
                capacity_units=slot.capacity_units,
            )
            for slot in sorted(runtime.inventory.slots, key=lambda item: item.id)
        )

        return StoreTelemetrySnapshot(
            absolute_game_minute=runtime.subday_clock.absolute_minutes,
            minute_of_day=runtime.subday_clock.minute_of_day,
            total_customer_sessions=len(customers),
            customer_state_counts=state_counts,
            checkouts=tuple(checkouts),
            staff=staff,
            inventory=inventory,
            known_cash_yen=runtime.cash.known_cash_yen,
            cash_is_exact=runtime.cash.cash_is_exact,
        )
