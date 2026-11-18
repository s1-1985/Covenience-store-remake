extends SceneTree
func _initialize() -> void:
    call_deferred("_run")
func _capture(name: String) -> void:
    if DisplayServer.get_name() != "headless":
        await RenderingServer.frame_post_draw
        var directory := OS.get_environment("CONVENI_CAPTURE_DIR")
        if directory.is_empty():
            directory = "user://"
        root.get_texture().get_image().save_png(directory.path_join(name + ".png"))
func _run() -> void:
    change_scene_to_file("res://scenes/main_menu.tscn")
    await process_frame
    await process_frame
    current_scene.new_game_button.pressed.emit()
    await process_frame
    await process_frame
    var game = current_scene
    game.set_process(false)
    var ui = game.phone_ui
    assert(ui != null)
    assert(is_equal_approx(ui.hud.offset_left, 160.0))
    assert(is_equal_approx(ui.hud.offset_right - ui.hud.offset_left, 960.0))
    assert(not ui.menu.visible)
    assert(ui.touch_controls.get_children().filter(func(n): return n is Button).size() == 11)
    game._on_site_tapped(Vector2i(26,12))
    ui.touch_controls._accept()
    await process_frame
    game.find_child("BuildStoreButton", true, false).pressed.emit()
    await process_frame
    ui.notice.hide()
    game.paused = true
    ui.close_window()
    game._refresh_ui()
    assert(not game.selecting_site)
    ui.command_open = true
    ui.refresh()
    assert(ui.menu.visible)
    ui.open_window("policy")
    assert(ui.window.visible and not ui.menu.visible)
    ui.touch_controls._cancel()
    assert(not ui.window.visible)
    game.town_view.touch_zoom(1.5)
    assert(is_equal_approx(game.town_view.map_tile_pixels, 18.0))
    game.town_view.touch_zoom(100.0)
    assert(is_equal_approx(game.town_view.map_tile_pixels, 48.0))
    game.town_view.touch_zoom(0.001)
    assert(is_equal_approx(game.town_view.map_tile_pixels, 8.0))
    ui.touch_controls.speed_label.pressed.emit()
    assert(game.speed == 2)
    ui.touch_controls.speed_label.pressed.emit()
    assert(game.speed == 4)
    ui.touch_controls.speed_label.pressed.emit()
    assert(game.speed == 8)
    ui.touch_controls.speed_label.pressed.emit()
    assert(game.speed == 1)
    # Supply one second of elapsed monotonic time with a tiny render delta.
    game.paused = false
    game._app_suspended = false
    game._clock_last_us = Time.get_ticks_usec() - 1000000
    game.accumulator = 0.0
    var prior: int = game.store_view.tick_serial
    game._process(0.001)
    var steps: int = game.store_view.tick_serial - prior
    assert(steps >= 1)
    assert(absf(game.accumulator + steps * game.tick_seconds - 1.0) < 0.02)
    game.paused = true
    var debt: float = game.accumulator
    game._process(0.001)
    assert(game._clock_last_us == 0 and is_equal_approx(debt, game.accumulator))
    await _capture("touch-store")
    game._on_show_town_map_pressed()
    ui.layout_screen()
    game.town_view.map_tile_pixels = 10.0
    game.town_view.view_origin_tile = Vector2i.ZERO
    ui.layout_screen()
    game.town_view.queue_redraw()
    await _capture("touch-town")
    ui.open_window("stores")
    await _capture("touch-menu")
    print("TOUCH_UI_PASS 4:3, direct site confirm, command/cancel, zoom bounds, 1/2/4/8 speed, monotonic debt conservation and pause")
    quit()
