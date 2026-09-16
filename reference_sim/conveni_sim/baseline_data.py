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
        # Strategy guide's store-selection screen and its 店舗1/店舗2 data
        # rows both show 6,000,000 yen for every "small" variant regardless
        # of orientation, so this previously-unknown price can be filled in
        # without touching small_top's separately-sourced editable_floor.
        construction_price_yen=EvidenceValue(6_000_000, EvidenceLevel.CONFIRMED_OFFICIAL, STRATEGY_GUIDE),
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
        construction_price_yen=EvidenceValue(12_000_000, EvidenceLevel.CONFIRMED_OFFICIAL, STRATEGY_GUIDE),
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
        construction_price_yen=EvidenceValue(12_000_000, EvidenceLevel.CONFIRMED_OFFICIAL, STRATEGY_GUIDE),
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
        # NOTE: the guide's own store-selection screen (chapter 1) prints
        # 24,000,000 yen for this tier, but its data-table page and all six
        # of its "大" (large) case-study layouts independently agree on
        # 18,000,000 yen (7 sources vs. 1). This is an internal conflict in
        # the source material itself, not a cross-source one; 18,000,000 is
        # used as the majority value. See
        # docs/research/strategy-guide-fixture-crosscheck-2026-09-16.md.
        construction_price_yen=EvidenceValue(18_000_000, EvidenceLevel.CONFIRMED_OFFICIAL, STRATEGY_GUIDE),
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
        construction_price_yen=EvidenceValue(18_000_000, EvidenceLevel.CONFIRMED_OFFICIAL, STRATEGY_GUIDE),
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
        # Strategy guide independently confirms this +2 service_bonus
        # ("店舗のサービス値が2上昇する"), matching the existing wiki value exactly.
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
        # NOTE: strategy guide reports a +4 service_bonus ("サービス値が4上昇する"),
        # not +3. Same conflict pattern as the maintenance figure above; the
        # wiki-derived 3 is kept, not silently overwritten. See the
        # crosscheck research note.
        EvidenceValue(3, EvidenceLevel.CONFIRMED_COMMUNITY, WIKI + "%E5%86%85%E8%A3%85"),
        purchase_price_yen=EvidenceValue(2_000, EvidenceLevel.CONFIRMED_OFFICIAL, STRATEGY_GUIDE),
        placement=EvidenceValue("indoor_outdoor", EvidenceLevel.CONFIRMED_OFFICIAL, STRATEGY_GUIDE),
    ),
    FixtureDefinition(
        "fountain",
        EvidenceValue((2, 2), EvidenceLevel.CONFIRMED_COMMUNITY, WIKI + "%E5%86%85%E8%A3%85"),
        EvidenceValue(2_400, EvidenceLevel.CONFIRMED_COMMUNITY, WIKI + "%E5%86%85%E8%A3%85"),
        # NOTE: strategy guide reports a +30 service_bonus ("サービス値が30上昇する"),
        # not +25. Same conflict pattern as bench above; the wiki-derived 25
        # is kept, not silently overwritten. See the crosscheck research note.
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
    # airship/radio/tv popularity_gain corrected from the WIKI-derived
    # +30/+50/+100 to the strategy guide's +40/+60/+90: cost/trigger_day/
    # trigger_hour already matched the guide exactly, and the guide's own
    # popularity_gain value was independently confirmed on four separate
    # primary-source pages (docs/research/strategy-guide-full-decode-2026-09-16.md
    # and the original scans), making it the stronger source for this one
    # field. See docs/research/strategy-guide-fixture-crosscheck-2026-09-16.md.
    PromotionDefinition("airship", EvidenceValue(1_000_000, EvidenceLevel.CONFIRMED_COMMUNITY, WIKI + "%E5%AE%A3%E4%BC%9D"), EvidenceValue(40, EvidenceLevel.CONFIRMED_OFFICIAL, STRATEGY_GUIDE), EvidenceValue(3, EvidenceLevel.CONFIRMED_COMMUNITY, WIKI + "%E5%AE%A3%E4%BC%9D"), EvidenceValue(15, EvidenceLevel.CONFIRMED_COMMUNITY, WIKI + "%E5%AE%A3%E4%BC%9D")),
    PromotionDefinition("radio", EvidenceValue(3_000_000, EvidenceLevel.CONFIRMED_COMMUNITY, WIKI + "%E5%AE%A3%E4%BC%9D"), EvidenceValue(60, EvidenceLevel.CONFIRMED_OFFICIAL, STRATEGY_GUIDE), EvidenceValue(1, EvidenceLevel.CONFIRMED_COMMUNITY, WIKI + "%E5%AE%A3%E4%BC%9D"), EvidenceValue(17, EvidenceLevel.CONFIRMED_COMMUNITY, WIKI + "%E5%AE%A3%E4%BC%9D")),
    PromotionDefinition("tv", EvidenceValue(5_000_000, EvidenceLevel.CONFIRMED_COMMUNITY, WIKI + "%E5%AE%A3%E4%BC%9D"), EvidenceValue(90, EvidenceLevel.CONFIRMED_OFFICIAL, STRATEGY_GUIDE), EvidenceValue(1, EvidenceLevel.CONFIRMED_COMMUNITY, WIKI + "%E5%AE%A3%E4%BC%9D"), EvidenceValue(19, EvidenceLevel.CONFIRMED_COMMUNITY, WIKI + "%E5%AE%A3%E4%BC%9D")),
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


def _sg_facility(
    facility_id: str,
    *,
    footprint: tuple[int, int],
    inducement_aid_yen: int,
    shopping_population: Optional[int] = None,
) -> TownFacilityAnchor:
    """Build one new strategy-guide-sourced inducement facility.

    Source: docs/research/strategy-guide-full-decode-2026-09-16.md section 9
    and the primary guide scans (inducement facility list, and the separate
    per-facility customer-count table). All 6 pre-existing facilities this
    file already carried (police_box/company/pool/vocational_school/
    university/station) were independently cross-checked against the same
    guide tables and matched exactly, which is why this new batch is trusted
    at CONFIRMED_OFFICIAL rather than left as a lower evidence tier.
    """

    evidence = EvidenceLevel.CONFIRMED_OFFICIAL
    return TownFacilityAnchor(
        facility_id,
        shopping_population=(
            EvidenceValue(shopping_population, evidence, STRATEGY_GUIDE)
            if shopping_population is not None
            else None
        ),
        inducement_aid_yen=EvidenceValue(inducement_aid_yen, evidence, STRATEGY_GUIDE),
        footprint=EvidenceValue(footprint, evidence, STRATEGY_GUIDE),
    )


TOWN_FACILITIES = (
    TownFacilityAnchor(
        "station",
        shopping_population=EvidenceValue(2_240, EvidenceLevel.CONFIRMED_COMMUNITY, WIKI + "%E3%82%B2%E3%83%BC%E3%83%A0%E3%83%A2%E3%83%BC%E3%83%89%E6%94%BB%E7%95%A5"),
    ),
    TownFacilityAnchor(
        "police_box",
        inducement_aid_yen=EvidenceValue(400_000, EvidenceLevel.CONFIRMED_VISUAL, VIDEO_LONGRUN),
        # Strategy guide independently confirms the same 400,000 yen aid and
        # adds the previously-unknown 2x2 footprint.
        footprint=EvidenceValue((2, 2), EvidenceLevel.CONFIRMED_OFFICIAL, STRATEGY_GUIDE),
    ),
    TownFacilityAnchor(
        "company",
        inducement_aid_yen=EvidenceValue(5_400_000, EvidenceLevel.CONFIRMED_VISUAL, VIDEO_LONGRUN),
        # Strategy guide independently confirms the same 5,400,000 yen aid.
        shopping_population=EvidenceValue(90, EvidenceLevel.CONFIRMED_OFFICIAL, STRATEGY_GUIDE),
        footprint=EvidenceValue((3, 3), EvidenceLevel.CONFIRMED_OFFICIAL, STRATEGY_GUIDE),
    ),
    TownFacilityAnchor(
        "pool",
        inducement_aid_yen=EvidenceValue(1_800_000, EvidenceLevel.CONFIRMED_VISUAL, VIDEO_V03_SEP2),
        # Strategy guide independently confirms the same 1,800,000 yen aid.
        shopping_population=EvidenceValue(40, EvidenceLevel.CONFIRMED_OFFICIAL, STRATEGY_GUIDE),
        footprint=EvidenceValue((3, 2), EvidenceLevel.CONFIRMED_OFFICIAL, STRATEGY_GUIDE),
    ),
    TownFacilityAnchor(
        "vocational_school",
        inducement_aid_yen=EvidenceValue(4_800_000, EvidenceLevel.CONFIRMED_VISUAL, VIDEO_LONGRUN),
        # Strategy guide independently confirms the same 4,800,000 yen aid.
        footprint=EvidenceValue((3, 4), EvidenceLevel.CONFIRMED_OFFICIAL, STRATEGY_GUIDE),
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
        # Strategy guide independently confirms the same 9,800,000 yen aid.
        footprint=EvidenceValue((7, 7), EvidenceLevel.CONFIRMED_OFFICIAL, STRATEGY_GUIDE),
    ),
    TownFacilityAnchor(
        "fire_station",
        construction_delay_is_nonzero=EvidenceValue(True, EvidenceLevel.PROVISIONAL, "PS long-play observation"),
        inducement_aid_yen=EvidenceValue(600_000, EvidenceLevel.CONFIRMED_OFFICIAL, STRATEGY_GUIDE),
        shopping_population=EvidenceValue(12, EvidenceLevel.CONFIRMED_OFFICIAL, STRATEGY_GUIDE),
        footprint=EvidenceValue((2, 3), EvidenceLevel.CONFIRMED_OFFICIAL, STRATEGY_GUIDE),
    ),
    # New facilities from the strategy guide's inducement list with no prior
    # entry in this file.
    _sg_facility("mansion", footprint=(2, 3), inducement_aid_yen=4_200_000),
    _sg_facility("gym", footprint=(2, 3), inducement_aid_yen=4_200_000, shopping_population=30),
    _sg_facility("athletic_field", footprint=(4, 5), inducement_aid_yen=2_000_000, shopping_population=30),
    _sg_facility("event_hall", footprint=(2, 2), inducement_aid_yen=6_000_000, shopping_population=260),
    _sg_facility("kindergarten", footprint=(2, 3), inducement_aid_yen=1_200_000),
    _sg_facility("elementary_school", footprint=(4, 4), inducement_aid_yen=3_200_000),
    _sg_facility("middle_school", footprint=(5, 5), inducement_aid_yen=5_000_000),
    _sg_facility("high_school", footprint=(6, 6), inducement_aid_yen=7_200_000),
    _sg_facility("park", footprint=(2, 2), inducement_aid_yen=2_000_000, shopping_population=24),
    _sg_facility("aquarium", footprint=(3, 3), inducement_aid_yen=2_700_000, shopping_population=60),
    _sg_facility("zoo", footprint=(6, 6), inducement_aid_yen=7_200_000, shopping_population=500),
    _sg_facility("amusement_park", footprint=(7, 7), inducement_aid_yen=9_800_000, shopping_population=750),
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


# Age (years) -> base hourly wage (yen) anchor table, transcribed directly
# from the strategy guide page headed "年齢別・社員の基本時給(円)"
# (age-based base hourly wage). A separate guide page states the generating
# formula hourly_wage_yen = age_years * 10 + 100, which reproduces every
# point below exactly; the labor-cost note on payroll confirms wages are
# computed as hourly_wage * hours_worked, not a flat monthly figure.
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
