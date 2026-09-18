extends Node2D

const VerticalSliceSimulationScript := preload("res://scripts/vertical_slice_simulation.gd")
const SaveGameServiceScript := preload("res://scripts/save_game_service.gd")
const MAIN_MENU_SCENE_PATH := "res://scenes/main_menu.tscn"

@onready var store_view: Node2D = $StoreView
@onready var clock_label: Label = $UI/Panel/Margin/VBox/ClockValue
@onready var cash_label: Label = $UI/Panel/Margin/VBox/CashValue
@onready var stock_label: Label = $UI/Panel/Margin/VBox/StockValue
@onready var basket_label: Label = $UI/Panel/Margin/VBox/BasketValue
@onready var customer_label: Label = $UI/Panel/Margin/VBox/CustomerValue
@onready var staff_label: Label = $UI/Panel/Margin/VBox/StaffValue
@onready var sales_label: Label = $UI/Panel/Margin/VBox/SalesValue
@onready var visits_label: Label = $UI/Panel/Margin/VBox/VisitsValue
@onready var rating_label: Label = $UI/Panel/Margin/VBox/RatingValue
@onready var town_label: Label = $UI/Panel/Margin/VBox/TownValue
@onready var event_label: Label = $UI/Panel/Margin/VBox/EventValue
@onready var layout_edit_label: Label = $UI/Panel/Margin/VBox/LayoutEditValue
@onready var pause_button: Button = $UI/Panel/Margin/VBox/Buttons/PauseButton
@onready var step_button: Button = $UI/Panel/Margin/VBox/Buttons/StepButton
@onready var reset_button: Button = $UI/Panel/Margin/VBox/Buttons/ResetButton
@onready var next_customer_button: Button = $UI/Panel/Margin/VBox/NextCustomerButton
@onready var rotate_fixture_button: Button = $UI/Panel/Margin/VBox/RotateFixtureButton
@onready var save_button: Button = $UI/Panel/Margin/VBox/MenuButtons/SaveButton
@onready var load_button: Button = $UI/Panel/Margin/VBox/MenuButtons/LoadButton
@onready var quit_to_menu_button: Button = $UI/Panel/Margin/VBox/MenuButtons/QuitToMenuButton

var config: Dictionary
var simulation
var tick_seconds := 0.25
var accumulator := 0.0
var paused := false
var _save_service


func _ready() -> void:
    config = _load_config()
    if config.is_empty():
        return
    simulation = VerticalSliceSimulationScript.new(config)
    tick_seconds = float(config["simulation"]["tick_seconds"])
    _save_service = SaveGameServiceScript.new()
    # GameLaunchState is an autoload (project.godot [autoload]); it is only
    # ever set by main_menu.gd's Continue button, so this is a no-op (and
    # every field above stays exactly the fresh-game state) whenever this
    # scene is entered directly, including the CI headless-smoke
    # instantiate-and-free check.
    if GameLaunchState.continue_from_save:
        GameLaunchState.continue_from_save = false
        _save_service.load_from_path(simulation)
    store_view.bind(config, simulation)
    pause_button.pressed.connect(_on_pause_pressed)
    step_button.pressed.connect(_on_step_pressed)
    reset_button.pressed.connect(_on_reset_pressed)
    next_customer_button.pressed.connect(_on_next_customer_pressed)
    rotate_fixture_button.pressed.connect(_on_rotate_fixture_pressed)
    save_button.pressed.connect(_on_save_pressed)
    load_button.pressed.connect(_on_load_pressed)
    quit_to_menu_button.pressed.connect(_on_quit_to_menu_pressed)
    store_view.fixture_selected.connect(_on_fixture_selected)
    store_view.fixture_relocation_requested.connect(_on_fixture_relocation_requested)
    _refresh_ui()


func _process(delta: float) -> void:
    if simulation == null or paused:
        return
    accumulator += delta
    while accumulator >= tick_seconds:
        accumulator -= tick_seconds
        if simulation.customers.active().phase == "done":
            simulation.tick_idle_for_demand()
        else:
            simulation.step()
        _refresh_ui()


func _unhandled_input(event: InputEvent) -> void:
    if event.is_action_pressed("ui_accept"):
        _on_pause_pressed()
        get_viewport().set_input_as_handled()


func _on_pause_pressed() -> void:
    if simulation == null:
        return
    paused = not paused
    pause_button.text = "Resume" if paused else "Pause"
    _refresh_ui()


func _on_step_pressed() -> void:
    if simulation == null or simulation.customers.active().phase == "done":
        return
    paused = true
    pause_button.text = "Resume"
    accumulator = 0.0
    simulation.step()
    _refresh_ui()


func _on_reset_pressed() -> void:
    if simulation == null:
        return
    paused = false
    pause_button.text = "Pause"
    accumulator = 0.0
    simulation.reset()
    layout_edit_label.text = "Layout reset to configured prototype"
    _refresh_ui()


func _on_next_customer_pressed() -> void:
    if simulation == null or not simulation.start_next_customer():
        return
    paused = false
    pause_button.text = "Pause"
    accumulator = 0.0
    _refresh_ui()


