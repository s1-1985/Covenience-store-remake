from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from .checkout_selection_policy import (
    CheckoutCustomerSelectionPolicy,
    CheckoutSelectionCoordinator,
    CheckoutSelectionEvaluation,
)
from .customer import CustomerState, CustomerTickResult
from .customer_demand import CustomerDemandCoordinator, CustomerDemandEvaluation
from .customer_purchase_policy import (
    CustomerPurchaseCoordinator,
    CustomerPurchaseEvaluation,
    CustomerPurchasePolicy,
)
from .operating_time import ClockAdvanceResult
from .staff import StaffTask
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
    checkout_selections: tuple[CheckoutSelectionEvaluation, ...]


class StoreStepOrchestrator:
    """Compose recovered store systems into one caller-driven step.

    The caller supplies the in-game minute delta. Demand, purchase choice, staff
    task selection and checkout-customer selection are delegated to replaceable
    policies. Service duration and completion remain explicit.
    """

    def __init__(
        self,
        runtime: StoreRuntimeHarness,
        *,
        demand: Optional[CustomerDemandCoordinator] = None,
        purchases: Optional[CustomerPurchaseCoordinator] = None,
        purchase_policy: Optional[CustomerPurchasePolicy] = None,
        staff_policy: Optional[StaffTaskPolicy] = None,
        checkout_policy: Optional[CheckoutCustomerSelectionPolicy] = None,
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
        self.checkout_policy = checkout_policy
        self._staff_candidates = (
            StaffWorkCandidateDiscovery(runtime) if staff_policy is not None else None
        )
        self._staff_tasks = (
            StaffTaskPolicyCoordinator(runtime.staff) if staff_policy is not None else None
        )
        self._checkout_selection = (
            CheckoutSelectionCoordinator(runtime) if checkout_policy is not None else None
        )

    def step(self, game_minutes: int) -> StoreStepResult:
        """Advance time, demand, traffic, purchases, staff choices, then checkout starts.

        The caller controls step cadence. Checkout selection may start service for
        staff currently assigned to a checkout, but this method never finishes
        service or settles the sale; measured/recovered duration can be inserted
        between start and explicit completion later.
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

        checkout_results: list[CheckoutSelectionEvaluation] = []
        if self.checkout_policy is not None and self._checkout_selection is not None:
            for staff in self.runtime.staff.staff:
                if staff.task is not StaffTask.CHECKOUT or staff.target_id is None:
                    continue
                checkout = self.runtime.checkout(staff.target_id)
                if checkout.customer_being_served_by(staff.id) is not None:
                    continue
                checkout_results.append(
                    self._checkout_selection.evaluate(staff.id, self.checkout_policy)
                )

        return StoreStepResult(
            clock=clock,
            demand=demand_result,
            traffic=traffic,
            purchases=tuple(purchase_results),
            staff_tasks=staff_result,
            checkout_selections=tuple(checkout_results),
        )
