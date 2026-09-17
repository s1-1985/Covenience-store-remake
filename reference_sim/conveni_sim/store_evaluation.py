from __future__ import annotations

from dataclasses import dataclass
from typing import Optional, Sequence

from .staff import StaffSkill, StoreStaffRoster
from .store_grid import StoreGrid
from .store_rating import RatingMonthlyEvaluation, RatingMonthlyInputs, evaluate_monthly_rating_change
from .store_value import (
    SecurityFacilityCoverage,
    compute_cleaning_value,
    compute_security_value,
    compute_service_value,
)


def _known_staff_skill_values(roster: StoreStaffRoster, skill: StaffSkill) -> tuple[int, ...]:
    return tuple(
        value
        for value in (state.skill_value(skill) for state in roster.staff)
        if value is not None
    )


@dataclass
class StoreEvaluationRuntime:
    """Bridges existing staff/grid runtime state into the strategy guide's
    service/security/cleaning/rating formulas
    (docs/research/strategy-guide-fixture-crosscheck-2026-09-16.md section 7,
    implemented as pure functions in store_value.py/store_rating.py).

    This closes the gap the 2026-09-16 session handoff flagged: those
    formulas existed but nothing called them, because `reference_sim` has no
    central orchestrator (`store_runtime.py` deliberately composes only
    grid/customer/staff/inventory/checkout/traffic/cleaning/customer_share/
    economy/purchases -- see PROJECT_MEMORY.md section 19) and each other
    subsystem (promotion.py, month_boundary.py, monthly_report.py, and now
    this module) is instead a standalone, separately-composed unit by
    design. This class follows that same pattern rather than reaching into
    `StoreRuntimeHarness` or `store_runtime.py`.

    It stays data-free like the rest of the runtime layer: it reads
    already-tracked staff skill values and the store's own
    `StoreGrid.size_tier`, but takes fixture service bonuses and any
    town-facility security coverage as caller-supplied inputs rather than
    resolving fixture ids or facility placement itself (no
    `baseline_data`/town-map dependency here -- a caller with access to
    `baseline_data.FIXTURES` resolves each `StoreGrid.placements[i].fixture_id`
    to its `service_bonus.value` and passes the resolved list in). See
    `town.py` for the analogous town-population/store-count side of this
    same gap (population growth and facility spatial placement remain
    documented UNKNOWN research gaps -- PROJECT_MEMORY.md section 17 -- not
    invented here).
    """

    staff: StoreStaffRoster
    grid: StoreGrid
    internal_rating_value: Optional[int] = None
    """0-100 internal evaluation value (see store_rating.star_rank_for_internal_value).
    Starts unknown rather than an invented default: the guide never states a
    new store's starting evaluation. `evaluate_month_end` requires a known
    value; call `set_internal_rating_value` first with one from evidence
    (e.g. an observed screenshot) or an explicit house-rule starting point.
    """

    def set_internal_rating_value(self, value: int) -> None:
        if not 0 <= value <= 100:
            raise ValueError("internal_rating_value must be 0..100")
        self.internal_rating_value = value

    def service_value(self, fixture_service_bonuses: Sequence[int] = ()) -> Optional[float]:
        """店舗のサービス値, or None if no staff member has a known service_skill."""
        skills = _known_staff_skill_values(self.staff, StaffSkill.SERVICE)
        if not skills:
            return None
        return compute_service_value(skills, fixture_service_bonuses)

    def security_value(
        self,
        facility_coverage: Optional[SecurityFacilityCoverage] = None,
    ) -> Optional[float]:
        """店舗のセキュリティ値, or None if the grid's size_tier is unknown."""
        if self.grid.size_tier is None:
            return None
        skills = _known_staff_skill_values(self.staff, StaffSkill.SECURITY)
        return compute_security_value(skills, self.grid.size_tier, facility_coverage)

    def cleaning_value(self) -> Optional[float]:
        """店舗の清掃値, or None if the grid's size_tier is unknown."""
        if self.grid.size_tier is None:
            return None
        skills = _known_staff_skill_values(self.staff, StaffSkill.CLEANING)
        return compute_cleaning_value(skills, self.grid.size_tier)

    def evaluate_month_end(
        self,
        *,
        price_change_pct: int,
        monthly_sales_yen: int,
        fixture_service_bonuses: Sequence[int] = (),
        facility_coverage: Optional[SecurityFacilityCoverage] = None,
    ) -> RatingMonthlyEvaluation:
        """Evaluate one month's ★ rating change and advance internal_rating_value.

        Raises if internal_rating_value, a service-skilled staff member, or
        the grid's size_tier is unknown, rather than substituting an
        invented value for any of them.
        """
        if self.internal_rating_value is None:
            raise ValueError(
                "internal_rating_value is unknown; call set_internal_rating_value first "
                "(the guide does not state a new store's starting evaluation)"
            )
        service = self.service_value(fixture_service_bonuses)
        security = self.security_value(facility_coverage)
        cleaning = self.cleaning_value()
        if service is None or security is None or cleaning is None:
            raise ValueError(
                "service/security/cleaning value requires at least one staff member with "
                "a known service_skill and a known grid.size_tier"
            )
        evaluation = evaluate_monthly_rating_change(
            RatingMonthlyInputs(
                current_internal_value=self.internal_rating_value,
                price_change_pct=price_change_pct,
                service_value=service,
                security_value=security,
                cleaning_value=cleaning,
                monthly_sales_yen=monthly_sales_yen,
            )
        )
        self.internal_rating_value = evaluation.next_internal_value
        return evaluation

    def apply_point_delta(self, points: int) -> int:
        """Apply a per-event rating delta and return the new internal value.

        For the guide's per-event (not month-end) adjustments --
        ANGRY_CUSTOMER_DOWNGRADE_POINTS / SHOPLIFTING_DOWNGRADE_POINTS /
        DONATION_UPGRADE_POINTS in store_rating.py -- which
        evaluate_monthly_rating_change's own docstring says are the
        caller's responsibility to apply separately.
        """
        if self.internal_rating_value is None:
            raise ValueError("internal_rating_value is unknown; call set_internal_rating_value first")
        self.internal_rating_value = max(0, min(100, self.internal_rating_value + points))
        return self.internal_rating_value
