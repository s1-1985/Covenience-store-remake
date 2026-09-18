extends Node

# Autoload singleton (see project.godot's [autoload] section). Godot has no
# built-in way to pass a parameter across a change_scene_to_file() call, so
# this is the minimal state needed to let the main menu tell the gameplay
# scene "load the existing save instead of starting fresh" without either
# scene needing to know about the other's internals.

var continue_from_save := false
