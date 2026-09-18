extends Node2D

const VerticalSliceSimulationScript := preload("res://scripts/vertical_slice_simulation.gd")
const SaveGameServiceScript := preload("res://scripts/save_game_service.gd")
const MAIN_MENU_SCENE_PATH := "res://scenes/main_menu.tscn"
# Sentinel prefix store_view.selected_fixture_id carries while the player is
# placing a newly-bought fixture (task #38), reusing the same tap-to-target
# flow relocate already uses instead of a separate input mode. No owned
# fixture id can ever collide with this, since every generated purchase id
# below also carries the same prefix.
const NEW_FIXTURE_SELECTION_PREFIX := "__new:"

@onready var store_view: Node2D = $StoreView
@onready var clock_label: Label = $UI/Panel/Margin/Scroll/VBox/ClockValue
@onready var cash_label: Label = $UI/Panel/Margin/Scroll/VBox/CashValue
@onready var stock_label: Label = $UI/Panel/Margin/Scroll/VBox/StockValue
@onready var basket_label: Label = $UI/Panel/Margin/Scroll/VBox/BasketValue
@onready var customer_label: Label = $UI/Panel/Margin/Scroll/VBox/CustomerValue
@onready var staff_label: Label = $UI/Panel/Margin/Scroll/VBox/StaffValue
@onready var sales_label: Label = $UI/Panel/Margin/Scroll/VBox/SalesValue
@onready var visits_label: Label = $UI/Panel/Margin/Scroll/VBox/VisitsValue
@onready var rating_label: Label = $UI/Panel/Margin/Scroll/VBox/RatingValue
@onready var town_label: Label = $UI/Panel/Margin/Scroll/VBox/TownValue
@onready var event_label: Label = $UI/Panel/Margin/Scroll/VBox/EventValue
@onready var layout_edit_label: Label = $UI/Panel/Margin/Scroll/VBox/LayoutEditValue
@onready var pause_button: Button = $UI/Panel/Margin/Scroll/VBox/Buttons/PauseButton
@onready var step_button: Button = $UI/Panel/Margin/Scroll/VBox/Buttons/StepButton
@onready var reset_button: Button = $UI/Panel/Margin/Scroll/VBox/Buttons/ResetButton
@onready var next_customer_button: Button = $UI/Panel/Margin/Scroll/VBox/NextCustomerButton
@onready var rotate_fixture_button: Button = $UI/Panel/Margin/Scroll/VBox/RotateFixtureButton
@onready var sample_layout_option: OptionButton = $UI/Panel/Margin/Scroll/VBox/SampleLayoutOption
@onready var load_sample_layout_button: Button = $UI/Panel/Margin/Scroll/VBox/LoadSampleLayoutButton
@onready var fixture_catalog_option: OptionButton = $UI/Panel/Margin/Scroll/VBox/FixtureCatalogOption
@onready var buy_fixture_button: Button = $UI/Panel/Margin/Scroll/VBox/BuyFixtureButton
@onready var permit_option: OptionButton = $UI/Panel/Margin/Scroll/VBox/PermitOption
@onready var buy_permit_button: Button = $UI/Panel/Margin/Scroll/VBox/BuyPermitButton
@onready var product_catalog_option: OptionButton = $UI/Panel/Margin/Scroll/VBox/ProductCatalogOption
@onready var procure_fixture_option: OptionButton = $UI/Panel/Margin/Scroll/VBox/ProcureFixtureOption
@onready var procure_product_button: Button = $UI/Panel/Margin/Scroll/VBox/ProcureProductButton
@onready var restock_product_option: OptionButton = $UI/Panel/Margin/Scroll/VBox/RestockProductOption
@onready var restock_button: Button = $UI/Panel/Margin/Scroll/VBox/RestockButton
@onready var promotion_option: OptionButton = $UI/Panel/Margin/Scroll/VBox/PromotionOption
@onready var buy_promotion_button: Button = $UI/Panel/Margin/Scroll/VBox/BuyPromotionButton
@onready var expand_chain_button: Button = $UI/Panel/Margin/Scroll/VBox/ExpandChainButton
@onready var save_button: Button = $UI/Panel/Margin/Scroll/VBox/MenuButtons/SaveButton
@onready var load_button: Button = $UI/Panel/Margin/Scroll/VBox/MenuButtons/LoadButton
@onready var quit_to_menu_button: Button = $UI/Panel/Margin/Scroll/VBox/MenuButtons/QuitToMenuButton

