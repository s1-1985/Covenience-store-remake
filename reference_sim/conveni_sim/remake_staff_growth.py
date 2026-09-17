from __future__ import annotations

import random
from dataclasses import dataclass, field

from .staff import StaffGrowthOpportunity, StoreStaffRoster, WORK_GROWTH_SKILL
from .staff_growth_resolution import (
    EVIDENCE_BACKED_UNIT_GROWTH,
    StaffGrowthResolution,
    StaffGrowthResolutionStatus,
)

# --- REMAKE_BALANCED_DEFAULT house rule ---------------------------------
#
# staff_growth_resolution.py's EvidenceBackedStaffGrowthResolver only
# resolves the two (task, skill) pairs first-title community evidence
# actually measured an increment for (replenish->replenishment,
# clean->cleaning); every other pair the guide's own multi-skill growth
# diagram confirms exists (checkout->register/service, replenish->
# cleaning/security, clean->security -- see WORK_GROWTH_SKILL in staff.py)
# is left permanently pending by that resolver, by design. This module adds
# a second, clearly-separate resolver that also handles those pairs, so the
# evidence-only resolver's guarantees stay untouched by callers who don't
# opt into this one.
REMAKE_BALANCED_UNIT_GROWTH: dict[tuple, int] = {
    (task, skill): EVIDENCE_BACKED_UNIT_GROWTH.get((task, skill), 1)
    for task, skills in WORK_GROWTH_SKILL.items()
    for skill in skills
}
"""+1 for every (task, skill) pair, since +1 is the only magnitude this
codebase has ever seen evidenced for this kind of growth (both confirmed
pairs happen to be +1); the newly-covered pairs inherit it as a
REMAKE_BALANCED_DEFAULT guess, not because it was independently measured
for them too."""

MANAGER_TEACHING_BONUS_CHANCE_PER_EDUCATION_POINT = 0.01
"""Guide text confirms the causal link (EXPLICIT_BEHAVIOR) -- "店長の教育
次第で社員能力を伸ばせる" / "店長教育値が高いと能力アップ率が高い" -- but
gives no rate. REMAKE_BALANCED_DEFAULT: each point of the manager's own
education skill (0-100) adds this much chance of one extra +1 on top of the
base increment for a subordinate's growth tick, so a manager with
education=100 grants, on average, up to double the base growth rate."""


@dataclass
class RemakeBalancedStaffGrowthResolver:
    """Resolves every WORK_GROWTH_SKILL (task, skill) pair, with a manager-
    education growth bonus layered on top. See module docstring:
    REMAKE_BALANCED_DEFAULT, not a recovered original formula -- a playable
    placeholder to retune (or replace outright if better evidence surfaces)
    after actual play.
    """

    roster: StoreStaffRoster
    manager_teaching_bonus_chance_per_education_point: float = MANAGER_TEACHING_BONUS_CHANCE_PER_EDUCATION_POINT
    rng: random.Random = field(default_factory=random.Random)

    def resolve_opportunity(self, opportunity: StaffGrowthOpportunity) -> StaffGrowthResolution:
        increment = REMAKE_BALANCED_UNIT_GROWTH.get((opportunity.task, opportunity.skill))
        if increment is None:
            return StaffGrowthResolution(
                opportunity.sequence,
                opportunity.staff_id,
                opportunity.task,
                StaffGrowthResolutionStatus.UNSUPPORTED_TASK,
                opportunity.before_value,
                opportunity.base_cap,
            )

        # Read the *current* live skill value rather than the opportunity's
        # own before_value snapshot. WORK_GROWTH_SKILL now lets more than one
        # task (e.g. both replenish and clean) open a growth opportunity for
        # the same skill (e.g. security); resolving a batch of pending
        # opportunities for the same skill from its stale creation-time
        # snapshot would silently discard whichever one resolves first, since
        # StoreStaffRoster.resolve_growth_opportunity sets the skill to an
        # absolute value rather than adding a delta.
        current_value = self.roster.staff_member(opportunity.staff_id).skill_value(opportunity.skill)
        if current_value is None:
            return StaffGrowthResolution(
                opportunity.sequence,
                opportunity.staff_id,
                opportunity.task,
                StaffGrowthResolutionStatus.UNKNOWN_BEFORE_VALUE,
                None,
                opportunity.base_cap,
            )
        if opportunity.base_cap is None:
            return StaffGrowthResolution(
                opportunity.sequence,
                opportunity.staff_id,
                opportunity.task,
                StaffGrowthResolutionStatus.UNKNOWN_BASE_CAP,
                current_value,
                None,
            )
        if current_value > opportunity.base_cap:
            return StaffGrowthResolution(
                opportunity.sequence,
                opportunity.staff_id,
                opportunity.task,
                StaffGrowthResolutionStatus.ABOVE_BASE_CAP,
                current_value,
                opportunity.base_cap,
            )

        if opportunity.manager_education is not None:
            bonus_chance = min(
                1.0,
                opportunity.manager_education * self.manager_teaching_bonus_chance_per_education_point,
            )
            if self.rng.random() < bonus_chance:
                increment += 1

        after = min(current_value + increment, opportunity.base_cap)
        self.roster.resolve_growth_opportunity(opportunity.sequence, after_value=after)
        return StaffGrowthResolution(
            opportunity.sequence,
            opportunity.staff_id,
            opportunity.task,
            StaffGrowthResolutionStatus.RESOLVED,
            current_value,
            opportunity.base_cap,
            after,
        )

    def resolve_all_pending(self) -> tuple[StaffGrowthResolution, ...]:
        results: list[StaffGrowthResolution] = []
        for opportunity in self.roster.unresolved_growth_opportunities:
            if (opportunity.task, opportunity.skill) not in REMAKE_BALANCED_UNIT_GROWTH:
                continue
            results.append(self.resolve_opportunity(opportunity))
        return tuple(results)
