extends RefCounted
# CONFIRMED_BINARY: SLPS_007.82 800470E4..800478F8, 344C4, 34AE4.
# Source calls and integer examples: tests/fixtures/source_survey.json.
const MASK := 0xffffffff
static func add(counts: Dictionary, category: String, heads: int) -> void:
    if not category.is_empty():
        counts[category] = (int(counts.get(category,0)) + heads) & MASK
static func rank(counts: Dictionary, product_order: Array) -> Array:
    var rows: Array = []
    for i in mini(27,product_order.size()):
        var id := str(product_order[i])
        var count := int(counts.get(id,0)) & MASK
        if count > 0: rows.append({"id":id,"index":i,"count":count})
    rows.sort_custom(func(a,b):
        return a.count > b.count if a.count != b.count else a.index < b.index)
    return rows.slice(0,8)
