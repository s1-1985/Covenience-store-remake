extends SceneTree
var game

func _initialize() -> void:
    call_deferred("run")

func check(ok: bool, message: String) -> bool:
    if not ok:
        push_error(message)
        quit(1)
    return ok

func run() -> void:
    change_scene_to_file("res://scenes/main.tscn")
    await process_frame
    await process_frame
    game = current_scene
    game.paused = true
    game.set_process(false)
    var s = game.simulation
    s.economy.cash_yen = 1000000000
    if not check(s.try_buy_store_site(Vector2i(26,12)), "First store setup failed"): return
    game._sync_site_selection()
    game.selecting_site = false
    var ui = game.phone_ui
    if ui.notice.visible: ui._finish_notice()
    ui.close_window()
    ui.layout_screen()
    var camera = ui.store_camera
    camera.zoom_at(3.0,camera.AREA.get_center())
    game.store_view.global_position += Vector2(70,40)
    camera._clamp()
    var scale_before: Vector2 = game.store_view.scale
    var position_before: Vector2 = game.store_view.global_position
    # Real hourly floor wear updates source_floor_clock even without a stain.
    s.minute_of_day = 60
    s._step_source_floor_wear()
    ui.layout_screen()
    if not check(game.store_view.scale.is_equal_approx(scale_before) and game.store_view.global_position.is_equal_approx(position_before), "Hourly floor update reset the player's zoom/pan"): return
    # Changing floor material/cleaning values must not replace store identity.
    s.config.store.source_floor[0][0] = int(s.config.store.source_floor[0][0]) ^ 1
    s.config.store.source_previous_cleanliness = 50
    for redraw in 3: ui.layout_screen()
    if not check(game.store_view.scale.is_equal_approx(scale_before) and game.store_view.global_position.is_equal_approx(position_before), "Floor changes reset the player's camera"): return
    # Layout refresh during a held gesture must keep both tracked fingers.
    var touch := InputEventScreenTouch.new()
    touch.pressed = true
    touch.position = camera.AREA.get_center()
    touch.index = 0
    camera._input(touch)
    s.config.store.source_floor_clock = 120
    ui.layout_screen()
    if not check(camera._points.has(0), "Layout refresh discarded an active finger"): return
    touch.pressed = false
    touch.canceled = true
    camera._input(touch)
    if not check(camera._points.is_empty(), "Canceled touch must clear tracking"): return
    # Another store must start fitted/centered rather than inheriting its view.
    if not check(s.try_buy_store_site(Vector2i(3,3),"small_top"), "Second store setup failed"): return
    game.select_store(1)
    ui.layout_screen()
    var rect: Rect2 = camera.content_rect()
    var center: Vector2 = game.store_view.global_position + rect.get_center()*game.store_view.scale
    if not check(center.distance_to(camera.AREA.get_center()) < 1, "New selected store must center"): return
    var identity: String = camera._identity
    # A real geometry change still resets view; dirt/counters do not.
    game.config.store.width_tiles = int(game.config.store.width_tiles)+1
    ui.layout_screen()
    if not check(camera._identity != identity, "Changed store geometry was not detected"): return
    rect = camera.content_rect()
    center = game.store_view.global_position + rect.get_center()*game.store_view.scale
    if not check(center.distance_to(camera.AREA.get_center()) < 1, "Changed store geometry must refit"): return
    game.free()
    await process_frame
    print("STORE_CAMERA_PERSISTENCE_PASS hourly wear/floor changes preserve zoom/pan/held fingers; store selection and geometry refit")
    quit()
