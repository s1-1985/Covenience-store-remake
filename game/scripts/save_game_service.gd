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
        DirAccess.make_dir_recursive_absolute(save_dir)
    var file := FileAccess.open(path, FileAccess.WRITE)
    if file == null:
        return false
    file.store_string(JSON.stringify(simulation.save_state()))
    file.close()
    return true


func load_from_path(simulation, path: String = DEFAULT_SAVE_PATH) -> bool:
    if not FileAccess.file_exists(path):
        return false
    var file := FileAccess.open(path, FileAccess.READ)
    if file == null:
        return false
    var json_text := file.get_as_text()
    file.close()
    var parsed = JSON.parse_string(json_text)
    if typeof(parsed) != TYPE_DICTIONARY:
        return false
    return simulation.load_state(parsed)


func save_exists(path: String = DEFAULT_SAVE_PATH) -> bool:
    return FileAccess.file_exists(path)


func delete_save(path: String = DEFAULT_SAVE_PATH) -> void:
    if FileAccess.file_exists(path):
        DirAccess.remove_absolute(path)
