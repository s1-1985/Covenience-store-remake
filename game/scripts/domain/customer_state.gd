class_name CustomerState
extends RefCounted

var customer_id: String
var position := Vector2i.ZERO
var phase := "done"
var basket: Array[Dictionary] = []
var planned_product_ids: Array[String] = []
var plan_index := 0
var shopping_ticks_remaining := 0
var checkout_ticks_remaining := 0
var route: Array[Vector2i] = []
var settled_transaction_id := ""
var settled_total_yen := 0


func _init(customer_config: Dictionary) -> void:
    customer_id = str(customer_config["id"])
    assert(not customer_id.is_empty())


func begin(
    entry: Vector2i,
    initial_route: Array[Vector2i],
    visit_plan_product_ids: Array[String]
) -> void:
    position = entry
    phase = "to_shelf"
    basket.clear()
    planned_product_ids = visit_plan_product_ids.duplicate()
    plan_index = 0
    shopping_ticks_remaining = 0
    checkout_ticks_remaining = 0
    route = initial_route
    settled_transaction_id = ""
    settled_total_yen = 0


func current_product_id() -> String:
    if plan_index >= planned_product_ids.size():
        return ""
    return planned_product_ids[plan_index]


func advance_plan() -> void:
    plan_index += 1


func add_basket_line(line: Dictionary) -> void:
    assert(not line.is_empty() and int(line["quantity"]) > 0)
    basket.append(line.duplicate(true))


func basket_total_yen() -> int:
    var total := 0
    for line in basket:
        total += int(line["quantity"]) * int(line["unit_price_yen"])
    return total


func mark_settled(record: Dictionary) -> void:
    assert(settled_transaction_id.is_empty())
    assert(record["customer_id"] == customer_id)
    assert(int(record["total_yen"]) == basket_total_yen())
    settled_transaction_id = str(record["transaction_id"])
    settled_total_yen = int(record["total_yen"])


func move_along_route(next_phase: String) -> bool:
    if not route.is_empty():
        position = route.pop_front()
    if route.is_empty():
        phase = next_phase
        return true
    return false
