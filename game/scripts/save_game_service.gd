class_name SaveGameService
extends RefCounted

# Thin I/O boundary around VerticalSliceSimulation.save_state()/
# load_state(). Those two methods do the actual state transform (pure
# Dictionary in/out, independently testable); this class only turns that
# Dictionary into/from a JSON file under Godot's user:// data directory, so
# it stays out of scripts/domain/ (which is I/O-free by convention
# elsewhere in this client).

const DEFAULT_SAVE_PATH := "user://saves/vertical_slice_save.json"


func save_to_path(simulation, path: String = DEFAULT_SAVE_PATH) -> bool:
    var save_dir := path.get_base_dir()
    if not save_dir.is_empty():
        if DirAccess.make_dir_recursive_absolute(save_dir) != OK:
            return false
    # Commit a complete JSON file, preserving the old save on write failure.
    var temporary := path + ".tmp"
    var file := FileAccess.open(temporary, FileAccess.WRITE)
    if file == null:
        return false
    file.store_string(JSON.stringify(simulation.save_state()))
    file.flush()
    var error := file.get_error()
    file.close()
    if error != OK:
        DirAccess.remove_absolute(temporary)
        return false
    if DirAccess.rename_absolute(temporary, path) != OK:
        DirAccess.remove_absolute(temporary)
        return false
    return true


func load_from_path(simulation, path: String = DEFAULT_SAVE_PATH) -> bool:
    var parsed := read_from_path(path)
    if parsed.is_empty():
        return false
    return simulation.load_state(parsed)


func read_from_path(path: String = DEFAULT_SAVE_PATH) -> Dictionary:
    if not FileAccess.file_exists(path):
        return {}
    var file := FileAccess.open(path, FileAccess.READ)
    if file == null:
        return {}
    var json_text := file.get_as_text()
    var error := file.get_error()
    file.close()
    if error != OK:
        return {}
    var json := JSON.new()
    if json.parse(json_text) != OK or not json.data is Dictionary:
        return {}
    return json.data


func save_exists(path: String = DEFAULT_SAVE_PATH) -> bool:
    return FileAccess.file_exists(path)


func delete_save(path: String = DEFAULT_SAVE_PATH) -> void:
    if FileAccess.file_exists(path):
        DirAccess.remove_absolute(path)
