extends Node2D

signal fixture_selected(fixture_id: String)
signal fixture_relocation_requested(fixture_id: String, origin_subcell: Vector2i)
# Task #78: emitted instead of re-selecting when a second fixture is tapped
# while edit_mode == "swap" (see edit_mode below).
signal fixture_swap_requested(fixture_id_a: String, fixture_id_b: String)

const SUBCELL_PIXELS := 36.0

# Task #67: first asset-wiring pass. These sprites (assets/raw/
# conveni_fixtures_remake_v3/) are this project's own newly-drawn art, not a
# recovered original asset (PROJECT_MEMORY.md section 1's 2026-09-21 policy
# note) -- a REMAKE_BALANCED_DEFAULT visual choice, same evidence tier as
# any other placeholder in this client. The sprite directory is copied into
# game/assets/fixtures/ (outside res:// paths cannot be loaded by Godot) at
# one PNG per fixture_catalog catalog_id, filenames matching catalog_id
# exactly. checkout-1/shelf-1/shelf-2 predate the catalog system (task #39/
# #41) and carry no catalog_id at all; FALLBACK_VISUAL_CATALOG_ID_BY_KIND
# gives them a same-footprint stand-in sprite for display only -- this does
# not assert they ARE that specific catalog fixture, only that they render
# with a plausible, correctly-sized sprite instead of a bare rectangle.
const FIXTURE_SPRITE_DIR := "res://assets/fixtures/"
const FALLBACK_VISUAL_CATALOG_ID_BY_KIND := {
    "checkout": "register_1",
    "shelf": "medium_ambient_shelf",
}

# Task #68: second asset-wiring pass, product overlay sprites (assets/raw/
# conveni_products_remake_v3/) -- same REMAKE_BALANCED_DEFAULT evidence tier
# as the task #67 fixture sprites above (this project's own newly-drawn
# art, not recovered original assets). manifest.json's 25 catalog_id values
# each ship three sprites (high/medium/low, one PNG per file already
# depicting that many units -- there is no in-code count/scale step) named
# "<catalog_id>_<state>.png" in game/assets/products/.
const PRODUCT_SPRITE_DIR := "res://assets/products/"
const PRODUCT_STOCK_DISPLAY_STATES := ["high", "medium", "low"]
# REMAKE_BALANCED_DEFAULT (task #68): the source package only ever states
# that fewer visible units should render at lower stock (README_CLAUDE.md's
# 9/5/2 example counts); it never states what stock_units/initial_stock_units
# ratio should switch the displayed sprite from one discrete state to the
# next. These two cutoffs are this project's own choice, not a recovered
# rule -- see docs/decisions/0138-product-overlay-sprite-wiring.md.
const HIGH_STOCK_DISPLAY_RATIO := 0.66
const MEDIUM_STOCK_DISPLAY_RATIO := 0.33
# REMAKE_BALANCED_DEFAULT (task #68): prototype-bread/prototype-drink (the
# vertical_slice.json "products" entries from task #38, before the
# product_catalog/catalog_id system existed at all -- see InventoryState's
# own catalog_id field, which is empty for exactly these two) have no
# recorded category. Their ids are unambiguous ("bread"/"drink"), but
# mapping them here is still this project's own display-only stand-in, the
# same status as FALLBACK_VISUAL_CATALOG_ID_BY_KIND above -- not a claim
# that InventoryState now knows their true category.
const FALLBACK_PRODUCT_CATALOG_ID_BY_PRODUCT_ID := {
    "prototype-bread": "bread",
    "prototype-drink": "cold_drink",
}

