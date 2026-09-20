from __future__ import annotations

import math
from typing import Iterable, Tuple

from .baseline_data import PERMITS, TRADE_AREA_RADIUS_TILES

# --- REMAKE_BALANCED_DEFAULT house rule ---------------------------------
#
# decision 0095 (task #26) deliberately declined to build any town/map
# spatial simulation -- "reference_sim自身も空間モデルを持たない...これを
# 発明すると...最も証拠の薄い領域を無根拠に埋めることになる" -- because at
# the time, no store-to-store distance/placement rule was itself confirmed.
# It now is: the strategy guide's own distance diagram (book pages 6-7,
# also independently corroborated by `_PERMIT_FEE_AND_DISTANCE_YEN_TILES`'s
# own citation in baseline_data.py) gives four concentric radii from a
# store -- 5 tiles (new-store construction), 7/11/15 tiles (tobacco/alcohol/
# medicine permit exclusion) -- and the guide's "来店手段/エリア半径" table
# (book page 31, `TRADE_AREA_RADIUS_TILES`) gives four more radii for a
# store's own trade-area circle by arrival method. What decision 0095 called
# "no spatial model to place a rival store on" is a real gap this module
# does not fill either: it takes two stores' Position values as already
# known (from a caller -- a test, or a future town/map layer) and answers
# "how far apart are they / does that violate a confirmed distance rule /
# how much do their two trade-area circles overlap", using those already-
# confirmed radii directly. Nothing here invents a town map size, a rival
# spawn algorithm, or which permits a given rival holds -- those remain
# open gaps for a caller (or a later task) to supply.
#
# Two things ARE this module's own REMAKE_BALANCED_DEFAULT choices, each
# tagged at its own definition below: the tile-distance metric (Chebyshev),
# since the guide states four radii in tiles but never states whether a
# diagonal tile counts as 1 or ~1.41 away (the same ambiguity
# `PermitDefinition.exclusion_distance_tiles`'s own note already flags);
# and the trade-area overlap ratio's normalization convention (overlap
# area / smaller circle's area), since `TradeAreaRadiusEntry`'s own
# docstring already flags that the guide states the radii but not how two
# overlapping circles are resolved.

Position = Tuple[int, int]


def chebyshev_distance_tiles(a: Position, b: Position) -> int:
    """REMAKE_BALANCED_DEFAULT distance metric between two store positions.

    The guide's own distance diagram states each ring's radius in tiles
    (5/7/11/15) but never states whether distance is measured Chebyshev
    (max(dx, dy), i.e. a diagonal tile counts as 1 away, matching how this
    project's existing in-store movement/pathfinding already treats a
    single step) or Euclidean -- the same gap
    `PermitDefinition.exclusion_distance_tiles`'s own evidence note already
    flags. Chebyshev is used here since it is this project's own existing
    convention for single-tile-step distance elsewhere (store_grid.py's
    layout movement), not because the guide confirms it.
    """

    return max(abs(a[0] - b[0]), abs(a[1] - b[1]))


STORE_CONSTRUCTION_MIN_DISTANCE_TILES = 5
"""CONFIRMED_OFFICIAL: the guide's distance diagram's innermost ring (book
pages 6-7) -- a new store cannot be built within this many tiles of an
existing store (any store, not just a same-chain one; see the diagram's own
"お店" reference point and `docs/research/permit-timing-and-state-reset-
exploits-2026-09-06.md`). Kept as its own named constant here (previously
only documented in a code comment on `_PERMIT_FEE_AND_DISTANCE_YEN_TILES`
in baseline_data.py) so it is a queryable, testable value like the three
permit radii below, not just prose."""


def can_construct_store_at(
    candidate: Position, existing_store_positions: Iterable[Position]
) -> bool:
    """CONFIRMED_OFFICIAL rule: a new store may not be built within
    `STORE_CONSTRUCTION_MIN_DISTANCE_TILES` of any existing store (see that
    constant's own note). `existing_store_positions` is caller-supplied and
    may include the player's own other stores and/or rival stores -- the
    guide's diagram does not distinguish between them for this rule."""

    return all(
        chebyshev_distance_tiles(candidate, existing) >= STORE_CONSTRUCTION_MIN_DISTANCE_TILES
        for existing in existing_store_positions
    )


PERMIT_EXCLUSION_DISTANCE_TILES = {
    permit.id: permit.exclusion_distance_tiles.value for permit in PERMITS
}
"""CONFIRMED_OFFICIAL: {permit_id: exclusion_distance_tiles}, sourced
directly from `baseline_data.PERMITS` (itself the guide's book pages 6-7
table/diagram) rather than duplicating those three numbers a second time."""


def can_acquire_permit_at(
    permit_id: str,
    candidate: Position,
    other_permit_holder_positions: Iterable[Position],
) -> bool:
    """CONFIRMED_OFFICIAL rule (guide book page 9: "販売許可には範囲があり、
    すでに販売許可を取っている店の範囲内では売ることができない"; also book
    page 74's mutual-exclusion example): a store may not acquire `permit_id`
    within that permit's exclusion radius of another store that ALREADY
    holds the same permit. `other_permit_holder_positions` is caller-
    supplied and must already be filtered to stores holding this specific
    permit -- this function does not track permit ownership itself, since
    no source states a formula for which permits a given rival holds (see
    module docstring)."""

    radius = PERMIT_EXCLUSION_DISTANCE_TILES[permit_id]
    return all(
        chebyshev_distance_tiles(candidate, holder) >= radius
        for holder in other_permit_holder_positions
    )


