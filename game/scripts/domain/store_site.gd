class_name StoreSite
extends RefCounted

# Task #95: where the player may open a store on the guide town map and
# what that land costs. Mirrors tools/build_guide_town_map.py's site_quote()
# (the contract test runs both on the same sites). Evidence per rule is in
# guide_town_map.store_site.evidence_note:
# - CONFIRMED_OFFICIAL: the store takes 2x2 squares (DATA4), land cost =
#   地価(4エリア分) + 建物評価額÷2, no store within 5 squares of another.
# - REMAKE_BALANCED_DEFAULT: the price shape (20,000,000 floor, +road,
#   +built-up share, rounded to the million) and the customer catchment
#   (building squares in the surrounding 16x16 area).

var rows: Array = []
var buildings: Array = []
var catalog: Dictionary = {}
var rules: Dictionary = {}
var width := 0
var height := 0
var footprint := Vector2i(2, 2)
# Map square -> index into `buildings`.
var _building_at: Dictionary = {}


func _init(guide_town_map: Dictionary) -> void:
    rows = guide_town_map["tile_rows"]
    buildings = guide_town_map["buildings"]
    catalog = guide_town_map["building_catalog"]
    rules = guide_town_map["store_site"]
    width = int(guide_town_map["width_tiles"])
    height = int(guide_town_map["height_tiles"])
    var size: Array = rules["footprint_tiles"]
    footprint = Vector2i(int(size[0]), int(size[1]))
    for index in buildings.size():
        var building: Dictionary = buildings[index]
        var tile: Array = building["tile"]
        var building_size: Array = building["size"]
        for y in range(int(tile[1]), int(tile[1]) + int(building_size[1])):
            for x in range(int(tile[0]), int(tile[0]) + int(building_size[0])):
                _building_at[Vector2i(x, y)] = index


func footprint_tiles(origin: Vector2i) -> Array[Vector2i]:
    var tiles: Array[Vector2i] = []
    for dy in footprint.y:
        for dx in footprint.x:
            tiles.append(origin + Vector2i(dx, dy))
    return tiles


func _kind(tile: Vector2i) -> String:
    if tile.x < 0 or tile.y < 0 or tile.x >= width or tile.y >= height:
        return ""
    return str(rows[tile.y])[tile.x]


func is_on_map(origin: Vector2i) -> bool:
    for tile in footprint_tiles(origin):
        if _kind(tile) == "":
            return false
    return true


func is_buildable_ground(origin: Vector2i) -> bool:
    if not is_on_map(origin):
        return false
    var unbuildable: Array = rules["unbuildable_tiles"]
    for tile in footprint_tiles(origin):
        if unbuildable.has(_kind(tile)):
            return false
    return true


func faces_road(origin: Vector2i) -> bool:
    for tile in footprint_tiles(origin):
        for step in [Vector2i(0, -1), Vector2i(1, 0), Vector2i(0, 1), Vector2i(-1, 0)]:
            if _kind(tile + step) == "R":
                return true
    return false


# Indices of the buildings (not already bought) standing on the site.
func buildings_on(origin: Vector2i, removed: Array = []) -> Array[int]:
    var found: Array[int] = []
    for tile in footprint_tiles(origin):
        if _building_at.has(tile):
            var index: int = _building_at[tile]
            if not found.has(index) and not removed.has(index):
                found.append(index)
    found.sort()
    return found


func building_at(tile: Vector2i, removed: Array = []) -> int:
    if not _building_at.has(tile) or removed.has(_building_at[tile]):
        return -1
    return int(_building_at[tile])


func building_name(index: int) -> String:
    return str(catalog[str(buildings[index]["sprite"])]["name"])


func building_value_yen(index: int) -> int:
    return int(catalog[str(buildings[index]["sprite"])]["price"]) * int(rules["building_price_unit_yen"])


