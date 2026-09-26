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
    # A copy: buildings induced during a game (task #111) are added to it.
    buildings = (guide_town_map["buildings"] as Array).duplicate(true)
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


# Task #102: each building in the site's catchment and the share of its
# squares that belong to this store (1/n per square when n stores reach it),
# as {building index: weight}.
func catchment_building_weights(origin: Vector2i, others: Array, removed: Array = []) -> Dictionary:
    var reach := int(rules["catchment_tiles"])
    var weights := {}
    for y in range(origin.y - reach, origin.y + footprint.y + reach):
        for x in range(origin.x - reach, origin.x + footprint.x + reach):
            var tile := Vector2i(x, y)
            if not _building_at.has(tile) or removed.has(_building_at[tile]):
                continue
            var stores := 1
            for other in others:
                if in_catchment(other, tile):
                    stores += 1
            var index: int = _building_at[tile]
            weights[index] = float(weights.get(index, 0.0)) + 1.0 / stores
    return weights


func building_profile(index: int) -> Dictionary:
    return catalog[str(buildings[index]["sprite"])]


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


# Task #106: how hard the player's stores press a rival this month --
# the share of the rival's catchment building squares that are also in a
# player store's catchment, times the price cut against the cut that has
# full effect. REMAKE_BALANCED_DEFAULT shape (guide_town_map.rival_ai,
# tools/guide_store_site.py rival_pressure()).
func rival_pressure(
    rival_origin: Vector2i, player_origins: Array, price_change_pct: int,
    full_effect_cut_pct: int, removed: Array = []
) -> float:
    var reach := int(rules["catchment_tiles"])
    var mine := 0
    var shared := 0
    for y in range(rival_origin.y - reach, rival_origin.y + footprint.y + reach):
        for x in range(rival_origin.x - reach, rival_origin.x + footprint.x + reach):
            var tile := Vector2i(x, y)
            if not _building_at.has(tile) or removed.has(_building_at[tile]):
                continue
            mine += 1
            for origin in player_origins:
                if in_catchment(origin, tile):
                    shared += 1
                    break
    if mine == 0:
        return 0.0
    var cut := minf(1.0, float(maxi(0, -price_change_pct)) / float(full_effect_cut_pct))
    return float(shared) / float(mine) * cut


# Task #106: the vacant 2x2 site a rival opens a store on -- the one whose
# customers (shared with the other stores) are the most, at least
# min_store_distance_tiles from every store and from the `avoid` sites
# (where it just withdrew from), top-left-most on a tie; (-1, -1) when
# there is none. Same rule as tools/guide_store_site.py
# best_open_site() / place_rivals() (REMAKE_BALANCED_DEFAULT).
func best_open_site(stores: Array, removed: Array = [], avoid: Array = []) -> Vector2i:
    var min_distance := int(rules["min_store_distance_tiles"])
    var best := Vector2i(-1, -1)
    var best_score := -1.0
    for y in height:
        for x in width:
            var origin := Vector2i(x, y)
            if not is_buildable_ground(origin) or not buildings_on(origin, removed).is_empty():
                continue
            var too_close := false
            for other in stores + avoid:
                var other_origin: Vector2i = other
                if maxi(absi(x - other_origin.x), absi(y - other_origin.y)) < min_distance:
                    too_close = true
                    break
            if too_close:
                continue
            var score := shared_catchment(origin, stores, removed)
            if score > best_score + 1e-9:
                best_score = score
                best = origin
    return best


# Task #111: a building put up during the game (誘致). Returns its index;
# the squares it covers now belong to it (the buildings that stood there
# are the caller's to mark removed, see buildings_under()).
func add_building(sprite: String, tile: Vector2i, size: Vector2i) -> int:
    var index := buildings.size()
    buildings.append({"sprite": sprite, "tile": [tile.x, tile.y], "size": [size.x, size.y]})
    for y in range(tile.y, tile.y + size.y):
        for x in range(tile.x, tile.x + size.x):
            _building_at[Vector2i(x, y)] = index
    return index


# Indices of the buildings (not already removed) with a square inside the
# rectangle.
func buildings_under(tile: Vector2i, size: Vector2i, removed: Array = []) -> Array[int]:
    var found: Array[int] = []
    for y in range(tile.y, tile.y + size.y):
        for x in range(tile.x, tile.x + size.x):
            var at := Vector2i(x, y)
            if _building_at.has(at) and not removed.has(_building_at[at]) and not found.has(_building_at[at]):
                found.append(_building_at[at])
    found.sort()
    return found


func rect_is_buildable(tile: Vector2i, size: Vector2i) -> bool:
    var unbuildable: Array = rules["unbuildable_tiles"]
    for y in range(tile.y, tile.y + size.y):
        for x in range(tile.x, tile.x + size.x):
            var kind := _kind(Vector2i(x, y))
            if kind == "" or unbuildable.has(kind):
                return false
    return true
