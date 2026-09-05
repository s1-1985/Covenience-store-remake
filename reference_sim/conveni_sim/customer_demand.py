from __future__ import annotations

from dataclasses import dataclass
from typing import Optional, Protocol, Sequence

from .customer_share import CustomerShareInputs
from .store_grid import GridPoint
from .store_runtime import CustomerAdmissionResult, StoreRuntimeHarness


@dataclass(frozen=True)
class CustomerDemandContext:
    """Snapshot supplied to a future first-title customer-demand policy.

    The reference core intentionally exposes the known context without defining
    a spawn-rate formula.  `None` keeps unresolved values explicit instead of
    treating them as neutral or zero.
    """

    absolute_minute: int
    minute_of_day: int
    elapsed_days: int
    store_open: Optional[bool]
    customer_share_percent: Optional[int]
    share_inputs: CustomerShareInputs


@dataclass(frozen=True)
class CustomerArrivalIntent:
    """One policy-produced attempt to create a gameplay customer."""

    customer_id: str
    entry_point: GridPoint
    exit_point: GridPoint
    merchandise_fixture_ids: tuple[str, ...] = ()
    checkout_fixture_id: Optional[str] = None

    def __post_init__(self) -> None:
        if not self.customer_id:
            raise ValueError("customer_id must be non-empty")


class CustomerDemandPolicy(Protocol):
    """Replaceable policy boundary for unresolved first-title demand logic."""

    def arrivals_for(self, context: CustomerDemandContext) -> Sequence[CustomerArrivalIntent]:
        ...


@dataclass(frozen=True)
class CustomerDemandEvaluation:
    context: CustomerDemandContext
    intents: tuple[CustomerArrivalIntent, ...]
    admissions: tuple[CustomerAdmissionResult, ...]


class CustomerDemandCoordinator:
    """Routes policy-produced demand through the effective opening-state gate.

    This coordinator does not invent arrival rates, time-of-day multipliers,
    share conversion, weather effects, retries, or queueing of rejected demand.
    A future recovered policy may use the supplied context and emit explicit
    intents.  Every emitted intent still passes through `admit_customer` so a
    closed or unknown store cannot be bypassed by gameplay demand.
    """

    def __init__(self, runtime: StoreRuntimeHarness, policy: CustomerDemandPolicy) -> None:
        self.runtime = runtime
        self.policy = policy

    def current_context(self) -> CustomerDemandContext:
        clock = self.runtime.subday_clock
        return CustomerDemandContext(
            absolute_minute=clock.absolute_minutes,
            minute_of_day=clock.minute_of_day,
            elapsed_days=clock.elapsed_days,
            store_open=self.runtime.store_open,
            customer_share_percent=self.runtime.customer_share.current_share_percent,
            share_inputs=self.runtime.customer_share.inputs,
        )

    def evaluate(self) -> CustomerDemandEvaluation:
        context = self.current_context()
        intents = tuple(self.policy.arrivals_for(context))
        admissions = tuple(
            self.runtime.admit_customer(
                intent.customer_id,
                entry_point=intent.entry_point,
                exit_point=intent.exit_point,
                merchandise_fixture_ids=intent.merchandise_fixture_ids,
                checkout_fixture_id=intent.checkout_fixture_id,
            )
            for intent in intents
        )
        return CustomerDemandEvaluation(
            context=context,
            intents=intents,
            admissions=admissions,
        )
