extends SceneTree
func _initialize() -> void:
    call_deferred("run")
func run() -> void:
    change_scene_to_file("res://scenes/main.tscn")
    await process_frame
    await process_frame
    var game = current_scene
    game.paused = true
    assert(game.simulation.try_buy_store_site(Vector2i(26,12)))
    game.selecting_site = false
    game.site_panel.hide()
    game.store_type_panel.hide()
    game.store_view.show()
    game.town_view.hide()
    var ui = game.phone_ui
    assert(ui.get_script().resource_path.ends_with("ps1_ui.gd"))
    ui.layout_screen()
    ui.open_window("interior")
    ui._navigate("floor_material")
    await process_frame
    await process_frame
    assert(ui.screen == "floor_material")
    assert(ui.window_id == "interior")
    assert(ui.hits.size() == 3, "Only the three clean materials may be selected")
    ui.hits[2]["action"].call()
    assert(ui.screen == "interior")
    for row in game.simulation.config["store"]["source_floor"]:
        for cell in row:
            if int(cell) >= 0 and int(cell) < 15: assert(int(cell) == 10)
    print("FLOOR_UI_PASS 3 clean icons; tap applies material10; return to interior")
    quit(0)
