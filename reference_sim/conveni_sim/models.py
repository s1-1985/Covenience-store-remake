from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Any, Optional


class EvidenceLevel(str, Enum):
    CONFIRMED_OFFICIAL = "confirmed_official"
    CONFIRMED_VISUAL = "confirmed_visual"
    CONFIRMED_COMMUNITY = "confirmed_community"
    STRONG_INFERENCE = "strong_inference"
    PROVISIONAL = "provisional"
    HYPOTHESIS = "hypothesis"
    REMAKE_BALANCED_DEFAULT = "remake_balanced_default"


@dataclass(frozen=True)
class EvidenceValue:
    value: Any
    evidence: EvidenceLevel
    source: str
    note: str = ""


@dataclass(frozen=True)
class StoreVariant:
    id: str
    size_tier: str
    orientation: Optional[str]
    construction_price_yen: Optional[EvidenceValue]
    editable_floor: Optional[EvidenceValue]
    unlocked_at_beginner_start: Optional[EvidenceValue]


@dataclass(frozen=True)
class FixtureDefinition:
    id: str
    footprint: Optional[EvidenceValue]
    maintenance_yen_per_day: Optional[EvidenceValue] = None
    service_bonus: Optional[EvidenceValue] = None
    parking_capacity: Optional[EvidenceValue] = None
    sale_mode: str = "not_applicable"
    blocks_pedestrian: Optional[EvidenceValue] = None


@dataclass(frozen=True)
class PromotionDefinition:
    id: str
    cost_yen: EvidenceValue
    popularity_gain: EvidenceValue
    trigger_day: EvidenceValue
    trigger_hour: EvidenceValue


@dataclass(frozen=True)
class PermitDefinition:
    id: str
    fee_yen: Optional[EvidenceValue]
    exclusion_distance_tiles: Optional[EvidenceValue]
    eligibility_is_independent: EvidenceValue


@dataclass(frozen=True)
class ScenarioDefinition:
    id: str
    initial_cash_yen: EvidenceValue
    objective: EvidenceValue


@dataclass(frozen=True)
class TownFacilityAnchor:
    id: str
    shopping_population: Optional[EvidenceValue] = None
    observed_population_range: Optional[EvidenceValue] = None
    construction_delay_is_nonzero: Optional[EvidenceValue] = None
