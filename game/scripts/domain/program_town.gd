class_name ProgramTown
extends RefCounted

# CONFIRMED_BINARY: 8002BD54 town_monthly, 8001F1C0/1F4B4 mutation helpers.
# Port of the already source-checked models, not an emulator or a growth-rate fit.
var cells: Array
var table: Array
var groups: Array
var seed := 0
var tier := 0
var actions: Array = []
var _kind_for_tile: Array[int] = []
const FACILITY_KINDS := {"police_box": 18, "fire_station": 19, "apartment": 49, "company": 42, "gym": 51, "pool": 53, "athletic_field": 52, "event_hall": 54, "kindergarten": 25, "elementary_school": 26, "middle_school": 27, "high_school": 28, "university": 29, "vocational_school": 30, "park": 35, "aquarium": 32, "zoo": 33, "amusement_park": 31}


func _init(data: Dictionary) -> void:
    cells = data["town_cells"].duplicate(true)
    table = data["buildings"]
    groups = data["groups"]
    _kind_for_tile.resize(640)
    _kind_for_tile.fill(0)
    for d in table:
        for tile in range(int(d["lower"]), int(d["upper"]) + 1):
            _kind_for_tile[tile] = int(d["id"])


func draw() -> int:
    seed = (seed * 1103515245 + 12345) & 0xffffffff
    return (seed >> 16) & 0x7fff


static func signed_byte(value: int) -> int:
    return ((value + 128) & 255) - 128


static func div0(a: int, b: int) -> int:
    return int(float(a) / float(b))


func kind(x: int, y: int) -> int:
    return _kind_for_tile[int(cells[y * 60 + x][0])]


func level(x: int, y: int) -> int:
    return int(cells[y * 60 + x][1])


func population(category: int = 0) -> int:
    var total := 0
    for c in cells:
        var g := int(c[5])
        if g < 0 or (category != 0 and int(c[3]) != category):
            continue
        for pair in groups[g]:
            if int(pair[0]) != -1:
                total += int(pair[1])
    return total


func replace_cell(x: int, y: int, d: Dictionary, tile_id: int) -> void:
    var c: Array = cells[y * 60 + x]
    c[0] = tile_id
    c[2] = int(d["attribute"])
    c[3] = int(d["category"])
    c[4] = (int(c[4]) | 24) if int(c[3]) > 0 else (int(c[4]) & ~24)
    c[5] = int(d["groups"][draw() % 5])


func demolish(x: int, y: int, mode: int = 0) -> void:
    var d: Dictionary = table[kind(x, y)]
    var width := int(d["width"])
    var v := int(cells[y * 60 + x][0]) - int(d["lower"])
    x -= v - div0(v, width) * width
    y -= div0(int(cells[y * 60 + x][0]) - int(d["lower"]), width)
    for yy in range(y, y + int(d["height"])):
        for xx in range(x, x + width):
            var replacement: Dictionary = table[9 + draw() % 5] if mode == 1 else table[12]
            replace_cell(xx, yy, replacement, int(replacement["lower"]))


func place(x: int, y: int, id: int, mode: int = 0) -> void:
    var d: Dictionary = table[id]
    var tile_id := int(d["lower"])
    for yy in range(y, y + int(d["height"])):
        for xx in range(x, x + int(d["width"])):
            if xx < 0 or yy < 0 or xx >= 60 or yy >= 50:
                continue
            if int(cells[yy * 60 + xx][3]) > 0:
                demolish(xx, yy, mode)
            replace_cell(xx, yy, d, tile_id)
            tile_id += 1


func rebuild_flags(stores: Array) -> void:
    for c in cells:
        var category := int(c[3])
        c[4] = 0 if category <= 0 else (16 if category in [3, 4, 5] else 24)
    for store in stores:
        if not bool(store["active"]):
            continue
        var r: Array = store["rect"]
        for y in range(maxi(0, int(r[1]) - 10), mini(49, int(r[3]) + 10) + 1):
            for x in range(maxi(0, int(r[0]) - 10), mini(59, int(r[2]) + 10) + 1):
                var c: Array = cells[y * 60 + x]
                if int(store["c76"]) != 0:
                    c[4] = int(c[4]) | 1
                if x >= int(r[0]) - 7 and x <= int(r[2]) + 7 and y >= int(r[1]) - 7 and y <= int(r[3]) + 7 and int(store["c75"]) != 0:
                    c[4] = int(c[4]) | 2
                if x >= int(r[0]) - 5 and x <= int(r[2]) + 5 and y >= int(r[1]) - 5 and y <= int(r[3]) + 5 and int(store["c74"]) != 0:
                    c[4] = int(c[4]) | 4
                if x >= int(r[0]) - 4 and x <= int(r[2]) + 4 and y >= int(r[1]) - 4 and y <= int(r[3]) + 4:
                    c[4] = int(c[4]) | 8


