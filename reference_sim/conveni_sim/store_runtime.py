from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Optional, Sequence

from .checkout import CheckoutServiceRecord, CheckoutStationRuntime
from .cleaning import StoreCleaningRuntime
from .customer import CustomerLifecycleHarness, CustomerSession, CustomerState, PurchaseFlow
from .customer_share import CustomerShareRuntime
from .economy import BankruptcyPolicy, DayEndResult, FinancialEvent, StoreCashLedger
from .inventory import InventoryMutation, StoreInventoryRuntime
from .manager_magazine_event import ManagerMagazineEventRuntime
from .operating_time import ClockAdvanceResult, OperatingHours, SubdayClock
from .purchases import BasketPickResult, SaleSettlement, StorePurchaseRuntime
from .staff import StoreStaffRoster
from .store_grid import GridPoint, StoreGrid
from .traffic import DynamicTrafficHarness


@dataclass(frozen=True)
class CheckoutSaleCompletion:
    settlement: SaleSettlement
    service_finished: CheckoutServiceRecord


@dataclass(frozen=True)
class CheckoutSaleResult:
    service_started: CheckoutServiceRecord
    settlement: SaleSettlement
    service_finished: CheckoutServiceRecord


@dataclass(frozen=True)
class ReplenishAndChargeResult:
    inventory_mutation: InventoryMutation
    procurement_event: FinancialEvent


class CustomerAdmissionStatus(str, Enum):
    ADMITTED = "admitted"
    STORE_CLOSED = "store_closed"
    OPEN_STATE_UNKNOWN = "open_state_unknown"


@dataclass(frozen=True)
class CustomerAdmissionResult:
    customer_id: str
    status: CustomerAdmissionStatus
    session: Optional[CustomerSession] = None

    @property
    def admitted(self) -> bool:
        return self.status is CustomerAdmissionStatus.ADMITTED


