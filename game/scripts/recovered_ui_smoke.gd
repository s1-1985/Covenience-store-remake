extends SceneTree
func _initialize() -> void:
    call_deferred("_run")
func _capture(name: String) -> void:
    if DisplayServer.get_name() == "headless":
        return
    await RenderingServer.frame_post_draw
    root.get_texture().get_image().save_png("user://" + name + ".png")
func _run() -> void:
    TranslationServer.set_locale("ja")
    change_scene_to_file("res://scenes/main_menu.tscn")
    await process_frame
    await process_frame
    current_scene.new_game_button.pressed.emit()
    await process_frame
    await process_frame
    var game = current_scene
    game.paused = true
    assert(game.simulation.program_town != null)
    assert(game.simulation._rival_stores.size() == 1)
    await _capture("recovered-town")
    game._on_site_tapped(Vector2i(26,12))
    game.site_buy_button.pressed.emit()
    var choices = game.find_child("SourceLayoutChoice", true, false)
    assert(choices != null and choices.item_count == 4)
    choices.select(1)
    choices.item_selected.emit(1)
    game.find_child("BuildStoreButton",true,false).pressed.emit()
    assert(game.store_view.visible and game.simulation.has_store_site())
    assert(int(game.simulation.config["store"]["source_layout_index"]) == 2)
    for i in 500:
        game.simulation.tick()
    game._refresh_ui()
    await process_frame
    await _capture("recovered-store")
    game.show_town_map_button.pressed.emit()
    game.town_view.center_on_store()
    game._refresh_ui()
    await process_frame
    await _capture("recovered-town-open")
    print("Recovered real UI smoke passed")
    quit()