var config: Dictionary
var simulation
var tick_seconds := 0.25
var accumulator := 0.0
var paused := false
var _save_service
var _sample_layout_ids: Array[String] = []
var _fixture_catalog_ids: Array[String] = []
var _permit_ids: Array[String] = []
var _product_catalog_ids: Array[String] = []
var _procure_fixture_ids: Array[String] = []
var _restock_product_ids: Array[String] = []
var _promotion_ids: Array[String] = []
var _next_fixture_purchase_sequence := 1
var _next_product_purchase_sequence := 1


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
    _populate_sample_layout_option()
    _populate_fixture_catalog_option()
    _populate_permit_option()
    _populate_product_catalog_option()
    _populate_promotion_option()
    _refresh_procure_fixture_option()
    _refresh_restock_product_option()
    pause_button.pressed.connect(_on_pause_pressed)
    step_button.pressed.connect(_on_step_pressed)
    reset_button.pressed.connect(_on_reset_pressed)
    next_customer_button.pressed.connect(_on_next_customer_pressed)
    rotate_fixture_button.pressed.connect(_on_rotate_fixture_pressed)
    load_sample_layout_button.pressed.connect(_on_load_sample_layout_pressed)
    buy_fixture_button.pressed.connect(_on_buy_fixture_pressed)
    buy_permit_button.pressed.connect(_on_buy_permit_pressed)
    procure_product_button.pressed.connect(_on_procure_product_pressed)
    restock_button.pressed.connect(_on_restock_pressed)
    buy_promotion_button.pressed.connect(_on_buy_promotion_pressed)
    expand_chain_button.pressed.connect(_on_expand_chain_pressed)
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
        if simulation.customers.all_settled():
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
    if simulation == null or simulation.customers.all_settled():
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
    _refresh_procure_fixture_option()
    _refresh_restock_product_option()
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
    if fixture_id.begins_with(NEW_FIXTURE_SELECTION_PREFIX):
        _try_place_new_fixture(fixture_id.substr(NEW_FIXTURE_SELECTION_PREFIX.length()), origin_subcell)
        return
    if simulation.try_relocate_fixture(fixture_id, origin_subcell):
        layout_edit_label.text = "Moved %s to (%d, %d)" % [
            fixture_id,
            origin_subcell.x,
            origin_subcell.y,
        ]
    elif not simulation.customers.all_settled():
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
    elif not simulation.customers.all_settled():
        layout_edit_label.text = "Finish the active visit before editing layout"
    else:
        layout_edit_label.text = "Cannot rotate there: blocked or route would break"
    _refresh_ui()


func _populate_sample_layout_option() -> void:
    sample_layout_option.clear()
    _sample_layout_ids.clear()
    for entry in config["sample_layouts"]:
        _sample_layout_ids.append(str(entry["sample_id"]))
        sample_layout_option.add_item(str(entry["label"]))


func _on_load_sample_layout_pressed() -> void:
    if _sample_layout_ids.is_empty():
        return
    var sample_id: String = _sample_layout_ids[sample_layout_option.selected]
    if simulation.try_load_sample_layout(sample_id):
        layout_edit_label.text = "Loaded sample layout: %s" % sample_id
        _refresh_procure_fixture_option()
        _refresh_restock_product_option()
    elif not simulation.customers.all_settled():
        layout_edit_label.text = "Finish the active visit before loading a sample layout"
    else:
        layout_edit_label.text = "Cannot load that sample layout: unaffordable or would strand stocked inventory"
    _refresh_ui()


# --- Economy actions (task #38) ---
#
# vertical_slice_simulation.gd already implements try_purchase_fixture/
# try_purchase_permit/try_procure_product/try_purchase_promotion/
# try_expand_chain/apply_explicit_restock, exercised only by headless_smoke.gd
# until now: none of them were reachable from the actual UI, so a player
# could not buy a fixture, get a permit, stock a product, run a promotion,
# restock a shelf, or expand the chain at all. This section is the first
# wiring of those actions into play, one straightforward OptionButton+Button
# pair per action (or, for a new fixture, the same tap-to-target flow
# relocate already uses instead of a separate placement UI).


func _populate_fixture_catalog_option() -> void:
    fixture_catalog_option.clear()
    _fixture_catalog_ids.clear()
    for entry in config["fixture_catalog"]:
        _fixture_catalog_ids.append(str(entry["catalog_id"]))
        fixture_catalog_option.add_item(
            "%s — ¥%s" % [entry["catalog_id"], _format_integer(int(entry["purchase_price_yen"]))]
        )


func _on_buy_fixture_pressed() -> void:
    if _fixture_catalog_ids.is_empty():
        return
    var catalog_id: String = _fixture_catalog_ids[fixture_catalog_option.selected]
    store_view.selected_fixture_id = NEW_FIXTURE_SELECTION_PREFIX + catalog_id
    layout_edit_label.text = "Buying %s — tap an empty grid cell to place it" % catalog_id
    _refresh_ui()