# Task #69: third asset-wiring pass, staff walking sprites (assets/raw/
# staff_v2/staff/) -- same REMAKE_BALANCED_DEFAULT evidence tier as tasks
# #67/#68 above. manifest.json ships 35 anonymous walking figures
# ("staff_001".."staff_035", 4 directions x 2 walk-cycle phases each, 160x160
# RGBA, feet-anchored at (80,154)) named "<sprite_id>_<direction>_<phase>.png"
# in game/assets/staff/ -- these are NOT identified with any of the 35 named
# staff_candidates entries by the source package itself (no name is printed
# on any sprite; reference_faces/ restores each candidate's PORTRAIT
# separately from the same guide pages but ships no sprite-to-portrait
# correspondence). _staff_sprite_id_for_candidate() below assigns sprites
# to candidates purely by list position in this file's own staff_candidates
# array (index 0 -> staff_001, index 1 -> staff_002, ...) so every named
# candidate at least renders as a distinct person instead of a plain
# rectangle -- this is a display-only convention, not a claim that
# staff_candidates[N] IS the person drawn in sprite staff_(N+1).
const STAFF_SPRITE_DIR := "res://assets/staff/"
const STAFF_SPRITE_DIRECTIONS := ["down", "left", "right", "up"]
# REMAKE_BALANCED_DEFAULT (task #69): only a walk cycle (A/B) ships, no
# dedicated standing/idle frame -- phase "A" is used for every staff member
# regardless of movement state, rather than inventing a walk-cycle timing
# convention this turn/tick-based simulation (no delta-time animation exists
# anywhere else in this renderer) has no confirmed basis for.
const STAFF_SPRITE_STATIC_PHASE := "A"
# REMAKE_BALANCED_DEFAULT (task #69): which of the 4 shipped directions to
# face is derived from the staff member's own last observed movement (the
# simulation's route/position data), not from anything the guide specifies
# about on-screen staff orientation. A staff member who has not yet moved,
# or whose position is unchanged since the last redraw, keeps facing
# whatever direction it last resolved to (initially "down").
const STAFF_SPRITE_SIZE_PX := SUBCELL_PIXELS * 2.0
const STAFF_SPRITE_ANCHOR_FRACTION := Vector2(0.5, 0.9625)

# Task #70: fourth asset-wiring pass, customer walking sprites (assets/raw/
# customer_v2/customer/) -- same REMAKE_BALANCED_DEFAULT evidence tier as
# tasks #67-#69 above. manifest.json ships 21 anonymous walking figures
# ("customer_01".."customer_21", 4 directions x 2 walk-cycle phases each,
# 160x160 RGBA, feet-anchored at (80,154) -- same geometry as the task #69
# staff package) copied (flattened from the source's one-subfolder-per-
# character layout) into game/assets/customers/ as
# "<sprite_id>_<direction>_<phase>.png". Unlike staff_candidates, this
# client's CustomerState has no archetype/identity field at all: customers
# are created with only an opaque customer_id (e.g. "customer-3",
# "concurrent-a") and are never linked to any of the 21 CONFIRMED_OFFICIAL
# CUSTOMER_ARCHETYPES (reference_sim/conveni_sim/baseline_data.py,
# book pages 134-143) -- no demand/visit-plan mechanic in this vertical
# slice selects an archetype per customer, so there is no real value to
# thread through the way task #68 threaded InventoryState.catalog_id.
# _customer_sprite_id_for_id() below therefore derives a sprite
# deterministically from each customer_id's own hash (not list position --
# there is no roster to have a position in) purely so each customer
# instance renders as a distinct, consistent-looking person instead of a
# plain circle. This is not an archetype assignment: it carries no
# demographic, behavioral, or visit-plan meaning whatsoever.
const CUSTOMER_SPRITE_DIR := "res://assets/customers/"
const CUSTOMER_SPRITE_COUNT := 21
const CUSTOMER_SPRITE_DIRECTIONS := ["down", "left", "right", "up"]
const CUSTOMER_SPRITE_STATIC_PHASE := "A"
const CUSTOMER_SPRITE_SIZE_PX := SUBCELL_PIXELS * 2.0
const CUSTOMER_SPRITE_ANCHOR_FRACTION := Vector2(0.5, 0.9625)

