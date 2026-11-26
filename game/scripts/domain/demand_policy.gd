class_name DemandPolicy
extends RefCounted

# --- REMAKE_BALANCED_DEFAULT house rule ---------------------------------
#
# reference_sim/conveni_sim/customer_demand.py's CustomerDemandPolicy
# protocol deliberately exposes no arrival-rate formula
# (docs/research/strategy-guide-full-decode-2026-09-16.md section 41 lists
# "客数発生式" as existence-confirmed but formula-unconfirmed).
# reference_sim/conveni_sim/remake_demand_policy.py already fills that gap
# with a tagged REMAKE_BALANCED_DEFAULT placeholder
# (population * share% * daily_visit_rate_per_population, spread evenly
# across opening minutes, reduced under bad weather). This class ports the
# same structure into the Godot production client so the store can gain
# customers on its own instead of only through the manual
# `VerticalSliceSimulation.start_next_customer()` boundary. The combination
# of factors into a rate is this port's own guess, not a recovered original
# formula, exactly as documented in the Python source it mirrors.
#
# `rival_store_count` applies the same rival-dilution constants
# (RIVAL_DILUTION_PER_COMPETITOR / MAX_RIVAL_DILUTION) that
# reference_sim/conveni_sim/remake_customer_share.py applies to its 0-100
# customer_share_percent score, but here multiplies the whole expected-
# visitor estimate instead. That target-quantity difference is a deliberate
# scope simplification, not a second independent guess at the constants
# themselves: as of task #27, this Godot port does compute service/
# security/cleaning gameplay stats (store_value.gd's compute_service_value/
# compute_security_value/compute_cleaning_value, fed monthly into the star
# rating by VerticalSliceSimulation._evaluate_store_rating()), but nothing
# feeds them into remake_customer_share.py's weighted
# compute_customer_share_percent() formula here, and assortment breadth
# still has no stat at all -- so there is still no 0-100 share score in
# this port for rival_store_count to dilute (this comment previously
# (incorrectly) said the stats themselves didn't exist yet; corrected in
# task #43).
# Defaults to 0 (no rival stores), which is a no-op multiplier of 1.0 and
# leaves every existing caller/test that never sets it unaffected.

var nearby_population: int
var customer_share_percent: float
var daily_visit_rate_per_population: float
var opening_minutes_per_day: int
var bad_weather_visit_multiplier: float
var is_bad_weather: bool
var rival_store_count: int
var rng: RandomNumberGenerator

const RIVAL_DILUTION_PER_COMPETITOR := 0.08
const MAX_RIVAL_DILUTION := 0.6


func _init(demand_config: Dictionary, source_rng: RandomNumberGenerator) -> void:
    nearby_population = int(demand_config["nearby_population"])
    customer_share_percent = float(demand_config["customer_share_percent"])
    daily_visit_rate_per_population = float(demand_config["daily_visit_rate_per_population"])
    opening_minutes_per_day = int(demand_config["opening_minutes_per_day"])
    bad_weather_visit_multiplier = float(demand_config["bad_weather_visit_multiplier"])
    is_bad_weather = bool(demand_config.get("is_bad_weather", false))
    rival_store_count = int(demand_config.get("rival_store_count", 0))
    rng = source_rng
    assert(nearby_population >= 0)
    assert(customer_share_percent >= 0.0 and customer_share_percent <= 100.0)
    assert(daily_visit_rate_per_population >= 0.0)
    assert(opening_minutes_per_day > 0)
    assert(bad_weather_visit_multiplier >= 0.0)
    assert(rival_store_count >= 0)


func expected_arrivals_per_minute() -> float:
    var expected_daily_visitors := (
        nearby_population * (customer_share_percent / 100.0) * daily_visit_rate_per_population
    )
    if is_bad_weather:
        expected_daily_visitors *= bad_weather_visit_multiplier
    if rival_store_count > 0:
        var dilution: float = min(
            MAX_RIVAL_DILUTION, RIVAL_DILUTION_PER_COMPETITOR * rival_store_count
        )
        expected_daily_visitors *= 1.0 - dilution
    # Task #103: a closed day (臨時休業) has no opening minutes.
    if opening_minutes_per_day <= 0:
        return 0.0
    return expected_daily_visitors / opening_minutes_per_day


func customer_arrives_this_minute() -> bool:
    var rate := expected_arrivals_per_minute()
    if rate <= 0.0:
        return false
    return rng.randf() < min(1.0, rate)
