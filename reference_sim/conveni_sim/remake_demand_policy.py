from __future__ import annotations

import random
from dataclasses import dataclass, field
from typing import Optional, Sequence

from .customer_demand import CustomerArrivalIntent, CustomerDemandContext, CustomerDemandPolicy
from .remake_customer_share import BAD_WEATHER_VALUES
from .store_grid import GridPoint

# --- REMAKE_BALANCED_DEFAULT house rule ---------------------------------
#
# customer_demand.py's CustomerDemandPolicy protocol deliberately exposes no
# arrival-rate formula (docs/research/strategy-guide-full-decode-2026-09-16.md
# section 41 lists "客数発生式" as explicitly un-derivable from the guide).
# This module fills that gap with a tagged, playable placeholder rather than
# leaving demand generation entirely absent, per the project's "build one,
# play it, adjust what feels wrong" approach agreed for this pass. Retune or
# replace outright if real evidence surfaces.
DAILY_VISIT_RATE_PER_POPULATION = 0.05
"""Expected fraction of the (share-weighted) nearby population that visits
this store on a day it fully captures them. 5% is a round, unevidenced
starting guess -- a 2,000-population trade area at 50% share would then draw
~50 visitors/day, a plausible small-store range to start tuning from."""

DEFAULT_OPENING_MINUTES_PER_DAY = 16 * 60
"""Used only when CustomerShareInputs.opening_minutes_per_day is unknown;
matches the guide's own example schedule "AM7:00~PM11:00 (16時間営業)"."""

BAD_WEATHER_VISIT_MULTIPLIER = 0.6
"""Source for the *direction* of this effect (EXPLICIT_BEHAVIOR, not a
guess): the guide's Q&A says bad weather reduces visits from customers who
do not consider shopping important that day. Because store_runtime.py's
customer sessions are not yet linked to a specific archetype's per-visit
買物重要度 stat (demand generation itself is not implemented), this is
applied as a single aggregate multiplier on total expected arrivals rather
than a per-customer filter; the 0.6 magnitude itself is a
REMAKE_BALANCED_DEFAULT guess.
"""


@dataclass
class RemakeBalancedDemandPolicy:
    """Concrete, tagged-guess CustomerDemandPolicy.

    CustomerDemandContext carries no store layout information (entry/exit
    points, which fixtures exist), so a real policy must be configured with
    that out of band; this class takes it at construction time and only uses
    the per-tick context to decide *whether* (not where) a customer arrives.

    Intended to be evaluated roughly once per game-minute (matching
    SubdayClock's granularity); at most one arrival is produced per call, so
    a very high expected rate under-spawns rather than bursts multiple
    customers in one tick. That is an accepted simplification of this
    placeholder, not a claim about the original's concurrency.
    """

    entry_point: GridPoint
    exit_point: GridPoint
    merchandise_fixture_ids: tuple[str, ...] = ()
    checkout_fixture_id: Optional[str] = None
    daily_visit_rate_per_population: float = DAILY_VISIT_RATE_PER_POPULATION
    default_opening_minutes_per_day: int = DEFAULT_OPENING_MINUTES_PER_DAY
    bad_weather_visit_multiplier: float = BAD_WEATHER_VISIT_MULTIPLIER
    customer_id_prefix: str = "remake-demand"
    rng: random.Random = field(default_factory=random.Random)
    _next_sequence: int = field(default=1, init=False, repr=False)

    def expected_arrivals_per_minute(self, context: CustomerDemandContext) -> Optional[float]:
        """Exposed for tests/inspection; None when required inputs are unknown."""
        share = context.customer_share_percent
        population = context.share_inputs.nearby_population
        if share is None or population is None:
            return None
        minutes_open = context.share_inputs.opening_minutes_per_day
        if minutes_open is None or minutes_open <= 0:
            minutes_open = self.default_opening_minutes_per_day

        expected_daily_visitors = population * (share / 100.0) * self.daily_visit_rate_per_population
        if context.share_inputs.weather in BAD_WEATHER_VALUES:
            expected_daily_visitors *= self.bad_weather_visit_multiplier

        return expected_daily_visitors / minutes_open

    def arrivals_for(self, context: CustomerDemandContext) -> Sequence[CustomerArrivalIntent]:
        if context.store_open is not True:
            return ()

        rate = self.expected_arrivals_per_minute(context)
        if rate is None or rate <= 0:
            return ()

        if self.rng.random() >= min(1.0, rate):
            return ()

        customer_id = f"{self.customer_id_prefix}-{self._next_sequence}"
        self._next_sequence += 1
        return (
            CustomerArrivalIntent(
                customer_id,
                entry_point=self.entry_point,
                exit_point=self.exit_point,
                merchandise_fixture_ids=self.merchandise_fixture_ids,
                checkout_fixture_id=self.checkout_fixture_id,
            ),
        )
