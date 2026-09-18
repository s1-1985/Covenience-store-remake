class_name CheckoutTiming
extends RefCounted

# REMAKE_BALANCED_DEFAULT, not a recovered original formula. The guide
# confirms register_skill has a large qualitative effect on checkout speed
# ("the lowest register skill can be so slow that one customer may
# effectively take a whole game day to process, while high-skill staff can
# become extremely fast" -- CONFIRMED_COMMUNITY/QUALITATIVE,
# docs/research/checkout-staff-dispatch-evidence-2026-09-05.md section 5),
# but that same note explicitly states no numeric seconds/ticks-per-skill
# formula should be invented from it. This inverse-proportion mapping is
# therefore this project's own tagged placeholder to retune after
# playtesting.
#
# REFERENCE_REGISTER_SKILL is not an arbitrary number: it is the median
# register_skill across the 35 CONFIRMED_OFFICIAL named staff candidates in
# reference_sim/conveni_sim/baseline_data.py's STAFF_CANDIDATES (task #32).
# `data/vertical_slice.json`'s existing `simulation.checkout_ticks` config
# value is reinterpreted as "ticks required at REFERENCE_REGISTER_SKILL"
# rather than a flat universal duration, so a staff member exactly at the
# reference skill sees no behavior change from before this task.
const REFERENCE_REGISTER_SKILL := 13
const MIN_CHECKOUT_TICKS := 1


func required_ticks(register_skill: int, reference_ticks: int) -> int:
    assert(register_skill >= 0)
    assert(reference_ticks > 0)
    if register_skill <= 0:
        # No confirmed behavior exists for a zero-skill staff member; treat
        # it as the slowest representable case rather than dividing by zero.
        return reference_ticks * REFERENCE_REGISTER_SKILL
    var scaled: float = (
        float(reference_ticks) * float(REFERENCE_REGISTER_SKILL) / float(register_skill)
    )
    return max(MIN_CHECKOUT_TICKS, int(round(scaled)))
