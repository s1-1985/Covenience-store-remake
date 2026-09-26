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
# Task #93: the town is drawn with the generated terrain tiles and building
# sprites of assets/raw/conveni_map_assets_v2 (new art) copied into
# assets/town/. REMAKE_BALANCED_DEFAULT: which terrain tile stands for each
# map class and which building sprite stands on each building tile are this
# project's own choices, recorded in guide_town_map (terrain_tiles/buildings)
# by tools/build_guide_town_map.py.
const TILE_PIXELS := 48.0
const MARGIN_TILES := 1
const PLAYER_MARKER_COLOR := Color("8bd17c")
const RIVAL_MARKER_COLOR := Color("ef476f")
const MARKER_OUTLINE_COLOR := Color("202020")
# Task #95: the 2x2 cursor while the player picks where to build.
const SITE_OK_COLOR := Color("ffd23f")
const SITE_BLOCKED_COLOR := Color("ef476f")
# A press that moves less than this (pixels) is a tap, not a drag.
const TAP_SLOP_PIXELS := 12.0

signal site_tapped(origin: Vector2i)
# Task #101: a tap on the map outside site selection (e.g. on a rival store).
signal map_tapped(tile: Vector2i)

var simulation
var map_tile_pixels := 24.0
# Task #93: like the original town screen, only part of the town is shown
# at a time and the view scrolls (here: drag to pan, in whole tiles).
# view_size is set by main.gd; view_origin_tile is the top-left tile shown.
var view_size := Vector2(640, 560)
var view_origin_tile := Vector2i.ZERO
var _town_textures: Dictionary = {}
var _drag_remainder := Vector2.ZERO
var _view_centered := false
# Task #95: while true, a tap on the map picks the 2x2 site under it (its
# top-left square) and site_tapped is emitted; site_cursor is drawn.
var selecting_site := false
var site_cursor := Vector2i(-1, -1)
var site_cursor_ok := false
# Task #111: the cursor also marks a facility's squares while choosing where
# to induce it.
var site_cursor_size := Vector2i(2, 2)
var _press_travel := 0.0


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


# Tiles that fit in view_size.
func view_tiles() -> Vector2i:
    var tiles := guide_map_tiles()
    return Vector2i(
        mini(tiles.x, int(view_size.x / map_tile_pixels)),
        mini(tiles.y, int(view_size.y / map_tile_pixels))
    )


func scroll_by_tiles(delta: Vector2i) -> void:
    var tiles := guide_map_tiles()
    var shown := view_tiles()
    view_origin_tile = Vector2i(
        clampi(view_origin_tile.x + delta.x, 0, maxi(0, tiles.x - shown.x)),
        clampi(view_origin_tile.y + delta.y, 0, maxi(0, tiles.y - shown.y))
    )
    queue_redraw()


# Centres the view on the player's store, or on the middle of the map
# before a site has been bought.
func center_on_store() -> void:
    var guide := guide_map()
    if guide.is_empty():
        return
    var focus := guide_map_tiles() / 2
    if simulation.has_store_site():
        focus = simulation.store_site_origin + Vector2i.ONE
    elif site_cursor.x >= 0:
        focus = site_cursor + Vector2i.ONE
    var shown := view_tiles()
    view_origin_tile = Vector2i.ZERO
    scroll_by_tiles(focus - shown / 2)
    _view_centered = true


# Map square under a point in this node's own (unscaled) coordinates.
func tile_at_local(local_point: Vector2) -> Vector2i:
    return view_origin_tile + Vector2i(
        int(floor(local_point.x / map_tile_pixels)), int(floor(local_point.y / map_tile_pixels))
    )


func show_site_cursor(origin: Vector2i, ok: bool) -> void:
    site_cursor = origin
    site_cursor_ok = ok
    queue_redraw()


func _unhandled_input(event: InputEvent) -> void:
    if not visible or guide_map().is_empty():
        return
    if event is InputEventScreenTouch or event is InputEventMouseButton:
        if event is InputEventMouseButton and event.button_index != MOUSE_BUTTON_LEFT:
            return
        if event.pressed:
            _press_travel = 0.0
            return
        if _press_travel > TAP_SLOP_PIXELS:
            return
        var local_point: Vector2 = get_global_transform_with_canvas().affine_inverse() * event.position
        var shown := view_tiles()
        if local_point.x < 0 or local_point.y < 0 or local_point.x >= shown.x * map_tile_pixels or local_point.y >= shown.y * map_tile_pixels:
            return
        if selecting_site:
            site_tapped.emit(tile_at_local(local_point))
        else:
            map_tapped.emit(tile_at_local(local_point))
        get_viewport().set_input_as_handled()
        return
    var relative := Vector2.ZERO
    if event is InputEventScreenDrag:
        relative = event.relative
    elif event is InputEventMouseMotion and (event.button_mask & MOUSE_BUTTON_MASK_LEFT) != 0:
        relative = event.relative
    else:
        return
    _press_travel += relative.length()
    # Dragging moves the town with the finger, so the view moves the other way.
    _drag_remainder -= relative / scale.x
    var whole := Vector2i(int(_drag_remainder.x / map_tile_pixels), int(_drag_remainder.y / map_tile_pixels))
    if whole != Vector2i.ZERO:
        _drag_remainder -= Vector2(whole) * map_tile_pixels
        scroll_by_tiles(whole)


