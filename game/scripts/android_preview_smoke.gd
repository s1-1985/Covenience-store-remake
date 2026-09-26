extends SceneTree

func _initialize() -> void:
    call_deferred("_run")

func _require(condition: bool, message: String) -> bool:
    if not condition:
        push_error(message)
        quit(1)
    return condition

func _capture(name: String) -> void:
    if DisplayServer.get_name() == "headless":
        return
    await RenderingServer.frame_post_draw
    root.get_texture().get_image().save_png("user://" + name + ".png")

func _run() -> void:
    TranslationServer.set_locale("ja")
    if not _require(TranslationServer.translate("New Game") == "はじめから", "Japanese catalog must load"):
        return
    var config = JSON.parse_string(FileAccess.get_file_as_string("res://data/vertical_slice.json"))
    if not _require("REMAKE_BALANCED_DEFAULT" in config["android_preview"]["evidence_note"], "Preview setup must disclose its limits"):
        return
    change_scene_to_file("res://scenes/main_menu.tscn")
    await process_frame
    await process_frame
    await _capture("preview-title")
    current_scene.new_game_button.pressed.emit()
    await process_frame
    await process_frame
    var game = current_scene
    game.paused = true
    if not _require(game.simulation != null, "New Game must initialize the real game"):
        return
    if not _require(game.simulation.economy.cash_yen == 200000000, "Preview must use the researched cash anchor instead of the test budget"):
        return
    if not _require(game.calendar_label.text == "01年目01月01日", "Japanese calendar must preserve year/month/day"):
        return
    # Task #95: a new game opens on the town map to pick the store's site;
    # time does not run until a site is bought.
    if not _require(game.selecting_site and game.site_panel.visible, "A new game must start by choosing a site"):
        return
    if not _require(game.get_node("/root/SoundManager").current_theme == "town", "The town tune plays while choosing the site"):
        return
    if not _require(game.town_view.visible and not game.store_view.visible, "Site choice happens on the town map"):
        return
    var start_minute: int = game.simulation.minute_of_day
    game.paused = false
    game._process(5.0)
    game.paused = true
    if not _require(game.simulation.minute_of_day == start_minute, "Time must not run before the store has a site"):
        return
    if not _require(game.site_buy_button.disabled, "Nothing to buy before a site is tapped"):
        return
    # A real tap on the road square (11, 20) through the viewport's input.
    var town: Node2D = game.town_view
    var road_point: Vector2 = town.get_global_transform_with_canvas() * ((Vector2(Vector2i(11, 20) - town.view_origin_tile) + Vector2(0.5, 0.5)) * town.map_tile_pixels)
    for pressed in [true, false]:
        var tap := InputEventMouseButton.new()
        tap.button_index = MOUSE_BUTTON_LEFT
        tap.pressed = pressed
        tap.position = road_point
        tap.global_position = road_point
        game.get_viewport().push_input(tap, true)
    if not _require(game._site_origin == Vector2i(11, 20), "Tapping the map must pick the square under the finger"):
        return
    if not _require(game.site_buy_button.disabled and "建てられません" in game.site_info_label.text, "A road is not a building site"):
        return
    game._on_site_tapped(Vector2i(13, 21))
    if not _require(game.site_info_label.text.begins_with("空地 ¥21,000,000"), "A vacant site shows 空地 and its price: " + game.site_info_label.text):
        return
    if not _require("たばこ○" in game.site_info_label.text, "The site shows which permits are available"):
        return
    await _capture("preview-site")
    game.site_buy_button.pressed.emit()
    # Task #104: then 「店舗を選んで下さい」 -- six stores, the two small
    # ones pickable, the chosen one's price shown.
    if not _require(game.store_type_panel.visible and game.selecting_site, "Buying the land asks which store to build"):
        return
    var locked := 0
    for type_id in game._store_type_buttons:
        if (game._store_type_buttons[type_id] as Button).disabled:
            locked += 1
    if not _require(game._store_type_buttons.size() == 6 and locked == 4, "Six stores, four of them locked at the start"):
        return
    if not _require(game._store_type_choice == "small_top" and "小型店（5×8）　¥6,000,000" in game.store_type_info_label.text, "The small store and its price are shown: " + game.store_type_info_label.text):
        return
    await _capture("preview-store-type")
    game.find_child("BuildStoreButton", true, false).pressed.emit()
    game.paused = true
    if not _require(not game.selecting_site and game.store_view.visible and not game.store_type_panel.visible, "Building the store opens it"):
        return
    if not _require(game.simulation.economy.cash_yen == 200000000 - 21000000 - 6000000, "The land and the store are paid from the starting cash"):
        return
    if not _require(game.simulation.layout.width_subcells == 10 and game.simulation.inventory.product_order.size() == 14, "The furnished 5x8 small store stands on the site"):
        return
    if not _require(game.simulation._rival_stores.size() == 2 and "競合2店" in game.town_label.text, "The rival 本店 and 2号店 are in town: " + game.town_label.text):
        return
    # Task #101: tapping the rival 2号店 on the town map offers 調査/買収/何もしない.
    game.show_town_map_button.pressed.emit()
    game._on_map_tapped(Vector2i(28, 10))
    if not _require(game.rival_panel.visible and "買収する（¥46,721,490）" == game.rival_buyout_button.text, "The rival menu offers the buyout: " + game.rival_buyout_button.text):
        return
    game.rival_buyout_button.pressed.emit()
    if not _require(game.simulation.player_store_count == 2 and "競合1店" in game.town_label.text and not game.rival_panel.visible, "Buying out the 2号店 makes it the player's: " + game.town_label.text):
        return
    game._on_map_tapped(Vector2i(9, 11))
    if not _require(game.rival_buyout_button.disabled and "本店は買収できません" == game.rival_buyout_button.text, "The 本店 cannot be bought"):
        return
    game.find_child("RivalLeaveButton", true, false).pressed.emit()
    game.show_town_map_button.pressed.emit()
    if not _require(ThemeDB.fallback_font.has_char(0x5E97), "Japanese glyphs must be available"):
        return
    for tick in range(1500):
        if game.simulation.customers.all_settled():
            game.simulation.tick_idle_for_demand()
        else:
            game.simulation.step()
        if game.simulation.snapshot()["completed_sales"] > 0:
            break
    game._refresh_ui()
    if not _require(game.simulation.snapshot()["completed_sales"] > 0, "A customer must walk, queue, and purchase"):
        return
    # Task #96: what happened is heard -- the door chime, the register.
    game.simulation.start_next_customer()
    game._refresh_ui()
    var heard: Array = game.get_node("/root/SoundManager").sfx_history
    if not _require(heard.has("door_chime") and heard.has("register") and heard.has("purchase"), "Entering, paying and buying land must make sounds: %s" % [heard]):
        return
    if not _require(game.get_node("/root/SoundManager").current_theme == "store", "The shop tune plays once the store is open"):
        return
    # Task #103: business hours can be changed from the panel.
    if not _require(game.business_hours_option != null and game.business_hours_option.get_item_text(game.business_hours_option.selected) == "AM7:00〜PM11:00", "The store opens AM7:00~PM11:00"):
        return
    # Task #102: the survey is shown with the store information.
    if not _require(game.survey_label != null and "アンケート" in game.survey_label.text and "欲しかった商品：" in game.survey_label.text, "The customer survey must be shown"):
        return
    # Task #97: tapping a shelf shows what it holds, and it can be
    # refilled right there while customers are in the store.
    var shelf = game.simulation.inventory.get_product("product-bread-1")
    shelf.stock_units = shelf.initial_stock_units - 4
    game.store_view.selected_fixture_id = shelf.fixture_id
    game._refresh_ui()
    var stock_text := "在庫 %d／%d" % [shelf.stock_units, shelf.initial_stock_units]
    if not _require(game.fixture_info_panel.visible and stock_text in game.fixture_info_label.text, "A selected shelf must show its product and stock: " + game.fixture_info_label.text):
        return
    if not _require(not game.fixture_restock_button.disabled, "A shelf that is not full can be refilled"):
        return
    var cash_before_refill: int = game.simulation.economy.cash_yen
    game.fixture_restock_button.pressed.emit()
    if not _require(shelf.stock_units == shelf.initial_stock_units and game.simulation.economy.cash_yen == cash_before_refill - 4 * shelf.restock_unit_cost_yen, "Refilling fills the shelf and pays for the missing units"):
        return
    game.fixture_info_panel.find_child("FixtureInfoClose", true, false).pressed.emit()
    if not _require(not game.fixture_info_panel.visible, "閉じる hides the fixture info"):
        return
    var sound_manager = game.get_node("/root/SoundManager")
    var sound_was_on: bool = sound_manager.enabled
    game.sound_toggle_button.pressed.emit()
    if not _require(sound_manager.enabled != sound_was_on and game.sound_toggle_button.text.begins_with("音："), "The sound button must switch sound on and off"):
        return
    game.sound_toggle_button.pressed.emit()
    await _capture("preview-store")
    # Task #110: the phone screen -- the store at full size, the original's
    # commands as a column on the right, each opening a window over the
    # play area (the old drawer panel is never shown).
    if not _require(is_equal_approx(game.store_view.scale.x, 1.0), "The phone store must be drawn at full size"):
        return
    var phone = game.phone_ui
    if not _require(phone != null and not game.get_node("UI/Panel").visible, "The phone uses its own screen, not the desktop panel"):
        return
    for command in ["interior", "staff", "policy", "promotion", "research", "system"]:
        phone.menu_buttons[command].pressed.emit()
        if not _require(phone.window.visible and phone.window_id == command, "The %s command must open its window" % command):
            return
        var window_rect: Rect2 = phone.window.get_global_rect()
        if not _require(window_rect.end.x <= phone.MENU_LEFT and window_rect.end.y <= 720.0, "The %s window must stay beside the command column: %s" % [command, window_rect]):
            return
        if not _require(game.store_view.editing == (command == "interior"), "Only the 内装 window edits the layout"):
            return
    phone.window.find_child("PhoneWindowClose", true, false).pressed.emit()
    if not _require(not phone.window.visible and not game.store_view.editing, "× closes the window"):
        return
    # A tap on the floor outside 内装 only deselects; it never moves anything.
    var bread_shelf: String = game.simulation.inventory.get_product("product-bread-1").fixture_id
    var bread_origin: Vector2i = game.simulation.layout.fixture_origin(bread_shelf)
    game.store_view.selected_fixture_id = bread_shelf
    var floor_cell := Vector2i(4, 10)
    var floor_point: Vector2 = game.store_view.get_global_transform_with_canvas() * ((Vector2(floor_cell) + Vector2(0.5, 0.5)) * game.store_view.SUBCELL_PIXELS)
    for pressed in [true, false]:
        var floor_tap := InputEventMouseButton.new()
        floor_tap.button_index = MOUSE_BUTTON_LEFT
        floor_tap.pressed = pressed
        floor_tap.position = floor_point
        floor_tap.global_position = floor_point
        game.get_viewport().push_input(floor_tap, true)
    if not _require(game.simulation.layout.is_walkable(floor_cell) and game.simulation.layout.fixture_origin(bread_shelf) == bread_origin and game.store_view.selected_fixture().is_empty(), "Outside 内装 a tap on the floor deselects and moves nothing"):
        return
    game.store_view.selected_fixture_id = ""
    # Pause and speed from the top band.
    var was_paused: bool = game.paused
    phone.pause_button.pressed.emit()
    if not _require(game.paused != was_paused, "The top band's pause button pauses and resumes"):
        return
    phone.pause_button.pressed.emit()
    phone.speed_button.pressed.emit()
    if not _require(game.speed == 2 and phone.speed_button.text == "×2", "The speed button speeds the game up"):
        return
    phone.speed_button.pressed.emit()
    phone.speed_button.pressed.emit()
    if not _require(game.speed == 1, "The speed button cycles back to ×1"):
        return
    game.paused = true
    # 営業方針: the price is changed with big buttons, not a spin box.
    phone.menu_buttons["policy"].pressed.emit()
    var cheaper: Button = null
    for node in phone.window_body.find_children("*", "Button", true, false):
        if (node as Button).text == "－5%":
            cheaper = node
    cheaper.pressed.emit()
    if not _require(game.simulation.price_change_pct == -5, "－5% lowers the prices"):
        return
    game.simulation.try_set_price_policy(0)
    await _capture("preview-policy")
    # A new, empty shelf bought and set down with customers inside, then
    # stocked from its card with a picture of the product.
    var free_origin := Vector2i(-1, -1)
    for y in range(0, game.simulation.layout.height_subcells, 2):
        for x in range(0, game.simulation.layout.width_subcells, 2):
            if free_origin.x < 0 and game.simulation.try_purchase_fixture("small_ambient_shelf", "shelf-new-1", Vector2i(x, y), game._find_open_interaction_cell(Vector2i(x, y), 2, 2)):
                free_origin = Vector2i(x, y)
    if not _require(free_origin.x >= 0, "A shelf can be bought and placed in the running store"):
        return
    game.store_view.selected_fixture_id = "shelf-new-1"
    game._refresh_ui()
    if not _require(game.fixture_stock_button.visible, "An empty shelf offers 商品を並べる"):
        return
    game.fixture_stock_button.pressed.emit()
    if not _require(phone.window.visible and phone.window_id == "stock", "商品を並べる opens the product pictures"):
        return
    var picture: Button = null
    for node in phone.window_body.find_children("*", "Button", true, false):
        if picture == null and not (node as Button).disabled:
            picture = node
    picture.pressed.emit()
    var stocked := false
    for stocked_product in game.simulation.inventory.products.values():
        if stocked_product.fixture_id == "shelf-new-1":
            stocked = true
    if not _require(stocked and not phone.window.visible, "Tapping a product picture stocks the shelf"):
        return
    game.store_view.selected_fixture_id = ""
    game._refresh_ui()
    await _capture("preview-economy")
    # A real tap on a customer shows what they are buying; one waiting at
    # the register can be thrown out (つまみだす).
    var queued = null
    for tick in 3000:
        game.simulation.tick()
        for customer in game.simulation.customers.active_customers():
            if customer.phase == "waiting_checkout":
                queued = customer
        if queued != null:
            break
    if not _require(queued != null, "Someone must end up waiting at the register"):
        return
    var customer_point: Vector2 = game.store_view.get_global_transform_with_canvas() * ((Vector2(queued.position) + Vector2(0.5, 0.2)) * game.store_view.SUBCELL_PIXELS)
    for pressed in [true, false]:
        var customer_tap := InputEventMouseButton.new()
        customer_tap.button_index = MOUSE_BUTTON_LEFT
        customer_tap.pressed = pressed
        customer_tap.position = customer_point
        customer_tap.global_position = customer_point
        game.get_viewport().push_input(customer_tap, true)
    if not _require(phone.customer_card.visible and "かご" in phone.customer_card_label.text and not phone.customer_eject_button.disabled, "Tapping a queued customer shows their basket and つまみだす: " + phone.customer_card_label.text):
        return
    var tapped_id: String = phone.customer_id
    phone.customer_eject_button.pressed.emit()
    if not _require(game.simulation.customers.customer(tapped_id).phase == "leaving" and not phone.customer_card.visible, "つまみだす sends the customer out"):
        return
    # システム → セーブ.
    phone.menu_buttons["system"].pressed.emit()
    for node in phone.window_body.find_children("*", "Button", true, false):
        if (node as Button).text == "セーブ":
            (node as Button).pressed.emit()
            break
    if not _require(game.layout_edit_label.text == "セーブ完了", "Saving from システム must succeed"):
        return
    phone.close_window()
    var saved_cash: int = game.simulation.economy.cash_yen
    game.simulation.economy.cash_yen = 123
    game.load_button.pressed.emit()
    game.paused = true
    if not _require(game.simulation.economy.cash_yen == saved_cash, "Load must restore money"):
        return
    if not _require(game.simulation.store_site_origin == Vector2i(13, 21) and not game.selecting_site, "Load must restore the store's site"):
        return
    game.show_town_map_button.pressed.emit()
    if not _require(game.town_view.visible and not game.store_view.visible, "Town/store switch must work"):
        return
    game.quit_to_menu_button.pressed.emit()
    await process_frame
    await process_frame
    if not _require(not current_scene.continue_button.disabled, "Continue must detect the save"):
        return
    current_scene.continue_button.pressed.emit()
    await process_frame
    await process_frame
    current_scene.paused = true
    if not _require(current_scene.simulation.economy.cash_yen == saved_cash, "Title Continue must restore money"):
        return
    if not _require(not current_scene.selecting_site, "Continue must not ask for a site again"):
        return
    print("Android preview flow passed: Japanese, funded start, site choice, sale, shortcuts, save/load, town, title, continue.")
    quit(0)
