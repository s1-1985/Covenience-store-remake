from __future__ import annotations

from dataclasses import dataclass
from typing import Optional, Protocol

from .staff import StaffCondition
from .staff_rest_timing import (
    StaffRestTimingContext,
    StaffRestTransitionDecision,
)


CONFIRMED_REST_BASE_RECOVERY = 1
CONFIRMED_REST_BONUS_RECOVERY = 1


class RestRecoveryBonusPolicy(Protocol):
    """Resolve whether the observed agility-linked +1 bonus applies this tick.

    The first-title source supports an agility relationship but the probability
    curve is not recovered. Returning None keeps the exact recovery amount
    unresolved and therefore prevents a state mutation.
    """

    def bonus_applies(self, context: StaffRestTimingContext) -> Optional[bool]: ...


@dataclass(frozen=True)
class RestRecoveryAmountResolution:
    staff_id: str
    base_amount: int
    bonus_amount: int
    bonus_applies: Optional[bool]
    exact_recovery_amount: Optional[int]


class EvidenceBackedRestRecoveryResolver:
    """Resolve the recovered 1-or-2 stamina recovery amount for one rest tick."""

    def resolve(
        self,
        context: StaffRestTimingContext,
        bonus_policy: RestRecoveryBonusPolicy,
    ) -> RestRecoveryAmountResolution:
        if context.condition is not StaffCondition.RESTING:
            raise ValueError("stamina recovery amount can only be resolved while resting")

        bonus = bonus_policy.bonus_applies(context)
        exact = (
            None
            if bonus is None
            else CONFIRMED_REST_BASE_RECOVERY
            + (CONFIRMED_REST_BONUS_RECOVERY if bonus else 0)
        )
        return RestRecoveryAmountResolution(
            staff_id=context.staff_id,
            base_amount=CONFIRMED_REST_BASE_RECOVERY,
            bonus_amount=CONFIRMED_REST_BONUS_RECOVERY,
            bonus_applies=bonus,
            exact_recovery_amount=exact,
        )


class EvidenceBackedIntervalRestPolicy:
    """Rest transition policy with explicit timing and evidence-backed amount.

    Break-room return time and recovery-check interval are caller supplied because
    their first-title values remain unresolved. At each eligible recovery check,
    the exact amount is 1 or 2 according to a replaceable bonus policy. No
    agility probability formula is embedded here.
    """

    def __init__(
        self,
        *,
        return_game_minutes: int,
        recovery_interval_game_minutes: int,
        bonus_policy: RestRecoveryBonusPolicy,
    ) -> None:
        if return_game_minutes < 0:
            raise ValueError("return_game_minutes must be >= 0")
        if recovery_interval_game_minutes <= 0:
            raise ValueError("recovery_interval_game_minutes must be > 0")
        self.return_game_minutes = return_game_minutes
        self.recovery_interval_game_minutes = recovery_interval_game_minutes
        self.bonus_policy = bonus_policy
        self._resolver = EvidenceBackedRestRecoveryResolver()
        self._last_recovery_absolute: dict[str, int] = {}

    def transition(
        self,
        context: StaffRestTimingContext,
    ) -> Optional[StaffRestTransitionDecision]:
        if context.condition is StaffCondition.RETURNING_TO_BREAK_ROOM:
            self._last_recovery_absolute.pop(context.staff_id, None)
            if context.elapsed_game_minutes >= self.return_game_minutes:
                return StaffRestTransitionDecision(arrive_at_break_room=True)
            return None

        if context.condition is not StaffCondition.RESTING:
            raise ValueError("unsupported staff condition for rest transition policy")

        baseline = self._last_recovery_absolute.get(
            context.staff_id,
            context.started_at_absolute_minute,
        )
        if context.current_absolute_minute - baseline < self.recovery_interval_game_minutes:
            return None

        resolution = self._resolver.resolve(context, self.bonus_policy)
        if resolution.exact_recovery_amount is None:
            return None

        self._last_recovery_absolute[context.staff_id] = context.current_absolute_minute
        return StaffRestTransitionDecision(
            recovery_amount=resolution.exact_recovery_amount,
        )
