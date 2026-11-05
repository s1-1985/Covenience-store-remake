class_name ProgramPeople
extends RefCounted

# Native state machines from customer_loop, purchase_full, customer_queue_state,
# staff_loop_selected, staff_target_chain (analysis 2c00ba53).
const Geometry = preload("res://scripts/domain/program_geometry.gd")
const Rules = preload("res://scripts/domain/program_rules.gd")
const OFF := Vector2i(-1, -1)
const REST_OFFSETS := [Vector2i(0, 2), Vector2i(0, 1), Vector2i(1, 1)]

static func clock(s) -> int:
    return ((s.day_count - 1) * 1440 + s.minute_of_day)

static func occupied(s, actor = null) -> Dictionary:
    var result = s.layout.blocked.duplicate()
    for p in s.customers.active_customers() + s.staff.all_staff():
        if p != actor and p.position.x >= 0:
            result[p.position] = true
    return result

static func fixture(s, p: Vector2i) -> Dictionary:
    var result = {}
    for f in s.layout.fixtures:
        var o: Vector2i = s._vec2i_from_array(f["origin_subcell"])
        var size: Vector2i = s._vec2i_from_array(f["footprint_tiles"]) * 2
        if p.x >= o.x and p.y >= o.y and p.x < o.x + size.x and p.y < o.y + size.y:
            result = f
    return result

static func facing_fixture(s, p) -> Dictionary:
    return fixture(s, p.position + Geometry.DIRECTIONS[p.source_direction])

static func base_grid(s) -> Dictionary:
    if s.layout.source_work_grid.is_empty():
        var room = OFF
        var size = Vector2i(2, 2)
        for f in s.layout.fixtures:
            if str(f["kind"]) == "break_room":
                room = s._vec2i_from_array(f["origin_subcell"])
                var kind: int = s.program_fixture_kind(f)
                size = Vector2i(int(s._recovery["fixture_records"][kind][9]), int(s._recovery["fixture_records"][kind][10]))
        if room == OFF:
            return {}
        s.layout.source_work_grid = Geometry.rebuild(s.layout.width_subcells, s.layout.height_subcells, s.config["store"]["source_floor"], s.layout.blocked, room, size)["grid"]
    return s.layout.source_work_grid

static func mark_fixture(s, grid: Dictionary, f: Dictionary, staff_mode: bool) -> void:
    var kind: int = s.program_fixture_kind(f)
    if kind < 0 or kind >= 53:
        return
    var row: Array = s._recovery["fixture_records"][kind]
    Geometry.use_sides(grid, s.layout.width_subcells, s.layout.height_subcells, s._vec2i_from_array(f["origin_subcell"]), [0, 3, 1, 2][int(f.get("rotation_quarter_turns", 0))], int(row[0]) & 255, Vector2i(int(row[9]), int(row[10])), staff_mode)

static func rest_origin(s) -> Vector2i:
    for f in s.layout.fixtures:
        if str(f["kind"]) == "break_room":
            return s._vec2i_from_array(f["origin_subcell"])
    return OFF

static func rest_points(s) -> Array[Vector2i]:
    var o = rest_origin(s)
    var result: Array[Vector2i] = []
    for x in range(o.x, o.x + 4):
        for p in [Vector2i(x, o.y - 1), Vector2i(x, o.y + 4)]:
            if x < s.layout.width_subcells and p.y >= 0 and p.y < s.layout.height_subcells:
                result.append(p)
    for y in range(o.y, o.y + 4):
        if y < s.layout.height_subcells:
            if o.x - 1 >= 0:
                result.append(Vector2i(o.x - 1, y))
            # Source compares right X with HEIGHT.
            if o.x + 4 < s.layout.height_subcells:
                result.append(Vector2i(o.x + 4, y))
    return result