func nearby(x: int, y: int, id: int, radius: int) -> bool:
    var d: Dictionary = table[id]
    var lo := int(table[20]["lower"]) if id in [20, 21] else int(d["lower"])
    var hi := int(table[21]["upper"]) if id in [20, 21] else int(d["upper"])
    for yy in range(maxi(0, y - radius), mini(49, y + int(d["height"]) + radius - 1) + 1):
        for xx in range(maxi(0, x - radius), mini(59, x + int(d["width"]) + radius - 1) + 1):
            var tile := int(cells[yy * 60 + xx][0])
            if lo <= tile and tile <= hi:
                return true
    return false


func feasible(x: int, y: int, id: int) -> bool:
    var d: Dictionary = table[id]
    var category := int(d["category"])
    var w := int(d["width"])
    var h := int(d["height"])
    if x < 0 or y < 0 or x + w > 60 or y + h > 50:
        return false
    if category == 0 or (category == 1 and id not in [20, 21]):
        return true
    for yy in range(y, y + h):
        for xx in range(x, x + w):
            var c: Array = cells[yy * 60 + xx]
            var flags := int(c[4])
            var tile := int(c[0])
            if category == 1:
                if tile < int(table[17]["lower"]) or tile > int(table[17]["upper"]):
                    return false
            elif category == 2:
                if flags & 8:
                    return false
            elif category == 3 and id == 49:
                if flags & 16 and (tile < int(table[43]["lower"]) or tile > int(table[48]["upper"])):
                    return false
            elif category >= 3 and category <= 5:
                if flags & 16:
                    return false
            elif category >= 6 and category <= 10:
                if flags & 16 and (int(c[3]) < 3 or int(c[3]) > 5):
                    return false
    return true


func choose(category: int) -> int:
    var options: Array[int] = []
    for d in table:
        if int(d["category"]) == category:
            options.append(int(d["id"]))
    assert(not options.is_empty())
    return options[draw() % options.size()]


func scan() -> Array[Vector2i]:
    var x0 := draw() % 60
    var y0 := draw() % 50
    var points: Array[Vector2i] = []
    for y in 50:
        for x in 60:
            points.append(Vector2i((x0 + x) % 60, (y0 + y) % 50))
    return points


func build(x: int, y: int, id: int) -> void:
    place(x, y, id)
    actions.append(["build", x, y, id])


func remove(x: int, y: int) -> void:
    demolish(x, y)
    actions.append(["remove", x, y])