# Task #83: unlike the task #67-#70 world sprites above (this project's own
# newly-drawn "remake" art), these 11 pieces (assets/raw/
# conveni_additional_assets_v1/) are direct crops from an actual first-title
# playthrough video ("type": "video" in that package's manifest.json, exact
# source_video/timestamp_seconds/crop_xyxy cited per entry) -- CONFIRMED_
# VISUAL evidence for the floor/wall/entrance artwork itself, not a REMAKE_
# BALANCED_DEFAULT placeholder. They were extracted in an earlier session
# but never wired into game/ until now. floor_blue_repeat is a repeatable-
# candidate crop of the store's own checkered floor (the package's own
# README notes it is not a strictly seamless tile -- video compression
# leaves minor seams, accepted here as still far closer to the original
# than the previous flat fill color). The 8 wall_* pieces are edge/corner
# border candidates, not a finished 9-slice set (same README caveat): edges
# are tiled only along their long axis below, corners are drawn at native
# size unstretched, exactly as the source package's own usage notes specify.
const FLOOR_SPRITE_DIR := "res://assets/floor/"
# REMAKE_BALANCED_DEFAULT: each wall/corner piece is drawn at its own native
# crop pixel size (not rescaled to SUBCELL_PIXELS) and positioned flush
# against the interior grid's own edge -- how thick the frame ends up
# looking on screen is this renderer's own display choice, since the source
# video's own scale does not convert 1:1 to this client's grid (see the
# asset package's README).

var config: Dictionary = {}
var simulation
var selected_fixture_id := ""
# Task #78: "move" (default) preserves the exact pre-existing tap
# behavior below (tapping a second fixture re-selects it); "swap" is the
# only mode in which tapping a second fixture emits fixture_swap_requested
# instead. main.gd sets this from its own EditModeOption dropdown.
var edit_mode := "move"
var _fixture_textures: Dictionary = {}
var _product_textures: Dictionary = {}
var _staff_textures: Dictionary = {}
var _staff_last_position: Dictionary = {}
var _staff_last_direction: Dictionary = {}
var _customer_textures: Dictionary = {}
var _customer_last_position: Dictionary = {}
var _customer_last_direction: Dictionary = {}
# Task #83: fixed 11-entry set (not catalog-driven, unlike the fixture/
# product/staff/customer texture caches above), so these are loaded once
# by exact filename rather than looked up dynamically.
var _floor_textures: Dictionary = {}


func _ready() -> void:
    # Pixel art stays crisp instead of the engine's default linear blur when
    # sprite rects are scaled to fit each fixture's in-game footprint.
    texture_filter = CanvasItem.TEXTURE_FILTER_NEAREST
    for sprite_name in [
        "floor_blue_repeat",
        "wall_north", "wall_south", "wall_east", "wall_west",
        "wall_nw", "wall_ne", "wall_sw", "wall_se",
        "entrance_in", "entrance_out",
    ]:
        _floor_textures[sprite_name] = load(FLOOR_SPRITE_DIR + sprite_name + ".png") as Texture2D


func selected_fixture() -> String:
    return selected_fixture_id


func bind(source_config: Dictionary, source_simulation) -> void:
    config = source_config
    simulation = source_simulation
    queue_redraw()


func _fixture_texture(catalog_id: String) -> Texture2D:
    if catalog_id.is_empty():
        return null
    if _fixture_textures.has(catalog_id):
        return _fixture_textures[catalog_id] as Texture2D
    var path := FIXTURE_SPRITE_DIR + catalog_id + ".png"
    var texture: Texture2D = null
    if ResourceLoader.exists(path):
        texture = load(path) as Texture2D
    _fixture_textures[catalog_id] = texture
    return texture