static func target(s, actor, task: String, mode: int = 0) -> bool:
    var grid = base_grid(s)
    if grid.is_empty() or actor.position.x < 0:
        return false
    grid = Geometry.prepare(grid, occupied(s, actor), Geometry.floor_value(s.config["store"]["source_floor"], actor.position) == 16, mode)
    var resting: bool = actor is StaffState and actor.source_state == 0
    var starts: Array = rest_points(s) if resting else [actor.position]
    for p in starts:
        if grid.get(p, -1) != -1:
            grid[p] = 0
    if task == "exit":
        for x in s.layout.width_subcells:
            for p in [Vector2i(x, 0), Vector2i(x, s.layout.height_subcells - 1)]:
                if grid[p] != -1:
                    grid[p] = 10000 if p.y == 0 else 10001
        for y in s.layout.height_subcells:
            for p in [Vector2i(0, y), Vector2i(s.layout.width_subcells - 1, y)]:
                if grid[p] != -1:
                    grid[p] = 10002 if p.x == 0 else 10003
    elif task == "clean":
        var rows: Array = s.config["store"]["source_floor"]
        for y in rows.size():
            for x in rows[y].size():
                var code = int(rows[y][x])
                if code >= 0 and code < 15 and code % 5:
                    for d in [Vector2i.ZERO, Vector2i.RIGHT, Vector2i.DOWN, Vector2i.ONE]:
                        var p: Vector2i = Vector2i(x, y) * 2 + d
                        if grid.get(p, -1) != -1:
                            grid[p] = 10001
        for other in s.staff.all_staff():
            if other == actor or other.source_state != 4:
                continue
            if s._program_rng.randi() % 100 + 1 > 2 * other.cleaning_skill or other.source_goal.x < 0:
                continue
            for d in [Vector2i.ZERO, Vector2i.RIGHT, Vector2i.DOWN, Vector2i.ONE]:
                var p: Vector2i = Vector2i(other.source_goal.x / 2, other.source_goal.y / 2) * 2 + d
                if grid.get(p, -1) >= 10000:
                    grid[p] = -2
    else:
        for f in s.layout.fixtures:
            var kind: int = s.program_fixture_kind(f)
            if kind < 0:
                continue
            var cat: int = int(s._recovery["fixture_records"][kind][0]) & 255
            var wanted = false
            if task == "rest":
                wanted = cat == 6
            elif task == "checkout":
                wanted = cat == 4
            else:
                for product in s.inventory.products.values():
                    if str(product.fixture_id) != str(f["id"]):
                        continue
                    if task == "refill":
                        wanted = product.stock_units * 100 / maxi(1, product.initial_stock_units) <= (actor.service_skill * 2 / 3 if s.config["store"].get("source_operating_state", 1) in [1, 2] else 99)
                    else:
                        var immediate = cat in [2, 3, 5]
                        wanted = product.stock_units > 0 and str(product.catalog_id) == actor.source_wanted and (actor.basket.is_empty() if immediate else actor.source_state != 4)
            if wanted:
                mark_fixture(s, grid, f, actor is StaffState)
        if task == "refill":
            for other in s.staff.all_staff():
                if other == actor or other.source_state != 2:
                    continue
                if s._program_rng.randi() % 100 + 1 > 2 * other.replenishment_skill or other.source_goal.x < 0:
                    continue
                var f = fixture(s, other.source_goal + Geometry.DIRECTIONS[other.source_goal_direction])
                if f.is_empty():
                    continue
                var mask = grid.duplicate()
                for p in mask:
                    if mask[p] >= 10000:
                        mask[p] = -2
                mark_fixture(s, mask, f, true)
                for p in mask:
                    if mask[p] >= 10000 and grid[p] >= 10000:
                        grid[p] = -2
    var found = {"result": 1}
    if resting:
        for p in starts:
            if grid.get(p, -1) >= 10000:
                found = {"result": 0, "goal": p, "direction": ((int(grid[p]) & 255) - 16) & 255, "grid": grid}
                grid[p] = 0
                break
    if found["result"] != 0:
        found = Geometry.search(grid, s.layout.width_subcells, s.layout.height_subcells, actor.position)
    actor.source_goal = OFF
    actor.route.clear()
    if found["result"] != 0:
        return false
    actor.source_goal = found["goal"]
    actor.source_goal_direction = found["direction"]
    var encoded = Geometry.encode(grid, actor.source_goal, actor.source_goal_direction)
    actor.route.assign(encoded["path"])
    actor.position = encoded["start"]
    actor.source_direction = encoded["direction"]
    return true

