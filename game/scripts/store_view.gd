extends Node2D

const SUBCELL_PIXELS := 42.0

var config: Dictionary = {}
var simulation: VerticalSliceSimulation


func bind(source_config: Dictionary, source_simulation: VerticalSliceSimulation) -> void:
    config = source_config
    simulation = source_simulation
    queue_redraw()


func _process(_delta: float) -> void:
    if simulation != null:
        queue_redraw()


func _draw() -> void:
    if config.is_empty() or simulation == null:
        return

    var width := simulation.width_subcells * SUBCELL_PIXELS
    var height := simulation.height_subcells * SUBCELL_PIXELS
    draw_rect(Rect2(Vector2.ZERO, Vector2(width, height)), Color("f5f1e8"), true)
    draw_rect(Rect2(Vector2.ZERO, Vector2(width, height)), Color("373737"), false, 3.0)

    _draw_grid(width, height)
    _draw_entry_exit()
    _draw_fixtures()
    _draw_staff()
    _draw_customer()


func _draw_grid(width: float, height: float) -> void:
    var subcells_per_tile := int(config["store"]["subcells_per_tile"])
    for x in range(simulation.width_subcells + 1):
        var thickness := 2.0 if x % subcells_per_tile == 0 else 1.0
        var shade := Color("aaa69d") if x % subcells_per_tile == 0 else Color("d8d4cb")
        var px := x * SUBCELL_PIXELS
        draw_line(Vector2(px, 0), Vector2(px, height), shade, thickness)
    for y in range(simulation.height_subcells + 1):
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
    for fixture in config["fixtures"]:
        var origin := _vec2i(fixture["origin_subcell"])
        var footprint: Array = fixture["footprint_tiles"]
        var size_subcells := Vector2i(int(footprint[0]) * scale, int(footprint[1]) * scale)
        var rect := Rect2(
            Vector2(origin.x, origin.y) * SUBCELL_PIXELS,
            Vector2(size_subcells.x, size_subcells.y) * SUBCELL_PIXELS
        ).grow(-3)
        var fill := Color("84a9d8") if fixture["kind"] == "shelf" else Color("d69a69")
        draw_rect(rect, fill, true)
        draw_rect(rect, Color("363636"), false, 2.0)
        var interaction := _vec2i(fixture["interaction_subcell"])
        draw_circle(_cell_center(interaction), 7.0, Color("f4d35e"))
        var label := "SHELF" if fixture["kind"] == "shelf" else "CHECKOUT"
        draw_string(
            ThemeDB.fallback_font,
            rect.position + Vector2(10, 24),
            label,
            HORIZONTAL_ALIGNMENT_LEFT,
            -1,
            16,
            Color("202020")
        )


func _draw_customer() -> void:
    if simulation.customer_phase == "done":
        return
    var center := _cell_center(simulation.customer_position)
    draw_circle(center, 13.0, Color("ef476f"))
    draw_circle(center, 13.0, Color("3a2630"), false, 2.0)


func _draw_staff() -> void:
    var center := _cell_center(simulation.staff_position)
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
