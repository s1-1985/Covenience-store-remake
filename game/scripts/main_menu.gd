extends Control

const SaveGameServiceScript := preload("res://scripts/save_game_service.gd")
const GAMEPLAY_SCENE_PATH := "res://scenes/main.tscn"

@onready var new_game_button: Button = $Panel/Margin/VBox/NewGameButton
@onready var continue_button: Button = $Panel/Margin/VBox/ContinueButton
@onready var quit_button: Button = $Panel/Margin/VBox/QuitButton
@onready var status_label: Label = $Panel/Margin/VBox/StatusLabel

var _save_service


func _ready() -> void:
    if OS.has_feature("android") or "--android-preview" in OS.get_cmdline_user_args():
        $Panel.offset_left = 340
        $Panel.offset_right = 940
        $Panel.offset_top = 140
        $Panel.offset_bottom = 580
        var mobile_theme := $Panel.theme.duplicate() as Theme
        mobile_theme.default_font_size = 22
        mobile_theme.set_font_size("font_size", "Button", 26)
        $Panel.theme = mobile_theme
        for button in [new_game_button, continue_button, quit_button]:
            button.custom_minimum_size.y = 72
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
    GameLaunchState.continue_from_save = true
    get_tree().change_scene_to_file(GAMEPLAY_SCENE_PATH)


func _on_quit_pressed() -> void:
    get_tree().quit()
