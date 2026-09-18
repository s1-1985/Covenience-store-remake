extends Control

const SaveGameServiceScript := preload("res://scripts/save_game_service.gd")
const GAMEPLAY_SCENE_PATH := "res://scenes/main.tscn"

@onready var new_game_button: Button = $Panel/Margin/VBox/NewGameButton
@onready var continue_button: Button = $Panel/Margin/VBox/ContinueButton
@onready var quit_button: Button = $Panel/Margin/VBox/QuitButton
@onready var status_label: Label = $Panel/Margin/VBox/StatusLabel

var _save_service


func _ready() -> void:
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
        status_label.text = "No save file found."
        continue_button.disabled = true
        return
    GameLaunchState.continue_from_save = true
    get_tree().change_scene_to_file(GAMEPLAY_SCENE_PATH)


func _on_quit_pressed() -> void:
    get_tree().quit()