static func move(s, actor, ability: int, is_staff: bool) -> void:
    if actor.route.is_empty():
        actor.source_goal = OFF
        return
    var next: Vector2i = actor.route[0]
    var occ = occupied(s, actor)
    var direction: int = Geometry.DIRECTIONS.find(next - actor.position)
    if not occ.has(next):
        actor.position = actor.route.pop_front()
        actor.source_direction = direction if direction >= 0 else actor.source_direction
        if not actor.route.is_empty():
            var turn: int = Geometry.DIRECTIONS.find(actor.route[0] - actor.position)
            if turn >= 0:
                actor.source_direction = turn
        return
    var stepped = false
    if s._program_rng.randi() % 100 + 1 <= ability:
        for table in Geometry.SIDE_TABLES:
            var p: Vector2i = actor.position + Geometry.DIRECTIONS[table[maxi(0, direction)]]
            if Geometry.inside(p, s.layout.width_subcells, s.layout.height_subcells) and not occ.has(p):
                actor.position = p
                actor.source_direction = maxi(0, direction)
                stepped = true
                break
    if is_staff:
        actor.source_goal = OFF
    elif stepped:
        actor.route.clear()
    elif s._program_wait_at_checkout(actor, false):
        actor.basket.clear()
        change_state(actor, 5)
    elif s._program_rng.randi() % 100 + 1 <= ability:
        target(s, actor, "exit" if actor.source_state == 5 else ("checkout" if actor.source_state == 3 else "purchase"), 0)

static func change_state(p, state: int) -> void:
    p.source_state = state
    p.source_goal = OFF
    p.route.clear()
    if state in [3, 5]:
        p.phase = "waiting_checkout" if state == 3 else "leaving"
    elif state in [2, 4]:
        p.phase = "shopping"

static func admit(s, row: Dictionary, heads: int):
    s.customers._forget_old_done_customers()
    var id = "%s-%d" % [s.customers._id_prefix, s.customers._next_sequence]
    s.customers._next_sequence += 1
    var p = preload("res://scripts/domain/customer_state.gd").new({"id": id})
    p.phase = "to_shelf"
    p.source_native = true
    p.position = OFF
    p.visit = row.duplicate(true)
    p.group_size = heads
    p.type_id = str(row["type"])
    p.budget_left = int(row["budget_yen"])
    p.source_wanted = str(row["primary"])
    p.source_candidates = row["extras"].slice(0, 3).duplicate()
    p.source_candidate_index = 0
    p.set_meta("checkout_patience", int(row.get("stamina", 100)))
    s.customers.customers[id] = p
    s.customers.active_customer_id = id
    var tables: Dictionary = s.source_actor_tables
    if not tables.is_empty():
        var profile: int = s._program_demand.rows.find(row)
        # ProgramDemand rows retain original profile index in 'source_index'.
        profile = int(row.get("source_index", profile))
        var group: int = int(tables["groups"][clampi(profile, 0, 143)])
        p.source_image = int(tables["appearances"][group * 4 + s._program_rng.randi() % 4])
    s._record_customer_entered(p)
    s._observe_chain_visitor_milestone(heads)
    return p

static func entry(s, p) -> void:
    var side: int = s._program_rng.randi() % 4
    var w: int = s.layout.width_subcells
    var h: int = s.layout.height_subcells
    var points: Array[Vector2i] = []
    match side:
        0:
            for x in w: points.append(Vector2i(x, 0))
        1:
            for y in h: points.append(Vector2i(w - 1, y))
        2:
            for x in range(w - 1, -1, -1): points.append(Vector2i(x, h - 1))
        3:
            for y in range(h - 1, -1, -1): points.append(Vector2i(0, y))
    var occ = occupied(s, p)
    var grid = base_grid(s)
    for pos in points:
        if not occ.has(pos) and grid.get(pos, -1) == -2:
            p.position = pos
            p.source_direction = [1, 2, 0, 3][side]
            p.source_deadline = clock(s) + int(p.visit.get("duration_minutes", 120))
            change_state(p, 2)
            return

