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

var nearby_population: int
var customer_share_percent: float
var daily_visit_rate_per_population: float
var opening_minutes_per_day: int
var bad_weather_visit_multiplier: float
var is_bad_weather: bool
var rng: RandomNumberGenerator


func _init(demand_config: Dictionary, source_rng: RandomNumberGenerator) -> void:
    nearby_population = int(demand_config["nearby_population"])
    customer_share_percent = float(demand_config["customer_share_percent"])
    daily_visit_rate_per_population = float(demand_config["daily_visit_rate_per_population"])
    opening_minutes_per_day = int(demand_config["opening_minutes_per_day"])
    bad_weather_visit_multiplier = float(demand_config["bad_weather_visit_multiplier"])
    is_bad_weather = bool(demand_config.get("is_bad_weather", false))
    rng = source_rng
    assert(nearby_population >= 0)
    assert(customer_share_percent >= 0.0 and customer_share_percent <= 100.0)
    assert(daily_visit_rate_per_population >= 0.0)
    assert(opening_minutes_per_day > 0)
    assert(bad_weather_visit_multiplier >= 0.0)


func expected_arrivals_per_minute() -> float:
    var expected_daily_visitors := (
        nearby_population * (customer_share_percent / 100.0) * daily_visit_rate_per_population
    )
    if is_bad_weather:
        expected_daily_visitors *= bad_weather_visit_multiplier
    return expected_daily_visitors / opening_minutes_per_day


func customer_arrives_this_minute() -> bool:
    var rate := expected_arrivals_per_minute()
    if rate <= 0.0:
        return false
    return rng.randf() < min(1.0, rate)
