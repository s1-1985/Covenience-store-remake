extends SceneTree
var ui
var game
func _initialize() -> void:
    call_deferred("_run")
func check(ok: bool, message: String) -> void:
    if not ok:
        push_error(message)
        quit(1)
func _tap(native: Vector2) -> void:
    if ui.notice.visible: ui._finish_notice()
    var event := InputEventMouseButton.new()
    event.button_index = MOUSE_BUTTON_LEFT
    event.pressed = true
    event.position = Vector2(160,0)+native*3
    ui._input(event)
    await process_frame
func _capture(id: String) -> void:
    if DisplayServer.get_name() != "headless":
        await RenderingServer.frame_post_draw
        var directory := OS.get_environment("CONVENI_CAPTURE_DIR")
        if directory.is_empty(): directory = "user://"
        root.get_texture().get_image().save_png(directory.path_join("ps-ui-"+id+".png"))
func _run() -> void:
    change_scene_to_file("res://scenes/main.tscn")
    await process_frame
    await process_frame
    game = current_scene
    game.paused = true
    ui = game.phone_ui
    check(ui != null,"Android UI missing")
    game._on_site_tapped(Vector2i(26,12))
    await process_frame
    await process_frame
    await _capture("site")
    await _tap(Vector2(115,160))
    check(game.store_type_panel.visible,"Location confirmation must open store variants")
    await process_frame
    await _capture("site_types")
    await _tap(Vector2(109,106))
    check(game.simulation.has_store_site(),"Native picker must purchase the real site")
    game.paused = true
    game._sync_site_selection()
    game.selecting_site = false
    game.site_panel.hide()
    game.store_type_panel.hide()
    game.store_view.show()
    game.town_view.hide()
    game._refresh_ui()
    ui.layout_screen()
    game.simulation.minute_of_day = 12*60 # daytime visual fixture
    # Every referenced state must draw with actual data, not canned figures.
    for id in ["root","realestate","promotion","research","store","interior","fixtures","policy","hours","prices","stock_prices","permits","advertising","facilities","staff","candidates","dismiss","transfer","renovation","shop","shop_graph","results","survey","system","close_shop"]:
        var town_screen: bool = id in ["root","realestate","promotion","research","advertising","facilities","shop","shop_graph","results","survey","system"]
        game.town_view.visible = town_screen
        game.store_view.visible = not town_screen
        ui.layout_screen()
        ui.open_window(id)
        await process_frame
        await process_frame
        await _capture(id)
        check(ui.screen == id,"Screen failed: "+id)
    ui.open_window("system")
    await process_frame
    var audio = root.get_node("SoundManager")
    var bits: int = audio.source_settings_bits
    await _tap(Vector2(205,113))
    check((audio.source_settings_bits&1)==0,"SE OFF hotspot failed")
    await _tap(Vector2(181,113))
    check((audio.source_settings_bits&1)==1,"SE ON hotspot failed")
    audio.set_source_settings(bits)
    ui.close_window()
    ui.open_window("interior")
    await process_frame
    await _tap(Vector2(230,87))
    check(ui.floor_mode=="move" and game.store_view.editing,"Move mode must release map touch")
    ui.handle_cancel()
    check(ui.floor_mode.is_empty() and ui.screen=="interior","Cancel must return to interior menu")
    ui.handle_start()
    check(ui.window_id.is_empty() and not game.store_view.editing,"Start must leave editing")
    print("PS1_UI_PASS location/store purchase + 25 screens, system taps, map editing, cancel/start")
    ui.hits.clear()
    ui._active_action = Callable()
    game.free()
    game = null
    ui = null
    await process_frame
    quit()