static func customer(s, p) -> void:
    if not p.source_native:
        s._advance_customer(p)
        return
    if p.source_state == 1:
        entry(s, p)
        return
    if p.source_goal.x < 0:
        if p.source_state in [2, 4]:
            if p.source_wanted.is_empty():
                if p.source_deadline < clock(s) or p.source_candidate_index >= 3:
                    change_state(p, 5 if p.source_state == 4 else 3)
                    return
                p.source_wanted = str(p.source_candidates[p.source_candidate_index]) if p.source_candidate_index < p.source_candidates.size() else ""
                p.source_candidate_index += 1
                if p.source_wanted.is_empty():
                    return
                if not s._program_demand.wants_extra(p.source_wanted, s.month_count - 1, int(p.visit.get("focus", 0)), s._program_rng):
                    p.source_wanted = ""
                    return
            if not target(s, p, "purchase", 1):
                s.survey_missing[p.source_wanted] = int(s.survey_missing.get(p.source_wanted, 0)) + p.group_size
                p.source_wanted = ""
            return
        if p.source_state == 3 and p.basket.is_empty():
            p.source_wanted = ""
            p.source_candidate_index = 0
            change_state(p, 4)
            return
        if not target(s, p, "exit" if p.source_state == 5 else "checkout", 1) and p.source_state == 3:
            p.set_meta("checkout_patience", 0)
            s._program_wait_at_checkout(p, false)
            p.basket.clear()
            change_state(p, 5)
        return
    if p.position != p.source_goal:
        move(s, p, int(p.visit.get("quickness", 100)), false)
        return
    if p.source_direction != p.source_goal_direction:
        p.source_direction = p.source_goal_direction
        return
    if p.source_state == 5:
        p.phase = "done"
        p.source_state = 0
        p.position = OFF
        if str(p.visit.get("arrival", "")) == "自動車":
            s._parking_used = maxi(0, s._parking_used - p.group_size)
        s._record_event("customer_exited", {"customer_id": p.customer_id})
        return
    if p.source_state == 3:
        service(s, p)
        return
    var f = facing_fixture(s, p)
    var product_id = ""
    for product in s.inventory.products.values():
        if str(product.fixture_id) == str(f.get("id", "")) and str(product.catalog_id) == p.source_wanted:
            product_id = str(product.product_id)
            break
    if product_id.is_empty():
        p.source_wanted = ""
        p.source_goal = OFF
        return
    var cost: int = s._apply_price_policy(s.inventory.get_product(product_id).sale_price_yen, p.source_wanted)
    if p.source_wanted == str(s.config["source_catalog"]["product_ids"][7]):
        if int(s._store_values()["security"]) < 100 - int(p.visit.get("manners", 100)) and p.source_deadline >= clock(s):
            return
    if p.budget_left >= cost:
        if s._program_rng.randi() % 100 + 1 > int(p.visit.get("quickness", 100)):
            return
        var line: Dictionary = s.inventory.try_take(product_id, p.group_size)
        if not line.is_empty():
            line["unit_price_yen"] = cost
            p.budget_left -= cost
            if s._source_immediate_sale(product_id):
                s._settle_source_immediate(p, line)
            else:
                p.basket.append(line)
            s._record_event("product_picked", {"customer_id": p.customer_id, "product_id": product_id})
    elif s._source_try_theft(p, product_id):
        change_state(p, 5)
        return
    p.source_wanted = ""
    p.source_goal = OFF

static func service(s, p) -> void:
    var f = facing_fixture(s, p)
    for worker in s.staff.all_staff():
        if worker.source_state != 1 or worker.source_served:
            continue
        if facing_fixture(s, worker).get("id", "") != f.get("id", "missing"):
            continue
        worker.source_served = true
        if Rules.checkout_ready(worker.register_skill, int(p.visit.get("quickness", 100)), s._program_rng):
            s._grow_staff(worker, "checkout")
            var record: Dictionary = s.economy.settle_basket(p.customer_id, s.minute_of_day, p.basket)
            p.mark_settled(record)
            s._store_sales_yen += int(record["total_yen"])
            for line in p.basket:
                var prod = s.inventory.get_product(str(line["product_id"]))
                s.survey_bought[prod.catalog_id] = int(s.survey_bought.get(prod.catalog_id, 0)) + int(line["quantity"])
                s._sold_counts[prod.catalog_id] = int(s._sold_counts.get(prod.catalog_id, 0)) + int(line["quantity"])
            p.basket.clear()
            worker.checkouts_done += 1
            s._record_event("checkout_completed", {"customer_id": p.customer_id, "staff_id": worker.staff_id, "transaction_id": p.settled_transaction_id})
            p.source_wanted = ""
            p.source_candidate_index = 0
            change_state(p, 4)
            return
        break
    if s._program_wait_at_checkout(p, false):
        p.basket.clear()
        change_state(p, 5)

static func relevant(s) -> bool:
    for p in s.customers.active_customers():
        if p.source_state >= 2 and p.position.x >= 0 and Geometry.floor_value(s.config["store"]["source_floor"], p.position) != 16:
            return true
    return false

static func gate(s, worker) -> bool:
    var active = 0
    var ability = 0
    var width = 0
    for f in s.layout.fixtures:
        if str(f["kind"]) == "checkout":
            var kind: int = s.program_fixture_kind(f)
            width = int(s._recovery["fixture_records"][kind][9])
    for p in s.staff.all_staff():
        if p.source_state == 1:
            active += 1
            if p != worker:
                ability += p.register_skill
    if active <= 0:
        return true
    if active >= width - 1:
        return false
    return s._program_rng.randi() % 100 + 1 > ability * 2

