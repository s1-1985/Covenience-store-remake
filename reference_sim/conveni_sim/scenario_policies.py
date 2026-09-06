from __future__ import annotations

from dataclasses import dataclass
from typing import Optional, Sequence

from .checkout_selection_policy import CheckoutSelectionContext
from .checkout_service_timing import (
    CheckoutServiceCompletionEffects,
    CheckoutServiceTimingContext,
)
from .customer_demand import (
    CustomerArrivalIntent,
    CustomerDemandContext,
)
from .customer_purchase_policy import (
    CustomerPurchaseContext,
    CustomerPurchaseDecision,
)
from .staff import StaffCondition, StaffTask
from .staff_rest_timing import (
    StaffRestTimingContext,
    StaffRestTransitionDecision,
)
from .staff_task_policy import StaffTaskDecision, StaffTaskDecisionContext
from .staff_work_timing import (
    StaffWorkCompletionDecision,
    StaffWorkTimingContext,
)
from .store_grid import GridPoint


@dataclass(frozen=True)
class ScheduledScenarioCustomer:
    minute_of_day: int
    customer_id: str

    def __post_init__(self) -> None:
        if not 0 <= self.minute_of_day < 24 * 60:
            raise ValueError("minute_of_day must be within 0..1439")
        if not self.customer_id:
            raise ValueError("customer_id must not be empty")


class ScheduledScenarioDemandPolicy:
    """Emit explicit one-day scenario arrivals when their configured minute is due.

    This is a deterministic scenario/test policy, not a recovered first-title
    demand formula. A coarse store-step cadence may delay an arrival until the
    first policy evaluation after its configured minute.
    """

    def __init__(
        self,
        schedule: Sequence[ScheduledScenarioCustomer],
        *,
        entry_point: GridPoint,
        exit_point: GridPoint,
        merchandise_fixture_ids: Sequence[str],
        checkout_fixture_id: Optional[str],
    ) -> None:
        self.schedule = tuple(sorted(schedule, key=lambda item: item.minute_of_day))
        ids = [item.customer_id for item in self.schedule]
        if len(ids) != len(set(ids)):
            raise ValueError("scenario customer ids must be unique")
        self.entry_point = entry_point
        self.exit_point = exit_point
        self.merchandise_fixture_ids = tuple(merchandise_fixture_ids)
        self.checkout_fixture_id = checkout_fixture_id
        self._emitted: set[str] = set()
        self._anchor_elapsed_days: Optional[int] = None

    def arrivals_for(self, context: CustomerDemandContext) -> tuple[CustomerArrivalIntent, ...]:
        if self._anchor_elapsed_days is None:
            self._anchor_elapsed_days = context.elapsed_days
        if context.elapsed_days != self._anchor_elapsed_days:
            return ()

        due: list[CustomerArrivalIntent] = []
        for item in self.schedule:
            if item.customer_id in self._emitted:
                continue
            if item.minute_of_day > context.minute_of_day:
                break
            self._emitted.add(item.customer_id)
            due.append(
                CustomerArrivalIntent(
                    customer_id=item.customer_id,
                    entry_point=self.entry_point,
                    exit_point=self.exit_point,
                    merchandise_fixture_ids=self.merchandise_fixture_ids,
                    checkout_fixture_id=self.checkout_fixture_id,
                )
            )
        return tuple(due)


class PreferredOfferScenarioPurchasePolicy:
    """Buy the first explicitly preferred in-stock offer, otherwise skip."""

    def __init__(self, preferred_slot_ids: Sequence[str], *, quantity: int) -> None:
        if quantity <= 0:
            raise ValueError("quantity must be > 0")
        self.preferred_slot_ids = tuple(preferred_slot_ids)
        self.quantity = quantity

    def choose_purchase(self, context: CustomerPurchaseContext) -> CustomerPurchaseDecision:
        by_id = {offer.slot_id: offer for offer in context.offers}
        for slot_id in self.preferred_slot_ids:
            offer = by_id.get(slot_id)
            if offer is not None and offer.units_available >= self.quantity:
                return CustomerPurchaseDecision.buy(slot_id, self.quantity)
        return CustomerPurchaseDecision.skip()


class OrderedScenarioStaffTaskPolicy:
    """Choose work from an explicit task order supplied by the scenario."""

    def __init__(self, task_order: Sequence[StaffTask]) -> None:
        self.task_order = tuple(task_order)
        if not self.task_order:
            raise ValueError("task_order must not be empty")

    def choose_task(self, context: StaffTaskDecisionContext) -> Optional[StaffTaskDecision]:
        for task in self.task_order:
            for candidate in context.candidates:
                if candidate.task is task:
                    return StaffTaskDecision(task, target_id=candidate.target_id)
        return None


