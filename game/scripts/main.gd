extends Node2D

const VerticalSliceSimulationScript := preload("res://scripts/vertical_slice_simulation.gd")
const SaveGameServiceScript := preload("res://scripts/save_game_service.gd")
const GuideStartingStoreScript := preload("res://scripts/domain/guide_starting_store.gd")
const PhoneUIScript := preload("res://scripts/phone_ui.gd")

var _android_panel: Control = null
# Task #95: a new game starts on the town map with 「出店場所を選んで下さい」
# (the original's order: site first, then the store, guide p.6-11 and the
# PS review's opening flow); time stays stopped until a site is bought.
var selecting_site := false
# Task #123: picking the land for the next store (新規出店).
var choosing_new_store := false
var site_panel: PanelContainer = null
var site_info_label: Label = null
var site_buy_button: Button = null
var site_cancel_button: Button = null
var _site_origin := Vector2i(-1, -1)
# Task #104: the 「店舗を選んで下さい」 panel shown after the land is chosen.
var store_type_panel: PanelContainer = null
var store_type_info_label: Label = null
var store_type_build_button: Button = null
var _store_type_buttons: Dictionary = {}
var _store_type_choice := ""
var _store_view_left := -1.0
# Task #96: the newest event already turned into a sound, and whether the
# clear fanfare has played.
var _heard_event_sequence := 0
var _heard_clear := false
var sound_toggle_button: Button = null
# Task #97: what the tapped fixture holds, with its restock button, shown
# over the store (the side panel is a closed drawer on the phone).
var fixture_info_panel: PanelContainer = null
var fixture_info_label: Label = null
var fixture_restock_button: Button = null
var fixture_stock_button: Button = null
var fixture_info_icon: TextureRect = null
# Task #110: the phone screen (phone_ui.gd), and the game speed its
# ×1/×2/×4 button sets (platform presentation).
var phone_ui = null
var speed := 1
# Task #101: the rival store menu on the town map, like the original's
# 「調査する / 買収する / 何もしない」 (guide p.53).
var rival_panel: PanelContainer = null
var rival_info_label: Label = null
var rival_investigate_button: Button = null
var rival_buyout_button: Button = null
var _rival_id := ""

# Test seam (task #89): see _load_config(). An Engine meta flag rather than a
# static var because the --script smoke runner cannot preload this script
# (its GameLaunchState autoload reference only resolves inside a full run).
const PROTOTYPE_STORE_FOR_TESTS_META := "use_prototype_store_for_tests"
const MAIN_MENU_SCENE_PATH := "res://scenes/main_menu.tscn"
# Sentinel prefix store_view.selected_fixture_id carries while the player is
# placing a newly-bought fixture (task #38), reusing the same tap-to-target
# flow relocate already uses instead of a separate input mode. No owned
# fixture id can ever collide with this, since every generated purchase id
# below also carries the same prefix.
const NEW_FIXTURE_SELECTION_PREFIX := "__new:"

# Task #71: first menu-UI asset pass. Unlike tasks #67-#70's world sprites
# (this project's own newly-drawn art), these icons (assets/raw/
# conveni_menu_fixtures_v1/, conveni_menu_products_v1/, conveni_menu_
# staff_v1/) are cropped directly from the strategy guide's own printed
# menu-icon pages (README_CLAUDE.md: "攻略本の掲載アイコンを切り出し...
# 新規描き起こしではありません", each entry's manifest citing its exact
# source_pdf_page) -- CONFIRMED_VISUAL evidence for the icon artwork itself,
# not a REMAKE_BALANCED_DEFAULT placeholder. Every fixture_catalog/
# product_catalog entry in this file has a matching icon (verified: zero
# gaps either direction beyond a handful of icons for fixtures/products
# this client hasn't implemented yet, e.g. register_2..4, indoor/
# outdoor_dispenser, cash -- those simply go unused). Staff face icons use
# the exact same "staff_001".."staff_035" numbering as the task #69 walking
# sprites, so _menu_icon() reuses store_view's existing (REMAKE_BALANCED_
# DEFAULT, position-based) _staff_sprite_id_for_candidate() rather than
# inventing a second numbering convention.
const MENU_ICON_DIR := "res://assets/menu_icons/"
var _menu_icon_textures: Dictionary = {}

@onready var store_view: Node2D = $StoreView
@onready var town_view: Node2D = $TownView
@onready var show_town_map_button: Button = $UI/Panel/Margin/Scroll/VBox/ShowTownMapButton
@onready var clock_label: Label = $UI/TopBar/Margin/HBox/ClockValue
@onready var calendar_label: Label = $UI/TopBar/Margin/HBox/CalendarValue
@onready var weather_label: Label = $UI/TopBar/Margin/HBox/WeatherValue
@onready var cash_label: Label = $UI/TopBar/Margin/HBox/CashValue
@onready var stock_label: Label = $UI/Panel/Margin/Scroll/VBox/StockValue
@onready var basket_label: Label = $UI/Panel/Margin/Scroll/VBox/BasketValue
@onready var customer_label: Label = $UI/Panel/Margin/Scroll/VBox/CustomerValue
@onready var staff_label: Label = $UI/Panel/Margin/Scroll/VBox/StaffValue
@onready var sales_label: Label = $UI/Panel/Margin/Scroll/VBox/SalesValue
@onready var visits_label: Label = $UI/Panel/Margin/Scroll/VBox/VisitsValue
@onready var rating_label: Label = $UI/Panel/Margin/Scroll/VBox/RatingValue
@onready var scenario_status_label: Label = $UI/Panel/Margin/Scroll/VBox/ScenarioStatusValue
@onready var town_label: Label = $UI/Panel/Margin/Scroll/VBox/TownValue
@onready var event_label: Label = $UI/Panel/Margin/Scroll/VBox/EventValue
@onready var layout_edit_label: Label = $UI/Panel/Margin/Scroll/VBox/LayoutEditValue
@onready var pause_button: Button = $UI/Panel/Margin/Scroll/VBox/Buttons/PauseButton
@onready var step_button: Button = $UI/Panel/Margin/Scroll/VBox/Buttons/StepButton
@onready var reset_button: Button = $UI/Panel/Margin/Scroll/VBox/Buttons/ResetButton
@onready var next_customer_button: Button = $UI/Panel/Margin/Scroll/VBox/NextCustomerButton
@onready var eject_customer_option: OptionButton = $UI/Panel/Margin/Scroll/VBox/EjectCustomerOption
@onready var eject_customer_button: Button = $UI/Panel/Margin/Scroll/VBox/EjectCustomerButton
@onready var edit_mode_option: OptionButton = $UI/Panel/Margin/Scroll/VBox/EditModeOption
@onready var rotate_fixture_button: Button = $UI/Panel/Margin/Scroll/VBox/RotateFixtureButton
@onready var sell_fixture_button: Button = $UI/Panel/Margin/Scroll/VBox/SellFixtureButton
@onready var deselect_fixture_button: Button = $UI/Panel/Margin/Scroll/VBox/DeselectFixtureButton
@onready var sample_layout_option: OptionButton = $UI/Panel/Margin/Scroll/VBox/SampleLayoutOption
@onready var load_sample_layout_button: Button = $UI/Panel/Margin/Scroll/VBox/LoadSampleLayoutButton
@onready var fixture_catalog_option: OptionButton = $UI/Panel/Margin/Scroll/VBox/FixtureCatalogOption
@onready var buy_fixture_button: Button = $UI/Panel/Margin/Scroll/VBox/BuyFixtureButton
@onready var permit_option: OptionButton = $UI/Panel/Margin/Scroll/VBox/PermitOption
@onready var buy_permit_button: Button = $UI/Panel/Margin/Scroll/VBox/BuyPermitButton
@onready var product_catalog_option: OptionButton = $UI/Panel/Margin/Scroll/VBox/ProductCatalogOption
@onready var procure_fixture_option: OptionButton = $UI/Panel/Margin/Scroll/VBox/ProcureFixtureOption
@onready var procure_product_button: Button = $UI/Panel/Margin/Scroll/VBox/ProcureProductButton
@onready var restock_button: Button = $UI/Panel/Margin/Scroll/VBox/RestockButton
@onready var promotion_option: OptionButton = $UI/Panel/Margin/Scroll/VBox/PromotionOption
@onready var buy_promotion_button: Button = $UI/Panel/Margin/Scroll/VBox/BuyPromotionButton
@onready var expand_chain_button: Button = $UI/Panel/Margin/Scroll/VBox/ExpandChainButton
@onready var price_change_spin_box: SpinBox = $UI/Panel/Margin/Scroll/VBox/PriceChangeSpinBox
@onready var set_price_policy_button: Button = $UI/Panel/Margin/Scroll/VBox/SetPricePolicyButton
@onready var staff_slot_option: OptionButton = $UI/Panel/Margin/Scroll/VBox/StaffSlotOption
@onready var hire_candidate_option: OptionButton = $UI/Panel/Margin/Scroll/VBox/HireCandidateOption
@onready var hire_candidate_button: Button = $UI/Panel/Margin/Scroll/VBox/HireCandidateButton
@onready var save_button: Button = $UI/Panel/Margin/Scroll/VBox/MenuButtons/SaveButton
@onready var load_button: Button = $UI/Panel/Margin/Scroll/VBox/MenuButtons/LoadButton
@onready var quit_to_menu_button: Button = $UI/Panel/Margin/Scroll/VBox/MenuButtons/QuitToMenuButton
@onready var game_over_layer: CanvasLayer = $GameOverLayer
@onready var game_over_reason_label: Label = $GameOverLayer/Panel/Margin/VBox/GameOverReason
@onready var game_over_reset_button: Button = $GameOverLayer/Panel/Margin/VBox/GameOverButtons/GameOverResetButton
@onready var game_over_menu_button: Button = $GameOverLayer/Panel/Margin/VBox/GameOverButtons/GameOverMenuButton

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
var _eject_customer_ids: Array[String] = []
var _promotion_ids: Array[String] = []
var _staff_slot_ids: Array[String] = []
var _hire_candidate_ids: Array[String] = []
var _next_fixture_purchase_sequence := 1
var _next_product_purchase_sequence := 1


