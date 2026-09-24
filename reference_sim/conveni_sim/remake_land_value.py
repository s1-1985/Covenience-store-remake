from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from .town import TownState

# --- REMAKE_BALANCED_DEFAULT house rule ---------------------------------
#
# Evidence confirms land value rises with both local urbanization (a
# busier, more built-up surrounding area raises nearby land price) and
# elapsed time (later years raise land price town-wide), and that
# deliberately inflating land value near a rival store is a viable
# competitive tactic
# (docs/research/ps-gameplay-economy-evidence-2026-09-05.md section 8:
# "地価は都市化と年数経過の両方で上昇", with its own suggested structure
# `land_price = base_price * local_development_factor * time_inflation_factor`;
# strategy-guide-full-decode-2026-09-16.md section 31.3 "地価を利用した圧迫";
# item 18 of section 41's "existence confirmed, formula unconfirmed" list:
# "地価変動式"). No exact formula, urbanization input variable, annual
# growth rate, tile-vs-area unit, or upper/lower bound is published. This
# module fills in the guide's own suggested multiplicative structure over
# `TownState`'s tracked population/store-count facts -- a playable
# REMAKE_BALANCED_DEFAULT placeholder, not a recovered original formula --
# expected to be retuned or replaced outright if better evidence surfaces.

ANNUAL_INFLATION_RATE = 0.05
"""Multiplicative land-price growth per elapsed year from time alone, with
every other factor held constant. A round, moderate figure: enough that
waiting out the early game visibly raises land cost over a multi-year
playthrough, without dominating every other economic decision."""

POPULATION_DEVELOPMENT_REFERENCE = 20_000
"""Population level treated as "fully developed" for the population term
below (it saturates at 1.0 here), anchored to the guide's own confirmed
early-scenario population goal (20,000 residents triggers the capital-
building event) as the one town-population figure already known to matter
to this game's pacing."""

STORE_DENSITY_REFERENCE_COUNT = 8
"""Number of stores (own + rivals) in town treated as "fully built up" for
the density term below; a round guess with no direct guide citation."""

POPULATION_DEVELOPMENT_WEIGHT = 0.6
STORE_DENSITY_DEVELOPMENT_WEIGHT = 0.4
"""Local development is a weighted blend of population growth and store
density, since the guide names both general population growth and
"繁華街化" (more stores/facilities nearby) as drivers of local land value
but never states their relative weight."""

MAX_LOCAL_DEVELOPMENT_FACTOR = 3.0
"""Upper bound on the multiplicative local-development bonus, so a single
fully-built-up tile cannot inflate to an unusable magnitude on its own;
time inflation (unbounded, see below) is the long-run driver instead."""

EXISTING_BUILDING_ACQUISITION_RATE = 0.5
"""CONFIRMED_OFFICIAL, not invented: the guide's own 建てる場所や店の規模を
決める page (実習マニュアル book page 7) states the purchase cost of an
occupied lot as 土地代 + 買収費(建物評価額の50%) -- acquiring a site that
already has a building on it costs the land price plus exactly half that
building's appraised value."""

NEW_BRANCH_LAND_AREA_COUNT = 4
"""CONFIRMED_OFFICIAL: the guide's third companion book ("攻略&データ
ブック", オールテクニックガイド ライバル対策, print page 79) states directly
"新規出店時の土地代 = 地価（4エリア分）+建物評価額／2" -- opening a new branch
costs exactly 4 areas' worth of land price, a fixed number independent of
the new store's eventual size. Pass this as `land_purchase_cost_yen()`'s
`area_count` when modeling a new-branch-opening cost specifically."""