func _try_place_new_fixture(catalog_id: String, origin_subcell: Vector2i) -> void:
    store_view.selected_fixture_id = ""
    var catalog_entry: Dictionary = {}
    for entry in config["fixture_catalog"]:
        if str(entry["catalog_id"]) == catalog_id:
            catalog_entry = entry
            break
    if catalog_entry.is_empty():
        _refresh_ui()
        return
    var footprint: Array = catalog_entry["footprint_tiles"]
    var subcells_per_tile: int = int(config["store"]["subcells_per_tile"])
    var width: int = int(footprint[0]) * subcells_per_tile
    var height: int = int(footprint[1]) * subcells_per_tile
    var interaction := _find_open_interaction_cell(origin_subcell, width, height)
    if interaction == Vector2i(-1, -1):
        layout_edit_label.text = "Cannot place %s there: no open cell next to it for customers/staff to use" % catalog_id
        _refresh_ui()
        return
    var instance_id := "fixture-purchase-%d" % _next_fixture_purchase_sequence
    _next_fixture_purchase_sequence += 1
    if simulation.try_purchase_fixture(catalog_id, instance_id, origin_subcell, interaction):
        layout_edit_label.text = "Purchased %s" % catalog_id
        _refresh_procure_fixture_option()
    elif not simulation.customers.all_settled():
        layout_edit_label.text = "Finish the active visit before buying a fixture"
    else:
        layout_edit_label.text = "Cannot place %s there: blocked, unaffordable, or route would break" % catalog_id
    _refresh_ui()


# The catalog only records a fixture's footprint, not where its interaction
# point goes -- every existing fixture in vertical_slice.json places that
# point one subcell outside its own footprint, so a newly-bought fixture
# reuses the same convention rather than requiring a second tap from the
# player. Tries the four cardinal neighbors of the footprint's top-left
# corner and returns the first that is walkable before this fixture is
# added; Vector2i(-1, -1) means none of the four worked.
func _find_open_interaction_cell(origin: Vector2i, width: int, height: int) -> Vector2i:
    var candidates: Array[Vector2i] = [
        Vector2i(origin.x, origin.y - 1),
        Vector2i(origin.x, origin.y + height),
        Vector2i(origin.x - 1, origin.y),
        Vector2i(origin.x + width, origin.y),
    ]
    for candidate in candidates:
        if simulation.layout.is_walkable(candidate):
            return candidate
    return Vector2i(-1, -1)


func _populate_permit_option() -> void:
    permit_option.clear()
    _permit_ids.clear()
    for entry in config["permits"]:
        _permit_ids.append(str(entry["permit_id"]))
        permit_option.add_item("%s — ¥%s" % [entry["permit_id"], _format_integer(int(entry["fee_yen"]))])


func _on_buy_permit_pressed() -> void:
    if _permit_ids.is_empty():
        return
    var permit_id: String = _permit_ids[permit_option.selected]
    if simulation.has_permit(permit_id):
        layout_edit_label.text = "Already hold the %s permit" % permit_id
    elif simulation.try_purchase_permit(permit_id):
        layout_edit_label.text = "Purchased permit: %s" % permit_id
    elif not simulation.customers.all_settled():
        layout_edit_label.text = "Finish the active visit before buying a permit"
    else:
        layout_edit_label.text = "Cannot afford the %s permit" % permit_id
    _refresh_ui()


func _populate_product_catalog_option() -> void:
    product_catalog_option.clear()
    _product_catalog_ids.clear()
    for entry in config["product_catalog"]:
        _product_catalog_ids.append(str(entry["catalog_id"]))
        product_catalog_option.add_item(
            "%s — ¥%s/unit" % [entry["catalog_id"], _format_integer(int(entry["restock_unit_cost_yen"]))]
        )


# Only shelf-kind fixtures hold products in this client (checkout/amenity/
# parking fixtures never do); repopulated whenever the set of owned
# fixtures can have changed (buying one, loading a sample, reset, load).
func _refresh_procure_fixture_option() -> void:
    procure_fixture_option.clear()
    _procure_fixture_ids.clear()
    for fixture in simulation.layout.fixtures:
        if str(fixture["kind"]) == "shelf":
            var fixture_id := str(fixture["id"])
            _procure_fixture_ids.append(fixture_id)
            procure_fixture_option.add_item(fixture_id)