func _ready() -> void:
    # Task #92: always Japanese, like the original (see main_menu.gd).
    TranslationServer.set_locale("ja")
    price_change_spin_box.suffix = tr("% change from list price")
    _prepare_android_ui()
    config = _load_config()
    if config.is_empty():
        return
    simulation = VerticalSliceSimulationScript.new(config)
    # Task #104: the store (and so config["store"]/["fixtures"]/...) can
    # change when it is built, so the UI reads the simulation's own config.
    config = simulation.config
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
    town_view.bind(simulation)
    _fit_store_view()
    _build_site_panel()
    _build_store_type_panel()
    _build_fixture_info_panel()
    _build_rival_panel()
    town_view.map_tapped.connect(_on_map_tapped)
    town_view.site_tapped.connect(_on_site_tapped)
    _populate_sample_layout_option()
    _populate_fixture_catalog_option()
    _populate_permit_option()
    _populate_product_catalog_option()
    _populate_promotion_option()
    _refresh_procure_fixture_option()
    _populate_staff_slot_option()
    _refresh_hire_candidate_option()
    pause_button.pressed.connect(_on_pause_pressed)
    step_button.pressed.connect(_on_step_pressed)
    reset_button.pressed.connect(_on_reset_pressed)
    next_customer_button.pressed.connect(_on_next_customer_pressed)
    eject_customer_button.pressed.connect(_on_eject_customer_pressed)
    edit_mode_option.item_selected.connect(_on_edit_mode_selected)
    if edit_mode_option.selected < 0:
        edit_mode_option.select(0)
    rotate_fixture_button.pressed.connect(_on_rotate_fixture_pressed)
    sell_fixture_button.pressed.connect(_on_sell_fixture_pressed)
    deselect_fixture_button.pressed.connect(_on_deselect_fixture_pressed)
    store_view.fixture_swap_requested.connect(_on_fixture_swap_requested)
    load_sample_layout_button.pressed.connect(_on_load_sample_layout_pressed)
    buy_fixture_button.pressed.connect(_on_buy_fixture_pressed)
    buy_permit_button.pressed.connect(_on_buy_permit_pressed)
    procure_product_button.pressed.connect(_on_procure_product_pressed)
    restock_button.pressed.connect(_on_restock_pressed)
    buy_promotion_button.pressed.connect(_on_buy_promotion_pressed)
    expand_chain_button.pressed.connect(_on_expand_chain_pressed)
    set_price_policy_button.pressed.connect(_on_set_price_policy_pressed)
    staff_slot_option.item_selected.connect(_on_staff_slot_selected)
    hire_candidate_button.pressed.connect(_on_hire_candidate_pressed)
    save_button.pressed.connect(_on_save_pressed)
    load_button.pressed.connect(_on_load_pressed)
    quit_to_menu_button.pressed.connect(_on_quit_to_menu_pressed)
    show_town_map_button.pressed.connect(_on_show_town_map_pressed)
    # Task #75: the game-over overlay reuses the exact same handlers as the
    # sidebar's own Reset/Quit-to-Menu buttons, rather than duplicating
    # their logic -- "Play Again" is just this client's existing full
    # reset() path, and "Return to Menu" is the existing scene-change path.
    game_over_reset_button.pressed.connect(_on_reset_pressed)
    game_over_menu_button.pressed.connect(_on_quit_to_menu_pressed)
    store_view.fixture_selected.connect(_on_fixture_selected)
    store_view.fixture_relocation_requested.connect(_on_fixture_relocation_requested)
    _build_sound_toggle()
    _build_business_hours_controls()
    if _is_android_preview():
        phone_ui = PhoneUIScript.new()
        phone_ui.name = "PhoneUI"
        add_child(phone_ui)
        phone_ui.setup(self)
        store_view.editing = false
    var button_sfx := str(config["sound"]["button_sfx"])
    for node in $UI.find_children("*", "BaseButton", true, false):
        (node as BaseButton).pressed.connect(func(): SoundManager.play_sfx(button_sfx))
    _heard_event_sequence = _latest_event_sequence()
    _heard_clear = simulation.clear_condition_met
    _sync_site_selection()
    _refresh_ui()


func _process(delta: float) -> void:
    if simulation == null or paused or selecting_site:
        store_view.tick_progress = 1.0
        return
    accumulator += delta * speed
    while accumulator >= tick_seconds:
        accumulator -= tick_seconds
        simulation.tick()
        store_view.tick_serial += 1
        _refresh_ui()
    # Task #97: how far through the current tick we are, for the smooth
    # movement drawing (store_view.gd).
    store_view.tick_progress = accumulator / tick_seconds


func _unhandled_input(event: InputEvent) -> void:
    if event.is_action_pressed("ui_accept"):
        _on_pause_pressed()
        get_viewport().set_input_as_handled()


func _on_show_town_map_pressed() -> void:
    if selecting_site:
        return
    _rival_id = ""
    town_view.visible = not town_view.visible
    store_view.visible = not town_view.visible
    show_town_map_button.text = tr("Show store") if town_view.visible else tr("Show town map")
    if town_view.visible:
        town_view.queue_redraw()


func _on_pause_pressed() -> void:
    if simulation == null or selecting_site:
        return
    paused = not paused
    pause_button.text = tr("Resume") if paused else tr("Pause")
    _refresh_ui()


func _on_step_pressed() -> void:
    if simulation == null or simulation.customers.all_settled():
        return
    paused = true
    pause_button.text = tr("Resume")
    accumulator = 0.0
    simulation.step()
    _refresh_ui()


func _on_reset_pressed() -> void:
    if simulation == null:
        return
    paused = false
    pause_button.text = tr("Pause")
    accumulator = 0.0
    simulation.reset()
    _heard_event_sequence = _latest_event_sequence()
    _heard_clear = simulation.clear_condition_met
    _select_current_business_hours()
    layout_edit_label.text = tr("Layout reset to configured prototype")
    _refresh_procure_fixture_option()
    _refresh_hire_candidate_option()
    _sync_site_selection()
    _refresh_ui()


func _on_next_customer_pressed() -> void:
    if simulation == null or not simulation.start_next_customer():
        return
    paused = false
    pause_button.text = tr("Pause")
    accumulator = 0.0
    _refresh_ui()


# Task #52: unlike the other catalog-driven option lists above (fixtures/
# permits/products/promotions), which only change after an explicit player
# action and so are refreshed just after those actions, the set of
# ejectable customers changes on its own every tick as customers walk
# through the store -- so this is also called from _refresh_ui() (task
# #52), not only from _ready()/explicit action handlers.
func _refresh_eject_customer_option() -> void:
    eject_customer_option.clear()
    _eject_customer_ids.clear()
    for customer in simulation.customers.active_customers():
        if customer.phase == "waiting_checkout" or customer.phase == "checkout":
            _eject_customer_ids.append(customer.customer_id)
            eject_customer_option.add_item("%s（%s）" % [_customer_label(customer.customer_id), tr(customer.phase)])
    eject_customer_option.disabled = _eject_customer_ids.is_empty()
    eject_customer_button.disabled = _eject_customer_ids.is_empty()


func _on_eject_customer_pressed() -> void:
    if _eject_customer_ids.is_empty():
        layout_edit_label.text = tr("No customer currently at checkout to eject")
        _refresh_ui()
        return
    var customer_id: String = _eject_customer_ids[eject_customer_option.selected]
    if simulation.try_eject_customer(customer_id):
        layout_edit_label.text = tr("Ejected customer %s before they could get angry") % _customer_label(customer_id)
    else:
        layout_edit_label.text = tr("Could not eject %s") % _customer_label(customer_id)
    _refresh_ui()


func _on_fixture_selected(fixture_id: String) -> void:
    # Task #110: outside 内装 a tap only shows the fixture's card.
    if fixture_id.is_empty() or not store_view.editing:
        _refresh_ui()
        return
    if store_view.edit_mode == "swap":
        layout_edit_label.text = tr("Selected: %s — tap another fixture to swap") % _fixture_label(fixture_id)
    else:
        layout_edit_label.text = tr("Selected: %s — tap an empty grid cell to move") % _fixture_label(fixture_id)


func _on_fixture_relocation_requested(fixture_id: String, origin_subcell: Vector2i) -> void:
    if fixture_id.begins_with(NEW_FIXTURE_SELECTION_PREFIX):
        _try_place_new_fixture(fixture_id.substr(NEW_FIXTURE_SELECTION_PREFIX.length()), origin_subcell)
        return
    if fixture_id.begins_with(STORED_FIXTURE_SELECTION_PREFIX):
        # Task #125: setting a fixture down out of storage.
        var index := int(fixture_id.substr(STORED_FIXTURE_SELECTION_PREFIX.length()))
        store_view.selected_fixture_id = ""
        if simulation.try_place_stored_fixture(index, origin_subcell):
            layout_edit_label.text = tr("Set the fixture down from storage")
            _reopen_interior_window()
        else:
            _show_edit_refusal()
        _refresh_ui()
        return
    if simulation.try_relocate_fixture(fixture_id, origin_subcell):
        layout_edit_label.text = tr("Moved %s to (%d, %d)") % [
            _fixture_label(fixture_id),
            origin_subcell.x,
            origin_subcell.y,
        ]
    elif not simulation.customers.all_settled() and not simulation._edits_while_open:
        layout_edit_label.text = tr("Finish the active visit before editing layout")
    else:
        _show_edit_refusal()
    _refresh_ui()


# Task #125: why an edit was refused, and the shelf it would cut off shown
# in red for a moment.
const STORED_FIXTURE_SELECTION_PREFIX := "__stored:"


func _show_edit_refusal() -> void:
    var reason: String = simulation.edit_refusal
    if reason == "locked":
        layout_edit_label.text = tr("Finish the active visit before editing layout")
    elif reason == "route:checkout":
        layout_edit_label.text = tr("That would cut off the register or the exit")
    elif reason.begins_with("route:"):
        var product_id := reason.substr(6)
        layout_edit_label.text = tr("That would cut off the %s shelf") % _product_label(product_id)
        if simulation.inventory.products.has(product_id):
            store_view.warn_fixture(simulation.inventory.get_product(product_id).fixture_id)
    elif reason == "people":
        layout_edit_label.text = tr("Someone is standing in the way")
    else:
        layout_edit_label.text = tr("A wall or another fixture is in the way")


