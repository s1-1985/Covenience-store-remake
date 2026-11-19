extends SceneTree
var game
var ui
func _initialize() -> void:
    call_deferred("_run")
func tap(at: Vector2) -> void:
    for down in [true, false]:
        var event := InputEventScreenTouch.new()
        event.position = at
        event.pressed = down
        event.index = 0
        root.push_input(event, true)
        await process_frame
func _run() -> void:
    change_scene_to_file("res://scenes/main.tscn")
    await process_frame
    await process_frame
    game = current_scene
    ui = game.phone_ui
    game.paused = true
    assert(game.simulation.try_buy_store_site(Vector2i(26,12)))
    game._sync_site_selection()
    game.selecting_site = false
    game.site_panel.hide()
    game.store_type_panel.hide()
    game.town_view.show()
    game.store_view.hide()
    ui.layout_screen()
    if ui.notice.visible: ui._finish_notice()
    ui.open_window("root")
    await process_frame
    await process_frame
    assert(not ui.hits.is_empty())
    await tap(Vector2(160,0) + Vector2(65,80)*3)
    assert(ui.screen == "realestate", "Actual viewport touch must open the tapped menu")
    assert(not ui.building_card.visible, "Menu release must not tap the map behind it")
    await tap(Vector2(1200,422)) # rail cancel
    assert(ui.screen == "root", "Cancel rail must remain clickable with a menu open")
    await tap(Vector2(1200,342)) # rail accept (first entry = store)
    assert(ui.screen == "store", "Accept rail must remain clickable with a menu open")
    await tap(Vector2(80,342)) # command rail closes menu
    assert(ui.screen.is_empty(), "Command rail must close an open menu")
    game.town_view.show()
    game.store_view.hide()
    var found := false
    for y in range(32):
        for x in range(32):
            ui._on_map_building_tapped(Vector2i(x,y))
            if ui.building_card.visible:
                found = true
                break
        if found: break
    assert(found)
    await process_frame
    await process_frame
    var rect: Rect2 = ui.building_card.get_global_rect()
    assert(rect.position.x >= ui.PLAY_LEFT and rect.end.x <= ui.PLAY_RIGHT, "Building details must fit between rails")
    print("PS1_MENU_DISPATCH_PASS viewport native touch, cancel/accept/command rails, modal release, building bounds")
    quit()
