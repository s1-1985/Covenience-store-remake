from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Optional

from .inventory import InventoryMutation


class CashDirection(str, Enum):
    CREDIT = "credit"
    DEBIT = "debit"


class FinancialEventKind(str, Enum):
    SALE = "sale"
    PROCUREMENT = "procurement"
    LABOR = "labor"
    FIXTURE_MAINTENANCE = "fixture_maintenance"
    PROMOTION = "promotion"
    CONSTRUCTION = "construction"
    LAND = "land"
    OTHER = "other"


class DayEndOutcome(str, Enum):
    SOLVENT = "solvent"
    BANKRUPT = "bankrupt"
    UNDETERMINED = "undetermined"
    NOT_EVALUATED = "not_evaluated"


@dataclass(frozen=True)
class FinancialEvent:
    sequence: int
    kind: FinancialEventKind
    direction: CashDirection
    amount_yen: Optional[int]
    note: str = ""
    source_id: Optional[str] = None

    @property
    def known(self) -> bool:
        return self.amount_yen is not None


@dataclass(frozen=True)
class BankruptcyPolicy:
    """Platform/observation-gated day-end bankruptcy policy.

    A detailed Saturn play record reports bankruptcy when cash is negative at
    the end of a day. PS parity is not yet independently confirmed, so the
    shared reference default does not enable that rule automatically.
    """

    check_negative_cash_at_end_of_day: bool = False


@dataclass(frozen=True)
class DaySummary:
    known_credits_yen: int
    known_debits_yen: int
    unknown_credit_events: int
    unknown_debit_events: int
    known_cash_yen: int
    cash_is_exact: bool


@dataclass(frozen=True)
class DayEndResult:
    outcome: DayEndOutcome
    summary: DaySummary


class StoreCashLedger:
    """Explicit cash-event ledger without guessed month-end formulas.

    Unknown cash effects are preserved as unknown instead of being silently
    counted as zero. Therefore `known_cash_yen` is only an exact cash balance
    while `cash_is_exact` is true.
    """

    def __init__(
        self,
        initial_cash_yen: int,
        *,
        bankruptcy_policy: BankruptcyPolicy = BankruptcyPolicy(),
    ) -> None:
        if initial_cash_yen < 0:
            raise ValueError("initial_cash_yen must be >= 0")
        self.initial_cash_yen = initial_cash_yen
        self.bankruptcy_policy = bankruptcy_policy
        self._events: list[FinancialEvent] = []
        self._day_start_index = 0

    @property
    def events(self) -> tuple[FinancialEvent, ...]:
        return tuple(self._events)

    @property
    def known_cash_yen(self) -> int:
        balance = self.initial_cash_yen
        for event in self._events:
            if event.amount_yen is None:
                continue
            if event.direction is CashDirection.CREDIT:
                balance += event.amount_yen
            else:
                balance -= event.amount_yen
        return balance

    @property
    def cash_is_exact(self) -> bool:
        return all(event.amount_yen is not None for event in self._events)

    def _record(
        self,
        kind: FinancialEventKind,
        direction: CashDirection,
        amount_yen: Optional[int],
        *,
        note: str = "",
        source_id: Optional[str] = None,
    ) -> FinancialEvent:
        if amount_yen is not None and amount_yen < 0:
            raise ValueError("amount_yen must be >= 0 or None")
        event = FinancialEvent(
            sequence=len(self._events),
            kind=kind,
            direction=direction,
            amount_yen=amount_yen,
            note=note,
            source_id=source_id,
        )
        self._events.append(event)
        return event

    def record_sale(
        self,
        amount_yen: Optional[int],
        *,
        source_id: Optional[str] = None,
        note: str = "",
    ) -> FinancialEvent:
        return self._record(
            FinancialEventKind.SALE,
            CashDirection.CREDIT,
            amount_yen,
            source_id=source_id,
            note=note,
        )

    def record_cost(
        self,
        kind: FinancialEventKind,
        amount_yen: Optional[int],
        *,
        source_id: Optional[str] = None,
        note: str = "",
    ) -> FinancialEvent:
        if kind is FinancialEventKind.SALE:
            raise ValueError("use record_sale for revenue")
        return self._record(
            kind,
            CashDirection.DEBIT,
            amount_yen,
            source_id=source_id,
            note=note,
        )

    def record_procurement_mutation(self, mutation: InventoryMutation) -> FinancialEvent:
        if mutation.quantity_delta <= 0:
            raise ValueError("only replenishment mutations create procurement spending")
        return self.record_cost(
            FinancialEventKind.PROCUREMENT,
            mutation.procurement_cost_yen,
            source_id=mutation.slot_id,
            note=f"{mutation.product_id} +{mutation.quantity_delta}",
        )

    def record_labor_cost_if_open(
        self,
        amount_yen: Optional[int],
        *,
        store_open: bool,
        staff_id: Optional[str] = None,
    ) -> Optional[FinancialEvent]:
        """Record labor only while open; closed-hours labor is reported as uncharged.

        This method deliberately does not suppress every other maintenance cost,
        because current evidence says 'many' operating costs stop while closed
        but does not yet enumerate every category.
        """
        if not store_open:
            return None
        return self.record_cost(
            FinancialEventKind.LABOR,
            amount_yen,
            source_id=staff_id,
        )

    def day_summary(self) -> DaySummary:
        day_events = self._events[self._day_start_index :]
        known_credits = sum(
            event.amount_yen or 0
            for event in day_events
            if event.direction is CashDirection.CREDIT and event.amount_yen is not None
        )
        known_debits = sum(
            event.amount_yen or 0
            for event in day_events
            if event.direction is CashDirection.DEBIT and event.amount_yen is not None
        )
        unknown_credits = sum(
            1
            for event in day_events
            if event.direction is CashDirection.CREDIT and event.amount_yen is None
        )
        unknown_debits = sum(
            1
            for event in day_events
            if event.direction is CashDirection.DEBIT and event.amount_yen is None
        )
        return DaySummary(
            known_credits_yen=known_credits,
            known_debits_yen=known_debits,
            unknown_credit_events=unknown_credits,
            unknown_debit_events=unknown_debits,
            known_cash_yen=self.known_cash_yen,
            cash_is_exact=self.cash_is_exact,
        )

    def close_day(self) -> DayEndResult:
        summary = self.day_summary()
        if not self.bankruptcy_policy.check_negative_cash_at_end_of_day:
            outcome = DayEndOutcome.NOT_EVALUATED
        elif not summary.cash_is_exact:
            outcome = DayEndOutcome.UNDETERMINED
        elif summary.known_cash_yen < 0:
            outcome = DayEndOutcome.BANKRUPT
        else:
            outcome = DayEndOutcome.SOLVENT

        self._day_start_index = len(self._events)
        return DayEndResult(outcome=outcome, summary=summary)
