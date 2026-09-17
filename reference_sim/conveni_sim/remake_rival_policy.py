from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

# --- REMAKE_BALANCED_DEFAULT house rule ---------------------------------
#
# rival.py's RivalChainRuntime deliberately never decides anything itself --
# "callers must provide each observed or policy-produced transition
# explicitly" -- because the guide confirms which *factors* matter to rival
# behavior (price, popularity, service, trade-area overlap, cash, land
# value; strategy-guide-full-decode-2026-09-16.md section 31.5's own
# suggested RivalPolicyInputs/RivalStoreState shape) but never publishes
# decision weights (section 41: "ライバルAI意思決定"). This module is a
# REMAKE_BALANCED_DEFAULT decision policy over those confirmed factors, not
# a recovered original AI -- a playable placeholder to retune (or replace
# outright if better evidence surfaces) after actual play.


class RivalDecision(str, Enum):
    EXPAND = "expand"
    HOLD = "hold"
    RETREAT = "retreat"


@dataclass(frozen=True)
class RivalPolicyInputs:
    """Observable state this policy considers for one rival store.

    Every field here is a guide-confirmed factor in rival behavior; only
    their combination into a decision is this module's own guess.
    """

    cash_yen: int
    monthly_profit_yen: int
    own_popularity: int
    rival_popularity: int
    own_service_value: float
    rival_service_value: float
    trade_area_overlap_ratio: float
    """0.0 (no shared trade area) to 1.0 (fully overlapping); caller-computed."""

    def __post_init__(self) -> None:
        if not 0 <= self.own_popularity <= 100:
            raise ValueError("own_popularity must be 0..100")
        if not 0 <= self.rival_popularity <= 100:
            raise ValueError("rival_popularity must be 0..100")
        if not 0.0 <= self.trade_area_overlap_ratio <= 1.0:
            raise ValueError("trade_area_overlap_ratio must be 0.0..1.0")


COMPETITIVE_PRESSURE_POPULARITY_WEIGHT = 0.5
COMPETITIVE_PRESSURE_SERVICE_WEIGHT = 0.5
"""competitive_pressure = weighted average of (own store's popularity/
service disadvantage relative to the rival), each normalized to roughly
-1..1, then scaled by how much the two trade areas actually overlap (no
overlap means the two stores barely compete regardless of the gap)."""

RETREAT_PRESSURE_THRESHOLD = 0.3
"""A losing-money branch retreats once competitive_pressure exceeds this."""

EXPANSION_CASH_THRESHOLD_YEN = 20_000_000
"""Minimum cash on hand before this policy considers opening a new branch,
loosely anchored to the guide's own small-store construction cost
(6,000,000 yen) plus a working-capital margin."""
EXPANSION_PRESSURE_CEILING = -0.1
"""Only expand where the rival chain is not already under meaningful
competitive pressure (i.e. it is doing at least as well as the player,
with a small margin)."""


def _competitive_pressure(inputs: RivalPolicyInputs) -> float:
    popularity_gap = (inputs.rival_popularity - inputs.own_popularity) / 100.0
    service_gap = _normalized_service_gap(inputs.rival_service_value, inputs.own_service_value)
    raw = (
        COMPETITIVE_PRESSURE_POPULARITY_WEIGHT * popularity_gap
        + COMPETITIVE_PRESSURE_SERVICE_WEIGHT * service_gap
    )
    return raw * inputs.trade_area_overlap_ratio


def _normalized_service_gap(rival_value: float, own_value: float) -> float:
    total = rival_value + own_value
    if total <= 0:
        return 0.0
    return (rival_value - own_value) / total


class RemakeBalancedRivalPolicy:
    """Concrete rival decision policy over RivalPolicyInputs (see module docstring)."""

    def decide(self, inputs: RivalPolicyInputs) -> RivalDecision:
        pressure = _competitive_pressure(inputs)

        if inputs.monthly_profit_yen < 0 and pressure > RETREAT_PRESSURE_THRESHOLD:
            return RivalDecision.RETREAT

        if (
            inputs.monthly_profit_yen > 0
            and inputs.cash_yen >= EXPANSION_CASH_THRESHOLD_YEN
            and pressure <= EXPANSION_PRESSURE_CEILING
        ):
            return RivalDecision.EXPAND

        return RivalDecision.HOLD