func monthly(stores: Array, reference: int = 100, divisor: int = 10000) -> Array:
    actions = []
    var residential := population(3)
    var value := 0
    for s in stores:
        value += int(s["value"])
    if residential > 0:
        value = div0(value, residential)
    if value <= 0:
        value = reference
    var base := div0((value - reference) * 10, value) if value >= reference else -div0((reference - value) * 100, reference)
    var grid: Array[int] = []
    grid.resize(3000)
    grid.fill(signed_byte(base))
    var administrative := Vector2i(-1, -1)
    var station_count := 0
    var maximum := 11
    for y in 50:
        for x in 60:
            var c: Array = cells[y * 60 + x]
            if administrative == Vector2i(-1, -1) and int(c[3]) == 9:
                administrative = Vector2i(x, y)
            if level(x, y) > maximum and feasible(x, y, 20) and not nearby(x, y, 20, 40):
                maximum = level(x, y)
            var tile := int(c[0])
            if tile in [int(table[20]["lower"]), int(table[21]["lower"])]:
                station_count += 1
                for yy in range(maxi(0, y - 8), mini(49, y + 8) + 1):
                    for xx in range(maxi(0, x - 8), mini(59, x + 8) + 1):
                        var k := yy * 60 + xx
                        grid[k] = signed_byte(mini(100, grid[k] + 30))
            if tile >= int(table[14]["lower"]) and tile <= int(table[16]["upper"]):
                # Preserve the original asymmetric vertical bound, not a square.
                var affected: Array[Vector2i] = [Vector2i(x, maxi(0, y - 3))]
                for xx in range(maxi(0, x - 3), mini(59, x + 3) + 1):
                    affected.append(Vector2i(xx, y))
                for point in affected:
                    var k := point.y * 60 + point.x
                    if int(cells[k][3]) != 1:
                        grid[k] = signed_byte(mini(100, grid[k] + 10))
    maximum -= 1
    for s in stores:
        var strength := signed_byte(mini(100, div0(int(s["value"]), divisor)))
        if strength <= 0:
            continue
        var r: Array = s["rect"]
        for y in range(maxi(0, int(r[1]) - 12), mini(49, int(r[3]) + 12) + 1):
            for x in range(maxi(0, int(r[0]) - 12), mini(59, int(r[2]) + 12) + 1):
                if not (x >= int(r[0]) - 7 and x <= int(r[2]) + 7 and y >= int(r[1]) - 7 and y <= int(r[3]) + 7):
                    if draw() & 3:
                        continue
                var k := y * 60 + x
                grid[k] = signed_byte(mini(100, grid[k] + strength))
    for y in 50:
        for x in 60:
            var k := y * 60 + x
            var lv := level(x, y)
            if grid[k] != 0:
                var roll := draw() % 100 + 1
                if grid[k] > 0 and roll <= grid[k] and lv < 25:
                    lv += 1
                if grid[k] < 0 and roll <= -grid[k] and lv >= 2:
                    lv -= 1
                cells[k][1] = lv
            if lv < 4 and draw() % 100 + 1 < 3:
                if int(table[kind(x, y)]["category"]) == 3:
                    remove(x, y)
            lv = level(x, y)
            if lv >= 8 and draw() % 100 + 1 < 3:
                var id := 43 + draw() % (6 if lv < 15 else 7)
                if feasible(x, y, id):
                    build(x, y, id)
    residential = population(3)
    for category in [4, 5]:
        var target := residential if category == 4 else div0(residential, 4)
        var difference := target - population(category)
        for point in scan():
            var lv := level(point.x, point.y)
            if difference < 0 and lv < 3 and int(table[kind(point.x, point.y)]["category"]) == category:
                remove(point.x, point.y)
                break
            if difference > 0 and lv >= 9:
                var id := choose(category)
                if feasible(point.x, point.y, id):
                    build(point.x, point.y, id)
                    break
    var p := population()
    if p >= 5000:
        var radius := 30 if p >= 20000 else (50 if p >= 8000 else 100)
        var id := choose(6 + draw() % 3 if p >= 8000 else 8)
        for point in scan():
            if level(point.x, point.y) >= 5 and feasible(point.x, point.y, id) and not nearby(point.x, point.y, id, radius):
                build(point.x, point.y, id)
                break
    p = population()
    var next_tier := 4 if p >= 20000 else (3 if p >= 16000 else (2 if p >= 8000 else (1 if p >= 5000 else 0)))
    if station_count < next_tier:
        for point in scan():
            if level(point.x, point.y) >= maximum and feasible(point.x, point.y, 20) and not nearby(point.x, point.y, 20, 40):
                build(point.x, point.y, 20)
                break
    if tier < next_tier:
        tier = next_tier
        var id := 22 if tier == 1 else (23 if tier < 4 else 24)
        if tier > 0 and administrative.x >= 0:
            build(administrative.x, administrative.y, id)
    rebuild_flags(stores)
    return actions


func raw_bytes() -> PackedByteArray:
    var out := PackedByteArray()
    out.resize(24000)
    for i in 3000:
        var c: Array = cells[i]
        out.encode_s16(i * 8, int(c[0]))
        for j in range(1, 5):
            out[i * 8 + j + 1] = int(c[j]) & 255
        out.encode_s16(i * 8 + 6, int(c[5]))
    return out


func snapshot() -> Dictionary:
    return {"cells": cells.duplicate(true), "seed": seed, "tier": tier}


func restore(data: Dictionary) -> void:
    assert(data["cells"].size() == 3000)
    cells = data["cells"].duplicate(true)
    seed = int(data["seed"])
    tier = int(data["tier"])


func guide_map(template: Dictionary) -> Dictionary:
    var out := template.duplicate(true)
    out["width_tiles"] = 60
    out["height_tiles"] = 50
    out["program_tiles"] = true
    out["store_site"]["building_price_unit_yen"] = 1000000
    for facility in out.get("inducement", {}).get("facilities", []):
        if FACILITY_KINDS.has(str(facility["id"])):
            var d: Dictionary = table[int(FACILITY_KINDS[str(facility["id"])])]
            facility["native_kind"] = int(d["id"])
            facility["size"] = [int(d["width"]), int(d["height"])]
    out["tile_rows"] = []
    out["buildings"] = []
    for d in table:
        var id := "ps1_%02d" % int(d["id"])
        out["building_catalog"][id] = {"name": str(d["name"]), "price": int(d["attribute"]) * int(d["width"]) * int(d["height"]), "native_kind": int(d["id"]), "size": [int(d["width"]), int(d["height"])]}
    for y in 50:
        var row := ""
        for x in 60:
            var c: Array = cells[y * 60 + x]
            var d: Dictionary = table[kind(x, y)]
            row += "T" if kind(x, y) == 17 else ("R" if int(c[3]) == 1 else "G")
            if int(d["category"]) > 2 and int(c[0]) == int(d["lower"]):
                out["buildings"].append({"sprite": "ps1_%02d" % int(d["id"]), "tile": [x, y], "size": [int(d["width"]), int(d["height"])]})
        out["tile_rows"].append(row)
    out["rival_stores"] = [{"id": "rival-hq", "role": "head", "name": "ライバル本店", "sprite": "map_red_hq", "position": [43, 12], "permits_held": [], "buyable": false}]
    return out
