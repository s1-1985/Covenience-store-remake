extends Node


var continue_from_save := false

var scenario_index := 0
var progress_flags := 0

func _ready() -> void:
    var path := "user://saves/vertical_slice_save.json"
    if FileAccess.file_exists(path):
        var saved = JSON.parse_string(FileAccess.get_file_as_string(path))
        if saved is Dictionary and saved.get("source_progress", {}) is Dictionary:
            progress_flags = int(saved.get("source_progress", {}).get("flags", 0)) & 255
