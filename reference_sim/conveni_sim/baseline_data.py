from __future__ import annotations

from .models import (
    EvidenceLevel,
    EvidenceValue,
    FixtureDefinition,
    PermitDefinition,
    ProductCategoryPricing,
    PromotionDefinition,
    PromotionPaymentTiming,
    SalaryTableEntry,
    ScenarioDefinition,
    StoreVariant,
    TownFacilityAnchor,
)

WIKI = "https://wikiwiki.jp/theconveni1/"
VIDEO_PS5 = "user-provided Console Archives PS5 first-title video, fixture UI around 14-17m"
VIDEO_LONGRUN = "user-provided first-title long-run video, facility-inducement UI around 70m48s"
VIDEO_V03_SEP2 = "user-provided V03 first-title video around 33m08s-35m02s, 1Y Sep day 2"
STRATEGY_GUIDE = (
    "official strategy guide scan (本1.pdf/本2.pdf/本2-1.pdf/本2-2.pdf), "
    "see docs/research/strategy-guide-full-decode-2026-09-16.md"
)


def _sg_fixture(
    fixture_id: str,
    *,
    footprint: tuple[int, int],
    purchase_price_yen: int,
    maintenance_yen_per_day: int,
    capacity: int,
    attention: int,
    placement: str,
) -> FixtureDefinition:
    """Build one strategy-guide-sourced fixture row with uniform provenance.

    All fields on these rows come from the same explicit numeric table
    (docs/research/strategy-guide-full-decode-2026-09-16.md section 4), so a
    single helper keeps the ~26 new rows below readable instead of repeating
    four EvidenceValue(..., EvidenceLevel.CONFIRMED_OFFICIAL, STRATEGY_GUIDE)
    calls per fixture.
    """

    evidence = EvidenceLevel.CONFIRMED_OFFICIAL
    return FixtureDefinition(
        fixture_id,
        EvidenceValue(footprint, evidence, STRATEGY_GUIDE),
        EvidenceValue(maintenance_yen_per_day, evidence, STRATEGY_GUIDE),
        purchase_price_yen=EvidenceValue(purchase_price_yen, evidence, STRATEGY_GUIDE),
        capacity=EvidenceValue(capacity, evidence, STRATEGY_GUIDE),
        attention=EvidenceValue(attention, evidence, STRATEGY_GUIDE),
        placement=EvidenceValue(placement, evidence, STRATEGY_GUIDE),
    )


