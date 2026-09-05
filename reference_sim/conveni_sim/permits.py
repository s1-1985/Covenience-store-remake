from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Iterable, Optional

from .economy import FinancialEvent, FinancialEventKind, StoreCashLedger
from .models import PermitDefinition


class PermitApplicationTrigger(str, Enum):
    REMODEL = "remodel"
    NEW_STORE = "new_store"


class PermitEligibility(str, Enum):
    ELIGIBLE = "eligible"
    INELIGIBLE = "ineligible"
    UNKNOWN = "unknown"


class PermitApplicationOutcome(str, Enum):
    ACQUIRED = "acquired"
    ALREADY_OWNED = "already_owned"
    INELIGIBLE = "ineligible"
    ELIGIBILITY_UNKNOWN = "eligibility_unknown"
    TRIGGER_UNCONFIRMED = "trigger_unconfirmed"


@dataclass(frozen=True)
class PermitApplicationResult:
    permit_id: str
    trigger: PermitApplicationTrigger
    outcome: PermitApplicationOutcome
    fee_yen: Optional[int] = None
    financial_event: Optional[FinancialEvent] = None

    @property
    def acquired(self) -> bool:
        return self.outcome is PermitApplicationOutcome.ACQUIRED


class StorePermitRuntime:
    """Per-store sales-permit state without guessed fees or distance rules.

    First-title evidence supports three independent permit categories and ties
    changing permits on an existing Saturn store to the remodel flow.  Exact
    fees, exclusion distances and the new-store application path are still
    unresolved, so callers must supply eligibility explicitly and new-store
    acquisition remains unconfirmed rather than silently enabled.
    """

    def __init__(
        self,
        definitions: Iterable[PermitDefinition],
        cash: StoreCashLedger,
    ) -> None:
        self._definitions = {definition.id: definition for definition in definitions}
        if not self._definitions:
            raise ValueError("at least one permit definition is required")
        self.cash = cash
        self._owned: set[str] = set()
        self._history: list[PermitApplicationResult] = []

    @property
    def owned_permits(self) -> frozenset[str]:
        return frozenset(self._owned)

    @property
    def history(self) -> tuple[PermitApplicationResult, ...]:
        return tuple(self._history)

    def definition(self, permit_id: str) -> PermitDefinition:
        return self._definitions[permit_id]

    def owns(self, permit_id: str) -> bool:
        self.definition(permit_id)
        return permit_id in self._owned

    def _definition_fee_yen(self, permit_id: str) -> Optional[int]:
        fee = self.definition(permit_id).fee_yen
        if fee is None:
            return None
        value = fee.value
        if not isinstance(value, int) or value < 0:
            raise ValueError("permit fee evidence value must be a non-negative integer")
        return value

    def apply(
        self,
        permit_id: str,
        *,
        trigger: PermitApplicationTrigger,
        eligibility: PermitEligibility,
        fee_yen_override: Optional[int] = None,
    ) -> PermitApplicationResult:
        self.definition(permit_id)
        if fee_yen_override is not None and fee_yen_override < 0:
            raise ValueError("fee_yen_override must be >= 0 or None")

        if permit_id in self._owned:
            result = PermitApplicationResult(
                permit_id,
                trigger,
                PermitApplicationOutcome.ALREADY_OWNED,
            )
            self._history.append(result)
            return result

        if trigger is PermitApplicationTrigger.NEW_STORE:
            result = PermitApplicationResult(
                permit_id,
                trigger,
                PermitApplicationOutcome.TRIGGER_UNCONFIRMED,
            )
            self._history.append(result)
            return result

        if trigger is not PermitApplicationTrigger.REMODEL:
            raise ValueError(f"unsupported permit application trigger: {trigger}")

        if eligibility is PermitEligibility.UNKNOWN:
            result = PermitApplicationResult(
                permit_id,
                trigger,
                PermitApplicationOutcome.ELIGIBILITY_UNKNOWN,
            )
            self._history.append(result)
            return result

        if eligibility is PermitEligibility.INELIGIBLE:
            result = PermitApplicationResult(
                permit_id,
                trigger,
                PermitApplicationOutcome.INELIGIBLE,
            )
            self._history.append(result)
            return result

        if eligibility is not PermitEligibility.ELIGIBLE:
            raise ValueError(f"unsupported permit eligibility: {eligibility}")

        fee_yen = (
            fee_yen_override
            if fee_yen_override is not None
            else self._definition_fee_yen(permit_id)
        )
        financial_event = self.cash.record_cost(
            FinancialEventKind.PERMIT,
            fee_yen,
            source_id=permit_id,
            note="first-title sales permit acquired during remodel flow",
        )
        self._owned.add(permit_id)
        result = PermitApplicationResult(
            permit_id=permit_id,
            trigger=trigger,
            outcome=PermitApplicationOutcome.ACQUIRED,
            fee_yen=fee_yen,
            financial_event=financial_event,
        )
        self._history.append(result)
        return result
