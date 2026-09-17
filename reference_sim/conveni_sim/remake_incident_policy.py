from __future__ import annotations

import random
from dataclasses import dataclass, field

from .store_events import FireOrRobberyRisk, shoplifting_is_possible

# --- REMAKE_BALANCED_DEFAULT house rule ---------------------------------
#
# store_events.py's shoplifting_is_possible()/FireOrRobberyRisk are
# deterministic eligibility checks only: the guide gives a hard boundary
# condition for each (万引き: 顧客のマナー値 > 店舗の警備値; 火災/強盗: no
# security facility in range, "more likely" when popularity exceeds
# security) but never an actual per-day probability
# (docs/research/strategy-guide-full-decode-2026-09-16.md section 41 lists
# both under "存在が確定したが数式は未確定"). This module adds the missing
# probability roll on top of those confirmed eligibility checks. A
# REMAKE_BALANCED_DEFAULT placeholder, not a recovered original formula --
# expected to be retuned or replaced after actual play.
FIRE_OR_ROBBERY_BASE_DAILY_PROBABILITY = 0.02
"""Chance per representative day that an eligible (risk_factors_present)
store actually suffers a fire/robbery. 2% keeps this a rare-but-real threat
across a multi-year playthrough rather than either never happening or
happening every few days."""

FIRE_OR_ROBBERY_POPULARITY_EXCESS_MULTIPLIER = 2.0
"""Applied on top of the base probability when popularity_exceeds_security
is also true, reflecting the guide's own qualitative "警備値より人気が高い
と発生しやすい" (more likely) hint; the multiplier's exact size is a guess."""

SHOPLIFTING_BASE_DAILY_PROBABILITY = 0.05
"""Chance per representative day that an eligible
(customer_manner_value > store_security_value) store actually experiences a
shoplifting incident, rather than every eligible day guaranteeing one."""


@dataclass
class RemakeBalancedIncidentPolicy:
    """Concrete probability layer over store_events.py's deterministic
    eligibility checks (see module docstring)."""

    fire_or_robbery_base_probability: float = FIRE_OR_ROBBERY_BASE_DAILY_PROBABILITY
    fire_or_robbery_popularity_excess_multiplier: float = FIRE_OR_ROBBERY_POPULARITY_EXCESS_MULTIPLIER
    shoplifting_base_probability: float = SHOPLIFTING_BASE_DAILY_PROBABILITY
    rng: random.Random = field(default_factory=random.Random)

    def fire_or_robbery_occurs_today(self, risk: FireOrRobberyRisk) -> bool:
        if not risk.risk_factors_present:
            return False
        probability = self.fire_or_robbery_base_probability
        if risk.popularity_exceeds_security:
            probability *= self.fire_or_robbery_popularity_excess_multiplier
        probability = min(1.0, probability)
        return self.rng.random() < probability

    def shoplifting_occurs_today(
        self,
        customer_manner_value: int,
        store_security_value: float,
    ) -> bool:
        if not shoplifting_is_possible(customer_manner_value, store_security_value):
            return False
        return self.rng.random() < self.shoplifting_base_probability
