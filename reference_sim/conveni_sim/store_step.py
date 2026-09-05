from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from .customer import CustomerState, CustomerTickResult
from .customer_demand import CustomerDemandCoordinator, CustomerDemandEvaluation
from .customer_purchase_policy import (
    CustomerPurchaseCoordinator,
    CustomerPurchaseEvaluation,
    CustomerPurchasePolicy,
)
from .operating_time import ClockAdvanceResult
from .staff_task_policy import (
    StaffTaskPolicy,
    StaffTaskPolicyApplication,
    StaffTaskPolicyCoordinator,
)
from .staff_work_candidates import StaffWorkCandidateDiscovery
from .store_runtime import StoreRuntimeHarness


@dataclass(frozen=True)
class StoreStepResult:
    """One explicit simulation step without inventing a real-time/game-time ratio."""

    clock: ClockAdvanceResult
    demand: Optional[CustomerDemandEvaluation]
    traffic: CustomerTickResult
    purchases: tuple[CustomerPurchaseEvaluation, ...]
    staff_tasks: Optional[StaffTaskPolicyApplication]


class StoreStepOrchestrator:
    """Compose already-recovered store systems into one caller-driven step.

    The caller supplies the in-game minute delta. Demand, purchase choice and
    staff task selection are delegated to replaceable policies. This layer does
    not decide checkout service duration, staff work duration, spawn rates,
    purchase weights, queue patience, or how many real seconds correspond to
    game time.
    """

    def __init__(
        self,
        runtime: StoreRuntimeHarness,
        *,
        demand: Optional[CustomerDemandCoordinator] = None,
        purchases: Optional[CustomerPurchaseCoordinator] = None,
        purchase_policy: Optional[CustomerPurchasePolicy] = None,
        staff_policy: Optional[StaffTaskPolicy] = None,
    ) -> None:
        if (purchases is None) != (purchase_policy is None):
            raise ValueError("purchases and purchase_policy must be supplied together")
        if demand is not None and demand.runtime is not runtime:
            raise ValueError("demand coordinator must use the same store runtime")
        if purchases is not None and purchases.runtime is not runtime:
            raise ValueError("purchase coordinator must use the same store runtime")
        self.runtime = runtime
        self.demand = demand
        self.purchases = purchases
        self.purchase_policy = purchase_policy
        self.staff_policy = staff_policy
        self._staff_candidates = (
            StaffWorkCandidateDiscovery(runtime) if staff_policy is not None else None
        )
        self._staff_tasks = (
            StaffTaskPolicyCoordinator(runtime.staff) if staff_policy is not None else None
        )

    def step(self, game_minutes: int) -> StoreStepResult:
        """Advance time, arrivals, traffic, purchases, then optional staff choices.

        The ordering is intentionally narrow and observable: time gates first,
        then gameplay demand, one traffic tick, purchase decisions for customers
        physically at merchandise, and finally one caller-authorized staff task
        reconsideration.  The caller controls how often `step()` is invoked, so
        this does not define the original task-reconsideration cadence.

        Task selection only assigns factual checkout/replenish/clean candidates.
        It does not move staff, complete work, refill stock, clean cells, serve a
        checkout customer, or consume stamina automatically.
        """
        clock = self.runtime.advance_game_minutes(game_minutes)
        demand_result = self.demand.evaluate() if self.demand is not None else None
        traffic = self.runtime.customers.tick()

        purchase_results: list[CustomerPurchaseEvaluation] = []
        if self.purchases is not None and self.purchase_policy is not None:
            ready_ids = tuple(
                customer.id
                for customer in self.runtime.customers.customers
                if customer.state is CustomerState.AT_MERCHANDISE
            )
            for customer_id in ready_ids:
                purchase_results.append(
                    self.purchases.evaluate(customer_id, self.purchase_policy)
                )

        staff_result: Optional[StaffTaskPolicyApplication] = None
        if (
            self.staff_policy is not None
            and self._staff_candidates is not None
            and self._staff_tasks is not None
        ):
            staff_result = self._staff_tasks.apply_policy(
                self.staff_policy,
                self._staff_candidates.candidates_by_staff(),
            )

        return StoreStepResult(
            clock=clock,
            demand=demand_result,
            traffic=traffic,
            purchases=tuple(purchase_results),
            staff_tasks=staff_result,
        )