# New fixtures with no prior baseline_data.py entry, transcribed from the
# strategy guide's explicit price/maintenance/capacity/attention/size table
# (docs/research/strategy-guide-full-decode-2026-09-16.md section 4). These do
# not overlap the IDs above (potted_plant/bench/fountain/parking_*/copier_*/
# vending_machine), which keep their existing confirmed values untouched.
STRATEGY_GUIDE_FIXTURES: tuple[FixtureDefinition, ...] = (
    # 4.1 常温棚・常温ワゴン (ambient shelves / wagons)
    _sg_fixture("small_ambient_shelf", footprint=(1, 1), purchase_price_yen=60,
                maintenance_yen_per_day=24, capacity=40, attention=10, placement="indoor"),
    _sg_fixture("medium_ambient_shelf", footprint=(2, 1), purchase_price_yen=100,
                maintenance_yen_per_day=48, capacity=80, attention=10, placement="indoor"),
    _sg_fixture("large_ambient_shelf", footprint=(3, 1), purchase_price_yen=140,
                maintenance_yen_per_day=72, capacity=120, attention=10, placement="indoor"),
    _sg_fixture("small_ambient_wagon", footprint=(1, 1), purchase_price_yen=30,
                maintenance_yen_per_day=24, capacity=15, attention=20, placement="indoor"),
    _sg_fixture("medium_ambient_wagon", footprint=(2, 1), purchase_price_yen=50,
                maintenance_yen_per_day=48, capacity=30, attention=20, placement="indoor"),
    _sg_fixture("large_ambient_wagon", footprint=(3, 1), purchase_price_yen=70,
                maintenance_yen_per_day=72, capacity=45, attention=20, placement="indoor"),
    _sg_fixture("large_ambient_wagon_2", footprint=(2, 2), purchase_price_yen=90,
                maintenance_yen_per_day=96, capacity=60, attention=30, placement="indoor"),
    # 4.2 冷蔵・冷凍 (refrigerated / frozen)
    _sg_fixture("small_refrigerated_shelf", footprint=(1, 1), purchase_price_yen=200,
                maintenance_yen_per_day=720, capacity=30, attention=10, placement="indoor"),
    _sg_fixture("medium_refrigerated_shelf", footprint=(1, 1), purchase_price_yen=350,
                maintenance_yen_per_day=1_200, capacity=60, attention=10, placement="indoor"),
    _sg_fixture("large_refrigerated_shelf", footprint=(3, 1), purchase_price_yen=500,
                maintenance_yen_per_day=1_920, capacity=90, attention=10, placement="indoor"),
    _sg_fixture("small_refrigerated_wagon", footprint=(1, 1), purchase_price_yen=120,
                maintenance_yen_per_day=960, capacity=10, attention=20, placement="indoor"),
    _sg_fixture("medium_refrigerated_wagon", footprint=(2, 1), purchase_price_yen=200,
                maintenance_yen_per_day=1_680, capacity=20, attention=20, placement="indoor"),
    _sg_fixture("large_refrigerated_wagon_1", footprint=(3, 1), purchase_price_yen=280,
                maintenance_yen_per_day=2_400, capacity=30, attention=20, placement="indoor"),
    _sg_fixture("large_refrigerated_wagon_2", footprint=(2, 2), purchase_price_yen=360,
                maintenance_yen_per_day=3_120, capacity=40, attention=30, placement="indoor"),
    _sg_fixture("small_frozen_shelf", footprint=(1, 1), purchase_price_yen=300,
                maintenance_yen_per_day=2_160, capacity=25, attention=10, placement="indoor"),
    _sg_fixture("medium_frozen_shelf", footprint=(2, 1), purchase_price_yen=500,
                maintenance_yen_per_day=3_600, capacity=50, attention=10, placement="indoor"),
    _sg_fixture("small_frozen_wagon", footprint=(1, 1), purchase_price_yen=200,
                maintenance_yen_per_day=1_920, capacity=10, attention=20, placement="indoor"),
    _sg_fixture("medium_frozen_wagon", footprint=(2, 1), purchase_price_yen=380,
                maintenance_yen_per_day=3_120, capacity=20, attention=20, placement="indoor"),
    # 4.3 専用ケース・イベント設備 (dedicated cases / event fixtures)
    _sg_fixture("hot_drink_case", footprint=(1, 1), purchase_price_yen=300,
                maintenance_yen_per_day=1_680, capacity=20, attention=20, placement="indoor"),
    _sg_fixture("oden_case", footprint=(1, 1), purchase_price_yen=100,
                maintenance_yen_per_day=1_920, capacity=10, attention=30, placement="indoor"),
    _sg_fixture("steamed_bun_case", footprint=(1, 1), purchase_price_yen=300,
                maintenance_yen_per_day=1_920, capacity=20, attention=30, placement="indoor"),
    _sg_fixture("event_shelf", footprint=(2, 1), purchase_price_yen=600,
                maintenance_yen_per_day=1_920, capacity=60, attention=40, placement="indoor"),
    _sg_fixture("event_wagon", footprint=(2, 1), purchase_price_yen=300,
                maintenance_yen_per_day=1_200, capacity=30, attention=60, placement="indoor"),
    # 4.4 自販機・レジ (vending machines / registers; copier_a/copier_b above
    # already correspond to the small/medium copier rows in this section)
    _sg_fixture("small_tobacco_vending", footprint=(1, 1), purchase_price_yen=600,
                maintenance_yen_per_day=240, capacity=20, attention=15, placement="indoor_outdoor"),
    _sg_fixture("large_tobacco_vending", footprint=(2, 1), purchase_price_yen=1_000,
                maintenance_yen_per_day=480, capacity=40, attention=20, placement="indoor_outdoor"),
    _sg_fixture("small_cold_drink_vending", footprint=(1, 1), purchase_price_yen=800,
                maintenance_yen_per_day=480, capacity=20, attention=15, placement="indoor_outdoor"),
    _sg_fixture("large_cold_drink_vending", footprint=(2, 1), purchase_price_yen=1_400,
                maintenance_yen_per_day=960, capacity=40, attention=20, placement="indoor_outdoor"),
    _sg_fixture("small_hot_cold_drink_vending", footprint=(1, 1), purchase_price_yen=1_000,
                maintenance_yen_per_day=960, capacity=15, attention=15, placement="indoor_outdoor"),
    _sg_fixture("large_hot_cold_drink_vending", footprint=(2, 1), purchase_price_yen=1_800,
                maintenance_yen_per_day=1_920, capacity=30, attention=20, placement="indoor_outdoor"),
    _sg_fixture("register_1", footprint=(2, 1), purchase_price_yen=2_000,
                maintenance_yen_per_day=1_440, capacity=0, attention=15, placement="indoor"),
    _sg_fixture("register_2", footprint=(2, 1), purchase_price_yen=3_000,
                maintenance_yen_per_day=1_680, capacity=60, attention=25, placement="indoor"),
    _sg_fixture("register_3", footprint=(3, 1), purchase_price_yen=3_000,
                maintenance_yen_per_day=1_680, capacity=0, attention=20, placement="indoor"),
    _sg_fixture("register_4", footprint=(3, 1), purchase_price_yen=5_000,
                maintenance_yen_per_day=1_920, capacity=90, attention=30, placement="indoor"),
    # 4.5 サービス・外構: only rows with no prior baseline_data.py entry.
    # potted_plant/bench/fountain/parking_* above already exist and were
    # cross-checked in place instead of being duplicated here. The
    # "UNCERTAIN_NAME" dispenser row from the guide is not transcribed
    # because its name could not be read from the scan.
    _sg_fixture("indoor_dispenser", footprint=(1, 1), purchase_price_yen=4_000,
                maintenance_yen_per_day=1_440, capacity=50, attention=20, placement="indoor"),
    _sg_fixture("break_room_1", footprint=(2, 2), purchase_price_yen=3_000,
                maintenance_yen_per_day=1_200, capacity=0, attention=0, placement="indoor_outdoor"),
    _sg_fixture("break_room_2", footprint=(2, 2), purchase_price_yen=7_000,
                maintenance_yen_per_day=2_400, capacity=0, attention=0, placement="indoor_outdoor"),
)