TRADE_AREA_RADIUS_TILES_BY_ARRIVAL_METHOD = {
    entry.arrival_method.value: entry.radius.value for entry in TRADE_AREA_RADIUS_TILES
}
"""CONFIRMED_OFFICIAL: {arrival_method: radius_tiles}, sourced directly from
`baseline_data.TRADE_AREA_RADIUS_TILES` (guide book page 31)."""


def trade_area_overlap_ratio(
    position_a: Position, radius_a: int, position_b: Position, radius_b: int
) -> float:
    """REMAKE_BALANCED_DEFAULT: how much two stores' circular trade areas
    overlap, as a 0.0 (no shared trade area) to 1.0 (the smaller circle is
    entirely inside the larger one) ratio -- exactly the shape
    `remake_rival_policy.RivalPolicyInputs.trade_area_overlap_ratio` already
    expected from a caller, but which no caller could previously compute
    (decision 0095: no rival entity/position existed). `radius_a`/`radius_b`
    are normally two `TRADE_AREA_RADIUS_TILES_BY_ARRIVAL_METHOD` values (the
    guide's own CONFIRMED_OFFICIAL per-arrival-method trade-area radii), but
    this function itself only does the geometry: standard circle-circle
    intersection area, normalized by the SMALLER circle's own area. This
    normalization (rather than e.g. union-based Jaccard overlap) is this
    module's own choice, not a recovered original resolution rule --
    `TradeAreaRadiusEntry`'s own evidence note already flags that the guide
    never states how two overlapping trade-area circles are resolved.
    """

    if radius_a < 0 or radius_b < 0:
        raise ValueError("radius_a and radius_b must be >= 0")
    smaller_radius, larger_radius = sorted((radius_a, radius_b))
    if smaller_radius == 0:
        return 0.0
    distance = math.dist(position_a, position_b)
    if distance >= radius_a + radius_b:
        return 0.0
    if distance <= larger_radius - smaller_radius:
        return 1.0

    r1, r2, d = float(radius_a), float(radius_b), distance
    part1 = r1 * r1 * math.acos((d * d + r1 * r1 - r2 * r2) / (2 * d * r1))
    part2 = r2 * r2 * math.acos((d * d + r2 * r2 - r1 * r1) / (2 * d * r2))
    part3 = 0.5 * math.sqrt(
        max(0.0, (-d + r1 + r2) * (d + r1 - r2) * (d - r1 + r2) * (d + r1 + r2))
    )
    overlap_area = part1 + part2 - part3
    smaller_circle_area = math.pi * smaller_radius * smaller_radius
    return min(1.0, max(0.0, overlap_area / smaller_circle_area))


def facility_area_tiles_within_range(
    store_position: Position,
    facility_position: Position,
    facility_footprint: Tuple[int, int],
    range_tiles: int,
) -> int:
    """Task #61: the spatial search `store_value.SecurityFacilityCoverage`'s
    own docstring explicitly leaves out of scope -- "counting how many area
    tiles of a facility fall in that range... is out of scope here; this
    module only turns an already-counted tile count into a bonus." This
    supplies exactly that count, given caller-known positions (same
    convention as the rest of this module): `police_box_area_tiles`/
    `fire_station_area_tiles` = facility_area_tiles_within_range(store_pos,
    facility_pos, CONFIRMED_OFFICIAL footprint from `baseline_data.
    TOWN_FACILITIES`, `store_value.SECURITY_FACILITY_RANGE_TILES`).

    CONFIRMED_OFFICIAL inputs: police_box's (2, 2) and fire_station's (2, 3)
    footprints (`baseline_data.TOWN_FACILITIES`), and the 16-tile range
    itself (`store_value.SECURITY_FACILITY_RANGE_TILES`, guide's own "店舗
    周囲16×16エリア" wording).

    REMAKE_BALANCED_DEFAULT interpretation (already implicit in `store_
    value.py`'s own "within this many tiles" phrasing, not newly introduced
    here): "16x16エリア範囲内" is read as "Chebyshev distance <=
    range_tiles from the store's own position", not as a literal 16x16-tile
    square region anchored some other way -- the guide states the
    dimensions and per-cell rate but not the exact region shape or anchor
    point, the same kind of gap this module's own tile-distance-metric note
    above already discusses.
    """

    footprint_width, footprint_height = facility_footprint
    if footprint_width < 0 or footprint_height < 0:
        raise ValueError("facility_footprint dimensions must be >= 0")
    if range_tiles < 0:
        raise ValueError("range_tiles must be >= 0")
    count = 0
    for dx in range(footprint_width):
        for dy in range(footprint_height):
            tile: Position = (facility_position[0] + dx, facility_position[1] + dy)
            if chebyshev_distance_tiles(store_position, tile) <= range_tiles:
                count += 1
    return count
