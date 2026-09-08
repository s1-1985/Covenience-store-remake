class_name StoreLayout
extends RefCounted

const CARDINAL_DIRECTIONS: Array[Vector2i] = [
    Vector2i(1, 0),
    Vector2i(-1, 0),
    Vector2i(0, 1),
    Vector2i(0, -1),
]

var width_subcells: int
var height_subcells: int
var entry: Vector2i
var exit: Vector2i
var blocked: Dictionary = {}
var fixtures: Array = []
var fixtures_by_id: Dictionary = {}
var _subcells_per_tile: int
var _initial_fixtures: Array


func _init(store_config: Dictionary, fixture_configs: Array) -> void:
    var scale := int(store_config["subcells_per_tile"])
    _subcells_per_tile = scale
    width_subcells = int(store_config["width_tiles"]) * scale
    height_subcells = int(store_config["height_tiles"]) * scale
    entry = _vec2i(store_config["entry_subcell"])
    exit = _vec2i(store_config["exit_subcell"])
    _initial_fixtures = fixture_configs.duplicate(true)
    fixtures = _initial_fixtures.duplicate(true)
    assert(width_subcells > 0 and height_subcells > 0 and scale > 0)
    assert(_inside(entry) and _inside(exit))
    _build_blocked_cells(scale)
    assert(not blocked.has(entry) and not blocked.has(exit))


func reset() -> void:
    fixtures = _initial_fixtures.duplicate(true)
    _build_blocked_cells(_subcells_per_tile)


func fixture_snapshot() -> Array:
    return fixtures.duplicate(true)


func restore_fixture_snapshot(snapshot: Array) -> void:
    assert(_fixture_configs_are_valid(snapshot))
    fixtures = snapshot.duplicate(true)
    _build_blocked_cells(_subcells_per_tile)


func interaction_for_fixture(fixture_id: String, expected_kind: String) -> Vector2i:
    assert(fixtures_by_id.has(fixture_id))
    var fixture: Dictionary = fixtures_by_id[fixture_id]
    assert(fixture["kind"] == expected_kind)
    return _vec2i(fixture["interaction_subcell"])


func fixture_origin(fixture_id: String) -> Vector2i:
    if not fixtures_by_id.has(fixture_id):
        return Vector2i(-1, -1)
    return _vec2i(fixtures_by_id[fixture_id]["origin_subcell"])


func is_walkable(cell: Vector2i) -> bool:
    return _inside(cell) and not blocked.has(cell)


func find_path(start: Vector2i, goal: Vector2i) -> Array[Vector2i]:
    if start == goal:
        return []
    var frontier: Array[Vector2i] = [start]
    var head := 0
    var came_from: Dictionary = {start: start}
    while head < frontier.size():
        var current: Vector2i = frontier[head]
        head += 1
        for direction in CARDINAL_DIRECTIONS:
            var candidate := current + direction
            if not _inside(candidate):
                continue
            if blocked.has(candidate) and candidate != goal:
                continue
            if came_from.has(candidate):
                continue
            came_from[candidate] = current
            if candidate == goal:
                return _reconstruct_path(came_from, start, goal)
            frontier.append(candidate)
    return []


func has_path(start: Vector2i, goal: Vector2i) -> bool:
    return start == goal or not find_path(start, goal).is_empty()


func fixture_at(cell: Vector2i) -> String:
    for fixture in fixtures:
        var origin := _vec2i(fixture["origin_subcell"])
        var footprint: Array = fixture["footprint_tiles"]
        var size := Vector2i(int(footprint[0]), int(footprint[1])) * _subcells_per_tile
        if Rect2i(origin, size).has_point(cell):
            return str(fixture["id"])
    return ""


func try_move_fixture(fixture_id: String, new_origin: Vector2i) -> bool:
    if not fixtures_by_id.has(fixture_id):
        return false
    var candidate_fixtures := fixtures.duplicate(true)
    for fixture in candidate_fixtures:
        if str(fixture["id"]) != fixture_id:
            continue
        var old_origin := _vec2i(fixture["origin_subcell"])
        var old_interaction := _vec2i(fixture["interaction_subcell"])
        var delta := new_origin - old_origin
        fixture["origin_subcell"] = [new_origin.x, new_origin.y]
        var new_interaction := old_interaction + delta
        fixture["interaction_subcell"] = [new_interaction.x, new_interaction.y]
        break
    if not _fixture_configs_are_valid(candidate_fixtures):
        return false
    fixtures = candidate_fixtures
    _build_blocked_cells(_subcells_per_tile)
    return true


