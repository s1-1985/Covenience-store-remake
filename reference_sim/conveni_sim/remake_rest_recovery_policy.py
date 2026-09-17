from __future__ import annotations

import random
from dataclasses import dataclass, field
from typing import Dict, Optional

from .staff_rest_timing import StaffRestTimingContext

# --- REMAKE_BALANCED_DEFAULT house rule ---------------------------------
#
# staff_rest_recovery.py's RestRecoveryBonusPolicy protocol deliberately
# exposes no probability curve for the observed agility-linked +1 stamina
# recovery bonus (PROJECT_MEMORY.md section 6: "Agility relates to...
# appears to affect stamina recovery probability" -- EXPLICIT_BEHAVIOR for
# the existence of the link, no rate). `StaffRestTimingContext` also carries
# no agility value, so a real policy needs it supplied out of band; this
# class takes a `staff_id -> agility` lookup at construction. A
# REMAKE_BALANCED_DEFAULT placeholder, not a recovered original formula --
# expected to be retuned or replaced after actual play.
AGILITY_TO_BONUS_PROBABILITY_SCALE = 1.0 / 100.0
"""agility is already 0-100 like every other staff stat; this scale turns it
directly into a 0-100% chance (agility=100 -> always get the bonus tick,
agility=50 -> half the time), the simplest monotonic mapping available
without further evidence."""


@dataclass
class RemakeBalancedRestRecoveryBonusPolicy:
    """Concrete, tagged-guess RestRecoveryBonusPolicy (see module docstring)."""

    agility_by_staff_id: Dict[str, int]
    scale: float = AGILITY_TO_BONUS_PROBABILITY_SCALE
    rng: random.Random = field(default_factory=random.Random)

    def bonus_applies(self, context: StaffRestTimingContext) -> Optional[bool]:
        agility = self.agility_by_staff_id.get(context.staff_id)
        if agility is None:
            return None
        probability = max(0.0, min(1.0, agility * self.scale))
        return self.rng.random() < probability
