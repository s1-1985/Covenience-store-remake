from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional

from .economy import FinancialEvent, StoreCashLedger
from .inventory import InventoryMutation, StoreInventoryRuntime


@dataclass(frozen=True)
class PurchaseLine:
    slot_id: str
    fixture_id: str
    product_id: str
    quantity: int
    unit_sale_price_yen: Optional[int]

    @property
    def line_total_yen(self) -> Optional[int]:
        if self.unit_sale_price_yen is None:
            return None
        return self.quantity * self.unit_sale_price_yen


@dataclass
class CustomerBasket:
    customer_id: str
    lines: list[PurchaseLine] = field(default_factory=list)
    settled: bool = False

    @property
    def known_subtotal_yen(self) -> int:
        return sum(line.line_total_yen or 0 for line in self.lines)

    @property
    def unknown_price_line_count(self) -> int:
        return sum(1 for line in self.lines if line.line_total_yen is None)

    @property
    def exact_total_yen(self) -> Optional[int]:
        if self.unknown_price_line_count:
            return None
        return self.known_subtotal_yen


@dataclass(frozen=True)
class BasketPickResult:
    inventory_mutation: InventoryMutation
    purchase_line: PurchaseLine


@dataclass(frozen=True)
class SaleSettlement:
    customer_id: str
    known_revenue_yen: int
    unknown_price_line_count: int
    financial_events: tuple[FinancialEvent, ...]

    @property
    def exact_total_yen(self) -> Optional[int]:
        if self.unknown_price_line_count:
            return None
        return self.known_revenue_yen


class StorePurchaseRuntime:
    """Explicit inventory-pick -> basket -> cash-settlement bridge.

    This runtime never chooses products, quantities or prices. Those values must
    come from source-backed masters or an external policy. It also does not
    decide whether settlement happens through a staffed checkout or a
    self-service fixture; the caller chooses when to settle the basket.
    """

    def __init__(self, inventory: StoreInventoryRuntime, cash: StoreCashLedger) -> None:
        self.inventory = inventory
        self.cash = cash
        self._baskets: dict[str, CustomerBasket] = {}
        self._settlements: list[SaleSettlement] = []

    @property
    def settlements(self) -> tuple[SaleSettlement, ...]:
        return tuple(self._settlements)

    def basket(self, customer_id: str) -> CustomerBasket:
        return self._baskets[customer_id]

    def open_basket(self, customer_id: str) -> CustomerBasket:
        if customer_id in self._baskets:
            raise ValueError(f"basket already exists for customer {customer_id!r}")
        basket = CustomerBasket(customer_id)
        self._baskets[customer_id] = basket
        return basket

    def pick_from_inventory(
        self,
        customer_id: str,
        slot_id: str,
        *,
        quantity: int,
        unit_sale_price_yen: Optional[int],
    ) -> BasketPickResult:
        basket = self._baskets[customer_id]
        if basket.settled:
            raise ValueError("cannot add items to a settled basket")
        if unit_sale_price_yen is not None and unit_sale_price_yen < 0:
            raise ValueError("unit_sale_price_yen must be >= 0 or None")

        slot = self.inventory.slot(slot_id)
        mutation = self.inventory.take_for_customer(slot_id, quantity)
        line = PurchaseLine(
            slot_id=slot.id,
            fixture_id=slot.fixture_id,
            product_id=slot.product_id,
            quantity=quantity,
            unit_sale_price_yen=unit_sale_price_yen,
        )
        basket.lines.append(line)
        return BasketPickResult(mutation, line)

    def settle(self, customer_id: str, *, source_id: Optional[str] = None) -> SaleSettlement:
        basket = self._baskets[customer_id]
        if basket.settled:
            raise ValueError("basket has already been settled")
        if not basket.lines:
            raise ValueError("cannot settle an empty basket")

        events: list[FinancialEvent] = []
        known_subtotal = basket.known_subtotal_yen
        unknown_line_count = basket.unknown_price_line_count

        if known_subtotal > 0 or unknown_line_count == 0:
            events.append(
                self.cash.record_sale(
                    known_subtotal,
                    source_id=source_id or customer_id,
                    note="known basket subtotal",
                )
            )
        if unknown_line_count:
            events.append(
                self.cash.record_sale(
                    None,
                    source_id=source_id or customer_id,
                    note=f"{unknown_line_count} basket line(s) have unknown sale price",
                )
            )

        basket.settled = True
        settlement = SaleSettlement(
            customer_id=customer_id,
            known_revenue_yen=known_subtotal,
            unknown_price_line_count=unknown_line_count,
            financial_events=tuple(events),
        )
        self._settlements.append(settlement)
        return settlement