@dataclass(frozen=True)
class RemakeBalancedLandValuePolicy:
    """Concrete land-value-over-time model over the guide's own suggested
    structure (see module docstring)."""

    annual_inflation_rate: float = ANNUAL_INFLATION_RATE
    population_development_reference: int = POPULATION_DEVELOPMENT_REFERENCE
    store_density_reference_count: int = STORE_DENSITY_REFERENCE_COUNT
    population_development_weight: float = POPULATION_DEVELOPMENT_WEIGHT
    store_density_development_weight: float = STORE_DENSITY_DEVELOPMENT_WEIGHT
    max_local_development_factor: float = MAX_LOCAL_DEVELOPMENT_FACTOR

    def local_development_factor(self, town: TownState) -> float:
        """1.0 (undeveloped) up to `max_local_development_factor` (fully
        built up), from the town's tracked population and store count."""
        population_term = min(
            1.0, town.population / self.population_development_reference
        )
        density_term = min(
            1.0, town.store_count_including_rivals / self.store_density_reference_count
        )
        development_level = (
            self.population_development_weight * population_term
            + self.store_density_development_weight * density_term
        )
        return 1.0 + development_level * (self.max_local_development_factor - 1.0)

    def time_inflation_factor(self, elapsed_years: float) -> float:
        if elapsed_years < 0:
            raise ValueError("elapsed_years must be >= 0")
        return (1.0 + self.annual_inflation_rate) ** elapsed_years

    def current_land_price_yen(
        self,
        base_land_price_yen: int,
        town: TownState,
        elapsed_years: float,
    ) -> int:
        if base_land_price_yen < 0:
            raise ValueError("base_land_price_yen must be >= 0")
        factor = self.local_development_factor(town) * self.time_inflation_factor(
            elapsed_years
        )
        return round(base_land_price_yen * factor)

    # Task #60: the guide's own 建てる場所や店の規模を決める page (実習
    # マニュアル book page 7) states this formula directly: 必要金額=土地代
    # (a vacant lot costs only the land price) where 地代~(エリア地価×
    # エリア数) (land price is approximately area land price times area
    # count) -- CONFIRMED_OFFICIAL that this multiplicative shape exists,
    # though the guide does not give a standalone "per-area land price"
    # table separate from current_land_price_yen()'s own whole-price output
    # above.
    #
    # ANALOGY-BASED (CLAUDE.md priority 2), not invented from nothing:
    # `base_land_price_per_area_yen` reinterprets current_land_price_yen()'s
    # own existing `base_land_price_yen` input/output as a PER-AREA rate
    # rather than a whole-plot price -- the same already-established
    # REMAKE_BALANCED_DEFAULT uniform-town-wide-price simplification
    # (decision 0095) applied per area instead of per plot, not a new
    # simplification. `area_count` is meant to come from a store variant's
    # own CONFIRMED_OFFICIAL `total_area_tiles` (task #57), on the
    # inference that this project's "エリア" and "tile" units are the same
    # (both the police-box/fire-station security bonus and this store-size
    # table describe footprints in the same "エリア" unit, e.g. "2x2
    # エリア" == a 2x2-tile footprint elsewhere) -- an inference, not a
    # statement the guide makes explicitly.
    #
    # Task #65 update (2026-09-24): for the specific case of opening a NEW
    # branch (as opposed to buying land for some other, size-chosen purpose),
    # the guide's third companion book ("攻略&データブック", オールテクニック
    # ガイド ライバル対策, print page 79) gives an exact, different number:
    # "新規出店時の土地代 = 地価（4エリア分）+建物評価額／2" -- a NEW branch's
    # area_count is CONFIRMED_OFFICIAL 4, a fixed constant independent of
    # whatever store size the player eventually builds, not derived from
    # `total_area_tiles` at all. This supersedes the total_area_tiles
    # inference above for that one specific call site (see
    # NEW_BRANCH_LAND_AREA_COUNT below); the total_area_tiles inference may
    # still be the best available anchor for some other, not-yet-built
    # land-purchase context (e.g. relocating the player's existing store),
    # since the guide does not say the ×4 figure generalizes beyond "新規
    # 出店" (opening a new branch).
    def land_purchase_cost_yen(
        self,
        base_land_price_per_area_yen: int,
        area_count: int,
        town: TownState,
        elapsed_years: float,
        existing_building_construction_price_yen: Optional[int] = None,
    ) -> int:
        if area_count < 0:
            raise ValueError("area_count must be >= 0")
        land_cost_yen = (
            self.current_land_price_yen(base_land_price_per_area_yen, town, elapsed_years)
            * area_count
        )
        if existing_building_construction_price_yen is None:
            return land_cost_yen
        if existing_building_construction_price_yen < 0:
            raise ValueError("existing_building_construction_price_yen must be >= 0")
        return land_cost_yen + round(
            existing_building_construction_price_yen * EXISTING_BUILDING_ACQUISITION_RATE
        )
