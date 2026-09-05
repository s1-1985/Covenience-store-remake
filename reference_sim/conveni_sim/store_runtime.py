from __future__ import annotations

from dataclasses import dataclass
from typing import Optional, Sequence

from .checkout import CheckoutServiceRecord, CheckoutStationRuntime
from .cleaning import StoreCleaningRuntime
from .customer import CustomerLifecycleHarness, CustomerSession, CustomerState, PurchaseFlow
from .customer_share import CustomerShareRuntime
from .economy import BankruptcyPolicy, DayEndResult, FinancialEvent, StoreCashLedger
from .inventory import InventoryMutation, StoreInventoryRuntime
from .operating_time import ClockAdvanceResult, OperatingHours, SubdayClock
from .purchases import BasketPickResult, SaleSettlement, StorePurchaseRuntime
from .staff import StoreStaffRoster
from .store_grid import GridPoint, StoreGrid
from .traffic import DynamicTrafficHarness


@dataclass(frozen=True)
class CheckoutSaleResult:
    service_started: CheckoutServiceRecord
    settlement: SaleSettlement
    service_finished: CheckoutServiceRecord


@dataclass(frozen=True)
class ReplenishAndChargeResult:
    inventory_mutation: InventoryMutation
    procurement_event: FinancialEvent


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
        self.inventory = StoreInventoryRuntime()
        self.cash = StoreCashLedger(
            initial_cash_yen,
            bankruptcy_policy=bankruptcy_policy,
        )
        self.purchases = StorePurchaseRuntime(self.inventory, self.cash)
        self.cleaning = StoreCleaningRuntime(grid)
        self.customer_share = CustomerShareRuntime()
        self.operating_hours = operating_hours
        self.subday_clock = subday_clock if subday_clock is not None else SubdayClock()
        self._checkouts: dict[str, CheckoutStationRuntime] = {}

    @property
    def checkout_fixture_ids(self) -> tuple[str, ...]:
        return tuple(self._checkouts)

    @property
    def store_open(self) -> Optional[bool]:
        """Current open/closed state, or None while the schedule is unknown."""
        if self.operating_hours is None:
            return None
        return self.operating_hours.is_open_clock(self.subday_clock)

    def set_operating_hours(self, operating_hours: Optional[OperatingHours]) -> None:
        self.operating_hours = operating_hours

    def advance_game_minutes(self, minutes: int) -> ClockAdvanceResult:
        """Advance explicit game time and mark observed date-change share refreshes."""
        result = self.subday_clock.advance_minutes(minutes)
        if result.days_crossed:
            self.customer_share.on_date_change(days_crossed=result.days_crossed)
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
        """Bridge known opening hours to the existing closed-hours labor rule.

        Unknown opening hours are not treated as either open or closed, because
        silently choosing one would create a false economy result.
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
        if fixture_id not in {placement.instance_id for placement in self.grid.placements}:
            raise KeyError(f"checkout fixture is not placed on the grid: {fixture_id}")
        checkout = CheckoutStationRuntime(
            fixture_id,
            self.customers,
            self.staff,
            simultaneous_staff_capacity=simultaneous_staff_capacity,
        )
        self._checkouts[fixture_id] = checkout
        return checkout

    def add_customer(
        self,
        customer_id: str,
        *,
        entry_point: GridPoint,
        exit_point: GridPoint,
        merchandise_fixture_ids: Sequence[str] = (),
        checkout_fixture_id: Optional[str] = None,
    ) -> CustomerSession:
        session = self.customers.add_customer(
            customer_id,
            entry_point=entry_point,
            exit_point=exit_point,
            merchandise_fixture_ids=merchandise_fixture_ids,
            checkout_fixture_id=checkout_fixture_id,
        )
        self.purchases.open_basket(customer_id)
        return session

    def customer_pick_and_continue(
        self,
        customer_id: str,
        slot_id: str,
        *,
        quantity: int,
        unit_sale_price_yen: Optional[int],
        flow: PurchaseFlow,
    ) -> BasketPickResult:
        session = self.customers.customer(customer_id)
        slot = self.inventory.slot(slot_id)
        if session.state is not CustomerState.AT_MERCHANDISE:
            raise ValueError("customer is not at merchandise")
        if session.current_merchandise_fixture_id != slot.fixture_id:
            raise ValueError(
                "customer current merchandise fixture does not match inventory slot fixture"
            )
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

    def complete_checkout_sale(
        self,
        checkout_fixture_id: str,
        *,
        staff_id: str,
        customer_id: str,
    ) -> CheckoutSaleResult:
        basket = self.purchases.basket(customer_id)
        if basket.settled:
            raise ValueError("customer basket is already settled")
        if not basket.lines:
            raise ValueError("customer basket is empty")

        checkout = self._checkouts[checkout_fixture_id]
        started = checkout.begin_service(staff_id, customer_id)
        settlement = self.purchases.settle(customer_id, source_id=checkout_fixture_id)
        finished = checkout.finish_service(staff_id)
        return CheckoutSaleResult(started, settlement, finished)

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
    ) -> ReplenishAndChargeResult:
        mutation = self.inventory.replenish(
            slot_id,
            quantity,
            staff_roster=self.staff if staff_id is not None else None,
            staff_id=staff_id,
            stamina_cost=stamina_cost,
            break_room_target_id=break_room_target_id,
        )
        event = self.cash.record_procurement_mutation(mutation)
        return ReplenishAndChargeResult(mutation, event)

    def close_day(self) -> DayEndResult:
        return self.cash.close_day()
