extends SceneTree
## Isolated Godot 4 map-asset render smoke test.
## Reads existing repository PNGs and manifests. Writes ONLY to a newly created
## output_<identifier> directory immediately beneath this isolated project.
## This is not an original-PS1-fidelity test or an approval of candidate art.

const MANIFEST_REL := "chatgpt_map_assets/manifests/connection_45_candidate_registry_2026-10-30.json"
const SAMPLES_REL := "chatgpt_map_assets/samples/connection_45_topology_5x5_2026-10-31.json"
const TILE_PX := 24
const SOURCE_PX := 64
const STEPS := [
	[1, 0, -1, 4],
	[2, 1, 0, 8],
	[4, 0, 1, 1],
	[8, -1, 0, 2]
]
const KINDS := ["road", "rail", "river"]


func _initialize() -> void:
	call_deferred("_run")


func _argument(args: PackedStringArray, flag: String) -> String:
	var index := args.find(flag)
	if index < 0 or index + 1 >= args.size():
		return ""
	return args[index + 1]


func _read_json(path: String) -> Variant:
	if not FileAccess.file_exists(path):
		push_error("Missing read-only input: " + path)
		return null
	return JSON.parse_string(FileAccess.get_file_as_string(path))


func _failure(message: String) -> void:
	push_error("Issue232 smoke FAIL: " + message)
	quit(2)


