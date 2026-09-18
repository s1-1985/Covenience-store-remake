class_name StoreRating
extends RefCounted

# --- CONFIRMED_OFFICIAL house rule ----------------------------------------
#
# Ported verbatim from reference_sim/conveni_sim/store_rating.py, which is
# itself a direct transcription of the strategy guide's own published
# rating table ("オールテクニックガイド" 評価関連 page, 書籍頁74-75; used
# over the near-duplicate table on 書籍頁38-39 whose security/cleaning
# thresholds differed slightly on manual transcription --
# docs/research/strategy-guide-fixture-crosscheck-2026-09-16.md). Unlike
# the REMAKE_BALANCED_DEFAULT modules elsewhere in this client, the
# thresholds and star breakpoints below are not this project's own guess:
# they are the guide's own numbers.

const UPGRADE_MIN_CRITERIA_MET := 3
const UPGRADE_POINTS := 5
const DOWNGRADE_POINTS_PER_CRITERION := -1
const ANGRY_CUSTOMER_DOWNGRADE_POINTS := -1
const SHOPLIFTING_DOWNGRADE_POINTS := -1
const DONATION_UPGRADE_POINTS := 5

const UPGRADE_THRESHOLDS_BY_CURRENT_STARS := {
    5: {"max_price_change_pct": -30, "min_service": 100, "min_security": 100, "min_cleaning": 100, "min_sales_yen": 15000000},
    4: {"max_price_change_pct": -20, "min_service": 90, "min_security": 90, "min_cleaning": 95, "min_sales_yen": 10000000},
    3: {"max_price_change_pct": -15, "min_service": 85, "min_security": 90, "min_cleaning": 95, "min_sales_yen": 9000000},
    2: {"max_price_change_pct": -10, "min_service": 70, "min_security": 80, "min_cleaning": 90, "min_sales_yen": 7000000},
    1: {"max_price_change_pct": -5, "min_service": 60, "min_security": 75, "min_cleaning": 85, "min_sales_yen": 5000000},
}

const DOWNGRADE_THRESHOLDS_BY_CURRENT_STARS := {
    5: {"min_price_change_pct": 1, "below_service": 100, "below_security": 80, "below_cleaning": 80, "below_sales_yen": 3000000},
    4: {"min_price_change_pct": 1, "below_service": 70, "below_security": 65, "below_cleaning": 95, "below_sales_yen": 2500000},
    3: {"min_price_change_pct": 1, "below_service": 60, "below_security": 60, "below_cleaning": 90, "below_sales_yen": 2000000},
    2: {"min_price_change_pct": 1, "below_service": 55, "below_security": 60, "below_cleaning": 85, "below_sales_yen": 1500000},
    1: {"min_price_change_pct": 1, "below_service": 30, "below_security": 50, "below_cleaning": 75, "below_sales_yen": 1000000},
}


func star_rank_for_internal_value(internal_value: int) -> int:
    assert(internal_value >= 0 and internal_value <= 100)
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


func evaluate_monthly_rating_change(
    current_internal_value: int,
    price_change_pct: int,
    service_value: float,
    security_value: float,
    cleaning_value: float,
    monthly_sales_yen: int
) -> Dictionary:
    assert(current_internal_value >= 0 and current_internal_value <= 100)
    assert(monthly_sales_yen >= 0)
    var current_stars := star_rank_for_internal_value(current_internal_value)
    # The guide's table has 5 rows (★1..★5); a 0-star store has no row of
    # its own, so it is evaluated against the ★1 row rather than inventing
    # a sixth, easier tier (matches store_rating.py's own comment).
    var table_rank: int = max(current_stars, 1)
    var upgrade: Dictionary = UPGRADE_THRESHOLDS_BY_CURRENT_STARS[table_rank]
    var downgrade: Dictionary = DOWNGRADE_THRESHOLDS_BY_CURRENT_STARS[table_rank]

    var criteria_met := 0
    if price_change_pct <= int(upgrade["max_price_change_pct"]):
        criteria_met += 1
    if service_value >= float(upgrade["min_service"]):
        criteria_met += 1
    if security_value >= float(upgrade["min_security"]):
        criteria_met += 1
    if cleaning_value >= float(upgrade["min_cleaning"]):
        criteria_met += 1
    if monthly_sales_yen >= int(upgrade["min_sales_yen"]):
        criteria_met += 1
    var upgrade_applies: bool = criteria_met >= UPGRADE_MIN_CRITERIA_MET

    var criteria_failed := 0
    if price_change_pct >= int(downgrade["min_price_change_pct"]):
        criteria_failed += 1
    if service_value < float(downgrade["below_service"]):
        criteria_failed += 1
    if security_value < float(downgrade["below_security"]):
        criteria_failed += 1
    if cleaning_value < float(downgrade["below_cleaning"]):
        criteria_failed += 1
    if monthly_sales_yen < int(downgrade["below_sales_yen"]):
        criteria_failed += 1
    var downgrade_points: int = criteria_failed * DOWNGRADE_POINTS_PER_CRITERION

    var net_point_change := downgrade_points
    if upgrade_applies:
        net_point_change += UPGRADE_POINTS
    var next_internal_value: int = max(0, min(100, current_internal_value + net_point_change))

    return {
        "current_stars": current_stars,
        "criteria_met": criteria_met,
        "upgrade_applies": upgrade_applies,
        "downgrade_points": downgrade_points,
        "net_point_change": net_point_change,
        "next_internal_value": next_internal_value,
    }
