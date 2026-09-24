from __future__ import annotations

from dataclasses import dataclass

# Task #62: CONFIRMED_COMMUNITY, two independent sources agree exactly --
# the first-title wiki's own game-mode-strategy page states a combined
# player+rival cap of 10 stores per map (docs/research/first-title-wiki-
# full-scan-delta-2026-09-05.md: "プレイヤー+ライバル合計10店舗上限"), and a
# PS long-play record independently reaches "プレイヤー5店+ライバル5店に
# なった時点で、これ以上新店舗は造れない" (docs/research/ps-longplay-rival-
# economy-events-2026-09-05.md section 5). This is a hard construction cap
# on the whole map, not the intermediate scenario's separate "10 player
# stores" clear condition (baseline_data.SCENARIOS' `objective` field) --
# the two are different facts that happen to share the number 10.
TOTAL_STORE_CAP_INCLUDING_RIVALS = 10


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

    def has_capacity_for_new_store(self) -> bool:
        """CONFIRMED_COMMUNITY: whether the map can still fit another store
        of either side, per `TOTAL_STORE_CAP_INCLUDING_RIVALS`'s own note.
        Callers (player construction, rival expansion) should check this
        before adding a store and increment `store_count_including_rivals`
        themselves once the store is actually built -- this method does not
        mutate state, matching this class's existing caller-tracked design."""

        return self.store_count_including_rivals < TOTAL_STORE_CAP_INCLUDING_RIVALS