func _town_texture(sprite_id: String) -> Texture2D:
    if not _town_textures.has(sprite_id):
        var path := TOWN_SPRITE_DIR + sprite_id + ".png"
        _town_textures[sprite_id] = load(path) as Texture2D if ResourceLoader.exists(path) else null
    return _town_textures[sprite_id] as Texture2D


func _tile_at(rows: Array, x: int, y: int) -> String:
    if y < 0 or y >= rows.size():
        return ""
    var line := str(rows[y])
    if x < 0 or x >= line.length():
        return ""
    return line[x]


# Which sides of a road tile continue as road (or cross the railway). A road
# running off the map edge continues too, when the tile behind it is road.
func _road_links(rows: Array, x: int, y: int) -> Dictionary:
    var links := {}
    for step in [Vector2i(0, -1), Vector2i(1, 0), Vector2i(0, 1), Vector2i(-1, 0)]:
        var neighbor := _tile_at(rows, x + step.x, y + step.y)
        if neighbor == "R" or neighbor == "T":
            links[step] = true
        elif neighbor == "" and _tile_at(rows, x - step.x, y - step.y) == "R":
            links[step] = true
    return links


# Road tile id and clockwise quarter turns for a set of links.
func _road_tile(links: Dictionary) -> Array:
    var n := links.has(Vector2i(0, -1))
    var e := links.has(Vector2i(1, 0))
    var s := links.has(Vector2i(0, 1))
    var w := links.has(Vector2i(-1, 0))
    match links.size():
        4:
            return ["map_road_cross", 0]
        3:
            # map_road_t_wes joins W, E and S; turn it so its missing side
            # lands on this tile's missing side.
            if not n:
                return ["map_road_t_wes", 0]
            if not e:
                return ["map_road_t_wes", 1]
            if not s:
                return ["map_road_t_wes", 2]
            return ["map_road_t_wes", 3]
        2:
            if n and s:
                return ["map_road_ns", 0]
            return ["map_road_ew", 0]
        1:
            # map_road_end_s is a dead end opening to the south.
            if s:
                return ["map_road_end_s", 0]
            if w:
                return ["map_road_end_s", 1]
            if n:
                return ["map_road_end_s", 2]
            return ["map_road_end_s", 3]
    return ["map_road_ew", 0]


func _draw_tile(sprite_id: String, rect: Rect2, quarter_turns: int = 0) -> void:
    var texture := _town_texture(sprite_id)
    if texture == null:
        draw_rect(rect, Color("3f8f3a"), true)
        return
    if quarter_turns == 0:
        draw_texture_rect(texture, rect, false)
        return
    draw_set_transform(rect.get_center(), PI * 0.5 * quarter_turns, Vector2.ONE)
    draw_texture_rect(texture, Rect2(-rect.size * 0.5, rect.size), false)
    draw_set_transform(Vector2.ZERO, 0.0, Vector2.ONE)