class FirstWaitingScenarioCheckoutPolicy:
    """Deterministic FIFO-like scenario policy; not an original-game claim."""

    def choose_customer(self, context: CheckoutSelectionContext) -> Optional[str]:
        return context.waiting_customer_ids[0] if context.waiting_customer_ids else None


class FixedScenarioCheckoutDurationPolicy:
    def __init__(self, required_game_minutes: int) -> None:
        if required_game_minutes < 0:
            raise ValueError("required_game_minutes must be >= 0")
        self.duration = required_game_minutes

    def required_game_minutes(self, context: CheckoutServiceTimingContext) -> int:
        return self.duration


class FixedScenarioCheckoutEffectsPolicy:
    def __init__(
        self,
        *,
        stamina_cost: Optional[int],
        break_room_target_id: Optional[str],
    ) -> None:
        if stamina_cost is not None and stamina_cost < 0:
            raise ValueError("stamina_cost must be >= 0 or None")
        self.effects = CheckoutServiceCompletionEffects(
            stamina_cost=stamina_cost,
            break_room_target_id=break_room_target_id,
        )

    def completion_effects(self, context: CheckoutServiceTimingContext) -> CheckoutServiceCompletionEffects:
        return self.effects


class FixedScenarioStaffWorkPolicy:
    """Complete replenish/clean work after explicit scenario durations."""

    def __init__(
        self,
        *,
        replenish_game_minutes: int,
        clean_game_minutes: int,
        replenish_up_to_quantity: int,
        replenish_stamina_cost: Optional[int],
        clean_stamina_cost: Optional[int],
        break_room_target_id: Optional[str],
    ) -> None:
        if replenish_game_minutes < 0 or clean_game_minutes < 0:
            raise ValueError("work durations must be >= 0")
        if replenish_up_to_quantity <= 0:
            raise ValueError("replenish_up_to_quantity must be > 0")
        for value in (replenish_stamina_cost, clean_stamina_cost):
            if value is not None and value < 0:
                raise ValueError("stamina costs must be >= 0 or None")
        self.replenish_game_minutes = replenish_game_minutes
        self.clean_game_minutes = clean_game_minutes
        self.replenish_up_to_quantity = replenish_up_to_quantity
        self.replenish_stamina_cost = replenish_stamina_cost
        self.clean_stamina_cost = clean_stamina_cost
        self.break_room_target_id = break_room_target_id

    def completion(self, context: StaffWorkTimingContext) -> Optional[StaffWorkCompletionDecision]:
        if context.task is StaffTask.REPLENISH:
            if context.elapsed_game_minutes < self.replenish_game_minutes:
                return None
            free = context.inventory_free_capacity or 0
            if free <= 0:
                return None
            return StaffWorkCompletionDecision(
                quantity=min(self.replenish_up_to_quantity, free),
                stamina_cost=self.replenish_stamina_cost,
                break_room_target_id=self.break_room_target_id,
            )

        if context.elapsed_game_minutes < self.clean_game_minutes:
            return None
        return StaffWorkCompletionDecision(
            stamina_cost=self.clean_stamina_cost,
            break_room_target_id=self.break_room_target_id,
        )


class IntervalScenarioRestPolicy:
    """Advance rest from explicit travel/recovery parameters supplied by a scenario."""

    def __init__(
        self,
        *,
        return_game_minutes: int,
        recovery_interval_game_minutes: int,
        recovery_amount: int,
    ) -> None:
        if return_game_minutes < 0:
            raise ValueError("return_game_minutes must be >= 0")
        if recovery_interval_game_minutes <= 0:
            raise ValueError("recovery_interval_game_minutes must be > 0")
        if recovery_amount <= 0:
            raise ValueError("recovery_amount must be > 0")
        self.return_game_minutes = return_game_minutes
        self.recovery_interval_game_minutes = recovery_interval_game_minutes
        self.recovery_amount = recovery_amount
        self._last_recovery_absolute: dict[str, int] = {}

    def transition(self, context: StaffRestTimingContext) -> Optional[StaffRestTransitionDecision]:
        if context.condition is StaffCondition.RETURNING_TO_BREAK_ROOM:
            self._last_recovery_absolute.pop(context.staff_id, None)
            if context.elapsed_game_minutes >= self.return_game_minutes:
                return StaffRestTransitionDecision(arrive_at_break_room=True)
            return None

        baseline = self._last_recovery_absolute.get(
            context.staff_id,
            context.started_at_absolute_minute,
        )
        if context.current_absolute_minute - baseline < self.recovery_interval_game_minutes:
            return None
        self._last_recovery_absolute[context.staff_id] = context.current_absolute_minute
        return StaffRestTransitionDecision(recovery_amount=self.recovery_amount)
