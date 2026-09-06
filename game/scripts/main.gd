extends Node2D

const VerticalSliceSimulationScript := preload("res://scripts/vertical_slice_simulation.gd")

@onready var store_view: Node2D = $StoreView
@onready var clock_label: Label = $UI/Panel/Margin/VBox/ClockValue
@onready var cash_label: Label = $UI/Panel/Margin/VBox/CashValue
@onready var stock_label: Label = $UI/Panel/Margin/VBox/StockValue
@onready var customer_label: Label = $UI/Panel/Margin/VBox/CustomerValue
@onready var staff_label: Label = $UI/Panel/Margin/VBox/StaffValue
@onready var sales_label: Label = $UI/Panel/Margin/VBox/SalesValue
@onready var event_label: Label = $UI/Panel/Margin/VBox/EventValue
@onready var pause_button: Button = $UI/Panel/Margin/VBox/Buttons/PauseButton
@onready var step_button: Button = $UI/Panel/Margin/VBox/Buttons/StepButton
@onready var reset_button: Button = $UI/Panel/Margin/VBox/Buttons/ResetButton

var config: Dictionary
var simulation: VerticalSliceSimulation
var tick_seconds := 0.25
var accumulator := 0.0
var paused := false


func _ready() -> void:
    config = _load_config()
    if config.is_empty():
        return
    simulation = VerticalSliceSimulationScript.new(config)
    tick_seconds = float(config["simulation"]["tick_seconds"])
    store_view.bind(config, simulation)
    pause_button.pressed.connect(_on_pause_pressed)
    step_button.pressed.connect(_on_step_pressed)
    reset_button.pressed.connect(_on_reset_pressed)
    _refresh_ui()


func _process(delta: float) -> void:
    if simulation == null or paused or simulation.customer_phase == "done":
        return
    accumulator += delta
    while accumulator >= tick_seconds:
        accumulator -= tick_seconds
        simulation.step()
        _refresh_ui()
        if simulation.customer_phase == "done":
            break


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
    if simulation == null or simulation.customer_phase == "done":
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
    _refresh_ui()


func _refresh_ui() -> void:
    if simulation == null:
        return
    var snapshot := simulation.snapshot()
    clock_label.text = str(snapshot["clock_text"])
    cash_label.text = "¥%s" % _format_integer(int(snapshot["cash_yen"]))
    stock_label.text = "%d units" % int(snapshot["stock_units"])
    customer_label.text = str(snapshot["customer_phase"])
    staff_label.text = str(snapshot["staff_state"])
    sales_label.text = str(snapshot["completed_sales"])
    event_label.text = str(snapshot["last_event"])
    if paused:
        event_label.text += "  [PAUSED]"
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


func _format_integer(value: int) -> String:
    var raw := str(abs(value))
    var chunks: Array[String] = []
    while raw.length() > 3:
        chunks.push_front(raw.right(3))
        raw = raw.left(raw.length() - 3)
    chunks.push_front(raw)
    var joined := ",".join(chunks)
    return "-%s" % joined if value < 0 else joined
