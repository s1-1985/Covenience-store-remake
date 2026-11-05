class_name ProgramGeometry
extends RefCounted

# CONFIRMED_BINARY: movement.py, route_codec.py, use_sides.py, store_map.py
# analysis 2c00ba53. Directions and gradient tie order are source data.
const DIRECTIONS := [Vector2i.UP, Vector2i.DOWN, Vector2i.LEFT, Vector2i.RIGHT]
const BACKTRACK := [Vector2i.DOWN, Vector2i.UP, Vector2i.RIGHT, Vector2i.LEFT]
const TURN := [3, 2, 0, 1]
const SIDE_TABLES := [[1, 0, 2, 3], [2, 3, 1, 0], [3, 2, 0, 1]]

static func inside(p: Vector2i, width: int, height: int) -> bool:
    return p.x >= 0 and p.y >= 0 and p.x < width and p.y < height

static func floor_value(rows: Array, p: Vector2i) -> int:
    var value := int(rows[p.y / 2][p.x / 2])
    return value - 256 if value >= 128 else value

static func rebuild(width: int, height: int, floors: Array, blocked: Dictionary, room: Vector2i, room_size: Vector2i) -> Dictionary:
    var grid := {}
    var frontier: Array[Vector2i] = []
    for y in height:
        for x in width:
            var p := Vector2i(x, y)
            grid[p] = -1 if blocked.has(p) else (-2 if floor_value(floors, p) < 28 else 0)
    # Preserve the source's completed initialization-loop locals for top/left.
    for x in range(room.x, room.x + room_size.x * 2):
        for p in [Vector2i(x, height - 1), Vector2i(x, room.y + room_size.y * 2)]:
            if inside(p, width, height) and grid[p] == -2:
                grid[p] = 0
    for y in range(room.y, room.y + room_size.y * 2):
        for p in [Vector2i(width - 1, y), Vector2i(room.x + room_size.x * 2, y)]:
            if inside(p, width, height) and grid[p] == -2:
                grid[p] = 0
    for p in grid:
        if grid[p] == 0:
            frontier.append(p)
    var depth := 0
    while not frontier.is_empty():
        frontier.sort_custom(func(a, b): return a.y * width + a.x < b.y * width + b.x)
        var next: Array[Vector2i] = []
        for p in frontier:
            for d in DIRECTIONS:
                var n: Vector2i = p + d
                if grid.get(n, -1) == -2:
                    grid[n] = depth + 1
                    next.append(n)
        frontier = next
        depth += 1
    var unreachable := 0
    for y in height:
        for x in width:
            var p := Vector2i(x, y)
            var value := int(grid[p])
            if value == -2:
                grid[p] = -10000
                if x + 1 < width and y + 1 < height and grid[p + Vector2i.RIGHT] == -2 and grid[p + Vector2i.DOWN] == -2 and grid[p + Vector2i.ONE] == -2:
                    grid[p] = -10001
                    for d in [Vector2i.RIGHT, Vector2i.DOWN, Vector2i.ONE]:
                        grid[p + d] = -10000
                    unreachable += 1
            elif value > 0:
                grid[p] = -2
            else:
                var code := floor_value(floors, p)
                if code >= 28 and code < 32:
                    grid[p] = -3
                elif code >= 32 and code < 36:
                    grid[p] = -4
                elif value == 0:
                    grid[p] = -2
    return {"grid": grid, "unreachable": unreachable}

static func prepare(base: Dictionary, occupied: Dictionary, outside: bool, mode: int) -> Dictionary:
    var grid := base.duplicate()
    for p in grid:
        if mode == 0 and occupied.has(p):
            grid[p] = -1
        elif grid[p] == -3:
            grid[p] = -2 if outside else -1
        elif grid[p] == -4:
            grid[p] = -1 if outside else -2
    return grid