STORE_VARIANTS = (
    StoreVariant(
        id="small_top",
        size_tier="small",
        orientation=None,
        construction_price_yen=EvidenceValue(
            6_000_000,
            EvidenceLevel.CONFIRMED_VISUAL,
            "PS store-selection screenshot",
            "Exact top/bottom orientation mapping is still unknown.",
        ),
        editable_floor=EvidenceValue(
            (8, 13),
            EvidenceLevel.CONFIRMED_VISUAL,
            "PS small-store visual reconstruction",
        ),
        unlocked_at_beginner_start=EvidenceValue(
            True,
            EvidenceLevel.CONFIRMED_VISUAL,
            "PS store-selection screenshot",
        ),
    ),
    StoreVariant(
        id="small_bottom",
        size_tier="small",
        orientation=None,
        construction_price_yen=None,
        editable_floor=None,
        unlocked_at_beginner_start=EvidenceValue(
            True,
            EvidenceLevel.CONFIRMED_VISUAL,
            "PS store-selection screenshot",
        ),
    ),
    StoreVariant(
        id="medium_top",
        size_tier="medium",
        orientation=None,
        construction_price_yen=None,
        editable_floor=None,
        unlocked_at_beginner_start=EvidenceValue(
            False,
            EvidenceLevel.CONFIRMED_VISUAL,
            "PS store-selection screenshot",
        ),
    ),
    StoreVariant(
        id="medium_bottom",
        size_tier="medium",
        orientation=None,
        construction_price_yen=None,
        editable_floor=None,
        unlocked_at_beginner_start=EvidenceValue(
            False,
            EvidenceLevel.CONFIRMED_VISUAL,
            "PS store-selection screenshot",
        ),
    ),
    StoreVariant(
        id="large_top",
        size_tier="large",
        orientation=None,
        construction_price_yen=None,
        editable_floor=EvidenceValue(
            (13, 14),
            EvidenceLevel.CONFIRMED_COMMUNITY,
            WIKI + "%E5%86%85%E8%A3%85",
            "Large-store 13x14 case; exact variant/orientation mapping remains unresolved.",
        ),
        unlocked_at_beginner_start=EvidenceValue(
            False,
            EvidenceLevel.CONFIRMED_VISUAL,
            "PS store-selection screenshot",
        ),
    ),
    StoreVariant(
        id="large_bottom",
        size_tier="large",
        orientation=None,
        construction_price_yen=None,
        editable_floor=None,
        unlocked_at_beginner_start=EvidenceValue(
            False,
            EvidenceLevel.CONFIRMED_VISUAL,
            "PS store-selection screenshot",
        ),
    ),
)