func _product_texture(catalog_id: String, stock_display_state: String) -> Texture2D:
    if catalog_id.is_empty() or stock_display_state.is_empty():
        return null
    var cache_key := catalog_id + "_" + stock_display_state
    if _product_textures.has(cache_key):
        return _product_textures[cache_key] as Texture2D
    var path := PRODUCT_SPRITE_DIR + cache_key + ".png"
    var texture: Texture2D = null
    if ResourceLoader.exists(path):
        texture = load(path) as Texture2D
    _product_textures[cache_key] = texture
    return texture


func _product_stock_display_state(stock_units: int, initial_stock_units: int) -> String:
    if stock_units <= 0 or initial_stock_units <= 0:
        return ""
    var ratio := float(stock_units) / float(initial_stock_units)
    if ratio > HIGH_STOCK_DISPLAY_RATIO:
        return "high"
    elif ratio > MEDIUM_STOCK_DISPLAY_RATIO:
        return "medium"
    return "low"


func _product_on_fixture(fixture_id: String):
    for product in simulation.inventory.products.values():
        if product.fixture_id == fixture_id:
            return product
    return null


func _product_display_catalog_id(product) -> String:
    if not product.catalog_id.is_empty():
        return product.catalog_id
    return str(FALLBACK_PRODUCT_CATALOG_ID_BY_PRODUCT_ID.get(product.product_id, ""))


func _staff_texture(sprite_id: String, direction: String, phase: String) -> Texture2D:
    if sprite_id.is_empty() or direction.is_empty() or phase.is_empty():
        return null
    var cache_key := sprite_id + "_" + direction + "_" + phase
    if _staff_textures.has(cache_key):
        return _staff_textures[cache_key] as Texture2D
    var path := STAFF_SPRITE_DIR + cache_key + ".png"
    var texture: Texture2D = null
    if ResourceLoader.exists(path):
        texture = load(path) as Texture2D
    _staff_textures[cache_key] = texture
    return texture


func _staff_sprite_id_for_candidate(candidate_id: String) -> String:
    if candidate_id.is_empty():
        return ""
    var candidates: Array = config.get("staff_candidates", [])
    for candidate_index in range(candidates.size()):
        if str(candidates[candidate_index]["candidate_id"]) == candidate_id:
            return "staff_%03d" % (candidate_index + 1)
    return ""


func _staff_facing_direction(staff_id: String, position: Vector2i) -> String:
    var previous_position: Vector2i = _staff_last_position.get(staff_id, position)
    var previous_direction: String = _staff_last_direction.get(staff_id, "down")
    var delta := position - previous_position
    var direction := previous_direction
    if delta != Vector2i.ZERO:
        if absi(delta.x) >= absi(delta.y):
            direction = "right" if delta.x > 0 else "left"
        else:
            direction = "down" if delta.y > 0 else "up"
    _staff_last_position[staff_id] = position
    _staff_last_direction[staff_id] = direction
    return direction


func _customer_texture(sprite_id: String, direction: String, phase: String) -> Texture2D:
    if sprite_id.is_empty() or direction.is_empty() or phase.is_empty():
        return null
    var cache_key := sprite_id + "_" + direction + "_" + phase
    if _customer_textures.has(cache_key):
        return _customer_textures[cache_key] as Texture2D
    var path := CUSTOMER_SPRITE_DIR + cache_key + ".png"
    var texture: Texture2D = null
    if ResourceLoader.exists(path):
        texture = load(path) as Texture2D
    _customer_textures[cache_key] = texture
    return texture


func _customer_sprite_id_for_id(customer_id: String) -> String:
    if customer_id.is_empty():
        return ""
    var sprite_number := (absi(customer_id.hash()) % CUSTOMER_SPRITE_COUNT) + 1
    return "customer_%02d" % sprite_number


