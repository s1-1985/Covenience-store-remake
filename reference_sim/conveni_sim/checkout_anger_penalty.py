from __future__ import annotations

from dataclasses import dataclass
from typing import Mapping, Optional

from .staff import StaffSkill, StoreStaffRoster


CHECKOUT_ANGER_SKILL_DELTA = -2
CHECKOUT_ANGER_AFFECTED_SKILLS = (
    StaffSkill.REGISTER,
    StaffSkill.REPLENISHMENT,
    StaffSkill.SECURITY,
    StaffSkill.CLEANING,
    StaffSkill.SERVICE,
)


@dataclass
class CheckoutAngerPenaltyEvent:
    """One explicit checkout-anger consequence supported by first-title research.

    The event records the recovered -2 effect for all runtime work skills except
    education. Stamina is a separate lifecycle value and is not part of this
    penalty. Lower-bound behavior remains unresolved, so recording the event does
    not mutate staff values by itself.
    """

    sequence: int
    staff_id: str
    delta: int
    before_values: tuple[tuple[StaffSkill, Optional[int]], ...]
    resolved_after_values: Optional[tuple[tuple[StaffSkill, int], ...]] = None

    @property
    def resolved(self) -> bool:
        return self.resolved_after_values is not None


class CheckoutAngerPenaltyRuntime:
    """Record confirmed -2 checkout anger penalties without guessing stat floors.

    First-title dedicated research states that checkout anger lowers register,
    replenishment, security, cleaning and service by 2, while education and
    stamina are unaffected. The minimum value/floor is not currently recovered.

    `record()` therefore creates a pending evidence-backed event only. `resolve()`
    requires an explicit minimum for every affected skill before any mutation is
    applied. Resolution is atomic and rejects stale events whose staff values
    changed after recording.
    """

    def __init__(self, roster: StoreStaffRoster) -> None:
        self.roster = roster
        self._events: list[CheckoutAngerPenaltyEvent] = []

    @property
    def events(self) -> tuple[CheckoutAngerPenaltyEvent, ...]:
        return tuple(self._events)

    @property
    def unresolved_events(self) -> tuple[CheckoutAngerPenaltyEvent, ...]:
        return tuple(event for event in self._events if not event.resolved)

    def event(self, sequence: int) -> CheckoutAngerPenaltyEvent:
        for event in self._events:
            if event.sequence == sequence:
                return event
        raise KeyError(f"unknown checkout anger penalty sequence: {sequence}")

    def record(self, staff_id: str) -> CheckoutAngerPenaltyEvent:
        staff = self.roster.staff_member(staff_id)
        event = CheckoutAngerPenaltyEvent(
            sequence=len(self._events) + 1,
            staff_id=staff_id,
            delta=CHECKOUT_ANGER_SKILL_DELTA,
            before_values=tuple(
                (skill, staff.skill_value(skill))
                for skill in CHECKOUT_ANGER_AFFECTED_SKILLS
            ),
        )
        self._events.append(event)
        return event

    @staticmethod
    def _validated_minimums(
        minimum_by_skill: Mapping[StaffSkill, int],
    ) -> dict[StaffSkill, int]:
        missing = [
            skill
            for skill in CHECKOUT_ANGER_AFFECTED_SKILLS
            if skill not in minimum_by_skill
        ]
        if missing:
            names = ", ".join(skill.value for skill in missing)
            raise ValueError(f"minimum value is required for affected skills: {names}")

        result: dict[StaffSkill, int] = {}
        for skill in CHECKOUT_ANGER_AFFECTED_SKILLS:
            value = minimum_by_skill[skill]
            if value < 0:
                raise ValueError("checkout anger minimum values must be >= 0")
            result[skill] = value
        return result

    def resolve(
        self,
        sequence: int,
        *,
        minimum_by_skill: Mapping[StaffSkill, int],
    ) -> CheckoutAngerPenaltyEvent:
        event = self.event(sequence)
        if event.resolved:
            raise ValueError("checkout anger penalty event is already resolved")

        minimums = self._validated_minimums(minimum_by_skill)
        staff = self.roster.staff_member(event.staff_id)
        before = dict(event.before_values)

        unknown = [skill for skill, value in before.items() if value is None]
        if unknown:
            names = ", ".join(skill.value for skill in unknown)
            raise ValueError(f"cannot resolve penalty with unknown current skills: {names}")

        # Validate the whole event before mutating any value. This preserves
        # atomicity if the event is stale or a supplied floor is inconsistent.
        after_values: dict[StaffSkill, int] = {}
        for skill in CHECKOUT_ANGER_AFFECTED_SKILLS:
            recorded = before[skill]
            assert recorded is not None
            current = staff.skill_value(skill)
            if current != recorded:
                raise ValueError(
                    f"staff skill changed after penalty was recorded: {skill.value}"
                )
            minimum = minimums[skill]
            if minimum > recorded:
                raise ValueError(
                    f"minimum value exceeds recorded skill value: {skill.value}"
                )
            after_values[skill] = max(minimum, recorded + event.delta)

        for skill, value in after_values.items():
            staff.runtime_skills[skill] = value

        event.resolved_after_values = tuple(
            (skill, after_values[skill])
            for skill in CHECKOUT_ANGER_AFFECTED_SKILLS
        )
        return event
