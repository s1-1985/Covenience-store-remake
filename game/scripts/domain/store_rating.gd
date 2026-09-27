class_name StoreRating
extends RefCounted

# --- CONFIRMED_OFFICIAL house rule ----------------------------------------
#
# Ported verbatim from reference_sim/conveni_sim/store_rating.py, which is
# itself a direct transcription of the strategy guide's own published
# rating table, printed twice with cell-for-cell identical values
# ("オールテクニックガイド" 評価関連, 書籍頁75, and "お店の評価の増加・減少の
# 原因", 書籍頁39). Task #86 corrected 11 cells an earlier manual
# transcription had wrong and added the 0-star row both pages print (see
# store_rating.py and docs/decisions/0157-*.md). Unlike
# the REMAKE_BALANCED_DEFAULT modules elsewhere in this client, the
# thresholds and star breakpoints below are not this project's own guess:
# they are the guide's own numbers.

# Task #129, CONFIRMED_BINARY (PS program SLPS_007.82, docs/research/
# ps1-executable-formulas-2026-09-26.md): the program keeps the score in
# 5..100 after each month's evaluation (0x80028A50), starts a new store at
# 10 (0x8001B120), and an angry customer only takes a point from a score of
# 6 or more (0x8003600C) -- so the score never drops below 5. It also uses
# the same table as the guide below (the 値段 column as 99/95/90/85/80/70 %
# of the list price, i.e. the guide's -1..-30 %), cell for cell.
const RATING_FLOOR := 5
const RATING_CAP := 100
const NEW_STORE_RATING := 10
# Each day at 0:00 the store's 人気 moves by this much for its current ★
# count (0x80028E60), never below the rating score, at most 100.
const DAILY_POPULARITY_CHANGE_BY_STARS := [-15, -10, -5, -3, 0, 5]
# The manager's advice when fewer than 3 items were good (0x80028800): the
# items in the order the program checks them, the advice lines (msg
# 251-255) and 「ランクが上がるでしょう」(msg 258).
const ADVICE_ITEMS := ["price", "service", "security", "cleaning", "sales"]
const ADVICE_TEXT := {
    "price": "もっと商品の値段を安くすると",
    "service": "もっとサービスを良くすると",
    "security": "もっとセキュリティを良くすると",
    "cleaning": "もっと店内を清潔にすると",
    "sales": "もっと売り上げを伸ばすと",
}
const ADVICE_TAIL := "ランクが上がるでしょう"
# Half the サービス advice names a service fixture (msg 256), half the
# セキュリティ advice a facility to induce nearby (msg 257); the program
# picks one of these at random (0x8009968C / 0x800CD6EC).
const ADVICE_SERVICE_FIXTURES := ["観葉植物", "ベンチ", "噴水"]
const ADVICE_SECURITY_FACILITIES := ["交番", "消防署"]

const UPGRADE_MIN_CRITERIA_MET := 3
const UPGRADE_POINTS := 5
const DOWNGRADE_POINTS_PER_CRITERION := -1
const ANGRY_CUSTOMER_DOWNGRADE_POINTS := -1
const SHOPLIFTING_DOWNGRADE_POINTS := -1
const DONATION_UPGRADE_POINTS := 5

# Task #65: re-verified 2026-09-24 directly against a 400dpi rescan of the
# strategy guide's third companion book ("攻略&データブック", オールテク
# ニックガイド 評価関連, print page 75): "お客に怒られる=1/6の確率で-1、
# 万引き=-1、寄付イベント=+5" -- confirms the three point constants above
# exactly (this file already had them, ported from reference_sim/conveni_sim/
# store_rating.py) and gives the angry-customer trigger's exact probability,
# which this file had not yet carried as a named constant.
const ANGRY_CUSTOMER_DOWNGRADE_PROBABILITY_NUMERATOR := 1
const ANGRY_CUSTOMER_DOWNGRADE_PROBABILITY_DENOMINATOR := 6

const UPGRADE_THRESHOLDS_BY_CURRENT_STARS := {
    5: {"max_price_change_pct": -30, "min_service": 100, "min_security": 100, "min_cleaning": 100, "min_sales_yen": 15000000},
    4: {"max_price_change_pct": -20, "min_service": 90, "min_security": 90, "min_cleaning": 100, "min_sales_yen": 10000000},
    3: {"max_price_change_pct": -15, "min_service": 80, "min_security": 85, "min_cleaning": 95, "min_sales_yen": 9000000},
    2: {"max_price_change_pct": -10, "min_service": 70, "min_security": 80, "min_cleaning": 90, "min_sales_yen": 7000000},
    1: {"max_price_change_pct": -5, "min_service": 60, "min_security": 75, "min_cleaning": 85, "min_sales_yen": 5000000},
    0: {"max_price_change_pct": -1, "min_service": 50, "min_security": 70, "min_cleaning": 80, "min_sales_yen": 3000000},
}

