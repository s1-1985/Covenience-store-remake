from __future__ import annotations

from dataclasses import dataclass
from typing import Mapping, Optional

from .staff import StaffSkill, StoreStaffRoster


@dataclass
class ManagerMagazineOpportunity:
    """One externally-confirmed manager magazine feature event.

    First-title research confirms that a sufficiently clean store can trigger a
    magazine feature and that the manager's abilities rise afterward. The
    threshold, probability, evaluation timing, affected skills and deltas are
    unresolved, so firing and resolution are explicit caller/observation inputs.
    """

    sequence: int
    manager_staff_id: str
    observed_cleaning: Optional[int]
    before_skills: tuple[tuple[StaffSkill, Optional[int]], ...]
    source: str
    resolved_after: Optional[tuple[tuple[StaffSkill, int], ...]] = None

    @property
    def resolved(self) -> bool:
        return self.resolved_after is not None


class ManagerMagazineEventRuntime:
    """Record and resolve the confirmed magazine-manager growth event safely.

    This runtime never decides whether cleaning is high enough, never rolls an
    event probability, and never invents a skill delta. A caller must explicitly
    record an observed/future-policy event, then explicitly supply the observed
    post-event skill values when they become known.
    """

    def __init__(self, staff: StoreStaffRoster) -> None:
        self.staff = staff
        self._opportunities: list[ManagerMagazineOpportunity] = []
        self._next_sequence = 1

    @property
    def opportunities(self) -> tuple[ManagerMagazineOpportunity, ...]:
        return tuple(self._opportunities)

    @property
    def unresolved_opportunities(self) -> tuple[ManagerMagazineOpportunity, ...]:
        return tuple(item for item in self._opportunities if not item.resolved)

    def opportunity(self, sequence: int) -> ManagerMagazineOpportunity:
        for item in self._opportunities:
            if item.sequence == sequence:
                return item
        raise KeyError(f"unknown magazine opportunity sequence: {sequence}")

    def record_feature_event(
        self,
        *,
        observed_cleaning: Optional[int] = None,
        source: str,
    ) -> ManagerMagazineOpportunity:
        if observed_cleaning is not None and not 0 <= observed_cleaning <= 100:
            raise ValueError("observed_cleaning must be 0..100 or None")
        if not source:
            raise ValueError("source must be non-empty")
        manager_staff_id = self.staff.manager_staff_id
        if manager_staff_id is None:
            raise ValueError("store has no manager assigned")
        manager = self.staff.staff_member(manager_staff_id)
        before_skills = tuple(
            (skill, manager.skill_value(skill))
            for skill in StaffSkill
        )
        item = ManagerMagazineOpportunity(
            sequence=self._next_sequence,
            manager_staff_id=manager_staff_id,
            observed_cleaning=observed_cleaning,
            before_skills=before_skills,
            source=source,
        )
        self._next_sequence += 1
        self._opportunities.append(item)
        return item

    def resolve_opportunity(
        self,
        sequence: int,
        *,
        after_skills: Mapping[StaffSkill, int],
    ) -> ManagerMagazineOpportunity:
        item = self.opportunity(sequence)
        if item.resolved:
            raise ValueError("magazine opportunity is already resolved")
        if not after_skills:
            raise ValueError("after_skills must include at least one observed skill")

        manager = self.staff.staff_member(item.manager_staff_id)
        before = dict(item.before_skills)
        normalized: list[tuple[StaffSkill, int]] = []
        for skill, value in after_skills.items():
            if not isinstance(skill, StaffSkill):
                raise TypeError("after_skills keys must be StaffSkill")
            if value < 0:
                raise ValueError("after skill values must be >= 0")
            before_value = before.get(skill)
            if before_value is not None and value < before_value:
                raise ValueError("magazine event resolution cannot reduce a skill")
            normalized.append((skill, value))

        for skill, value in normalized:
            manager.runtime_skills[skill] = value
        item.resolved_after = tuple(normalized)
        return item