func _customer_facing_direction(customer_id: String, position: Vector2i) -> String:
    var previous_position: Vector2i = _customer_last_position.get(customer_id, position)
    var previous_direction: String = _customer_last_direction.get(customer_id, "down")
    var delta := position - previous_position
    var direction := previous_direction
    if delta != Vector2i.ZERO:
        if absi(delta.x) >= absi(delta.y):
            direction = "right" if delta.x > 0 else "left"
        else:
            direction = "down" if delta.y > 0 else "up"
    _customer_last_position[customer_id] = position
    _customer_last_direction[customer_id] = direction
    return direction


func _process(_delta: float) -> void:
    if simulation != null:
        queue_redraw()


func _unhandled_input(event: InputEvent) -> void:
    # Task #72: while the town map (TownView) is shown in this store view's
    # place, this node is hidden but would otherwise still process taps
    # against its own (stale) coordinates -- guard on visibility.
    if not visible:
        return
    var pointer_position := Vector2.ZERO
    var pressed := false
    if event is InputEventMouseButton:
        pressed = event.pressed and event.button_index == MOUSE_BUTTON_LEFT
        pointer_position = event.position
    elif event is InputEventScreenTouch:
        pressed = event.pressed
        pointer_position = event.position
    if not pressed or simulation == null:
        return
    var local_position := to_local(pointer_position)
    var cell := Vector2i(floori(local_position.x / SUBCELL_PIXELS), floori(local_position.y / SUBCELL_PIXELS))
    if not simulation.layout.is_walkable(cell):
        var fixture_id: String = simulation.layout.fixture_at(cell)
        if not fixture_id.is_empty():
            # Task #78: in "swap" mode, tapping a second, different fixture
            # requests a swap instead of just changing the selection --
            # every other mode (including the default "move") keeps the
            # original re-select behavior unchanged.
            if edit_mode == "swap" and not selected_fixture_id.is_empty() and fixture_id != selected_fixture_id:
                fixture_swap_requested.emit(selected_fixture_id, fixture_id)
                get_viewport().set_input_as_handled()
                return
            selected_fixture_id = fixture_id
            fixture_selected.emit(fixture_id)
            queue_redraw()
            get_viewport().set_input_as_handled()
        return
    if not selected_fixture_id.is_empty():
        fixture_relocation_requested.emit(selected_fixture_id, cell)
        get_viewport().set_input_as_handled()


func _draw() -> void:
    if config.is_empty() or simulation == null:
        return

    var width: float = simulation.layout.width_subcells * SUBCELL_PIXELS
    var height: float = simulation.layout.height_subcells * SUBCELL_PIXELS
    _draw_floor(width, height)
    _draw_walls(width, height)

    _draw_grid(width, height)
    _draw_entry_exit()
    _draw_fixtures()
    _draw_staff()
    _draw_customer()


# Task #83: tiles the CONFIRMED_VISUAL floor crop (see _floor_textures'
# declaration above) at its own native pixel size across the interior,
# replacing the previous flat fill color. draw_texture_rect's own tile
# behavior (not a manual loop) handles the repeat.
func _draw_floor(width: float, height: float) -> void:
    var floor_texture: Texture2D = _floor_textures["floor_blue_repeat"]
    if floor_texture == null:
        draw_rect(Rect2(Vector2.ZERO, Vector2(width, height)), Color("f5f1e8"), true)
        return
    draw_texture_rect(floor_texture, Rect2(Vector2.ZERO, Vector2(width, height)), true)


