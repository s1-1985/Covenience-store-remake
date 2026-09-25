extends Node2D

# Task #72: town-map wiring, scoped down after investigation. assets/raw/
# conveni_map_assets_v2/'s 52 sprites are all town FACILITIES (schools,
# parks, restaurants, houses, companies, stations, ...) -- none of them
# depict a convenience store (the player's own store or a rival's), and
# this client has no confirmed or even REMAKE_BALANCED_DEFAULT placement
# data for where any of those 52 facility types would sit on a map. Inventing
# a full facility layout would mean guessing an unconfirmed town spatial
# simulation, which PROJECT_MEMORY.md section 17 explicitly names as a
# research gap this project must not paper over with invented placement.
# So this view draws only what vertical_slice_simulation.gd already tracks
# (task #59's _player_store_position and _rival_stores, added solely to
# enforce the CONFIRMED_OFFICIAL permit-exclusion-distance rule) as plain
# colored markers on the same abstract coordinate scale, not the 52
# facility sprites -- an honest "what the data model actually contains"
# view rather than a dressed-up fake town. _rival_stores defaults to empty
# (vertical_slice.json's own town_spatial_evidence_note), so the default
# scenario shows exactly one marker.
# Task #90: when the config carries "guide_town_map" (the guide p.11
# beginner-map screenshot read tile by tile, see that block's
# evidence_note), this view draws that town -- grass, bare ground, roads,
# the railway, houses and the store lot -- instead of the bare markers
# described above. The markers remain the fallback for configs without it.
const TOWN_SPRITE_DIR := "res://assets/town/"
# REMAKE_BALANCED_DEFAULT: building tiles use this project's own generated
# 1x1 house sprites (assets/raw/conveni_map_assets_v2, new art); which of
# the three goes on a tile is this project's own deterministic choice.
const HOUSE_SPRITE_IDS := ["house_small_a", "house_small_b", "house_small_c"]
const GRASS_COLOR := Color("3f8f3a")
const GRASS_SPECK_COLOR := Color("357a31")
const GROUND_COLOR := Color("8a5a32")
const ROAD_COLOR := Color("7b7d80")
const RAIL_BED_COLOR := Color("a7a39a")
const RAIL_COLOR := Color("e6e6e6")
const LOT_COLOR := Color("e8872a")
const TILE_PIXELS := 48.0
const MARGIN_TILES := 1
const PLAYER_MARKER_COLOR := Color("8bd17c")
const RIVAL_MARKER_COLOR := Color("ef476f")
const MARKER_OUTLINE_COLOR := Color("202020")

var simulation
var map_tile_pixels := 16.0
var _house_textures: Array = []


func bind(source_simulation) -> void:
    simulation = source_simulation
    queue_redraw()


func guide_map() -> Dictionary:
    if simulation == null:
        return {}
    return simulation.config.get("guide_town_map", {})


# Size of the guide map in tiles (Vector2i.ZERO when there is none), for
# main.gd's layout.
func guide_map_tiles() -> Vector2i:
    var guide := guide_map()
    if guide.is_empty():
        return Vector2i.ZERO
    return Vector2i(int(guide["width_tiles"]), int(guide["height_tiles"]))


func _house_texture(x: int, y: int) -> Texture2D:
    if _house_textures.is_empty():
        for sprite_id in HOUSE_SPRITE_IDS:
            var path: String = TOWN_SPRITE_DIR + str(sprite_id) + ".png"
            _house_textures.append(load(path) as Texture2D if ResourceLoader.exists(path) else null)
    return _house_textures[(x * 7 + y * 3) % _house_textures.size()]


func _tile_at(rows: Array, x: int, y: int) -> String:
    if y < 0 or y >= rows.size():
        return ""
    var line := str(rows[y])
    if x < 0 or x >= line.length():
        return ""
    return line[x]