# Building squares within catchment_tiles of the site; squares off the map
# count as empty (guide p.8: a store at the map edge gets no customers from
# beyond it).
func catchment_building_tiles(origin: Vector2i, removed: Array = []) -> int:
    var reach := int(rules["catchment_tiles"])
    var count := 0
    for y in range(origin.y - reach, origin.y + footprint.y + reach):
        for x in range(origin.x - reach, origin.x + footprint.x + reach):
            var tile := Vector2i(x, y)
            if _building_at.has(tile) and not removed.has(_building_at[tile]):
                count += 1
    return count


# Task #98: is a map square inside a store's catchment (the same square
# area catchment_building_tiles() counts)?
func in_catchment(store_origin: Vector2i, tile: Vector2i) -> bool:
    var reach := int(rules["catchment_tiles"])
    return (
        tile.x >= store_origin.x - reach and tile.x < store_origin.x + footprint.x + reach
        and tile.y >= store_origin.y - reach and tile.y < store_origin.y + footprint.y + reach
    )


# Task #98: building squares in the site's catchment, each counted as 1/n
# when n stores (this site included) have it in their catchment -- the
# customers of a building near two stores are shared between them.
# REMAKE_BALANCED_DEFAULT (tools/guide_store_site.py shared_catchment()).
func shared_catchment(origin: Vector2i, others: Array, removed: Array = []) -> float:
    var reach := int(rules["catchment_tiles"])
    var total := 0.0
    for y in range(origin.y - reach, origin.y + footprint.y + reach):
        for x in range(origin.x - reach, origin.x + footprint.x + reach):
            var tile := Vector2i(x, y)
            if not _building_at.has(tile) or removed.has(_building_at[tile]):
                continue
            var stores := 1
            for other in others:
                if in_catchment(other, tile):
                    stores += 1
            total += 1.0 / stores
    return total


# REMAKE_BALANCED_DEFAULT price shape (see the file header), before any
# growth over time.
func start_land_price_yen(origin: Vector2i) -> int:
    var density := float(catchment_building_tiles(origin)) / float(rules["max_catchment_building_tiles"])
    var price := float(rules["floor_land_price_yen"]) + float(rules["density_bonus_yen"]) * minf(1.0, density)
    if faces_road(origin):
        price += float(rules["road_bonus_yen"])
    var step := float(rules["price_step_yen"])
    return int(floor((price + step / 2.0) / step) * step)


# Nearby population a store on this site draws: the scenario's
# nearby_population scaled by this site's catchment against the mean site
# (REMAKE_BALANCED_DEFAULT, see the file header).
func nearby_population(origin: Vector2i, base_population: int, removed: Array = [], others: Array = []) -> int:
    var mean := float(rules["mean_catchment_building_tiles"])
    return int(round(float(base_population) * shared_catchment(origin, others, removed) / mean))


# Full quote for buying the site now. `growth` scales the land price for
# time passed since the start of the game; `other_stores` are the origins of
# every other store on the map; `removed` are buildings already bought.
func quote(origin: Vector2i, growth: float, other_stores: Array, removed: Array = []) -> Dictionary:
    var result := {
        "origin": origin,
        "buildable": false,
        "reason": "",
        "land_yen": 0,
        "building_yen": 0,
        "total_yen": 0,
        "bought_buildings": [],
        "label": "",
    }
    if not is_buildable_ground(origin):
        result["reason"] = "not_buildable_ground"
        return result
    var min_distance := int(rules["min_store_distance_tiles"])
    for other in other_stores:
        var other_origin: Vector2i = other
        if maxi(absi(origin.x - other_origin.x), absi(origin.y - other_origin.y)) < min_distance:
            result["reason"] = "too_close_to_store"
            return result
    var land_yen := int(round(float(start_land_price_yen(origin)) * growth))
    var bought := buildings_on(origin, removed)
    var building_value := 0
    var names: Array[String] = []
    for index in bought:
        building_value += building_value_yen(index)
        names.append(building_name(index))
    result["buildable"] = true
    result["land_yen"] = land_yen
    result["building_yen"] = building_value / 2
    result["total_yen"] = land_yen + building_value / 2
    result["bought_buildings"] = bought
    result["label"] = "・".join(names)
    return result
