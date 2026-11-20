extends RefCounted
# CONFIRMED_BINARY: 80063208 group step, 80063714 individual editor,
# 8003473C purchase price. 26 editable categories; cash26 is excluded.
static func step(values: Array, delta: int) -> Array:
    if values.size()!=26 or delta not in [-1,1]: return []
    var changed: Array = []
    for value in values:
        var next := int(value)+delta
        if next < 0 or next > 100: return []
        changed.append(next)
    return changed
static func unit(base: int, cost_percent: int, setting: int) -> int:
    return base*(cost_percent+setting)/100