# Task #126: 改装 -- the store becomes store type `type_id` (another size or
# orientation), see VerticalSliceSimulation.try_renovate_store().
func renovate_store(type_id: String) -> bool:
    if not simulation.try_renovate_store(type_id):
        layout_edit_label.text = tr("Not enough money to renovate") if simulation.edit_refusal == "cash" else tr("Cannot renovate into this store")
        SoundManager.play_sfx(str(config["sound"]["refused_sfx"]))
        return false
    store_view.selected_fixture_id = ""
    _store_layout_changed()
    var moved: Dictionary = simulation.event_log.records[-1]["details"] if simulation.event_log.records[-1]["event_type"] == "store_renovated" else {}
    layout_edit_label.text = tr("Renovated the store (%d fixtures put in storage)") % int(moved.get("fixtures_stored", 0))
    _reopen_interior_window()
    _refresh_ui()
    return true


# The size, orientation (縦長/横長) and floor of a store type, for the
# store type buttons.
func store_type_caption(entry: Dictionary) -> String:
    var floor_tiles: Array = entry["floor_tiles"]
    var shape := tr("tall") if int(floor_tiles[1]) > int(floor_tiles[0]) else tr("wide")
    return "%s・%s %d×%d" % [tr("store_tier_" + str(entry["size_tier"])), shape, int(floor_tiles[0]), int(floor_tiles[1])]


# The phone's 内装 window lists the storage; rebuild it after a change.
func _reopen_interior_window() -> void:
    if phone_ui != null and phone_ui.window_id == "interior":
        phone_ui.open_window("interior")


func _on_store_fixture_pressed() -> void:
    var fixture_id: String = store_view.selected_fixture()
    if fixture_id.is_empty() or fixture_id.begins_with("__"):
        return
    var label := _fixture_label(fixture_id)
    if simulation.try_store_fixture(fixture_id):
        store_view.selected_fixture_id = ""
        layout_edit_label.text = tr("Put %s into storage") % label
        _refresh_procure_fixture_option()
        _reopen_interior_window()
    elif simulation.edit_refusal == "locked":
        _show_edit_refusal()
    else:
        layout_edit_label.text = tr("The register and the break room stay in place")
    _refresh_ui()


func _on_rotate_fixture_pressed() -> void:
    var fixture_id: String = store_view.selected_fixture()
    if fixture_id.is_empty():
        layout_edit_label.text = tr("Select a fixture before rotating")
    elif simulation.try_rotate_fixture_clockwise(fixture_id):
        layout_edit_label.text = tr("Rotated %s clockwise") % _fixture_label(fixture_id)
    elif not simulation.customers.all_settled() and not simulation._edits_while_open:
        layout_edit_label.text = tr("Finish the active visit before editing layout")
    else:
        _show_edit_refusal()
    _refresh_ui()


# Task #78: EditModeOption's two items are declared in main.tscn as
# id 0 = "Move", id 1 = "Swap" (matching store_view.edit_mode's own
# "move"/"swap" string values).
func _on_edit_mode_selected(index: int) -> void:
    store_view.edit_mode = "swap" if edit_mode_option.get_item_id(index) == 1 else "move"


func _on_fixture_swap_requested(fixture_id_a: String, fixture_id_b: String) -> void:
    if simulation.try_swap_fixtures(fixture_id_a, fixture_id_b):
        layout_edit_label.text = tr("Swapped %s and %s") % [_fixture_label(fixture_id_a), _fixture_label(fixture_id_b)]
    elif not simulation.customers.all_settled():
        layout_edit_label.text = tr("Finish the active visit before editing layout")
    else:
        layout_edit_label.text = tr("Cannot swap those: route would break")
    _refresh_ui()


func _on_sell_fixture_pressed() -> void:
    var fixture_id: String = store_view.selected_fixture()
    # The name is read before the sale: afterwards the fixture is gone.
    var label := _fixture_label(fixture_id)
    if fixture_id.is_empty():
        layout_edit_label.text = tr("Select a fixture before selling")
    elif simulation.try_sell_fixture(fixture_id):
        # Task #117: a shelf is sold with its goods, which go back at cost.
        var goods_refund := int(simulation.event_log.records[-1]["details"].get("goods_refund_yen", 0))
        if goods_refund > 0:
            layout_edit_label.text = tr("Sold %s (goods returned: ¥%s)") % [label, _format_integer(goods_refund)]
        else:
            layout_edit_label.text = tr("Sold %s") % label
        store_view.selected_fixture_id = ""
        _refresh_procure_fixture_option()
    elif simulation._layout_edit_locked():
        layout_edit_label.text = tr("Finish the active visit before selling a fixture")
    else:
        layout_edit_label.text = tr("Cannot sell that fixture: it's the checkout or has no catalog price")
    _refresh_ui()


func _on_deselect_fixture_pressed() -> void:
    store_view.selected_fixture_id = ""
    layout_edit_label.text = tr("Deselected")
    _refresh_ui()


func _populate_sample_layout_option() -> void:
    sample_layout_option.clear()
    _sample_layout_ids.clear()
    for entry in config["sample_layouts"]:
        _sample_layout_ids.append(str(entry["sample_id"]))
        sample_layout_option.add_item(tr(str(entry["label"])))


func _on_load_sample_layout_pressed() -> void:
    if _sample_layout_ids.is_empty():
        return
    var sample_id: String = _sample_layout_ids[sample_layout_option.selected]
    if simulation.try_load_sample_layout(sample_id):
        layout_edit_label.text = tr("Loaded sample layout: %s") % tr(str(simulation._sample_layout_catalog[sample_id]["label"]))
        _refresh_procure_fixture_option()
    elif not simulation.customers.all_settled():
        layout_edit_label.text = tr("Finish the active visit before loading a sample layout")
    else:
        layout_edit_label.text = tr("Cannot load that sample layout: unaffordable or would strand stocked inventory")
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
        var catalog_id := str(entry["catalog_id"])
        _fixture_catalog_ids.append(catalog_id)
        fixture_catalog_option.add_item(
            "%s — ¥%s" % [tr(catalog_id), _format_integer(int(entry["purchase_price_yen"]))]
        )
        var icon := _menu_icon("fixtures", catalog_id)
        if icon != null:
            fixture_catalog_option.set_item_icon(fixture_catalog_option.item_count - 1, icon)


func _on_buy_fixture_pressed() -> void:
    if _fixture_catalog_ids.is_empty():
        return
    var catalog_id: String = _fixture_catalog_ids[fixture_catalog_option.selected]
    store_view.selected_fixture_id = NEW_FIXTURE_SELECTION_PREFIX + catalog_id
    layout_edit_label.text = tr("Buying %s — tap an empty grid cell to place it") % tr(catalog_id)
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
    if simulation._front_search_enabled():
        # Task #125: the front goes on whichever side works.
        var auto_id := "fixture-purchase-%d" % _next_fixture_purchase_sequence
        _next_fixture_purchase_sequence += 1
        if simulation.try_purchase_fixture_at(catalog_id, auto_id, origin_subcell):
            layout_edit_label.text = tr("Purchased %s") % tr(catalog_id)
            _refresh_procure_fixture_option()
        elif simulation.economy.cash_yen < int(catalog_entry["purchase_price_yen"]):
            layout_edit_label.text = tr("Cannot place %s there: blocked, unaffordable, or route would break") % tr(catalog_id)
        else:
            _show_edit_refusal()
        _refresh_ui()
        return
    var interaction := _find_open_interaction_cell(origin_subcell, width, height)
    if interaction == Vector2i(-1, -1):
        layout_edit_label.text = tr("Cannot place %s there: no open cell next to it for customers/staff to use") % tr(catalog_id)
        _refresh_ui()
        return
    var instance_id := "fixture-purchase-%d" % _next_fixture_purchase_sequence
    _next_fixture_purchase_sequence += 1
    if simulation.try_purchase_fixture(catalog_id, instance_id, origin_subcell, interaction):
        layout_edit_label.text = tr("Purchased %s") % tr(catalog_id)
        _refresh_procure_fixture_option()
    elif not simulation.customers.all_settled():
        layout_edit_label.text = tr("Finish the active visit before buying a fixture")
    else:
        layout_edit_label.text = tr("Cannot place %s there: blocked, unaffordable, or route would break") % tr(catalog_id)
    _refresh_ui()


# REMAKE_BALANCED_DEFAULT (task #38): the catalog only records a fixture's
# footprint, not where its interaction point goes, and no strategy-guide/
# wiki source states a placement rule for where a newly-bought fixture's
# interaction point should land -- this is not a recovered original
# placement rule. Every existing fixture in vertical_slice.json happens to
# place that point one subcell outside its own footprint, so this reuses
# that observation as a convenience heuristic (avoiding a second tap from
# the player) rather than inventing an unrelated rule. Tries the four
# cardinal neighbors of the footprint's top-left corner and returns the
# first that is walkable before this fixture is added; Vector2i(-1, -1)
# means none of the four worked.
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
        permit_option.add_item("%s — ¥%s" % [tr(str(entry["permit_id"])), _format_integer(int(entry["fee_yen"]))])


func _on_buy_permit_pressed() -> void:
    if _permit_ids.is_empty():
        return
    var permit_id: String = _permit_ids[permit_option.selected]
    if simulation.has_permit(permit_id):
        layout_edit_label.text = tr("Already hold the %s permit") % tr(permit_id)
    elif simulation.try_purchase_permit(permit_id):
        layout_edit_label.text = tr("Purchased permit: %s") % tr(permit_id)
    else:
        layout_edit_label.text = tr("Cannot afford the %s permit") % tr(permit_id)
    _refresh_ui()


