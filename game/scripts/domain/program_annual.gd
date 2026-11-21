extends RefCounted
# CONFIRMED_BINARY 80029C14..29C70 adds monthly columns as signed32;
# 80029FC8..2A0B0 shifts three previous annual records, then clears current.
static func add_sales(current: int, monthly: int) -> int:
    return ((current+monthly+0x80000000)&0xffffffff)-0x80000000

static func rollover(current: int, previous: Array) -> Array:
    var values: Array = [current]
    for value in previous.slice(0,2):values.append(int(value))
    return values

static func valid_history(value: Variant) -> bool:
    if not value is Array or value.size()>3:return false
    for item in value:
        if (not item is int and not item is float) or float(item)!=floorf(float(item)) or item< -2147483648 or item>2147483647:return false
    return true