FIXTURES = (
    FixtureDefinition(
        "potted_plant",
        EvidenceValue((1, 1), EvidenceLevel.CONFIRMED_COMMUNITY, WIKI + "%E5%86%85%E8%A3%85"),
        EvidenceValue(120, EvidenceLevel.CONFIRMED_COMMUNITY, WIKI + "%E5%86%85%E8%A3%85"),
        EvidenceValue(2, EvidenceLevel.CONFIRMED_COMMUNITY, WIKI + "%E5%86%85%E8%A3%85"),
        # Strategy guide confirms the same 1x1 footprint and 120 yen/day
        # maintenance independently; only purchase_price_yen was previously
        # unknown and is added here without touching the confirmed values.
        purchase_price_yen=EvidenceValue(1_000, EvidenceLevel.CONFIRMED_OFFICIAL, STRATEGY_GUIDE),
        placement=EvidenceValue("indoor_outdoor", EvidenceLevel.CONFIRMED_OFFICIAL, STRATEGY_GUIDE),
    ),
    FixtureDefinition(
        "bench",
        EvidenceValue((1, 1), EvidenceLevel.CONFIRMED_COMMUNITY, WIKI + "%E5%86%85%E8%A3%85"),
        # NOTE: strategy guide reports 160 yen/day maintenance for the bench,
        # not 168. This is a direct numeric conflict between two sources; see
        # docs/research/strategy-guide-fixture-crosscheck-2026-09-16.md.
        # The wiki-derived 168 value is kept as-is rather than silently
        # overwritten.
        EvidenceValue(168, EvidenceLevel.CONFIRMED_COMMUNITY, WIKI + "%E5%86%85%E8%A3%85"),
        EvidenceValue(3, EvidenceLevel.CONFIRMED_COMMUNITY, WIKI + "%E5%86%85%E8%A3%85"),
        purchase_price_yen=EvidenceValue(2_000, EvidenceLevel.CONFIRMED_OFFICIAL, STRATEGY_GUIDE),
        placement=EvidenceValue("indoor_outdoor", EvidenceLevel.CONFIRMED_OFFICIAL, STRATEGY_GUIDE),
    ),
    FixtureDefinition(
        "fountain",
        EvidenceValue((2, 2), EvidenceLevel.CONFIRMED_COMMUNITY, WIKI + "%E5%86%85%E8%A3%85"),
        EvidenceValue(2_400, EvidenceLevel.CONFIRMED_COMMUNITY, WIKI + "%E5%86%85%E8%A3%85"),
        EvidenceValue(25, EvidenceLevel.CONFIRMED_COMMUNITY, WIKI + "%E5%86%85%E8%A3%85"),
        # Strategy guide confirms the same 2400 yen/day maintenance.
        purchase_price_yen=EvidenceValue(5_000, EvidenceLevel.CONFIRMED_OFFICIAL, STRATEGY_GUIDE),
        placement=EvidenceValue("indoor_outdoor", EvidenceLevel.CONFIRMED_OFFICIAL, STRATEGY_GUIDE),
    ),
    FixtureDefinition(
        "parking_ground",
        EvidenceValue((1, 2), EvidenceLevel.CONFIRMED_COMMUNITY, WIKI + "%E5%86%85%E8%A3%85"),
        EvidenceValue(0, EvidenceLevel.CONFIRMED_COMMUNITY, WIKI + "%E5%86%85%E8%A3%85"),
        parking_capacity=EvidenceValue(2, EvidenceLevel.CONFIRMED_COMMUNITY, WIKI + "%E5%86%85%E8%A3%85"),
        blocks_pedestrian=EvidenceValue(True, EvidenceLevel.CONFIRMED_COMMUNITY, WIKI + "%E5%86%85%E8%A3%85", "Parking cells are reported as non-walkable."),
        # Strategy guide confirms the same 0 yen/day maintenance and capacity 2.
        purchase_price_yen=EvidenceValue(500, EvidenceLevel.CONFIRMED_OFFICIAL, STRATEGY_GUIDE),
        placement=EvidenceValue("outdoor", EvidenceLevel.CONFIRMED_OFFICIAL, STRATEGY_GUIDE),
    ),
    FixtureDefinition(
        "parking_two_story",
        EvidenceValue((1, 2), EvidenceLevel.CONFIRMED_COMMUNITY, WIKI + "%E5%86%85%E8%A3%85"),
        EvidenceValue(240, EvidenceLevel.CONFIRMED_COMMUNITY, WIKI + "%E5%86%85%E8%A3%85"),
        parking_capacity=EvidenceValue(4, EvidenceLevel.CONFIRMED_COMMUNITY, WIKI + "%E5%86%85%E8%A3%85"),
        blocks_pedestrian=EvidenceValue(True, EvidenceLevel.CONFIRMED_COMMUNITY, WIKI + "%E5%86%85%E8%A3%85", "Parking cells are reported as non-walkable."),
        # Strategy guide confirms the same 240 yen/day maintenance and capacity 4.
        purchase_price_yen=EvidenceValue(1_000, EvidenceLevel.CONFIRMED_OFFICIAL, STRATEGY_GUIDE),
        placement=EvidenceValue("outdoor", EvidenceLevel.CONFIRMED_OFFICIAL, STRATEGY_GUIDE),
    ),
    FixtureDefinition(
        "parking_tower",
        EvidenceValue((2, 3), EvidenceLevel.CONFIRMED_COMMUNITY, WIKI + "%E5%86%85%E8%A3%85"),
        EvidenceValue(4_800, EvidenceLevel.CONFIRMED_COMMUNITY, WIKI + "%E5%86%85%E8%A3%85"),
        parking_capacity=EvidenceValue(20, EvidenceLevel.CONFIRMED_COMMUNITY, WIKI + "%E5%86%85%E8%A3%85"),
        blocks_pedestrian=EvidenceValue(True, EvidenceLevel.CONFIRMED_COMMUNITY, WIKI + "%E5%86%85%E8%A3%85", "Parking cells are reported as non-walkable."),
        # Strategy guide confirms the same 4800 yen/day maintenance and capacity 20.
        purchase_price_yen=EvidenceValue(9_000, EvidenceLevel.CONFIRMED_OFFICIAL, STRATEGY_GUIDE),
        placement=EvidenceValue("outdoor", EvidenceLevel.CONFIRMED_OFFICIAL, STRATEGY_GUIDE),
    ),
    FixtureDefinition(
        "copier_a",
        # Strategy guide's 小型コピー機 (small copier) row matches this
        # record's price/maintenance/capacity/attention exactly, which
        # independently confirms copier_a is the small copier and lets the
        # previously-unknown footprint/placement be filled in.
        footprint=EvidenceValue((1, 1), EvidenceLevel.CONFIRMED_OFFICIAL, STRATEGY_GUIDE),
        maintenance_yen_per_day=EvidenceValue(1_200, EvidenceLevel.CONFIRMED_VISUAL, VIDEO_PS5),
        purchase_price_yen=EvidenceValue(1_500, EvidenceLevel.CONFIRMED_VISUAL, VIDEO_PS5),
        capacity=EvidenceValue(20, EvidenceLevel.CONFIRMED_VISUAL, VIDEO_PS5),
        attention=EvidenceValue(10, EvidenceLevel.CONFIRMED_VISUAL, VIDEO_PS5),
        placement=EvidenceValue("indoor", EvidenceLevel.CONFIRMED_OFFICIAL, STRATEGY_GUIDE),
    ),
    FixtureDefinition(
        "copier_b",
        # Strategy guide's 中型コピー機 (medium copier) row matches this
        # record's price/maintenance/capacity/attention exactly; same
        # cross-corroboration as copier_a above.
        footprint=EvidenceValue((2, 1), EvidenceLevel.CONFIRMED_OFFICIAL, STRATEGY_GUIDE),
        maintenance_yen_per_day=EvidenceValue(1_440, EvidenceLevel.CONFIRMED_VISUAL, VIDEO_PS5),
        purchase_price_yen=EvidenceValue(2_000, EvidenceLevel.CONFIRMED_VISUAL, VIDEO_PS5),
        capacity=EvidenceValue(40, EvidenceLevel.CONFIRMED_VISUAL, VIDEO_PS5),
        attention=EvidenceValue(15, EvidenceLevel.CONFIRMED_VISUAL, VIDEO_PS5),
        placement=EvidenceValue("indoor", EvidenceLevel.CONFIRMED_OFFICIAL, STRATEGY_GUIDE),
    ),
    FixtureDefinition(
        "vending_machine",
        footprint=None,
        sale_mode="self_service_candidate",
    ),
) + STRATEGY_GUIDE_FIXTURES

