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
    game.paused = true
    if not _require(not game.selecting_site and game.store_view.visible, "Buying the land opens the store"):
        return
    if not _require(game.simulation.economy.cash_yen == 200000000 - 21000000, "The land is paid from the starting cash"):
        return
    if not _require(ThemeDB.fallback_font.has_char(0x5E97), "Japanese glyphs must be available"):
        return
    for tick in range(500):
        if game.simulation.customers.all_settled():
            game.simulation.tick_idle_for_demand()
        else:
            game.simulation.step()
        if game.simulation.snapshot()["completed_sales"] > 0:
            break
    game._refresh_ui()
    if not _require(game.simulation.snapshot()["completed_sales"] > 0, "A customer must walk, queue, and purchase"):
        return
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
