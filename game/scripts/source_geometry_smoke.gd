extends SceneTree
const Geometry = preload("res://scripts/domain/program_geometry.gd")
func point(a) -> Vector2i:
    return Vector2i(int(a[0]), int(a[1]))
func grid_of(rows: Array) -> Dictionary:
    var result := {}
    for y in rows.size():
        for x in rows[y].size():
            result[Vector2i(x, y)] = int(rows[y][x])
    return result
func _init() -> void:
    var data: Dictionary = JSON.parse_string(FileAccess.get_file_as_string("res://data/source_geometry_cases.json"))
    for row in data["routes"]:
        var result: Dictionary = Geometry.search(grid_of(row["grid"]), int(row["width"]), int(row["height"]), point(row["start"]))
        assert(int(result["result"]) == int(row["result"]))
        if int(result["result"]) == 0:
            assert(result["goal"] == point(row["goal"]))
            assert(result["direction"] == int(row["goal"][2]))
            assert(result["grid"] == grid_of(row["gradient"]))
            var encoded := Geometry.encode(result["grid"], result["goal"], result["direction"])
            assert(encoded["packed"] == row["packed"].map(func(v): return int(v)))
            assert(encoded["start"] == point(row["route_start"]))
            assert(encoded["direction"] == int(row["route_start"][2]))
    for row in data["sides"]:
        var grid := {}
        for y in 10:
            for x in 10:
                grid[Vector2i(x, y)] = -2
        grid[Vector2i(4, 1)] = -1
        Geometry.use_sides(grid, 10, 10, Vector2i(2, 2), int(row["orientation"]), int(row["category"]), Vector2i(2, 1), bool(row["mode"]))
        assert(grid == grid_of(row["expected"]))
    for row in data["maps"]:
        var blocked := {}
        for p in row["blocked"]:
            blocked[point(p)] = true
        var result := Geometry.rebuild(int(row["width"]), int(row["height"]), row["floor"], blocked, point(row["room"]), point(row["room_size"]))
        assert(result["grid"] == grid_of(row["expected"]))
        assert(result["unreachable"] == int(row["unreachable"]))
    print("SOURCE_GEOMETRY_PASS 60 routes / 88 side masks / 24 working maps")
    quit()
