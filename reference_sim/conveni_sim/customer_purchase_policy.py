from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Optional, Protocol, Sequence

from .customer import CustomerState, PurchaseFlow
from .purchases import BasketPickResult
from .store_runtime import StoreRuntimeHarness


@dataclass(frozen=True)
class MerchandiseOffer:
    """Caller-supplied sellable offer for one inventory slot.

    Sale price and staffed/self-service flow are supplied by merchandising data,
    not invented by the customer AI.  `None` price remains explicitly unknown.
    """

    slot_id: str
    unit_sale_price_yen: Optional[int]
    flow: PurchaseFlow

    def __post_init__(self) -> None:
        if not self.slot_id:
            raise ValueError("slot_id must be non-empty")
        if self.unit_sale_price_yen is not None and self.unit_sale_price_yen < 0:
            raise ValueError("unit_sale_price_yen must be >= 0 or None")


@dataclass(frozen=True)
class MerchandiseOfferSnapshot:
    slot_id: str
    fixture_id: str
    product_id: str
    units_available: int
    unit_sale_price_yen: Optional[int]
    flow: PurchaseFlow


@dataclass(frozen=True)
class CustomerPurchaseContext:
    """Known state visible to a future first-title purchase-choice policy."""

    customer_id: str
    current_fixture_id: str
    merchandise_visit_index: int
    purchased_fixture_ids: tuple[str, ...]
    basket_line_count: int
    basket_known_subtotal_yen: int
    basket_unknown_price_line_count: int
    offers: tuple[MerchandiseOfferSnapshot, ...]


class PurchaseDecisionAction(str, Enum):
    BUY = "buy"
    SKIP = "skip"


@dataclass(frozen=True)
class CustomerPurchaseDecision:
    action: PurchaseDecisionAction
    slot_id: Optional[str] = None
    quantity: Optional[int] = None

    def __post_init__(self) -> None:
        if self.action is PurchaseDecisionAction.BUY:
            if not self.slot_id:
                raise ValueError("buy decision requires slot_id")
            if self.quantity is None or self.quantity <= 0:
                raise ValueError("buy decision requires positive quantity")
        else:
            if self.slot_id is not None or self.quantity is not None:
                raise ValueError("skip decision must not include slot_id or quantity")

    @classmethod
    def buy(cls, slot_id: str, quantity: int = 1) -> "CustomerPurchaseDecision":
        return cls(PurchaseDecisionAction.BUY, slot_id=slot_id, quantity=quantity)

    @classmethod
    def skip(cls) -> "CustomerPurchaseDecision":
        return cls(PurchaseDecisionAction.SKIP)


class CustomerPurchasePolicy(Protocol):
    """Replaceable boundary for unresolved first-title product-choice logic."""

    def choose_purchase(
        self,
        context: CustomerPurchaseContext,
    ) -> Optional[CustomerPurchaseDecision]: ...


@dataclass(frozen=True)
class CustomerPurchaseEvaluation:
    context: CustomerPurchaseContext
    decision: Optional[CustomerPurchaseDecision]
    pick_result: Optional[BasketPickResult]


class CustomerPurchaseCoordinator:
    """Apply explicit purchase choices without inventing demand probabilities.

    The coordinator exposes only in-stock offers at the fixture the customer has
    already reached.  A policy may buy one supplied offer, explicitly skip the
    stop, or return no decision.  Product preference, primary/add-on weights,
    fixture attention, budget distribution and price elasticity remain policy or
    future master-data concerns.
    """

    def __init__(
        self,
        runtime: StoreRuntimeHarness,
        offers: Sequence[MerchandiseOffer],
    ) -> None:
        self.runtime = runtime
        self._offers = tuple(offers)
        slot_ids = [offer.slot_id for offer in self._offers]
        if len(slot_ids) != len(set(slot_ids)):
            raise ValueError("each inventory slot may have at most one merchandise offer")

    def current_context(self, customer_id: str) -> CustomerPurchaseContext:
        session = self.runtime.customers.customer(customer_id)
        if session.state is not CustomerState.AT_MERCHANDISE:
            raise ValueError("customer is not at merchandise")
        fixture_id = session.current_merchandise_fixture_id
        if fixture_id is None:
            raise RuntimeError("AT_MERCHANDISE without current fixture")

        snapshots: list[MerchandiseOfferSnapshot] = []
        for offer in self._offers:
            slot = self.runtime.inventory.slot(offer.slot_id)
            if slot.fixture_id != fixture_id or slot.units <= 0:
                continue
            snapshots.append(
                MerchandiseOfferSnapshot(
                    slot_id=slot.id,
                    fixture_id=slot.fixture_id,
                    product_id=slot.product_id,
                    units_available=slot.units,
                    unit_sale_price_yen=offer.unit_sale_price_yen,
                    flow=offer.flow,
                )
            )

        basket = self.runtime.purchases.basket(customer_id)
        return CustomerPurchaseContext(
            customer_id=customer_id,
            current_fixture_id=fixture_id,
            merchandise_visit_index=session.next_merchandise_index,
            purchased_fixture_ids=session.interacted_fixture_ids,
            basket_line_count=len(basket.lines),
            basket_known_subtotal_yen=basket.known_subtotal_yen,
            basket_unknown_price_line_count=basket.unknown_price_line_count,
            offers=tuple(snapshots),
        )

    def evaluate(
        self,
        customer_id: str,
        policy: CustomerPurchasePolicy,
    ) -> CustomerPurchaseEvaluation:
        context = self.current_context(customer_id)
        decision = policy.choose_purchase(context)
        if decision is None:
            return CustomerPurchaseEvaluation(context, None, None)

        if decision.action is PurchaseDecisionAction.SKIP:
            self.runtime.customer_skip_and_continue(customer_id)
            return CustomerPurchaseEvaluation(context, decision, None)

        selected = next(
            (offer for offer in context.offers if offer.slot_id == decision.slot_id),
            None,
        )
        if selected is None:
            raise ValueError("policy selected a slot that is not an in-stock offer at this fixture")
        assert decision.quantity is not None
        if decision.quantity > selected.units_available:
            raise ValueError("policy selected a quantity larger than available stock")

        pick = self.runtime.customer_pick_and_continue(
            customer_id,
            selected.slot_id,
            quantity=decision.quantity,
            unit_sale_price_yen=selected.unit_sale_price_yen,
            flow=selected.flow,
        )
        return CustomerPurchaseEvaluation(context, decision, pick)
