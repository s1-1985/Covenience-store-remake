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
    # Task #57: 建物面積 breakdown from the guide's own 店舗データ table
    # (book pages 106-109), distinct from editable_floor (店舗内, the
    # in-store placement grid used by store_grid.py). Reference-only for
    # now, like several other fields on this dataclass -- nothing in
    # reference_sim or game/ consumes a store's total footprint/whole-
    # building/floor/exterior area yet.
    total_area_tiles: Optional[EvidenceValue] = None
    whole_building_area_tiles: Optional[EvidenceValue] = None
    floor_area_tiles: Optional[EvidenceValue] = None
    exterior_space_tiles: Optional[EvidenceValue] = None


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
    A first re-read attempt confirmed the labels above with high confidence
    but could not reliably resolve the *digit count actually printed per
    data row* at the scan resolution then available (9 vs. 11 digits on
    independent re-parses of the same row). A subsequently supplied
    higher-resolution scan of the same pages renders the header and every
    data row unambiguously, with exactly 10 digits per row in every case;
    `behavior_stats_raw` now holds those 10 values in the printed
    left-to-right order documented above. It remains a single raw tuple
    (rather than 10 separate named fields) purely to avoid a larger,
    separately-reviewable schema change; the mapping is no longer uncertain.
    One row (`boy_elementary_student`'s 15:00 visit) prints "700" in the 平
    position where every other row is <=100; this is preserved verbatim as
    an apparent source misprint rather than silently corrected -- see
    docs/research/strategy-guide-fixture-crosscheck-2026-09-16.md.
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
    profit_per_unit_yen: Optional[EvidenceValue] = None
    """The guide's own "1個の利益" (profit per unit) column from the DATA
    LIST product table (book page 85): standard_retail_price_yen minus the
    per-unit procurement cost, i.e. price * margin_rate / 100. This field
    was previously named `restock_quantity` and documented as the table's
    "1回補給" column; a higher-resolution re-read of the same page found no
    "1回補給" column at all -- the guide's actual column order there is
    定価(price) / 原価率(cost rate) / 1個の利益(profit per unit) / 季節
    (season) / 商品棚(compatible fixtures) / 最大維持費(max maintenance) /
    最大収容力(max capacity) / 需要数例(demand example). Every value under
    the old name matched this column (not a restock quantity) exactly, so
    the field was renamed rather than kept under its previous, incorrect
    label; there is still no confirmed "units per restock action" figure
    anywhere in the guide.
    """
    max_maintenance_yen_per_day: Optional[EvidenceValue] = None
    """The DATA LIST product table's "最大維持費" column: the highest daily
    maintenance cost among the fixtures this category can be displayed on
    (see `compatible_fixtures_text`), not a per-category running cost of
    its own."""
    max_capacity: Optional[EvidenceValue] = None
    """The same table's "最大収容力" column: the highest stock capacity
    among the fixtures this category can be displayed on."""
    demand_example_count: Optional[EvidenceValue] = None
    """The same table's "需要数例" column. The guide's own caption
    explicitly warns this is worked example under one specific unstated set
    of conditions ("いろいろな条件が重なるため、実際にはこうなるわけではない。
    あくまでも一例" -- many conditions overlap, so it will not actually turn
    out this way; just one example), not a demand formula or coefficient.
    None for "cash", where the guide prints "?" instead of a number."""
    compatible_fixtures_text: Optional[EvidenceValue] = None
    """The same table's "商品棚" column, verbatim: the fixture group names
    (as printed, comma-separated) this category can be displayed on. Kept
    as raw text rather than resolved to `FixtureDefinition` ids, consistent
    with this file's policy of not inventing mappings; cross-reference
    against `FixtureDefinition.compatible_product_categories` (transcribed
    separately, from each fixture's own "取扱商品" column) rather than
    relying on either table alone."""

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


@dataclass(frozen=True)
class TradeAreaRadiusEntry:
    """One arrival-method -> trade-area radius anchor from the strategy guide.

    The guide prints this under "お客の来店手段で、範囲が変わる" / "来店手段/
    エリア半径" (book page 31): a customer's arrival method changes the
    radius of the circle, centered on the store, within which the guide's
    own diagram shows population being drawn as potential customers. This
    is the guide's own answer to what earlier research
    (docs/research/strategy-guide-full-decode-2026-09-16.md section 19.1)
    listed as an unconfirmed "商圏半径の内部計算式" (trade-area radius
    formula) -- at least the per-arrival-method radius anchors are directly
    printed, though the guide does not state the tile/distance unit, nor
    whether overlap with a rival's circle is resolved by simple proportional
    split, nearest-store-wins, or something else (see `arrival_method` on
    `CustomerVisitProfile` for the same four method strings used here).
    """

    arrival_method: EvidenceValue
    """徒歩(on foot) / 自転車(bicycle) / バイク(motorbike) / 自動車(car), matching
    `CustomerVisitProfile.arrival_method`'s own values."""
    radius: EvidenceValue
    """Printed as a bare number ("エリア半径"); unit not stated by the guide."""
