extends SceneTree

const Sim = preload("res://scripts/vertical_slice_simulation.gd")
const Start = preload("res://scripts/domain/guide_starting_store.gd")
const Customer = preload("res://scripts/domain/customer_state.gd")
const People = preload("res://scripts/domain/program_people.gd")

func setup():
    var base: Dictionary = JSON.parse_string(FileAccess.get_file_as_string("res://data/vertical_slice.json"))
    var s = Sim.new(Start.apply(base))
    assert(s.try_buy_store_site(Vector2i(26, 12)))
    return s

func _initialize() -> void:
    var s = setup()
    var workers = s.staff.all_staff()
    for i in workers.size():
        People.enter_rest(s, workers[i], i)
    var p = Customer.new({"id": "ejected-at-counter"})
    p.source_native = true
    p.source_state = 3
    p.phase = "waiting_checkout"
    p.visit = {"quickness": 100}
    p.position = s.layout.entry
    p.basket.append({"product_id": s.inventory.product_order[0], "quantity": 1, "unit_price_yen": 100})
    s.customers.customers[p.customer_id] = p
    assert(People.target(s, p, "checkout", 1))
    p.position = p.source_goal
    p.source_direction = p.source_goal_direction
    p.route.clear()
    var cashier = s.staff.members["staff-1"]
    People.enter_rest(s, cashier, 0)
    assert(People.target(s, cashier, "checkout"))
    cashier.position = cashier.source_goal
    cashier.source_direction = cashier.source_goal_direction
    cashier.source_state = 1
    cashier.register_skill = 100
    var cash: int = s.economy.cash_yen
    var sales: int = s.economy.completed_sales
    assert(s.try_eject_customer(p.customer_id))
    assert(p.source_state == 5 and p.phase == "leaving" and p.source_goal.x < 0 and p.route.is_empty())
    assert(not s.try_eject_customer(p.customer_id))
    var clone = setup()
    assert(clone.load_state(JSON.parse_string(JSON.stringify(s.save_state()))))
    var q = clone.customers.customers[p.customer_id]
    assert(q.source_state == 5)
    for i in 200:
        if p.source_state == 0:
            break
        People.customer(s, p)
        People.customer(clone, q)
        assert(s.economy.cash_yen == cash and clone.economy.cash_yen == cash)
        assert(s.economy.completed_sales == sales and clone.economy.completed_sales == sales)
        assert(s._program_rng.seed == clone._program_rng.seed and p.position == q.position)
    assert(p.phase == "done" and q.phase == "done")
    assert(p.basket_total_yen() == 100 and q.basket_total_yen() == 100)
    assert(p.settled_transaction_id.is_empty() and q.settled_transaction_id.is_empty())
    print("EJECTION_CONSISTENCY_PASS native cashier-ready ejection, immediate checkout invalidation, unpaid exit, JSON continuation and no stale settlement")
    quit()
