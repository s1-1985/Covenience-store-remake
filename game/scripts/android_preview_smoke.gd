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
    # Task #94: the store is drawn at full size and the panel is a closed
    # drawer until a shortcut opens it.
    if not _require(is_equal_approx(game.store_view.scale.x, 1.0), "The phone store must be drawn at full size"):
        return
    var drawer: Control = game.get_node("UI/Panel")
    if not _require(drawer.offset_left >= 1280.0, "The phone panel must start closed"):
        return
    game.get_node("UI/AndroidShortcuts").get_child(2).pressed.emit()
    await process_frame
    await process_frame
    if not _require(game.get_node("UI/Panel/Margin/Scroll").scroll_vertical > 0, "Economy shortcut must navigate"):
        return
    if not _require(drawer.offset_left < 1280.0, "A shortcut must open the panel"):
        return
    game.get_node("UI/AndroidShortcuts/ClosePanel").pressed.emit()
    if not _require(drawer.offset_left >= 1280.0, "閉じる must close the panel"):
        return
    await _capture("preview-economy")
    game.get_node("UI/AndroidShortcuts").get_child(4).pressed.emit()
    if not _require(game.layout_edit_label.text == "セーブ完了", "Quick save must succeed"):
        return
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
