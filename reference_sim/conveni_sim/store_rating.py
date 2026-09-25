from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

STAR_RANK_VALUES = (0, 1, 2, 3, 4, 5)
"""Star display, 0 (☆☆☆☆☆) through 5 (★★★★★)."""


def star_rank_for_internal_value(internal_value: int) -> int:
    """Convert the 0-100 internal evaluation value to a 0-5 star count.

    Source: strategy guide "オールテクニックガイド" 評価関連 page
    ("ランク表示と内部評価値: ★★★★★=100, ★★★★☆=80-99, ★★★☆☆=60-79,
    ★★☆☆☆=40-59, ★☆☆☆☆=20-39, ☆☆☆☆☆=0-19").
    """
    if not 0 <= internal_value <= 100:
        raise ValueError("internal_value must be 0..100")
    if internal_value == 100:
        return 5
    if internal_value >= 80:
        return 4
    if internal_value >= 60:
        return 3
    if internal_value >= 40:
        return 2
    if internal_value >= 20:
        return 1
    return 0


@dataclass(frozen=True)
class RatingUpgradeThreshold:
    """One row of the guide's monthly rating-increase table."""

    max_price_change_pct: int
    min_service: int
    min_security: int
    min_cleaning: int
    min_sales_yen: int


@dataclass(frozen=True)
class RatingDowngradeThreshold:
    """One row of the guide's monthly rating-decrease table."""

    min_price_change_pct: int
    below_service: int
    below_security: int
    below_cleaning: int
    below_sales_yen: int


# Source: the guide's "ランク評価値の増減要因" table, printed twice with
# cell-for-cell identical values: "オールテクニックガイド" 評価関連 (書籍頁75,
# PDF4 page 14) and "お店の評価の増加・減少の原因" (書籍頁39, PDF1 page 17).
# Task #86 re-read both at 5x render and corrected 11 cells that an earlier
# manual transcription had wrong (the "near-duplicate tables differ" note
# this comment used to carry was that transcription error, not a real
# conflict), and added the 0-star (☆☆☆☆☆) row both pages print but the
# earlier transcription had dropped. `price_change_pct` is the sale price's
# percent change from the guide's standard price (negative = discounted,
# positive = marked up); the guide prints it as "-30%以下" (p.75) /
# "30%以下" in a 販売価格率 column (p.39), and the decrease side as "+1%以上"
# / "101%以上".
UPGRADE_THRESHOLDS_BY_CURRENT_STARS: dict[int, RatingUpgradeThreshold] = {
    5: RatingUpgradeThreshold(max_price_change_pct=-30, min_service=100, min_security=100, min_cleaning=100, min_sales_yen=15_000_000),
    4: RatingUpgradeThreshold(max_price_change_pct=-20, min_service=90, min_security=90, min_cleaning=100, min_sales_yen=10_000_000),
    3: RatingUpgradeThreshold(max_price_change_pct=-15, min_service=80, min_security=85, min_cleaning=95, min_sales_yen=9_000_000),
    2: RatingUpgradeThreshold(max_price_change_pct=-10, min_service=70, min_security=80, min_cleaning=90, min_sales_yen=7_000_000),
    1: RatingUpgradeThreshold(max_price_change_pct=-5, min_service=60, min_security=75, min_cleaning=85, min_sales_yen=5_000_000),
    0: RatingUpgradeThreshold(max_price_change_pct=-1, min_service=50, min_security=70, min_cleaning=80, min_sales_yen=3_000_000),
}

# The ★5 decrease row's 清掃 cell is printed as a bare "100" on both pages,
# where every other cell in that column reads "N未満". Encoded as
# below_cleaning=100 (i.e. "less than 100"), the only reading under which
# the cell is a penalty condition at all; a literal "cleaning == 100 costs a
# point" would penalise a perfect score. Not a numeric guess: the printed
# number is kept as-is, only the missing "未満" is inferred from its column.
DOWNGRADE_THRESHOLDS_BY_CURRENT_STARS: dict[int, RatingDowngradeThreshold] = {
    5: RatingDowngradeThreshold(min_price_change_pct=1, below_service=80, below_security=80, below_cleaning=100, below_sales_yen=3_000_000),
    4: RatingDowngradeThreshold(min_price_change_pct=1, below_service=70, below_security=70, below_cleaning=95, below_sales_yen=2_500_000),
    3: RatingDowngradeThreshold(min_price_change_pct=1, below_service=60, below_security=65, below_cleaning=90, below_sales_yen=2_000_000),
    2: RatingDowngradeThreshold(min_price_change_pct=1, below_service=50, below_security=60, below_cleaning=85, below_sales_yen=1_500_000),
    1: RatingDowngradeThreshold(min_price_change_pct=1, below_service=40, below_security=55, below_cleaning=80, below_sales_yen=1_000_000),
    0: RatingDowngradeThreshold(min_price_change_pct=1, below_service=30, below_security=50, below_cleaning=75, below_sales_yen=500_000),
}

