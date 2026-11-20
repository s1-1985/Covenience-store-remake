extends RefCounted
# SLPS_007.82 8003C628..3CB78. Mutate the grid during the row-major scan:
# the anchor cell itself is not revisited after its footprint is erased.
static func scan(grid: Array, floors: Array, descriptors: Array, rng) -> Dictionary:
    var burned: Array[Vector2i] = []
    var writes := 0
    for y in grid.size():
        for x in grid[y].size():
            var word := int(grid[y][x]) & 0xffffffff
            if word == 0:
                var code := int(floors[y/2][x/2]) & 255
                if code >= 128: code -= 256
                if code >= 0 and code < 16:
                    floors[y/2][x/2] = code/5*5 + rng.randi()%4 + 1
                    writes += 1
            if word & 0x80000000 == 0: continue
            var kind := (word >> 12) & 1023
            if kind >= 53: continue
            var descriptor: Array = descriptors[kind]
            if int(descriptor[0]) & 255 in [4,6]: continue
            var width := int(descriptor[9])*2
            var height := int(descriptor[10])*2
            if (word >> 22) & 3 >= 2:
                var previous := width
                width = height
                height = previous
            for yy in range(y,y+height):
                for xx in range(x,x+width): grid[yy][xx] = 0
            burned.append(Vector2i(x,y))
    return {"burned":burned,"floor_writes":writes}

static func clear_customer_image(grid: Array, at: Vector2i) -> void:
    if at.x < 0 or at.y < 0 or at.y >= grid.size() or at.x >= grid[at.y].size(): return
    grid[at.y][at.x] = int(grid[at.y][at.x]) & 0xffc00fff