func _populate_product_catalog_option() -> void:
    product_catalog_option.clear()
    _product_catalog_ids.clear()
    for entry in config["product_catalog"]:
        var catalog_id := str(entry["catalog_id"])
        _product_catalog_ids.append(catalog_id)
        product_catalog_option.add_item(
            tr("%s — ¥%s/unit") % [tr(catalog_id), _format_integer(int(entry["restock_unit_cost_yen"]))]
        )
        var icon := _menu_icon("products", catalog_id)
        if icon != null:
            product_catalog_option.set_item_icon(product_catalog_option.item_count - 1, icon)


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
            procure_fixture_option.add_item(_fixture_label(fixture_id))


func _on_procure_product_pressed() -> void:
    if _product_catalog_ids.is_empty() or _procure_fixture_ids.is_empty():
        layout_edit_label.text = tr("No shelf fixture available to stock (buy one first)")
        _refresh_ui()
        return
    var catalog_id: String = _product_catalog_ids[product_catalog_option.selected]
    var fixture_id: String = _procure_fixture_ids[procure_fixture_option.selected]
    var instance_id := "product-purchase-%d" % _next_product_purchase_sequence
    _next_product_purchase_sequence += 1
    if simulation.try_procure_product(catalog_id, instance_id, fixture_id):
        layout_edit_label.text = tr("Stocked %s on %s") % [tr(catalog_id), _fixture_label(fixture_id)]
    elif not simulation.customers.all_settled():
        layout_edit_label.text = tr("Finish the active visit before stocking a product")
    else:
        layout_edit_label.text = tr("Cannot stock %s on %s: missing permit, unaffordable, or already stocked there") % [
            tr(catalog_id),
            _fixture_label(fixture_id),
        ]
    _refresh_ui()


# Task #79/#80: CONFIRMED_OFFICIAL (owner direct-play testimony, 2026-09-24,
# independently corroborated by docs/research/strategy-guide-third-companion-
# book-full-extraction-2026-09-24.md's PDF1 p.68-71 Q&A transcription --
# "player CAN manually restock via cursor+select"; see docs/decisions/
# 0149-*.md and 0150-*.md): the restock command is not an always-available
# generic picker. It only becomes available for the currently selected
# fixture, and only once that fixture's stocked product is running low.
# This reuses
# store_view.selected_fixture()/_product_on_fixture() (the same fixture
# selection this UI already uses for move/swap/sell/rotate) and the
# existing restock_trigger_stock_units_at_or_below threshold that
# _step_restock_tasks() already uses to trigger the autonomous staff
# restock task (decision 0089) -- not a second, independently invented
# threshold.
func _selected_fixture_restock_target():
    var fixture_id: String = store_view.selected_fixture()
    if fixture_id.is_empty():
        return null
    var product = store_view._product_on_fixture(fixture_id)
    if product == null:
        return null
    # Task #97: the owner's testimony (decision 0149) is 「中身が減っていると
    # 補充のコマンドが出て」 -- available as soon as the shelf is not full,
    # not only once it is empty (the old reading of the staff trigger level).
    if product.stock_units >= product.initial_stock_units:
        return null
    return product


func _on_restock_pressed() -> void:
    var product = _selected_fixture_restock_target()
    if product == null:
        layout_edit_label.text = tr("Select a shelf that is not full to restock it")
        _refresh_ui()
        return
    # REMAKE_BALANCED_DEFAULT (task #38): apply_explicit_restock() takes an
    # arbitrary caller-chosen quantity; no strategy-guide/wiki source states
    # a real order-lot size, so this button's one-tap batch size (the
    # product's own initial_stock_units) is this UI's own default, not a
    # recovered original restock quantity. total_cost_yen is not invented,
    # though: it is quantity times the product's own CONFIRMED_OFFICIAL
    # restock_unit_cost_yen.
    # Task #97: fills the shelf back up to its starting (full) stock, never
    # beyond it.
    var quantity: int = product.initial_stock_units - product.stock_units
    var total_cost_yen: int = quantity * product.restock_unit_cost_yen
    var staff_id: String = simulation.staff.checkout_staff().staff_id
    if simulation.apply_explicit_restock(product.product_id, staff_id, quantity, total_cost_yen):
        layout_edit_label.text = tr("Restocked %d units of %s for ¥%s") % [
            quantity,
            _product_label(product.product_id),
            _format_integer(total_cost_yen),
        ]
    else:
        layout_edit_label.text = tr("Cannot restock now")
    _refresh_ui()


func _populate_promotion_option() -> void:
    promotion_option.clear()
    _promotion_ids.clear()
    for entry in config["promotions"]:
        _promotion_ids.append(str(entry["promotion_id"]))
        promotion_option.add_item(
            tr("%s — ¥%s (+%d popularity)") % [
                tr(str(entry["promotion_id"])),
                _format_integer(int(entry["cost_yen"])),
                int(entry["popularity_gain"]),
            ]
        )


func _on_buy_promotion_pressed() -> void:
    if _promotion_ids.is_empty():
        return
    var promotion_id: String = _promotion_ids[promotion_option.selected]
    if simulation.try_purchase_promotion(promotion_id):
        layout_edit_label.text = tr("Scheduled promotion: %s") % tr(promotion_id)
    else:
        layout_edit_label.text = tr("Cannot buy that promotion: unaffordable or already scheduled/used this month")
    _refresh_ui()


func _on_expand_chain_pressed() -> void:
    if simulation.try_expand_chain():
        layout_edit_label.text = tr("Expanded the chain to %d store(s)") % int(simulation.player_store_count)
    elif simulation.town_is_full():
        layout_edit_label.text = tr("The town already has 10 stores, rivals included")
    else:
        layout_edit_label.text = tr("Cannot expand the chain: unaffordable, or the scenario target is already reached")
    _refresh_ui()


func _on_set_price_policy_pressed() -> void:
    var new_price_change_pct: int = int(round(price_change_spin_box.value))
    if simulation.try_set_price_policy(new_price_change_pct):
        layout_edit_label.text = tr("Price policy set: %+d%% from list price") % new_price_change_pct
    else:
        layout_edit_label.text = tr("Cannot set that price policy (must be -100% or above)")
    _refresh_ui()


# Task #56: staff_slot_option is populated once at _ready() (the roster's
# slot ids -- staff-1/staff-2 plus the manager's staff-3 since task #91 --
# never change, only who occupies them does), unlike hire_candidate_option
# below.
func _populate_staff_slot_option() -> void:
    staff_slot_option.clear()
    _staff_slot_ids.clear()
    for staff_id in simulation.staff.members.keys():
        _staff_slot_ids.append(str(staff_id))
        staff_slot_option.add_item(str(staff_id))


func _on_staff_slot_selected(_index: int) -> void:
    _refresh_hire_candidate_option()


# Task #56: unlike the static catalog-driven option lists above (fixtures/
# permits/products/promotions), which are populated once from config and
# never change again, which candidates are selectable here changes as soon
# as a hire happens elsewhere -- try_hire_candidate()'s own cross-slot
# collision rule (a real person can't occupy both slots at once) means the
# newly-hired candidate must drop out of this list for the OTHER slot,
# while whoever they replaced becomes selectable again. So this is
# refreshed after every hire, on slot-selection change, and on reset/load,
# but (unlike _refresh_eject_customer_option()) not every _process() tick,
# since nothing else changes this set between explicit player actions.
func _refresh_hire_candidate_option() -> void:
    hire_candidate_option.clear()
    _hire_candidate_ids.clear()
    if _staff_slot_ids.is_empty():
        hire_candidate_button.disabled = true
        return
    var selected_staff_id: String = _staff_slot_ids[staff_slot_option.selected]
    var employed_elsewhere: Array[String] = []
    for staff_member in simulation.staff.all_staff():
        if staff_member.staff_id != selected_staff_id:
            employed_elsewhere.append(staff_member.candidate_id)
    for entry in config["staff_candidates"]:
        var candidate_id := str(entry["candidate_id"])
        if candidate_id in employed_elsewhere:
            continue
        _hire_candidate_ids.append(candidate_id)
        hire_candidate_option.add_item(
            tr("%s — register %d / replen %d / ¥%s/day (体力%s 学歴%s 敏捷性%s 社交性%s)") % [
                entry["display_name"],
                int(entry["register_skill"]),
                int(entry["replenishment_skill"]),
                _format_integer(int(entry["salary_yen_per_day_24h"])),
                _resume_stat_band(int(entry["stamina"])),
                _resume_stat_band(int(entry["academic_background"])),
                _resume_stat_band(int(entry["agility"])),
                _resume_stat_band(int(entry["sociability"])),
            ]
        )
        var icon := _menu_icon("staff", store_view._staff_sprite_id_for_candidate(candidate_id))
        if icon != null:
            hire_candidate_option.set_item_icon(hire_candidate_option.item_count - 1, icon)
    hire_candidate_button.disabled = _hire_candidate_ids.is_empty()


func _on_hire_candidate_pressed() -> void:
    if _staff_slot_ids.is_empty() or _hire_candidate_ids.is_empty():
        layout_edit_label.text = tr("No candidate available to hire")
        _refresh_ui()
        return
    var staff_id: String = _staff_slot_ids[staff_slot_option.selected]
    var candidate_id: String = _hire_candidate_ids[hire_candidate_option.selected]
    if simulation.try_hire_candidate(staff_id, candidate_id):
        layout_edit_label.text = tr("Hired %s into %s") % [_candidate_label(candidate_id), tr(staff_id)]
        _refresh_hire_candidate_option()
    elif not simulation.customers.all_settled():
        layout_edit_label.text = tr("Finish the active visit before hiring")
    else:
        layout_edit_label.text = tr("Cannot hire %s into %s") % [_candidate_label(candidate_id), tr(staff_id)]
    _refresh_ui()


func _on_save_pressed() -> void:
    if simulation == null:
        return
    if _save_service.save_to_path(simulation):
        layout_edit_label.text = tr("Game saved")
    else:
        layout_edit_label.text = tr("Save failed")
    _refresh_ui()


