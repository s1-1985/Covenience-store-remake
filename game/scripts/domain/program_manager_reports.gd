extends RefCounted

# SLPS_007.82 8003BA40..8003BC88: canonical order, unsigned report counts.
# Best may have sold out; worst must still have stock. Strict comparisons
# preserve the first product index when counts tie.
static func candidates(counts: Dictionary, stocked: Array, order: Array) -> Dictionary:
    var best := ""
    var worst := ""
    for category in order.slice(0, 27):
        var id := str(category)
        var count := int(counts.get(id, 0)) & 0xffffffff
        if best.is_empty() or count > (int(counts.get(best, 0)) & 0xffffffff):
            best = id
        if stocked.has(id) and (worst.is_empty() or count < (int(counts.get(worst, 0)) & 0xffffffff)):
            worst = id
    return {"best": best, "worst": worst}