PROMOTIONS = (
    PromotionDefinition(
        "direct_mail",
        EvidenceValue(100_000, EvidenceLevel.CONFIRMED_VISUAL, VIDEO_V03_SEP2),
        EvidenceValue(12, EvidenceLevel.CONFIRMED_VISUAL, VIDEO_V03_SEP2),
        EvidenceValue(2, EvidenceLevel.CONFIRMED_VISUAL, VIDEO_V03_SEP2),
        EvidenceValue(10, EvidenceLevel.CONFIRMED_VISUAL, VIDEO_V03_SEP2),
        EvidenceValue(
            PromotionPaymentTiming.TRIGGER_EVENT,
            EvidenceLevel.CONFIRMED_VISUAL,
            VIDEO_V03_SEP2,
            "Cash falls by exactly 100,000 yen as the day-2 10:00 event fires.",
        ),
    ),
    PromotionDefinition("newspaper", EvidenceValue(500_000, EvidenceLevel.CONFIRMED_COMMUNITY, WIKI + "%E5%AE%A3%E4%BC%9D"), EvidenceValue(20, EvidenceLevel.CONFIRMED_COMMUNITY, WIKI + "%E5%AE%A3%E4%BC%9D"), EvidenceValue(2, EvidenceLevel.CONFIRMED_COMMUNITY, WIKI + "%E5%AE%A3%E4%BC%9D"), EvidenceValue(7, EvidenceLevel.CONFIRMED_COMMUNITY, WIKI + "%E5%AE%A3%E4%BC%9D")),
    PromotionDefinition("airship", EvidenceValue(1_000_000, EvidenceLevel.CONFIRMED_COMMUNITY, WIKI + "%E5%AE%A3%E4%BC%9D"), EvidenceValue(30, EvidenceLevel.CONFIRMED_COMMUNITY, WIKI + "%E5%AE%A3%E4%BC%9D"), EvidenceValue(3, EvidenceLevel.CONFIRMED_COMMUNITY, WIKI + "%E5%AE%A3%E4%BC%9D"), EvidenceValue(15, EvidenceLevel.CONFIRMED_COMMUNITY, WIKI + "%E5%AE%A3%E4%BC%9D")),
    PromotionDefinition("radio", EvidenceValue(3_000_000, EvidenceLevel.CONFIRMED_COMMUNITY, WIKI + "%E5%AE%A3%E4%BC%9D"), EvidenceValue(50, EvidenceLevel.CONFIRMED_COMMUNITY, WIKI + "%E5%AE%A3%E4%BC%9D"), EvidenceValue(1, EvidenceLevel.CONFIRMED_COMMUNITY, WIKI + "%E5%AE%A3%E4%BC%9D"), EvidenceValue(17, EvidenceLevel.CONFIRMED_COMMUNITY, WIKI + "%E5%AE%A3%E4%BC%9D")),
    PromotionDefinition("tv", EvidenceValue(5_000_000, EvidenceLevel.CONFIRMED_COMMUNITY, WIKI + "%E5%AE%A3%E4%BC%9D"), EvidenceValue(100, EvidenceLevel.CONFIRMED_COMMUNITY, WIKI + "%E5%AE%A3%E4%BC%9D"), EvidenceValue(1, EvidenceLevel.CONFIRMED_COMMUNITY, WIKI + "%E5%AE%A3%E4%BC%9D"), EvidenceValue(19, EvidenceLevel.CONFIRMED_COMMUNITY, WIKI + "%E5%AE%A3%E4%BC%9D")),
)

