from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from .checkout_selection_policy import (
    CheckoutCustomerSelectionPolicy,
    CheckoutSelectionCoordinator,
    CheckoutSelectionEvaluation,
)
from .checkout_service_timing import (
    CheckoutServiceDurationPolicy,
    CheckoutServiceTimingCoordinator,
    CheckoutServiceTimingEvaluation,
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
    checkout_timing: tuple[CheckoutServiceTimingEvaluation, ...]
    demand: Optional[CustomerDemandEvaluation]
    traffic: CustomerTickResult
    purchases: tuple[CustomerPurchaseEvaluation, ...]
    staff_tasks: Optional[StaffTaskPolicyApplication]
    checkout_selections: tuple[CheckoutSelectionEvaluation, ...]


class StoreStepOrchestrator:
    """Compose recovered store systems into one caller-driven step.

    The caller supplies the in-game minute delta. Demand, purchase choice, staff
    task selection, checkout-customer selection and optional checkout duration
    are delegated to replaceable policies. No original timing coefficient is
    invented by this layer.
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
        checkout_timing: Optional[CheckoutServiceTimingCoordinator] = None,
        checkout_duration_policy: Optional[CheckoutServiceDurationPolicy] = None,
    ) -> None:
        if (purchases is None) != (purchase_policy is None):
            raise ValueError("purchases and purchase_policy must be supplied together")
        if (checkout_timing is None) != (checkout_duration_policy is None):
            raise ValueError(
                "checkout_timing and checkout_duration_policy must be supplied together"
            )
        if demand is not None and demand.runtime is not runtime:
            raise ValueError("demand coordinator must use the same store runtime")
        if purchases is not None and purchases.runtime is not runtime:
            raise ValueError("purchase coordinator must use the same store runtime")
        if checkout_timing is not None and checkout_timing.runtime is not runtime:
            raise ValueError("checkout timing coordinator must use the same store runtime")
        self.runtime = runtime
        self.demand = demand
        self.purchases = purchases
        self.purchase_policy = purchase_policy
        self.staff_policy = staff_policy
        self.checkout_policy = checkout_policy
        self.checkout_timing = checkout_timing
        self.checkout_duration_policy = checkout_duration_policy
        self._staff_candidates = (
            StaffWorkCandidateDiscovery(runtime) if staff_policy is not None else None
        )
        self._staff_tasks = (
            StaffTaskPolicyCoordinator(runtime.staff) if staff_policy is not None else None
        )
        self._checkout_selection = (
            CheckoutSelectionCoordinator(runtime) if checkout_policy is not None else None
        )

    def _active_checkout_staff_ids(self) -> tuple[str, ...]:
        active: list[str] = []
        for fixture_id in self.runtime.checkout_fixture_ids:
            checkout = self.runtime.checkout(fixture_id)
            active.extend(record.staff_id for record in checkout.active_services)
        return tuple(active)

    def step(self, game_minutes: int) -> StoreStepResult:
        """Advance one policy-driven store step.

        The caller controls step cadence. Timed checkout completion is optional:
        when both a timing coordinator and duration policy are supplied, services
        that were registered on an earlier step are evaluated immediately after
        the game clock advances. Completed services settle through the existing
        checkout path before traffic moves.

        A staff member with an active checkout service is locked out of the
        generic task selector until that service is completed or cancelled.
        Checkout services started by this orchestrator are registered with the
        timing coordinator at the current absolute game minute, so later steps
        can complete them without an external finish call.

        Without checkout timing inputs, the previous explicit-completion
        behavior is preserved.
        """
        clock = self.runtime.advance_game_minutes(game_minutes)

        checkout_timing_results: tuple[CheckoutServiceTimingEvaluation, ...] = ()
        if (
            self.checkout_timing is not None
            and self.checkout_duration_policy is not None
        ):
            checkout_timing_results = self.checkout_timing.evaluate_all(
                self.checkout_duration_policy
            )

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
                locked_staff_ids=self._active_checkout_staff_ids(),
            )

        checkout_results: list[CheckoutSelectionEvaluation] = []
        if self.checkout_policy is not None and self._checkout_selection is not None:
            for staff in self.runtime.staff.staff:
                if staff.task is not StaffTask.CHECKOUT or staff.target_id is None:
                    continue
                checkout = self.runtime.checkout(staff.target_id)
                if checkout.customer_being_served_by(staff.id) is not None:
                    continue
                evaluation = self._checkout_selection.evaluate(
                    staff.id,
                    self.checkout_policy,
                )
                checkout_results.append(evaluation)
                if (
                    evaluation.service_started is not None
                    and self.checkout_timing is not None
                ):
                    self.checkout_timing.register_started(evaluation.service_started)

        return StoreStepResult(
            clock=clock,
            checkout_timing=checkout_timing_results,
            demand=demand_result,
            traffic=traffic,
            purchases=tuple(purchase_results),
            staff_tasks=staff_result,
            checkout_selections=tuple(checkout_results),
        )
