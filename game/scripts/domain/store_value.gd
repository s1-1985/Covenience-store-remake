class_name StoreValue
extends RefCounted

# --- CONFIRMED_BINARY house rule (task #128) ------------------------------
#
# The store's サービス / 警備 / 清掃 as the PS program computes them
# (SLPS_007.82: サービス 0x800221D0, 警備 0x800224E0, 清掃 0x8002287C; see
# docs/research/ps1-executable-formulas-2026-09-26.md). Before task #128
# this file followed the strategy guide's own formula, which prints the
# store-size base value 1.5/1.65/1.8 as a multiplier; the program divides
# by it instead (清掃 = sum x 100 / 150..180), uses 2.5/2.75/3.0 for 警備,
# and caps all three values at 100.
#
# Keyed by size_tier ("small"/"medium"/"large"); the program keys the same
# numbers by store type (small, small, medium, medium, large, large).
# STORE_SIZE_VALUE_MULTIPLIER keeps the guide's printed base values; it is
# the set of known size tiers and the divisor for 清掃.

const STORE_SIZE_VALUE_MULTIPLIER := {
    "small": 1.5,
    "medium": 1.65,
    "large": 1.8,
}
const CLEANING_DIVISOR := {"small": 150, "medium": 165, "large": 180}
const SECURITY_DIVISOR := {"small": 250, "medium": 275, "large": 300}
const VALUE_CAP := 100
# 警備: each town square of a 交番 / 消防署 within 7 squares of the store's
# site adds this much (the program counts squares, not buildings).
const SECURITY_PER_SQUARE := {"交番": 10, "消防署": 5}
const SECURITY_REACH_SQUARES := 7


# サービス = the staff's 接客 averaged (integer) + the service fixtures'
# bonuses (観葉植物 2, ベンチ 4, 噴水 30), at most 100.
func compute_service_value(
    staff_service_skills: Array, fixture_service_bonuses: Array
) -> float:
    assert(not staff_service_skills.is_empty())
    var total := 0
    for value in staff_service_skills:
        assert(int(value) >= 0)
        total += int(value)
    var value := total / staff_service_skills.size()
    for bonus in fixture_service_bonuses:
        assert(int(bonus) >= 0)
        value += int(bonus)
    return float(mini(VALUE_CAP, value))


# 警備 = the staff's 警備 summed x 100 / (250, 275, 300) + the security
# facilities' squares nearby, at most 100.
func compute_security_value(staff_security_skills: Array, size_tier: String, facility_bonus := 0) -> float:
    assert(SECURITY_DIVISOR.has(size_tier))
    var total := 0
    for value in staff_security_skills:
        assert(int(value) >= 0)
        total += int(value)
    return float(mini(VALUE_CAP, total * 100 / int(SECURITY_DIVISOR[size_tier]) + facility_bonus))


# 清掃 = the staff's 清掃 summed x 100 / (150, 165, 180), at most 100.
func compute_cleaning_value(staff_cleaning_skills: Array, size_tier: String) -> float:
    assert(CLEANING_DIVISOR.has(size_tier))
    var total := 0
    for value in staff_cleaning_skills:
        assert(int(value) >= 0)
        total += int(value)
    return float(mini(VALUE_CAP, total * 100 / int(CLEANING_DIVISOR[size_tier])))