func _on_load_pressed() -> void:
    if simulation == null:
        return
    if _save_service.load_from_path(simulation):
        _select_current_business_hours()
        _heard_event_sequence = _latest_event_sequence()
        _heard_clear = simulation.clear_condition_met
        paused = false
        pause_button.text = tr("Pause")
        accumulator = 0.0
        layout_edit_label.text = tr("Game loaded")
        _refresh_procure_fixture_option()
        _refresh_hire_candidate_option()
        _sync_site_selection()
    else:
        layout_edit_label.text = tr("No compatible save found")
    _refresh_ui()


func _on_quit_to_menu_pressed() -> void:
    GameLaunchState.continue_from_save = false
    get_tree().change_scene_to_file(MAIN_MENU_SCENE_PATH)


func _refresh_ui() -> void:
    if simulation == null:
        return
    var snapshot: Dictionary = simulation.snapshot()
    clock_label.text = str(snapshot["clock_text"])
    # Task #103: whether the store is open right now.
    if not simulation.is_open_now():
        clock_label.text += "　" + tr("Closed")
    # Task #77: task #75's original "Month X · Day Y of Z (Day N overall)"
    # was invented without checking docs/research/official-screenshot-
    # evidence-2026-09-05.md section 1, which already had CONFIRMED_
    # OFFICIAL/CONFIRMED_VISUAL evidence for this: the official PS-version
    # screenshot ss01 shows the date as "01年目01月01日" (year/month/day),
    # not a bare month+day counter, and omits any "day N of 4" or running
    # total. This client's own REPRESENTATIVE_DAYS_PER_MONTH=4 (also
    # CONFIRMED_OFFICIAL, "1月=4日間×8") means the day this client actually
    # simulates within a month IS 1-4, so showing days_completed_this_month
    # + 1 as "Day" is the correct representative-day value, not an invented
    # abstraction -- only the missing Year field and the extra "of 4 (Day N
    # overall)" suffix (neither shown on the official screen) were the
    # actual gaps. Kept in English rather than the screenshot's literal
    # Japanese to stay consistent with the rest of this client's UI text.
    var calendar_year: int = int(snapshot["month_count"]) / VerticalSliceSimulationScript.MONTHS_PER_YEAR + 1
    var calendar_month_in_year: int = int(snapshot["month_count"]) % VerticalSliceSimulationScript.MONTHS_PER_YEAR + 1
    calendar_label.text = tr("Year %d · Month %d, Day %d") % [
        calendar_year,
        calendar_month_in_year,
        int(snapshot["days_completed_this_month"]) + 1,
    ]
    # Task #85: bracketed like the original HUD, one-character labels padded
    # to two cells ("［雨 ］" in the gameplay-video frame video_900s.png).
    weather_label.text = "［%s］" % str(snapshot["weather_display_label"]).rpad(2)
    cash_label.text = "¥%s" % _format_integer(int(snapshot["cash_yen"]))
    stock_label.text = tr("%d units") % int(snapshot["stock_units"])
    basket_label.text = tr("%d items / ¥%s") % [
        int(snapshot["customer_basket_count"]),
        _format_integer(int(snapshot["customer_basket_total_yen"])),
    ]
    var active_customers: Array = snapshot["active_customers"]
    if active_customers.is_empty():
        customer_label.text = tr("no active customers")
    else:
        var customer_parts: Array[String] = []
        for entry in active_customers:
            customer_parts.append(tr(str(entry["phase"])))
        customer_label.text = tr("%d active — %s") % [active_customers.size(), ", ".join(customer_parts)]
    staff_label.text = tr("%s: %s (%d staff)") % [
        tr(str(snapshot["staff_id"])),
        tr(str(snapshot["staff_state"])),
        int(snapshot["staff_count"]),
    ]
    var last_sale: Dictionary = snapshot["last_sale"]
    sales_label.text = str(snapshot["completed_sales"])
    if not last_sale.is_empty():
        sales_label.text += tr(" (last: ¥%s)") % _format_integer(int(last_sale["total_yen"]))
    visits_label.text = tr("Visits: %d / %d") % [
        int(snapshot["completed_visits"]),
        int(snapshot["started_visits"]),
    ]
    rating_label.text = tr("%s (popularity %d)") % [
        _star_rank_text(int(snapshot["star_rating"])),
        int(snapshot["popularity"]),
    ]
    # Task #75: clear_condition_met (player_store_count reaching the
    # PROVISIONAL PLAYER_STORE_COUNT_SCENARIO_TARGET) is a permanent flag,
    # not a one-time event -- the player keeps playing after clearing it
    # (see _evaluate_terminal_state()'s own comment), so this label just
    # stays on rather than needing separate "already shown once" state.
    if bool(snapshot["clear_condition_met"]) and not simulation._town_growth().is_empty():
        # Task #114: the beginner map's clear, 都庁を誘致する.
        scenario_status_label.text = "都庁が建ちました。初級マップクリア（このまま続けられます）"
    elif bool(snapshot["clear_condition_met"]):
        scenario_status_label.text = tr("Scenario cleared — reached %d stores (you can keep playing)") % [
            VerticalSliceSimulationScript.PLAYER_STORE_COUNT_SCENARIO_TARGET
        ]
    else:
        scenario_status_label.text = ""
    var rival_store_count: int = int(snapshot["town_store_count_including_rivals"]) - int(snapshot["player_store_count"])
    town_label.text = tr("population %s, %d rival store%s, land ¥%s") % [
        _format_integer(int(snapshot["town_population"])),
        rival_store_count,
        "" if TranslationServer.get_locale().begins_with("ja") or rival_store_count == 1 else "s",
        _format_integer(int(snapshot["land_value_yen"])),
    ]
    _refresh_survey_label()
    event_label.text = tr(str(snapshot["last_event"]))
    if paused:
        event_label.text += tr("  [PAUSED]")
    next_customer_button.disabled = not simulation.customers.can_admit_concurrent()
    _refresh_eject_customer_option()
    rotate_fixture_button.disabled = store_view.selected_fixture().is_empty()
    sell_fixture_button.disabled = store_view.selected_fixture().is_empty()
    # Task #79: contextual restock -- see the evidence comment on
    # _selected_fixture_restock_target() for why this is gated on the
    # selected fixture's own stock level rather than always enabled.
    var restock_target = _selected_fixture_restock_target()
    if restock_target == null:
        restock_button.disabled = true
        restock_button.text = tr("Restock selected product")
    else:
        restock_button.disabled = false
        restock_button.text = tr("Restock %s (stock: %d)") % [_product_label(restock_target.product_id), restock_target.stock_units]
    expand_chain_button.text = tr("Expand chain (¥%s, currently %d store(s))") % [
        _format_integer(int(simulation.chain_expansion_cost_yen())),
        int(snapshot["player_store_count"]),
    ]
    set_price_policy_button.text = tr("Set price policy (currently %+d%%)") % int(snapshot["price_change_pct"])
    # Task #75: is_game_over/game_over_reason have existed on the simulation
    # since the bankrupt/time-limit game-over paths were wired, but nothing
    # in this UI ever surfaced them -- every economy action's own is_game_
    # over guard already made them silently stop working, with no on-screen
    # explanation. The overlay's full-screen background blocks further
    # input by default Control mouse-filter behavior, so no other button
    # needs its own is_game_over check added.
    var game_over_now: bool = bool(snapshot["is_game_over"])
    game_over_layer.visible = game_over_now
    if game_over_now:
        game_over_reason_label.text = _game_over_reason_text(str(snapshot["game_over_reason"]))
        if not paused:
            paused = true
            pause_button.text = tr("Resume")
    store_view.queue_redraw()
    _refresh_fixture_info()
    if rival_panel != null:
        _refresh_rival_panel()
    _play_event_sounds()
    if phone_ui != null:
        phone_ui.refresh()


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
    # Task #89/#104: every new game gets the guide town and, once the land
    # and store are chosen, a furnished small store (GuideStartingStore).
    # The automated UI scenarios set the
    # PROTOTYPE_STORE_FOR_TESTS_META Engine meta to keep the small
    # prototype store their scripted coordinates were written against.
    if not Engine.has_meta(PROTOTYPE_STORE_FOR_TESTS_META):
        loaded = GuideStartingStoreScript.apply(loaded)
    # The researched beginner cash anchor (¥200,000,000, also on the guide
    # p.11 start screen the town map is read from). Task #95: every real new
    # game now starts with it, since the land is bought out of it; the
    # furnished store itself is still granted (REMAKE_BALANCED_DEFAULT, see
    # android_preview.evidence_note).
    if _is_android_preview() or not Engine.has_meta(PROTOTYPE_STORE_FOR_TESTS_META):
        loaded["economy"]["initial_cash_yen"] = int(loaded["android_preview"]["starting_cash_yen"])
    return loaded


func _star_rank_text(star_rating: int) -> String:
    assert(star_rating >= 0 and star_rating <= 5)
    return "★".repeat(star_rating) + "☆".repeat(5 - star_rating)


# Task #75: game_over_reason is one of the two literal strings
# _trigger_game_over() ever passes ("bankrupt"/"time_limit_exceeded", see
# vertical_slice_simulation.gd's own CONFIRMED comment on
# GAME_OVER_YEAR_LIMIT/bankruptcy above _init()) -- this only translates
# those two known values into player-facing copy, it does not invent a
# third game-over condition.
func _game_over_reason_text(reason: String) -> String:
    match reason:
        "bankrupt":
            return tr("Cash went negative at a day/month boundary.")
        "time_limit_exceeded":
            return tr("100 years passed without reaching the scenario's clear condition.")
        _:
            return reason


func _menu_icon(category: String, id: String) -> Texture2D:
    if category.is_empty() or id.is_empty():
        return null
    var cache_key := category + "/" + id
    if _menu_icon_textures.has(cache_key):
        return _menu_icon_textures[cache_key] as Texture2D
    var path := MENU_ICON_DIR + cache_key + ".png"
    var texture: Texture2D = null
    if ResourceLoader.exists(path):
        texture = load(path) as Texture2D
    _menu_icon_textures[cache_key] = texture
    return texture