# The ★5 row's 清掃 cell is printed as a bare "100" (no "未満") on both
# pages; encoded as below_cleaning=100, same as store_rating.py.
const DOWNGRADE_THRESHOLDS_BY_CURRENT_STARS := {
    5: {"min_price_change_pct": 1, "below_service": 80, "below_security": 80, "below_cleaning": 100, "below_sales_yen": 3000000},
    4: {"min_price_change_pct": 1, "below_service": 70, "below_security": 70, "below_cleaning": 95, "below_sales_yen": 2500000},
    3: {"min_price_change_pct": 1, "below_service": 60, "below_security": 65, "below_cleaning": 90, "below_sales_yen": 2000000},
    2: {"min_price_change_pct": 1, "below_service": 50, "below_security": 60, "below_cleaning": 85, "below_sales_yen": 1500000},
    1: {"min_price_change_pct": 1, "below_service": 40, "below_security": 55, "below_cleaning": 80, "below_sales_yen": 1000000},
    0: {"min_price_change_pct": 1, "below_service": 30, "below_security": 50, "below_cleaning": 75, "below_sales_yen": 500000},
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
    var upgrade: Dictionary = UPGRADE_THRESHOLDS_BY_CURRENT_STARS[current_stars]
    var downgrade: Dictionary = DOWNGRADE_THRESHOLDS_BY_CURRENT_STARS[current_stars]

    var criteria_met := 0
    # Task #129: which items were not good, in ADVICE_ITEMS order (the
    # program's bit mask for the manager's advice).
    var not_good: Array[String] = []
    var good_flags := [
        price_change_pct <= int(upgrade["max_price_change_pct"]),
        service_value >= float(upgrade["min_service"]),
        security_value >= float(upgrade["min_security"]),
        cleaning_value >= float(upgrade["min_cleaning"]),
        monthly_sales_yen >= int(upgrade["min_sales_yen"]),
    ]
    for index in range(good_flags.size()):
        if good_flags[index]:
            criteria_met += 1
        else:
            not_good.append(ADVICE_ITEMS[index])
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
    var next_internal_value: int = clampi(current_internal_value + net_point_change, RATING_FLOOR, RATING_CAP)

    return {
        "current_stars": current_stars,
        "criteria_met": criteria_met,
        "upgrade_applies": upgrade_applies,
        "downgrade_points": downgrade_points,
        "net_point_change": net_point_change,
        "next_internal_value": next_internal_value,
        "not_good_items": not_good,
    }


# Task #129: the day's change in 人気 (CONFIRMED_BINARY, see
# DAILY_POPULARITY_CHANGE_BY_STARS).
func next_day_popularity(popularity: int, internal_value: int) -> int:
    var stars := star_rank_for_internal_value(internal_value)
    var next: int = popularity + int(DAILY_POPULARITY_CHANGE_BY_STARS[stars])
    return mini(RATING_CAP, maxi(next, internal_value))


# Task #129: the manager's advice after a month with fewer than 3 good
# items (CONFIRMED_BINARY, 0x80028800): with a chance of the manager's
# ability out of 100, one of the five items is drawn at random; if that
# item was not good, the advice for it is given (else nothing). Returns ""
# when no advice is given.
func manager_advice(evaluation: Dictionary, manager_ability: int, rng: RandomNumberGenerator) -> String:
    if bool(evaluation["upgrade_applies"]):
        return ""
    if rng.randi_range(1, 100) > manager_ability:
        return ""
    var item: String = ADVICE_ITEMS[rng.randi_range(0, ADVICE_ITEMS.size() - 1)]
    if not (evaluation["not_good_items"] as Array).has(item):
        return ""
    var text := ""
    if item == "service" and rng.randi_range(0, 1) == 0:
        text = "%sなどを置いて\n" % ADVICE_SERVICE_FIXTURES[rng.randi_range(0, ADVICE_SERVICE_FIXTURES.size() - 1)]
    elif item == "security" and rng.randi_range(0, 1) == 0:
        text = "%sなどを近くに誘致して\n" % ADVICE_SECURITY_FACILITIES[rng.randi_range(0, ADVICE_SECURITY_FACILITIES.size() - 1)]
    return text + str(ADVICE_TEXT[item]) + "\n" + ADVICE_TAIL