PERMITS = tuple(
    PermitDefinition(
        id=permit_id,
        fee_yen=None,
        exclusion_distance_tiles=None,
        eligibility_is_independent=EvidenceValue(
            True,
            EvidenceLevel.CONFIRMED_COMMUNITY,
            "PS long-play observation: tobacco/alcohol available while medicine unavailable at the same site",
        ),
    )
    for permit_id in ("tobacco", "alcohol", "medicine")
)

SCENARIO_GUIDE = WIKI + "%E3%82%B2%E3%83%BC%E3%83%A0%E3%83%A2%E3%83%BC%E3%83%89%E6%94%BB%E7%95%A5"

SCENARIOS = (
    ScenarioDefinition(
        "beginner",
        EvidenceValue(200_000_000, EvidenceLevel.CONFIRMED_COMMUNITY, SCENARIO_GUIDE),
        EvidenceValue(
            "metropolitan_government_after_population_threshold",
            EvidenceLevel.CONFIRMED_COMMUNITY,
            SCENARIO_GUIDE,
        ),
    ),
    ScenarioDefinition(
        "intermediate",
        EvidenceValue(150_000_000, EvidenceLevel.CONFIRMED_COMMUNITY, SCENARIO_GUIDE),
        EvidenceValue(
            "10_player_stores", EvidenceLevel.CONFIRMED_COMMUNITY, SCENARIO_GUIDE
        ),
    ),
    ScenarioDefinition(
        "advanced",
        EvidenceValue(150_000_000, EvidenceLevel.CONFIRMED_COMMUNITY, SCENARIO_GUIDE),
        EvidenceValue(
            "owner_rating_5_stars", EvidenceLevel.CONFIRMED_COMMUNITY, SCENARIO_GUIDE
        ),
    ),
)