static func use_sides(grid: Dictionary, width: int, height: int, origin: Vector2i, orientation: int, category: int, fixture_size: Vector2i, staff_mode: bool) -> void:
    var size := fixture_size * 2
    if orientation >= 2:
        size = Vector2i(size.y, size.x)
    var mask := 15
    if category in [0, 2, 5, 8]:
        mask = 8 >> orientation
    elif category == 4:
        mask = 8 >> ([1, 0, 3, 2][orientation] if staff_mode else orientation)
    for x in range(origin.x, origin.x + size.x):
        if mask & 8:
            _mark(grid, Vector2i(x, origin.y - 1), width, height, 10001)
        if mask & 4:
            _mark(grid, Vector2i(x, origin.y + size.y), width, height, 10000)
    for y in range(origin.y, origin.y + size.y):
        if mask & 2:
            _mark(grid, Vector2i(origin.x - 1, y), width, height, 10003)
        if mask & 1:
            _mark(grid, Vector2i(origin.x + size.x, y), width, height, 10002)

static func _mark(grid: Dictionary, p: Vector2i, width: int, height: int, value: int) -> void:
    if inside(p, width, height) and grid[p] != -1:
        grid[p] = value

static func search(grid: Dictionary, width: int, height: int, start: Vector2i) -> Dictionary:
    if not grid.has(start):
        return {"result": 1}
    if grid[start] >= 10000:
        var direction := ((int(grid[start]) & 255) - 16) & 255
        grid[start] = 0
        return {"result": 0, "goal": start, "direction": direction, "grid": grid}
    var frontier: Array[Vector2i] = []
    for p in grid:
        if grid[p] == 0:
            frontier.append(p)
    var depth := 0
    while not frontier.is_empty():
        frontier.sort_custom(func(a, b): return a.y * width + a.x < b.y * width + b.x)
        var next: Array[Vector2i] = []
        for p in frontier:
            for d in DIRECTIONS:
                var n: Vector2i = p + d
                if not inside(n, width, height):
                    continue
                var value := int(grid[n])
                if value >= 10000:
                    grid[n] = depth + 1
                    return {"result": 0, "goal": n, "direction": ((value & 255) - 16) & 255, "grid": grid}
                if value == -2:
                    grid[n] = depth + 1
                    next.append(n)
        frontier = next
        depth += 1
    return {"result": 1}

static func encode(grid: Dictionary, goal: Vector2i, direction: int) -> Dictionary:
    var output := [255, 255, 255, 255, 255, 255, 255, 255, 255, 255]
    var cursor := goal
    var depth := int(grid[goal])
    var count := 0
    var guard := 0
    var runs: Array = []
    while depth > 0:
        guard += 1
        assert(guard <= 4 * (int(grid[goal]) + 1) + 10000, "Invalid source route gradient")
        var next: Vector2i = cursor + BACKTRACK[direction]
        if grid.get(next, -100000) == depth - 1:
            cursor = next
            count += 1
            depth -= 1
        else:
            if count > 0:
                runs.push_front(((direction << 6) | (count & 255)) & 255)
            direction = TURN[direction]
            count = 0
    runs.push_front(((direction << 6) | (count & 255)) & 255)
    for i in mini(runs.size(), 10):
        output[i] = runs[i]
    var path: Array[Vector2i] = []
    var p := cursor
    for value in output:
        if value == 255:
            break
        for step in int(value) & 63:
            p += DIRECTIONS[int(value) >> 6]
            path.append(p)
    return {"packed": output, "start": cursor, "direction": direction, "path": path}

static func route(start: Vector2i, goals: Dictionary, width: int, height: int, walkable: Callable) -> Array[Vector2i]:
    var grid := {}
    for y in height:
        for x in width:
            var p := Vector2i(x, y)
            grid[p] = -2 if walkable.call(p) else -1
    for p in goals:
        grid[p] = 10000
    if not goals.has(start):
        grid[start] = 0
    var found := search(grid, width, height, start)
    var empty: Array[Vector2i] = []
    if int(found["result"]) != 0:
        return empty
    return encode(found["grid"], found["goal"], found["direction"])["path"]