UPGRADE_MIN_CRITERIA_MET = 3
"""Source: "内部評価値を増減させるには5項目中3つをクリアしている必要がある"
-- at least 3 of the 5 upgrade criteria must be met, not all 5."""

UPGRADE_POINTS = 5
DOWNGRADE_POINTS_PER_CRITERION = -1
ANGRY_CUSTOMER_DOWNGRADE_PROBABILITY = (1, 6)
"""Source: "お客に怒られる(1/6の確率)で-1" -- a 1-in-6 chance per angry
customer, expressed as a (numerator, denominator) fraction rather than a
float so the exact ratio stays visible. Rolling this probability is outside
this module's scope; ANGRY_CUSTOMER_DOWNGRADE_POINTS is what to apply if a
caller's own dice roll succeeds."""
ANGRY_CUSTOMER_DOWNGRADE_POINTS = -1
SHOPLIFTING_DOWNGRADE_POINTS = -1
DONATION_UPGRADE_POINTS = 5


@dataclass(frozen=True)
class RatingMonthlyInputs:
    current_internal_value: int
    price_change_pct: int
    service_value: float
    security_value: float
    cleaning_value: float
    monthly_sales_yen: int

    def __post_init__(self) -> None:
        if not 0 <= self.current_internal_value <= 100:
            raise ValueError("current_internal_value must be 0..100")
        if self.monthly_sales_yen < 0:
            raise ValueError("monthly_sales_yen must be >= 0")


@dataclass(frozen=True)
class RatingMonthlyEvaluation:
    inputs: RatingMonthlyInputs
    current_stars: int
    criteria_met: int
    upgrade_applies: bool
    downgrade_points: int

    @property
    def net_point_change(self) -> int:
        change = self.downgrade_points
        if self.upgrade_applies:
            change += UPGRADE_POINTS
        return change

    @property
    def next_internal_value(self) -> int:
        return max(0, min(100, self.inputs.current_internal_value + self.net_point_change))


def evaluate_monthly_rating_change(inputs: RatingMonthlyInputs) -> RatingMonthlyEvaluation:
    """Evaluate one month's rating (★) increase/decrease per the guide's table.

    Source: strategy guide "オールテクニックガイド" 評価関連 page. Increase:
    at least 3 of (price/service/security/cleaning/sales) meet the current
    rank's upgrade thresholds -> +5. Decrease: -1 for each of the same 5
    criteria that falls below the current rank's downgrade thresholds. Other
    guide-listed adjustments (an angry customer at a 1/6 chance -1,
    shoplifting -1, a donation event +5) are *not* included here, since they
    are per-event rather than per-month-end triggers; apply
    ANGRY_CUSTOMER_DOWNGRADE_POINTS / SHOPLIFTING_DOWNGRADE_POINTS /
    DONATION_UPGRADE_POINTS separately when those events occur.

    This function does not itself convert `next_internal_value` back to a
    star count; call `star_rank_for_internal_value` on the result if needed.
    """
    current_stars = star_rank_for_internal_value(inputs.current_internal_value)
    upgrade = UPGRADE_THRESHOLDS_BY_CURRENT_STARS[current_stars]
    downgrade = DOWNGRADE_THRESHOLDS_BY_CURRENT_STARS[current_stars]

    criteria_met = sum(
        (
            inputs.price_change_pct <= upgrade.max_price_change_pct,
            inputs.service_value >= upgrade.min_service,
            inputs.security_value >= upgrade.min_security,
            inputs.cleaning_value >= upgrade.min_cleaning,
            inputs.monthly_sales_yen >= upgrade.min_sales_yen,
        )
    )
    upgrade_applies = criteria_met >= UPGRADE_MIN_CRITERIA_MET

    criteria_failed = sum(
        (
            inputs.price_change_pct >= downgrade.min_price_change_pct,
            inputs.service_value < downgrade.below_service,
            inputs.security_value < downgrade.below_security,
            inputs.cleaning_value < downgrade.below_cleaning,
            inputs.monthly_sales_yen < downgrade.below_sales_yen,
        )
    )
    downgrade_points = criteria_failed * DOWNGRADE_POINTS_PER_CRITERION

    return RatingMonthlyEvaluation(
        inputs=inputs,
        current_stars=current_stars,
        criteria_met=criteria_met,
        upgrade_applies=upgrade_applies,
        downgrade_points=downgrade_points,
    )
