class_name CustomerShare
extends RefCounted

# --- REMAKE_BALANCED_DEFAULT house rule ---------------------------------
#
# Ported from reference_sim/conveni_sim/remake_customer_share.py, itself
# already tagged REMAKE_BALANCED_DEFAULT there: the strategy guide and
# first-title community research both name the *factors* behind 顧客独占率
# (customer share) -- service, cleaning, security, popularity, assortment
# breadth, business hours, weather, and nearby rival stores
# (PROJECT_MEMORY.md section 8) -- but never publish a formula combining
# them (docs/research/strategy-guide-full-decode-2026-09-16.md section 41
# lists "顧客独占率計算式" itself as explicitly un-derivable from the
# guide). The weights below match the Python source field-for-field and
# weight-for-weight; this is a recovered-factor-list, invented-combination
# placeholder, not a recovered original formula, exactly as documented in
# the Python source it mirrors.
#
# Deliberate simplification versus remake_customer_share.py: the Python
# source also accepts `weather`/`competing_store_ids` and folds them into
# this same 0-100 score via a multiplicative penalty/dilution, treating any
# omitted factor (including these two) as "unknown" and excluding it from
# the weighted average. This port omits both parameters entirely rather
# than adding an "unknown" representation for values this client always
# has -- demand_policy.gd already applies bad-weather and rival-store
# dilution to the whole expected-visitor estimate downstream of this score
# (task #27/#36-era code, unchanged by this task). Feeding the same two
# factors into this score as well would double-count them, not add
# fidelity; the target-quantity difference (whole visitor estimate here,
# 0-100 share score in reference_sim) is the same deliberate scope
# simplification demand_policy.gd's own header comment already documents.
# Likewise, every one of the six weighted factors below is always known in
# this client by the time this is called (VerticalSliceSimulation always
# has computed all of popularity/service_value/security_value/
# cleaning_value/product count/opening_minutes_per_day before calling
# this), so the Python source's "exclude unknown factors and renormalize"
# branch has no reachable case here and is not ported; weight_total is
# always exactly 1.0 (the six weights below sum to 1.0).
const POPULARITY_WEIGHT := 0.30
const SERVICE_WEIGHT := 0.25
const CLEANING_WEIGHT := 0.15
const SECURITY_WEIGHT := 0.10
const ASSORTMENT_WEIGHT := 0.10
const HOURS_WEIGHT := 0.10

const ASSORTMENT_SATURATION_PRODUCT_COUNT := 20
const FULL_DAY_MINUTES := 24 * 60


# service_value/cleaning_value/security_value come from store_value.gd,
# whose scale is not independently invented here: store_rating.gd's own
# CONFIRMED_OFFICIAL upgrade/downgrade thresholds already treat those same
# three values as roughly 0-100 (e.g. "min_service": 100 for 5-star), so
# clamping them to [0, 100] here reuses that same confirmed ceiling rather
# than guessing a new one; store_value.gd's own outputs are not otherwise
# bounded to 100 (e.g. more/higher-skill staff than this vertical slice's
# fixed 2-person roster could in principle exceed it).
func compute_customer_share_percent(
    popularity: int,
    service_value: float,
    cleaning_value: float,
    security_value: float,
    assortment_product_count: int,
    opening_minutes_per_day: int
) -> int:
    assert(popularity >= 0 and popularity <= 100)
    assert(assortment_product_count >= 0)
    assert(opening_minutes_per_day >= 0)
    var assortment_score: float = min(
        100.0,
        float(assortment_product_count) / float(ASSORTMENT_SATURATION_PRODUCT_COUNT) * 100.0
    )
    var hours_score: float = float(opening_minutes_per_day) / float(FULL_DAY_MINUTES) * 100.0
    var weighted_sum: float = (
        POPULARITY_WEIGHT * float(popularity)
        + SERVICE_WEIGHT * clamp(service_value, 0.0, 100.0)
        + CLEANING_WEIGHT * clamp(cleaning_value, 0.0, 100.0)
        + SECURITY_WEIGHT * clamp(security_value, 0.0, 100.0)
        + ASSORTMENT_WEIGHT * assortment_score
        + HOURS_WEIGHT * hours_score
    )
    return int(clamp(round(weighted_sum), 0.0, 100.0))