func try_rotate_fixture_clockwise(fixture_id: String) -> bool:
    if not fixtures_by_id.has(fixture_id):
        return false
    var candidate_fixtures := fixtures.duplicate(true)
    for fixture in candidate_fixtures:
        if str(fixture["id"]) != fixture_id:
            continue
        var origin := _vec2i(fixture["origin_subcell"])
        var interaction := _vec2i(fixture["interaction_subcell"])
        var footprint: Array = fixture["footprint_tiles"]
        var old_height := int(footprint[1]) * _subcells_per_tile
        var relative_interaction := interaction - origin
        var rotated_interaction := Vector2i(
            old_height - 1 - relative_interaction.y,
            relative_interaction.x
        )
        fixture["footprint_tiles"] = [int(footprint[1]), int(footprint[0])]
        fixture["interaction_subcell"] = [
            origin.x + rotated_interaction.x,
            origin.y + rotated_interaction.y,
        ]
        fixture["rotation_quarter_turns"] = (
            int(fixture.get("rotation_quarter_turns", 0)) + 1
        ) % 4
        break
    if not _fixture_configs_are_valid(candidate_fixtures):
        return false
    fixtures = candidate_fixtures
    _build_blocked_cells(_subcells_per_tile)
    return true


func _build_blocked_cells(scale: int) -> void:
    blocked.clear()
    fixtures_by_id.clear()
    for fixture in fixtures:
        var fixture_id := str(fixture["id"])
        assert(not fixture_id.is_empty() and not fixtures_by_id.has(fixture_id))
        fixtures_by_id[fixture_id] = fixture
        var origin := _vec2i(fixture["origin_subcell"])
        var footprint: Array = fixture["footprint_tiles"]
        var width := int(footprint[0]) * scale
        var height := int(footprint[1]) * scale
        assert(width > 0 and height > 0)
        for y in range(origin.y, origin.y + height):
            for x in range(origin.x, origin.x + width):
                var cell := Vector2i(x, y)
                assert(_inside(cell))
                assert(not blocked.has(cell))
                blocked[cell] = true
    for fixture in fixtures:
        var interaction := _vec2i(fixture["interaction_subcell"])
        assert(_inside(interaction) and not blocked.has(interaction))


func _fixture_configs_are_valid(candidate_fixtures: Array) -> bool:
    var occupied: Dictionary = {}
    var ids: Dictionary = {}
    for fixture in candidate_fixtures:
        var fixture_id := str(fixture.get("id", ""))
        if fixture_id.is_empty() or ids.has(fixture_id):
            return false
        ids[fixture_id] = true
        var origin := _vec2i(fixture["origin_subcell"])
        var footprint: Array = fixture["footprint_tiles"]
        var width := int(footprint[0]) * _subcells_per_tile
        var height := int(footprint[1]) * _subcells_per_tile
        if width <= 0 or height <= 0:
            return false
        for y in range(origin.y, origin.y + height):
            for x in range(origin.x, origin.x + width):
                var cell := Vector2i(x, y)
                if not _inside(cell) or occupied.has(cell):
                    return false
                occupied[cell] = true
    for fixture in candidate_fixtures:
        var interaction := _vec2i(fixture["interaction_subcell"])
        if not _inside(interaction) or occupied.has(interaction):
            return false
    return not occupied.has(entry) and not occupied.has(exit)


func _reconstruct_path(came_from: Dictionary, start: Vector2i, goal: Vector2i) -> Array[Vector2i]:
    var reversed_path: Array[Vector2i] = []
    var current := goal
    while current != start:
        reversed_path.append(current)
        current = came_from[current]
    reversed_path.reverse()
    return reversed_path


func _inside(cell: Vector2i) -> bool:
    return cell.x >= 0 and cell.y >= 0 and cell.x < width_subcells and cell.y < height_subcells


func _vec2i(value: Array) -> Vector2i:
    return Vector2i(int(value[0]), int(value[1]))
