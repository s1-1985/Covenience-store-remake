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


class PromotionPaymentTiming(str, Enum):
    TRIGGER_EVENT = "trigger_event"


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
    placement: Optional[EvidenceValue] = None
    """Where the fixture may be sited: indoor / outdoor / indoor_outdoor."""


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
class CustomerVisitProfile:
    """One time-slot row from the strategy guide's per-archetype visit table.

    The guide's "顧客データ" table gives each customer archetype multiple
    rows, one per observed visit-start time, each with its own budget and
    wanted products (both vary by time of day). This is intentionally a
    separate, finer-grained table from `CustomerArchetypeDefinition`
    (a single coarse profile per archetype) rather than an attempt to force
    this richer per-visit data into that coarser shape.

    The guide's own numbered legend (items 7-17 on the same page) defines 10
    per-row tuning stats, in this printed order:
    ス スタミナ (stamina; endurance for things like checkout queueing)
    素 素早さ (quickness; speed picking products)
    マ マナー (manner; propensity to shoplift / leave comments)
    集 集中力 (focus; resistance to buying anything besides the wanted item)
    買 買物重要度 (how important shopping is to this customer)
    価 価格重視度 (price sensitivity)
    距 距離重視度 (sensitivity to store distance)
    サ サービス重視度 (service sensitivity)
    平 平日来店割合 (weekday visit-rate share)
    休 休日来店割合 (holiday visit-rate share)
    On a second, dedicated re-read attempt, the *labels* above are now
    confirmed with high confidence (large, clearly legible legend text), but
    the *digit count actually printed per data row* still was not: re-parsing
    the same archetype's adjacent rows independently produced different
    counts (9 vs. 11) at the scan resolution available, which is the same
    kind of inconsistency that blocked a confident per-row decomposition the
    first time. Decomposing into 10 named fields would therefore still risk
    misaligning values across rows. `behavior_stats_raw` keeps the printed
    digits as one raw tuple in left-to-right reading order instead; see the
    crosscheck research note for detail.
    """

    archetype_id: str
    visit_start_time: EvidenceValue
    """Printed clock time the visit window starts, e.g. "6:00"."""
    visit_duration_minutes: EvidenceValue
    arrival_method: EvidenceValue
    """徒歩(on foot) / 自転車(bicycle) / バイク(motorbike) / 自動車(car)."""
    behavior_stats_raw: EvidenceValue
    """Raw tuple of the row's ス/素/マ/集/買/価/距/サ/平/休-ish digits, in
    printed left-to-right order; see class docstring."""
    budget_yen: EvidenceValue
    primary_wanted_product: EvidenceValue
    secondary_wanted_products: EvidenceValue
    """Tuple of up to 3 product-category ids the customer also wants."""


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
    service_skill_growth_ceiling: Optional[EvidenceValue] = None
    register_skill_growth_ceiling: Optional[EvidenceValue] = None
    cleaning_skill_growth_ceiling: Optional[EvidenceValue] = None
    replenishment_skill_growth_ceiling: Optional[EvidenceValue] = None
    security_skill_growth_ceiling: Optional[EvidenceValue] = None
    """The guide's "能力の分岐ポイント" value per skill: the point at which
    that skill's growth rate slows. Independent of the matching *_skill
    (initial) field; a candidate can have a known growth ceiling even when
    their initial value for a different skill is unconfirmed."""


@dataclass(frozen=True)
class PromotionDefinition:
    id: str
    cost_yen: EvidenceValue
    popularity_gain: EvidenceValue
    trigger_day: EvidenceValue
    trigger_hour: EvidenceValue
    payment_timing: Optional[EvidenceValue] = None


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
class TownBuildingProfile:
    """One general town-building type's size/price/customer-demand profile.

    Distinct from `TownFacilityAnchor`, which models the smaller set of
    facilities the player can *induce* (with an inducement aid amount).
    This models the strategy guide's broader "建物" table: any building
    that can appear on the town map, what products its customers tend to
    want, and whether it generates customers only in the day or around the
    clock.
    """

    id: str
    display_name_ja: str
    footprint: EvidenceValue
    building_attribute: EvidenceValue
    """役場/学校/アミューズメント/店/住宅/駅/会社/その他施設, as printed."""
    building_price_yen: EvidenceValue
    wanted_products: EvidenceValue
    """Tuple of product-category ids this building's customers tend to want,
    in the guide's own printed order."""
    active_overnight: EvidenceValue
    """Whether the guide lists this building under 深夜から早朝にも客のいる
    建物 (customers appear even 24:00-6:00) rather than only daytime."""


@dataclass(frozen=True)
class TownFacilityAnchor:
    id: str
    shopping_population: Optional[EvidenceValue] = None
    observed_population_range: Optional[EvidenceValue] = None
    construction_delay_is_nonzero: Optional[EvidenceValue] = None
    inducement_aid_yen: Optional[EvidenceValue] = None
    footprint: Optional[EvidenceValue] = None
    """Facility footprint in map tiles, e.g. (2, 2)."""


@dataclass(frozen=True)
class ProductCategoryPricing:
    """Category-level standard price / cost-rate / margin-rate master row.

    This is distinct from `ProductDefinition`, which models one specific
    product SKU. The strategy guide only publishes category-level pricing,
    not per-SKU prices, so this class exists to hold that coarser table
    without inventing individual product rows.
    """

    id: str
    display_name_ja: str
    standard_retail_price_yen: EvidenceValue
    cost_rate_pct: EvidenceValue
    margin_rate_pct: EvidenceValue
    seasonal_demand: Optional[EvidenceValue] = None
    """"summer" / "winter" if the guide flags this category as seasonal,
    else None (year-round, per the guide's own "なし" (none) marking)."""
    restock_quantity: Optional[EvidenceValue] = None
    """Units replenished per restock action ("1回補給"), from the guide's
    DATA LIST product table. The same table's other two trailing numeric
    columns remain unmapped; see decision 0080."""

    def __post_init__(self) -> None:
        cost = self.cost_rate_pct.value
        margin = self.margin_rate_pct.value
        if cost + margin != 100:
            raise ValueError(
                f"{self.id}: cost_rate_pct + margin_rate_pct must equal 100, "
                f"got {cost} + {margin}"
            )

    @property
    def procurement_cost_yen(self) -> Optional[int]:
        """Derived as base_price * cost_rate / 100; rounding rule is unconfirmed."""
        price = self.standard_retail_price_yen.value
        rate = self.cost_rate_pct.value
        if price is None or rate is None:
            return None
        return price * rate // 100


@dataclass(frozen=True)
class SalaryTableEntry:
    """One age -> base hourly wage anchor point from the strategy guide's staff table.

    The guide prints this table under the heading "年齢別・社員の基本時給(円)"
    (age-based base hourly wage) and states the generating formula elsewhere
    as hourly_wage_yen = age_years * 10 + 100; both agree with every sampled
    point here.
    """

    age_years: int
    hourly_wage_yen: EvidenceValue
