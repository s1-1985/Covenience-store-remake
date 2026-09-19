class_name RestockTiming
extends RefCounted

# REMAKE_BALANCED_DEFAULT, not a recovered original formula. This project's
# own qualitative research notes confirm replenishment_skill has a real
# effect on restock throughput -- "Early low-skill staff clean slowly
# because they are also occupied with replenishment and other tasks"
# (CONFIRMED_COMMUNITY/DIRECT-PLAY-SS,
# docs/research/ss-early-store-operations-and-acquisition-2026-09-06.md
# section 4) and "agility bounds replenishment"
# (docs/research/checkout-staff-dispatch-evidence-2026-09-05.md section 6)
# -- but neither source, nor any other collected research note, states a
# numeric seconds/ticks-per-skill formula. This inverse-proportion mapping
# reuses the exact shape CheckoutTiming (task #33) already established for
# register_skill, applied here to replenishment_skill; it is this project's
# own tagged placeholder to retune after playtesting, not a claim about the
# original title's restock formula.
#
# REFERENCE_REPLENISHMENT_SKILL is not an arbitrary number: it is the
# median replenishment_skill across the 35 CONFIRMED_OFFICIAL named staff
# candidates in reference_sim/conveni_sim/baseline_data.py's
# STAFF_CANDIDATES (task #32), the same sourcing CheckoutTiming used for
# REFERENCE_REGISTER_SKILL. `data/vertical_slice.json`'s existing
# `simulation.restock_ticks` config value is reinterpreted as "ticks
# required at REFERENCE_REPLENISHMENT_SKILL" rather than a flat universal
# duration, so a staff member exactly at the reference skill sees no
# behavior change from before this task.
const REFERENCE_REPLENISHMENT_SKILL := 13
const MIN_RESTOCK_TICKS := 1


func required_ticks(replenishment_skill: int, reference_ticks: int) -> int:
    assert(replenishment_skill >= 0)
    assert(reference_ticks > 0)
    if replenishment_skill <= 0:
        # No confirmed behavior exists for a zero-skill staff member; treat
        # it as the slowest representable case rather than dividing by zero.
        return reference_ticks * REFERENCE_REPLENISHMENT_SKILL
    var scaled: float = (
        float(reference_ticks) * float(REFERENCE_REPLENISHMENT_SKILL) / float(replenishment_skill)
    )
    return max(MIN_RESTOCK_TICKS, int(round(scaled)))