func _on_fixture_selected(fixture_id: String) -> void:
    layout_edit_label.text = "Selected: %s — tap an empty grid cell to move" % fixture_id


func _on_fixture_relocation_requested(fixture_id: String, origin_subcell: Vector2i) -> void:
    if simulation.try_relocate_fixture(fixture_id, origin_subcell):
        layout_edit_label.text = "Moved %s to (%d, %d)" % [
            fixture_id,
            origin_subcell.x,
            origin_subcell.y,
        ]
    elif not simulation.customers.can_admit():
        layout_edit_label.text = "Finish the active visit before editing layout"
    else:
        layout_edit_label.text = "Cannot move there: blocked, outside, or route would break"
    _refresh_ui()


func _on_rotate_fixture_pressed() -> void:
    var fixture_id: String = store_view.selected_fixture()
    if fixture_id.is_empty():
        layout_edit_label.text = "Select a fixture before rotating"
    elif simulation.try_rotate_fixture_clockwise(fixture_id):
        layout_edit_label.text = "Rotated %s clockwise" % fixture_id
    elif not simulation.customers.can_admit():
        layout_edit_label.text = "Finish the active visit before editing layout"
    else:
        layout_edit_label.text = "Cannot rotate there: blocked or route would break"
    _refresh_ui()


func _on_save_pressed() -> void:
    if simulation == null:
        return
    if _save_service.save_to_path(simulation):
        layout_edit_label.text = "Game saved"
    else:
        layout_edit_label.text = "Save failed"
    _refresh_ui()


func _on_load_pressed() -> void:
    if simulation == null:
        return
    if _save_service.load_from_path(simulation):
        paused = false
        pause_button.text = "Pause"
        accumulator = 0.0
        layout_edit_label.text = "Game loaded"
    else:
        layout_edit_label.text = "No compatible save found"
    _refresh_ui()


func _on_quit_to_menu_pressed() -> void:
    GameLaunchState.continue_from_save = false
    get_tree().change_scene_to_file(MAIN_MENU_SCENE_PATH)


func _refresh_ui() -> void:
    if simulation == null:
        return
    var snapshot: Dictionary = simulation.snapshot()
    clock_label.text = str(snapshot["clock_text"])
    cash_label.text = "¥%s" % _format_integer(int(snapshot["cash_yen"]))
    stock_label.text = "%d units" % int(snapshot["stock_units"])
    basket_label.text = "%d items / ¥%s" % [
        int(snapshot["customer_basket_count"]),
        _format_integer(int(snapshot["customer_basket_total_yen"])),
    ]
    customer_label.text = "%s: %s" % [snapshot["customer_id"], snapshot["customer_phase"]]
    staff_label.text = "%s: %s (%d staff)" % [
        snapshot["staff_id"],
        snapshot["staff_state"],
        int(snapshot["staff_count"]),
    ]
    var last_sale: Dictionary = snapshot["last_sale"]
    sales_label.text = str(snapshot["completed_sales"])
    if not last_sale.is_empty():
        sales_label.text += " (last: ¥%s)" % _format_integer(int(last_sale["total_yen"]))
    visits_label.text = "Visits: %d / %d" % [
        int(snapshot["completed_visits"]),
        int(snapshot["started_visits"]),
    ]
    rating_label.text = "%s (popularity %d)" % [
        _star_rank_text(int(snapshot["star_rating"])),
        int(snapshot["popularity"]),
    ]
    var rival_store_count: int = int(snapshot["town_store_count_including_rivals"]) - int(snapshot["player_store_count"])
    town_label.text = "population %s, %d rival store%s, land ¥%s" % [
        _format_integer(int(snapshot["town_population"])),
        rival_store_count,
        "" if rival_store_count == 1 else "s",
        _format_integer(int(snapshot["land_value_yen"])),
    ]
    event_label.text = str(snapshot["last_event"])
    if paused:
        event_label.text += "  [PAUSED]"
    next_customer_button.disabled = not simulation.customers.can_admit()
    rotate_fixture_button.disabled = store_view.selected_fixture().is_empty()
    store_view.queue_redraw()


func _load_config() -> Dictionary:
    var path := "res://data/vertical_slice.json"
    if not FileAccess.file_exists(path):
        push_error("Missing vertical slice config: %s" % path)
        return {}
    var parsed = JSON.parse_string(FileAccess.get_file_as_string(path))
    if typeof(parsed) != TYPE_DICTIONARY:
        push_error("Vertical slice config is not a JSON object")
        return {}
    var loaded: Dictionary = parsed
    if loaded.get("provisional", false) != true:
        push_error("Vertical slice config must explicitly remain provisional")
        return {}
    return loaded


func _star_rank_text(star_rating: int) -> String:
    assert(star_rating >= 0 and star_rating <= 5)
    return "★".repeat(star_rating) + "☆".repeat(5 - star_rating)


func _format_integer(value: int) -> String:
    var raw := str(abs(value))
    var chunks: Array[String] = []
    while raw.length() > 3:
        chunks.push_front(raw.right(3))
        raw = raw.left(raw.length() - 3)
    chunks.push_front(raw)
    var joined := ",".join(chunks)
    return "-%s" % joined if value < 0 else joined
