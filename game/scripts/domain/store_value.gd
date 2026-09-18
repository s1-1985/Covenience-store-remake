class_name StoreValue
extends RefCounted

# --- CONFIRMED_OFFICIAL house rule ----------------------------------------
#
# Ported verbatim from reference_sim/conveni_sim/store_value.py, itself a
# transcription of the strategy guide's service/security/cleaning value
# formulas ("オールテクニックガイド" 内装関連/誘致関連 pages --
# docs/research/strategy-guide-fixture-crosscheck-2026-09-16.md section 7).
#
# One simplification versus store_value.py: `compute_security_value()`
# there also accepts a police-box/fire-station SecurityFacilityCoverage
# bonus (each within the store's confirmed 16x16-tile range). This client
# has no police-box/fire-station fixtures or spatial facility search yet,
# so that bonus is omitted here entirely (equivalent to always passing
# zero coverage) rather than guessed at.

const STORE_SIZE_VALUE_MULTIPLIER := {
    "small": 1.5,
    "medium": 1.65,
    "large": 1.8,
}


func compute_service_value(
    staff_service_skills: Array, fixture_service_bonuses: Array
) -> float:
    assert(not staff_service_skills.is_empty())
    var total := 0.0
    for value in staff_service_skills:
        assert(int(value) >= 0)
        total += float(value)
    var average: float = total / staff_service_skills.size()
    var bonus_total := 0.0
    for bonus in fixture_service_bonuses:
        assert(int(bonus) >= 0)
        bonus_total += float(bonus)
    return average + bonus_total


func compute_security_value(staff_security_skills: Array, size_tier: String) -> float:
    assert(STORE_SIZE_VALUE_MULTIPLIER.has(size_tier))
    var total := 0.0
    for value in staff_security_skills:
        assert(int(value) >= 0)
        total += float(value)
    return total * float(STORE_SIZE_VALUE_MULTIPLIER[size_tier])


func compute_cleaning_value(staff_cleaning_skills: Array, size_tier: String) -> float:
    assert(STORE_SIZE_VALUE_MULTIPLIER.has(size_tier))
    var total := 0.0
    for value in staff_cleaning_skills:
        assert(int(value) >= 0)
        total += float(value)
    return total * float(STORE_SIZE_VALUE_MULTIPLIER[size_tier])
