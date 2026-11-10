extends RefCounted
## Issue #232: candidate-only NESW direction lookup.
## Standalone helper. NOT integrated into game/scripts/town_view.gd.
## Do not treat returned paths as production-approved textures.
## The caller must arrange read-only access to the isolated registry/assets.
##
## Bits: N=1, E=2, S=4, W=8. Mask 0 is not an asset.
const KINDS: Array[String] = ["road", "rail", "river"]


static func mask_from_neighbors(n: bool, e: bool, s: bool, w: bool) -> int:
    var mask := 0
    if n:
        mask |= 1
    if e:
        mask |= 2
    if s:
        mask |= 4
    if w:
        mask |= 8
    return mask


static func candidate_id(kind: String, mask: int) -> String:
    if not KINDS.has(kind) or mask < 1 or mask > 15:
        return ""
    var suffix := ""
    if (mask & 1) != 0:
        suffix += "n"
    if (mask & 2) != 0:
        suffix += "e"
    if (mask & 4) != 0:
        suffix += "s"
    if (mask & 8) != 0:
        suffix += "w"
    return kind + "_" + suffix


## Returns an empty dictionary for any malformed/incomplete registry.
## Accepts the existing connection_45_candidate_registry_2026-10-30.json.
static func index_registry(registry: Dictionary) -> Dictionary:
    var result: Dictionary = {}
    var assets: Array = registry.get("assets", [])
    if assets.size() != 45:
        return {}
    for item in assets:
        if not item is Dictionary:
            return {}
        var kind: String = str(item.get("kind", ""))
        var mask: int = int(item.get("direction_bits_nesw", 0))
        var key: String = candidate_id(kind, mask)
        if key.is_empty() or str(item.get("asset_id", "")) != key or result.has(key):
            return {}
        if str(item.get("candidate_path", "")).is_empty():
            return {}
        result[key] = item
    for kind in KINDS:
        for mask in range(1, 16):
            if not result.has(candidate_id(kind, mask)):
                return {}
    return result


static func candidate_for(index: Dictionary, kind: String, mask: int) -> Dictionary:
    var key: String = candidate_id(kind, mask)
    if key.is_empty():
        return {}
    return index.get(key, {})