# Task #83: draws the 8 real wall/corner crops as a frame immediately
# outside the interior rect -- edges tiled along their long axis only,
# corners at native size unstretched, per the source asset package's own
# usage notes (see _floor_textures' declaration above).
func _draw_walls(width: float, height: float) -> void:
    var north: Texture2D = _floor_textures["wall_north"]
    var south: Texture2D = _floor_textures["wall_south"]
    var east: Texture2D = _floor_textures["wall_east"]
    var west: Texture2D = _floor_textures["wall_west"]
    var nw: Texture2D = _floor_textures["wall_nw"]
    var ne: Texture2D = _floor_textures["wall_ne"]
    var sw: Texture2D = _floor_textures["wall_sw"]
    var se: Texture2D = _floor_textures["wall_se"]
    if north == null or south == null or east == null or west == null \
            or nw == null or ne == null or sw == null or se == null:
        draw_rect(Rect2(Vector2.ZERO, Vector2(width, height)), Color("373737"), false, 3.0)
        return
    draw_texture_rect(north, Rect2(Vector2(0, -north.get_height()), Vector2(width, north.get_height())), true)
    draw_texture_rect(south, Rect2(Vector2(0, height), Vector2(width, south.get_height())), true)
    draw_texture_rect(west, Rect2(Vector2(-west.get_width(), 0), Vector2(west.get_width(), height)), true)
    draw_texture_rect(east, Rect2(Vector2(width, 0), Vector2(east.get_width(), height)), true)
    draw_texture_rect(nw, Rect2(Vector2(-nw.get_width(), -nw.get_height()), nw.get_size()), false)
    draw_texture_rect(ne, Rect2(Vector2(width, -ne.get_height()), ne.get_size()), false)
    draw_texture_rect(sw, Rect2(Vector2(-sw.get_width(), height), sw.get_size()), false)
    draw_texture_rect(se, Rect2(Vector2(width, height), se.get_size()), false)


func _draw_grid(width: float, height: float) -> void:
    var subcells_per_tile := int(config["store"]["subcells_per_tile"])
    for x in range(simulation.layout.width_subcells + 1):
        var thickness := 1.5 if x % subcells_per_tile == 0 else 1.0
        var shade := Color(0, 0, 0, 0.18) if x % subcells_per_tile == 0 else Color(0, 0, 0, 0.08)
        var px := x * SUBCELL_PIXELS
        draw_line(Vector2(px, 0), Vector2(px, height), shade, thickness)
    for y in range(simulation.layout.height_subcells + 1):
        var thickness := 1.5 if y % subcells_per_tile == 0 else 1.0
        var shade := Color(0, 0, 0, 0.18) if y % subcells_per_tile == 0 else Color(0, 0, 0, 0.08)
        var py := y * SUBCELL_PIXELS
        draw_line(Vector2(0, py), Vector2(width, py), shade, thickness)


# Task #83: replaces the previous flat-colored rounded rects + "IN"/"OUT"
# text labels with the real entrance crops (see _floor_textures'
# declaration above) -- the source footage shows no roman-letter overlay,
# only the arrow-and-mat artwork itself, so this drops the synthetic text
# rather than layering it over the real sprite.
func _draw_entry_exit() -> void:
    var entry := _vec2i(config["store"]["entry_subcell"])
    var exit := _vec2i(config["store"]["exit_subcell"])
    var entry_texture: Texture2D = _floor_textures["entrance_in"]
    var exit_texture: Texture2D = _floor_textures["entrance_out"]
    if entry_texture != null:
        draw_texture_rect(entry_texture, _cell_rect(entry), false)
    else:
        draw_rect(_cell_rect(entry).grow(-5), Color("8bd17c"), true)
        _draw_text_at(entry, "IN")
    if exit_texture != null:
        draw_texture_rect(exit_texture, _cell_rect(exit), false)
    else:
        draw_rect(_cell_rect(exit).grow(-5), Color("efa36f"), true)
        _draw_text_at(exit, "OUT")


