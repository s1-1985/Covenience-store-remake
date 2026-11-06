extends SceneTree
const Save := preload("res://scripts/save_game_service.gd")
var original: PackedByteArray
var had_save := false
var launch

func _initialize() -> void:
    call_deferred("_run")

func start_game() -> Node:
    launch.scenario_index = 0
    launch.continue_from_save = false
    change_scene_to_file("res://scenes/main.tscn")
    await process_frame
    await process_frame
    current_scene.paused = true
    return current_scene

func _run() -> void:
    launch = root.get_node("GameLaunchState")
    had_save = FileAccess.file_exists(Save.DEFAULT_SAVE_PATH)
    if had_save:
        original = FileAccess.get_file_as_bytes(Save.DEFAULT_SAVE_PATH)
    var game = await start_game()
    game.simulation._set_source_ending(1)
    game.simulation._record_event("manager_report", {"text": "終了中は通知を消費しない"})
    game._refresh_ui()
    var view = game.ending_view
    assert(view != null and view.ending == 1)
    assert("REMAKE_BALANCED_DEFAULT" in view.tables["evidence_note"])
    assert("REMAKE_BALANCED_DEFAULT" in FileAccess.get_file_as_string("res://scripts/ending_view.gd"))
    var notification_state: String = JSON.stringify(game.simulation.notifications.snapshot())
    await process_frame
    await process_frame
    assert(notification_state == JSON.stringify(game.simulation.notifications.snapshot()))
    assert(view.next_button.disabled)
    view.advance_frames(389)
    view.next_button.pressed.emit()
    assert(view.stage == "credits")
    assert(view.next_button.disabled)
    view.advance_frames(7120)
    view.next_button.pressed.emit()
    assert(view.stage == "save")
    assert(view.save_yes.visible and view.save_no.visible)
    view.save_no.pressed.emit()
    await process_frame
    await process_frame
    assert(current_scene.has_node("Panel/Margin/VBox/NewGameButton"))
    assert(FileAccess.file_exists(Save.DEFAULT_SAVE_PATH) == had_save)
    if had_save:
        assert(FileAccess.get_file_as_bytes(Save.DEFAULT_SAVE_PATH) == original)
    game = await start_game()
    game.simulation.source_progress["flags"] = 3
    game.simulation._set_source_ending(2)
    game._refresh_ui()
    view = game.ending_view
    view.advance_frames(389)
    view.advance()
    view.advance_frames(7120)
    view.advance()
    # A real filesystem failure: the temporary file path is a directory.
    assert(DirAccess.make_dir_recursive_absolute(Save.DEFAULT_SAVE_PATH + ".tmp") == OK)
    view.save_yes.pressed.emit()
    assert(game.simulation.source_progress["save_finished"] == 0)
    assert(view.stage == "save" and "保存できません" in view.status.text)
    assert(FileAccess.file_exists(Save.DEFAULT_SAVE_PATH) == had_save)
    if had_save:
        assert(FileAccess.get_file_as_bytes(Save.DEFAULT_SAVE_PATH) == original)
    assert(DirAccess.remove_absolute(Save.DEFAULT_SAVE_PATH + ".tmp") == OK)
    view.save_yes.pressed.emit()
    await process_frame
    await process_frame
    var payload: Dictionary = JSON.parse_string(FileAccess.get_file_as_string(Save.DEFAULT_SAVE_PATH))
    assert(int(payload["source_progress"]["save_finished"]) == 255)
    assert(int(payload["source_progress"]["flags"]) == 7)
    var menu = current_scene
    var choices = menu.find_child("ScenarioChoice", true, false)
    assert(not choices.is_item_disabled(3))
    menu.continue_button.pressed.emit()
    await process_frame
    assert(current_scene == menu and "クリア結果" in menu.status_label.text)
    game = await start_game()
    game.simulation._trigger_game_over("bankrupt")
    game._refresh_ui()
    view = game.ending_view
    assert(view != null and not view.save_yes.visible)
    view.advance_frames(5)
    view.next_button.pressed.emit()
    await process_frame
    await process_frame
    assert(FileAccess.get_file_as_string(Save.DEFAULT_SAVE_PATH) == JSON.stringify(payload))
    if had_save:
        var file := FileAccess.open(Save.DEFAULT_SAVE_PATH, FileAccess.WRITE)
        file.store_buffer(original)
        file.close()
    else:
        DirAccess.remove_absolute(Save.DEFAULT_SAVE_PATH)
    launch.progress_flags = 0
    print("SOURCE_ENDING_UI_PASS original artwork, credits, decline preservation, accepted FF save, title/unlock, bankruptcy")
    quit()
