from __future__ import annotations

from .models import (
    EvidenceLevel,
    EvidenceValue,
    FixtureDefinition,
    PermitDefinition,
    PromotionDefinition,
    ScenarioDefinition,
    StoreVariant,
    TownFacilityAnchor,
)

WIKI = "https://wikiwiki.jp/theconveni1/"

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
    ),
    FixtureDefinition(
        "bench",
        EvidenceValue((1, 1), EvidenceLevel.CONFIRMED_COMMUNITY, WIKI + "%E5%86%85%E8%A3%85"),
        EvidenceValue(168, EvidenceLevel.CONFIRMED_COMMUNITY, WIKI + "%E5%86%85%E8%A3%85"),
        EvidenceValue(3, EvidenceLevel.CONFIRMED_COMMUNITY, WIKI + "%E5%86%85%E8%A3%85"),
    ),
    FixtureDefinition(
        "fountain",
        EvidenceValue((2, 2), EvidenceLevel.CONFIRMED_COMMUNITY, WIKI + "%E5%86%85%E8%A3%85"),
        EvidenceValue(2_400, EvidenceLevel.CONFIRMED_COMMUNITY, WIKI + "%E5%86%85%E8%A3%85"),
        EvidenceValue(25, EvidenceLevel.CONFIRMED_COMMUNITY, WIKI + "%E5%86%85%E8%A3%85"),
    ),
    FixtureDefinition(
        "parking_ground",
        EvidenceValue((1, 2), EvidenceLevel.CONFIRMED_COMMUNITY, WIKI + "%E5%86%85%E8%A3%85"),
        EvidenceValue(0, EvidenceLevel.CONFIRMED_COMMUNITY, WIKI + "%E5%86%85%E8%A3%85"),
        parking_capacity=EvidenceValue(2, EvidenceLevel.CONFIRMED_COMMUNITY, WIKI + "%E5%86%85%E8%A3%85"),
    ),
    FixtureDefinition(
        "parking_two_story",
        EvidenceValue((1, 2), EvidenceLevel.CONFIRMED_COMMUNITY, WIKI + "%E5%86%85%E8%A3%85"),
        EvidenceValue(240, EvidenceLevel.CONFIRMED_COMMUNITY, WIKI + "%E5%86%85%E8%A3%85"),
        parking_capacity=EvidenceValue(4, EvidenceLevel.CONFIRMED_COMMUNITY, WIKI + "%E5%86%85%E8%A3%85"),
    ),
    FixtureDefinition(
        "parking_tower",
        EvidenceValue((2, 3), EvidenceLevel.CONFIRMED_COMMUNITY, WIKI + "%E5%86%85%E8%A3%85"),
        EvidenceValue(4_800, EvidenceLevel.CONFIRMED_COMMUNITY, WIKI + "%E5%86%85%E8%A3%85"),
        parking_capacity=EvidenceValue(20, EvidenceLevel.CONFIRMED_COMMUNITY, WIKI + "%E5%86%85%E8%A3%85"),
    ),
    FixtureDefinition(
        "vending_machine",
        footprint=None,
        sale_mode="self_service_candidate",
    ),
)

PROMOTIONS = (
    PromotionDefinition("direct_mail", EvidenceValue(100_000, EvidenceLevel.CONFIRMED_COMMUNITY, WIKI + "%E5%AE%A3%E4%BC%9D"), EvidenceValue(12, EvidenceLevel.CONFIRMED_COMMUNITY, WIKI + "%E5%AE%A3%E4%BC%9D"), EvidenceValue(2, EvidenceLevel.CONFIRMED_COMMUNITY, WIKI + "%E5%AE%A3%E4%BC%9D"), EvidenceValue(10, EvidenceLevel.CONFIRMED_COMMUNITY, WIKI + "%E5%AE%A3%E4%BC%9D")),
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

SCENARIOS = (
    ScenarioDefinition("beginner", EvidenceValue(200_000_000, EvidenceLevel.CONFIRMED_VISUAL, "Official/current PS screenshot"), EvidenceValue("metropolitan_government_after_population_threshold", EvidenceLevel.CONFIRMED_COMMUNITY, WIKI + "%E3%82%B2%E3%83%BC%E3%83%A0%E3%83%A2%E3%83%BC%E3%83%89%E6%94%BB%E7%95%A5")),
    ScenarioDefinition("intermediate", EvidenceValue(150_000_000, EvidenceLevel.CONFIRMED_COMMUNITY, WIKI + "%E3%82%B2%E3%83%BC%E3%83%A0%E3%83%A2%E3%83%BC%E3%83%89%E6%94%BB%E7%95%A5"), EvidenceValue("10_player_stores", EvidenceLevel.CONFIRMED_COMMUNITY, WIKI + "%E3%82%B2%E3%83%BC%E3%83%A0%E3%83%A2%E3%83%BC%E3%83%89%E6%94%BB%E7%95%A5")),
    ScenarioDefinition("advanced", EvidenceValue(150_000_000, EvidenceLevel.CONFIRMED_COMMUNITY, WIKI + "%E3%82%B2%E3%83%BC%E3%83%A0%E3%83%A2%E3%83%BC%E3%83%89%E6%94%BB%E7%95%A5"), EvidenceValue("owner_rating_5_stars", EvidenceLevel.CONFIRMED_COMMUNITY, WIKI + "%E3%82%B2%E3%83%BC%E3%83%A0%E3%83%A2%E3%83%BC%E3%83%89%E6%94%BB%E7%95%A5")),
)

TOWN_FACILITIES = (
    TownFacilityAnchor(
        "station",
        shopping_population=EvidenceValue(2_240, EvidenceLevel.CONFIRMED_COMMUNITY, WIKI + "%E3%82%B2%E3%83%BC%E3%83%A0%E3%83%A2%E3%83%BC%E3%83%89%E6%94%BB%E7%95%A5"),
    ),
    TownFacilityAnchor(
        "university",
        observed_population_range=EvidenceValue((700, 800), EvidenceLevel.PROVISIONAL, "PS direct-play strategy observation"),
    ),
    TownFacilityAnchor(
        "fire_station",
        construction_delay_is_nonzero=EvidenceValue(True, EvidenceLevel.PROVISIONAL, "PS long-play observation"),
    ),
)
