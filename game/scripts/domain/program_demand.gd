class_name ProgramDemand
extends RefCounted

# --- CONFIRMED_BINARY house rule (task #130) ------------------------------
#
# Who comes to which store, as the PS program (SLPS_007.82) decides it; see
# docs/research/ps1-executable-formulas-2026-09-26.md. The tables are in
# config["ps1_program_tables"] (tools/ps1/extract_program_tables.py).
#
# Once a day, at 0:00 (0x8002619C): every town square with a customer mix
# sends each of its (visit row, head count) pairs to one store, unless
# - the row's 買物重要度 + 20 is below the day's weather value,
# - its goods are out of season (a summer item in Dec-Feb, a winter item in
#   Jun-Aug: 90% stay home; 0x80027328),
# - a 1-100 roll is above the row's 平日来店割合 (休日来店割合 on a holiday).
# The store (0x80026A64) is one that passes a 1-100 roll against 人気 + 20,
# is open at the row's hour, has parking for a car, has the row's goods on
# a shelf and is within the arrival's reach (walk 20, bicycle 40, motorbike
# 60, car 70 squares); the highest 値段の値 x 価格重視度 + 近さ x 距離重視度 +
# サービスの値 x サービス重視度 wins, then more of the goods, then more 人気.
# 値段の値 and サービスの値 are relative across the stores (0x80024740): the
# cheapest store 100, the best-served 100.
#
# Then every 2 game minutes (0x800319AC), with a 1 in 4 chance, an open
# store with room lets in one group: the first visit row (from a random
# start) that may come at this hour and still has heads left sends up to 5
# of them together.

var tables: Dictionary
var rows: Array
var mixes: Array
var _reach: Dictionary
var _closeness_min: int
var _closeness_max: int


func _init(program_tables: Dictionary) -> void:
    tables = program_tables
    rows = tables["visit_rows"]
    mixes = tables["customer_mixes"]
    _reach = tables["arrival_reach_squares"]
    _closeness_min = int(tables["closeness_squares"][0])
    _closeness_max = int(tables["closeness_squares"][1])


# The day's weather value from its category (0x800261AC): 快晴 0, then a
# random value inside the category's band.
func weather_value(category_index: int, rng: RandomNumberGenerator) -> int:
    var band: Array = tables["weather_value_bands"][clampi(category_index, 0, 4)]
    return rng.randi_range(int(band[0]), int(band[1]))


# month_index 0-11, day 1-4 (a month has four days, the program's clock).
func is_holiday(month_index: int, day: int) -> bool:
    return int(tables["holidays"][month_index % 12][clampi(day, 1, 4) - 1]) != 0


# True when the goods keep the customer home today (0x80027328).
func out_of_season(product: String, month_index: int, rng: RandomNumberGenerator) -> bool:
    var season := str(tables["product_seasons"].get(product, ""))
    if season.is_empty():
        return false
    var month := month_index % 12 + 1
    var off_months := [12, 1, 2] if season == "summer" else [6, 7, 8]
    return off_months.has(month) and rng.randi_range(1, 100) <= 90


# Whether a customer goes for one of their row's extra goods (0x800342AC):
# a seasonal item always in its season and 9 in 10 times not out of it;
# otherwise skipped when a 1-100 roll is at or under the row's 集中力.
func wants_extra(product: String, month_index: int, focus: int, rng: RandomNumberGenerator) -> bool:
    var season := str(tables["product_seasons"].get(product, ""))
    var month := month_index % 12 + 1
    if not season.is_empty():
        var in_months := [6, 7, 8] if season == "summer" else [12, 1, 2]
        if in_months.has(month):
            return true
        if out_of_season(product, month_index, rng):
            return false
    return rng.randi_range(1, 100) > focus


# One of the building type's five candidate mixes for a town square
# (REMAKE_BALANCED_DEFAULT: the program draws it when the map is made; here
# it follows from the square's position so it needs no saving).
func square_mix(catalog_id: String, square: Vector2i) -> int:
    var entry: Dictionary = tables["building_types"].get(catalog_id, {})
    if entry.is_empty():
        return -1
    var candidates: Array = entry["mix_candidates"]
    return int(candidates[(square.x * 7 + square.y * 13) % candidates.size()])


func mix_heads(mix_id: int) -> int:
    var total := 0
    if mix_id < 0 or mix_id >= mixes.size():
        return 0
    for pair in mixes[mix_id]:
        total += int(pair[1])
    return total


