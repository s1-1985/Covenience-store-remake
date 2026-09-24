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
const TILE_PIXELS := 48.0
const MARGIN_TILES := 1
const PLAYER_MARKER_COLOR := Color("8bd17c")
const RIVAL_MARKER_COLOR := Color("ef476f")
const MARKER_OUTLINE_COLOR := Color("202020")

var simulation


func bind(source_simulation) -> void:
    simulation = source_simulation
    queue_redraw()


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