TOWN_FACILITIES = (
    TownFacilityAnchor(
        "station",
        shopping_population=EvidenceValue(2_240, EvidenceLevel.CONFIRMED_COMMUNITY, WIKI + "%E3%82%B2%E3%83%BC%E3%83%A0%E3%83%A2%E3%83%BC%E3%83%89%E6%94%BB%E7%95%A5"),
    ),
    TownFacilityAnchor(
        "police_box",
        inducement_aid_yen=EvidenceValue(400_000, EvidenceLevel.CONFIRMED_VISUAL, VIDEO_LONGRUN),
    ),
    TownFacilityAnchor(
        "company",
        inducement_aid_yen=EvidenceValue(5_400_000, EvidenceLevel.CONFIRMED_VISUAL, VIDEO_LONGRUN),
    ),
    TownFacilityAnchor(
        "pool",
        inducement_aid_yen=EvidenceValue(1_800_000, EvidenceLevel.CONFIRMED_VISUAL, VIDEO_V03_SEP2),
    ),
    TownFacilityAnchor(
        "vocational_school",
        inducement_aid_yen=EvidenceValue(4_800_000, EvidenceLevel.CONFIRMED_VISUAL, VIDEO_LONGRUN),
    ),
    TownFacilityAnchor(
        "university",
        observed_population_range=EvidenceValue(
            (500, 800),
            EvidenceLevel.PROVISIONAL,
            "PS direct-play strategy observation",
            "Observed long-play range only; not an exact fixed population value.",
        ),
        inducement_aid_yen=EvidenceValue(9_800_000, EvidenceLevel.CONFIRMED_VISUAL, VIDEO_LONGRUN),
    ),
    TownFacilityAnchor(
        "fire_station",
        construction_delay_is_nonzero=EvidenceValue(True, EvidenceLevel.PROVISIONAL, "PS long-play observation"),
    ),
)


def _sg_category(
    category_id: str,
    display_name_ja: str,
    *,
    standard_retail_price_yen: int,
    cost_rate_pct: int,
    margin_rate_pct: int,
) -> ProductCategoryPricing:
    """Build one strategy-guide product-category pricing row with uniform provenance.

    Source: docs/research/strategy-guide-full-decode-2026-09-16.md section 3.
    This is category-level standard pricing, not a per-SKU price list; no
    prior baseline_data.py table covered this, so there is nothing to
    cross-check or conflict with here.
    """

    evidence = EvidenceLevel.CONFIRMED_OFFICIAL
    return ProductCategoryPricing(
        category_id,
        display_name_ja,
        EvidenceValue(standard_retail_price_yen, evidence, STRATEGY_GUIDE),
        EvidenceValue(cost_rate_pct, evidence, STRATEGY_GUIDE),
        EvidenceValue(margin_rate_pct, evidence, STRATEGY_GUIDE),
    )


