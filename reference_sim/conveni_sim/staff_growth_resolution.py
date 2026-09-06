from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from .staff import StaffGrowthOpportunity, StaffTask, StoreStaffRoster


EVIDENCE_BACKED_UNIT_GROWTH = {
    StaffTask.REPLENISH: 1,
    StaffTask.CLEAN: 1,
}


class StaffGrowthResolutionStatus(str, Enum):
    RESOLVED = "resolved"
    UNSUPPORTED_TASK = "unsupported_task"
    UNKNOWN_BEFORE_VALUE = "unknown_before_value"
    UNKNOWN_BASE_CAP = "unknown_base_cap"
    ABOVE_BASE_CAP = "above_base_cap"


@dataclass(frozen=True)
class StaffGrowthResolution:
    opportunity_sequence: int
    staff_id: str
    task: StaffTask
    status: StaffGrowthResolutionStatus
    before_value: int | None
    base_cap: int | None
    after_value: int | None = None


class EvidenceBackedStaffGrowthResolver:
    """Resolve only numerically recovered first-title work-growth rules.

    Current first-title dedicated community evidence explicitly supports +1 per
    replenishment action and +1 per floor-cleaning action. Checkout work is known
    to grow register skill, but its exact increment remains unresolved and is
    therefore intentionally left pending.

    Normal growth also needs a known current value and known normal base cap. If
    either is missing, or the runtime value is already above the normal cap due
    to a separate cap-bypass event, this resolver leaves the opportunity open.
    """

    def __init__(self, roster: StoreStaffRoster) -> None:
        self.roster = roster

    def resolve_opportunity(self, opportunity: StaffGrowthOpportunity) -> StaffGrowthResolution:
        increment = EVIDENCE_BACKED_UNIT_GROWTH.get(opportunity.task)
        if increment is None:
            return StaffGrowthResolution(
                opportunity.sequence,
                opportunity.staff_id,
                opportunity.task,
                StaffGrowthResolutionStatus.UNSUPPORTED_TASK,
                opportunity.before_value,
                opportunity.base_cap,
            )
        if opportunity.before_value is None:
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
                opportunity.before_value,
                None,
            )
        if opportunity.before_value > opportunity.base_cap:
            return StaffGrowthResolution(
                opportunity.sequence,
                opportunity.staff_id,
                opportunity.task,
                StaffGrowthResolutionStatus.ABOVE_BASE_CAP,
                opportunity.before_value,
                opportunity.base_cap,
            )

        after = min(opportunity.before_value + increment, opportunity.base_cap)
        self.roster.resolve_growth_opportunity(
            opportunity.sequence,
            after_value=after,
        )
        return StaffGrowthResolution(
            opportunity.sequence,
            opportunity.staff_id,
            opportunity.task,
            StaffGrowthResolutionStatus.RESOLVED,
            opportunity.before_value,
            opportunity.base_cap,
            after,
        )

    def resolve_supported_pending(self) -> tuple[StaffGrowthResolution, ...]:
        """Attempt every pending replenish/clean opportunity once.

        Unsupported checkout opportunities remain available for a future
        evidence-backed register-growth rule and are not returned here.
        """
        results: list[StaffGrowthResolution] = []
        for opportunity in self.roster.unresolved_growth_opportunities:
            if opportunity.task not in EVIDENCE_BACKED_UNIT_GROWTH:
                continue
            results.append(self.resolve_opportunity(opportunity))
        return tuple(results)