func _on_procure_product_pressed() -> void:
    if _product_catalog_ids.is_empty() or _procure_fixture_ids.is_empty():
        layout_edit_label.text = "No shelf fixture available to stock (buy one first)"
        _refresh_ui()
        return
    var catalog_id: String = _product_catalog_ids[product_catalog_option.selected]
    var fixture_id: String = _procure_fixture_ids[procure_fixture_option.selected]
    var instance_id := "product-purchase-%d" % _next_product_purchase_sequence
    _next_product_purchase_sequence += 1
    if simulation.try_procure_product(catalog_id, instance_id, fixture_id):
        layout_edit_label.text = "Stocked %s on %s" % [catalog_id, fixture_id]
        _refresh_restock_product_option()
    elif not simulation.customers.all_settled():
        layout_edit_label.text = "Finish the active visit before stocking a product"
    else:
        layout_edit_label.text = "Cannot stock %s on %s: missing permit, unaffordable, or already stocked there" % [
            catalog_id,
            fixture_id,
        ]
    _refresh_ui()


# Repopulated whenever the set of stocked products can have changed
# (procuring one, reset, load); sample-layout loading never removes a
# fixture holding stock (task #37), so it does not need to trigger this.
func _refresh_restock_product_option() -> void:
    restock_product_option.clear()
    _restock_product_ids.clear()
    for product_id in simulation.inventory.product_order:
        var product = simulation.inventory.get_product(product_id)
        _restock_product_ids.append(product_id)
        restock_product_option.add_item("%s (stock: %d)" % [product_id, product.stock_units])


func _on_restock_pressed() -> void:
    if _restock_product_ids.is_empty():
        layout_edit_label.text = "No stocked product to restock yet"
        _refresh_ui()
        return
    var product_id: String = _restock_product_ids[restock_product_option.selected]
    var product = simulation.inventory.get_product(product_id)
    var quantity: int = maxi(1, product.initial_stock_units)
    var total_cost_yen: int = quantity * product.restock_unit_cost_yen
    var staff_id: String = simulation.staff.checkout_staff().staff_id
    if simulation.apply_explicit_restock(product_id, staff_id, quantity, total_cost_yen):
        layout_edit_label.text = "Restocked %d units of %s for ¥%s" % [
            quantity,
            product_id,
            _format_integer(total_cost_yen),
        ]
        _refresh_restock_product_option()
    else:
        layout_edit_label.text = "Finish the active visit before restocking"
    _refresh_ui()


func _populate_promotion_option() -> void:
    promotion_option.clear()
    _promotion_ids.clear()
    for entry in config["promotions"]:
        _promotion_ids.append(str(entry["promotion_id"]))
        promotion_option.add_item(
            "%s — ¥%s (+%d popularity)" % [
                entry["promotion_id"],
                _format_integer(int(entry["cost_yen"])),
                int(entry["popularity_gain"]),
            ]
        )


func _on_buy_promotion_pressed() -> void:
    if _promotion_ids.is_empty():
        return
    var promotion_id: String = _promotion_ids[promotion_option.selected]
    if simulation.try_purchase_promotion(promotion_id):
        layout_edit_label.text = "Scheduled promotion: %s" % promotion_id
    elif not simulation.customers.all_settled():
        layout_edit_label.text = "Finish the active visit before buying a promotion"
    else:
        layout_edit_label.text = "Cannot buy that promotion: unaffordable or already scheduled/used this month"
    _refresh_ui()


func _on_expand_chain_pressed() -> void:
    if simulation.try_expand_chain():
        layout_edit_label.text = "Expanded the chain to %d store(s)" % int(simulation.player_store_count)
    elif not simulation.customers.all_settled():
        layout_edit_label.text = "Finish the active visit before expanding the chain"
    else:
        layout_edit_label.text = "Cannot expand the chain: unaffordable, or the scenario target is already reached"
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
        _refresh_procure_fixture_option()
        _refresh_restock_product_option()
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
    var active_customers: Array = snapshot["active_customers"]
    if active_customers.is_empty():
        customer_label.text = "no active customers"
    else:
        var customer_parts: Array[String] = []
        for entry in active_customers:
            customer_parts.append("%s: %s" % [entry["customer_id"], entry["phase"]])
        customer_label.text = "%d active — %s" % [active_customers.size(), ", ".join(customer_parts)]
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
    next_customer_button.disabled = not simulation.customers.can_admit_concurrent()
    rotate_fixture_button.disabled = store_view.selected_fixture().is_empty()
    expand_chain_button.text = "Expand chain (¥%s, currently %d store(s))" % [
        _format_integer(int(simulation.chain_expansion_cost_yen())),
        int(snapshot["player_store_count"]),
    ]
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
