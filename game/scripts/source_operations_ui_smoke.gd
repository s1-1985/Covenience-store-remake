extends SceneTree
func _initialize() -> void:
    call_deferred("_run")
func _buttons(node: Node, label: String) -> Array:
    var result: Array = []
    if node is Button and node.text == label:
        result.append(node)
    for child in node.get_children():
        result.append_array(_buttons(child, label))
    return result
func _run() -> void:
    change_scene_to_file("res://scenes/main_menu.tscn")
    await process_frame
    await process_frame
    current_scene.new_game_button.pressed.emit()
    await process_frame
    await process_frame
    var game = current_scene
    game.paused = true
    game._on_site_tapped(Vector2i(26, 12))
    game.site_buy_button.pressed.emit()
    game.find_child("BuildStoreButton", true, false).pressed.emit()
    var phone = game.phone_ui
    phone.open_window("staff")
    assert(_buttons(phone.window_body, "配置変更").size() == 1)
    phone._confirm_dismiss("staff-2")
    var dialog: ConfirmationDialog
    for child in game.get_children():
        if child is ConfirmationDialog:
            dialog = child
    assert(dialog != null)
    dialog.confirmed.emit()
    assert(not game.simulation.staff.members.has("staff-2"))
    phone._fill_source_candidates("staff-2")
    var hire: Array = _buttons(phone.window_body, "雇う")
    assert(hire.size() == 10)
    hire[0].pressed.emit()
    assert(game.simulation.staff.members.has("staff-2"))
    phone._fill_source_transfers()
    assert(_buttons(phone.window_body, "交換して確定").size() == 1)
    phone.close_window()
    phone.open_window("staff")
    game._refresh_ui()
    await process_frame
    if DisplayServer.get_name() != "headless":
        await RenderingServer.frame_post_draw
        root.get_texture().get_image().save_png("/workspace/scratch/ef646d079df5/source-staff-screen.png")
    print("Source staff UI: dismissal confirmation, ten candidates, actual hiring, transfer controls and Japanese display passed")
    quit(0)