# CONFIRMED_OFFICIAL (third companion book, docs/research/strategy-guide-
# third-companion-book-full-extraction-2026-09-24.md, "人材募集した段階
# では、その人のこまかい能力まではわからない...4つの能力とパラメータは
# 下の表のようになっている" -- 体力~スタミナ, 学歴~レジ・セキュリティ
# 能力, 敏捷性~商品補充・店内移動速度, 社交性~サービス・清掃能力): the
# original hiring screen's 4 résumé stats (体力/学歴/敏捷性/社交性) each
# reveal only a coarse band before hiring, not the exact underlying
# number -- 40-69 is "普通", 70-100 is "高い". This dropdown already shows
# the exact real skill numbers (task #56's staff_candidates data), so the
# band is appended as additional source-faithful context, not a removal
# of information the player currently sees.
func _resume_stat_band(value: int) -> String:
    return "高い" if value >= 70 else "普通"


func _format_integer(value: int) -> String:
    var raw := str(abs(value))
    var chunks: Array[String] = []
    while raw.length() > 3:
        chunks.push_front(raw.right(3))
        raw = raw.left(raw.length() - 3)
    chunks.push_front(raw)
    var joined := ",".join(chunks)
    return "-%s" % joined if value < 0 else joined


# Task #89: platform presentation only. Shrinks the store drawing (never
# enlarges it) so the whole floor fits left of the controls; the prototype
# store used by the tests already fits and stays at scale 1. Taps still map
# correctly because store_view converts them with to_local().
func _fit_store_view() -> void:
    if phone_ui != null:
        phone_ui.layout_screen()
        return
    var store: Dictionary = config["store"]
    var tile_pixels: float = store_view.SUBCELL_PIXELS * int(store["subcells_per_tile"])
    var natural := Vector2(int(store["width_tiles"]), int(store["height_tiles"])) * tile_pixels
    var right_edge: float = ($UI/Panel as Control).offset_left - 20.0
    var shortcuts := $UI.get_node_or_null("AndroidShortcuts") as Control
    if _store_view_left < 0.0:
        _store_view_left = store_view.position.x
    store_view.position.x = _store_view_left
    if shortcuts != null:
        store_view.position.x = 20.0
        right_edge = shortcuts.position.x - 10.0
    var available := Vector2(right_edge - store_view.position.x, 710.0 - store_view.position.y)
    var fit := minf(1.0, minf(available.x / natural.x, available.y / natural.y))
    store_view.scale = Vector2(fit, fit)
    # Task #90: the town map uses the same area.
    town_view.position = store_view.position
    town_view.view_size = available
    # Task #104: a small store is centred in that area instead of hugging
    # its left edge.
    store_view.position.x += maxf(0.0, (available.x - natural.x * fit) / 2.0)


# Task #95: the 「出店場所を選んで下さい」 bar along the bottom of the town
# map: what the tapped site is and costs, and the button that buys it.
# Platform presentation; the rules and prices come from StoreSite.
func _build_site_panel() -> void:
    site_panel = PanelContainer.new()
    site_panel.name = "SitePanel"
    site_panel.theme = ($UI/Panel as Control).theme
    site_panel.visible = false
    var box := VBoxContainer.new()
    site_panel.add_child(box)
    var title := Label.new()
    title.text = tr("Choose where to build your store")
    box.add_child(title)
    var row := HBoxContainer.new()
    box.add_child(row)
    site_info_label = Label.new()
    site_info_label.size_flags_horizontal = Control.SIZE_EXPAND_FILL
    site_info_label.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
    row.add_child(site_info_label)
    site_buy_button = Button.new()
    site_buy_button.name = "BuySiteButton"
    site_buy_button.text = tr("Buy this land")
    site_buy_button.custom_minimum_size = Vector2(200, 56)
    site_buy_button.pressed.connect(_on_buy_site_pressed)
    row.add_child(site_buy_button)
    site_cancel_button = Button.new()
    site_cancel_button.name = "CancelSiteButton"
    site_cancel_button.text = tr("Cancel")
    site_cancel_button.custom_minimum_size = Vector2(120, 56)
    site_cancel_button.pressed.connect(cancel_new_store)
    row.add_child(site_cancel_button)
    $UI.add_child(site_panel)
    site_panel.position = Vector2(town_view.position.x, town_view.position.y + town_view.view_size.y - 130.0)
    site_panel.size = Vector2(town_view.view_size.x, 120.0)


func _needs_store_site() -> bool:
    return (
        simulation.store_site != null
        and (not simulation.has_store_site() or choosing_new_store)
        and not simulation.is_game_over
        and not Engine.has_meta(PROTOTYPE_STORE_FOR_TESTS_META)
    )


# Task #123: 新規出店 -- pick the land on the town map, then the store, as
# for the first store; "やめる" goes back.
func start_new_store() -> void:
    if simulation.store_types().is_empty() or simulation.town_is_full() or simulation.is_game_over:
        return
    choosing_new_store = true
    _sync_site_selection()
    site_info_label.text = tr("Tap the map to pick a 2x2 site for the new store")
    _refresh_ui()


func cancel_new_store() -> void:
    if not choosing_new_store:
        return
    choosing_new_store = false
    _sync_site_selection()
    _refresh_ui()


# Task #123: look at (and run) store `index`: 本店 is 0.
func select_store(index: int) -> void:
    if not simulation.select_store(index):
        return
    _rival_id = ""
    _store_layout_changed()
    town_view.center_on_store()
    if town_view.visible and not selecting_site:
        _on_show_town_map_pressed()
    layout_edit_label.text = tr("Now running %s") % simulation.store_name
    _refresh_ui()


# Enters or leaves site selection to match the simulation (new game, reset,
# load).
func _sync_site_selection() -> void:
    var was_selecting := selecting_site
    selecting_site = _needs_store_site()
    site_panel.visible = selecting_site
    site_cancel_button.visible = choosing_new_store
    store_type_panel.visible = false
    _store_layout_changed()
    town_view.selecting_site = selecting_site
    town_view.show_site_cursor(Vector2i(-1, -1), false)
    _site_origin = Vector2i(-1, -1)
    if selecting_site:
        _set_android_panel_open(false)
        town_view.visible = true
        store_view.visible = false
        show_town_map_button.text = tr("Show store")
        site_info_label.text = tr("Tap the map to pick a 2x2 site")
        site_buy_button.disabled = true
    elif was_selecting:
        # The store now stands on the bought site: show it.
        town_view.visible = false
        store_view.visible = true
        show_town_map_button.text = tr("Show town map")
    town_view.center_on_store()
    SoundManager.play_theme("town" if selecting_site else "store")


func _on_site_tapped(origin: Vector2i) -> void:
    if not selecting_site or store_type_panel.visible:
        return
    _site_origin = origin
    var quote: Dictionary = simulation.store_site_quote(origin)
    town_view.show_site_cursor(origin, bool(quote["buildable"]))
    site_info_label.text = _site_quote_text(quote)
    if not bool(quote["buildable"]):
        SoundManager.play_sfx(str(config["sound"]["refused_sfx"]))
    site_buy_button.disabled = (
        not bool(quote["buildable"]) or simulation.economy.cash_yen < int(quote["total_yen"])
    )


# Task #104: the store just built (or loaded) may be another size than the
# one drawn so far.
func _store_layout_changed() -> void:
    config = simulation.config
    store_view.bind(config, simulation)
    store_view.selected_fixture_id = ""
    _fit_store_view()
    _populate_sample_layout_option()
    _refresh_procure_fixture_option()


# Like the original's land popup 「空地 ¥20,000,000 🚬○🍺○💊○」 (guide p.10),
# with the permit icons written out as words.
func _site_quote_text(quote: Dictionary) -> String:
    if not bool(quote["buildable"]):
        match str(quote["reason"]):
            "too_close_to_store":
                return tr("Too close to another store (no store within 5 squares)")
            _:
                return tr("Cannot build here (roads, railway and the map edge)")
    var marks: Array[String] = []
    for permit_id in ["tobacco", "alcohol", "medicine"]:
        var available: bool = bool((quote["permits_available"] as Dictionary).get(permit_id, false))
        marks.append("%s%s" % [tr("permit_short_" + permit_id), "○" if available else "×"])
    var name := str(quote["label"]) if not str(quote["label"]).is_empty() else tr("Vacant lot")
    var text := "%s ¥%s  %s" % [name, _format_integer(int(quote["total_yen"])), " ".join(marks)]
    if int(quote["building_yen"]) > 0:
        text += "\n" + tr("(land ¥%s + buying the building ¥%s)") % [
            _format_integer(int(quote["land_yen"])),
            _format_integer(int(quote["building_yen"])),
        ]
    return text


func _on_buy_site_pressed() -> void:
    if not selecting_site or _site_origin.x < 0:
        return
    if simulation.store_types().is_empty():
        _build_store(simulation.store_type_id)
        return
    # Task #104: like the original, the store is picked after the land.
    _store_type_choice = ""
    for entry in simulation.store_types():
        if simulation.store_type_is_selectable(str(entry["id"])):
            _store_type_choice = str(entry["id"])
            break
    store_type_panel.visible = true
    _refresh_store_type_panel()


func _build_store(type_id: String) -> void:
    if not simulation.try_buy_store_site(_site_origin, type_id):
        site_info_label.text = tr("Cannot buy this land")
        if store_type_panel.visible:
            store_type_info_label.text = tr("Not enough money to buy the land and build this store")
        SoundManager.play_sfx(str(config["sound"]["refused_sfx"]))
        return
    store_type_panel.visible = false
    layout_edit_label.text = tr("Bought the land and opened the store")
    if choosing_new_store:
        # The new store is the last one; go and run it.
        choosing_new_store = false
        _sync_site_selection()
        select_store(simulation.store_count() - 1)
        paused = false
        pause_button.text = tr("Pause")
        return
    _sync_site_selection()
    paused = false
    pause_button.text = tr("Pause")
    accumulator = 0.0
    _refresh_ui()


