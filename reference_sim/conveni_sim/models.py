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
    purchase_price_yen: Optional[EvidenceValue] = None
    capacity: Optional[EvidenceValue] = None
    compatible_product_categories: Optional[EvidenceValue] = None
    interaction_sides: Optional[EvidenceValue] = None
    attention: Optional[EvidenceValue] = None
    security_bonus: Optional[EvidenceValue] = None


@dataclass(frozen=True)
class ProductDefinition:
    """Guide-ready product master row; unknown means None, never inferred zero."""

    id: str
    display_name: Optional[EvidenceValue] = None
    category: Optional[EvidenceValue] = None
    temperature_zone: Optional[EvidenceValue] = None
    procurement_cost_yen: Optional[EvidenceValue] = None
    standard_retail_price_yen: Optional[EvidenceValue] = None
    compatible_fixture_ids: Optional[EvidenceValue] = None
    required_permit_id: Optional[EvidenceValue] = None
    primary_purchase_eligibility: Optional[EvidenceValue] = None
    add_on_purchase_eligibility: Optional[EvidenceValue] = None
    audience_affinities: Optional[EvidenceValue] = None


@dataclass(frozen=True)
class CustomerArchetypeDefinition:
    """Customer-group data slots without inventing missing numeric behavior."""

    id: str
    display_name: Optional[EvidenceValue] = None
    visual_archetype: Optional[EvidenceValue] = None
    origin_building_affinities: Optional[EvidenceValue] = None
    spending_power_profile: Optional[EvidenceValue] = None
    preferred_primary_products: Optional[EvidenceValue] = None
    preferred_add_on_products: Optional[EvidenceValue] = None
    patience_profile: Optional[EvidenceValue] = None
    anger_profile: Optional[EvidenceValue] = None


@dataclass(frozen=True)
class StaffDefinition:
    """Guide-ready staff master row with hiring and runtime stats kept separate."""

    id: str
    display_name: Optional[EvidenceValue] = None
    starting_age_years: Optional[EvidenceValue] = None
    salary_yen_per_day_24h: Optional[EvidenceValue] = None
    stamina: Optional[EvidenceValue] = None
    academic_background: Optional[EvidenceValue] = None
    agility: Optional[EvidenceValue] = None
    sociability: Optional[EvidenceValue] = None
    education: Optional[EvidenceValue] = None
    register_skill: Optional[EvidenceValue] = None
    replenishment_skill: Optional[EvidenceValue] = None
    security_skill: Optional[EvidenceValue] = None
    cleaning_skill: Optional[EvidenceValue] = None
    service_skill: Optional[EvidenceValue] = None


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
    inducement_aid_yen: Optional[EvidenceValue] = None