func _draw_guide_map(guide: Dictionary) -> void:
    var rows: Array = guide["tile_rows"]
    var t := map_tile_pixels
    for y in range(rows.size()):
        var line := str(rows[y])
        for x in range(line.length()):
            var kind := line[x]
            var rect := Rect2(Vector2(x, y) * t, Vector2(t, t))
            var ground := GROUND_COLOR if kind == "D" else GRASS_COLOR
            draw_rect(rect, ground, true)
            if kind == "G" and (x * 5 + y * 3) % 4 == 0:
                draw_rect(Rect2(rect.position + Vector2(t * 0.25, t * 0.25), Vector2(t * 0.3, t * 0.3)), GRASS_SPECK_COLOR, true)
            match kind:
                "R":
                    var half := t * 0.22
                    var center := rect.get_center()
                    draw_rect(Rect2(center - Vector2(half, half), Vector2(half, half) * 2.0), ROAD_COLOR, true)
                    for step in [Vector2i(1, 0), Vector2i(-1, 0), Vector2i(0, 1), Vector2i(0, -1)]:
                        var neighbor := _tile_at(rows, x + step.x, y + step.y)
                        if neighbor == "R" or neighbor == "T":
                            var arm := Rect2(center - Vector2(half, half), Vector2(half, half) * 2.0)
                            arm = arm.expand(center + Vector2(step) * t * 0.5 + Vector2(step.y, step.x).abs() * half)
                            arm = arm.expand(center + Vector2(step) * t * 0.5 - Vector2(step.y, step.x).abs() * half)
                            draw_rect(arm, ROAD_COLOR, true)
                "T":
                    draw_rect(Rect2(rect.position + Vector2(0, t * 0.2), Vector2(t, t * 0.6)), RAIL_BED_COLOR, true)
                    draw_line(rect.position + Vector2(0, t * 0.35), rect.position + Vector2(t, t * 0.35), RAIL_COLOR, 1.5)
                    draw_line(rect.position + Vector2(0, t * 0.65), rect.position + Vector2(t, t * 0.65), RAIL_COLOR, 1.5)
                "B":
                    var house := _house_texture(x, y)
                    if house != null:
                        draw_texture_rect(house, rect, false)
                    else:
                        draw_rect(rect.grow(-2), Color("d9534f"), true)
                "O":
                    draw_rect(rect, LOT_COLOR, true)
                    draw_rect(rect, LOT_COLOR.darkened(0.2), false, 1.0)
    var lot: Array = guide["store_lot_origin_tile"]
    var lot_rect := Rect2(Vector2(int(lot[0]), int(lot[1])) * t, Vector2(5, 5) * t)
    draw_rect(lot_rect, Color("202020"), false, 2.0)
    draw_string(ThemeDB.fallback_font, lot_rect.position + Vector2(4, lot_rect.size.y * 0.6), tr("Main store"), HORIZONTAL_ALIGNMENT_LEFT, -1, int(t * 0.9), Color("111111"))
    # Rival stores keep this client's abstract tile offsets from the
    # player's store (task #59), drawn relative to the lot.
    for rival in simulation._rival_stores:
        var offset: Vector2i = rival["position"] - simulation._player_store_position
        var cell := Vector2(int(lot[0]) + 2 + offset.x, int(lot[1]) + 2 + offset.y)
        var marker := Rect2(cell * t, Vector2(t, t)).grow(-1)
        draw_rect(marker, RIVAL_MARKER_COLOR, true)
        draw_rect(marker, MARKER_OUTLINE_COLOR, false, 1.0)
    draw_rect(Rect2(Vector2.ZERO, Vector2(guide_map_tiles()) * t), Color("202020"), false, 2.0)


# Pure data extraction, kept separate from _draw() so it can be unit-tested
# without needing an actual render pass (this project's established pattern
# for store_view.gd's own helper functions). Returns one entry per marker:
# {"position": Vector2i, "label": String, "is_player": bool}.
func _town_points(source_simulation) -> Array:
    var points: Array = [{
        "position": source_simulation._player_store_position,
        "label": "YOU",
        "is_player": true,
    }]
    for rival in source_simulation._rival_stores:
        points.append({
            "position": rival["position"],
            "label": str(rival["id"]),
            "is_player": false,
        })
    return points


# Smallest tile-aligned rectangle covering every point plus MARGIN_TILES of
# padding on each side, as {"origin": Vector2i, "size": Vector2i}.
func _bounding_box(points: Array) -> Dictionary:
    var first_position: Vector2i = points[0]["position"]
    var min_x := first_position.x
    var max_x := first_position.x
    var min_y := first_position.y
    var max_y := first_position.y
    for point in points:
        var point_position: Vector2i = point["position"]
        min_x = mini(min_x, point_position.x)
        max_x = maxi(max_x, point_position.x)
        min_y = mini(min_y, point_position.y)
        max_y = maxi(max_y, point_position.y)
    var origin := Vector2i(min_x - MARGIN_TILES, min_y - MARGIN_TILES)
    var size := Vector2i(
        (max_x - min_x) + MARGIN_TILES * 2 + 1,
        (max_y - min_y) + MARGIN_TILES * 2 + 1
    )
    return {"origin": origin, "size": size}


func _draw() -> void:
    if simulation == null:
        return
    var guide := guide_map()
    if not guide.is_empty():
        _draw_guide_map(guide)
        return
    var points := _town_points(simulation)
    var box := _bounding_box(points)
    var origin: Vector2i = box["origin"]
    var size: Vector2i = box["size"]
    var width_px := float(size.x) * TILE_PIXELS
    var height_px := float(size.y) * TILE_PIXELS

    draw_rect(Rect2(Vector2.ZERO, Vector2(width_px, height_px)), Color("2c2f36"), true)
    for x in range(size.x + 1):
        var px := x * TILE_PIXELS
        draw_line(Vector2(px, 0), Vector2(px, height_px), Color("3d414a"), 1.0)
    for y in range(size.y + 1):
        var py := y * TILE_PIXELS
        draw_line(Vector2(0, py), Vector2(width_px, py), Color("3d414a"), 1.0)
    draw_rect(Rect2(Vector2.ZERO, Vector2(width_px, height_px)), Color("545a66"), false, 2.0)

    for point in points:
        var cell: Vector2i = point["position"] - origin
        var rect := Rect2(
            Vector2(cell.x, cell.y) * TILE_PIXELS, Vector2(TILE_PIXELS, TILE_PIXELS)
        ).grow(-5)
        var fill: Color = PLAYER_MARKER_COLOR if point["is_player"] else RIVAL_MARKER_COLOR
        draw_rect(rect, fill, true)
        draw_rect(rect, MARKER_OUTLINE_COLOR, false, 2.0)
        draw_string(
            ThemeDB.fallback_font,
            rect.position + Vector2(4, rect.size.y - 6),
            str(point["label"]),
            HORIZONTAL_ALIGNMENT_LEFT,
            -1,
            13,
            Color("111111")
        )
