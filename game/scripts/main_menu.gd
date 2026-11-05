extends Control

const SaveGameServiceScript := preload("res://scripts/save_game_service.gd")
const PhoneUIScript := preload("res://scripts/phone_ui.gd")
const GAMEPLAY_SCENE_PATH := "res://scenes/main.tscn"

@onready var new_game_button: Button = $Panel/Margin/VBox/NewGameButton
@onready var continue_button: Button = $Panel/Margin/VBox/ContinueButton
@onready var quit_button: Button = $Panel/Margin/VBox/QuitButton
@onready var status_label: Label = $Panel/Margin/VBox/StatusLabel

var _save_service


func _ready() -> void:


    TranslationServer.set_locale("ja")

    SoundManager.play_theme("town")
    if OS.has_feature("android") or "--android-preview" in OS.get_cmdline_user_args():

        PhoneUIScript.add_field($Background)
        $Panel.offset_left = 340
        $Panel.offset_right = 940
        $Panel.offset_top = 40
        $Panel.offset_bottom = 680
        $Panel.theme = PhoneUIScript.make_theme()
        $Panel / Margin / VBox / Title.text = "ザ・コンビニ\n～あの町を独占せよ～"
        $Panel / Margin / VBox / Title.add_theme_font_size_override("font_size", 40)
        $Panel / Margin / VBox / Title.add_theme_color_override("font_color", Color("2f7d68"))
        $Panel / Margin / VBox / Subtitle.text = "再現試作（開発途中のプレイ確認版）"
        $Panel / Margin / VBox / Subtitle.add_theme_color_override("font_color", Color("6b6152"))
        for button in [new_game_button, continue_button, quit_button]:
            button.custom_minimum_size.y = 80
            button.add_theme_font_size_override("font_size", 30)
    var choices := OptionButton.new()
    choices.name = "ScenarioChoice"
    choices.custom_minimum_size.y = 48
    for label in ["初級", "中級", "上級", "極上"]:
        choices.add_item(label)
    choices.select(GameLaunchState.scenario_index)
    choices.item_selected.connect( func(index): GameLaunchState.scenario_index = index)
    $Panel / Margin / VBox.add_child(choices)
    $Panel / Margin / VBox.move_child(choices, new_game_button.get_index())
    _save_service = SaveGameServiceScript.new()
    continue_button.disabled = not _save_service.save_exists()
    new_game_button.pressed.connect(_on_new_game_pressed)
    continue_button.pressed.connect(_on_continue_pressed)
    quit_button.pressed.connect(_on_quit_pressed)


func _on_new_game_pressed() -> void:
    GameLaunchState.continue_from_save = false
    get_tree().change_scene_to_file(GAMEPLAY_SCENE_PATH)


func _on_continue_pressed() -> void:
    if not _save_service.save_exists():
        status_label.text = tr("No save file found.")
        continue_button.disabled = true
        return
    var saved = JSON.parse_string(FileAccess.get_file_as_string(SaveGameServiceScript.DEFAULT_SAVE_PATH))
    if saved is Dictionary:
        var ids := ["town0001", "town0002", "town0003", "townps"]
        for index in ids.size():
            if str(saved.get("scenario_id", "")) == "ps1-%s-recovered" % ids[index]:
                GameLaunchState.scenario_index = index
    GameLaunchState.continue_from_save = true
    get_tree().change_scene_to_file(GAMEPLAY_SCENE_PATH)


func _on_quit_pressed() -> void:
    get_tree().quit()
