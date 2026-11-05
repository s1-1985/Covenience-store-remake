class_name ProgramOperations
extends RefCounted

# Native ports of verified models from analysis commit 2c00ba53.
# floor_wear.py (80031498), staff_work.py, staff_candidate_pool.py (8006F8BC).
static func cleanliness(rows: Array) -> int:
    var count := 0
    var clean := 0
    for row in rows:
        for value in row:
            if int(value) >= 0 and int(value) < 16:
                count += 1
                clean += int(int(value) % 5 == 0)
    return clean * 100 / count if count else 100

static func wear(rows: Array, previous: int, positions: Array, rng) -> int:
    var percentage := cleanliness(rows)
    if previous < percentage:
        for position in positions:
            var x: int = position.x / 2
            var y: int = position.y / 2
            if y < 0 or y >= rows.size() or x < 0 or x >= rows[y].size():
                continue
            var code := int(rows[y][x])
            if code >= 0 and code < 16 and code % 5 == 0:
                rows[y][x] = code / 5 * 5 + rng.randi() % 4 + 1
                break
    return percentage

static func sample_candidates(free: Array, rng) -> Array[String]:
    var slots := free.duplicate()
    var result: Array[String] = []
    # Preserve rejected repeat draws: the source marks an entry -1 rather
    # than shrinking the sampling array, so the next RNG value is significant.
    while result.size() < mini(10, free.size()):
        var index: int = rng.randi() % slots.size()
        if str(slots[index]) != "":
            result.append(str(slots[index]))
            slots[index] = ""
    return result

static func refill_threshold(ability: int, policy: int) -> int:
    return ability * 2 / 3 if policy in [1, 2] else 99

static func clean_tile(code: int, ability: int, rng) -> int:
    if rng.randi() % 5 != 0:
        return code
    if rng.randi() % 100 + 1 > ability:
        return code
    return code / 5 * 5

# Generic route target tie order, movement.py 80017...; original BFS visits
# cells in row-major order at each depth, with north/south/west/east neighbors.
static func route(start: Vector2i, goals: Dictionary, width: int, height: int, walkable: Callable) -> Array[Vector2i]:
    var result: Array[Vector2i] = []
    if goals.has(start):
        return result
    var grid := {start: 0}
    var previous := {}
    var depth := 0
    var directions := [Vector2i.UP, Vector2i.DOWN, Vector2i.LEFT, Vector2i.RIGHT]
    var target := Vector2i(-1, -1)
    while target.x < 0:
        var changed := false
        for y in height:
            for x in width:
                var cell := Vector2i(x, y)
                if grid.get(cell, -1) != depth:
                    continue
                for direction in directions:
                    var next: Vector2i = cell + direction
                    if next.x < 0 or next.x >= width or next.y < 0 or next.y >= height or grid.has(next):
                        continue
                    if goals.has(next) or walkable.call(next):
                        grid[next] = depth + 1
                        previous[next] = cell
                        changed = true
                        if goals.has(next):
                            target = next
                            break
                if target.x >= 0:
                    break
            if target.x >= 0:
                break
        if not changed:
            return result
        depth += 1
    while target != start:
        result.push_front(target)
        target = previous[target]
    return result