func _draw_fixtures() -> void:
    var scale := int(config["store"]["subcells_per_tile"])
    for fixture in simulation.layout.fixtures:
        var origin := _vec2i(fixture["origin_subcell"])
        var footprint: Array = fixture["footprint_tiles"]
        var size_subcells := Vector2i(int(footprint[0]) * scale, int(footprint[1]) * scale)
        var rect := Rect2(
            Vector2(origin.x, origin.y) * SUBCELL_PIXELS,
            Vector2(size_subcells.x, size_subcells.y) * SUBCELL_PIXELS
        ).grow(-3)
        var catalog_id := str(fixture.get("catalog_id", ""))
        if catalog_id.is_empty():
            catalog_id = str(FALLBACK_VISUAL_CATALOG_ID_BY_KIND.get(fixture["kind"], ""))
        var texture := _fixture_texture(catalog_id)
        var fill := Color("84a9d8")
        var label := "SHELF"
        if fixture["kind"] == "checkout":
            fill = Color("d69a69")
            label = "CHECKOUT"
        elif fixture["kind"] == "amenity":
            fill = Color("9ad6a8")
            label = str(fixture["id"]).to_upper()
        elif fixture["kind"] == "parking":
            fill = Color("8d8d8d")
            label = str(fixture["id"]).to_upper()
        if texture != null:
            draw_texture_rect(texture, rect, false)
        else:
            draw_rect(rect, fill, true)
            draw_string(
                ThemeDB.fallback_font,
                rect.position + Vector2(10, 24),
                label,
                HORIZONTAL_ALIGNMENT_LEFT,
                -1,
                16,
                Color("202020")
            )
        var product = _product_on_fixture(str(fixture["id"]))
        if product != null:
            var product_catalog_id := _product_display_catalog_id(product)
            var stock_display_state := _product_stock_display_state(
                product.stock_units, product.initial_stock_units
            )
            var product_texture := _product_texture(product_catalog_id, stock_display_state)
            if product_texture != null:
                _draw_product_overlay(product_texture, origin, footprint, scale)
        var outline := Color("f4d35e") if fixture["id"] == selected_fixture_id else Color("363636")
        var outline_width := 5.0 if fixture["id"] == selected_fixture_id else 2.0
        draw_rect(rect, outline, false, outline_width)
        var interaction := _vec2i(fixture["interaction_subcell"])
        draw_circle(_cell_center(interaction), 7.0, Color("f4d35e"))


func _draw_product_overlay(texture: Texture2D, origin: Vector2i, footprint: Array, scale: int) -> void:
    # README_CLAUDE.md ("商品の重ね方"): "2×1や3×1はタイルごとに繰り返す" --
    # a multi-tile shelf repeats the same overlay once per tile rather than
    # stretching one sprite across the whole footprint.
    var tile_pixels := SUBCELL_PIXELS * scale
    for tile_x in range(int(footprint[0])):
        for tile_y in range(int(footprint[1])):
            var tile_origin := Vector2(
                (origin.x + tile_x * scale) * SUBCELL_PIXELS,
                (origin.y + tile_y * scale) * SUBCELL_PIXELS
            )
            var tile_rect := Rect2(tile_origin, Vector2(tile_pixels, tile_pixels)).grow(-6)
            draw_texture_rect(texture, tile_rect, false)


func _draw_customer() -> void:
    # Every customer still in the store is drawn (task #36, concurrent
    # customers), not only the single most-recently-admitted one. Customers
    # sharing a cell (e.g. several waiting in the checkout queue, which has
    # no dedicated queue-cell geometry yet -- see decision 0105) are offset
    # slightly so they stay individually visible instead of fully
    # overlapping; this is a cosmetic-only spread, not a claim about the
    # original game's queue positions.
    var seen_positions: Dictionary = {}
    for customer in simulation.customers.active_customers():
        var center: Vector2 = _cell_center(customer.position)
        var stack_index: int = seen_positions.get(customer.position, 0)
        seen_positions[customer.position] = stack_index + 1
        center += Vector2(stack_index * 6.0, stack_index * 6.0)
        var sprite_id := _customer_sprite_id_for_id(customer.customer_id)
        var direction := _customer_facing_direction(customer.customer_id, customer.position)
        var texture := _customer_texture(sprite_id, direction, CUSTOMER_SPRITE_STATIC_PHASE)
        if texture != null:
            var draw_size := Vector2(CUSTOMER_SPRITE_SIZE_PX, CUSTOMER_SPRITE_SIZE_PX)
            var anchor_offset := Vector2(
                CUSTOMER_SPRITE_ANCHOR_FRACTION.x * draw_size.x,
                CUSTOMER_SPRITE_ANCHOR_FRACTION.y * draw_size.y
            )
            draw_texture_rect(texture, Rect2(center - anchor_offset, draw_size), false)
        else:
            draw_circle(center, 13.0, Color("ef476f"))
            draw_circle(center, 13.0, Color("3a2630"), false, 2.0)