# Task #104: 「店舗を選んで下さい」 -- the six stores in 2 rows x 3 columns
# with the ones that cannot be built yet greyed out, and the chosen one's
# price (CONFIRMED_VISUAL layout of the PS screen, see
# guide_store_types.evidence_note). Platform presentation.
func _build_store_type_panel() -> void:
    store_type_panel = PanelContainer.new()
    store_type_panel.name = "StoreTypePanel"
    store_type_panel.theme = ($UI/Panel as Control).theme
    store_type_panel.visible = false
    var box := VBoxContainer.new()
    store_type_panel.add_child(box)
    var title := Label.new()
    title.text = tr("Choose your store")
    title.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
    box.add_child(title)
    var grid := GridContainer.new()
    grid.columns = 3
    box.add_child(grid)
    var cells: Dictionary = {}
    for entry in simulation.store_types():
        var cell: Array = entry["grid_cell"]
        cells[Vector2i(int(cell[0]), int(cell[1]))] = entry
    for row in 2:
        for column in 3:
            var entry: Dictionary = cells.get(Vector2i(column, row), {})
            var button := Button.new()
            button.custom_minimum_size = Vector2(96, 96)
            button.toggle_mode = true
            button.expand_icon = true
            if not entry.is_empty():
                var type_id := str(entry["id"])
                button.name = "StoreType_" + type_id
                button.icon = _menu_icon("store_types", str(entry["icon"]))
                # Task #126: which way the floor runs (縦長/横長) and its size.
                button.text = store_type_caption(entry)
                button.icon_alignment = HORIZONTAL_ALIGNMENT_CENTER
                button.vertical_icon_alignment = VERTICAL_ALIGNMENT_TOP
                button.add_theme_font_size_override("font_size", 14)
                button.custom_minimum_size = Vector2(132, 112)
                button.disabled = not simulation.store_type_is_selectable(type_id)
                if button.disabled:
                    button.modulate = Color(0.4, 0.4, 0.4)
                button.pressed.connect(func():
                    _store_type_choice = type_id
                    _refresh_store_type_panel())
                _store_type_buttons[type_id] = button
            else:
                button.disabled = true
            grid.add_child(button)
    store_type_info_label = Label.new()
    store_type_info_label.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
    store_type_info_label.custom_minimum_size = Vector2(320, 0)
    box.add_child(store_type_info_label)
    var row_box := HBoxContainer.new()
    box.add_child(row_box)
    store_type_build_button = Button.new()
    store_type_build_button.name = "BuildStoreButton"
    store_type_build_button.text = tr("Build this store")
    store_type_build_button.pressed.connect(func(): _build_store(_store_type_choice))
    row_box.add_child(store_type_build_button)
    var back := Button.new()
    back.name = "StoreTypeBackButton"
    back.text = tr("Back")
    back.pressed.connect(func(): store_type_panel.visible = false)
    row_box.add_child(back)
    for button in [store_type_build_button, back]:
        button.custom_minimum_size = Vector2(0, 56)
        button.size_flags_horizontal = Control.SIZE_EXPAND_FILL
    $UI.add_child(store_type_panel)
    var panel_size := store_type_panel.get_combined_minimum_size()
    store_type_panel.size = panel_size
    store_type_panel.position = town_view.position + (town_view.view_size - panel_size) / 2.0


func _refresh_store_type_panel() -> void:
    for type_id in _store_type_buttons:
        (_store_type_buttons[type_id] as Button).set_pressed_no_signal(type_id == _store_type_choice)
    var entry: Dictionary = GuideStartingStoreScript.store_type_entry(config, _store_type_choice)
    if entry.is_empty():
        store_type_info_label.text = ""
        store_type_build_button.disabled = true
        return
    var price := int(entry["construction_price_yen"])
    var land := int(simulation.store_site_quote(_site_origin).get("total_yen", 0))
    store_type_info_label.text = "%s　¥%s\n%s" % [
        store_type_caption(entry),
        _format_integer(price),
        tr("Land ¥%s + store ¥%s = ¥%s") % [
            _format_integer(land), _format_integer(price), _format_integer(land + price),
        ],
    ]
    store_type_build_button.disabled = simulation.economy.cash_yen < land + price


# Task #96: sounds for what just happened -- each event type in
# config["sound"]["event_sfx"] plays its effect (at most once per refresh),
# and reaching the scenario goal plays the fanfare once. REMAKE_BALANCED_DEFAULT
# pairing, see that block's evidence_note.
func _latest_event_sequence() -> int:
    var records: Array = simulation.event_log.records
    return 0 if records.is_empty() else int(records[-1]["sequence"])


func _play_event_sounds() -> void:
    var records: Array = simulation.event_log.records
    var event_sfx: Dictionary = config["sound"]["event_sfx"]
    var newest := _latest_event_sequence()
    if newest < _heard_event_sequence:
        _heard_event_sequence = 0
    var to_play: Array[String] = []
    var index := records.size() - 1
    while index >= 0 and int(records[index]["sequence"]) > _heard_event_sequence:
        var sfx := str(event_sfx.get(str(records[index]["event_type"]), ""))
        if not sfx.is_empty() and not to_play.has(sfx):
            to_play.append(sfx)
        index -= 1
    _heard_event_sequence = newest
    for sfx in to_play:
        SoundManager.play_sfx(sfx)
    if simulation.clear_condition_met and not _heard_clear:
        SoundManager.play_sfx(str(config["sound"]["clear_sfx"]))
    _heard_clear = simulation.clear_condition_met


# Task #102: the monthly customer survey (アンケート: 買った商品 /
# 欲しかった商品, guide p.70 screenshot), under the store information.
var survey_label: Label = null


func _refresh_survey_label() -> void:
    if survey_label == null:
        survey_label = Label.new()
        survey_label.name = "SurveyValue"
        survey_label.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
        var vbox := $UI/Panel/Margin/Scroll/VBox
        vbox.add_child(survey_label)
        vbox.move_child(survey_label, town_label.get_index() + 1)
    var survey: Dictionary = simulation.last_survey
    var title := tr("Survey (last month)")
    if survey.is_empty():
        survey = {"bought": simulation.survey_bought, "missing": simulation.survey_missing}
        title = tr("Survey (this month so far)")
    survey_label.text = "%s\n%s %s\n%s %s" % [
        title,
        tr("Bought:"), _survey_top(survey["bought"]),
        tr("Wanted but not in the store:"), _survey_top(survey["missing"]),
    ]


func _survey_top(counts: Dictionary) -> String:
    var keys: Array = counts.keys()
    keys.sort_custom(func(a, b): return int(counts[a]) > int(counts[b]))
    var parts: Array[String] = []
    for key in keys.slice(0, 5):
        parts.append("%s%d" % [tr(str(key)), int(counts[key])])
    return "、".join(parts) if not parts.is_empty() else tr("none")


# Task #103: 営業時間 (business hours), next to the price policy.
var business_hours_option: OptionButton = null


func _build_business_hours_controls() -> void:
    var presets: Array = simulation.business_hours_presets()
    if presets.is_empty():
        return
    var vbox := $UI/Panel/Margin/Scroll/VBox
    var title := Label.new()
    title.text = tr("Business hours")
    vbox.add_child(title)
    vbox.move_child(title, set_price_policy_button.get_index() + 1)
    business_hours_option = OptionButton.new()
    business_hours_option.name = "BusinessHoursOption"
    for preset in presets:
        business_hours_option.add_item(str(preset["label"]))
    vbox.add_child(business_hours_option)
    vbox.move_child(business_hours_option, title.get_index() + 1)
    _select_current_business_hours()
    business_hours_option.item_selected.connect(func(index: int):
        var preset_id := str(presets[index]["id"])
        if simulation.try_set_business_hours(preset_id):
            layout_edit_label.text = tr("Business hours: %s") % str(presets[index]["label"])
        _refresh_ui()
    )
    if _is_android_preview():
        business_hours_option.custom_minimum_size.y = 64


func _select_current_business_hours() -> void:
    if business_hours_option == null:
        return
    var presets: Array = simulation.business_hours_presets()
    for index in presets.size():
        if str(presets[index]["id"]) == simulation.business_hours_id:
            business_hours_option.select(index)


func _build_sound_toggle() -> void:
    sound_toggle_button = Button.new()
    sound_toggle_button.name = "SoundToggleButton"
    var vbox := $UI/Panel/Margin/Scroll/VBox
    vbox.add_child(sound_toggle_button)
    vbox.move_child(sound_toggle_button, vbox.get_node("MenuButtons").get_index() + 1)
    if _is_android_preview():
        sound_toggle_button.custom_minimum_size.y = 64
    _refresh_sound_toggle()
    sound_toggle_button.pressed.connect(func():
        SoundManager.set_enabled(not SoundManager.enabled)
        _refresh_sound_toggle()
    )


func _refresh_sound_toggle() -> void:
    sound_toggle_button.text = tr("Sound: on") if SoundManager.enabled else tr("Sound: off")


func _build_fixture_info_panel() -> void:
    fixture_info_panel = PanelContainer.new()
    fixture_info_panel.name = "FixtureInfoPanel"
    fixture_info_panel.theme = ($UI/Panel as Control).theme
    fixture_info_panel.visible = false
    var card := VBoxContainer.new()
    fixture_info_panel.add_child(card)
    var top_row := HBoxContainer.new()
    card.add_child(top_row)
    var row := HBoxContainer.new()
    row.alignment = BoxContainer.ALIGNMENT_END
    card.add_child(row)
    fixture_info_icon = TextureRect.new()
    fixture_info_icon.expand_mode = TextureRect.EXPAND_IGNORE_SIZE
    fixture_info_icon.stretch_mode = TextureRect.STRETCH_KEEP_ASPECT_CENTERED
    fixture_info_icon.custom_minimum_size = Vector2(56, 56)
    top_row.add_child(fixture_info_icon)
    fixture_info_label = Label.new()
    fixture_info_label.size_flags_horizontal = Control.SIZE_EXPAND_FILL
    fixture_info_label.vertical_alignment = VERTICAL_ALIGNMENT_CENTER
    fixture_info_label.clip_text = true
    fixture_info_label.text_overrun_behavior = TextServer.OVERRUN_TRIM_ELLIPSIS
    top_row.add_child(fixture_info_label)
    fixture_restock_button = Button.new()
    fixture_restock_button.name = "FixtureRestockButton"
    fixture_restock_button.custom_minimum_size = Vector2(170, 52)
    fixture_restock_button.pressed.connect(_on_restock_pressed)
    row.add_child(fixture_restock_button)
    # Task #110: an empty shelf is stocked from here on the phone.
    fixture_stock_button = Button.new()
    fixture_stock_button.name = "FixtureStockButton"
    fixture_stock_button.text = "商品を並べる"
    fixture_stock_button.custom_minimum_size = Vector2(170, 52)
    fixture_stock_button.visible = false
    fixture_stock_button.pressed.connect(func():
        if phone_ui != null:
            phone_ui.open_stock_window(store_view.selected_fixture()))
    row.add_child(fixture_stock_button)
    var close := Button.new()
    close.name = "FixtureInfoClose"
    close.text = tr("Close")
    close.custom_minimum_size = Vector2(90, 52)
    close.pressed.connect(_on_deselect_fixture_pressed)
    row.add_child(close)
    $UI.add_child(fixture_info_panel)


