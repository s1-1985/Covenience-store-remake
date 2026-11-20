extends RefCounted
# CONFIRMED_BINARY: SLPS_007.82 800B92D0 fees, 8001E660 rectangle
# query, 8001F8BC masks. Selection bits and map bits differ.
const IDS := ["tobacco", "alcohol", "medicine"]
const NAMES := {"tobacco":"たばこ","alcohol":"酒類","medicine":"薬品類"}
const FEES := {"tobacco":3000000,"alcohol":7000000,"medicine":10000000}
const MAP_BITS := {"tobacco":4,"alcohol":2,"medicine":1}
static func restricted(cells: Array, rect: Rect2i, permit_id: String) -> bool:
    if not MAP_BITS.has(permit_id): return true
    if rect.position.x < 0 or rect.position.y < 0 or rect.end.x > 60 or rect.end.y > 50 or not rect.has_area(): return true
    var bit: int = MAP_BITS[permit_id]
    for y in range(rect.position.y,rect.end.y):
        for x in range(rect.position.x,rect.end.x):
            if int(cells[y*60+x][4]) & bit: return true
    return false
