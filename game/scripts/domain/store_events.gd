class_name StoreEvents
extends RefCounted

# --- CONFIRMED_OFFICIAL house rule ----------------------------------------
#
# Ported verbatim from reference_sim/conveni_sim/store_events.py's
# magazine_or_contest_event_is_eligible()/compute_contest_prize_yen(). The
# strategy guide's event-trigger table states the eligibility gate
# ("人口1万人以上 かつ マップ内に5店舗以上") and the prize formula
# ("店舗数(ライバル店を含む)×1000万円") as CONFIRMED_OFFICIAL. Whether the
# event actually fires once eligible is described as "選ばれることもある"
# (may or may not be picked) -- an unconfirmed, undocumented draw -- so
# this class exposes only the deterministic eligibility gate and prize
# amount, and never rolls or auto-applies the event itself.

const TOWN_POPULATION_THRESHOLD := 10000
const STORE_COUNT_THRESHOLD := 5
const CONTEST_PRIZE_YEN_PER_STORE := 10000000


func magazine_or_contest_event_is_eligible(
    town_population: int, store_count_including_rivals: int
) -> bool:
    assert(town_population >= 0)
    assert(store_count_including_rivals >= 0)
    return (
        town_population >= TOWN_POPULATION_THRESHOLD
        and store_count_including_rivals >= STORE_COUNT_THRESHOLD
    )


func compute_contest_prize_yen(store_count_including_rivals: int) -> int:
    assert(store_count_including_rivals >= 0)
    return store_count_including_rivals * CONTEST_PRIZE_YEN_PER_STORE