func _build_rival_panel() -> void:
    rival_panel = PanelContainer.new()
    rival_panel.name = "RivalPanel"
    rival_panel.theme = ($UI/Panel as Control).theme
    rival_panel.visible = false
    var box := VBoxContainer.new()
    rival_panel.add_child(box)
    rival_info_label = Label.new()
    rival_info_label.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
    rival_info_label.custom_minimum_size.x = town_view.view_size.x - 40.0
    box.add_child(rival_info_label)
    var row := HBoxContainer.new()
    box.add_child(row)
    rival_investigate_button = Button.new()
    rival_investigate_button.name = "RivalInvestigateButton"
    rival_investigate_button.pressed.connect(_on_investigate_rival_pressed)
    row.add_child(rival_investigate_button)
    rival_buyout_button = Button.new()
    rival_buyout_button.name = "RivalBuyoutButton"
    rival_buyout_button.pressed.connect(_on_buy_out_rival_pressed)
    row.add_child(rival_buyout_button)
    var leave := Button.new()
    leave.name = "RivalLeaveButton"
    leave.text = tr("Do nothing")
    leave.pressed.connect(func(): _show_rival(""))
    row.add_child(leave)
    for button in [rival_investigate_button, rival_buyout_button, leave]:
        button.custom_minimum_size = Vector2(0, 56)
        button.size_flags_horizontal = Control.SIZE_EXPAND_FILL
    $UI.add_child(rival_panel)
    rival_panel.position = Vector2(town_view.position.x, town_view.position.y + town_view.view_size.y - 150.0)
    rival_panel.size = Vector2(town_view.view_size.x, 140.0)


func _on_map_tapped(tile: Vector2i) -> void:
    if selecting_site:
        return
    # Task #123: tapping one of the player's stores goes into it.
    var store_index: int = simulation.store_at_tile(tile)
    if store_index >= 0:
        select_store(store_index)
        return
    _show_rival(simulation.rival_at(tile))


func _show_rival(rival_id: String) -> void:
    _rival_id = rival_id
    _refresh_rival_panel()


func _refresh_rival_panel() -> void:
    rival_panel.visible = not _rival_id.is_empty() and town_view.visible and not selecting_site
    if not rival_panel.visible:
        return
    var entry: Dictionary = simulation._rival_guide_entry(_rival_id)
    var text := str(entry.get("name", _rival_id))
    if simulation.rival_investigated(_rival_id):
        var data: Dictionary = entry.get("guide_data", {})
        text += "　" + tr("Hours %s, popularity %d, security %d, cleaning %d, service %d") % [
            str(data.get("hours", "")), int(data.get("popularity", 0)), int(data.get("security", 0)),
            int(data.get("cleaning", 0)), int(data.get("service", 0)),
        ]
        # Task #106: what the investigation shows about its losses.
        var losing: int = simulation.rival_deficit_months(_rival_id)
        if losing > 0:
            text += "　" + tr("Losing money for %d months in a row") % losing
    rival_info_label.text = text
    rival_investigate_button.text = tr("Investigate (¥%s)") % _format_integer(simulation.rival_investigation_cost_yen())
    rival_investigate_button.disabled = (
        simulation.rival_investigated(_rival_id)
        or simulation.economy.cash_yen < simulation.rival_investigation_cost_yen()
    )
    if simulation.rival_is_buyable(_rival_id):
        var price: int = simulation.rival_buyout_price_yen(_rival_id)
        rival_buyout_button.text = tr("Buy out (¥%s)") % _format_integer(price)
        rival_buyout_button.disabled = simulation.economy.cash_yen < price
    else:
        rival_buyout_button.text = tr("A main store cannot be bought")
        rival_buyout_button.disabled = true


func _on_investigate_rival_pressed() -> void:
    if simulation.try_investigate_rival(_rival_id):
        layout_edit_label.text = tr("Investigated the rival store")
    _refresh_ui()


func _on_buy_out_rival_pressed() -> void:
    if simulation.try_buy_out_rival(_rival_id):
        layout_edit_label.text = tr("Bought out the rival store: now %d stores") % simulation.player_store_count
        _show_rival("")
        town_view.queue_redraw()
    else:
        SoundManager.play_sfx(str(config["sound"]["refused_sfx"]))
    _refresh_ui()


# Name, product and stock of the selected fixture. The panel sits along
# the bottom of the store, or along the top when the fixture is in the
# lower half, so it never covers what it describes.
func _refresh_fixture_info() -> void:
    var fixture_id: String = store_view.selected_fixture()
    var show: bool = (
        not fixture_id.is_empty()
        and store_view.visible
        and not selecting_site
        and simulation.layout.fixtures_by_id.has(fixture_id)
    )
    fixture_info_panel.visible = show
    if not show:
        return
    var fixture: Dictionary = simulation.layout.fixtures_by_id[fixture_id]
    var product = store_view._product_on_fixture(fixture_id)
    var name_key := str(fixture.get("catalog_id", ""))
    if name_key.is_empty():
        name_key = "fixture_kind_" + str(fixture["kind"])
    fixture_info_icon.texture = _menu_icon("fixtures", str(fixture.get("catalog_id", "")))
    # Task #117: a shelf that already holds something can be given another
    # product from the same button.
    fixture_stock_button.visible = phone_ui != null and str(fixture["kind"]) == "shelf" and not store_view.editing
    fixture_stock_button.text = "商品を並べる" if product == null else "商品を変える"
    if product == null:
        fixture_info_label.text = tr(name_key)
        fixture_restock_button.visible = false
    else:
        fixture_info_icon.texture = _menu_icon("products", product.catalog_id)
        fixture_info_label.text = tr("%s: %s, stock %d / %d") % [
            tr(name_key), _product_label(product.product_id), product.stock_units, product.initial_stock_units,
        ]
        var missing: int = product.initial_stock_units - product.stock_units
        fixture_restock_button.visible = true
        fixture_restock_button.disabled = missing <= 0
        fixture_restock_button.text = tr("Restock (¥%s)") % _format_integer(missing * product.restock_unit_cost_yen) if missing > 0 else tr("Full")
    var store_size: Vector2 = Vector2(
        simulation.layout.width_subcells, simulation.layout.height_subcells
    ) * store_view.SUBCELL_PIXELS * store_view.scale
    var height: float = maxf(72.0, fixture_info_panel.get_combined_minimum_size().y)
    var origin_y := float(_vec2i_of(fixture["origin_subcell"]).y) / float(simulation.layout.height_subcells)
    var y: float = store_view.position.y + store_size.y - height if origin_y < 0.5 else store_view.position.y
    if phone_ui != null:
        # Task #110: a card over the store, wide enough for its buttons.
        var width: float = maxf(store_size.x, 560.0)
        fixture_info_panel.position = Vector2(
            clampf(store_view.position.x + (store_size.x - width) / 2.0, 8.0, 1020.0 - width - 8.0), y
        )
        fixture_info_panel.size = Vector2(width, height)
        return
    fixture_info_panel.position = Vector2(store_view.position.x, y)
    fixture_info_panel.size = Vector2(store_size.x, height)


func _vec2i_of(value: Array) -> Vector2i:
    return Vector2i(int(value[0]), int(value[1]))


# Task #92: player-facing names for internal ids, so no message shows a raw
# id such as "shelf-bread-1" or "customer-12".
func _fixture_label(fixture_id: String) -> String:
    if not simulation.layout.fixtures_by_id.has(fixture_id):
        return fixture_id
    var fixture: Dictionary = simulation.layout.fixtures_by_id[fixture_id]
    var name_key := str(fixture.get("catalog_id", ""))
    if name_key.is_empty():
        name_key = "fixture_kind_" + str(fixture["kind"])
    var label := tr(name_key)
    for product_id in simulation.inventory.product_order:
        var product = simulation.inventory.get_product(product_id)
        if product.fixture_id == fixture_id:
            return tr("%s (%s)") % [label, _product_label(product_id)]
    return label


func _product_label(product_id: String) -> String:
    var product = simulation.inventory.get_product(product_id)
    if product == null:
        return product_id
    var catalog_id := str(product.catalog_id)
    return tr(catalog_id) if not catalog_id.is_empty() else tr(product_id)


func _customer_label(customer_id: String) -> String:
    return tr("Customer %s") % customer_id.get_slice("-", customer_id.get_slice_count("-") - 1)


func _candidate_label(candidate_id: String) -> String:
    for entry in config["staff_candidates"]:
        if str(entry["candidate_id"]) == candidate_id:
            return str(entry["display_name"])
    return candidate_id


func _is_android_preview() -> bool:
    return OS.has_feature("android") or "--android-preview" in OS.get_cmdline_user_args()


func _prepare_android_ui() -> void:
    if not _is_android_preview():
        return
    # Task #110: the phone screen is phone_ui.gd, built in _ready(); the
    # desktop side panel stays in the scene (its controls are what the
    # phone windows call into) but is never shown on a phone.
    ($UI/Panel as Control).visible = false


# Task #94: the phone panel is parked off-screen rather than hidden, so its
# layout (and the shortcut scroll targets) stay valid while closed.
func _set_android_panel_open(open: bool) -> void:
    if _android_panel == null:
        return
    _android_panel.offset_left = 540.0 if open else 1300.0
    _android_panel.offset_right = _android_panel.offset_left + 540.0
