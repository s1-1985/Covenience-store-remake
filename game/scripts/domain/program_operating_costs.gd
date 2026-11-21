extends RefCounted

# CONFIRMED_BINARY: existing operating_costs.py, 8001D8AC/D980/DB5C/DBE4/DD7C.
# Source hourly rates, intermediate products and totals are signed32 words.
const Width = preload("res://scripts/domain/operating_statement.gd")

static func wage(hourly: int, manager: bool, hours: int) -> int:
    hourly = Width.signed32(hourly)
    if manager:
        hourly = Width.signed32(hourly * 130) / 100
    return Width.signed32(hourly * hours)

static func maintenance(kinds: Array, rates: Array, hours: int) -> int:
    var total := 0
    for kind in kinds:
        # Original anchor scan excludes kind53+ before reading the rate table.
        if int(kind) >= 0 and int(kind) < 53:
            total = Width.signed32(total + Width.signed32(int(rates[int(kind)][2]) * hours))
    return total
