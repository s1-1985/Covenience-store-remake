from __future__ import annotations

from dataclasses import dataclass


@dataclass
class TownState:
    """Caller-tracked town-level facts the guide's event-eligibility checks
    need (store_events.py's `magazine_or_contest_event_is_eligible` /
    `compute_contest_prize_yen`; docs/research/strategy-guide-fixture-
    crosscheck-2026-09-16.md section 7).

    This is deliberately just tracked state, not a town/map simulation:
    `reference_sim` has no spatial model of the town map, facility
    placement, or population-growth rules. Those remain documented UNKNOWN
    research gaps (PROJECT_MEMORY.md section 17: "町発展の一般式" and
    related items are explicitly not to be invented). A caller -- a test, or
    a future town/map layer -- is responsible for keeping `population` and
    `store_count_including_rivals` current; this class only holds the two
    numbers store_events.py's eligibility checks are defined in terms of, so
    a caller has one obvious place to put them rather than passing bare ints
    around.

    Security-facility coverage (police box / fire station tile counts within
    a store's 16x16 range, used by store_value.compute_security_value and
    store_events.FireOrRobberyRisk) is deliberately NOT modeled here either,
    for the same reason: no spatial facility-placement data exists yet. A
    caller supplies a `store_value.SecurityFacilityCoverage` directly to
    those call sites once/if that spatial layer exists.
    """

    population: int = 0
    store_count_including_rivals: int = 0

    def __post_init__(self) -> None:
        if self.population < 0:
            raise ValueError("population must be >= 0")
        if self.store_count_including_rivals < 0:
            raise ValueError("store_count_including_rivals must be >= 0")
