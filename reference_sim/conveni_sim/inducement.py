from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Optional

from .economy import FinancialEvent, FinancialEventKind, StoreCashLedger


class InducementPlacementState(str, Enum):
    ACTIVE = "active"
    CANCELLED = "cancelled"
    CONFIRMED = "confirmed"


@dataclass(frozen=True)
class InducementPlacementQuote:
    location_id: str
    placeable: bool
    displayed_site_cost_yen: Optional[int]


class InducementPlacementSession:
    """Evidence-bounded facility-placement transaction.

    V03 directly shows the selected facility's aid amount leaving cash when
    placement mode begins and returning in full when placement is cancelled.
    V01 police-box and V03 pool confirmation debit the location quote in
    addition to the aid already paid. Site-price calculation, affordability
    policy, construction and activation remain outside this transaction.
    """

    def __init__(
        self,
        *,
        facility_id: str,
        aid_yen: int,
        ledger: StoreCashLedger,
    ) -> None:
        if not facility_id:
            raise ValueError("facility_id must be non-empty")
        if aid_yen < 0:
            raise ValueError("aid_yen must be >= 0")
        self.facility_id = facility_id
        self.aid_yen = aid_yen
        self.ledger = ledger
        self.state = InducementPlacementState.ACTIVE
        self._quotes: list[InducementPlacementQuote] = []
        self.refund_event: Optional[FinancialEvent] = None
        self.confirmation_event: Optional[FinancialEvent] = None
        self.aid_debit_event = ledger.record_cost(
            FinancialEventKind.INDUCEMENT,
            aid_yen,
            source_id=facility_id,
            note="facility aid reserved on entering placement mode",
        )

    @property
    def quotes(self) -> tuple[InducementPlacementQuote, ...]:
        return tuple(self._quotes)

    def record_quote(
        self,
        location_id: str,
        *,
        placeable: bool,
        displayed_site_cost_yen: Optional[int] = None,
    ) -> InducementPlacementQuote:
        if self.state is not InducementPlacementState.ACTIVE:
            raise ValueError("inducement placement session is no longer active")
        if not location_id:
            raise ValueError("location_id must be non-empty")
        if displayed_site_cost_yen is not None and displayed_site_cost_yen < 0:
            raise ValueError("displayed_site_cost_yen must be >= 0 or None")
        quote = InducementPlacementQuote(
            location_id=location_id,
            placeable=placeable,
            displayed_site_cost_yen=displayed_site_cost_yen,
        )
        self._quotes.append(quote)
        return quote

    def confirm(self) -> FinancialEvent:
        """Commit the current location's explicit quote exactly once.

        This records a caller-authorized transaction; it does not decide
        whether the original game permits a purchase with insufficient cash.
        """
        if self.state is not InducementPlacementState.ACTIVE:
            raise ValueError("inducement placement session is no longer active")
        if not self._quotes:
            raise ValueError("a current placement quote is required")
        quote = self._quotes[-1]
        if not quote.placeable or quote.displayed_site_cost_yen is None:
            raise ValueError("current location must be placeable with a known site cost")
        event = self.ledger.record_cost(
            FinancialEventKind.INDUCEMENT,
            quote.displayed_site_cost_yen,
            source_id=self.facility_id,
            note=f"additional placement payment at {quote.location_id}",
        )
        self.confirmation_event = event
        self.state = InducementPlacementState.CONFIRMED
        return event

    def cancel(self) -> FinancialEvent:
        if self.state is not InducementPlacementState.ACTIVE:
            raise ValueError("inducement placement session is no longer active")
        refund = self.ledger.record_refund(
            FinancialEventKind.INDUCEMENT,
            self.aid_yen,
            source_id=self.facility_id,
            note="facility aid returned after placement cancellation",
        )
        self.refund_event = refund
        self.state = InducementPlacementState.CANCELLED
        return refund
