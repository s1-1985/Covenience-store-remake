class_name LandValuePolicy
extends RefCounted

# --- REMAKE_BALANCED_DEFAULT house rule ---------------------------------
#
# Ported from reference_sim/conveni_sim/remake_land_value.py. Evidence
# confirms land value rises with both local urbanization (a busier,
# more built-up surrounding area raises nearby land price) and elapsed time
# (later years raise land price town-wide), and that deliberately inflating
# land value near a rival store is a viable competitive tactic
# (docs/research/ps-gameplay-economy-evidence-2026-09-05.md section 8;
# strategy-guide-full-decode-2026-09-16.md section 31.3; item 18 of section
# 41's "existence confirmed, formula unconfirmed" list: "地価変動式"). No
# exact formula, urbanization input variable, annual growth rate, tile-vs-
# area unit, or upper/lower bound is published. This is a
# REMAKE_BALANCED_DEFAULT placeholder over the guide's own suggested
# multiplicative structure (land_price = base_price *
# local_development_factor * time_inflation_factor), not a recovered
# original formula -- expected to be retuned or replaced outright if
# better evidence surfaces. It is informational only in this client: no
# feature yet consumes it (no land purchase/store-sale mechanic exists).

const ANNUAL_INFLATION_RATE := 0.05
const POPULATION_DEVELOPMENT_REFERENCE := 20000
const STORE_DENSITY_REFERENCE_COUNT := 8
const POPULATION_DEVELOPMENT_WEIGHT := 0.6
const STORE_DENSITY_DEVELOPMENT_WEIGHT := 0.4
const MAX_LOCAL_DEVELOPMENT_FACTOR := 3.0


func local_development_factor(town) -> float:
    var population_term: float = min(
        1.0, float(town.population) / POPULATION_DEVELOPMENT_REFERENCE
    )
    var density_term: float = min(
        1.0, float(town.store_count_including_rivals) / STORE_DENSITY_REFERENCE_COUNT
    )
    var development_level := (
        POPULATION_DEVELOPMENT_WEIGHT * population_term
        + STORE_DENSITY_DEVELOPMENT_WEIGHT * density_term
    )
    return 1.0 + development_level * (MAX_LOCAL_DEVELOPMENT_FACTOR - 1.0)


func time_inflation_factor(elapsed_years: float) -> float:
    assert(elapsed_years >= 0.0)
    return pow(1.0 + ANNUAL_INFLATION_RATE, elapsed_years)


func current_land_price_yen(base_land_price_yen: int, town, elapsed_years: float) -> int:
    assert(base_land_price_yen >= 0)
    var factor: float = local_development_factor(town) * time_inflation_factor(elapsed_years)
    return int(round(base_land_price_yen * factor))
