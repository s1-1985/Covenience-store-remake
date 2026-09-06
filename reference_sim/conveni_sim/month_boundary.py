from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Optional

from .economy import StoreCashLedger


class MonthBoundaryOutcome(str, Enum):
    CONTINUE = "continue"
    BANKRUPT = "bankrupt"
    UNDETERMINED = "undetermined"


@dataclass(frozen=True)
class MonthBoundaryBankruptcyPolicy:
    """Evidence-gated month-boundary terminal rule.

    First-title PS footage and an SS play record support bankruptcy when cash is
    negative at a day/month boundary. No zero-cash sample is currently known,
    so equality with zero remains explicitly unresolved unless a future source
    supplies that rule.
    """

    bankrupt_when_negative: bool = True
    bankrupt_when_zero: Optional[bool] = None


@dataclass(frozen=True)
class MonthBoundaryResult:
    outcome: MonthBoundaryOutcome
    known_cash_yen: int
    cash_is_exact: bool

    @property
    def suppress_normal_month_start_presentation(self) -> bool:
        """Terminal bankruptcy preempts ordinary report/notification display."""
        return self.outcome is MonthBoundaryOutcome.BANKRUPT


class MonthBoundaryTerminalGate:
    """Evaluate terminal state after caller-controlled month-start settlement.

    This object deliberately does not create settlement events, derive skipped
    day costs, aggregate the four representative days, or decide report values.
    The caller first records every evidence-backed settlement event in the cash
    ledger, then invokes this gate before normal month-start presentation.
    """

    def __init__(
        self,
        ledger: StoreCashLedger,
        *,
        policy: MonthBoundaryBankruptcyPolicy = MonthBoundaryBankruptcyPolicy(),
    ) -> None:
        self.ledger = ledger
        self.policy = policy

    def evaluate(self) -> MonthBoundaryResult:
        cash = self.ledger.known_cash_yen
        exact = self.ledger.cash_is_exact

        if not exact:
            outcome = MonthBoundaryOutcome.UNDETERMINED
        elif cash < 0:
            outcome = (
                MonthBoundaryOutcome.BANKRUPT
                if self.policy.bankrupt_when_negative
                else MonthBoundaryOutcome.UNDETERMINED
            )
        elif cash == 0:
            if self.policy.bankrupt_when_zero is None:
                outcome = MonthBoundaryOutcome.UNDETERMINED
            else:
                outcome = (
                    MonthBoundaryOutcome.BANKRUPT
                    if self.policy.bankrupt_when_zero
                    else MonthBoundaryOutcome.CONTINUE
                )
        else:
            outcome = MonthBoundaryOutcome.CONTINUE

        return MonthBoundaryResult(
            outcome=outcome,
            known_cash_yen=cash,
            cash_is_exact=exact,
        )