# 値段の値 and サービスの値 for each store (0x80024740): 100 for the cheapest /
# best-served store, 0 for the dearest / worst, in proportion between; 100
# for everyone when they are all the same.
func relative_values(stores: Array) -> void:
    var price_min := 10000
    var price_max := -10000
    var service_min := 10000
    var service_max := -10000
    for store in stores:
        price_min = mini(price_min, int(store["price_percent"]))
        price_max = maxi(price_max, int(store["price_percent"]))
        service_min = mini(service_min, int(store["service"]))
        service_max = maxi(service_max, int(store["service"]))
    for store in stores:
        store["price_value"] = 100 if price_max == price_min else 100 - (int(store["price_percent"]) - price_min) * 100 / (price_max - price_min)
        store["service_value"] = 100 if service_max == service_min else (int(store["service"]) - service_min) * 100 / (service_max - service_min)


# Squares from a town square to a store's site (0 inside it).
func distance_to(store: Dictionary, square: Vector2i) -> int:
    var site: Rect2i = store["site"]
    var dx := maxi(site.position.x - square.x, square.x - (site.end.x - 1))
    var dy := maxi(site.position.y - square.y, square.y - (site.end.y - 1))
    return dx + dy


# The store a row's customers from `square` go to, or -1 (0x80026A64).
func choose_store(row: Dictionary, square: Vector2i, stores: Array, rng: RandomNumberGenerator) -> int:
    var best := -1
    var best_score := 0
    var best_stock := 0
    var best_popularity := 0
    var product := str(row["primary"])
    for index in stores.size():
        var store: Dictionary = stores[index]
        if rng.randi_range(1, 100) > int(store["popularity"]) + int(tables["popularity_bonus"]):
            continue
        if not bool(store["open_hours"][int(row["start_hour"]) % 24]):
            continue
        if str(row["arrival"]) == "自動車" and int(store["parking"]) <= 0:
            continue
        var stock := int(store["stock"].get(product, 0))
        if stock <= 0:
            continue
        var distance := distance_to(store, square)
        if distance > int(_reach[str(row["arrival"])]):
            continue
        var closeness := 100 - (distance - _closeness_min) * 100 / (_closeness_max - _closeness_min)
        var score: int = (
            int(store["price_value"]) * int(row["price_sensitivity"])
            + closeness * int(row["distance_sensitivity"])
            + int(store["service_value"]) * int(row["service_sensitivity"])
        )
        var better := best < 0 or score > best_score
        if not better and score == best_score:
            better = stock > best_stock or (stock == best_stock and int(store["popularity"]) > best_popularity)
        if better:
            best = index
            best_score = score
            best_stock = stock
            best_popularity = int(store["popularity"])
    return best


# The day's customers for each store: an Array (one per store) of
# {row index: heads}. `squares` is [[Vector2i, mix id], ...].
func allocate_day(
    squares: Array, stores: Array, weather: int, holiday: bool, month_index: int, rng: RandomNumberGenerator
) -> Array:
    relative_values(stores)
    var counts: Array = []
    for store in stores:
        counts.append({})
    for entry in squares:
        var square: Vector2i = entry[0]
        for pair in mixes[int(entry[1])]:
            var row_index := int(pair[0])
            var row: Dictionary = rows[row_index]
            if int(row["shopping_importance"]) + int(tables["weather_importance_bonus"]) < weather:
                continue
            if out_of_season(str(row["primary"]), month_index, rng):
                continue
            var share := int(row["holiday_share"]) if holiday else int(row["weekday_share"])
            if rng.randi_range(1, 100) > share:
                continue
            var chosen := choose_store(row, square, stores, rng)
            if chosen < 0:
                continue
            var store_counts: Dictionary = counts[chosen]
            store_counts[row_index] = int(store_counts.get(row_index, 0)) + int(pair[1])
    return counts


# The next group to let in, [row index, heads] or [] (0x800319AC). Takes
# the heads out of `counts`.
func next_group(counts: Dictionary, hour: int, holiday: bool, rng: RandomNumberGenerator) -> Array:
    var window: Array = tables["visit_hours"]["holiday" if holiday else "weekday"][hour % 24]
    var start := rng.randi_range(0, rows.size() - 1)
    for step in rows.size():
        var row_index := (start + 1 + step) % rows.size()
        var heads := int(counts.get(row_index, 0))
        if heads <= 0 or int(window[int(rows[row_index]["start_hour"]) % 24]) == 0:
            continue
        var group := mini(heads, int(tables["max_group_size"]))
        counts[row_index] = heads - group
        return [row_index, group]
    return []
