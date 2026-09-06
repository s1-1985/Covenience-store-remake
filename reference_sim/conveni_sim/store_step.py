from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from .checkout_anger_timing import (
    CheckoutAngerTimingCoordinator,
    CheckoutAngerTimingEvaluation,
    CheckoutAngerTriggerPolicy,
)
from .checkout_selection_policy import (
    CheckoutCustomerSelectionPolicy,
    CheckoutSelectionCoordinator,
    CheckoutSelectionEvaluation,
)
from .checkout_service_timing import (
    CheckoutServiceCompletionEffectsPolicy,
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
from .staff_growth_resolution import (
    EvidenceBackedStaffGrowthResolver,
    StaffGrowthResolution,
)
from .staff_rest_timing import (
    StaffRestTimingCoordinator,
    StaffRestTimingEvaluation,
    StaffRestTransitionPolicy,
)
from .staff_task_policy import (
    StaffTaskPolicy,
    StaffTaskPolicyApplication,
    StaffTaskPolicyCoordinator,
)
from .staff_work_candidates import StaffWorkCandidateDiscovery
from .staff_work_interruption import (
    StaffWorkInterruptionCoordinator,
    StaffWorkInterruptionEvaluation,
    StaffWorkInterruptionPolicy,
)
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
    staff_rest_timing: tuple[StaffRestTimingEvaluation, ...]
    checkout_anger_timing: tuple[CheckoutAngerTimingEvaluation, ...]
    checkout_timing: tuple[CheckoutServiceTimingEvaluation, ...]
    staff_work_timing: tuple[StaffWorkTimingEvaluation, ...]
    staff_work_interruptions: tuple[StaffWorkInterruptionEvaluation, ...]
    staff_growth: tuple[StaffGrowthResolution, ...]
    demand: Optional[CustomerDemandEvaluation]
    traffic: CustomerTickResult
    purchases: tuple[CustomerPurchaseEvaluation, ...]
    staff_tasks: Optional[StaffTaskPolicyApplication]
    checkout_selections: tuple[CheckoutSelectionEvaluation, ...]


class StoreStepOrchestrator:
    """Compose recovered store systems into one caller-driven step.

    The caller supplies the in-game minute delta. Demand, purchase choice, staff
    task selection, checkout-customer selection, optional checkout duration and
    completion effects, optional checkout-pressure anger triggering, optional
    replenish/clean completion/interruption, optional recovered work growth and
    optional rest transitions are delegated to replaceable layers. No unresolved
    original timing, patience, interruption threshold or stamina coefficient is
    invented.
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
        checkout_completion_effects_policy: Optional[CheckoutServiceCompletionEffectsPolicy] = None,
        checkout_anger_timing: Optional[CheckoutAngerTimingCoordinator] = None,
        checkout_anger_policy: Optional[CheckoutAngerTriggerPolicy] = None,
        staff_work_timing: Optional[StaffWorkTimingCoordinator] = None,
        staff_work_completion_policy: Optional[StaffWorkCompletionPolicy] = None,
        staff_work_interruption_policy: Optional[StaffWorkInterruptionPolicy] = None,
        staff_growth_resolver: Optional[EvidenceBackedStaffGrowthResolver] = None,
        staff_rest_timing: Optional[StaffRestTimingCoordinator] = None,
        staff_rest_transition_policy: Optional[StaffRestTransitionPolicy] = None,
    ) -> None:
        if (purchases is None) != (purchase_policy is None):
            raise ValueError("purchases and purchase_policy must be supplied together")
        if (checkout_timing is None) != (checkout_duration_policy is None):
            raise ValueError(
                "checkout_timing and checkout_duration_policy must be supplied together"
            )
        if checkout_completion_effects_policy is not None and checkout_timing is None:
            raise ValueError(
                "checkout_completion_effects_policy requires checkout timing"
            )
        if (checkout_anger_timing is None) != (checkout_anger_policy is None):
            raise ValueError(
                "checkout_anger_timing and checkout_anger_policy must be supplied together"
            )
        if (staff_work_timing is None) != (staff_work_completion_policy is None):
            raise ValueError(
                "staff_work_timing and staff_work_completion_policy must be supplied together"
            )
        if staff_work_interruption_policy is not None and staff_work_timing is None:
            raise ValueError("staff work interruption requires staff work timing")
        if (staff_rest_timing is None) != (staff_rest_transition_policy is None):
            raise ValueError(
                "staff_rest_timing and staff_rest_transition_policy must be supplied together"
            )
        if demand is not None and demand.runtime is not runtime:
            raise ValueError("demand coordinator must use the same store runtime")
        if purchases is not None and purchases.runtime is not runtime:
            raise ValueError("purchase coordinator must use the same store runtime")
        if checkout_timing is not None and checkout_timing.runtime is not runtime:
            raise ValueError("checkout timing coordinator must use the same store runtime")
        if checkout_anger_timing is not None and checkout_anger_timing.runtime is not runtime:
            raise ValueError("checkout anger timing coordinator must use the same store runtime")
        if staff_work_timing is not None and staff_work_timing.runtime is not runtime:
            raise ValueError("staff work timing coordinator must use the same store runtime")
        if staff_growth_resolver is not None and staff_growth_resolver.roster is not runtime.staff:
            raise ValueError("staff growth resolver must use the same store roster")
        if staff_rest_timing is not None and staff_rest_timing.runtime is not runtime:
            raise ValueError("staff rest timing coordinator must use the same store runtime")
        self.runtime = runtime
        self.demand = demand
        self.purchases = purchases
        self.purchase_policy = purchase_policy
        self.staff_policy = staff_policy
        self.checkout_policy = checkout_policy
        self.checkout_timing = checkout_timing
        self.checkout_duration_policy = checkout_duration_policy
        self.checkout_completion_effects_policy = checkout_completion_effects_policy
        self.checkout_anger_timing = checkout_anger_timing
        self.checkout_anger_policy = checkout_anger_policy
        self.staff_work_timing = staff_work_timing
        self.staff_work_completion_policy = staff_work_completion_policy
        self.staff_work_interruption_policy = staff_work_interruption_policy
        self.staff_growth_resolver = staff_growth_resolver
        self.staff_rest_timing = staff_rest_timing
        self.staff_rest_transition_policy = staff_rest_transition_policy
        self._staff_candidates = (
            StaffWorkCandidateDiscovery(runtime) if staff_policy is not None else None
        )
        self._staff_tasks = (
            StaffTaskPolicyCoordinator(runtime.staff) if staff_policy is not None else None
        )
        self._staff_work_interruption = (
            StaffWorkInterruptionCoordinator(runtime, staff_work_timing)
            if staff_work_timing is not None and staff_work_interruption_policy is not None
            else None
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

        Existing rest states are evaluated immediately after the game clock
        advances. Existing checkout-pressure states are then evaluated before a
        checkout may complete in the same step. Timed checkout and non-checkout
        work follow. After demand/traffic/purchase updates, an optional explicit
        work-interruption policy may release active replenish/clean work in
        response to factual checkout demand. Ordinary staff task selection then
        runs, so a released staff member may choose checkout in that same step.

        With no interruption policy, active replenish/clean work remains locked
        exactly as before; checkout demand alone never cancels it.
        """
        clock = self.runtime.advance_game_minutes(game_minutes)

        staff_rest_timing_results: tuple[StaffRestTimingEvaluation, ...] = ()
        if (
            self.staff_rest_timing is not None
            and self.staff_rest_transition_policy is not None
        ):
            self.staff_rest_timing.sync_from_roster()
            staff_rest_timing_results = self.staff_rest_timing.evaluate_all(
                self.staff_rest_transition_policy
            )

        checkout_anger_timing_results: tuple[CheckoutAngerTimingEvaluation, ...] = ()
        if self.checkout_anger_timing is not None and self.checkout_anger_policy is not None:
            checkout_anger_timing_results = self.checkout_anger_timing.evaluate_all(
                self.checkout_anger_policy
            )

        checkout_timing_results: tuple[CheckoutServiceTimingEvaluation, ...] = ()
        if (
            self.checkout_timing is not None
            and self.checkout_duration_policy is not None
        ):
            checkout_timing_results = self.checkout_timing.evaluate_all(
                self.checkout_duration_policy,
                completion_effects_policy=self.checkout_completion_effects_policy,
            )

        staff_work_timing_results: tuple[StaffWorkTimingEvaluation, ...] = ()
        if (
            self.staff_work_timing is not None
            and self.staff_work_completion_policy is not None
        ):
            staff_work_timing_results = self.staff_work_timing.evaluate_all(
                self.staff_work_completion_policy
            )

        staff_growth_results: tuple[StaffGrowthResolution, ...] = ()
        if self.staff_growth_resolver is not None:
            staff_growth_results = self.staff_growth_resolver.resolve_supported_pending()

        if self.staff_rest_timing is not None:
            self.staff_rest_timing.sync_from_roster()

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

        if self.checkout_anger_timing is not None:
            self.checkout_anger_timing.sync_from_runtime()

        staff_work_interruption_results: tuple[StaffWorkInterruptionEvaluation, ...] = ()
        if (
            self._staff_work_interruption is not None
            and self.staff_work_interruption_policy is not None
        ):
            staff_work_interruption_results = self._staff_work_interruption.evaluate_all(
                self.staff_work_interruption_policy
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
                current_minute_of_day=self.runtime.subday_clock.minute_of_day,
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
                if evaluation.service_started is not None and self.checkout_timing is not None:
                    self.checkout_timing.register_started(evaluation.service_started)

        if self.checkout_anger_timing is not None:
            self.checkout_anger_timing.sync_from_runtime()

        return StoreStepResult(
            clock=clock,
            staff_rest_timing=staff_rest_timing_results,
            checkout_anger_timing=checkout_anger_timing_results,
            checkout_timing=checkout_timing_results,
            staff_work_timing=staff_work_timing_results,
            staff_work_interruptions=staff_work_interruption_results,
            staff_growth=staff_growth_results,
            demand=demand_result,
            traffic=traffic,
            purchases=tuple(purchase_results),
            staff_tasks=staff_result,
            checkout_selections=tuple(checkout_results),
        )