func _run() -> void:
	var args := OS.get_cmdline_user_args()
	var repo_root := _argument(args, "--repo-root").simplify_path()
	var output_name := _argument(args, "--output-name")
	if repo_root.is_empty() or not DirAccess.dir_exists_absolute(repo_root):
		_failure("--repo-root must be an existing repository directory")
		return
	if not output_name.begins_with("output_") or not output_name.is_valid_identifier():
		_failure("--output-name must be a fresh identifier starting with output_")
		return

	var project_root := ProjectSettings.globalize_path("res://").simplify_path()
	var expected_root := repo_root.path_join("chatgpt_map_assets/godot_smoke_2026-11-04").simplify_path()
	if project_root != expected_root:
		_failure("Project must be launched from the isolated directory in --repo-root")
		return
	var output_dir := project_root.path_join(output_name)
	if DirAccess.dir_exists_absolute(output_dir) or FileAccess.file_exists(output_dir):
		_failure("Output already exists; refusing to overwrite: " + output_dir)
		return

	var manifest = _read_json(repo_root.path_join(MANIFEST_REL))
	var samples = _read_json(repo_root.path_join(SAMPLES_REL))
	if not manifest is Dictionary or not samples is Dictionary:
		_failure("Manifest or sample JSON could not be parsed")
		return
	var assets: Array = manifest.get("assets", [])
	var maps: Array = samples.get("maps", [])
	if assets.size() != 45 or maps.size() != 3:
		_failure("Expected exactly 45 assets and 3 topology maps")
		return

	var by_id: Dictionary = {}
	var images: Dictionary = {}
	var mask_seen: Dictionary = {}
	var counts := {"road": 0, "rail": 0, "river": 0}
	for entry in assets:
		if not entry is Dictionary:
			_failure("Malformed manifest asset entry")
			return
		var kind := str(entry.get("kind", ""))
		var mask := int(entry.get("direction_bits_nesw", 0))
		var asset_id := str(entry.get("asset_id", ""))
		var rel := str(entry.get("candidate_path", ""))
		if not KINDS.has(kind) or mask < 1 or mask > 15:
			_failure("Invalid kind/mask: " + asset_id)
			return
		var suffix := ""
		for part in [[1, "n"], [2, "e"], [4, "s"], [8, "w"]]:
			if mask & int(part[0]):
				suffix += str(part[1])
		if asset_id != kind + "_" + suffix or by_id.has(asset_id):
			_failure("Duplicate or inconsistent asset id: " + asset_id)
			return
		var mask_key := kind + ":" + str(mask)
		if mask_seen.has(mask_key):
			_failure("Duplicate direction mask: " + mask_key)
			return
		if not rel.begins_with("chatgpt_map_assets/") or rel.contains("..") or not rel.ends_with(".png"):
			_failure("Unsafe candidate path: " + rel)
			return
		if int(entry.get("width_px", 0)) != SOURCE_PX or int(entry.get("height_px", 0)) != SOURCE_PX:
			_failure("Wrong manifest dimensions: " + asset_id)
			return
		var image := Image.new()
		var err := image.load(repo_root.path_join(rel))
		if err != OK or image.get_size() != Vector2i(SOURCE_PX, SOURCE_PX):
			_failure("PNG missing, corrupt, or not 64x64: " + rel)
			return
		by_id[asset_id] = entry
		images[asset_id] = image
		mask_seen[mask_key] = true
		counts[kind] += 1
	for kind in KINDS:
		if counts[kind] != 15:
			_failure("Incomplete masks for " + kind)
			return

	var validated_maps: Array = []
	for map_data in maps:
		if not map_data is Dictionary:
			_failure("Malformed topology map")
			return
		var kind := str(map_data.get("kind", ""))
		var width := int(map_data.get("width", 0))
		var height := int(map_data.get("height", 0))
		var tiles: Array = map_data.get("tiles", [])
		if not KINDS.has(kind) or width != 5 or height != 5 or tiles.size() != 24:
			_failure("Unexpected topology map dimensions/count")
			return
		var positions: Dictionary = {}
		var distinct: Dictionary = {}
		for tile in tiles:
			if not tile is Dictionary:
				_failure("Malformed tile entry")
				return
			var x := int(tile.get("x", -1))
			var y := int(tile.get("y", -1))
			var asset_id := str(tile.get("asset_id", ""))
			var mask := int(tile.get("direction_bits_nesw", 0))
			var key := str(x) + "," + str(y)
			if x < 0 or x >= width or y < 0 or y >= height or positions.has(key):
				_failure("Out-of-bounds or repeated tile: " + key)
				return
			if not by_id.has(asset_id) or str(by_id[asset_id]["kind"]) != kind or int(by_id[asset_id]["direction_bits_nesw"]) != mask:
				_failure("Tile does not match manifest: " + asset_id)
				return
			positions[key] = tile
			distinct[mask] = true
		if distinct.size() != 15:
			_failure("Not all 15 masks represented in " + kind)
			return
		var directed_edges := 0
		for tile in tiles:
			var x := int(tile["x"])
			var y := int(tile["y"])
			var mask := int(tile["direction_bits_nesw"])
			for step in STEPS:
				if mask & int(step[0]):
					var other_key := str(x + int(step[1])) + "," + str(y + int(step[2]))
					if not positions.has(other_key) or (int(positions[other_key]["direction_bits_nesw"]) & int(step[3])) == 0:
						_failure("Non-reciprocal connection in " + kind + " at " + str(x) + "," + str(y))
						return
					directed_edges += 1
		if directed_edges != 48:
			_failure("Expected 24 reciprocal edges for " + kind)
			return
		validated_maps.append(map_data)

	# All inputs have passed validation. This creates a fresh directory only.
	if DirAccess.make_dir_absolute(output_dir) != OK:
		_failure("Could not create fresh output directory")
		return
	var results: Array = []
	for map_data in validated_maps:
		var kind := str(map_data["kind"])
		var viewport := SubViewport.new()
		viewport.size = Vector2i(5 * TILE_PX, 5 * TILE_PX)
		viewport.transparent_bg = true
		viewport.disable_3d = true
		viewport.render_target_update_mode = SubViewport.UPDATE_ALWAYS
		get_root().add_child(viewport)
		for tile in map_data["tiles"]:
			var sprite := Sprite2D.new()
			sprite.centered = false
			sprite.texture_filter = CanvasItem.TEXTURE_FILTER_NEAREST
			sprite.texture = ImageTexture.create_from_image(images[str(tile["asset_id"])])
			sprite.position = Vector2(int(tile["x"]) * TILE_PX, int(tile["y"]) * TILE_PX)
			sprite.scale = Vector2(float(TILE_PX) / SOURCE_PX, float(TILE_PX) / SOURCE_PX)
			viewport.add_child(sprite)
		await RenderingServer.frame_post_draw
		await RenderingServer.frame_post_draw
		var rendered := viewport.get_texture().get_image()
		var target := output_dir.path_join(kind + "_24px_godot.png")
		if rendered == null or rendered.get_size() != Vector2i(120, 120):
			viewport.queue_free()
			_failure("Invalid viewport image for " + kind)
			return
		var used := rendered.get_used_rect()
		if used.size.x == 0 or used.size.y == 0:
			viewport.queue_free()
			_failure("Blank viewport image for " + kind)
			return
		if rendered.save_png(target) != OK:
			viewport.queue_free()
			_failure("PNG save failed for " + kind)
			return
		results.append({"kind": kind, "output": kind + "_24px_godot.png", "size_px": [120, 120], "mask_count": 15, "connected_edges": 24, "nonempty_render": true})
		viewport.queue_free()

	var report := {
		"issue": 232,
		"status": "GODOT_RENDER_SMOKE_ONLY_NOT_ART_ACCEPTED",
		"engine": Engine.get_version_info(),
		"candidate_count": assets.size(),
		"results": results,
		"not_verified": ["original PlayStation appearance", "visual seam quality", "full game regression", "main renderer integration"],
		"source_files_modified": false
	}
	var report_file := FileAccess.open(output_dir.path_join("report.json"), FileAccess.WRITE)
	if report_file == null:
		_failure("Could not write report")
		return
	report_file.store_string(JSON.stringify(report, "\t") + "\n")
	report_file.close()
	print("Issue232 isolated Godot smoke PASS: 45 candidates, 3 viewport images, no game edits. Art NOT approved.")
	quit(0)
