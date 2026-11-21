extends RefCounted

# SLPS_007.82 8003CFB8..8003D504. Entries follow the caller's active-store
# order; even a unique winner consumes the tie-break RNG call.
static func choose(entries: Array, kind: String, rng) -> Dictionary:
    if kind not in ["contest", "popular", "clean", "service", "cheap"]: return {}
    var active := entries.slice(0, 10)
    if active.size() < 5: return {}
    var best := -1000
    for entry in active: best = maxi(best, int(entry.value))
    if kind == "cheap" and best <= 0: return {}
    var winners: Array = active.filter(func(entry): return int(entry.value) >= best)
    return winners[rng.randi() % winners.size()]
