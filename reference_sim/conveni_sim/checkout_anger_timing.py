from __future__ import annotations

from dataclasses import dataclass
from typing import Optional, Protocol

from .checkout_anger_penalty import CheckoutAngerPenaltyEvent, CheckoutAngerPenaltyRuntime
from .customer import CustomerState
from .store_runtime import StoreRuntimeHarness


@dataclass
class CheckoutAngerTimingState:
    customer_id: str
    checkout_fixture_id: str
    waiting_started_at_absolute_minute: int
    service_started_at_absolute_minute: Optional[int] = None
    active_staff_id: Optional[str] = None
    anger_triggered: bool = False


@dataclass(frozen=True)
class CheckoutAngerTimingContext:
    customer_id: str
    checkout_fixture_id: str
    current_absolute_minute: int
    waiting_started_at_absolute_minute: int
    service_started_at_absolute_minute: Optional[int]
    active_staff_id: Optional[str]
    waiting_customer_count: int
    active_service_count: int

    @property
    def total_checkout_elapsed_game_minutes(self) -> int:
        return self.current_absolute_minute - self.waiting_started_at_absolute_minute

    @property
    def pre_service_wait_game_minutes(self) -> int:
        end = (
            self.current_absolute_minute
            if self.service_started_at_absolute_minute is None
            else self.service_started_at_absolute_minute
        )
        return end - self.waiting_started_at_absolute_minute

    @property
    def service_elapsed_game_minutes(self) -> Optional[int]:
        if self.service_started_at_absolute_minute is None:
            return None
        return self.current_absolute_minute - self.service_started_at_absolute_minute

    @property
    def in_service(self) -> bool:
        return self.active_staff_id is not None


class CheckoutAngerTriggerPolicy(Protocol):
    """Replaceable trigger boundary for unresolved first-title anger timing.

    True requests the confirmed anger consequence for the currently active
    checkout staff member. False/None keep observing. Queue wait, service time,
    total checkout elapsed time, customer patience and thresholds remain policy
    concerns until recovered from evidence.
    """

    def should_trigger(self, context: CheckoutAngerTimingContext) -> Optional[bool]: ...


@dataclass(frozen=True)
class CheckoutAngerTimingEvaluation:
    context: CheckoutAngerTimingContext
    trigger_requested: Optional[bool]
    triggered: bool
    penalty_event: Optional[CheckoutAngerPenaltyEvent] = None


class CheckoutAngerTimingCoordinator:
    """Timestamp checkout pressure and route explicit anger triggers safely.

    Customer sessions remain WAITING_CHECKOUT while actively being served, so
    this layer separately tracks first arrival at checkout and each contiguous
    active-service segment. If service is interrupted, the service timer resets
    when a later service begins while the original checkout-wait start is kept.

    The coordinator never invents an anger threshold. A trigger is consumed only
    while an active staff member exists, because the recovered -2 consequence is
    staff-specific. A trigger request made with no active staff remains pending
    rather than assigning the penalty to a guessed employee.
    """

    def __init__(
        self,
        runtime: StoreRuntimeHarness,
        penalty_runtime: CheckoutAngerPenaltyRuntime,
    ) -> None:
        if penalty_runtime.roster is not runtime.staff:
            raise ValueError("checkout anger penalty runtime must use the same store roster")
        self.runtime = runtime
        self.penalty_runtime = penalty_runtime
        self._states: dict[str, CheckoutAngerTimingState] = {}

    @property
    def active_states(self) -> tuple[CheckoutAngerTimingState, ...]:
        return tuple(self._states.values())

    def state(self, customer_id: str) -> CheckoutAngerTimingState:
        return self._states[customer_id]

    def _active_service_by_customer(self) -> dict[str, tuple[str, str]]:
        result: dict[str, tuple[str, str]] = {}
        for fixture_id in self.runtime.checkout_fixture_ids:
            checkout = self.runtime.checkout(fixture_id)
            for record in checkout.active_services:
                result[record.customer_id] = (fixture_id, record.staff_id)
        return result

    def sync_from_runtime(self) -> None:
        current = self.runtime.subday_clock.absolute_minutes
        active = self._active_service_by_customer()
        waiting_ids: set[str] = set()

        for customer in self.runtime.customers.customers:
            if customer.state is not CustomerState.WAITING_CHECKOUT:
                continue
            fixture_id = customer.checkout_fixture_id
            if fixture_id is None:
                continue
            waiting_ids.add(customer.id)
            active_pair = active.get(customer.id)
            active_staff_id = active_pair[1] if active_pair is not None else None

            state = self._states.get(customer.id)
            if state is None:
                state = CheckoutAngerTimingState(
                    customer_id=customer.id,
                    checkout_fixture_id=fixture_id,
                    waiting_started_at_absolute_minute=current,
                )
                self._states[customer.id] = state

            if active_staff_id is None:
                if state.active_staff_id is not None:
                    state.active_staff_id = None
                    state.service_started_at_absolute_minute = None
            elif state.active_staff_id != active_staff_id:
                state.active_staff_id = active_staff_id
                state.service_started_at_absolute_minute = current
            elif state.service_started_at_absolute_minute is None:
                state.service_started_at_absolute_minute = current

        for customer_id in tuple(self._states):
            if customer_id not in waiting_ids:
                del self._states[customer_id]

    def current_context(self, customer_id: str) -> CheckoutAngerTimingContext:
        state = self._states[customer_id]
        checkout = self.runtime.checkout(state.checkout_fixture_id)
        waiting = checkout.refresh_waiting()
        return CheckoutAngerTimingContext(
            customer_id=state.customer_id,
            checkout_fixture_id=state.checkout_fixture_id,
            current_absolute_minute=self.runtime.subday_clock.absolute_minutes,
            waiting_started_at_absolute_minute=state.waiting_started_at_absolute_minute,
            service_started_at_absolute_minute=state.service_started_at_absolute_minute,
            active_staff_id=state.active_staff_id,
            waiting_customer_count=len(waiting),
            active_service_count=len(checkout.active_services),
        )

    def evaluate_customer(
        self,
        customer_id: str,
        policy: CheckoutAngerTriggerPolicy,
    ) -> CheckoutAngerTimingEvaluation:
        state = self._states[customer_id]
        context = self.current_context(customer_id)
        if state.anger_triggered:
            return CheckoutAngerTimingEvaluation(context, False, False, None)

        requested = policy.should_trigger(context)
        if requested is not True:
            return CheckoutAngerTimingEvaluation(context, requested, False, None)
        if context.active_staff_id is None:
            return CheckoutAngerTimingEvaluation(context, True, False, None)

        event = self.penalty_runtime.record(context.active_staff_id)
        state.anger_triggered = True
        return CheckoutAngerTimingEvaluation(context, True, True, event)

    def evaluate_all(
        self,
        policy: CheckoutAngerTriggerPolicy,
    ) -> tuple[CheckoutAngerTimingEvaluation, ...]:
        self.sync_from_runtime()
        return tuple(
            self.evaluate_customer(customer_id, policy)
            for customer_id in tuple(self._states)
        )