func _draw_staff() -> void:
    var resting_index := 0
    for staff_member in simulation.staff.all_staff():
        var center: Vector2 = _cell_center(staff_member.position)
        # Task #88: a resting staff member's logical position is the break
        # room's door (its interaction cell); they are drawn inside the room
        # itself so "resting" reads differently from "standing at the door".
        # REMAKE_BALANCED_DEFAULT: no recovered source shows how the original
        # draws staff inside the 社員休憩室, so the in-room spot and the
        # fan-out offsets in _break_room_rest_spot() are this project's own.
        if staff_member.rest_phase == "resting":
            var rest_spot = _break_room_rest_spot(resting_index)
            if rest_spot != null:
                center = rest_spot
                resting_index += 1
        var sprite_id := _staff_sprite_id_for_candidate(staff_member.candidate_id)
        var direction := _staff_facing_direction(staff_member.staff_id, staff_member.position)
        var texture := _staff_texture(sprite_id, direction, STAFF_SPRITE_STATIC_PHASE)
        if texture != null:
            var draw_size := Vector2(STAFF_SPRITE_SIZE_PX, STAFF_SPRITE_SIZE_PX)
            var anchor_offset := Vector2(
                STAFF_SPRITE_ANCHOR_FRACTION.x * draw_size.x,
                STAFF_SPRITE_ANCHOR_FRACTION.y * draw_size.y
            )
            draw_texture_rect(texture, Rect2(center - anchor_offset, draw_size), false)
        else:
            var rect := Rect2(center - Vector2(12, 12), Vector2(24, 24))
            draw_rect(rect, Color("118ab2"), true)
            draw_rect(rect, Color("17324d"), false, 2.0)


func _break_room_rest_spot(index: int):
    var scale := int(config["store"]["subcells_per_tile"])
    for fixture in simulation.layout.fixtures:
        if str(fixture["kind"]) != "break_room":
            continue
        var origin := _vec2i(fixture["origin_subcell"])
        var footprint: Array = fixture["footprint_tiles"]
        var size := Vector2(int(footprint[0]) * scale, int(footprint[1]) * scale) * SUBCELL_PIXELS
        var room_center := Vector2(origin.x, origin.y) * SUBCELL_PIXELS + size * 0.5
        var offsets: Array[Vector2] = [
            Vector2(-0.22, 0.1), Vector2(0.22, 0.1), Vector2(-0.22, -0.2), Vector2(0.22, -0.2)
        ]
        return room_center + offsets[index % offsets.size()] * size
    return null


func _draw_text_at(cell: Vector2i, text: String) -> void:
    draw_string(
        ThemeDB.fallback_font,
        _cell_rect(cell).position + Vector2(4, 20),
        text,
        HORIZONTAL_ALIGNMENT_LEFT,
        -1,
        13,
        Color("222222")
    )


func _cell_rect(cell: Vector2i) -> Rect2:
    return Rect2(
        Vector2(cell.x, cell.y) * SUBCELL_PIXELS,
        Vector2(SUBCELL_PIXELS, SUBCELL_PIXELS)
    )


func _cell_center(cell: Vector2i) -> Vector2:
    return Vector2(cell.x + 0.5, cell.y + 0.5) * SUBCELL_PIXELS


func _vec2i(value: Array) -> Vector2i:
    return Vector2i(int(value[0]), int(value[1]))