class StoreRuntimeHarness:
    """Headless composition of the currently recovered store subsystems.

    This class adds no autonomous AI, timing or pricing rules. It only wires the
    existing explicit layers together so an observation or later production
    policy can drive a full customer/store transaction without duplicating
    bookkeeping code.
    """

    def __init__(
        self,
        grid: StoreGrid,
        *,
        initial_cash_yen: int,
        bankruptcy_policy: BankruptcyPolicy = BankruptcyPolicy(),
        operating_hours: Optional[OperatingHours] = None,
        subday_clock: Optional[SubdayClock] = None,
    ) -> None:
        self.grid = grid
        self.traffic = DynamicTrafficHarness(grid)
        self.customers = CustomerLifecycleHarness(self.traffic)
        self.staff = StoreStaffRoster()
        self.manager_magazine_events = ManagerMagazineEventRuntime(self.staff)
        self.inventory = StoreInventoryRuntime()
        self.cash = StoreCashLedger(
            initial_cash_yen,
            bankruptcy_policy=bankruptcy_policy,
        )
        self.purchases = StorePurchaseRuntime(self.inventory, self.cash)
        self.cleaning = StoreCleaningRuntime(grid)
        self.customer_share = CustomerShareRuntime()
        self.operating_hours = operating_hours
        self.temporary_closed = False
        self.subday_clock = subday_clock if subday_clock is not None else SubdayClock()
        self._checkouts: dict[str, CheckoutStationRuntime] = {}

    @property
    def checkout_fixture_ids(self) -> tuple[str, ...]:
        return tuple(self._checkouts)

    @property
    def store_open(self) -> Optional[bool]:
        """Current effective open/closed state, or None when only the schedule is unknown."""
        if self.temporary_closed:
            return False
        if self.operating_hours is None:
            return None
        return self.operating_hours.is_open_clock(self.subday_clock)

    def _fixture_is_placed(self, fixture_id: str) -> bool:
        return any(
            placement.instance_id == fixture_id
            for placement in self.grid.placements
        )

    def _require_placed_fixture(self, fixture_id: str, *, role: str) -> None:
        if not self._fixture_is_placed(fixture_id):
            raise ValueError(f"{role} fixture is not currently placed on the grid: {fixture_id}")

    def set_operating_hours(self, operating_hours: Optional[OperatingHours]) -> None:
        self.operating_hours = operating_hours

    def set_temporary_closure(self, closed: bool) -> None:
        """Toggle explicit 臨時休業 without changing the ordinary opening schedule."""
        self.temporary_closed = closed

    def advance_game_minutes(self, minutes: int) -> ClockAdvanceResult:
        """Advance explicit game time and apply evidence-backed date-change gates."""
        result = self.subday_clock.advance_minutes(minutes)
        if result.days_crossed:
            self.customer_share.on_date_change(days_crossed=result.days_crossed)
            if self.temporary_closed:
                self.customer_share.apply_share(
                    0,
                    source="first-title FAQ: temporary closure at date change",
                )
        return result

    def observe_weather(self, weather: str) -> None:
        """Record current weather; known weather changes request a share refresh."""
        self.customer_share.observe_weather(weather)

    def record_labor_cost_current_time(
        self,
        amount_yen: Optional[int],
        *,
        staff_id: Optional[str] = None,
    ) -> Optional[FinancialEvent]:
        """Bridge effective open state to the existing closed-hours labor rule.

        Unknown ordinary opening hours are not treated as either open or closed,
        unless the store is explicitly under temporary closure.
        """
        store_open = self.store_open
        if store_open is None:
            raise ValueError("operating hours are unknown")
        return self.cash.record_labor_cost_if_open(
            amount_yen,
            store_open=store_open,
            staff_id=staff_id,
        )

    def checkout(self, fixture_id: str) -> CheckoutStationRuntime:
        return self._checkouts[fixture_id]

    def add_checkout(
        self,
        fixture_id: str,
        *,
        simultaneous_staff_capacity: int,
    ) -> CheckoutStationRuntime:
        if fixture_id in self._checkouts:
            raise ValueError(f"checkout already registered: {fixture_id}")
        if not self._fixture_is_placed(fixture_id):
            raise KeyError(f"checkout fixture is not placed on the grid: {fixture_id}")
        checkout = CheckoutStationRuntime(
            fixture_id,
            self.customers,
            self.staff,
            simultaneous_staff_capacity=simultaneous_staff_capacity,
        )
        self._checkouts[fixture_id] = checkout
        return checkout

    def admit_customer(
        self,
        customer_id: str,
        *,
        entry: GridPoint,
        exit: GridPoint,
        merchandise_fixture_ids: Sequence[str],
        checkout_fixture_id: Optional[str] = None,
    ) -> CustomerAdmissionResult:
        """Create a customer only when effective opening state is confirmed open."""
        open_state = self.store_open
        if open_state is None:
            return CustomerAdmissionResult(
                customer_id,
                CustomerAdmissionStatus.OPEN_STATE_UNKNOWN,
            )
        if not open_state:
            return CustomerAdmissionResult(
                customer_id,
                CustomerAdmissionStatus.STORE_CLOSED,
            )
        session = self.customers.enter_customer(
            customer_id,
            entry=entry,
            exit=exit,
            merchandise_fixture_ids=merchandise_fixture_ids,
            checkout_fixture_id=checkout_fixture_id,
        )
        return CustomerAdmissionResult(
            customer_id,
            CustomerAdmissionStatus.ADMITTED,
            session,
        )

    def advance_customer_traffic(self) -> dict[str, GridPoint]:
        """Advance one headless traffic tick and project arrivals into customer states."""
        moved = self.traffic.tick()
        self.customers.sync_arrivals()
        for checkout in self._checkouts.values():
            checkout.refresh_waiting()
        return moved

    def customer_pick_and_continue(
        self,
        customer_id: str,
        *,
        slot_id: str,
        quantity: int = 1,
        unit_sale_price_yen: Optional[int],
        flow: PurchaseFlow,
    ) -> BasketPickResult:
        """Pick stock at the customer's current merchandise stop, then continue route."""
        session = self.customers.customer(customer_id)
        slot = self.inventory.slot(slot_id)
        if session.state is not CustomerState.AT_MERCHANDISE:
            raise ValueError("customer is not at merchandise")
        if session.current_merchandise_fixture_id != slot.fixture_id:
            raise ValueError(
                "customer current merchandise fixture does not match inventory slot fixture"
            )
        self._require_placed_fixture(slot.fixture_id, role="merchandise")
        if flow is PurchaseFlow.CHECKOUT_REQUIRED and session.checkout_fixture_id is None:
            raise ValueError("checkout-required interaction needs a checkout fixture")

        pick = self.purchases.pick_from_inventory(
            customer_id,
            slot_id,
            quantity=quantity,
            unit_sale_price_yen=unit_sale_price_yen,
        )
        self.customers.record_merchandise_interaction(customer_id, flow=flow)
        return pick

    def customer_skip_and_continue(self, customer_id: str) -> CustomerSession:
        """Advance a visited merchandise stop without creating a purchase."""
        return self.customers.leave_merchandise_without_purchase(customer_id)

    def begin_checkout_service(
        self,
        checkout_fixture_id: str,
        *,
        staff_id: str,
        customer_id: str,
    ) -> CheckoutServiceRecord:
        """Start checkout service without assuming how long it takes."""
        basket = self.purchases.basket(customer_id)
        if basket.settled:
            raise ValueError("customer basket is already settled")
        if not basket.lines:
            raise ValueError("customer basket is empty")
        return self._checkouts[checkout_fixture_id].begin_service(staff_id, customer_id)

    def finish_checkout_sale(
        self,
        checkout_fixture_id: str,
        *,
        staff_id: str,
    ) -> CheckoutSaleCompletion:
        """Settle and finish an already-active checkout service explicitly."""
        checkout = self._checkouts[checkout_fixture_id]
        customer_id = checkout.customer_being_served_by(staff_id)
        if customer_id is None:
            raise KeyError(f"staff member {staff_id!r} has no active checkout service")
        basket = self.purchases.basket(customer_id)
        if basket.settled:
            raise ValueError("customer basket is already settled")
        if not basket.lines:
            raise ValueError("customer basket is empty")

        settlement = self.purchases.settle(customer_id, source_id=checkout_fixture_id)
        finished = checkout.finish_service(staff_id)
        return CheckoutSaleCompletion(settlement, finished)

    def complete_checkout_sale(
        self,
        checkout_fixture_id: str,
        *,
        staff_id: str,
        customer_id: str,
    ) -> CheckoutSaleResult:
        """Backward-compatible immediate start+finish helper for explicit replays."""
        started = self.begin_checkout_service(
            checkout_fixture_id,
            staff_id=staff_id,
            customer_id=customer_id,
        )
        completion = self.finish_checkout_sale(
            checkout_fixture_id,
            staff_id=staff_id,
        )
        return CheckoutSaleResult(
            started,
            completion.settlement,
            completion.service_finished,
        )

    def settle_self_service(
        self,
        customer_id: str,
        *,
        source_id: Optional[str] = None,
    ) -> SaleSettlement:
        session = self.customers.customer(customer_id)
        if session.requires_checkout and not session.completed_checkout:
            raise ValueError("customer basket requires staffed checkout before self-service settlement")
        return self.purchases.settle(customer_id, source_id=source_id)

    def replenish_and_charge(
        self,
        slot_id: str,
        quantity: int,
        *,
        staff_id: Optional[str] = None,
        stamina_cost: Optional[int] = None,
        break_room_target_id: Optional[str] = None,
        source_id: Optional[str] = None,
    ) -> ReplenishAndChargeResult:
        """Replenish stock and record the procurement outflow in one explicit operation."""
        if staff_id is None and (stamina_cost is not None or break_room_target_id is not None):
            raise ValueError("staff_id is required for staff work metadata")
        slot = self.inventory.slot(slot_id)
        self._require_placed_fixture(slot.fixture_id, role="inventory")
        mutation = self.inventory.replenish(
            slot_id,
            quantity,
            staff_roster=self.staff if staff_id is not None else None,
            staff_id=staff_id,
            stamina_cost=stamina_cost,
            break_room_target_id=break_room_target_id,
        )
        event = self.cash.record_procurement(
            mutation.procurement_cost_yen,
            source_id=source_id or slot_id,
        )
        return ReplenishAndChargeResult(mutation, event)

    def end_day(
        self,
        *,
        labor_cost_yen: Optional[int],
        other_costs_yen: Sequence[Optional[int]] = (),
    ) -> DayEndResult:
        """Close the day through the explicit financial boundary."""
        return self.cash.close_day(
            labor_cost_yen=labor_cost_yen,
            other_costs_yen=other_costs_yen,
        )
