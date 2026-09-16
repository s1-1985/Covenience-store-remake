from __future__ import annotations

from dataclasses import dataclass
from typing import Optional, Sequence

STORE_SIZE_VALUE_MULTIPLIER = {
    "small": 1.5,
    "medium": 1.65,
    "large": 1.8,
}
"""Store-size multiplier used by the security/cleaning value formulas below.

Source: strategy guide "オールテクニックガイド" 誘致関連 page
(docs/research/strategy-guide-fixture-crosscheck-2026-09-16.md section 7),
printed as "10×10の店舗=1.5、12×12の店舗=1.65、14×14の店舗=1.8". The guide's
own "14×14" label for the large tier is itself one of several conflicting
size notations for "large" recorded in the crosscheck note; the key is
mapped here onto `StoreVariant.size_tier`'s existing "small"/"medium"/
"large" values rather than the guide's raw dimension text.
"""

POLICE_BOX_BONUS_PER_AREA_TILE = 10
POLICE_BOX_MAX_BONUS = 40
FIRE_STATION_BONUS_PER_AREA_TILE = 5
FIRE_STATION_MAX_BONUS = 30
SECURITY_FACILITY_RANGE_TILES = 16
"""Facilities only contribute if within this many tiles of the store, per
the guide's own "店舗周囲16×16エリア" wording. The spatial search itself
(counting how many area tiles of a facility fall in that range) is out of
scope here; this module only turns an already-counted tile count into a
bonus.
"""


@dataclass(frozen=True)
class SecurityFacilityCoverage:
    """Police-box/fire-station tile counts within the store's 16x16 range.

    Source: strategy guide "オールテクニックガイド" 誘致関連 page, printed as
    "交番=店舗周囲16×16エリア内に存在した場合、1エリアごとに+10(最大+40)"
    and "消防署=...1エリアごとに+5(最大+30)". `*_area_tiles` is the number of
    map tiles belonging to that facility type found within range; callers
    are responsible for that spatial count (this class only combines
    already-counted tiles into bonuses/eligibility, matching this module's
    docstring above).
    """

    police_box_area_tiles: int = 0
    fire_station_area_tiles: int = 0

    def __post_init__(self) -> None:
        if self.police_box_area_tiles < 0:
            raise ValueError("police_box_area_tiles must be >= 0")
        if self.fire_station_area_tiles < 0:
            raise ValueError("fire_station_area_tiles must be >= 0")

    @property
    def police_box_bonus(self) -> int:
        return min(POLICE_BOX_MAX_BONUS, self.police_box_area_tiles * POLICE_BOX_BONUS_PER_AREA_TILE)

    @property
    def fire_station_bonus(self) -> int:
        return min(FIRE_STATION_MAX_BONUS, self.fire_station_area_tiles * FIRE_STATION_BONUS_PER_AREA_TILE)

    @property
    def total_security_bonus(self) -> int:
        return self.police_box_bonus + self.fire_station_bonus

    @property
    def has_any_protection(self) -> bool:
        """True once at least one police_box/fire_station tile is in range.

        Reused by the fire/robbery risk check in store_events.py, which the
        guide ties to the same 16x16 coverage: "店舗周囲16×16エリアにセキュ
        リティ施設が無い場合" (fire/robbery becomes possible without any
        security facility in range).
        """
        return self.police_box_area_tiles > 0 or self.fire_station_area_tiles > 0


NO_SECURITY_FACILITY_COVERAGE = SecurityFacilityCoverage()


def compute_service_value(
    staff_service_skills: Sequence[int],
    fixture_service_bonuses: Sequence[int] = (),
) -> float:
    """店舗のサービス値 = 社員(最大3人)のサービス値平均 + サービス設備の付加効果.

    Source: strategy guide "オールテクニックガイド" 内装関連 page
    ("店舗のサービス値 = 社員3人のサービス値平均 + サービス設備の付加効果").
    The guide's "3人" reflects the first-title 3-staff-per-store cap
    (`staff.FIRST_TITLE_MAX_STAFF_PER_STORE`); this function averages over
    however many service_skill values are actually supplied rather than
    hardcoding a count of exactly 3, so it stays correct for a
    partially-staffed store. `fixture_service_bonuses` are each fixture's
    confirmed `service_bonus` (observed_plant=+2, bench=+3 or +4 depending
    on source, fountain=+25 or +30 -- see the crosscheck research note for
    the still-open bench/fountain conflicts).
    """
    if not staff_service_skills:
        raise ValueError("at least one staff service_skill value is required")
    if any(value < 0 for value in staff_service_skills):
        raise ValueError("staff service_skill values must be >= 0")
    if any(value < 0 for value in fixture_service_bonuses):
        raise ValueError("fixture service_bonus values must be >= 0")
    average = sum(staff_service_skills) / len(staff_service_skills)
    return average + sum(fixture_service_bonuses)


def compute_security_value(
    staff_security_skills: Sequence[int],
    size_tier: str,
    facility_coverage: Optional[SecurityFacilityCoverage] = None,
) -> float:
    """店舗のセキュリティ値 = 社員のセキュリティ値合計 × 店舗規模別基準値 + セキュリティ施設の効果.

    Source: strategy guide "オールテクニックガイド" 誘致関連 page. Empty
    `staff_security_skills` is allowed (sums to 0), since an unstaffed store
    still has a defined (zero) staff contribution, unlike the service-value
    average above which is undefined with zero staff.
    """
    if size_tier not in STORE_SIZE_VALUE_MULTIPLIER:
        raise ValueError(f"unknown size_tier: {size_tier!r}")
    if any(value < 0 for value in staff_security_skills):
        raise ValueError("staff security_skill values must be >= 0")
    base = sum(staff_security_skills) * STORE_SIZE_VALUE_MULTIPLIER[size_tier]
    bonus = facility_coverage.total_security_bonus if facility_coverage is not None else 0
    return base + bonus


def compute_cleaning_value(staff_cleaning_skills: Sequence[int], size_tier: str) -> float:
    """店舗の清掃値 = 社員の清掃値合計 × 店舗規模別基準値.

    Source: strategy guide "オールテクニックガイド" 誘致関連 page (same
    page as compute_security_value; the guide states the identical
    size-tier multiplier applies to both).
    """
    if size_tier not in STORE_SIZE_VALUE_MULTIPLIER:
        raise ValueError(f"unknown size_tier: {size_tier!r}")
    if any(value < 0 for value in staff_cleaning_skills):
        raise ValueError("staff cleaning_skill values must be >= 0")
    return sum(staff_cleaning_skills) * STORE_SIZE_VALUE_MULTIPLIER[size_tier]