func _draw_guide_map(guide: Dictionary) -> void:
    if not _view_centered:
        center_on_store()
    var rows: Array = guide["tile_rows"]
    var tiles: Dictionary = guide["terrain_tiles"]
    var t := map_tile_pixels
    var shown := view_tiles()
    var origin := Vector2(view_origin_tile) * t
    for y in range(view_origin_tile.y, view_origin_tile.y + shown.y):
        var line := str(rows[y])
        for x in range(view_origin_tile.x, view_origin_tile.x + shown.x):
            var kind := line[x]
            var rect := Rect2(Vector2(x, y) * t - origin, Vector2(t, t))
            if kind == "R":
                var road := _road_tile(_road_links(rows, x, y))
                _draw_tile(str(road[0]), rect, int(road[1]))
            elif kind == "T" and _tile_at(rows, x, y - 1) == "R" and _tile_at(rows, x, y + 1) == "R":
                _draw_tile("map_crossing_basic", rect)
            else:
                _draw_tile(str(tiles.get(kind, "map_grass_plain")), rect)
    var shown_rect := Rect2(Vector2(view_origin_tile), Vector2(shown))
    var bought: Array = simulation.bought_buildings()
    # Task #111: the simulation's own list, which grows with 誘致.
    var map_buildings: Array = simulation.store_site.buildings if simulation.store_site != null else guide["buildings"]
    for index in map_buildings.size():
        if bought.has(index):
            continue
        var building: Dictionary = map_buildings[index]
        var tile: Array = building["tile"]
        var size: Array = building["size"]
        var footprint := Rect2(Vector2(int(tile[0]), int(tile[1])), Vector2(int(size[0]), int(size[1])))
        if not shown_rect.encloses(footprint):
            continue
        _draw_tile(str(building["sprite"]), Rect2(footprint.position * t - origin, footprint.size * t))
    # The player's store: the flat 本店 mark seen on the original town map
    # (CONFIRMED_VISUAL, video crop) on the 2x2 site the player bought
    # (DATA4 コンビニ(自) 2×2), on paving.
    # Task #123: 本店 is store 0 whichever store is being looked at.
    var head_origin: Vector2i = simulation.store_field(0, "store_site_origin")
    if head_origin != simulation.NO_STORE_SITE:
        var mark := Rect2(Vector2(head_origin), Vector2(2, 2))
        if shown_rect.encloses(mark):
            var mark_rect := Rect2(mark.position * t - origin, mark.size * t)
            for dy in 2:
                for dx in 2:
                    _draw_tile("map_concrete", Rect2(mark_rect.position + Vector2(dx, dy) * t, Vector2(t, t)))
            _draw_tile(str(guide["store_mark_sprite"]), mark_rect)
    # Rival stores: with the guide map their positions are map squares
    # (task #95), each a 2x2 store, drawn as the red 本/02 marks cut from
    # the gameplay video (task #98, guide_town_map.rival_stores).
    var rival_sprites := {}
    for entry in guide.get("rival_stores", []):
        rival_sprites[str(entry["id"])] = str(entry["sprite"])
    for rival in simulation._rival_stores:
        var cell := Vector2(rival["position"])
        if not shown_rect.encloses(Rect2(cell, Vector2(2, 2))):
            continue
        var marker := Rect2(cell * t - origin, Vector2(2 * t, 2 * t))
        if rival_sprites.has(str(rival["id"])):
            for dy in 2:
                for dx in 2:
                    _draw_tile("map_concrete", Rect2(marker.position + Vector2(dx, dy) * t, Vector2(t, t)))
            _draw_tile(rival_sprites[str(rival["id"])], marker)
        else:
            draw_rect(marker.grow(-1), RIVAL_MARKER_COLOR, true)
            draw_rect(marker.grow(-1), MARKER_OUTLINE_COLOR, false, 1.0)
    # Task #101: rival branches the player bought, as the blue 02 mark
    # (gameplay video crop, map_blue_02).
    for branch in simulation.owned_branches:
        var branch_cell := Vector2(branch["position"])
        if not shown_rect.encloses(Rect2(branch_cell, Vector2(2, 2))):
            continue
        var branch_rect := Rect2(branch_cell * t - origin, Vector2(2 * t, 2 * t))
        for dy in 2:
            for dx in 2:
                _draw_tile("map_concrete", Rect2(branch_rect.position + Vector2(dx, dy) * t, Vector2(t, t)))
        _draw_tile("map_blue_02", branch_rect)
    # Task #111: the lot of a facility under construction (誘致用地).
    if not simulation.pending_inducement.is_empty():
        var pending: Dictionary = simulation.pending_inducement
        var facility: Dictionary = simulation._inducement_facility(str(pending["facility_id"]))
        var lot := Rect2(
            Vector2(pending["origin"]) * t - origin,
            Vector2(int(facility["size"][0]), int(facility["size"][1])) * t
        )
        draw_rect(lot, Color(0.85, 0.7, 0.3, 0.55), true)
        draw_rect(lot, Color("7a4b00"), false, 2.0)
        draw_string(ThemeDB.fallback_font, lot.position + Vector2(4, 18), "工事中", HORIZONTAL_ALIGNMENT_LEFT, -1, 16, Color("3b2a10"))
    if selecting_site and site_cursor.x >= 0:
        var cursor := Rect2(Vector2(site_cursor) * t - origin, Vector2(site_cursor_size) * t)
        var cursor_color := SITE_OK_COLOR if site_cursor_ok else SITE_BLOCKED_COLOR
        draw_rect(cursor, Color(cursor_color, 0.35), true)
        draw_rect(cursor, cursor_color, false, 3.0)
    draw_rect(Rect2(Vector2.ZERO, Vector2(shown) * t), Color("202020"), false, 2.0)


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