# Category-level standard price / cost-rate / margin-rate table, transcribed
# from the strategy guide (docs/research/strategy-guide-full-decode-2026-09-16.md
# section 3). `cash` (現金, the special zero-margin category used for cash-like
# instruments) is included as-is from the source table.
PRODUCT_CATEGORY_PRICING: tuple[ProductCategoryPricing, ...] = (
    _sg_category("cold_drink", "冷たい飲料", standard_retail_price_yen=110, cost_rate_pct=50, margin_rate_pct=50),
    _sg_category("hot_drink", "温かい飲料", standard_retail_price_yen=110, cost_rate_pct=50, margin_rate_pct=50),
    _sg_category("alcohol", "酒類", standard_retail_price_yen=1_000, cost_rate_pct=70, margin_rate_pct=30),
    _sg_category("bento", "弁当類", standard_retail_price_yen=400, cost_rate_pct=60, margin_rate_pct=40),
    _sg_category("bread", "パン類", standard_retail_price_yen=300, cost_rate_pct=50, margin_rate_pct=50),
    _sg_category("instant_food", "インスタント類", standard_retail_price_yen=150, cost_rate_pct=60, margin_rate_pct=40),
    _sg_category("snacks", "菓子類", standard_retail_price_yen=200, cost_rate_pct=60, margin_rate_pct=40),
    _sg_category("books", "本類", standard_retail_price_yen=400, cost_rate_pct=60, margin_rate_pct=40),
    _sg_category("tobacco", "たばこ", standard_retail_price_yen=250, cost_rate_pct=70, margin_rate_pct=30),
    _sg_category("ice_cream", "アイスクリーム", standard_retail_price_yen=100, cost_rate_pct=50, margin_rate_pct=50),
    _sg_category("stationery", "文房具", standard_retail_price_yen=150, cost_rate_pct=60, margin_rate_pct=40),
    _sg_category("retort_food", "レトルト類", standard_retail_price_yen=600, cost_rate_pct=60, margin_rate_pct=40),
    _sg_category("electronics", "電機製品類", standard_retail_price_yen=800, cost_rate_pct=60, margin_rate_pct=40),
    _sg_category("seasoning", "調味料類", standard_retail_price_yen=400, cost_rate_pct=60, margin_rate_pct=40),
    _sg_category("vegetables", "野菜類", standard_retail_price_yen=1_500, cost_rate_pct=50, margin_rate_pct=50),
    _sg_category("frozen_food", "冷凍食品類", standard_retail_price_yen=500, cost_rate_pct=60, margin_rate_pct=40),
    _sg_category("fish", "魚類", standard_retail_price_yen=1_000, cost_rate_pct=60, margin_rate_pct=40),
    _sg_category("oden", "おでん", standard_retail_price_yen=250, cost_rate_pct=50, margin_rate_pct=50),
    _sg_category("meat", "肉類", standard_retail_price_yen=1_200, cost_rate_pct=50, margin_rate_pct=50),
    _sg_category("daily_goods", "日用品", standard_retail_price_yen=800, cost_rate_pct=60, margin_rate_pct=40),
    _sg_category("copy_paper", "コピー用紙", standard_retail_price_yen=50, cost_rate_pct=60, margin_rate_pct=40),
    _sg_category("event_goods", "イベント商品", standard_retail_price_yen=1_000, cost_rate_pct=60, margin_rate_pct=40),
    _sg_category("parcel_delivery_form", "宅急便申込書", standard_retail_price_yen=1_000, cost_rate_pct=80, margin_rate_pct=20),
    _sg_category("chinese_steamed_bun", "中華まん", standard_retail_price_yen=170, cost_rate_pct=60, margin_rate_pct=40),
    _sg_category("medicine", "薬品", standard_retail_price_yen=1_500, cost_rate_pct=70, margin_rate_pct=30),
    _sg_category("underwear", "下着類", standard_retail_price_yen=1_000, cost_rate_pct=60, margin_rate_pct=40),
    _sg_category("cash", "現金", standard_retail_price_yen=0, cost_rate_pct=100, margin_rate_pct=0),
)


# Age (years) -> monthly salary (yen) anchor table from the strategy guide
# (docs/research/strategy-guide-full-decode-2026-09-16.md section 5). The
# guide's own unit label was not independently re-confirmed against in-game
# UI, so the raw value is kept as printed rather than converted.
SALARY_TABLE: tuple[SalaryTableEntry, ...] = (
    SalaryTableEntry(15, EvidenceValue(250, EvidenceLevel.CONFIRMED_OFFICIAL, STRATEGY_GUIDE)),
    SalaryTableEntry(20, EvidenceValue(300, EvidenceLevel.CONFIRMED_OFFICIAL, STRATEGY_GUIDE)),
    SalaryTableEntry(25, EvidenceValue(350, EvidenceLevel.CONFIRMED_OFFICIAL, STRATEGY_GUIDE)),
    SalaryTableEntry(30, EvidenceValue(400, EvidenceLevel.CONFIRMED_OFFICIAL, STRATEGY_GUIDE)),
    SalaryTableEntry(35, EvidenceValue(450, EvidenceLevel.CONFIRMED_OFFICIAL, STRATEGY_GUIDE)),
    SalaryTableEntry(40, EvidenceValue(500, EvidenceLevel.CONFIRMED_OFFICIAL, STRATEGY_GUIDE)),
    SalaryTableEntry(45, EvidenceValue(550, EvidenceLevel.CONFIRMED_OFFICIAL, STRATEGY_GUIDE)),
    SalaryTableEntry(50, EvidenceValue(600, EvidenceLevel.CONFIRMED_OFFICIAL, STRATEGY_GUIDE)),
    SalaryTableEntry(55, EvidenceValue(650, EvidenceLevel.CONFIRMED_OFFICIAL, STRATEGY_GUIDE)),
    SalaryTableEntry(60, EvidenceValue(700, EvidenceLevel.CONFIRMED_OFFICIAL, STRATEGY_GUIDE)),
)