static func choose_work(s, p) -> bool:
    if p.stamina > 0:
        if gate(s, p) and clock(s) % 100 >= 100 - p.service_skill and relevant(s) and target(s, p, "checkout"):
            p.source_state = 1
            p.state = "checkout"
            p.rest_phase = ""
            return true
        if target(s, p, "refill"):
            p.source_state = 2
            p.state = "to_restock"
            p.rest_phase = ""
            return true
        if clock(s) % 100 >= 100 - p.service_skill and target(s, p, "clean"):
            p.source_state = 4
            p.state = "cleaning"
            p.rest_phase = ""
            return true
    if p.source_state == 0:
        return false
    target(s, p, "rest")
    p.source_state = 3
    p.state = "idle"
    p.rest_phase = "to_break_room"
    return true

static func enter_rest(s, p, slot: int) -> void:
    p.source_state = 0
    p.position = rest_origin(s) + REST_OFFSETS[clampi(slot, 0, 2)]
    p.source_direction = 1
    p.source_goal = OFF
    p.route.clear()
    p.state = "idle"
    p.rest_phase = "resting"

static func employee(s, p, slot: int) -> void:
    if p.source_state < 0:
        enter_rest(s, p, slot)
    if p.source_state == 0:
        if p.stamina < p.stamina_max:
            var f = fixture(s, p.position)
            p.stamina = Rules.resting_energy(p.stamina, p.stamina_max, s.program_fixture_kind(f) == 49, s._program_rng)
        elif (clock(s) / 2) % 3 == slot:
            choose_work(s, p)
        return
    p.stamina = Rules.working_energy(p.stamina, s._program_rng)
    if p.stamina <= 0 and p.source_state != 3:
        p.source_goal = OFF
    if p.source_goal.x < 0:
        choose_work(s, p)
        return
    if p.position != p.source_goal:
        move(s, p, int(s._staff_candidate_catalog.get(p.candidate_id, {}).get("agility", 0)), true)
        return
    if p.source_direction != p.source_goal_direction:
        p.source_direction = p.source_goal_direction
        return
    match p.source_state:
        1:
            if not relevant(s):
                p.source_goal = OFF
        2:
            var f = facing_fixture(s, p)
            for product in s.inventory.products.values():
                if str(product.fixture_id) != str(f.get("id", "")):
                    continue
                p.restock_target_product_id = str(product.product_id)
                s._complete_restock(p)
                if product.stock_units >= product.initial_stock_units:
                    p.source_goal = OFF
                else:
                    p.state = "restocking"
                return
            p.source_goal = OFF
        3:
            enter_rest(s, p, slot)
        4:
            if clock(s) & 7 == 0:
                p.source_direction = [1, 0, 2, 3][p.source_direction]
                p.source_goal_direction = p.source_direction
            var x: int = p.position.x / 2
            var y: int = p.position.y / 2
            var rows: Array = s.config["store"]["source_floor"]
            var before = int(rows[y][x])
            rows[y][x] = preload("res://scripts/domain/program_operations.gd").clean_tile(before, p.cleaning_skill, s._program_rng)
            if int(rows[y][x]) % 5 == 0:
                s._grow_staff(p, "clean")
                p.source_goal = OFF

static func operating_state(s) -> void:
    var state = int(s.config["store"].get("source_operating_state", 1))
    var previous = state
    if state in [0, 2]:
        if s.is_open_now():
            state = 3
    elif not s.is_open_now():
        state = 2
    if state == 3:
        state = 1
    if state == 2 and s.customers.all_settled():
        state = 0
    s.config["store"]["source_operating_state"] = state
    if state in [0, 1] and state != previous:
        var codes = {28: 29, 30: 31, 32: 33, 34: 35} if state == 0 else {29: 28, 31: 30, 33: 32, 35: 34}
        for row in s.config["store"]["source_floor"]:
            for i in row.size():
                row[i] = codes.get(int(row[i]), row[i])
        s.layout.source_work_grid.clear()

static func step(s) -> void:
    operating_state(s)
    if base_grid(s).is_empty():
        return
    for p in s.staff.all_staff():
        p.source_served = false
    s._admit_program_group()
    for p in s.customers.active_customers():
        customer(s, p)
    var people: Array = s.staff.all_staff()
    for i in range(people.size() - 1, -1, -1):
        var slot = int(str(people[i].staff_id).get_slice("-", 1)) - 1
        employee(s, people[i], slot)
    s._step_source_floor_wear()
    if s.minute_of_day % 2 == 0:
        s._step_manager_reports()
        s._step_incidents()
