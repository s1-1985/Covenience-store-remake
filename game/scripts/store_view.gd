extends Node2D

signal fixture_selected(fixture_id: String)
signal fixture_relocation_requested(fixture_id: String, origin_subcell: Vector2i)

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

var config: Dictionary = {}
var simulation
var selected_fixture_id := ""
var _fixture_textures: Dictionary = {}
var _product_textures: Dictionary = {}


func _ready() -> void:
    # Pixel art stays crisp instead of the engine's default linear blur when
    # sprite rects are scaled to fit each fixture's in-game footprint.
    texture_filter = CanvasItem.TEXTURE_FILTER_NEAREST


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


func _process(_delta: float) -> void:
    if simulation != null:
        queue_redraw()


func _unhandled_input(event: InputEvent) -> void:
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
    draw_rect(Rect2(Vector2.ZERO, Vector2(width, height)), Color("f5f1e8"), true)
    draw_rect(Rect2(Vector2.ZERO, Vector2(width, height)), Color("373737"), false, 3.0)

    _draw_grid(width, height)
    _draw_entry_exit()
    _draw_fixtures()
    _draw_staff()
    _draw_customer()


func _draw_grid(width: float, height: float) -> void:
    var subcells_per_tile := int(config["store"]["subcells_per_tile"])
    for x in range(simulation.layout.width_subcells + 1):
        var thickness := 2.0 if x % subcells_per_tile == 0 else 1.0
        var shade := Color("aaa69d") if x % subcells_per_tile == 0 else Color("d8d4cb")
        var px := x * SUBCELL_PIXELS
        draw_line(Vector2(px, 0), Vector2(px, height), shade, thickness)
    for y in range(simulation.layout.height_subcells + 1):
        var thickness := 2.0 if y % subcells_per_tile == 0 else 1.0
        var shade := Color("aaa69d") if y % subcells_per_tile == 0 else Color("d8d4cb")
        var py := y * SUBCELL_PIXELS
        draw_line(Vector2(0, py), Vector2(width, py), shade, thickness)


func _draw_entry_exit() -> void:
    var entry := _vec2i(config["store"]["entry_subcell"])
    var exit := _vec2i(config["store"]["exit_subcell"])
    draw_rect(_cell_rect(entry).grow(-5), Color("8bd17c"), true)
    draw_rect(_cell_rect(exit).grow(-5), Color("efa36f"), true)
    _draw_text_at(entry, "IN")
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
        draw_circle(center, 13.0, Color("ef476f"))
        draw_circle(center, 13.0, Color("3a2630"), false, 2.0)


func _draw_staff() -> void:
    for staff_member in simulation.staff.all_staff():
        var center: Vector2 = _cell_center(staff_member.position)
        var rect := Rect2(center - Vector2(12, 12), Vector2(24, 24))
        draw_rect(rect, Color("118ab2"), true)
        draw_rect(rect, Color("17324d"), false, 2.0)


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
