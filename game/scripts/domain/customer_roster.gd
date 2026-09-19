class_name CustomerRoster
extends RefCounted

const CustomerStateScript := preload("res://scripts/domain/customer_state.gd")

var customers: Dictionary = {}
var active_customer_id := ""
var _id_prefix: String
var _visit_plan_product_ids: Array[String] = []
var _next_sequence := 1
# REMAKE_BALANCED_DEFAULT (task #36): the strategy guide/wiki research never
# states how many shoppers the original title allows in a store at once, so
# this cap is this project's own scope decision (not a recovered original
# limit), configured per scenario in vertical_slice.json rather than
# hardcoded here.
var _max_concurrent_customers: int


func _init(customer_config: Dictionary) -> void:
    _id_prefix = str(customer_config["id_prefix"])
    _visit_plan_product_ids.assign(customer_config["visit_plan_product_ids"])
    _max_concurrent_customers = int(customer_config["max_concurrent_customers"])
    assert(not _id_prefix.is_empty() and not _visit_plan_product_ids.is_empty())
    assert(_max_concurrent_customers >= 1)


func reset() -> void:
    customers.clear()
    active_customer_id = ""
    _next_sequence = 1


func can_admit() -> bool:
    return active_customer_id.is_empty() or active().phase == "done"


# Room for another concurrently active customer (task #36), independent of
# the single most-recently-admitted customer can_admit() tracks. Used by the
# explicit/observed admission path (start_explicit_customer -> admit_explicit)
# so more than one customer can be in the store at once; the default
# demand-driven flow (start_next_customer/demand_admit_if_due -> admit_default)
# deliberately keeps using can_admit() above and stays exactly as
# single-customer as before this task.
func can_admit_concurrent() -> bool:
    return _active_non_done_count() < _max_concurrent_customers


# True once every admitted customer has reached phase "done" (or none have
# been admitted yet). Needed once can_admit_concurrent() makes more than one
# customer active at a time: can_admit() alone only reflects the single
# most-recently-admitted customer, so it can wrongly read as "no visit in
# progress" while an earlier-admitted customer is still active. Callers that
# need "no visit in progress anywhere, safe to edit the store layout" must
# use this instead of can_admit().
func all_settled() -> bool:
    return _active_non_done_count() == 0


func _active_non_done_count() -> int:
    var count := 0
    for customer in customers.values():
        if customer.phase != "done":
            count += 1
    return count


func default_plan() -> Array[String]:
    return _visit_plan_product_ids.duplicate()


# Task #55: visit_plan_product_ids is caller-supplied (the caller is
# expected to start from default_plan() and may extend it, e.g. with
# incidental-want products) rather than always reusing
# _visit_plan_product_ids internally, so "default" now describes only how
# the customer_id/entry route are derived, not that the plan itself is
# fixed.
func admit_default(entry: Vector2i, initial_route: Array[Vector2i], visit_plan_product_ids: Array[String]):
    assert(can_admit_concurrent())
    var customer_id := "%s-%d" % [_id_prefix, _next_sequence]
    _next_sequence += 1
    return admit_explicit(customer_id, entry, initial_route, visit_plan_product_ids)


func admit_explicit(
    customer_id: String,
    entry: Vector2i,
    initial_route: Array[Vector2i],
    visit_plan_product_ids: Array[String]
):
    assert(can_admit_concurrent())
    assert(not customer_id.is_empty() and not customers.has(customer_id))
    assert(not visit_plan_product_ids.is_empty())
    var customer = CustomerStateScript.new({"id": customer_id})
    customer.begin(entry, initial_route, visit_plan_product_ids)
    customers[customer_id] = customer
    active_customer_id = customer_id
    return customer


func active():
    assert(not active_customer_id.is_empty() and customers.has(active_customer_id))
    return customers[active_customer_id]


func customer(customer_id: String):
    return customers[customer_id]


# All customers still in progress (any phase other than "done"), in
# admission order. Used by the per-tick simulation loop and by rendering, so
# every concurrently admitted customer is advanced/drawn, not only the
# single most-recently-admitted one active() tracks.
func active_customers() -> Array:
    var result: Array = []
    for customer_state in customers.values():
        if customer_state.phase != "done":
            result.append(customer_state)
    return result


func completed_count() -> int:
    var total := 0
    for customer in customers.values():
        if customer.phase == "done":
            total += 1
    return total


func all_customers() -> Array:
    return customers.values()
