from __future__ import annotations

from dataclasses import dataclass
from typing import Optional, Protocol

from .checkout import CheckoutServiceRecord
from .staff import StaffSkill
from .store_runtime import CheckoutSaleCompletion, StoreRuntimeHarness


@dataclass(frozen=True)
class CheckoutServiceTimingState:
    staff_id: str
    customer_id: str
    checkout_fixture_id: str
    started_at_absolute_minute: int


@dataclass(frozen=True)
class CheckoutServiceTimingContext:
    staff_id: str
    customer_id: str
    checkout_fixture_id: str
    started_at_absolute_minute: int
    current_absolute_minute: int
    elapsed_game_minutes: int
    register_skill: Optional[int]
    simultaneous_staff_capacity: int
    stamina_current: Optional[int]
    stamina_max: Optional[int]


class CheckoutServiceDurationPolicy(Protocol):
    """Replaceable duration policy for unresolved first-title checkout timing."""

    def required_game_minutes(self, context: CheckoutServiceTimingContext) -> Optional[int]: ...


@dataclass(frozen=True)
class CheckoutServiceCompletionEffects:
    """Explicit post-checkout effects with unresolved numeric values."""

    stamina_cost: Optional[int] = None
    break_room_target_id: Optional[str] = None

    def __post_init__(self) -> None:
        if self.stamina_cost is not None and self.stamina_cost < 0:
            raise ValueError("stamina_cost must be >= 0 or None")


class CheckoutServiceCompletionEffectsPolicy(Protocol):
    """Replaceable policy for unresolved checkout stamina effects."""

    def completion_effects(
        self,
        context: CheckoutServiceTimingContext,
    ) -> CheckoutServiceCompletionEffects: ...


@dataclass(frozen=True)
class CheckoutServiceTimingEvaluation:
    context: CheckoutServiceTimingContext
    required_game_minutes: Optional[int]
    completed: bool
    sale: Optional[CheckoutSaleCompletion] = None
    completion_effects: Optional[CheckoutServiceCompletionEffects] = None


class CheckoutServiceTimingCoordinator:
    """Track checkout elapsed game time without inventing timing/effect formulas.

    A supplied duration policy controls when service can complete. An optional
    completion-effects policy may supply an explicit stamina cost and break-room
    target. Effects are validated before sale settlement so unknown stamina does
    not leave a partially settled transaction.
    """

    def __init__(self, runtime: StoreRuntimeHarness) -> None:
        self.runtime = runtime
        self._active: dict[str, CheckoutServiceTimingState] = {}

    @property
    def active_states(self) -> tuple[CheckoutServiceTimingState, ...]:
        return tuple(self._active.values())

    def register_started(
        self,
        record: CheckoutServiceRecord,
        *,
        started_at_absolute_minute: Optional[int] = None,
    ) -> CheckoutServiceTimingState:
        if record.staff_id in self._active:
            raise ValueError("staff member already has registered checkout timing")
        checkout = self.runtime.checkout(record.fixture_id)
        if checkout.customer_being_served_by(record.staff_id) != record.customer_id:
            raise ValueError("checkout service record is not currently active")
        start = (
            self.runtime.subday_clock.absolute_minutes
            if started_at_absolute_minute is None
            else started_at_absolute_minute
        )
        if start < 0:
            raise ValueError("started_at_absolute_minute must be >= 0")
        if start > self.runtime.subday_clock.absolute_minutes:
            raise ValueError("checkout service cannot start in the future")
        state = CheckoutServiceTimingState(
            staff_id=record.staff_id,
            customer_id=record.customer_id,
            checkout_fixture_id=record.fixture_id,
            started_at_absolute_minute=start,
        )
        self._active[record.staff_id] = state
        return state

    def unregister_staff(self, staff_id: str) -> Optional[CheckoutServiceTimingState]:
        return self._active.pop(staff_id, None)

    def current_context(self, staff_id: str) -> CheckoutServiceTimingContext:
        state = self._active[staff_id]
        checkout = self.runtime.checkout(state.checkout_fixture_id)
        if checkout.customer_being_served_by(staff_id) != state.customer_id:
            raise ValueError("registered checkout service is no longer active")
        current = self.runtime.subday_clock.absolute_minutes
        if current < state.started_at_absolute_minute:
            raise ValueError("runtime clock moved before checkout service start")
        staff = self.runtime.staff.staff_member(staff_id)
        return CheckoutServiceTimingContext(
            staff_id=staff_id,
            customer_id=state.customer_id,
            checkout_fixture_id=state.checkout_fixture_id,
            started_at_absolute_minute=state.started_at_absolute_minute,
            current_absolute_minute=current,
            elapsed_game_minutes=current - state.started_at_absolute_minute,
            register_skill=staff.skill_value(StaffSkill.REGISTER),
            simultaneous_staff_capacity=checkout.simultaneous_staff_capacity,
            stamina_current=staff.stamina_current,
            stamina_max=staff.stamina_max,
        )

    def _validated_effects(
        self,
        context: CheckoutServiceTimingContext,
        policy: Optional[CheckoutServiceCompletionEffectsPolicy],
    ) -> Optional[CheckoutServiceCompletionEffects]:
        if policy is None:
            return None
        effects = policy.completion_effects(context)
        if not isinstance(effects, CheckoutServiceCompletionEffects):
            raise TypeError("checkout completion effects policy returned an invalid value")
        if effects.stamina_cost is not None:
            staff = self.runtime.staff.staff_member(context.staff_id)
            if not staff.stamina_tracking_enabled or staff.stamina_current is None:
                raise ValueError("checkout stamina effect requires a known stamina value")
        return effects

    def evaluate_staff(
        self,
        staff_id: str,
        policy: CheckoutServiceDurationPolicy,
        *,
        completion_effects_policy: Optional[CheckoutServiceCompletionEffectsPolicy] = None,
    ) -> CheckoutServiceTimingEvaluation:
        context = self.current_context(staff_id)
        required = policy.required_game_minutes(context)
        if required is not None and required < 0:
            raise ValueError("checkout duration policy returned a negative duration")
        if required is None or context.elapsed_game_minutes < required:
            return CheckoutServiceTimingEvaluation(context, required, False, None, None)

        effects = self._validated_effects(context, completion_effects_policy)
        sale = self.runtime.finish_checkout_sale(
            context.checkout_fixture_id,
            staff_id=staff_id,
        )
        if effects is not None and effects.stamina_cost is not None:
            self.runtime.staff.consume_stamina(
                staff_id,
                effects.stamina_cost,
                break_room_target_id=effects.break_room_target_id,
            )
        del self._active[staff_id]
        return CheckoutServiceTimingEvaluation(context, required, True, sale, effects)

    def evaluate_all(
        self,
        policy: CheckoutServiceDurationPolicy,
        *,
        completion_effects_policy: Optional[CheckoutServiceCompletionEffectsPolicy] = None,
    ) -> tuple[CheckoutServiceTimingEvaluation, ...]:
        # Snapshot ids because successful completion mutates `_active`.
        return tuple(
            self.evaluate_staff(
                staff_id,
                policy,
                completion_effects_policy=completion_effects_policy,
            )
            for staff_id in tuple(self._active)
        )
