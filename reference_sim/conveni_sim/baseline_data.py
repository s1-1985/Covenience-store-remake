from __future__ import annotations

from .models import (
    AnnualCalendarMonthEntry,
    BusinessHoursPresetEntry,
    CustomerArchetypeDefinition,
    CustomerVisitProfile,
    EvidenceLevel,
    EvidenceValue,
    FixtureDefinition,
    MonthlyWeatherPercentagesEntry,
    PermitDefinition,
    ProductCategoryPricing,
    PromotionDefinition,
    PromotionPaymentTiming,
    SalaryTableEntry,
    ScenarioDefinition,
    StaffDefinition,
    StoreVariant,
    TownBuildingProfile,
    TownFacilityAnchor,
    TradeAreaRadiusEntry,
)
from .operating_time import OperatingHours

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
    compatible_product_categories: Optional[tuple[str, ...]] = None,
) -> FixtureDefinition:
    """Build one strategy-guide-sourced fixture row with uniform provenance.

    All fields on these rows come from the same explicit numeric table
    (docs/research/strategy-guide-full-decode-2026-09-16.md section 4), so a
    single helper keeps the ~26 new rows below readable instead of repeating
    four EvidenceValue(..., EvidenceLevel.CONFIRMED_OFFICIAL, STRATEGY_GUIDE)
    calls per fixture. `compatible_product_categories`, where given, is
    transcribed from each fixture's own "取扱商品" column on the guide's
    fixture-data pages (book pages 110-119) rather than the harder-to-read
    fixture x category ○/× matrix elsewhere in the guide.
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
        compatible_product_categories=(
            EvidenceValue(compatible_product_categories, evidence, STRATEGY_GUIDE)
            if compatible_product_categories is not None
            else None
        ),
    )


# New fixtures with no prior baseline_data.py entry, transcribed from the
# strategy guide's explicit price/maintenance/capacity/attention/size table
# (docs/research/strategy-guide-full-decode-2026-09-16.md section 4). These do
# not overlap the IDs above (potted_plant/bench/fountain/parking_*/copier_*/
# vending_machine), which keep their existing confirmed values untouched.
STRATEGY_GUIDE_FIXTURES: tuple[FixtureDefinition, ...] = (
    # 4.1 常温棚・常温ワゴン (ambient shelves / wagons)
    _sg_fixture("small_ambient_shelf", footprint=(1, 1), purchase_price_yen=60,
                maintenance_yen_per_day=24, capacity=40, attention=10, placement="indoor",
                compatible_product_categories=("bread", "instant_food", "snacks", "books", "stationery", "electronics", "retort_food", "seasoning", "daily_goods", "underwear")),
    _sg_fixture("medium_ambient_shelf", footprint=(2, 1), purchase_price_yen=100,
                maintenance_yen_per_day=48, capacity=80, attention=10, placement="indoor",
                compatible_product_categories=("bread", "instant_food", "snacks", "books", "stationery", "electronics", "retort_food", "seasoning", "daily_goods", "underwear")),
    _sg_fixture("large_ambient_shelf", footprint=(3, 1), purchase_price_yen=140,
                maintenance_yen_per_day=72, capacity=120, attention=10, placement="indoor",
                compatible_product_categories=("bento", "bread", "instant_food", "snacks", "books", "stationery", "electronics", "retort_food", "seasoning", "daily_goods", "underwear", "medicine")),
    _sg_fixture("small_ambient_wagon", footprint=(1, 1), purchase_price_yen=30,
                maintenance_yen_per_day=24, capacity=15, attention=20, placement="indoor",
                compatible_product_categories=("bread", "instant_food", "snacks", "books", "stationery", "electronics", "retort_food", "seasoning", "daily_goods", "underwear")),
    _sg_fixture("medium_ambient_wagon", footprint=(2, 1), purchase_price_yen=50,
                maintenance_yen_per_day=48, capacity=30, attention=20, placement="indoor",
                compatible_product_categories=("bento", "bread", "instant_food", "snacks", "books", "stationery", "electronics", "retort_food", "seasoning", "daily_goods", "underwear", "medicine")),
    _sg_fixture("large_ambient_wagon", footprint=(3, 1), purchase_price_yen=70,
                maintenance_yen_per_day=72, capacity=45, attention=20, placement="indoor",
                compatible_product_categories=("bento", "bread", "instant_food", "snacks", "books", "stationery", "electronics", "retort_food", "seasoning", "daily_goods", "medicine", "underwear")),
    _sg_fixture("large_ambient_wagon_2", footprint=(2, 2), purchase_price_yen=90,
                maintenance_yen_per_day=96, capacity=60, attention=30, placement="indoor",
                compatible_product_categories=("bento", "bread", "instant_food", "snacks", "books", "stationery", "electronics", "retort_food", "seasoning", "daily_goods", "medicine", "underwear")),
    # 4.2 冷蔵・冷凍 (refrigerated / frozen)
    _sg_fixture("small_refrigerated_shelf", footprint=(1, 1), purchase_price_yen=200,
                maintenance_yen_per_day=720, capacity=30, attention=10, placement="indoor",
                compatible_product_categories=("cold_drink", "alcohol", "bento", "vegetables", "fish", "meat", "snacks")),
    _sg_fixture("medium_refrigerated_shelf", footprint=(1, 1), purchase_price_yen=350,
                maintenance_yen_per_day=1_200, capacity=60, attention=10, placement="indoor",
                compatible_product_categories=("cold_drink", "alcohol", "bento", "vegetables", "fish", "meat", "snacks")),
    _sg_fixture("large_refrigerated_shelf", footprint=(3, 1), purchase_price_yen=500,
                maintenance_yen_per_day=1_920, capacity=90, attention=10, placement="indoor",
                compatible_product_categories=("cold_drink", "alcohol", "bento", "vegetables", "fish", "meat", "medicine")),
    _sg_fixture("small_refrigerated_wagon", footprint=(1, 1), purchase_price_yen=120,
                maintenance_yen_per_day=960, capacity=10, attention=20, placement="indoor",
                compatible_product_categories=("cold_drink", "bento", "vegetables", "fish", "meat", "snacks")),
    _sg_fixture("medium_refrigerated_wagon", footprint=(2, 1), purchase_price_yen=200,
                maintenance_yen_per_day=1_680, capacity=20, attention=20, placement="indoor",
                compatible_product_categories=("cold_drink", "alcohol", "bento", "vegetables", "fish", "meat", "snacks")),
    _sg_fixture("large_refrigerated_wagon_1", footprint=(3, 1), purchase_price_yen=280,
                maintenance_yen_per_day=2_400, capacity=30, attention=20, placement="indoor",
                compatible_product_categories=("cold_drink", "alcohol", "bento", "vegetables", "fish", "meat", "medicine")),
    _sg_fixture("large_refrigerated_wagon_2", footprint=(2, 2), purchase_price_yen=360,
                maintenance_yen_per_day=3_120, capacity=40, attention=30, placement="indoor",
                compatible_product_categories=("cold_drink", "alcohol", "bento", "vegetables", "fish", "meat", "medicine")),
    _sg_fixture("small_frozen_shelf", footprint=(1, 1), purchase_price_yen=300,
                maintenance_yen_per_day=2_160, capacity=25, attention=10, placement="indoor",
                compatible_product_categories=("frozen_food", "ice_cream")),
    _sg_fixture("medium_frozen_shelf", footprint=(2, 1), purchase_price_yen=500,
                maintenance_yen_per_day=3_600, capacity=50, attention=10, placement="indoor",
                compatible_product_categories=("frozen_food", "ice_cream")),
    _sg_fixture("small_frozen_wagon", footprint=(1, 1), purchase_price_yen=200,
                maintenance_yen_per_day=1_920, capacity=10, attention=20, placement="indoor",
                compatible_product_categories=("frozen_food", "ice_cream")),
    _sg_fixture("medium_frozen_wagon", footprint=(2, 1), purchase_price_yen=380,
                maintenance_yen_per_day=3_120, capacity=20, attention=20, placement="indoor",
                compatible_product_categories=("frozen_food", "ice_cream")),
    # 4.3 専用ケース・イベント設備 (dedicated cases / event fixtures)
    _sg_fixture("hot_drink_case", footprint=(1, 1), purchase_price_yen=300,
                maintenance_yen_per_day=1_680, capacity=20, attention=20, placement="indoor",
                compatible_product_categories=("hot_drink",)),
    _sg_fixture("oden_case", footprint=(1, 1), purchase_price_yen=100,
                maintenance_yen_per_day=1_920, capacity=10, attention=30, placement="indoor",
                compatible_product_categories=("oden",)),
    _sg_fixture("steamed_bun_case", footprint=(1, 1), purchase_price_yen=300,
                maintenance_yen_per_day=1_920, capacity=20, attention=30, placement="indoor",
                compatible_product_categories=("chinese_steamed_bun",)),
    _sg_fixture("event_shelf", footprint=(2, 1), purchase_price_yen=600,
                maintenance_yen_per_day=1_920, capacity=60, attention=40, placement="indoor",
                compatible_product_categories=("event_goods",)),
    _sg_fixture("event_wagon", footprint=(2, 1), purchase_price_yen=300,
                maintenance_yen_per_day=1_200, capacity=30, attention=60, placement="indoor",
                compatible_product_categories=("event_goods",)),
    # 4.4 自販機・レジ (vending machines / registers; copier_a/copier_b above
    # already correspond to the small/medium copier rows in this section)
    _sg_fixture("small_tobacco_vending", footprint=(1, 1), purchase_price_yen=600,
                maintenance_yen_per_day=240, capacity=20, attention=15, placement="indoor_outdoor",
                compatible_product_categories=("tobacco",)),
    _sg_fixture("large_tobacco_vending", footprint=(2, 1), purchase_price_yen=1_000,
                maintenance_yen_per_day=480, capacity=40, attention=20, placement="indoor_outdoor",
                compatible_product_categories=("tobacco",)),
    _sg_fixture("small_cold_drink_vending", footprint=(1, 1), purchase_price_yen=800,
                maintenance_yen_per_day=480, capacity=20, attention=15, placement="indoor_outdoor",
                compatible_product_categories=("cold_drink", "alcohol")),
    _sg_fixture("large_cold_drink_vending", footprint=(2, 1), purchase_price_yen=1_400,
                maintenance_yen_per_day=960, capacity=40, attention=20, placement="indoor_outdoor",
                compatible_product_categories=("cold_drink", "alcohol")),
    _sg_fixture("small_hot_cold_drink_vending", footprint=(1, 1), purchase_price_yen=1_000,
                maintenance_yen_per_day=960, capacity=15, attention=15, placement="indoor_outdoor",
                compatible_product_categories=("cold_drink", "hot_drink")),
    _sg_fixture("large_hot_cold_drink_vending", footprint=(2, 1), purchase_price_yen=1_800,
                maintenance_yen_per_day=1_920, capacity=30, attention=20, placement="indoor_outdoor",
                compatible_product_categories=("cold_drink", "hot_drink")),
    _sg_fixture("register_1", footprint=(2, 1), purchase_price_yen=2_000,
                maintenance_yen_per_day=1_440, capacity=0, attention=15, placement="indoor"),
    _sg_fixture("register_2", footprint=(2, 1), purchase_price_yen=3_000,
                maintenance_yen_per_day=1_680, capacity=60, attention=25, placement="indoor",
                compatible_product_categories=("parcel_delivery_form",)),
    _sg_fixture("register_3", footprint=(3, 1), purchase_price_yen=3_000,
                maintenance_yen_per_day=1_680, capacity=0, attention=20, placement="indoor"),
    _sg_fixture("register_4", footprint=(3, 1), purchase_price_yen=5_000,
                maintenance_yen_per_day=1_920, capacity=90, attention=30, placement="indoor",
                compatible_product_categories=("parcel_delivery_form",)),
    # 4.5 サービス・外構: only rows with no prior baseline_data.py entry.
    # potted_plant/bench/fountain/parking_* above already exist and were
    # cross-checked in place instead of being duplicated here. The
    # "UNCERTAIN_NAME" dispenser row from the guide is not transcribed
    # because its name could not be read from the scan.
    _sg_fixture("indoor_dispenser", footprint=(1, 1), purchase_price_yen=4_000,
                maintenance_yen_per_day=1_440, capacity=50, attention=20, placement="indoor",
                compatible_product_categories=("cash",)),
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
        # RESOLVED (2026-09-17, explicit one-off user instruction: on a
        # strategy-guide vs. existing-value conflict, take the guide's
        # value). The guide's 店舗データ table (book pages 106-109) prints
        # each store size as two orientations with distinct 店舗内(editable
        # floor) dimensions: 店舗1=5x8, 店舗2=8x5 (small); 店舗3=7x10,
        # 店舗4=10x7 (medium); 店舗5=8x12, 店舗6=12x8 (large). Neither
        # matched the previous (8,13)/(13,14) visual-reconstruction values,
        # which are superseded here. The guide does not label which of its
        # two orientations is this codebase's "top" vs. "bottom" id; store1/
        # 3/5 are assigned to *_top and store2/4/6 to *_bottom purely by
        # matching list order on both sides -- an inference, not a confirmed
        # mapping. See docs/research/strategy-guide-fixture-crosscheck-2026-09-16.md.
        editable_floor=EvidenceValue(
            (5, 8),
            EvidenceLevel.CONFIRMED_OFFICIAL,
            STRATEGY_GUIDE,
            "店舗1's 店舗内 dimensions; top/bottom orientation match to store1/2 is inferred, not confirmed.",
        ),
        unlocked_at_beginner_start=EvidenceValue(
            True,
            EvidenceLevel.CONFIRMED_VISUAL,
            "PS store-selection screenshot",
        ),
        # Task #57: 建物面積 breakdown (総面積/建物全体/床面積/店外スペース),
        # 店舗1's row. CONFIRMED_OFFICIAL, cross-checked against the guide's
        # own chapter-4 資料集 table (book pages 106-109) against the
        # already-ported 本2.pdf source and found value-for-value identical;
        # see docs/research/strategy-guide-shopkeeper-manual-part2-2026-09-19.md
        # section 4.1.
        total_area_tiles=EvidenceValue(100, EvidenceLevel.CONFIRMED_OFFICIAL, STRATEGY_GUIDE),
        whole_building_area_tiles=EvidenceValue(70, EvidenceLevel.CONFIRMED_OFFICIAL, STRATEGY_GUIDE),
        floor_area_tiles=EvidenceValue(40, EvidenceLevel.CONFIRMED_OFFICIAL, STRATEGY_GUIDE),
        exterior_space_tiles=EvidenceValue(30, EvidenceLevel.CONFIRMED_OFFICIAL, STRATEGY_GUIDE),
    ),
    StoreVariant(
        id="small_bottom",
        size_tier="small",
        orientation=None,
        # Strategy guide's store-selection screen and its 店舗1/店舗2 data
        # rows both show 6,000,000 yen for every "small" variant regardless
        # of orientation, so this previously-unknown price can be filled in
        # without touching small_top's separately-sourced editable_floor.
        # Independently confirmed by direct video observation (V02 Console
        # Archives PS5 video 09:12; video-v02-opening-transactions-2026-09-08.md).
        construction_price_yen=EvidenceValue(6_000_000, EvidenceLevel.CONFIRMED_OFFICIAL, STRATEGY_GUIDE),
        editable_floor=EvidenceValue(
            (8, 5),
            EvidenceLevel.CONFIRMED_OFFICIAL,
            STRATEGY_GUIDE,
            "店舗2's 店舗内 dimensions; top/bottom orientation match to store1/2 is inferred, not confirmed.",
        ),
        unlocked_at_beginner_start=EvidenceValue(
            True,
            EvidenceLevel.CONFIRMED_VISUAL,
            "PS store-selection screenshot",
        ),
        # Task #57: 店舗2's row; guide states the same small-tier area
        # breakdown for both orientations (see small_top's own comment).
        total_area_tiles=EvidenceValue(100, EvidenceLevel.CONFIRMED_OFFICIAL, STRATEGY_GUIDE),
        whole_building_area_tiles=EvidenceValue(70, EvidenceLevel.CONFIRMED_OFFICIAL, STRATEGY_GUIDE),
        floor_area_tiles=EvidenceValue(40, EvidenceLevel.CONFIRMED_OFFICIAL, STRATEGY_GUIDE),
        exterior_space_tiles=EvidenceValue(30, EvidenceLevel.CONFIRMED_OFFICIAL, STRATEGY_GUIDE),
    ),
    StoreVariant(
        id="medium_top",
        size_tier="medium",
        orientation=None,
        # Independently confirmed by direct video observation (V02 Console
        # Archives PS5 video 09:05; 12:05-12:10; video-v02-opening-transactions-2026-09-08.md).
        construction_price_yen=EvidenceValue(12_000_000, EvidenceLevel.CONFIRMED_OFFICIAL, STRATEGY_GUIDE),
        # See small_top's comment: guide's 店舗3 店舗内 dimensions; top/bottom
        # match to store3/4 is inferred by list order, not confirmed.
        editable_floor=EvidenceValue(
            (7, 10),
            EvidenceLevel.CONFIRMED_OFFICIAL,
            STRATEGY_GUIDE,
            "店舗3's 店舗内 dimensions; top/bottom orientation match to store3/4 is inferred, not confirmed.",
        ),
        unlocked_at_beginner_start=EvidenceValue(
            False,
            EvidenceLevel.CONFIRMED_VISUAL,
            "PS store-selection screenshot",
        ),
        # Task #57: 店舗3's row (see small_top's comment for source/method).
        total_area_tiles=EvidenceValue(144, EvidenceLevel.CONFIRMED_OFFICIAL, STRATEGY_GUIDE),
        whole_building_area_tiles=EvidenceValue(108, EvidenceLevel.CONFIRMED_OFFICIAL, STRATEGY_GUIDE),
        floor_area_tiles=EvidenceValue(70, EvidenceLevel.CONFIRMED_OFFICIAL, STRATEGY_GUIDE),
        exterior_space_tiles=EvidenceValue(36, EvidenceLevel.CONFIRMED_OFFICIAL, STRATEGY_GUIDE),
    ),
    StoreVariant(
        id="medium_bottom",
        size_tier="medium",
        orientation=None,
        construction_price_yen=EvidenceValue(12_000_000, EvidenceLevel.CONFIRMED_OFFICIAL, STRATEGY_GUIDE),
        editable_floor=EvidenceValue(
            (10, 7),
            EvidenceLevel.CONFIRMED_OFFICIAL,
            STRATEGY_GUIDE,
            "店舗4's 店舗内 dimensions; top/bottom orientation match to store3/4 is inferred, not confirmed.",
        ),
        unlocked_at_beginner_start=EvidenceValue(
            False,
            EvidenceLevel.CONFIRMED_VISUAL,
            "PS store-selection screenshot",
        ),
        # Task #57: 店舗4's row (same area breakdown as medium_top -- the
        # guide's table gives identical values for both medium orientations,
        # same as it does for the small tier).
        total_area_tiles=EvidenceValue(144, EvidenceLevel.CONFIRMED_OFFICIAL, STRATEGY_GUIDE),
        whole_building_area_tiles=EvidenceValue(108, EvidenceLevel.CONFIRMED_OFFICIAL, STRATEGY_GUIDE),
        floor_area_tiles=EvidenceValue(70, EvidenceLevel.CONFIRMED_OFFICIAL, STRATEGY_GUIDE),
        exterior_space_tiles=EvidenceValue(36, EvidenceLevel.CONFIRMED_OFFICIAL, STRATEGY_GUIDE),
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
        # used as the majority value, and is independently confirmed by
        # direct video observation (V02 Console Archives PS5 video 09:07;
        # video-v02-opening-transactions-2026-09-08.md). See
        # docs/research/strategy-guide-fixture-crosscheck-2026-09-16.md.
        construction_price_yen=EvidenceValue(18_000_000, EvidenceLevel.CONFIRMED_OFFICIAL, STRATEGY_GUIDE),
        # RESOLVED (2026-09-17): see small_top's comment above. Guide's 店舗5
        # 店舗内 dimensions; superseded the wiki-derived 13x14, which did not
        # match either the guide's 店舗内 or 店舗外周 columns for any store
        # (see the crosscheck note). Top/bottom match to store5/6 is
        # inferred by list order, not confirmed.
        editable_floor=EvidenceValue(
            (8, 12),
            EvidenceLevel.CONFIRMED_OFFICIAL,
            STRATEGY_GUIDE,
            "店舗5's 店舗内 dimensions; top/bottom orientation match to store5/6 is inferred, not confirmed.",
        ),
        unlocked_at_beginner_start=EvidenceValue(
            False,
            EvidenceLevel.CONFIRMED_VISUAL,
            "PS store-selection screenshot",
        ),
        # Task #57: 店舗5's row. total_area_tiles=196=14x14, independently
        # re-confirming (not resolving) the already-flagged large-tier
        # footprint conflict noted above: this matches 14x14, not the case-
        # study captions' 16x16 (see docs/research/strategy-guide-shopkeeper-
        # manual-part2-2026-09-19.md section 4.1's own cross-check note).
        # Left as-is, same as the existing conflict -- not adjudicated here.
        total_area_tiles=EvidenceValue(196, EvidenceLevel.CONFIRMED_OFFICIAL, STRATEGY_GUIDE),
        whole_building_area_tiles=EvidenceValue(154, EvidenceLevel.CONFIRMED_OFFICIAL, STRATEGY_GUIDE),
        floor_area_tiles=EvidenceValue(108, EvidenceLevel.CONFIRMED_OFFICIAL, STRATEGY_GUIDE),
        exterior_space_tiles=EvidenceValue(42, EvidenceLevel.CONFIRMED_OFFICIAL, STRATEGY_GUIDE),
    ),
    StoreVariant(
        id="large_bottom",
        size_tier="large",
        orientation=None,
        # Independently confirmed by direct video observation (V02 Console
        # Archives PS5 video 09:06; video-v02-opening-transactions-2026-09-08.md).
        construction_price_yen=EvidenceValue(18_000_000, EvidenceLevel.CONFIRMED_OFFICIAL, STRATEGY_GUIDE),
        editable_floor=EvidenceValue(
            (12, 8),
            EvidenceLevel.CONFIRMED_OFFICIAL,
            STRATEGY_GUIDE,
            "店舗6's 店舗内 dimensions; top/bottom orientation match to store5/6 is inferred, not confirmed.",
        ),
        unlocked_at_beginner_start=EvidenceValue(
            False,
            EvidenceLevel.CONFIRMED_VISUAL,
            "PS store-selection screenshot",
        ),
        # Task #57: 店舗6's row (same area breakdown as large_top).
        total_area_tiles=EvidenceValue(196, EvidenceLevel.CONFIRMED_OFFICIAL, STRATEGY_GUIDE),
        whole_building_area_tiles=EvidenceValue(154, EvidenceLevel.CONFIRMED_OFFICIAL, STRATEGY_GUIDE),
        floor_area_tiles=EvidenceValue(108, EvidenceLevel.CONFIRMED_OFFICIAL, STRATEGY_GUIDE),
        exterior_space_tiles=EvidenceValue(42, EvidenceLevel.CONFIRMED_OFFICIAL, STRATEGY_GUIDE),
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
        # RESOLVED (2026-09-17, explicit one-off user instruction: on a
        # strategy-guide vs. existing-value conflict, take the guide's
        # value). Guide reports 160 yen/day maintenance
        # ("維持費160円/日"), independently confirmed twice more (fixture
        # data table and オールテクニックガイド, book pages 69/118-119); the
        # wiki-derived 168 previously kept here is superseded. See
        # docs/research/strategy-guide-fixture-crosscheck-2026-09-16.md for
        # the earlier never-overwrite record of this conflict.
        EvidenceValue(160, EvidenceLevel.CONFIRMED_OFFICIAL, STRATEGY_GUIDE),
        # RESOLVED (same instruction/session as above): guide reports +4
        # service_bonus ("サービス値が4上昇する"), independently confirmed
        # twice; the wiki-derived +3 previously kept here is superseded.
        EvidenceValue(4, EvidenceLevel.CONFIRMED_OFFICIAL, STRATEGY_GUIDE),
        purchase_price_yen=EvidenceValue(2_000, EvidenceLevel.CONFIRMED_OFFICIAL, STRATEGY_GUIDE),
        placement=EvidenceValue("indoor_outdoor", EvidenceLevel.CONFIRMED_OFFICIAL, STRATEGY_GUIDE),
    ),
    FixtureDefinition(
        "fountain",
        EvidenceValue((2, 2), EvidenceLevel.CONFIRMED_COMMUNITY, WIKI + "%E5%86%85%E8%A3%85"),
        EvidenceValue(2_400, EvidenceLevel.CONFIRMED_COMMUNITY, WIKI + "%E5%86%85%E8%A3%85"),
        # RESOLVED (2026-09-17, same instruction as bench above): guide
        # reports +30 service_bonus ("サービス値が30上昇する"), independently
        # confirmed twice; the wiki-derived +25 previously kept here is
        # superseded.
        EvidenceValue(30, EvidenceLevel.CONFIRMED_OFFICIAL, STRATEGY_GUIDE),
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
        compatible_product_categories=EvidenceValue(("copy_paper",), EvidenceLevel.CONFIRMED_OFFICIAL, STRATEGY_GUIDE),
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
        compatible_product_categories=EvidenceValue(("copy_paper",), EvidenceLevel.CONFIRMED_OFFICIAL, STRATEGY_GUIDE),
    ),
    FixtureDefinition(
        "vending_machine",
        footprint=None,
        sale_mode="self_service_candidate",
    ),
) + STRATEGY_GUIDE_FIXTURES
# V02 Console Archives PS5 video (timestamps 09:50, 13:00-15:01) independently
# confirms, via direct gameplay observation, the exact same
# maintenance/purchase-price/capacity/attention values already recorded above
# for small_ambient_shelf, medium_ambient_shelf, large_ambient_shelf,
# steamed_bun_case, and small_cold_drink_vending (all sourced from the
# strategy guide's own fixture data pages). See
# docs/research/video-v02-opening-transactions-2026-09-08.md.

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

_PERMIT_FEE_AND_DISTANCE_YEN_TILES = {
    # From the guide's own "販売許可に必要な金額" table and its distance
    # diagram (both book pages 6-7), independently corroborated by the same
    # page's "合計2千万円になってしまう" (3M + 7M + 10M = 20M) body text.
    # The diagram's rings are labeled 店建設可能=5 / たばこ販売可能=7 /
    # 酒類販売可能=11 / 薬類販売可能=15 tiles out from a store; the 5-tile
    # ring is the store-to-store minimum distance (see
    # docs/research/permit-timing-and-state-reset-exploits-2026-09-06.md),
    # not a permit, so only the outer three map to a permit id here.
    "tobacco": (7_000_000, 7),
    "alcohol": (3_000_000, 11),
    "medicine": (10_000_000, 15),
}

PERMITS = tuple(
    PermitDefinition(
        id=permit_id,
        fee_yen=EvidenceValue(
            _PERMIT_FEE_AND_DISTANCE_YEN_TILES[permit_id][0], EvidenceLevel.CONFIRMED_OFFICIAL, STRATEGY_GUIDE
        ),
        exclusion_distance_tiles=EvidenceValue(
            _PERMIT_FEE_AND_DISTANCE_YEN_TILES[permit_id][1],
            EvidenceLevel.CONFIRMED_OFFICIAL,
            STRATEGY_GUIDE,
            "Tile unit and whether this is Chebyshev/Euclidean distance is not confirmed by the guide.",
        ),
        eligibility_is_independent=EvidenceValue(
            True,
            EvidenceLevel.CONFIRMED_COMMUNITY,
            "PS long-play observation: tobacco/alcohol available while medicine unavailable at the same site",
        ),
    )
    for permit_id in ("tobacco", "alcohol", "medicine")
)

SCENARIO_GUIDE = WIKI + "%E3%82%B2%E3%83%BC%E3%83%A0%E3%83%A2%E3%83%BC%E3%83%89%E6%94%BB%E7%95%A5"
SCENARIO_INITIAL_RIVAL_TOPOLOGY = (
    "docs/research/scenario-initial-rival-topology-2026-09-06.md, citing PS long-play records "
    "https://pinkblue.sakura.ne.jp/contents/kansou/game/psgame/ps-simulation/ps-ai/"
    "ai-the-conbini-tyukyu.html (intermediate) and ai-the-conbini-jokyu.html (advanced)"
)

SCENARIOS = (
    ScenarioDefinition(
        "beginner",
        EvidenceValue(200_000_000, EvidenceLevel.CONFIRMED_COMMUNITY, SCENARIO_GUIDE),
        EvidenceValue(
            "metropolitan_government_after_population_threshold",
            EvidenceLevel.CONFIRMED_COMMUNITY,
            SCENARIO_GUIDE,
        ),
        # Task #62: exact initial rival store count is UNKNOWN (research doc
        # section 4) -- only that at least one rival branch exists at start.
        initial_rival_branch_exists=EvidenceValue(
            True, EvidenceLevel.CONFIRMED_COMMUNITY, SCENARIO_INITIAL_RIVAL_TOPOLOGY,
            "PS beginner long-play record shows a rival branch (2号店) acquired shortly after "
            "start; total rival store count at start is not stated anywhere found so far.",
        ),
    ),
    ScenarioDefinition(
        "intermediate",
        EvidenceValue(150_000_000, EvidenceLevel.CONFIRMED_COMMUNITY, SCENARIO_GUIDE),
        EvidenceValue(
            "10_player_stores", EvidenceLevel.CONFIRMED_COMMUNITY, SCENARIO_GUIDE
        ),
        # Task #62: PS intermediate long-play explicitly states "ライバル店は
        # 最初3店舗ありました" (1 headquarters + 2 branches), two of which the
        # player then acquires -- position/size/permits/staff/layout remain
        # UNKNOWN and are deliberately not invented here.
        initial_rival_store_roles=EvidenceValue(
            ("headquarters", "branch", "branch"),
            EvidenceLevel.CONFIRMED_COMMUNITY,
            SCENARIO_INITIAL_RIVAL_TOPOLOGY,
        ),
    ),
    ScenarioDefinition(
        "advanced",
        EvidenceValue(150_000_000, EvidenceLevel.CONFIRMED_COMMUNITY, SCENARIO_GUIDE),
        EvidenceValue(
            "owner_rating_5_stars", EvidenceLevel.CONFIRMED_COMMUNITY, SCENARIO_GUIDE
        ),
        # Task #62: PS advanced long-play explicitly states the rival has
        # only a headquarters at start ("ライバル店も本店のみ"), then opens
        # branches over time (3 rival stores by year 2).
        initial_rival_store_roles=EvidenceValue(
            ("headquarters",), EvidenceLevel.CONFIRMED_COMMUNITY, SCENARIO_INITIAL_RIVAL_TOPOLOGY
        ),
        rival_can_open_branches_after_start=EvidenceValue(
            True, EvidenceLevel.CONFIRMED_COMMUNITY, SCENARIO_INITIAL_RIVAL_TOPOLOGY
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
    seasonal_demand: Optional[str] = None,
    profit_per_unit_yen: Optional[int] = None,
    max_maintenance_yen_per_day: Optional[int] = None,
    max_capacity: Optional[int] = None,
    demand_example_count: Optional[int] = None,
    compatible_fixtures_text: Optional[str] = None,
) -> ProductCategoryPricing:
    """Build one strategy-guide product-category pricing row with uniform provenance.

    Source: docs/research/strategy-guide-full-decode-2026-09-16.md section 3,
    re-read against the guide's DATA LIST product table (book page 85) on a
    higher-resolution scan. This is category-level standard pricing, not a
    per-SKU price list; no prior baseline_data.py table covered this, so
    there is nothing to cross-check or conflict with here.

    `seasonal_demand` comes from that table's own "季節" (season) column.
    The remaining four keyword args come from its 定価/原価率 columns'
    trailing five columns -- 1個の利益(profit_per_unit_yen) / 商品棚
    (compatible_fixtures_text) / 最大維持費(max_maintenance_yen_per_day) /
    最大収容力(max_capacity) / 需要数例(demand_example_count) -- which an
    earlier, lower-resolution read of this same page could not resolve with
    confidence and mapped incorrectly (see `ProductCategoryPricing`'s
    `profit_per_unit_yen` docstring for the correction record; decision
    0080 documents the original, mistaken reading).
    """

    evidence = EvidenceLevel.CONFIRMED_OFFICIAL
    return ProductCategoryPricing(
        category_id,
        display_name_ja,
        EvidenceValue(standard_retail_price_yen, evidence, STRATEGY_GUIDE),
        EvidenceValue(cost_rate_pct, evidence, STRATEGY_GUIDE),
        EvidenceValue(margin_rate_pct, evidence, STRATEGY_GUIDE),
        seasonal_demand=(
            EvidenceValue(seasonal_demand, evidence, STRATEGY_GUIDE)
            if seasonal_demand is not None
            else None
        ),
        profit_per_unit_yen=(
            EvidenceValue(profit_per_unit_yen, evidence, STRATEGY_GUIDE)
            if profit_per_unit_yen is not None
            else None
        ),
        max_maintenance_yen_per_day=(
            EvidenceValue(max_maintenance_yen_per_day, evidence, STRATEGY_GUIDE)
            if max_maintenance_yen_per_day is not None
            else None
        ),
        max_capacity=(
            EvidenceValue(max_capacity, evidence, STRATEGY_GUIDE)
            if max_capacity is not None
            else None
        ),
        demand_example_count=(
            EvidenceValue(
                demand_example_count,
                evidence,
                STRATEGY_GUIDE,
                note="Guide's own caption: a worked example under one unstated "
                "condition set, not a demand formula or coefficient.",
            )
            if demand_example_count is not None
            else None
        ),
        compatible_fixtures_text=(
            EvidenceValue(compatible_fixtures_text, evidence, STRATEGY_GUIDE)
            if compatible_fixtures_text is not None
            else None
        ),
    )


# Category-level standard price / cost-rate / margin-rate table, transcribed
# from the strategy guide (docs/research/strategy-guide-full-decode-2026-09-16.md
# section 3). `cash` (現金, the special zero-margin category used for cash-like
# instruments) is included as-is from the source table. The five trailing
# keyword args on every row (profit_per_unit_yen through
# compatible_fixtures_text) were re-read from a higher-resolution scan of the
# same DATA LIST product table (book page 85); see `_sg_category`'s
# docstring for why `profit_per_unit_yen` replaces a previous, incorrect
# `restock_quantity` field of the same values.
PRODUCT_CATEGORY_PRICING: tuple[ProductCategoryPricing, ...] = (
    _sg_category("cold_drink", "冷たい飲料", standard_retail_price_yen=110, cost_rate_pct=50, margin_rate_pct=50, seasonal_demand="summer", profit_per_unit_yen=55, max_maintenance_yen_per_day=130, max_capacity=90, demand_example_count=48, compatible_fixtures_text="冷蔵棚/ワゴン,飲料自販・冷蔵/温冷"),
    _sg_category("hot_drink", "温かい飲料", standard_retail_price_yen=110, cost_rate_pct=50, margin_rate_pct=50, seasonal_demand="winter", profit_per_unit_yen=55, max_maintenance_yen_per_day=80, max_capacity=30, demand_example_count=37, compatible_fixtures_text="温ジュース,飲料自販・温冷"),
    _sg_category("alcohol", "酒類", standard_retail_price_yen=1_000, cost_rate_pct=70, margin_rate_pct=30, profit_per_unit_yen=300, max_maintenance_yen_per_day=130, max_capacity=90, demand_example_count=23, compatible_fixtures_text="冷蔵棚/ワゴン,飲料自販・冷蔵"),
    _sg_category("bento", "弁当類", standard_retail_price_yen=400, cost_rate_pct=60, margin_rate_pct=40, profit_per_unit_yen=160, max_maintenance_yen_per_day=130, max_capacity=120, demand_example_count=28, compatible_fixtures_text="常温棚/ワゴン,冷蔵棚/ワゴン"),
    _sg_category("bread", "パン類", standard_retail_price_yen=300, cost_rate_pct=50, margin_rate_pct=50, profit_per_unit_yen=150, max_maintenance_yen_per_day=4, max_capacity=120, demand_example_count=22, compatible_fixtures_text="常温棚/ワゴン"),
    _sg_category("instant_food", "インスタント類", standard_retail_price_yen=150, cost_rate_pct=60, margin_rate_pct=40, profit_per_unit_yen=60, max_maintenance_yen_per_day=4, max_capacity=120, demand_example_count=26, compatible_fixtures_text="常温棚/ワゴン"),
    _sg_category("snacks", "菓子類", standard_retail_price_yen=200, cost_rate_pct=60, margin_rate_pct=40, profit_per_unit_yen=80, max_maintenance_yen_per_day=4, max_capacity=120, demand_example_count=37, compatible_fixtures_text="常温棚/ワゴン"),
    _sg_category("books", "本類", standard_retail_price_yen=400, cost_rate_pct=60, margin_rate_pct=40, profit_per_unit_yen=160, max_maintenance_yen_per_day=4, max_capacity=120, demand_example_count=7, compatible_fixtures_text="常温棚/ワゴン"),
    _sg_category("tobacco", "たばこ", standard_retail_price_yen=250, cost_rate_pct=70, margin_rate_pct=30, profit_per_unit_yen=75, max_maintenance_yen_per_day=20, max_capacity=40, demand_example_count=23, compatible_fixtures_text="たばこ自販"),
    _sg_category("ice_cream", "アイスクリーム", standard_retail_price_yen=100, cost_rate_pct=50, margin_rate_pct=50, seasonal_demand="summer", profit_per_unit_yen=50, max_maintenance_yen_per_day=130, max_capacity=60, demand_example_count=19, compatible_fixtures_text="冷凍棚/ワゴン"),
    _sg_category("stationery", "文房具", standard_retail_price_yen=150, cost_rate_pct=60, margin_rate_pct=40, profit_per_unit_yen=60, max_maintenance_yen_per_day=4, max_capacity=120, demand_example_count=4, compatible_fixtures_text="常温棚/ワゴン"),
    _sg_category("retort_food", "レトルト類", standard_retail_price_yen=600, cost_rate_pct=60, margin_rate_pct=40, profit_per_unit_yen=240, max_maintenance_yen_per_day=4, max_capacity=120, demand_example_count=17, compatible_fixtures_text="常温棚/ワゴン"),
    _sg_category("electronics", "電機製品類", standard_retail_price_yen=800, cost_rate_pct=60, margin_rate_pct=40, profit_per_unit_yen=320, max_maintenance_yen_per_day=4, max_capacity=120, demand_example_count=8, compatible_fixtures_text="常温棚/ワゴン"),
    _sg_category("seasoning", "調味料類", standard_retail_price_yen=400, cost_rate_pct=60, margin_rate_pct=40, profit_per_unit_yen=160, max_maintenance_yen_per_day=4, max_capacity=120, demand_example_count=1, compatible_fixtures_text="常温棚/ワゴン"),
    _sg_category("vegetables", "野菜類", standard_retail_price_yen=1_500, cost_rate_pct=50, margin_rate_pct=50, profit_per_unit_yen=750, max_maintenance_yen_per_day=130, max_capacity=90, demand_example_count=18, compatible_fixtures_text="冷蔵棚/ワゴン"),
    _sg_category("frozen_food", "冷凍食品類", standard_retail_price_yen=500, cost_rate_pct=60, margin_rate_pct=40, profit_per_unit_yen=200, max_maintenance_yen_per_day=130, max_capacity=60, demand_example_count=1, compatible_fixtures_text="冷凍棚/ワゴン"),
    _sg_category("fish", "魚類", standard_retail_price_yen=1_000, cost_rate_pct=60, margin_rate_pct=40, profit_per_unit_yen=400, max_maintenance_yen_per_day=130, max_capacity=90, demand_example_count=18, compatible_fixtures_text="冷蔵棚/ワゴン"),
    _sg_category("oden", "おでん", standard_retail_price_yen=250, cost_rate_pct=50, margin_rate_pct=50, seasonal_demand="winter", profit_per_unit_yen=125, max_maintenance_yen_per_day=80, max_capacity=10, demand_example_count=14, compatible_fixtures_text="おでん専用ケース"),
    _sg_category("daily_goods", "日用品", standard_retail_price_yen=800, cost_rate_pct=60, margin_rate_pct=40, profit_per_unit_yen=320, max_maintenance_yen_per_day=4, max_capacity=120, demand_example_count=16, compatible_fixtures_text="常温棚/ワゴン"),
    _sg_category("copy_paper", "コピー用紙", standard_retail_price_yen=50, cost_rate_pct=60, margin_rate_pct=40, profit_per_unit_yen=20, max_maintenance_yen_per_day=60, max_capacity=40, demand_example_count=5, compatible_fixtures_text="コピー機"),
    _sg_category("parcel_delivery_form", "宅急便申込書", standard_retail_price_yen=1_000, cost_rate_pct=80, margin_rate_pct=20, profit_per_unit_yen=200, max_maintenance_yen_per_day=80, max_capacity=90, demand_example_count=4, compatible_fixtures_text="レジ"),
    _sg_category("medicine", "薬品", standard_retail_price_yen=1_500, cost_rate_pct=70, margin_rate_pct=30, profit_per_unit_yen=450, max_maintenance_yen_per_day=130, max_capacity=120, demand_example_count=13, compatible_fixtures_text="常温棚/ワゴン,冷蔵棚/ワゴン"),
    _sg_category("underwear", "下着類", standard_retail_price_yen=1_000, cost_rate_pct=60, margin_rate_pct=40, profit_per_unit_yen=400, max_maintenance_yen_per_day=4, max_capacity=120, demand_example_count=28, compatible_fixtures_text="常温棚/ワゴン"),
    _sg_category("event_goods", "イベント商品", standard_retail_price_yen=1_000, cost_rate_pct=60, margin_rate_pct=40, profit_per_unit_yen=400, max_maintenance_yen_per_day=80, max_capacity=60, demand_example_count=12, compatible_fixtures_text="イベントケース棚/ワゴン"),
    _sg_category("chinese_steamed_bun", "中華まん", standard_retail_price_yen=170, cost_rate_pct=60, margin_rate_pct=40, seasonal_demand="winter", profit_per_unit_yen=68, max_maintenance_yen_per_day=80, max_capacity=20, demand_example_count=7, compatible_fixtures_text="中華まん専用ケース"),
    _sg_category("meat", "肉類", standard_retail_price_yen=1_200, cost_rate_pct=50, margin_rate_pct=50, profit_per_unit_yen=600, max_maintenance_yen_per_day=130, max_capacity=90, demand_example_count=10, compatible_fixtures_text="冷蔵棚/ワゴン"),
    _sg_category("cash", "現金", standard_retail_price_yen=0, cost_rate_pct=100, margin_rate_pct=0, profit_per_unit_yen=0, max_maintenance_yen_per_day=100, max_capacity=90, compatible_fixtures_text="キャッシュディスペンサー"),
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

# Trade-area radius by arrival method, transcribed from the guide's "来店手段
# /エリア半径" table (book page 31). See `TradeAreaRadiusEntry`'s docstring:
# this directly answers part of what prior research had recorded as an
# unresolved "商圏半径の内部計算式".
TRADE_AREA_RADIUS_TILES: tuple[TradeAreaRadiusEntry, ...] = (
    TradeAreaRadiusEntry(
        EvidenceValue("徒歩", EvidenceLevel.CONFIRMED_OFFICIAL, STRATEGY_GUIDE),
        EvidenceValue(20, EvidenceLevel.CONFIRMED_OFFICIAL, STRATEGY_GUIDE),
    ),
    TradeAreaRadiusEntry(
        EvidenceValue("自転車", EvidenceLevel.CONFIRMED_OFFICIAL, STRATEGY_GUIDE),
        EvidenceValue(40, EvidenceLevel.CONFIRMED_OFFICIAL, STRATEGY_GUIDE),
    ),
    TradeAreaRadiusEntry(
        EvidenceValue("バイク", EvidenceLevel.CONFIRMED_OFFICIAL, STRATEGY_GUIDE),
        EvidenceValue(60, EvidenceLevel.CONFIRMED_OFFICIAL, STRATEGY_GUIDE),
    ),
    TradeAreaRadiusEntry(
        EvidenceValue("自動車", EvidenceLevel.CONFIRMED_OFFICIAL, STRATEGY_GUIDE),
        EvidenceValue(70, EvidenceLevel.CONFIRMED_OFFICIAL, STRATEGY_GUIDE),
    ),
)

QUICK_REFERENCE_GUIDE_TIME_PAGE = (
    "official strategy guide quick reference book, \"時間\" section (book "
    "page 2-3); re-verified 2026-09-24 against a 400dpi rescan of the same "
    "physical page, superseding the 2026-09-19 moderate-confidence "
    "transcription in docs/research/quick-reference-guide-part1-2026-09-19.md "
    "section 1.6/1.7 where the two disagree (see docs/decisions/0132-*.md)"
)

# 年間カレンダー table (書籍頁3): season + weekday/holiday flag for each of the
# 4 representative days simulated per in-game month. CONFIRMED_OFFICIAL, not a
# guess -- clock.py's RepresentativeDayType previously used only a "day==4 is
# the sole holiday" simplification (its own comment invited replacement "if
# the guidebook contradicts it"); this table is that contradiction; see
# decision 0132.
ANNUAL_CALENDAR: tuple[AnnualCalendarMonthEntry, ...] = (
    AnnualCalendarMonthEntry(
        1,
        EvidenceValue("冬期", EvidenceLevel.CONFIRMED_OFFICIAL, QUICK_REFERENCE_GUIDE_TIME_PAGE),
        EvidenceValue(
            ("holiday", "weekday", "weekday", "holiday"),
            EvidenceLevel.CONFIRMED_OFFICIAL,
            QUICK_REFERENCE_GUIDE_TIME_PAGE,
        ),
    ),
    AnnualCalendarMonthEntry(
        2,
        EvidenceValue("冬期", EvidenceLevel.CONFIRMED_OFFICIAL, QUICK_REFERENCE_GUIDE_TIME_PAGE),
        EvidenceValue(
            ("weekday", "weekday", "weekday", "holiday"),
            EvidenceLevel.CONFIRMED_OFFICIAL,
            QUICK_REFERENCE_GUIDE_TIME_PAGE,
        ),
    ),
    AnnualCalendarMonthEntry(
        3,
        EvidenceValue("冬期", EvidenceLevel.CONFIRMED_OFFICIAL, QUICK_REFERENCE_GUIDE_TIME_PAGE),
        EvidenceValue(
            ("weekday", "weekday", "weekday", "holiday"),
            EvidenceLevel.CONFIRMED_OFFICIAL,
            QUICK_REFERENCE_GUIDE_TIME_PAGE,
        ),
    ),
    AnnualCalendarMonthEntry(
        4,
        EvidenceValue("冬期", EvidenceLevel.CONFIRMED_OFFICIAL, QUICK_REFERENCE_GUIDE_TIME_PAGE),
        EvidenceValue(
            ("weekday", "weekday", "weekday", "holiday"),
            EvidenceLevel.CONFIRMED_OFFICIAL,
            QUICK_REFERENCE_GUIDE_TIME_PAGE,
        ),
    ),
    AnnualCalendarMonthEntry(
        5,
        EvidenceValue("冬期", EvidenceLevel.CONFIRMED_OFFICIAL, QUICK_REFERENCE_GUIDE_TIME_PAGE),
        EvidenceValue(
            ("holiday", "holiday", "weekday", "holiday"),
            EvidenceLevel.CONFIRMED_OFFICIAL,
            QUICK_REFERENCE_GUIDE_TIME_PAGE,
        ),
    ),
    AnnualCalendarMonthEntry(
        6,
        EvidenceValue("夏期", EvidenceLevel.CONFIRMED_OFFICIAL, QUICK_REFERENCE_GUIDE_TIME_PAGE),
        EvidenceValue(
            ("weekday", "weekday", "weekday", "holiday"),
            EvidenceLevel.CONFIRMED_OFFICIAL,
            QUICK_REFERENCE_GUIDE_TIME_PAGE,
        ),
    ),
    AnnualCalendarMonthEntry(
        7,
        EvidenceValue("夏期", EvidenceLevel.CONFIRMED_OFFICIAL, QUICK_REFERENCE_GUIDE_TIME_PAGE),
        EvidenceValue(
            ("weekday", "weekday", "weekday", "holiday"),
            EvidenceLevel.CONFIRMED_OFFICIAL,
            QUICK_REFERENCE_GUIDE_TIME_PAGE,
        ),
    ),
    AnnualCalendarMonthEntry(
        8,
        EvidenceValue("夏期", EvidenceLevel.CONFIRMED_OFFICIAL, QUICK_REFERENCE_GUIDE_TIME_PAGE),
        EvidenceValue(
            ("weekday", "holiday", "weekday", "holiday"),
            EvidenceLevel.CONFIRMED_OFFICIAL,
            QUICK_REFERENCE_GUIDE_TIME_PAGE,
        ),
    ),
    AnnualCalendarMonthEntry(
        9,
        EvidenceValue("夏期", EvidenceLevel.CONFIRMED_OFFICIAL, QUICK_REFERENCE_GUIDE_TIME_PAGE),
        EvidenceValue(
            ("weekday", "weekday", "weekday", "holiday"),
            EvidenceLevel.CONFIRMED_OFFICIAL,
            QUICK_REFERENCE_GUIDE_TIME_PAGE,
        ),
    ),
    AnnualCalendarMonthEntry(
        10,
        EvidenceValue("夏期", EvidenceLevel.CONFIRMED_OFFICIAL, QUICK_REFERENCE_GUIDE_TIME_PAGE),
        EvidenceValue(
            ("weekday", "weekday", "weekday", "holiday"),
            EvidenceLevel.CONFIRMED_OFFICIAL,
            QUICK_REFERENCE_GUIDE_TIME_PAGE,
        ),
    ),
    AnnualCalendarMonthEntry(
        11,
        EvidenceValue("夏期", EvidenceLevel.CONFIRMED_OFFICIAL, QUICK_REFERENCE_GUIDE_TIME_PAGE),
        EvidenceValue(
            ("weekday", "weekday", "weekday", "holiday"),
            EvidenceLevel.CONFIRMED_OFFICIAL,
            QUICK_REFERENCE_GUIDE_TIME_PAGE,
        ),
    ),
    AnnualCalendarMonthEntry(
        12,
        EvidenceValue("冬期", EvidenceLevel.CONFIRMED_OFFICIAL, QUICK_REFERENCE_GUIDE_TIME_PAGE),
        EvidenceValue(
            ("weekday", "weekday", "holiday", "holiday"),
            EvidenceLevel.CONFIRMED_OFFICIAL,
            QUICK_REFERENCE_GUIDE_TIME_PAGE,
        ),
    ),
)

# 天候のパーセンテージ設定 table (書籍頁3): monthly percentage weights for 5
# weather categories. CONFIRMED_OFFICIAL; every row sums to exactly 100. This
# supersedes `remake_customer_share.BAD_WEATHER_VALUES`'s old comment, which
# mis-cited this same table's column headers as "快晴/大雨/雪/台風/荒天" --
# 大雨/雪 are not their own columns, they are two of the four conditions the
# table's own parenthetical bundles into 荒天 ("荒天=大雨・雷雨・台風・大雪");
# see decision 0132.
MONTHLY_WEATHER_PERCENTAGES: tuple[MonthlyWeatherPercentagesEntry, ...] = (
    MonthlyWeatherPercentagesEntry(
        1,
        EvidenceValue(30, EvidenceLevel.CONFIRMED_OFFICIAL, QUICK_REFERENCE_GUIDE_TIME_PAGE),
        EvidenceValue(30, EvidenceLevel.CONFIRMED_OFFICIAL, QUICK_REFERENCE_GUIDE_TIME_PAGE),
        EvidenceValue(20, EvidenceLevel.CONFIRMED_OFFICIAL, QUICK_REFERENCE_GUIDE_TIME_PAGE),
        EvidenceValue(15, EvidenceLevel.CONFIRMED_OFFICIAL, QUICK_REFERENCE_GUIDE_TIME_PAGE),
        EvidenceValue(5, EvidenceLevel.CONFIRMED_OFFICIAL, QUICK_REFERENCE_GUIDE_TIME_PAGE),
    ),
    MonthlyWeatherPercentagesEntry(
        2,
        EvidenceValue(30, EvidenceLevel.CONFIRMED_OFFICIAL, QUICK_REFERENCE_GUIDE_TIME_PAGE),
        EvidenceValue(30, EvidenceLevel.CONFIRMED_OFFICIAL, QUICK_REFERENCE_GUIDE_TIME_PAGE),
        EvidenceValue(10, EvidenceLevel.CONFIRMED_OFFICIAL, QUICK_REFERENCE_GUIDE_TIME_PAGE),
        EvidenceValue(20, EvidenceLevel.CONFIRMED_OFFICIAL, QUICK_REFERENCE_GUIDE_TIME_PAGE),
        EvidenceValue(10, EvidenceLevel.CONFIRMED_OFFICIAL, QUICK_REFERENCE_GUIDE_TIME_PAGE),
    ),
    MonthlyWeatherPercentagesEntry(
        3,
        EvidenceValue(30, EvidenceLevel.CONFIRMED_OFFICIAL, QUICK_REFERENCE_GUIDE_TIME_PAGE),
        EvidenceValue(30, EvidenceLevel.CONFIRMED_OFFICIAL, QUICK_REFERENCE_GUIDE_TIME_PAGE),
        EvidenceValue(20, EvidenceLevel.CONFIRMED_OFFICIAL, QUICK_REFERENCE_GUIDE_TIME_PAGE),
        EvidenceValue(15, EvidenceLevel.CONFIRMED_OFFICIAL, QUICK_REFERENCE_GUIDE_TIME_PAGE),
        EvidenceValue(5, EvidenceLevel.CONFIRMED_OFFICIAL, QUICK_REFERENCE_GUIDE_TIME_PAGE),
    ),
    MonthlyWeatherPercentagesEntry(
        4,
        EvidenceValue(30, EvidenceLevel.CONFIRMED_OFFICIAL, QUICK_REFERENCE_GUIDE_TIME_PAGE),
        EvidenceValue(30, EvidenceLevel.CONFIRMED_OFFICIAL, QUICK_REFERENCE_GUIDE_TIME_PAGE),
        EvidenceValue(20, EvidenceLevel.CONFIRMED_OFFICIAL, QUICK_REFERENCE_GUIDE_TIME_PAGE),
        EvidenceValue(15, EvidenceLevel.CONFIRMED_OFFICIAL, QUICK_REFERENCE_GUIDE_TIME_PAGE),
        EvidenceValue(5, EvidenceLevel.CONFIRMED_OFFICIAL, QUICK_REFERENCE_GUIDE_TIME_PAGE),
    ),
    MonthlyWeatherPercentagesEntry(
        5,
        EvidenceValue(40, EvidenceLevel.CONFIRMED_OFFICIAL, QUICK_REFERENCE_GUIDE_TIME_PAGE),
        EvidenceValue(30, EvidenceLevel.CONFIRMED_OFFICIAL, QUICK_REFERENCE_GUIDE_TIME_PAGE),
        EvidenceValue(10, EvidenceLevel.CONFIRMED_OFFICIAL, QUICK_REFERENCE_GUIDE_TIME_PAGE),
        EvidenceValue(15, EvidenceLevel.CONFIRMED_OFFICIAL, QUICK_REFERENCE_GUIDE_TIME_PAGE),
        EvidenceValue(5, EvidenceLevel.CONFIRMED_OFFICIAL, QUICK_REFERENCE_GUIDE_TIME_PAGE),
    ),
    MonthlyWeatherPercentagesEntry(
        6,
        EvidenceValue(1, EvidenceLevel.CONFIRMED_OFFICIAL, QUICK_REFERENCE_GUIDE_TIME_PAGE),
        EvidenceValue(9, EvidenceLevel.CONFIRMED_OFFICIAL, QUICK_REFERENCE_GUIDE_TIME_PAGE),
        EvidenceValue(30, EvidenceLevel.CONFIRMED_OFFICIAL, QUICK_REFERENCE_GUIDE_TIME_PAGE),
        EvidenceValue(50, EvidenceLevel.CONFIRMED_OFFICIAL, QUICK_REFERENCE_GUIDE_TIME_PAGE),
        EvidenceValue(10, EvidenceLevel.CONFIRMED_OFFICIAL, QUICK_REFERENCE_GUIDE_TIME_PAGE),
    ),
    MonthlyWeatherPercentagesEntry(
        7,
        EvidenceValue(20, EvidenceLevel.CONFIRMED_OFFICIAL, QUICK_REFERENCE_GUIDE_TIME_PAGE),
        EvidenceValue(20, EvidenceLevel.CONFIRMED_OFFICIAL, QUICK_REFERENCE_GUIDE_TIME_PAGE),
        EvidenceValue(30, EvidenceLevel.CONFIRMED_OFFICIAL, QUICK_REFERENCE_GUIDE_TIME_PAGE),
        EvidenceValue(20, EvidenceLevel.CONFIRMED_OFFICIAL, QUICK_REFERENCE_GUIDE_TIME_PAGE),
        EvidenceValue(10, EvidenceLevel.CONFIRMED_OFFICIAL, QUICK_REFERENCE_GUIDE_TIME_PAGE),
    ),
    MonthlyWeatherPercentagesEntry(
        8,
        EvidenceValue(30, EvidenceLevel.CONFIRMED_OFFICIAL, QUICK_REFERENCE_GUIDE_TIME_PAGE),
        EvidenceValue(30, EvidenceLevel.CONFIRMED_OFFICIAL, QUICK_REFERENCE_GUIDE_TIME_PAGE),
        EvidenceValue(20, EvidenceLevel.CONFIRMED_OFFICIAL, QUICK_REFERENCE_GUIDE_TIME_PAGE),
        EvidenceValue(10, EvidenceLevel.CONFIRMED_OFFICIAL, QUICK_REFERENCE_GUIDE_TIME_PAGE),
        EvidenceValue(10, EvidenceLevel.CONFIRMED_OFFICIAL, QUICK_REFERENCE_GUIDE_TIME_PAGE),
    ),
    MonthlyWeatherPercentagesEntry(
        9,
        EvidenceValue(20, EvidenceLevel.CONFIRMED_OFFICIAL, QUICK_REFERENCE_GUIDE_TIME_PAGE),
        EvidenceValue(30, EvidenceLevel.CONFIRMED_OFFICIAL, QUICK_REFERENCE_GUIDE_TIME_PAGE),
        EvidenceValue(20, EvidenceLevel.CONFIRMED_OFFICIAL, QUICK_REFERENCE_GUIDE_TIME_PAGE),
        EvidenceValue(10, EvidenceLevel.CONFIRMED_OFFICIAL, QUICK_REFERENCE_GUIDE_TIME_PAGE),
        EvidenceValue(20, EvidenceLevel.CONFIRMED_OFFICIAL, QUICK_REFERENCE_GUIDE_TIME_PAGE),
    ),
    MonthlyWeatherPercentagesEntry(
        10,
        EvidenceValue(40, EvidenceLevel.CONFIRMED_OFFICIAL, QUICK_REFERENCE_GUIDE_TIME_PAGE),
        EvidenceValue(30, EvidenceLevel.CONFIRMED_OFFICIAL, QUICK_REFERENCE_GUIDE_TIME_PAGE),
        EvidenceValue(10, EvidenceLevel.CONFIRMED_OFFICIAL, QUICK_REFERENCE_GUIDE_TIME_PAGE),
        EvidenceValue(10, EvidenceLevel.CONFIRMED_OFFICIAL, QUICK_REFERENCE_GUIDE_TIME_PAGE),
        EvidenceValue(10, EvidenceLevel.CONFIRMED_OFFICIAL, QUICK_REFERENCE_GUIDE_TIME_PAGE),
    ),
    MonthlyWeatherPercentagesEntry(
        11,
        EvidenceValue(40, EvidenceLevel.CONFIRMED_OFFICIAL, QUICK_REFERENCE_GUIDE_TIME_PAGE),
        EvidenceValue(30, EvidenceLevel.CONFIRMED_OFFICIAL, QUICK_REFERENCE_GUIDE_TIME_PAGE),
        EvidenceValue(10, EvidenceLevel.CONFIRMED_OFFICIAL, QUICK_REFERENCE_GUIDE_TIME_PAGE),
        EvidenceValue(15, EvidenceLevel.CONFIRMED_OFFICIAL, QUICK_REFERENCE_GUIDE_TIME_PAGE),
        EvidenceValue(5, EvidenceLevel.CONFIRMED_OFFICIAL, QUICK_REFERENCE_GUIDE_TIME_PAGE),
    ),
    MonthlyWeatherPercentagesEntry(
        12,
        EvidenceValue(30, EvidenceLevel.CONFIRMED_OFFICIAL, QUICK_REFERENCE_GUIDE_TIME_PAGE),
        EvidenceValue(30, EvidenceLevel.CONFIRMED_OFFICIAL, QUICK_REFERENCE_GUIDE_TIME_PAGE),
        EvidenceValue(20, EvidenceLevel.CONFIRMED_OFFICIAL, QUICK_REFERENCE_GUIDE_TIME_PAGE),
        EvidenceValue(15, EvidenceLevel.CONFIRMED_OFFICIAL, QUICK_REFERENCE_GUIDE_TIME_PAGE),
        EvidenceValue(5, EvidenceLevel.CONFIRMED_OFFICIAL, QUICK_REFERENCE_GUIDE_TIME_PAGE),
    ),
)

QUICK_REFERENCE_GUIDE_HOURS_DIAGRAM = QUICK_REFERENCE_GUIDE_TIME_PAGE.replace(
    "\"時間\" section (book page 2-3)", "\"時間\" section, hours clock diagram (book page 2)"
)

# 5 numbered fixed-hours presets, plus 24h/temporary-closure, from the quick
# reference guide's clock diagram (書籍頁2). CONFIRMED_OFFICIAL; `printed_label`
# is transcribed verbatim including preset 3's own internal inconsistency
# (11:00~2:00 is 15 hours, printed labeled "16時間営業") -- see
# BusinessHoursPresetEntry's docstring and decision 0132. No caller consumes
# this table yet (`operating_time.OperatingHours` remains free-form); this is
# reference data only, the same "hold it even though nothing consumes it yet"
# pattern already used for `StoreVariant.total_area_tiles` etc. (task #57).
BUSINESS_HOURS_PRESETS: tuple[BusinessHoursPresetEntry, ...] = (
    BusinessHoursPresetEntry(
        1,
        EvidenceValue("AM10:00~PM6:00", EvidenceLevel.CONFIRMED_OFFICIAL, QUICK_REFERENCE_GUIDE_HOURS_DIAGRAM),
        EvidenceValue("8時間営業", EvidenceLevel.CONFIRMED_OFFICIAL, QUICK_REFERENCE_GUIDE_HOURS_DIAGRAM),
        EvidenceValue(
            OperatingHours.from_hm(10, 0, 18, 0),
            EvidenceLevel.CONFIRMED_OFFICIAL,
            QUICK_REFERENCE_GUIDE_HOURS_DIAGRAM,
        ),
    ),
    BusinessHoursPresetEntry(
        2,
        EvidenceValue("AM7:00~PM11:00", EvidenceLevel.CONFIRMED_OFFICIAL, QUICK_REFERENCE_GUIDE_HOURS_DIAGRAM),
        EvidenceValue("16時間営業", EvidenceLevel.CONFIRMED_OFFICIAL, QUICK_REFERENCE_GUIDE_HOURS_DIAGRAM),
        EvidenceValue(
            OperatingHours.from_hm(7, 0, 23, 0),
            EvidenceLevel.CONFIRMED_OFFICIAL,
            QUICK_REFERENCE_GUIDE_HOURS_DIAGRAM,
        ),
    ),
    BusinessHoursPresetEntry(
        3,
        EvidenceValue("AM11:00~AM2:00", EvidenceLevel.CONFIRMED_OFFICIAL, QUICK_REFERENCE_GUIDE_HOURS_DIAGRAM),
        EvidenceValue("16時間営業", EvidenceLevel.CONFIRMED_OFFICIAL, QUICK_REFERENCE_GUIDE_HOURS_DIAGRAM),
        EvidenceValue(
            OperatingHours.from_hm(11, 0, 2, 0),
            EvidenceLevel.CONFIRMED_OFFICIAL,
            QUICK_REFERENCE_GUIDE_HOURS_DIAGRAM,
        ),
    ),
    BusinessHoursPresetEntry(
        4,
        EvidenceValue("PM0:00~AM4:00", EvidenceLevel.CONFIRMED_OFFICIAL, QUICK_REFERENCE_GUIDE_HOURS_DIAGRAM),
        EvidenceValue("16時間営業", EvidenceLevel.CONFIRMED_OFFICIAL, QUICK_REFERENCE_GUIDE_HOURS_DIAGRAM),
        EvidenceValue(
            OperatingHours.from_hm(12, 0, 4, 0),
            EvidenceLevel.CONFIRMED_OFFICIAL,
            QUICK_REFERENCE_GUIDE_HOURS_DIAGRAM,
        ),
    ),
    BusinessHoursPresetEntry(
        5,
        EvidenceValue("PM7:00~AM11:00", EvidenceLevel.CONFIRMED_OFFICIAL, QUICK_REFERENCE_GUIDE_HOURS_DIAGRAM),
        EvidenceValue("16時間営業", EvidenceLevel.CONFIRMED_OFFICIAL, QUICK_REFERENCE_GUIDE_HOURS_DIAGRAM),
        EvidenceValue(
            OperatingHours.from_hm(19, 0, 11, 0),
            EvidenceLevel.CONFIRMED_OFFICIAL,
            QUICK_REFERENCE_GUIDE_HOURS_DIAGRAM,
        ),
    ),
    BusinessHoursPresetEntry(
        None,
        EvidenceValue("24時間営業", EvidenceLevel.CONFIRMED_OFFICIAL, QUICK_REFERENCE_GUIDE_HOURS_DIAGRAM),
        EvidenceValue("24時間営業", EvidenceLevel.CONFIRMED_OFFICIAL, QUICK_REFERENCE_GUIDE_HOURS_DIAGRAM),
        EvidenceValue(
            OperatingHours.twenty_four_hours(),
            EvidenceLevel.CONFIRMED_OFFICIAL,
            QUICK_REFERENCE_GUIDE_HOURS_DIAGRAM,
        ),
    ),
    BusinessHoursPresetEntry(
        None,
        EvidenceValue("臨時休業", EvidenceLevel.CONFIRMED_OFFICIAL, QUICK_REFERENCE_GUIDE_HOURS_DIAGRAM),
        EvidenceValue("臨時休業", EvidenceLevel.CONFIRMED_OFFICIAL, QUICK_REFERENCE_GUIDE_HOURS_DIAGRAM),
        None,
    ),
)


def _sg_staff_candidate(
    candidate_id: str,
    display_name_ja: str,
    *,
    age_years: int,
    hourly_wage_yen: int,
    stamina: int,
    agility: int,
    academic_background: int,
    sociability: int,
    education: int,
    service_skill: int,
    register_skill: int,
    cleaning_skill: int,
    replenishment_skill: int,
    security_skill: Optional[int] = None,
    service_skill_growth_ceiling: Optional[int] = None,
    register_skill_growth_ceiling: Optional[int] = None,
    cleaning_skill_growth_ceiling: Optional[int] = None,
    replenishment_skill_growth_ceiling: Optional[int] = None,
    security_skill_growth_ceiling: Optional[int] = None,
) -> StaffDefinition:
    """Build one named staff-candidate row from the strategy guide's roster.

    Source: docs/research/strategy-guide-full-decode-2026-09-16.md section
    "店員データ" (guide book pages 127-133). Each candidate's stamina/
    agility/academic_background/sociability come from the guide's own
    per-candidate "性格" (personality) block; academic_background is
    populated from that block's "賢さ" stat, which the guide's earlier
    résumé-mapping page (体力/学歴/敏捷性/社交性) treats as the same
    "学歴" concept under a different label in this table's header.
    `salary_yen_per_day_24h` is derived as hourly_wage_yen * 24, following
    the guide's own stated payroll formula (labor cost = hourly wage *
    hours worked) rather than being printed directly; the derivation is
    noted on the value itself. `security_skill` is left `None` on the one
    candidate (丸山昭夫) whose printed initial value could not be read with
    confidence from the scan, rather than guessed.

    `*_skill_growth_ceiling` is the guide's own "能力の分岐ポイント" value per
    skill, from the same per-candidate card as the initial skill values
    (large-font individual cards, not the smaller consolidated DATA LIST
    table). Every one of the 34 candidates with a confirmed initial skill
    set was cross-checked digit-for-digit against the already-transcribed
    initial values above before this pass trusted the ceiling column;
    all 34 matched exactly. 丸山昭夫's ceiling values are included even
    though his initial security_skill remains unconfirmed, since the two
    are read from separate, independently legible cells.
    """

    evidence = EvidenceLevel.CONFIRMED_OFFICIAL
    return StaffDefinition(
        candidate_id,
        display_name=EvidenceValue(display_name_ja, evidence, STRATEGY_GUIDE),
        starting_age_years=EvidenceValue(age_years, evidence, STRATEGY_GUIDE),
        salary_yen_per_day_24h=EvidenceValue(
            hourly_wage_yen * 24,
            evidence,
            STRATEGY_GUIDE,
            f"Derived as the guide's printed hourly_wage_yen ({hourly_wage_yen}) * 24h, "
            "following the guide's own payroll formula (labor cost = hourly wage * hours worked).",
        ),
        stamina=EvidenceValue(stamina, evidence, STRATEGY_GUIDE),
        academic_background=EvidenceValue(academic_background, evidence, STRATEGY_GUIDE),
        agility=EvidenceValue(agility, evidence, STRATEGY_GUIDE),
        sociability=EvidenceValue(sociability, evidence, STRATEGY_GUIDE),
        education=EvidenceValue(education, evidence, STRATEGY_GUIDE),
        register_skill=EvidenceValue(register_skill, evidence, STRATEGY_GUIDE),
        replenishment_skill=EvidenceValue(replenishment_skill, evidence, STRATEGY_GUIDE),
        security_skill=(
            EvidenceValue(security_skill, evidence, STRATEGY_GUIDE)
            if security_skill is not None
            else None
        ),
        cleaning_skill=EvidenceValue(cleaning_skill, evidence, STRATEGY_GUIDE),
        service_skill=EvidenceValue(service_skill, evidence, STRATEGY_GUIDE),
        service_skill_growth_ceiling=(
            EvidenceValue(service_skill_growth_ceiling, evidence, STRATEGY_GUIDE)
            if service_skill_growth_ceiling is not None
            else None
        ),
        register_skill_growth_ceiling=(
            EvidenceValue(register_skill_growth_ceiling, evidence, STRATEGY_GUIDE)
            if register_skill_growth_ceiling is not None
            else None
        ),
        cleaning_skill_growth_ceiling=(
            EvidenceValue(cleaning_skill_growth_ceiling, evidence, STRATEGY_GUIDE)
            if cleaning_skill_growth_ceiling is not None
            else None
        ),
        replenishment_skill_growth_ceiling=(
            EvidenceValue(replenishment_skill_growth_ceiling, evidence, STRATEGY_GUIDE)
            if replenishment_skill_growth_ceiling is not None
            else None
        ),
        security_skill_growth_ceiling=(
            EvidenceValue(security_skill_growth_ceiling, evidence, STRATEGY_GUIDE)
            if security_skill_growth_ceiling is not None
            else None
        ),
    )


# Full named staff-candidate roster (35 people) transcribed directly from
# the strategy guide's primary page scans (book pages 127-133). No prior
# StaffDefinition rows existed in this file.
#
# RESOLVED (2026-09-19): komiya_chiaki's security_skill_growth_ceiling was
# transcribed as 41 (matching register_skill_growth_ceiling/
# replenishment_skill_growth_ceiling's own 41s on the same card, an easy
# adjacent-cell misread), but a direct re-read of the source card (book
# page 127) confirms the printed value is 44 (matching service_skill_
# growth_ceiling/cleaning_skill_growth_ceiling's own 44s instead). Fixed
# below; see docs/decisions for the task that made this correction.
STAFF_CANDIDATES: tuple[StaffDefinition, ...] = (
    _sg_staff_candidate("takenaka_sayuri", "竹中小百合", age_years=28, hourly_wage_yen=280, stamina=80, agility=65, academic_background=90, sociability=90, education=90, service_skill=14, register_skill=14, cleaning_skill=14, replenishment_skill=12, security_skill=14, service_skill_growth_ceiling=54, register_skill_growth_ceiling=52, cleaning_skill_growth_ceiling=52, replenishment_skill_growth_ceiling=48, security_skill_growth_ceiling=51),
    _sg_staff_candidate("yoshida_yuki", "吉田有紀", age_years=24, hourly_wage_yen=270, stamina=60, agility=80, academic_background=65, sociability=80, education=65, service_skill=11, register_skill=10, cleaning_skill=11, replenishment_skill=11, security_skill=10, service_skill_growth_ceiling=44, register_skill_growth_ceiling=45, cleaning_skill_growth_ceiling=41, replenishment_skill_growth_ceiling=40, security_skill_growth_ceiling=38),
    _sg_staff_candidate("komiya_chiaki", "小宮千明", age_years=30, hourly_wage_yen=280, stamina=70, agility=70, academic_background=70, sociability=75, education=70, service_skill=13, register_skill=13, cleaning_skill=13, replenishment_skill=13, security_skill=13, service_skill_growth_ceiling=44, register_skill_growth_ceiling=41, cleaning_skill_growth_ceiling=44, replenishment_skill_growth_ceiling=41, security_skill_growth_ceiling=44),
    _sg_staff_candidate("hamada_yuko", "浜田夕子", age_years=22, hourly_wage_yen=270, stamina=65, agility=70, academic_background=55, sociability=50, education=55, service_skill=10, register_skill=11, cleaning_skill=9, replenishment_skill=9, security_skill=9, service_skill_growth_ceiling=33, register_skill_growth_ceiling=44, cleaning_skill_growth_ceiling=40, replenishment_skill_growth_ceiling=25, security_skill_growth_ceiling=27),
    _sg_staff_candidate("manda_machiko", "万田町子", age_years=42, hourly_wage_yen=320, stamina=70, agility=65, academic_background=60, sociability=65, education=65, service_skill=17, register_skill=20, cleaning_skill=17, replenishment_skill=17, security_skill=18, service_skill_growth_ceiling=41, register_skill_growth_ceiling=55, cleaning_skill_growth_ceiling=36, replenishment_skill_growth_ceiling=35, security_skill_growth_ceiling=42),
    _sg_staff_candidate("tominaga_fukuko", "富永福子", age_years=58, hourly_wage_yen=320, stamina=40, agility=40, academic_background=70, sociability=70, education=70, service_skill=19, register_skill=20, cleaning_skill=20, replenishment_skill=16, security_skill=18, service_skill_growth_ceiling=36, register_skill_growth_ceiling=40, cleaning_skill_growth_ceiling=40, replenishment_skill_growth_ceiling=32, security_skill_growth_ceiling=34),
    _sg_staff_candidate("shinoda_nobuko", "忍田信子", age_years=39, hourly_wage_yen=320, stamina=60, agility=70, academic_background=70, sociability=85, education=70, service_skill=18, register_skill=16, cleaning_skill=18, replenishment_skill=15, security_skill=16, service_skill_growth_ceiling=38, register_skill_growth_ceiling=42, cleaning_skill_growth_ceiling=38, replenishment_skill_growth_ceiling=42, security_skill_growth_ceiling=38),
    _sg_staff_candidate("ichikawa_chieko", "市川智恵子", age_years=35, hourly_wage_yen=300, stamina=75, agility=55, academic_background=70, sociability=75, education=70, service_skill=16, register_skill=16, cleaning_skill=16, replenishment_skill=15, security_skill=16, service_skill_growth_ceiling=41, register_skill_growth_ceiling=43, cleaning_skill_growth_ceiling=39, replenishment_skill_growth_ceiling=37, security_skill_growth_ceiling=37),
    _sg_staff_candidate("sugimura_machiko", "杉村真知子", age_years=32, hourly_wage_yen=300, stamina=70, agility=75, academic_background=85, sociability=95, education=85, service_skill=15, register_skill=14, cleaning_skill=15, replenishment_skill=13, security_skill=14, service_skill_growth_ceiling=65, register_skill_growth_ceiling=58, cleaning_skill_growth_ceiling=60, replenishment_skill_growth_ceiling=52, security_skill_growth_ceiling=50),
    _sg_staff_candidate("tanaka_sachiko", "田中幸子", age_years=44, hourly_wage_yen=330, stamina=75, agility=75, academic_background=80, sociability=85, education=80, service_skill=19, register_skill=18, cleaning_skill=19, replenishment_skill=18, security_skill=18, service_skill_growth_ceiling=48, register_skill_growth_ceiling=46, cleaning_skill_growth_ceiling=48, replenishment_skill_growth_ceiling=46, security_skill_growth_ceiling=46),
    _sg_staff_candidate("hanazawa_sakie", "花沢咲江", age_years=46, hourly_wage_yen=330, stamina=60, agility=60, academic_background=55, sociability=65, education=55, service_skill=18, register_skill=19, cleaning_skill=18, replenishment_skill=17, security_skill=18, service_skill_growth_ceiling=36, register_skill_growth_ceiling=38, cleaning_skill_growth_ceiling=36, replenishment_skill_growth_ceiling=34, security_skill_growth_ceiling=36),
    _sg_staff_candidate("satonaka_ryoko", "里中涼子", age_years=18, hourly_wage_yen=270, stamina=65, agility=80, academic_background=80, sociability=90, education=80, service_skill=9, register_skill=9, cleaning_skill=9, replenishment_skill=8, security_skill=9, service_skill_growth_ceiling=65, register_skill_growth_ceiling=60, cleaning_skill_growth_ceiling=65, replenishment_skill_growth_ceiling=55, security_skill_growth_ceiling=55),
    _sg_staff_candidate("yamamoto_nobuo", "山本信夫", age_years=31, hourly_wage_yen=290, stamina=95, agility=75, academic_background=60, sociability=75, education=60, service_skill=13, register_skill=13, cleaning_skill=13, replenishment_skill=16, security_skill=14, service_skill_growth_ceiling=40, register_skill_growth_ceiling=39, cleaning_skill_growth_ceiling=41, replenishment_skill_growth_ceiling=55, security_skill_growth_ceiling=52),
    _sg_staff_candidate("yamashita_daisuke", "山下大介", age_years=16, hourly_wage_yen=250, stamina=55, agility=70, academic_background=50, sociability=55, education=50, service_skill=8, register_skill=8, cleaning_skill=8, replenishment_skill=10, security_skill=8, service_skill_growth_ceiling=36, register_skill_growth_ceiling=36, cleaning_skill_growth_ceiling=36, replenishment_skill_growth_ceiling=39, security_skill_growth_ceiling=49),
    _sg_staff_candidate("sugimoto_saburo", "杉本三郎", age_years=36, hourly_wage_yen=300, stamina=70, agility=75, academic_background=55, sociability=65, education=55, service_skill=15, register_skill=16, cleaning_skill=15, replenishment_skill=16, security_skill=16, service_skill_growth_ceiling=40, register_skill_growth_ceiling=43, cleaning_skill_growth_ceiling=41, replenishment_skill_growth_ceiling=45, security_skill_growth_ceiling=43),
    _sg_staff_candidate("amenaka_seijin", "雨中聖人", age_years=22, hourly_wage_yen=270, stamina=40, agility=100, academic_background=40, sociability=50, education=40, service_skill=8, register_skill=13, cleaning_skill=8, replenishment_skill=8, security_skill=8, service_skill_growth_ceiling=50, register_skill_growth_ceiling=90, cleaning_skill_growth_ceiling=50, replenishment_skill_growth_ceiling=80, security_skill_growth_ceiling=30),
    _sg_staff_candidate("akimoto_sanshiro", "秋本三四郎", age_years=28, hourly_wage_yen=280, stamina=70, agility=75, academic_background=70, sociability=60, education=70, service_skill=10, register_skill=12, cleaning_skill=10, replenishment_skill=13, security_skill=11, service_skill_growth_ceiling=32, register_skill_growth_ceiling=36, cleaning_skill_growth_ceiling=34, replenishment_skill_growth_ceiling=39, security_skill_growth_ceiling=35),
    _sg_staff_candidate("sasaki_nobuo", "佐々木信雄", age_years=20, hourly_wage_yen=270, stamina=87, agility=75, academic_background=70, sociability=70, education=70, service_skill=9, register_skill=9, cleaning_skill=9, replenishment_skill=12, security_skill=9, service_skill_growth_ceiling=34, register_skill_growth_ceiling=36, cleaning_skill_growth_ceiling=35, replenishment_skill_growth_ceiling=42, security_skill_growth_ceiling=38),
    _sg_staff_candidate("moriyama_yukinojo", "森山雪之丈", age_years=26, hourly_wage_yen=280, stamina=80, agility=70, academic_background=80, sociability=75, education=80, service_skill=12, register_skill=13, cleaning_skill=12, replenishment_skill=12, security_skill=12, service_skill_growth_ceiling=42, register_skill_growth_ceiling=43, cleaning_skill_growth_ceiling=43, replenishment_skill_growth_ceiling=39, security_skill_growth_ceiling=40),
    _sg_staff_candidate("nishida_toshio", "西田年男", age_years=53, hourly_wage_yen=340, stamina=60, agility=65, academic_background=75, sociability=75, education=75, service_skill=18, register_skill=18, cleaning_skill=18, replenishment_skill=16, security_skill=19, service_skill_growth_ceiling=36, register_skill_growth_ceiling=36, cleaning_skill_growth_ceiling=38, replenishment_skill_growth_ceiling=34, security_skill_growth_ceiling=40),
    _sg_staff_candidate("minamida_yoji", "南田洋次", age_years=40, hourly_wage_yen=310, stamina=75, agility=75, academic_background=75, sociability=75, education=75, service_skill=17, register_skill=18, cleaning_skill=18, replenishment_skill=18, security_skill=18, service_skill_growth_ceiling=38, register_skill_growth_ceiling=40, cleaning_skill_growth_ceiling=40, replenishment_skill_growth_ceiling=40, security_skill_growth_ceiling=42),
    _sg_staff_candidate("taniguchi_akira", "谷口明", age_years=26, hourly_wage_yen=280, stamina=75, agility=60, academic_background=60, sociability=60, education=60, service_skill=11, register_skill=11, cleaning_skill=11, replenishment_skill=13, security_skill=12, service_skill_growth_ceiling=33, register_skill_growth_ceiling=33, cleaning_skill_growth_ceiling=33, replenishment_skill_growth_ceiling=39, security_skill_growth_ceiling=36),
    _sg_staff_candidate("nagasawa_tatsuya", "長沢達也", age_years=34, hourly_wage_yen=310, stamina=85, agility=75, academic_background=80, sociability=75, education=80, service_skill=15, register_skill=16, cleaning_skill=15, replenishment_skill=16, security_skill=17, service_skill_growth_ceiling=51, register_skill_growth_ceiling=55, cleaning_skill_growth_ceiling=54, replenishment_skill_growth_ceiling=65, security_skill_growth_ceiling=61),
    _sg_staff_candidate("konno_kyosuke", "今野京介", age_years=21, hourly_wage_yen=280, stamina=80, agility=70, academic_background=85, sociability=75, education=85, service_skill=10, register_skill=10, cleaning_skill=10, replenishment_skill=10, security_skill=10, service_skill_growth_ceiling=45, register_skill_growth_ceiling=48, cleaning_skill_growth_ceiling=47, replenishment_skill_growth_ceiling=52, security_skill_growth_ceiling=48),
    _sg_staff_candidate("maruyama_akio", "丸山昭夫", age_years=28, hourly_wage_yen=280, stamina=90, agility=70, academic_background=75, sociability=65, education=75, service_skill=10, register_skill=11, cleaning_skill=11, replenishment_skill=14, security_skill=None, service_skill_growth_ceiling=32, register_skill_growth_ceiling=35, cleaning_skill_growth_ceiling=34, replenishment_skill_growth_ceiling=55, security_skill_growth_ceiling=50),
    _sg_staff_candidate("fukumoto_takahito", "福本孝仁", age_years=32, hourly_wage_yen=310, stamina=75, agility=75, academic_background=95, sociability=80, education=95, service_skill=13, register_skill=16, cleaning_skill=13, replenishment_skill=13, security_skill=16, service_skill_growth_ceiling=58, register_skill_growth_ceiling=68, cleaning_skill_growth_ceiling=63, replenishment_skill_growth_ceiling=62, security_skill_growth_ceiling=63),
    _sg_staff_candidate("oda_nobuyuki", "小田伸行", age_years=27, hourly_wage_yen=280, stamina=75, agility=75, academic_background=65, sociability=65, education=65, service_skill=11, register_skill=12, cleaning_skill=11, replenishment_skill=13, security_skill=12, service_skill_growth_ceiling=33, register_skill_growth_ceiling=36, cleaning_skill_growth_ceiling=34, replenishment_skill_growth_ceiling=40, security_skill_growth_ceiling=37),
    _sg_staff_candidate("ikegami_hideo", "池上秀夫", age_years=25, hourly_wage_yen=270, stamina=70, agility=70, academic_background=75, sociability=50, education=60, service_skill=11, register_skill=12, cleaning_skill=11, replenishment_skill=12, security_skill=10, service_skill_growth_ceiling=32, register_skill_growth_ceiling=36, cleaning_skill_growth_ceiling=32, replenishment_skill_growth_ceiling=40, security_skill_growth_ceiling=38),
    _sg_staff_candidate("kaneda_tetsuya", "金田哲也", age_years=36, hourly_wage_yen=330, stamina=75, agility=75, academic_background=85, sociability=80, education=85, service_skill=16, register_skill=17, cleaning_skill=16, replenishment_skill=16, security_skill=16, service_skill_growth_ceiling=48, register_skill_growth_ceiling=54, cleaning_skill_growth_ceiling=48, replenishment_skill_growth_ceiling=51, security_skill_growth_ceiling=50),
    _sg_staff_candidate("sugawara_fumio", "菅原文夫", age_years=42, hourly_wage_yen=330, stamina=85, agility=85, academic_background=85, sociability=70, education=85, service_skill=17, register_skill=18, cleaning_skill=17, replenishment_skill=20, security_skill=20, service_skill_growth_ceiling=35, register_skill_growth_ceiling=35, cleaning_skill_growth_ceiling=35, replenishment_skill_growth_ceiling=42, security_skill_growth_ceiling=50),
    _sg_staff_candidate("takahashi_daisuke", "高橋大介", age_years=24, hourly_wage_yen=280, stamina=75, agility=70, academic_background=75, sociability=75, education=75, service_skill=11, register_skill=11, cleaning_skill=11, replenishment_skill=11, security_skill=11, service_skill_growth_ceiling=40, register_skill_growth_ceiling=40, cleaning_skill_growth_ceiling=42, replenishment_skill_growth_ceiling=45, security_skill_growth_ceiling=42),
    _sg_staff_candidate("okudaira_yasuo", "奥平康夫", age_years=51, hourly_wage_yen=340, stamina=60, agility=60, academic_background=95, sociability=80, education=95, service_skill=18, register_skill=20, cleaning_skill=18, replenishment_skill=17, security_skill=19, service_skill_growth_ceiling=50, register_skill_growth_ceiling=44, cleaning_skill_growth_ceiling=50, replenishment_skill_growth_ceiling=34, security_skill_growth_ceiling=40),
    _sg_staff_candidate("nakayama_koji", "中山光次", age_years=17, hourly_wage_yen=260, stamina=80, agility=75, academic_background=80, sociability=80, education=80, service_skill=9, register_skill=9, cleaning_skill=9, replenishment_skill=8, security_skill=8, service_skill_growth_ceiling=55, register_skill_growth_ceiling=50, cleaning_skill_growth_ceiling=60, replenishment_skill_growth_ceiling=55, security_skill_growth_ceiling=60),
    _sg_staff_candidate("matoba_joji", "的場丈二", age_years=19, hourly_wage_yen=260, stamina=95, agility=60, academic_background=70, sociability=65, education=70, service_skill=8, register_skill=8, cleaning_skill=8, replenishment_skill=12, security_skill=10, service_skill_growth_ceiling=37, register_skill_growth_ceiling=37, cleaning_skill_growth_ceiling=37, replenishment_skill_growth_ceiling=65, security_skill_growth_ceiling=50),
    _sg_staff_candidate("asada_shuji", "朝田宗司", age_years=43, hourly_wage_yen=310, stamina=70, agility=60, academic_background=50, sociability=65, education=50, service_skill=16, register_skill=16, cleaning_skill=16, replenishment_skill=18, security_skill=18, service_skill_growth_ceiling=32, register_skill_growth_ceiling=32, cleaning_skill_growth_ceiling=32, replenishment_skill_growth_ceiling=36, security_skill_growth_ceiling=36),
)


def _sg_visit(
    archetype_id: str,
    visit_start_time: str,
    visit_duration_minutes: int,
    arrival_method: str,
    behavior_stats_raw: tuple[int, ...],
    budget_yen: int,
    primary_wanted_product: Optional[str],
    secondary_wanted_products: tuple[str, ...],
) -> CustomerVisitProfile:
    """Build one strategy-guide-sourced customer visit-schedule row.

    Source: docs/research/strategy-guide-full-decode-2026-09-16.md section 7
    and the primary guide scans (顧客データ table, book pages 134-143).
    """

    evidence = EvidenceLevel.CONFIRMED_OFFICIAL
    return CustomerVisitProfile(
        archetype_id,
        visit_start_time=EvidenceValue(visit_start_time, evidence, STRATEGY_GUIDE),
        visit_duration_minutes=EvidenceValue(visit_duration_minutes, evidence, STRATEGY_GUIDE),
        arrival_method=EvidenceValue(arrival_method, evidence, STRATEGY_GUIDE),
        behavior_stats_raw=EvidenceValue(behavior_stats_raw, evidence, STRATEGY_GUIDE),
        budget_yen=EvidenceValue(budget_yen, evidence, STRATEGY_GUIDE),
        primary_wanted_product=(
            EvidenceValue(primary_wanted_product, evidence, STRATEGY_GUIDE)
            if primary_wanted_product is not None
            else None
        ),
        secondary_wanted_products=EvidenceValue(secondary_wanted_products, evidence, STRATEGY_GUIDE),
    )


# Customer archetype roster (21 archetypes), transcribed directly from the
# strategy guide's primary page scans (book pages 134-143). No prior
# CustomerArchetypeDefinition rows existed in this file.
CUSTOMER_ARCHETYPES: tuple[CustomerArchetypeDefinition, ...] = (
    CustomerArchetypeDefinition("female_college_student", display_name=EvidenceValue("女子大生", EvidenceLevel.CONFIRMED_OFFICIAL, STRATEGY_GUIDE), visual_archetype=EvidenceValue("18~23歳", EvidenceLevel.CONFIRMED_OFFICIAL, STRATEGY_GUIDE)),
    CustomerArchetypeDefinition("college_student", display_name=EvidenceValue("大学生", EvidenceLevel.CONFIRMED_OFFICIAL, STRATEGY_GUIDE), visual_archetype=EvidenceValue("18~23歳", EvidenceLevel.CONFIRMED_OFFICIAL, STRATEGY_GUIDE)),
    CustomerArchetypeDefinition("salaryman", display_name=EvidenceValue("サラリーマン", EvidenceLevel.CONFIRMED_OFFICIAL, STRATEGY_GUIDE), visual_archetype=EvidenceValue("25~40歳", EvidenceLevel.CONFIRMED_OFFICIAL, STRATEGY_GUIDE)),
    CustomerArchetypeDefinition("ol", display_name=EvidenceValue("OL", EvidenceLevel.CONFIRMED_OFFICIAL, STRATEGY_GUIDE), visual_archetype=EvidenceValue("20~38歳", EvidenceLevel.CONFIRMED_OFFICIAL, STRATEGY_GUIDE)),
    CustomerArchetypeDefinition("middle_aged_man", display_name=EvidenceValue("おじさん", EvidenceLevel.CONFIRMED_OFFICIAL, STRATEGY_GUIDE), visual_archetype=EvidenceValue("40~55歳", EvidenceLevel.CONFIRMED_OFFICIAL, STRATEGY_GUIDE)),
    CustomerArchetypeDefinition("middle_aged_woman", display_name=EvidenceValue("おばさん", EvidenceLevel.CONFIRMED_OFFICIAL, STRATEGY_GUIDE), visual_archetype=EvidenceValue("40~58歳", EvidenceLevel.CONFIRMED_OFFICIAL, STRATEGY_GUIDE)),
    CustomerArchetypeDefinition("elderly_man", display_name=EvidenceValue("おじいさん", EvidenceLevel.CONFIRMED_OFFICIAL, STRATEGY_GUIDE), visual_archetype=EvidenceValue("65~78歳", EvidenceLevel.CONFIRMED_OFFICIAL, STRATEGY_GUIDE)),
    CustomerArchetypeDefinition("elderly_woman", display_name=EvidenceValue("おばあさん", EvidenceLevel.CONFIRMED_OFFICIAL, STRATEGY_GUIDE), visual_archetype=EvidenceValue("65~78歳", EvidenceLevel.CONFIRMED_OFFICIAL, STRATEGY_GUIDE)),
    CustomerArchetypeDefinition("boy_elementary_student", display_name=EvidenceValue("男子小学生", EvidenceLevel.CONFIRMED_OFFICIAL, STRATEGY_GUIDE), visual_archetype=EvidenceValue("7~12歳", EvidenceLevel.CONFIRMED_OFFICIAL, STRATEGY_GUIDE)),
    CustomerArchetypeDefinition("girl_elementary_student", display_name=EvidenceValue("女子小学生", EvidenceLevel.CONFIRMED_OFFICIAL, STRATEGY_GUIDE), visual_archetype=EvidenceValue("7~12歳", EvidenceLevel.CONFIRMED_OFFICIAL, STRATEGY_GUIDE)),
    CustomerArchetypeDefinition("boy_middle_school_student", display_name=EvidenceValue("男子中学生", EvidenceLevel.CONFIRMED_OFFICIAL, STRATEGY_GUIDE), visual_archetype=EvidenceValue("13~15歳", EvidenceLevel.CONFIRMED_OFFICIAL, STRATEGY_GUIDE)),
    CustomerArchetypeDefinition("girl_middle_school_student", display_name=EvidenceValue("女子中学生", EvidenceLevel.CONFIRMED_OFFICIAL, STRATEGY_GUIDE), visual_archetype=EvidenceValue("13~15歳", EvidenceLevel.CONFIRMED_OFFICIAL, STRATEGY_GUIDE)),
    CustomerArchetypeDefinition("boy_high_school_student", display_name=EvidenceValue("男子高校生", EvidenceLevel.CONFIRMED_OFFICIAL, STRATEGY_GUIDE), visual_archetype=EvidenceValue("16~18歳", EvidenceLevel.CONFIRMED_OFFICIAL, STRATEGY_GUIDE)),
    CustomerArchetypeDefinition("girl_high_school_student", display_name=EvidenceValue("女子高校生", EvidenceLevel.CONFIRMED_OFFICIAL, STRATEGY_GUIDE), visual_archetype=EvidenceValue("16~18歳", EvidenceLevel.CONFIRMED_OFFICIAL, STRATEGY_GUIDE)),
    CustomerArchetypeDefinition("boy_kindergartner", display_name=EvidenceValue("男子幼稚園児", EvidenceLevel.CONFIRMED_OFFICIAL, STRATEGY_GUIDE), visual_archetype=EvidenceValue("4~6歳", EvidenceLevel.CONFIRMED_OFFICIAL, STRATEGY_GUIDE)),
    CustomerArchetypeDefinition("girl_kindergartner", display_name=EvidenceValue("女子幼稚園児", EvidenceLevel.CONFIRMED_OFFICIAL, STRATEGY_GUIDE), visual_archetype=EvidenceValue("4~6歳", EvidenceLevel.CONFIRMED_OFFICIAL, STRATEGY_GUIDE)),
    CustomerArchetypeDefinition("man_with_child", display_name=EvidenceValue("子供連れのおじさん", EvidenceLevel.CONFIRMED_OFFICIAL, STRATEGY_GUIDE), visual_archetype=EvidenceValue("35~38歳", EvidenceLevel.CONFIRMED_OFFICIAL, STRATEGY_GUIDE)),
    CustomerArchetypeDefinition("woman_with_child", display_name=EvidenceValue("子供連れのおばさん", EvidenceLevel.CONFIRMED_OFFICIAL, STRATEGY_GUIDE), visual_archetype=EvidenceValue("38~41歳", EvidenceLevel.CONFIRMED_OFFICIAL, STRATEGY_GUIDE)),
    CustomerArchetypeDefinition("woman_carrying_infant", display_name=EvidenceValue("子抱きのおばさん", EvidenceLevel.CONFIRMED_OFFICIAL, STRATEGY_GUIDE), visual_archetype=EvidenceValue("30~39歳", EvidenceLevel.CONFIRMED_OFFICIAL, STRATEGY_GUIDE)),
    CustomerArchetypeDefinition("man_in_wheelchair", display_name=EvidenceValue("車椅子の男性", EvidenceLevel.CONFIRMED_OFFICIAL, STRATEGY_GUIDE), visual_archetype=EvidenceValue("30~33歳", EvidenceLevel.CONFIRMED_OFFICIAL, STRATEGY_GUIDE)),
    CustomerArchetypeDefinition("man_on_crutches", display_name=EvidenceValue("松葉杖の男性", EvidenceLevel.CONFIRMED_OFFICIAL, STRATEGY_GUIDE), visual_archetype=EvidenceValue("25~28歳", EvidenceLevel.CONFIRMED_OFFICIAL, STRATEGY_GUIDE)),
)


# Per-archetype, per-visit-time schedule rows (143 rows across the 21
# archetypes above), transcribed directly from the strategy guide's primary
# page scans (book pages 134-143). This replaces an earlier transcription
# pass whose `behavior_stats_raw` tuples were unreliable (missing digits,
# 7-9 elements instead of 10) because the scan resolution then available
# could not resolve the dense per-row digit blocks with confidence (see the
# now-superseded uncertainty note this file used to carry, and
# docs/research/strategy-guide-fixture-crosscheck-2026-09-16.md). A
# subsequently supplied higher-resolution scan of the same pages renders the
# 10-column ス/素/マ/集/買/価/距/サ/平/休 header and every data row legibly
# with no ambiguity, so every row below has been re-read from that scan and
# every tuple has exactly 10 elements in the guide's own printed order.
CUSTOMER_VISIT_SCHEDULE: tuple[CustomerVisitProfile, ...] = (
    # 女子大生 (18~23歳) -- 20 rows
    _sg_visit("female_college_student", "6:00", 120, "徒歩", (50, 80, 40, 10, 30, 50, 80, 20, 100, 50), 500, "bread", ("cold_drink",)),
    _sg_visit("female_college_student", "7:00", 60, "自転車", (50, 90, 50, 10, 50, 80, 40, 20, 100, 50), 800, "bread", ("hot_drink", "snacks", "daily_goods")),
    _sg_visit("female_college_student", "6:00", 120, "徒歩", (50, 80, 40, 40, 30, 50, 80, 20, 100, 50), 1000, "bread", ("cold_drink", "snacks", "medicine")),
    _sg_visit("female_college_student", "7:00", 120, "徒歩", (50, 90, 50, 30, 30, 50, 80, 20, 100, 50), 700, "bread", ("hot_drink", "books")),
    _sg_visit("female_college_student", "11:00", 120, "徒歩", (50, 100, 60, 20, 30, 50, 60, 20, 100, 50), 800, "bread", ("cold_drink", "snacks", "copy_paper")),
    _sg_visit("female_college_student", "12:00", 60, "自転車", (50, 100, 80, 20, 30, 80, 40, 20, 100, 50), 1000, "bread", ("hot_drink", "books", "tobacco")),
    _sg_visit("female_college_student", "11:00", 120, "徒歩", (50, 100, 60, 20, 30, 50, 60, 20, 100, 50), 800, "bento", ("cold_drink", "snacks", "event_goods")),
    _sg_visit("female_college_student", "12:00", 120, "徒歩", (50, 100, 60, 30, 30, 50, 60, 20, 100, 50), 800, "bento", ("cold_drink", "ice_cream", "event_goods")),
    _sg_visit("female_college_student", "17:00", 120, "徒歩", (50, 100, 60, 40, 30, 50, 60, 20, 100, 60), 1000, "bento", ("hot_drink", "ice_cream", "copy_paper")),
    _sg_visit("female_college_student", "18:00", 60, "自転車", (60, 100, 60, 40, 50, 80, 40, 20, 100, 60), 1000, "instant_food", ("hot_drink", "snacks", "tobacco")),
    _sg_visit("female_college_student", "18:00", 120, "徒歩", (50, 100, 60, 40, 30, 50, 60, 40, 100, 60), 1500, "retort_food", ("cold_drink", "copy_paper", "stationery")),
    _sg_visit("female_college_student", "19:00", 120, "徒歩", (60, 100, 60, 80, 70, 20, 20, 20, 100, 50), 3000, "event_goods", ("snacks", "books", "stationery")),
    _sg_visit("female_college_student", "19:00", 120, "徒歩", (50, 100, 60, 50, 30, 50, 60, 40, 100, 50), 1000, "bento", ("cold_drink", "snacks", "chinese_steamed_bun")),
    _sg_visit("female_college_student", "20:00", 60, "自転車", (50, 100, 60, 50, 50, 80, 40, 20, 100, 50), 1000, "bento", ("hot_drink", "snacks", "alcohol")),
    _sg_visit("female_college_student", "20:00", 60, "徒歩", (50, 100, 60, 50, 80, 50, 40, 20, 100, 50), 3000, "copy_paper", ("cold_drink", "snacks", "ice_cream")),
    _sg_visit("female_college_student", "20:00", 60, "自動車", (50, 100, 60, 50, 90, 50, 40, 20, 100, 50), 5000, "parcel_delivery_form", ("hot_drink", "snacks", "event_goods")),
    _sg_visit("female_college_student", "20:00", 180, "徒歩", (50, 100, 60, 90, 70, 50, 60, 40, 100, 50), 1500, "snacks", ("instant_food", "ice_cream", "books")),
    _sg_visit("female_college_student", "21:00", 180, "自転車", (90, 100, 60, 10, 100, 10, 10, 10, 100, 50), 3000, "medicine", ("daily_goods",)),
    _sg_visit("female_college_student", "21:00", 120, "徒歩", (50, 80, 50, 80, 80, 50, 60, 40, 100, 50), 3000, "instant_food", ("alcohol", "tobacco", "event_goods")),
    _sg_visit("female_college_student", "17:00", 60, "自動車", (80, 80, 70, 80, 60, 20, 80, 20, 100, 50), 3000, "cold_drink", ("ice_cream", "snacks", "event_goods")),
    # 大学生 (18~23歳) -- 25 rows
    _sg_visit("college_student", "6:00", 120, "徒歩", (90, 100, 60, 10, 70, 60, 50, 10, 100, 50), 400, "bread", ("cold_drink",)),
    _sg_visit("college_student", "6:00", 120, "自転車", (90, 100, 60, 30, 80, 60, 40, 10, 100, 50), 800, "bento", ("hot_drink", "tobacco", "stationery")),
    _sg_visit("college_student", "7:00", 120, "徒歩", (90, 100, 60, 30, 80, 60, 40, 10, 100, 50), 400, "bread", ("cold_drink", "books", "stationery")),
    _sg_visit("college_student", "7:00", 120, "徒歩", (90, 100, 60, 50, 70, 60, 40, 10, 100, 50), 800, "bento", ("hot_drink", "tobacco", "copy_paper")),
    _sg_visit("college_student", "6:00", 120, "自転車", (90, 100, 40, 10, 100, 100, 10, 10, 100, 50), 500, "tobacco", ("cold_drink",)),
    _sg_visit("college_student", "11:00", 120, "徒歩", (90, 100, 60, 30, 70, 60, 50, 10, 100, 50), 400, "bread", ("cold_drink",)),
    _sg_visit("college_student", "12:00", 120, "徒歩", (90, 100, 60, 30, 70, 60, 50, 10, 100, 50), 800, "bento", ("hot_drink", "tobacco", "chinese_steamed_bun")),
    _sg_visit("college_student", "12:00", 120, "徒歩", (90, 100, 60, 30, 70, 60, 50, 10, 100, 50), 800, "bento", ("cold_drink", "chinese_steamed_bun")),
    _sg_visit("college_student", "13:00", 120, "徒歩", (90, 100, 60, 30, 70, 60, 50, 10, 100, 50), 800, "bento", ("cold_drink", "books", "copy_paper")),
    _sg_visit("college_student", "13:00", 120, "自転車", (100, 100, 40, 10, 100, 10, 10, 10, 100, 50), 500, "tobacco", ("cold_drink",)),
    _sg_visit("college_student", "17:00", 120, "徒歩", (90, 100, 60, 40, 70, 60, 50, 10, 100, 50), 1200, "bento", ("hot_drink", "books", "daily_goods")),
    _sg_visit("college_student", "18:00", 120, "徒歩", (90, 100, 60, 40, 70, 60, 50, 20, 100, 50), 1200, "retort_food", ("cold_drink", "books", "copy_paper")),
    _sg_visit("college_student", "18:00", 120, "徒歩", (90, 100, 60, 40, 70, 60, 50, 20, 100, 50), 1200, "instant_food", ("cold_drink", "copy_paper", "tobacco")),
    _sg_visit("college_student", "19:00", 120, "徒歩", (90, 100, 60, 40, 70, 60, 50, 20, 100, 50), 1200, "bento", ("alcohol", "tobacco", "oden")),
    _sg_visit("college_student", "19:00", 120, "徒歩", (90, 80, 60, 80, 80, 80, 50, 40, 100, 50), 1200, "meat", ("vegetables", "fish", "seasoning")),
    _sg_visit("college_student", "21:00", 120, "徒歩", (90, 100, 60, 50, 70, 60, 50, 20, 100, 50), 1200, "instant_food", ("hot_drink", "books", "stationery")),
    _sg_visit("college_student", "22:00", 120, "徒歩", (90, 100, 60, 60, 70, 60, 50, 10, 100, 50), 1200, "retort_food", ("chinese_steamed_bun", "hot_drink", "snacks")),
    _sg_visit("college_student", "22:00", 120, "自転車", (90, 100, 60, 90, 90, 40, 30, 10, 100, 50), 3000, "alcohol", ("oden", "snacks", "tobacco")),
    _sg_visit("college_student", "22:00", 120, "バイク", (90, 100, 60, 80, 100, 10, 20, 10, 100, 50), 2000, "tobacco", ("hot_drink", "alcohol", "chinese_steamed_bun")),
    _sg_visit("college_student", "22:00", 120, "バイク", (90, 100, 60, 80, 100, 10, 20, 10, 100, 50), 3000, "ice_cream", ("instant_food", "frozen_food", "chinese_steamed_bun")),
    _sg_visit("college_student", "23:00", 120, "徒歩", (90, 100, 60, 50, 70, 60, 50, 20, 100, 50), 1200, "fish", ("alcohol", "tobacco", "oden")),
    _sg_visit("college_student", "23:00", 180, "バイク", (90, 100, 60, 60, 90, 60, 50, 20, 100, 50), 3000, "copy_paper", ("hot_drink", "stationery", "tobacco")),
    _sg_visit("college_student", "0:00", 120, "徒歩", (90, 100, 60, 50, 70, 60, 50, 10, 100, 50), 1200, "bento", ("alcohol", "books", "oden")),
    _sg_visit("college_student", "2:00", 120, "徒歩", (60, 60, 50, 80, 90, 10, 20, 10, 100, 50), 1200, "bento", ("oden", "chinese_steamed_bun", "snacks")),
    _sg_visit("college_student", "3:00", 120, "徒歩", (90, 60, 50, 80, 100, 10, 20, 10, 100, 50), 2000, "tobacco", ("hot_drink", "alcohol", "chinese_steamed_bun")),
    # サラリーマン (25~40歳) -- 18 rows
    _sg_visit("salaryman", "5:00", 120, "徒歩", (70, 90, 90, 30, 70, 30, 60, 30, 100, 20), 1000, "bread", ("hot_drink", "stationery")),
    _sg_visit("salaryman", "6:00", 120, "徒歩", (70, 90, 90, 30, 70, 30, 60, 30, 100, 20), 800, "bread", ("cold_drink", "tobacco")),
    _sg_visit("salaryman", "7:00", 60, "徒歩", (70, 90, 90, 50, 70, 30, 60, 30, 100, 20), 1000, "bento", ("hot_drink", "books", "tobacco")),
    _sg_visit("salaryman", "8:00", 60, "自転車", (70, 90, 90, 50, 70, 30, 60, 30, 100, 20), 800, "bread", ("cold_drink", "medicine", "tobacco")),
    _sg_visit("salaryman", "12:00", 60, "徒歩", (70, 90, 90, 30, 70, 30, 60, 30, 100, 20), 1000, "bread", ("hot_drink", "tobacco")),
    _sg_visit("salaryman", "12:00", 60, "徒歩", (70, 90, 90, 30, 70, 30, 60, 30, 100, 20), 1300, "bento", ("cold_drink", "daily_goods")),
    _sg_visit("salaryman", "12:00", 60, "徒歩", (70, 90, 90, 30, 70, 30, 60, 30, 100, 20), 1000, "instant_food", ("cold_drink", "books", "chinese_steamed_bun")),
    _sg_visit("salaryman", "12:00", 60, "徒歩", (70, 90, 90, 30, 70, 30, 60, 30, 100, 20), 1500, "bento", ("cold_drink", "books")),
    _sg_visit("salaryman", "12:00", 60, "徒歩", (100, 90, 100, 60, 100, 100, 70, 30, 100, 20), 700, "tobacco", ("cold_drink", "hot_drink")),
    _sg_visit("salaryman", "19:00", 60, "徒歩", (70, 90, 90, 60, 70, 30, 60, 30, 100, 20), 2000, "bento", ("cold_drink", "medicine", "tobacco")),
    _sg_visit("salaryman", "20:00", 60, "徒歩", (70, 90, 90, 60, 70, 30, 60, 30, 100, 20), 2000, "retort_food", ("hot_drink", "alcohol", "oden")),
    _sg_visit("salaryman", "19:00", 60, "徒歩", (70, 90, 90, 60, 70, 30, 60, 30, 100, 20), 2000, "bento", ("cold_drink", "medicine", "tobacco")),
    _sg_visit("salaryman", "20:00", 120, "徒歩", (70, 90, 90, 60, 70, 30, 60, 30, 100, 20), 2000, "retort_food", ("hot_drink", "alcohol", "oden")),
    _sg_visit("salaryman", "22:00", 60, "徒歩", (70, 60, 80, 90, 90, 80, 70, 20, 100, 20), 5000, "alcohol", ("oden", "snacks", "retort_food")),
    _sg_visit("salaryman", "23:00", 60, "徒歩", (70, 80, 90, 60, 70, 30, 60, 30, 100, 20), 2500, "instant_food", ("alcohol", "instant_food", "tobacco")),
    _sg_visit("salaryman", "0:00", 60, "徒歩", (70, 80, 90, 50, 70, 30, 60, 30, 100, 20), 2500, "bento", ("hot_drink", "oden", "chinese_steamed_bun")),
    _sg_visit("salaryman", "1:00", 60, "自転車", (70, 80, 90, 50, 70, 30, 60, 30, 100, 20), 3000, "instant_food", ("alcohol", "instant_food", "tobacco")),
    _sg_visit("salaryman", "0:00", 120, "徒歩", (100, 70, 80, 70, 100, 100, 30, 10, 100, 20), 1000, "tobacco", ("hot_drink", "alcohol", "chinese_steamed_bun")),
    # OL (20~38歳) -- 18 rows
    _sg_visit("ol", "6:00", 60, "徒歩", (70, 80, 90, 30, 30, 70, 70, 40, 100, 20), 1000, "bread", ("hot_drink", "books")),
    _sg_visit("ol", "7:00", 60, "徒歩", (70, 80, 90, 70, 50, 70, 70, 40, 100, 20), 1000, "bread", ("hot_drink", "medicine", "tobacco")),
    _sg_visit("ol", "7:00", 60, "徒歩", (70, 90, 90, 30, 30, 70, 70, 40, 100, 20), 800, "bread", ("hot_drink",)),
    _sg_visit("ol", "8:00", 60, "徒歩", (70, 90, 90, 60, 30, 70, 70, 40, 100, 20), 1000, "bread", ("cold_drink", "snacks", "books")),
    _sg_visit("ol", "12:00", 60, "徒歩", (70, 90, 90, 30, 30, 70, 70, 40, 100, 20), 1200, "bento", ("cold_drink", "ice_cream", "tobacco")),
    _sg_visit("ol", "12:00", 60, "徒歩", (70, 90, 90, 30, 30, 70, 70, 40, 100, 20), 1200, "bread", ("cold_drink", "tobacco", "event_goods")),
    _sg_visit("ol", "12:00", 60, "徒歩", (70, 90, 90, 30, 30, 70, 70, 40, 100, 20), 1500, "bento", ("hot_drink", "snacks", "ice_cream")),
    _sg_visit("ol", "12:00", 60, "徒歩", (70, 90, 90, 50, 30, 70, 70, 40, 100, 20), 2000, "bento", ("cold_drink", "medicine", "daily_goods")),
    _sg_visit("ol", "18:00", 60, "徒歩", (70, 90, 90, 30, 30, 70, 70, 40, 100, 20), 2000, "instant_food", ("cold_drink", "snacks", "tobacco")),
    _sg_visit("ol", "19:00", 180, "徒歩", (70, 90, 90, 80, 80, 80, 80, 50, 100, 20), 4000, "vegetables", ("meat", "fish", "seasoning")),
    _sg_visit("ol", "19:00", 120, "徒歩", (70, 90, 90, 30, 30, 70, 70, 40, 100, 20), 2000, "bread", ("hot_drink", "snacks", "event_goods")),
    _sg_visit("ol", "20:00", 60, "徒歩", (70, 90, 90, 30, 90, 90, 40, 20, 100, 20), 2000, "bento", ("cold_drink", "snacks", "books")),
    _sg_visit("ol", "20:00", 120, "徒歩", (70, 90, 90, 50, 90, 60, 40, 20, 100, 20), 1000, "copy_paper", ("cold_drink", "hot_drink", "books")),
    _sg_visit("ol", "21:00", 60, "徒歩", (70, 80, 90, 40, 30, 70, 90, 40, 100, 20), 3000, "retort_food", ("instant_food", "frozen_food", "chinese_steamed_bun")),
    _sg_visit("ol", "21:00", 120, "徒歩", (80, 70, 80, 80, 80, 70, 60, 40, 100, 20), 4000, "alcohol", ("snacks", "oden", "instant_food")),
    _sg_visit("ol", "21:00", 120, "徒歩", (80, 70, 80, 80, 80, 70, 60, 40, 100, 20), 5000, "daily_goods", ("snacks", "hot_drink", "frozen_food")),
    _sg_visit("ol", "21:00", 120, "徒歩", (80, 70, 80, 80, 80, 70, 60, 40, 100, 20), 5000, "books", ("snacks", "alcohol", "oden")),
    _sg_visit("ol", "22:00", 60, "徒歩", (70, 70, 80, 50, 30, 70, 70, 40, 100, 20), 3000, "instant_food", ("hot_drink", "oden", "snacks")),
    # おじさん (40~55歳) -- 6 rows
    _sg_visit("middle_aged_man", "22:00", 120, "徒歩", (50, 70, 70, 70, 50, 10, 10, 50, 70, 100), 8000, "alcohol", ("oden", "snacks", "tobacco")),
    _sg_visit("middle_aged_man", "23:00", 120, "自動車", (50, 70, 30, 70, 100, 10, 10, 10, 70, 100), 10000, "alcohol", ("oden", "snacks", "tobacco")),
    _sg_visit("middle_aged_man", "15:00", 120, "自動車", (50, 70, 70, 50, 50, 10, 10, 50, 70, 100), 1500, "ice_cream", ("cold_drink", "tobacco")),
    _sg_visit("middle_aged_man", "15:00", 120, "バイク", (50, 70, 70, 50, 50, 10, 10, 50, 70, 100), 1000, "ice_cream", ("tobacco", "hot_drink")),
    _sg_visit("middle_aged_man", "23:00", 120, "自動車", (50, 70, 30, 80, 100, 10, 10, 10, 70, 100), 5000, "tobacco", ("alcohol", "snacks", "tobacco")),
    _sg_visit("middle_aged_man", "15:00", 120, "徒歩", (50, 70, 70, 50, 60, 10, 10, 50, 70, 100), 1500, "tobacco", ("cold_drink", "hot_drink")),
    # おばさん (40~58歳) -- 10 rows
    _sg_visit("middle_aged_woman", "10:00", 240, "徒歩", (100, 50, 80, 40, 100, 100, 40, 70, 80, 100), 10000, "daily_goods", ("fish", "meat", "frozen_food")),
    _sg_visit("middle_aged_woman", "14:00", 240, "自転車", (100, 50, 80, 40, 100, 100, 20, 70, 80, 100), 15000, "underwear", ("vegetables", "meat", "electronics")),
    _sg_visit("middle_aged_woman", "10:00", 240, "徒歩", (100, 50, 80, 50, 100, 100, 40, 70, 80, 100), 12000, "underwear", ("daily_goods", "retort_food", "vegetables")),
    _sg_visit("middle_aged_woman", "14:00", 240, "自転車", (100, 50, 80, 50, 100, 100, 20, 70, 80, 100), 12000, "underwear", ("vegetables", "frozen_food", "seasoning")),
    _sg_visit("middle_aged_woman", "10:00", 240, "徒歩", (100, 50, 80, 40, 100, 100, 30, 80, 80, 100), 5000, "vegetables", ("retort_food", "frozen_food", "meat")),
    _sg_visit("middle_aged_woman", "10:00", 240, "自転車", (100, 50, 80, 40, 100, 90, 20, 80, 80, 100), 5000, "meat", ("bread", "instant_food", "frozen_food")),
    _sg_visit("middle_aged_woman", "15:00", 240, "徒歩", (100, 50, 80, 30, 100, 90, 30, 80, 80, 100), 8000, "vegetables", ("fish", "meat", "seasoning")),
    _sg_visit("middle_aged_woman", "15:00", 240, "自動車", (100, 50, 80, 30, 100, 90, 10, 80, 80, 100), 8000, "fish", ("vegetables", "meat", "seasoning")),
    _sg_visit("middle_aged_woman", "16:00", 240, "バイク", (100, 50, 80, 30, 100, 90, 10, 80, 80, 100), 10000, "vegetables", ("fish", "meat", "seasoning")),
    _sg_visit("middle_aged_woman", "17:00", 240, "自動車", (100, 50, 80, 30, 100, 90, 10, 80, 80, 100), 10000, "vegetables", ("fish", "meat", "seasoning")),
    # おじいさん (65~78歳) -- 4 rows
    _sg_visit("elderly_man", "10:00", 360, "徒歩", (10, 20, 100, 70, 80, 20, 80, 80, 70, 100), 3000, "tobacco", ("hot_drink", "chinese_steamed_bun", "medicine")),
    _sg_visit("elderly_man", "15:00", 360, "徒歩", (10, 20, 100, 70, 70, 20, 80, 70, 100, 100), 5000, "alcohol", ("snacks", "fish", "vegetables")),
    _sg_visit("elderly_man", "9:00", 360, "徒歩", (10, 20, 100, 70, 20, 20, 90, 100, 70, 100), 5000, "daily_goods", ("underwear", "electronics", "medicine")),
    _sg_visit("elderly_man", "10:00", 360, "徒歩", (10, 20, 100, 70, 10, 20, 90, 100, 70, 100), 8000, "underwear", ("daily_goods", "frozen_food", "medicine")),
    # おばあさん (65~78歳) -- 6 rows
    _sg_visit("elderly_woman", "11:00", 360, "徒歩", (20, 20, 100, 70, 20, 30, 90, 100, 70, 100), 10000, "daily_goods", ("underwear", "electronics", "medicine")),
    _sg_visit("elderly_woman", "11:00", 360, "徒歩", (20, 20, 100, 70, 10, 30, 90, 100, 70, 100), 8000, "underwear", ("daily_goods", "frozen_food", "medicine")),
    _sg_visit("elderly_woman", "16:00", 360, "徒歩", (10, 20, 100, 70, 50, 20, 90, 100, 70, 100), 6000, "fish", ("vegetables", "meat", "seasoning")),
    _sg_visit("elderly_woman", "15:00", 360, "徒歩", (20, 20, 100, 70, 50, 30, 90, 100, 70, 100), 6000, "fish", ("vegetables", "meat", "seasoning")),
    _sg_visit("elderly_woman", "11:00", 360, "徒歩", (20, 20, 100, 70, 90, 30, 70, 80, 70, 100), 8000, "medicine", ("underwear", "daily_goods", "vegetables")),
    _sg_visit("elderly_woman", "13:00", 360, "徒歩", (20, 20, 100, 70, 80, 20, 100, 80, 70, 100), 7000, "parcel_delivery_form", ("hot_drink", "snacks", "electronics")),
    # 男子小学生 (7~12歳) -- 2 rows
    _sg_visit("boy_elementary_student", "14:00", 120, "自転車", (100, 70, 50, 80, 50, 10, 70, 50, 70, 100), 1000, "stationery", ("cold_drink", "snacks", "event_goods")),
    _sg_visit("boy_elementary_student", "15:00", 120, "自転車", (100, 70, 50, 80, 50, 10, 70, 50, 700, 100), 800, "snacks", ("cold_drink", "event_goods")),
    # 女子小学生 (7~12歳) -- 2 rows
    _sg_visit("girl_elementary_student", "15:00", 120, "自転車", (100, 70, 50, 80, 50, 10, 70, 50, 70, 100), 1000, "stationery", ("cold_drink", "snacks", "event_goods")),
    _sg_visit("girl_elementary_student", "14:00", 120, "自転車", (100, 70, 50, 80, 50, 10, 70, 50, 70, 100), 800, "snacks", ("cold_drink", "event_goods")),
    # 男子中学生 (13~15歳) -- 5 rows
    _sg_visit("boy_middle_school_student", "7:00", 60, "自転車", (100, 80, 50, 10, 90, 10, 50, 10, 70, 100), 500, "stationery", ()),
    _sg_visit("boy_middle_school_student", "14:00", 120, "自転車", (100, 80, 50, 30, 80, 10, 30, 10, 70, 100), 800, "cold_drink", ("hot_drink", "snacks", "books")),
    _sg_visit("boy_middle_school_student", "15:00", 120, "徒歩", (100, 80, 50, 30, 80, 10, 30, 10, 70, 100), 800, "cold_drink", ("hot_drink", "stationery", "snacks")),
    _sg_visit("boy_middle_school_student", "17:00", 120, "自転車", (100, 80, 50, 30, 80, 30, 30, 10, 70, 100), 1500, "event_goods", ("snacks", "cold_drink", "books")),
    _sg_visit("boy_middle_school_student", "15:00", 120, "徒歩", (100, 100, 10, 80, 50, 10, 30, 10, 70, 100), 3000, "cold_drink", ("hot_drink", "books", "event_goods")),
    # 女子中学生 (13~15歳) -- 4 rows
    _sg_visit("girl_middle_school_student", "7:00", 60, "徒歩", (100, 80, 50, 10, 90, 20, 50, 10, 70, 100), 500, "stationery", ()),
    _sg_visit("girl_middle_school_student", "15:00", 120, "徒歩", (100, 80, 50, 30, 80, 30, 30, 10, 70, 100), 1000, "cold_drink", ("ice_cream", "snacks", "stationery")),
    _sg_visit("girl_middle_school_student", "17:00", 120, "自転車", (100, 80, 50, 30, 80, 30, 30, 10, 70, 100), 1000, "cold_drink", ("ice_cream", "stationery", "books")),
    _sg_visit("girl_middle_school_student", "15:00", 120, "徒歩", (100, 80, 50, 30, 80, 10, 30, 10, 70, 100), 1200, "event_goods", ("chinese_steamed_bun", "hot_drink", "snacks")),
    # 男子高校生 (16~18歳) -- 4 rows
    _sg_visit("boy_high_school_student", "16:00", 120, "徒歩", (100, 90, 40, 30, 80, 10, 30, 10, 70, 100), 1500, "cold_drink", ("hot_drink", "event_goods", "stationery")),
    _sg_visit("boy_high_school_student", "17:00", 120, "バイク", (100, 90, 40, 30, 80, 10, 10, 10, 70, 100), 1500, "cold_drink", ("hot_drink", "event_goods", "stationery")),
    _sg_visit("boy_high_school_student", "16:00", 120, "バイク", (100, 90, 40, 30, 80, 10, 10, 10, 70, 100), 3000, "event_goods", ("chinese_steamed_bun", "cold_drink", "stationery")),
    _sg_visit("boy_high_school_student", "17:00", 120, "バイク", (100, 90, 10, 80, 50, 10, 10, 10, 70, 100), 4000, "medicine", ("cold_drink", "event_goods", "chinese_steamed_bun")),
    # 女子高校生 (16~18歳) -- 5 rows
    _sg_visit("girl_high_school_student", "16:00", 180, "徒歩", (100, 90, 40, 30, 100, 50, 50, 30, 70, 100), 3000, "copy_paper", ("cold_drink", "stationery", "event_goods")),
    _sg_visit("girl_high_school_student", "16:00", 120, "徒歩", (100, 90, 40, 30, 80, 10, 30, 30, 70, 100), 2000, "cold_drink", ("hot_drink", "snacks", "event_goods")),
    _sg_visit("girl_high_school_student", "17:00", 120, "自転車", (100, 90, 40, 30, 80, 10, 20, 30, 70, 100), 2000, "cold_drink", ("hot_drink", "snacks", "books")),
    _sg_visit("girl_high_school_student", "16:00", 120, "徒歩", (100, 90, 40, 30, 80, 10, 30, 30, 70, 100), 2000, "ice_cream", ("cold_drink", "snacks", "books")),
    _sg_visit("girl_high_school_student", "17:00", 120, "自転車", (100, 90, 40, 30, 80, 10, 20, 30, 70, 100), 3500, "event_goods", ("snacks", "cold_drink", "stationery")),
    # 男子幼稚園児 (4~6歳) -- 1 row
    _sg_visit("boy_kindergartner", "13:00", 120, "徒歩", (40, 60, 50, 100, 30, 0, 90, 80, 50, 100), 500, "snacks", ("cold_drink", "event_goods")),
    # 女子幼稚園児 (4~6歳) -- 1 row
    _sg_visit("girl_kindergartner", "13:00", 120, "徒歩", (40, 60, 50, 100, 30, 0, 90, 80, 50, 100), 500, "snacks", ("cold_drink", "event_goods")),
    # 子供連れのおじさん (35~38歳) -- 3 rows
    _sg_visit("man_with_child", "20:00", 240, "自動車", (40, 30, 80, 70, 60, 50, 20, 30, 20, 100), 4000, "snacks", ("cold_drink", "ice_cream", "event_goods")),
    _sg_visit("man_with_child", "15:00", 240, "徒歩", (40, 30, 80, 70, 80, 50, 50, 30, 20, 100), 20000, "electronics", ("daily_goods", "underwear", "event_goods")),
    _sg_visit("man_with_child", "16:00", 60, "自動車", (40, 40, 80, 60, 70, 20, 80, 20, 20, 100), 6000, "cold_drink", ("ice_cream", "snacks", "event_goods")),
    # 子供連れのおばさん (38~41歳) -- 6 rows
    _sg_visit("woman_with_child", "20:00", 240, "徒歩", (40, 30, 70, 60, 50, 80, 60, 70, 20, 100), 5000, "snacks", ("cold_drink", "event_goods", "medicine")),
    _sg_visit("woman_with_child", "14:00", 240, "自転車", (50, 30, 80, 50, 80, 90, 40, 70, 20, 100), 10000, "daily_goods", ("vegetables", "meat", "seasoning")),
    _sg_visit("woman_with_child", "15:00", 240, "自動車", (50, 30, 80, 50, 80, 90, 10, 70, 20, 100), 15000, "underwear", ("vegetables", "frozen_food", "seasoning")),
    _sg_visit("woman_with_child", "16:00", 240, "自動車", (50, 30, 80, 40, 100, 90, 10, 70, 20, 100), 5000, "fish", ("vegetables", "frozen_food", "seasoning")),
    _sg_visit("woman_with_child", "17:00", 240, "徒歩", (50, 30, 80, 40, 100, 90, 70, 70, 20, 100), 8000, "meat", ("vegetables", "fish", "seasoning")),
    _sg_visit("woman_with_child", "16:00", 60, "自動車", (40, 40, 80, 70, 70, 20, 80, 20, 20, 100), 6000, "cold_drink", ("ice_cream", "snacks", "event_goods")),
    # 子抱きのおばさん (30~39歳) -- 1 row
    _sg_visit("woman_carrying_infant", "15:00", 240, "自動車", (40, 30, 70, 60, 70, 80, 20, 70, 20, 100), 18000, "electronics", ("underwear", "daily_goods", "event_goods")),
    # 車椅子の男性 (30~33歳) -- 1 row
    _sg_visit("man_in_wheelchair", "14:00", 360, "徒歩", (30, 10, 80, 50, 20, 0, 100, 50, 70, 100), 15000, "books", ("cold_drink", "snacks", "medicine")),
    # 松葉杖の男性 (25~28歳) -- 1 row
    _sg_visit("man_on_crutches", "11:00", 360, "徒歩", (30, 10, 80, 50, 20, 0, 100, 50, 70, 100), 15000, "books", ("cold_drink", "snacks", "medicine")),
)


def _sg_building(
    building_id: str,
    display_name_ja: str,
    *,
    footprint: tuple[int, int],
    building_attribute: str,
    building_price_yen: int,
    wanted_products: tuple[str, ...],
    active_overnight: bool,
) -> TownBuildingProfile:
    """Build one general town-building row from the strategy guide's DATA4 table.

    Source: docs/research/strategy-guide-full-decode-2026-09-16.md section 9
    and the primary guide scans (建物 table, book pages 92-95). Product
    names are mapped to the same category ids used by
    PRODUCT_CATEGORY_PRICING. Some source rows list 6-8 wanted products;
    only the clearly legible leading items are kept per row rather than
    guessing at partially-illegible trailing entries.
    """

    evidence = EvidenceLevel.CONFIRMED_OFFICIAL
    return TownBuildingProfile(
        building_id,
        display_name_ja,
        footprint=EvidenceValue(footprint, evidence, STRATEGY_GUIDE),
        building_attribute=EvidenceValue(building_attribute, evidence, STRATEGY_GUIDE),
        building_price_yen=EvidenceValue(building_price_yen, evidence, STRATEGY_GUIDE),
        wanted_products=EvidenceValue(wanted_products, evidence, STRATEGY_GUIDE),
        active_overnight=EvidenceValue(active_overnight, evidence, STRATEGY_GUIDE),
    )


# General town-building demand profiles (59 buildings), transcribed directly
# from the strategy guide's primary page scans (book pages 92-95). Distinct
# from TOWN_FACILITIES (the smaller set of inducible facilities); this
# covers any building that can appear on the town map. `active_overnight`
# follows the guide's own two-table split (daytime-only vs. round-the-clock
# customer presence).
TOWN_BUILDINGS: tuple[TownBuildingProfile, ...] = (
    # 朝から夜だけ客のいる建物 (daytime-only)
    _sg_building("police_box_building", "交番", footprint=(2, 2), building_attribute="その他施設", building_price_yen=100, wanted_products=("bento", "tobacco", "cold_drink"), active_overnight=False),
    _sg_building("village_office", "役場(村役場)", footprint=(2, 2), building_attribute="役場", building_price_yen=700, wanted_products=("bento", "instant_food", "bread", "vegetables", "meat"), active_overnight=False),
    _sg_building("prefectural_office", "役所(県庁)", footprint=(5, 5), building_attribute="役場", building_price_yen=200, wanted_products=("bento", "bread", "tobacco", "instant_food", "retort_food"), active_overnight=False),
    _sg_building("metropolitan_government_office", "都庁", footprint=(7, 7), building_attribute="役場", building_price_yen=400, wanted_products=("bento", "bread", "tobacco", "instant_food", "retort_food"), active_overnight=False),
    _sg_building("kindergarten_building", "幼稚園", footprint=(3, 2), building_attribute="学校", building_price_yen=200, wanted_products=("snacks", "fish", "meat", "cold_drink", "vegetables"), active_overnight=False),
    _sg_building("elementary_school_building", "小学校", footprint=(4, 4), building_attribute="学校", building_price_yen=200, wanted_products=("stationery", "snacks", "meat", "cold_drink"), active_overnight=False),
    _sg_building("middle_school_building", "中学校", footprint=(5, 5), building_attribute="学校", building_price_yen=200, wanted_products=("cold_drink", "event_goods", "stationery", "hot_drink"), active_overnight=False),
    _sg_building("high_school_building", "高校", footprint=(6, 6), building_attribute="学校", building_price_yen=200, wanted_products=("cold_drink", "event_goods", "copy_paper", "chinese_steamed_bun"), active_overnight=False),
    _sg_building("amusement_park_building", "遊園地", footprint=(7, 7), building_attribute="アミューズメント", building_price_yen=200, wanted_products=("snacks", "cold_drink", "hot_drink", "ice_cream"), active_overnight=False),
    _sg_building("aquarium_building", "水族館", footprint=(3, 3), building_attribute="アミューズメント", building_price_yen=300, wanted_products=("snacks", "cold_drink", "ice_cream"), active_overnight=False),
    _sg_building("zoo_building", "動物園", footprint=(6, 6), building_attribute="アミューズメント", building_price_yen=200, wanted_products=("snacks", "cold_drink", "ice_cream"), active_overnight=False),
    _sg_building("small_park_building", "公園(小)", footprint=(1, 1), building_attribute="アミューズメント", building_price_yen=1_000, wanted_products=("snacks", "cold_drink", "hot_drink"), active_overnight=False),
    _sg_building("large_park_building", "公園(大)", footprint=(2, 2), building_attribute="アミューズメント", building_price_yen=500, wanted_products=("snacks", "cold_drink", "hot_drink"), active_overnight=False),
    _sg_building("game_center", "ゲームセンター", footprint=(1, 1), building_attribute="店", building_price_yen=2_000, wanted_products=("tobacco", "medicine", "cold_drink", "daily_goods"), active_overnight=False),
    _sg_building("pachinko_parlor", "パチンコ屋", footprint=(2, 2), building_attribute="店", building_price_yen=800, wanted_products=("bread", "tobacco", "alcohol", "fish", "cold_drink"), active_overnight=False),
    _sg_building("house_small_d", "住宅(小D)", footprint=(1, 2), building_attribute="住宅", building_price_yen=1_000, wanted_products=("alcohol", "ice_cream", "fish", "daily_goods", "underwear", "vegetables"), active_overnight=False),
    _sg_building("house_medium_a", "住宅(中A)", footprint=(2, 2), building_attribute="住宅", building_price_yen=700, wanted_products=("bread", "alcohol", "ice_cream", "vegetables", "daily_goods", "underwear"), active_overnight=False),
    _sg_building("house_large_c", "住宅(大C)", footprint=(3, 2), building_attribute="住宅", building_price_yen=700, wanted_products=("alcohol", "ice_cream", "fish", "daily_goods", "underwear", "vegetables"), active_overnight=False),
    _sg_building("bathhouse", "銭湯", footprint=(2, 2), building_attribute="店", building_price_yen=700, wanted_products=("instant_food", "bento", "alcohol", "ice_cream", "bread"), active_overnight=False),
    _sg_building("gym_building", "体育館", footprint=(3, 3), building_attribute="その他施設", building_price_yen=700, wanted_products=("snacks", "cold_drink", "hot_drink"), active_overnight=False),
    _sg_building("athletic_field_building", "運動場", footprint=(5, 4), building_attribute="その他施設", building_price_yen=100, wanted_products=("cold_drink", "bento", "medicine", "snacks", "ice_cream"), active_overnight=False),
    _sg_building("pool_building", "プール", footprint=(3, 2), building_attribute="その他施設", building_price_yen=300, wanted_products=("cold_drink", "bento", "medicine", "snacks"), active_overnight=False),
    _sg_building("event_hall_building", "イベント会場", footprint=(2, 2), building_attribute="その他施設", building_price_yen=1_500, wanted_products=("event_goods", "snacks", "cold_drink", "chinese_steamed_bun"), active_overnight=False),
    _sg_building("family_restaurant", "ファミリーレストラン", footprint=(2, 2), building_attribute="店", building_price_yen=1_000, wanted_products=("tobacco", "instant_food", "alcohol", "daily_goods", "electronics", "underwear"), active_overnight=False),
    _sg_building("restaurant", "レストラン", footprint=(2, 1), building_attribute="店", building_price_yen=2_500, wanted_products=("tobacco", "instant_food", "alcohol", "daily_goods", "electronics", "underwear"), active_overnight=False),
    _sg_building("fast_food_a", "ファーストフードA", footprint=(1, 1), building_attribute="店", building_price_yen=1_000, wanted_products=("instant_food", "retort_food", "alcohol", "event_goods", "copy_paper", "snacks"), active_overnight=False),
    _sg_building("fast_food_b", "ファーストフードB", footprint=(1, 1), building_attribute="店", building_price_yen=2_000, wanted_products=("retort_food", "alcohol", "tobacco", "copy_paper", "snacks", "instant_food", "chinese_steamed_bun"), active_overnight=False),
    _sg_building("soba_shop", "そば屋", footprint=(1, 1), building_attribute="店", building_price_yen=1_000, wanted_products=("vegetables", "meat", "bento", "instant_food", "fish", "retort_food"), active_overnight=False),
    _sg_building("toy_store", "おもちゃ屋", footprint=(1, 1), building_attribute="店", building_price_yen=1_000, wanted_products=("daily_goods", "vegetables", "underwear", "electronics", "fish", "meat"), active_overnight=False),
    _sg_building("clothing_store", "洋品店", footprint=(1, 1), building_attribute="店", building_price_yen=1_000, wanted_products=("vegetables", "fish", "underwear", "daily_goods"), active_overnight=False),
    _sg_building("electronics_store", "電気屋", footprint=(1, 1), building_attribute="店", building_price_yen=1_000, wanted_products=("electronics", "underwear", "daily_goods", "fish", "vegetables"), active_overnight=False),
    # 深夜から早朝にも客のいる建物 (24-hour customer presence)
    _sg_building("fire_station_building", "消防署", footprint=(3, 2), building_attribute="その他施設", building_price_yen=100, wanted_products=("bento", "cold_drink"), active_overnight=True),
    _sg_building("station_small", "駅(小)", footprint=(2, 1), building_attribute="駅", building_price_yen=1_000, wanted_products=("bread", "bento", "instant_food", "hot_drink", "cold_drink", "retort_food"), active_overnight=True),
    _sg_building("station_large", "駅(大)", footprint=(4, 2), building_attribute="駅", building_price_yen=200, wanted_products=("bread", "bento", "tobacco", "instant_food", "retort_food", "cold_drink"), active_overnight=True),
    _sg_building("university_building", "大学", footprint=(7, 7), building_attribute="学校", building_price_yen=200, wanted_products=("bento", "bread", "instant_food", "event_goods", "retort_food", "cold_drink"), active_overnight=True),
    _sg_building("vocational_school_building", "専門学校", footprint=(4, 3), building_attribute="学校", building_price_yen=400, wanted_products=("bento", "bread", "event_goods", "retort_food", "cold_drink"), active_overnight=True),
    _sg_building("company_small_a", "会社(小A)", footprint=(2, 2), building_attribute="会社", building_price_yen=800, wanted_products=("bread", "bento", "tobacco", "instant_food", "cold_drink"), active_overnight=True),
    _sg_building("company_small_b", "会社(小B)", footprint=(2, 2), building_attribute="会社", building_price_yen=800, wanted_products=("bread", "tobacco", "cold_drink", "instant_food"), active_overnight=True),
    _sg_building("company_small_c", "会社(小C)", footprint=(2, 2), building_attribute="会社", building_price_yen=1_000, wanted_products=("bread", "bento", "alcohol", "instant_food", "daily_goods", "books", "medicine"), active_overnight=True),
    _sg_building("company_large_a", "会社(大A)", footprint=(3, 3), building_attribute="会社", building_price_yen=500, wanted_products=("bread", "bento", "alcohol", "instant_food", "daily_goods", "books", "medicine"), active_overnight=True),
    _sg_building("company_large_b", "会社(大B)", footprint=(3, 3), building_attribute="会社", building_price_yen=600, wanted_products=("bread", "bento", "alcohol", "instant_food", "daily_goods", "books", "retort_food"), active_overnight=True),
    _sg_building("house_small_a", "住宅(小A)", footprint=(1, 1), building_attribute="住宅", building_price_yen=1_000, wanted_products=("bread", "bento", "tobacco", "alcohol", "instant_food", "daily_goods", "snacks"), active_overnight=True),
    _sg_building("house_small_b", "住宅(小B)", footprint=(1, 1), building_attribute="住宅", building_price_yen=1_000, wanted_products=("instant_food", "retort_food", "vegetables", "meat", "fish", "event_goods", "tobacco"), active_overnight=True),
    _sg_building("house_small_c", "住宅(小C)", footprint=(1, 1), building_attribute="住宅", building_price_yen=2_000, wanted_products=("bread", "alcohol", "instant_food", "tobacco", "event_goods", "ice_cream", "chinese_steamed_bun"), active_overnight=True),
    _sg_building("house_medium_b", "住宅(中B)", footprint=(2, 2), building_attribute="住宅", building_price_yen=700, wanted_products=("daily_goods", "alcohol", "meat", "event_goods", "instant_food", "retort_food", "electronics"), active_overnight=True),
    _sg_building("family_restaurant_a", "ファミリーレストランA", footprint=(2, 2), building_attribute="店", building_price_yen=1_000, wanted_products=("fish", "ice_cream", "electronics", "underwear", "copy_paper", "instant_food", "alcohol"), active_overnight=True),
    _sg_building("family_restaurant_b", "ファミリーレストランB", footprint=(2, 2), building_attribute="店", building_price_yen=1_000, wanted_products=("electronics", "underwear", "tobacco", "alcohol", "ice_cream", "instant_food", "frozen_food"), active_overnight=True),
    _sg_building("ramen_shop", "ラーメン屋", footprint=(1, 1), building_attribute="店", building_price_yen=2_000, wanted_products=("instant_food", "bento", "tobacco", "alcohol", "hot_drink"), active_overnight=True),
    _sg_building("izakaya_a", "飲み屋A", footprint=(1, 1), building_attribute="店", building_price_yen=1_000, wanted_products=("snacks", "medicine", "hot_drink", "bento", "retort_food", "alcohol", "bread"), active_overnight=True),
    _sg_building("izakaya_b", "飲み屋B", footprint=(1, 1), building_attribute="店", building_price_yen=1_000, wanted_products=("instant_food", "bento", "retort_food", "alcohol", "daily_goods", "oden", "bread"), active_overnight=True),
    _sg_building("izakaya_c", "飲み屋C", footprint=(1, 1), building_attribute="店", building_price_yen=1_000, wanted_products=("bento", "alcohol", "tobacco", "daily_goods", "oden", "hot_drink"), active_overnight=True),
    _sg_building("bookstore", "本屋", footprint=(1, 1), building_attribute="店", building_price_yen=1_000, wanted_products=("instant_food", "books", "bento", "bread", "event_goods"), active_overnight=True),
    # 客のいない建物 (no customer demand)
    _sg_building("own_conveni_lot", "コンビニ(自)", footprint=(2, 2), building_attribute="店", building_price_yen=300, wanted_products=(), active_overnight=False),
    _sg_building("rival_conveni_lot", "コンビニ(敵)", footprint=(2, 2), building_attribute="店", building_price_yen=300, wanted_products=(), active_overnight=False),
    _sg_building("vacant_lot", "空き地", footprint=(1, 1), building_attribute="", building_price_yen=0, wanted_products=(), active_overnight=False),
    _sg_building("road", "道路", footprint=(1, 1), building_attribute="", building_price_yen=100, wanted_products=(), active_overnight=False),
    _sg_building("railway", "線路", footprint=(1, 1), building_attribute="", building_price_yen=100, wanted_products=(), active_overnight=False),
    _sg_building("town_hall_lot", "役場用地", footprint=(1, 1), building_attribute="", building_price_yen=0, wanted_products=(), active_overnight=False),
    _sg_building("inducement_lot", "誘致用地", footprint=(1, 1), building_attribute="", building_price_yen=0, wanted_products=(), active_overnight=False),
)

# Exact hour boundaries for the 6 time-of-day buckets the strategy guide
# uses throughout its customer-frequency tables (book pages 92-95 legend).
TIME_OF_DAY_BUCKETS_HOURS = {
    "morning": (7, 11),
    "midday": (12, 15),
    "evening": (16, 19),
    "night": (20, 23),
    "late_night": (24, 3),
    "early_morning": (4, 6),
}
