extends RefCounted
# SLPS_007.82 8003BF28: finance/owner gates before two shared RNG calls.
static func signed32(value: int) -> int:
    value &= 0xffffffff
    return value-0x100000000 if value >= 0x80000000 else value

static func eligible(rival: bool, security: int, popularity: int, heads: int, last_sales: int, sales: int, assets: int) -> bool:
    return financial_gate(rival,security,popularity,heads,last_sales,sales) and signed32(assets) > 99999

static func financial_gate(rival: bool, security: int, popularity: int, heads: int, last_sales: int, sales: int) -> bool:
    return not rival and security < popularity and (heads & 0xffffffff) >= 2000 and signed32(last_sales) > 999999 and signed32(sales) > 99999

static func draw(rng) -> int:
    var kind := 0 if rng.randi() % 128 == 100 else -1
    if rng.randi() % 256 == 100: kind = 1
    return kind
