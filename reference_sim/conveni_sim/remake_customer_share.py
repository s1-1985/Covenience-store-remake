from __future__ import annotations

from typing import Optional

from .customer_share import CustomerShareInputs

# --- REMAKE_BALANCED_DEFAULT house rule ---------------------------------
#
# The strategy guide and first-title community research both name the
# *factors* behind 顧客独占率 (customer share) -- service, cleaning,
# security, popularity, assortment breadth, business hours, weather, and
# nearby rival stores (PROJECT_MEMORY.md section 8;
# docs/research/strategy-guide-full-decode-2026-09-16.md section 41 lists
# "顧客独占率計算式" itself as explicitly un-derivable from the guide) -- but
# never publish a formula combining them. Everything below this comment is
# therefore a deliberately-tagged `EvidenceLevel.REMAKE_BALANCED_DEFAULT`
# house rule, not a recovered original formula: a playable placeholder to
# unblock the demand pipeline, expected to be retuned (or replaced outright
# if better evidence surfaces) after actual playtesting, per the project's
# "build one, play it, adjust the numbers that feel wrong" approach agreed
# for this pass.
#
# Weights sum to 1.0 across whichever of the six weighted factors are
# actually known; an unknown factor is excluded and the rest are
# renormalized, rather than treating "unknown" as "zero" (an unknown
# security value must not silently read as "worst possible security").
POPULARITY_WEIGHT = 0.30
SERVICE_WEIGHT = 0.25
CLEANING_WEIGHT = 0.15
SECURITY_WEIGHT = 0.10
ASSORTMENT_WEIGHT = 0.10
HOURS_WEIGHT = 0.10

ASSORTMENT_SATURATION_PRODUCT_COUNT = 20
"""Carrying this many distinct products (or more) scores the full 100 on the
assortment factor; picked as a round number roughly matching the guide's own
~26-category product master, not a recovered threshold."""

FULL_DAY_MINUTES = 24 * 60

RIVAL_DILUTION_PER_COMPETITOR = 0.08
"""Each competing store the caller lists as sharing this trade area shaves
this fraction off the pre-rival score, capped by MAX_RIVAL_DILUTION so a
crowded map can't zero a store out entirely from this factor alone."""
MAX_RIVAL_DILUTION = 0.6

BAD_WEATHER_VALUES = frozenset({"雨", "雪", "雨・雪", "大雨", "雷雨", "台風", "大雪", "荒天"})
"""The guide's own 5-way weather category table (quick reference,
"天候のパーセンテージ設定", book page 3) is 快晴/晴れ/曇り/雨・雪/荒天, with
荒天 itself glossed as the umbrella "大雨・雷雨・台風・大雪" -- re-verified
2026-09-24 against a 400dpi rescan (see baseline_data.MONTHLY_WEATHER_
PERCENTAGES and decision 0132), superseding this constant's own prior
comment, which mis-cited the columns as "快晴/大雨/雪/台風/荒天" (treating
荒天's own component conditions as if they were separate top-level columns).
This set includes both the two adverse bucket names themselves (雨・雪,
荒天) and their component condition words, so a caller passing either the
bucket label or a specific condition is recognized; 快晴/晴れ/曇り are not
bad weather here (the guide does not say cloudy skies reduce visits)."""
BAD_WEATHER_PENALTY = 0.15


def compute_customer_share_percent(inputs: CustomerShareInputs) -> Optional[int]:
    """REMAKE_BALANCED_DEFAULT 0-100 customer-share estimate from known inputs.

    Returns None only when every weighted factor is unknown (nothing to
    average). The result is meant to be fed to
    `CustomerShareRuntime.apply_share(value, source="remake_balanced_default")`,
    not to replace that runtime's own evidence-safe bookkeeping.
    """
    weighted_sum = 0.0
    weight_total = 0.0

    for value, weight in (
        (inputs.popularity, POPULARITY_WEIGHT),
        (inputs.service, SERVICE_WEIGHT),
        (inputs.cleaning, CLEANING_WEIGHT),
        (inputs.security, SECURITY_WEIGHT),
    ):
        if value is None:
            continue
        weighted_sum += weight * value
        weight_total += weight

    if inputs.assortment_product_ids is not None:
        assortment_score = min(
            100.0,
            len(inputs.assortment_product_ids) / ASSORTMENT_SATURATION_PRODUCT_COUNT * 100.0,
        )
        weighted_sum += ASSORTMENT_WEIGHT * assortment_score
        weight_total += ASSORTMENT_WEIGHT

    if inputs.opening_minutes_per_day is not None:
        hours_score = inputs.opening_minutes_per_day / FULL_DAY_MINUTES * 100.0
        weighted_sum += HOURS_WEIGHT * hours_score
        weight_total += HOURS_WEIGHT

    if weight_total == 0:
        return None

    score = weighted_sum / weight_total

    if inputs.competing_store_ids:
        dilution = min(
            MAX_RIVAL_DILUTION,
            RIVAL_DILUTION_PER_COMPETITOR * len(inputs.competing_store_ids),
        )
        score *= 1 - dilution

    if inputs.weather in BAD_WEATHER_VALUES:
        score *= 1 - BAD_WEATHER_PENALTY

    return max(0, min(100, round(score)))
