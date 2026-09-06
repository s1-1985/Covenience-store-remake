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
from .staff_work_timing import (
    TIMED_STAFF_WORK_TASKS,
    StaffWorkCompletionPolicy,
    StaffWorkTimingCoordinator,
    StaffWorkTimingEvaluation,
)
from .store_runtime import StoreRuntimeHarness


@dataclass(frozen=True)
class StoreStepResult:
    """One explicit simulation step without inventing a real-time/game-time ratio."""

    clock: ClockAdvanceResult
    checkout_timing: tuple[CheckoutServiceTimingEvaluation, ...]
    staff_work_timing: tuple[StaffWorkTimingEvaluation, ...]
    demand: Optional[CustomerDemandEvaluation]
    traffic: CustomerTickResult
    purchases: tuple[CustomerPurchaseEvaluation, ...]
    staff_tasks: Optional[StaffTaskPolicyApplication]
    checkout_selections: tuple[CheckoutSelectionEvaluation, ...]


class StoreStepOrchestrator:
    """Compose recovered store systems into one caller-driven step.

    The caller supplies the in-game minute delta. Demand, purchase choice, staff
    task selection, checkout-customer selection, optional checkout duration and
    optional replenish/clean completion are delegated to replaceable policies.
    No original timing coefficient is invented by this layer.
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
        staff_work_timing: Optional[StaffWorkTimingCoordinator] = None,
        staff_work_completion_policy: Optional[StaffWorkCompletionPolicy] = None,
    ) -> None:
        if (purchases is None) != (purchase_policy is None):
            raise ValueError("purchases and purchase_policy must be supplied together")
        if (checkout_timing is None) != (checkout_duration_policy is None):
            raise ValueError(
                "checkout_timing and checkout_duration_policy must be supplied together"
            )
        if (staff_work_timing is None) != (staff_work_completion_policy is None):
            raise ValueError(
                "staff_work_timing and staff_work_completion_policy must be supplied together"
            )
        if demand is not None and demand.runtime is not runtime:
            raise ValueError("demand coordinator must use the same store runtime")
        if purchases is not None and purchases.runtime is not runtime:
            raise ValueError("purchase coordinator must use the same store runtime")
        if checkout_timing is not None and checkout_timing.runtime is not runtime:
            raise ValueError("checkout timing coordinator must use the same store runtime")
        if staff_work_timing is not None and staff_work_timing.runtime is not runtime:
            raise ValueError("staff work timing coordinator must use the same store runtime")
        self.runtime = runtime
        self.demand = demand
        self.purchases = purchases
        self.purchase_policy = purchase_policy
        self.staff_policy = staff_policy
        self.checkout_policy = checkout_policy
        self.checkout_timing = checkout_timing
        self.checkout_duration_policy = checkout_duration_policy
        self.staff_work_timing = staff_work_timing
        self.staff_work_completion_policy = staff_work_completion_policy
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

    def _locked_staff_ids(self) -> tuple[str, ...]:
        locked = list(self._active_checkout_staff_ids())
        if self.staff_work_timing is not None:
            locked.extend(self.staff_work_timing.active_staff_ids)
        return tuple(locked)

    def step(self, game_minutes: int) -> StoreStepResult:
        """Advance one policy-driven store step.

        The caller controls step cadence. Timed checkout and non-checkout work
        completion are optional. Existing registered work is evaluated after the
        game clock advances; completed work uses the existing settlement,
        replenishment or cleaning paths before demand/traffic and new task
        selection run.

        Staff inside an active timed work lifecycle are locked out of the generic
        task selector until completion, stale-target release or explicit
        unregistration. Newly selected checkout/replenish/clean work is
        registered at the current absolute game minute for later steps.

        Omitting either timing-policy pair preserves the prior explicit behavior
        for that work type.
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

        staff_work_timing_results: tuple[StaffWorkTimingEvaluation, ...] = ()
        if (
            self.staff_work_timing is not None
            and self.staff_work_completion_policy is not None
        ):
            staff_work_timing_results = self.staff_work_timing.evaluate_all(
                self.staff_work_completion_policy
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
                locked_staff_ids=self._locked_staff_ids(),
            )
            if self.staff_work_timing is not None:
                for applied in staff_result.applied:
                    if applied.decision.task in TIMED_STAFF_WORK_TASKS:
                        self.staff_work_timing.register_assigned(applied.staff_id)

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
            staff_work_timing=staff_work_timing_results,
            demand=demand_result,
            traffic=traffic,
            purchases=tuple(purchase_results),
            staff_tasks=staff_result,
            checkout_selections=tuple(checkout_results),
        )
