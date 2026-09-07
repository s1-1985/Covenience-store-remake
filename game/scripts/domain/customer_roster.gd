class_name CustomerRoster
extends RefCounted

const CustomerStateScript := preload("res://scripts/domain/customer_state.gd")

var customers: Dictionary = {}
var active_customer_id := ""
var _id_prefix: String
var _visit_plan_product_ids: Array[String] = []
var _next_sequence := 1


func _init(customer_config: Dictionary) -> void:
    _id_prefix = str(customer_config["id_prefix"])
    _visit_plan_product_ids.assign(customer_config["visit_plan_product_ids"])
    assert(not _id_prefix.is_empty() and not _visit_plan_product_ids.is_empty())


func reset() -> void:
    customers.clear()
    active_customer_id = ""
    _next_sequence = 1


func can_admit() -> bool:
    return active_customer_id.is_empty() or active().phase == "done"


func admit(entry: Vector2i, initial_route: Array[Vector2i]):
    assert(can_admit())
    var customer_id := "%s-%d" % [_id_prefix, _next_sequence]
    _next_sequence += 1
    var customer = CustomerStateScript.new({"id": customer_id})
    customer.begin(entry, initial_route, _visit_plan_product_ids)
    customers[customer_id] = customer
    active_customer_id = customer_id
    return customer


func active():
    assert(not active_customer_id.is_empty() and customers.has(active_customer_id))
    return customers[active_customer_id]


func completed_count() -> int:
    var total := 0
    for customer in customers.values():
        if customer.phase == "done":
            total += 1
    return total


func all_customers() -> Array:
    return customers.values()
