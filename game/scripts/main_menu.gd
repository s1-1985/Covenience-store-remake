extends Control

const SaveGameServiceScript := preload("res://scripts/save_game_service.gd")
const PhoneUIScript := preload("res://scripts/phone_ui.gd")
const GAMEPLAY_SCENE_PATH := "res://scenes/main.tscn"

@onready var new_game_button: Button = $Panel/Margin/VBox/NewGameButton
@onready var continue_button: Button = $Panel/Margin/VBox/ContinueButton
@onready var quit_button: Button = $Panel/Margin/VBox/QuitButton
@onready var status_label: Label = $Panel/Margin/VBox/StatusLabel

var ps_title
var _save_service


func _ready() -> void:


    TranslationServer.set_locale("ja")

    SoundManager.stop_music()
    SoundManager.play_source(-1)
    SoundManager.play_source_bgm(0) # original title 80057C50 -> BGM01
    if OS.has_feature("android") or "--android-preview" in OS.get_cmdline_user_args():
        $Background.color = Color("101715")
        $Panel.hide()
        ps_title = preload("res://scripts/ps1_title.gd").new()
        add_child(ps_title)
        ps_title.setup(self)
        $Panel.theme = PhoneUIScript.make_theme()
        $Panel.offset_left = 370
        $Panel.offset_right = 910
        $Panel.offset_top = 180
        $Panel.offset_bottom = 540
        $Panel/Margin/VBox/Title.text = "難易度を選んで下さい"
        $Panel/Margin/VBox/Title.add_theme_font_size_override("font_size",30)
        $Panel/Margin/VBox/Subtitle.hide()
        $Panel/Margin/VBox/Separator.hide()
        new_game_button.text = "決定"
        quit_button.text = "戻る"
        continue_button.hide()
    var choices := OptionButton.new()
    choices.name = "ScenarioChoice"
    choices.custom_minimum_size.y = 48
    for label in ["初級", "中級", "上級", "極上"]:
        choices.add_item(label)
    var limit := preload("res://scripts/domain/program_progression.gd").menu_limit(GameLaunchState.progress_flags)
    choices.set_item_disabled(3, limit < 4)
    if GameLaunchState.scenario_index >= limit:
        GameLaunchState.scenario_index = 0
    choices.select(GameLaunchState.scenario_index)
    choices.item_selected.connect( func(index): GameLaunchState.scenario_index = index)
    $Panel / Margin / VBox.add_child(choices)
    $Panel / Margin / VBox.move_child(choices, new_game_button.get_index())
    _save_service = SaveGameServiceScript.new()
    continue_button.disabled = not _save_service.save_exists()
    new_game_button.pressed.connect(_on_new_game_pressed)
    continue_button.pressed.connect(_on_continue_pressed)
    quit_button.pressed.connect(_on_quit_pressed)
    if not GameLaunchState.continue_error.is_empty():
        status_label.text = GameLaunchState.continue_error
        if ps_title != null:
            ps_title.phase = "menu"
            ps_title.selected = 1
            ps_title.message = GameLaunchState.continue_error
        GameLaunchState.continue_error = ""


func _on_new_game_pressed() -> void:
    GameLaunchState.continue_from_save = false
    get_tree().change_scene_to_file(GAMEPLAY_SCENE_PATH)


func _on_continue_pressed() -> void:
    if not _save_service.save_exists():
        status_label.text = tr("No save file found.")
        continue_button.disabled = true
        return
    var saved: Dictionary = _save_service.read_from_path()
    if saved.is_empty():
        status_label.text = tr("No compatible save found")
        return
    if not saved.get("source_progress", {}) is Dictionary:
        status_label.text = tr("No compatible save found")
        return
    var progress: Dictionary = saved.get("source_progress", {})
    if int(progress.get("save_finished", 0)) == 255:
        GameLaunchState.progress_flags = int(progress.get("flags", 0)) & 255
        var choices = find_child("ScenarioChoice", true, false)
        choices.set_item_disabled(3, preload("res://scripts/domain/program_progression.gd").menu_limit(GameLaunchState.progress_flags) < 4)
        status_label.text = "クリア結果を読み込みました。"
        return
    var ids := ["town0001", "town0002", "town0003", "townps"]
    for index in ids.size():
        if str(saved.get("scenario_id", "")) == "ps1-%s-recovered" % ids[index]:
            GameLaunchState.scenario_index = index
    GameLaunchState.continue_from_save = true
    get_tree().change_scene_to_file(GAMEPLAY_SCENE_PATH)


func show_scenarios() -> void:
    ps_title.hide()
    $Panel.show()
    new_game_button.grab_focus()

func _on_quit_pressed() -> void:
    if ps_title != null:
        $Panel.hide()
        ps_title.show()
        ps_title.grab_focus()
        ps_title.phase = "menu"
        return
    get_tree().quit()
