from __future__ import annotations

from dataclasses import dataclass

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
