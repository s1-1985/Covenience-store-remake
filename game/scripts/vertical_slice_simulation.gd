class_name VerticalSliceSimulation
extends RefCounted

const StoreLayoutScript := preload("res://scripts/domain/store_layout.gd")
const InventoryCatalogScript := preload("res://scripts/domain/inventory_catalog.gd")
const EconomyStateScript := preload("res://scripts/domain/economy_state.gd")
const CustomerRosterScript := preload("res://scripts/domain/customer_roster.gd")
const StaffRosterScript := preload("res://scripts/domain/staff_roster.gd")
const RuntimeEventLogScript := preload("res://scripts/domain/runtime_event_log.gd")
const DemandPolicyScript := preload("res://scripts/domain/demand_policy.gd")
const TownStateScript := preload("res://scripts/domain/town_state.gd")
const LandValuePolicyScript := preload("res://scripts/domain/land_value_policy.gd")
const StoreRatingScript := preload("res://scripts/domain/store_rating.gd")
const StoreValueScript := preload("res://scripts/domain/store_value.gd")
const CustomerShareScript := preload("res://scripts/domain/customer_share.gd")
const ChainVisitorMilestoneScript := preload("res://scripts/domain/chain_visitor_milestone.gd")
const StoreEventsScript := preload("res://scripts/domain/store_events.gd")
const CheckoutTimingScript := preload("res://scripts/domain/checkout_timing.gd")
const RestockTimingScript := preload("res://scripts/domain/restock_timing.gd")

# CONFIRMED_OFFICIAL, not a guess: the strategy guide states this multiplier
# directly ("1月=4日間×8"; reference_sim/conveni_sim/month_aggregation.py
# mirrors the same citation). What the guide does not state is how each
# representative day's own net result is computed internally; this client,
# like month_aggregation.py, only turns the already-tracked cash change
# across REPRESENTATIVE_DAYS_PER_MONTH days into the displayed monthly figure.
const REPRESENTATIVE_DAYS_PER_MONTH := 4
const MONTH_MULTIPLIER := 8

# CONFIRMED, not a guess:
# - bankruptcy: PS footage and an SS play record support game over when cash
#   is negative at a day/month boundary
#   (reference_sim/conveni_sim/month_boundary.py's
#   MonthBoundaryBankruptcyPolicy.bankrupt_when_negative=True). No zero-cash
#   sample is known, so cash == 0 is explicitly left unresolved there
#   (bankrupt_when_zero=None) -- this client leaves it unresolved too, and
#   does NOT treat it as bankruptcy.
# - time limit: the guide's own second game-over path, 100 years without
#   meeting the scenario's clear condition
#   (reference_sim/conveni_sim/store_events.scenario_time_limit_exceeded /
#   GAME_OVER_YEAR_LIMIT). `clear_condition_met` defaults to false and is
#   set true once `player_store_count` reaches
#   PLAYER_STORE_COUNT_SCENARIO_TARGET (see that constant below);
#   MONTHS_PER_YEAR mirrors reference_sim/conveni_sim/observations.py.
const GAME_OVER_YEAR_LIMIT := 100
const MONTHS_PER_YEAR := 12

# CONFIRMED_COMMUNITY floor, not a guess: the original game's Wiki records a
# minimum land price of 20,000,000 yen
# (docs/research/store-unlock-and-daily-pricing-delta-2026-09-05.md section
# 5). reference_sim/conveni_sim/remake_land_value.py takes
# base_land_price_yen as a caller-supplied parameter rather than hardcoding
# it, so this constant -- picking the confirmed floor as the base for the
# player's own store's land -- is this client's own choice, not a ported
# value.
const BASE_LAND_PRICE_YEN := 20_000_000

# PROVISIONAL, not CONFIRMED_OFFICIAL: PROJECT_MEMORY.md section 14 records
# "intermediate: reach 10 company stores" as a scenario clear condition
# from community sources, explicitly flagged there as unverified
# ("must be verified against manual/gameplay before implementation"). This
# is the only concrete numeric scenario-clear target this project has
# found for chain expansion, so it is used as a playable placeholder --
# expected to be retuned or replaced if better evidence surfaces, exactly
# like this client's other REMAKE_BALANCED_DEFAULT placeholders, but kept
# under its own weaker PROVISIONAL tag since even the community source
# itself is unconfirmed here.
const PLAYER_STORE_COUNT_SCENARIO_TARGET := 10

var config: Dictionary
var layout
var inventory
var economy
var customers
var staff
var event_log
var demand
var _demand_rng: RandomNumberGenerator

var minute_of_day: int
var day_count: int
var month_count: int
var last_event := "store opened"
var _checkout_interaction := Vector2i.ZERO
var _shopping_ticks: int
var _checkout_ticks: int
var _step_game_minutes: int
var _restock_ticks: int
var _restock_trigger_stock_units_at_or_below: int
var _restock_task_enabled: bool
var _days_completed_this_month: int
var _cash_at_month_start: int
var _revenue_at_month_start: int
var is_game_over: bool
var game_over_reason: String
var clear_condition_met: bool
var _fixture_catalog: Dictionary = {}
var _sample_layout_catalog: Dictionary = {}
var _permit_catalog: Dictionary = {}
var _product_catalog: Dictionary = {}
var _permits_held: Dictionary = {}
var _promotion_catalog: Dictionary = {}
var _promotions_used_this_month: Dictionary = {}
var _scheduled_promotions: Array[Dictionary] = []
var popularity: int
var town
var _land_value_policy
var internal_rating_value: int
var star_rating: int
var _store_rating
var _store_value
var _customer_share
var _store_size_tier: String
var player_store_count: int
var _chain_visitor_milestone
var _store_events
var _checkout_timing
var _restock_timing
# FIFO order in which customers who have finished shopping are waiting for
# the single checkout fixture's one staff-service slot (task #36, concurrent
# customers). Serving strictly in arrival order is this project's own
# REMAKE_BALANCED_DEFAULT choice: reference_sim's CheckoutStationRuntime
# deliberately leaves service order to an explicit policy rather than
# forcing FIFO, citing first-title FAQ evidence that a later-arriving
# customer can sometimes be served first, so this is not a claim about the
# original game's tie-break rule.
var _checkout_queue: Array[String] = []


func _init(source_config: Dictionary) -> void:
    config = source_config.duplicate(true)
    _require_config()
    for entry in config["fixture_catalog"]:
        _fixture_catalog[str(entry["catalog_id"])] = entry
    for entry in config["permits"]:
        _permit_catalog[str(entry["permit_id"])] = entry
    for entry in config["product_catalog"]:
        _product_catalog[str(entry["catalog_id"])] = entry
    for entry in config["promotions"]:
        _promotion_catalog[str(entry["promotion_id"])] = entry
    for entry in config["sample_layouts"]:
        _sample_layout_catalog[str(entry["sample_id"])] = entry
    layout = StoreLayoutScript.new(config["store"], config["fixtures"])
    inventory = InventoryCatalogScript.new(config["products"])
    economy = EconomyStateScript.new(config["economy"])
    customers = CustomerRosterScript.new(config["customer"])
    staff = StaffRosterScript.new(config["staff"])
    event_log = RuntimeEventLogScript.new()
    _demand_rng = RandomNumberGenerator.new()
    demand = DemandPolicyScript.new(config["demand"], _demand_rng)
    town = TownStateScript.new(config["town"])
    _land_value_policy = LandValuePolicyScript.new()
    # The dilution formula counts competing/rival stores, not the player's
    # own store, so store_count_including_rivals is reduced by one (never
    # below zero) before being applied.
    demand.rival_store_count = max(0, town.store_count_including_rivals - 1)
    _store_rating = StoreRatingScript.new()
    _store_value = StoreValueScript.new()
    _customer_share = CustomerShareScript.new()
    _store_size_tier = str(config["store"]["size_tier"])
    assert(_store_value.STORE_SIZE_VALUE_MULTIPLIER.has(_store_size_tier))
    _store_events = StoreEventsScript.new()
    _checkout_timing = CheckoutTimingScript.new()
    _restock_timing = RestockTimingScript.new()
    var simulation: Dictionary = config["simulation"]
    _checkout_interaction = layout.interaction_for_fixture(
        str(simulation["checkout_fixture_id"]),
        "checkout"
    )
    _shopping_ticks = int(simulation["shopping_ticks"])
    _checkout_ticks = int(simulation["checkout_ticks"])
    _step_game_minutes = int(simulation["step_game_minutes"])
    _restock_ticks = int(simulation["restock_ticks"])
    _restock_trigger_stock_units_at_or_below = int(
        simulation["restock_trigger_stock_units_at_or_below"]
    )
    _restock_task_enabled = bool(simulation["restock_task_enabled"])
    assert(_shopping_ticks > 0 and _checkout_ticks > 0 and _step_game_minutes > 0)
    assert(_restock_ticks > 0 and _restock_trigger_stock_units_at_or_below >= 0)
    assert(float(simulation["tick_seconds"]) > 0.0)
    for staff_member in staff.all_staff():
        assert(layout.is_walkable(staff_member.position))
    assert(_required_routes_are_reachable())
    reset()


func reset() -> void:
    minute_of_day = int(config["simulation"]["start_minute_of_day"])
    day_count = 0
    month_count = 0
    _days_completed_this_month = 0
    layout.reset()
    inventory.reset()
    economy.reset()
    customers.reset()
    staff.reset()
    event_log.reset()
    _checkout_queue.clear()
    _cash_at_month_start = economy.cash_yen
    _revenue_at_month_start = economy.recorded_revenue_yen()
    is_game_over = false
    game_over_reason = ""
    clear_condition_met = false
    _permits_held.clear()
    _promotions_used_this_month.clear()
    _scheduled_promotions.clear()
    popularity = 0
    # No confirmed starting evaluation for a brand-new store exists (the
    # guide never states one; store_evaluation.py's own
    # internal_rating_value likewise starts unknown until a caller sets
    # it), so 0 (the lowest tier, 0-19 -> 0 stars) is used as the most
    # natural REMAKE_BALANCED_DEFAULT starting point, matching the
    # precedent already set for `popularity`.
    internal_rating_value = 0
    star_rating = _store_rating.star_rank_for_internal_value(internal_rating_value)
    # This playable vertical slice is itself the player's first store, so
    # the chain always starts at 1, not 0.
    player_store_count = 1
    _chain_visitor_milestone = ChainVisitorMilestoneScript.new()
    _demand_rng.seed = int(config["demand"]["rng_seed"])
    _refresh_interactions()
    _start_default_customer()


func start_next_customer() -> bool:
    if is_game_over or not customers.can_admit_concurrent():
        return false
    _start_default_customer()
    return true


func start_explicit_customer(customer_id: String, product_ids: Array[String]) -> bool:
    if is_game_over or not customers.can_admit_concurrent() or customer_id.is_empty():
        return false
    if customers.customers.has(customer_id) or not _product_plan_is_valid(product_ids):
        return false
    var first_interaction := _product_interaction(product_ids[0])
    var customer = customers.admit_explicit(
        customer_id,
        layout.entry,
        layout.find_path(layout.entry, first_interaction),
        product_ids
    )
    _record_customer_entered(customer)
    return true


func demand_admit_if_due() -> bool:
    if is_game_over or not customers.can_admit():
        return false
    if not demand.customer_arrives_this_minute():
        return false
    _start_default_customer()
    return true


func tick_idle_for_demand() -> bool:
    if is_game_over:
        return false
    _advance_minute_of_day()
    _step_restock_tasks()
    return demand_admit_if_due()


func apply_explicit_restock(
    product_id: String,
    staff_id: String,
    quantity: int,
    total_cost_yen: int
) -> bool:
    if is_game_over or not customers.all_settled() or quantity <= 0 or total_cost_yen < 0:
        return false
    if not inventory.products.has(product_id) or not staff.members.has(staff_id):
        return false
    var resulting_stock: int = inventory.add_explicit_units(product_id, quantity)
    var expense: Dictionary = economy.record_explicit_expense(
        "inventory_restock",
        minute_of_day,
        total_cost_yen,
        {"product_id": product_id, "quantity": quantity, "staff_id": staff_id}
    )
    _record_event("inventory_restock", {
        "product_id": product_id,
        "quantity": quantity,
        "staff_id": staff_id,
        "expense_id": expense["expense_id"],
        "resulting_stock_units": resulting_stock,
    })
    return true


func try_purchase_fixture(
    catalog_id: String,
    instance_id: String,
    origin_subcell: Vector2i,
    interaction_subcell: Vector2i
) -> bool:
    if is_game_over or not customers.all_settled() or _any_restock_task_active():
        return false
    if instance_id.is_empty() or layout.fixtures_by_id.has(instance_id):
        return false
    if not _fixture_catalog.has(catalog_id):
        return false
    var catalog_entry: Dictionary = _fixture_catalog[catalog_id]
    var required_permit_id := str(catalog_entry.get("required_permit_id", ""))
    if not required_permit_id.is_empty() and not has_permit(required_permit_id):
        return false
    var price_yen: int = int(catalog_entry["purchase_price_yen"])
    if economy.cash_yen < price_yen:
        return false
    var catalog_footprint_tiles: Array = catalog_entry["footprint_tiles"]
    var fixture_config := {
        "id": instance_id,
        "kind": str(catalog_entry["kind"]),
        "catalog_id": catalog_id,
        "rotation_quarter_turns": 0,
        "origin_subcell": [origin_subcell.x, origin_subcell.y],
        "footprint_tiles": catalog_footprint_tiles.duplicate(),
        "interaction_subcell": [interaction_subcell.x, interaction_subcell.y],
    }
    var previous_fixtures: Array = layout.fixture_snapshot()
    if not layout.try_add_fixture(fixture_config):
        return false
    _refresh_interactions()
    if not _required_routes_are_reachable() or not _all_staff_are_walkable():
        layout.restore_fixture_snapshot(previous_fixtures)
        _refresh_interactions()
        return false
    var expense: Dictionary = economy.record_explicit_expense(
        "fixture_purchase",
        minute_of_day,
        price_yen,
        {"catalog_id": catalog_id, "instance_id": instance_id}
    )
    _record_event("fixture_purchased", {
        "catalog_id": catalog_id,
        "instance_id": instance_id,
        "expense_id": expense["expense_id"],
        "origin_subcell": [origin_subcell.x, origin_subcell.y],
    })
    return true


func has_permit(permit_id: String) -> bool:
    return _permits_held.has(permit_id)


func try_purchase_permit(permit_id: String) -> bool:
    if is_game_over or not customers.all_settled():
        return false
    if has_permit(permit_id) or not _permit_catalog.has(permit_id):
        return false
    var fee_yen: int = int(_permit_catalog[permit_id]["fee_yen"])
    if economy.cash_yen < fee_yen:
        return false
    var expense: Dictionary = economy.record_explicit_expense(
        "permit_purchase",
        minute_of_day,
        fee_yen,
        {"permit_id": permit_id}
    )
    _permits_held[permit_id] = true
    _record_event("permit_purchased", {
        "permit_id": permit_id,
        "expense_id": expense["expense_id"],
    })
    return true


func try_procure_product(catalog_id: String, instance_id: String, fixture_id: String) -> bool:
    if is_game_over or not customers.all_settled():
        return false
    if instance_id.is_empty() or inventory.products.has(instance_id):
        return false
    if not _product_catalog.has(catalog_id):
        return false
    if not layout.fixtures_by_id.has(fixture_id):
        return false
    var catalog_entry: Dictionary = _product_catalog[catalog_id]
    var required_permit_id := str(catalog_entry.get("required_permit_id", ""))
    if not required_permit_id.is_empty() and not has_permit(required_permit_id):
        return false
    # Task #45: a fixture only carries compatible_product_categories/capacity
    # when it was purchased from fixture_catalog (has its own catalog_id) and
    # that catalog entry actually defines them (every shelf-kind entry does;
    # amenity/parking/checkout entries never hold products and don't). A
    # fixture with neither -- e.g. shelf-1/shelf-2, the prototype scenario's
    # two starting shelves from before the catalog system existed -- has no
    # confirmed data to check against, so it stays unrestricted rather than
    # inventing a rule for it.
    var fixture: Dictionary = layout.fixtures_by_id[fixture_id]
    var fixture_catalog_entry: Dictionary = _fixture_catalog.get(str(fixture.get("catalog_id", "")), {})
    if fixture_catalog_entry.has("compatible_product_categories"):
        var compatible_categories: Array = fixture_catalog_entry["compatible_product_categories"]
        if not compatible_categories.has(catalog_id):
            return false
    var initial_stock_units: int = int(catalog_entry["initial_stock_units"])
    if fixture_catalog_entry.has("capacity"):
        initial_stock_units = min(initial_stock_units, int(fixture_catalog_entry["capacity"]))
    var restock_unit_cost_yen: int = int(catalog_entry["restock_unit_cost_yen"])
    var procurement_cost_yen: int = initial_stock_units * restock_unit_cost_yen
    if economy.cash_yen < procurement_cost_yen:
        return false
    var product_config := {
        "id": instance_id,
        "fixture_id": fixture_id,
        "initial_stock_units": initial_stock_units,
        "sale_price_yen": int(catalog_entry["sale_price_yen"]),
        "restock_unit_cost_yen": restock_unit_cost_yen,
    }
    if not inventory.add_product(product_config):
        return false
    var expense: Dictionary = economy.record_explicit_expense(
        "product_procurement",
        minute_of_day,
        procurement_cost_yen,
        {"catalog_id": catalog_id, "instance_id": instance_id, "fixture_id": fixture_id}
    )
    _record_event("product_procured", {
        "catalog_id": catalog_id,
        "instance_id": instance_id,
        "fixture_id": fixture_id,
        "expense_id": expense["expense_id"],
    })
    return true


func try_purchase_promotion(promotion_id: String) -> bool:
    if is_game_over or not customers.all_settled():
        return false
    if not _promotion_catalog.has(promotion_id):
        return false
    if _promotions_used_this_month.has(promotion_id):
        return false
    var catalog_entry: Dictionary = _promotion_catalog[promotion_id]
    var trigger_day: int = int(catalog_entry["trigger_day"])
    var trigger_hour: int = int(catalog_entry["trigger_hour"])
    var current_day_of_month := _days_completed_this_month + 1
    var current_hour := minute_of_day / 60
    if current_day_of_month > trigger_day or (
        current_day_of_month == trigger_day and current_hour > trigger_hour
    ):
        return false
    _promotions_used_this_month[promotion_id] = true
    _scheduled_promotions.append({
        "promotion_id": promotion_id,
        "trigger_day": trigger_day,
        "trigger_hour": trigger_hour,
    })
    _record_event("promotion_scheduled", {
        "promotion_id": promotion_id,
        "trigger_day": trigger_day,
        "trigger_hour": trigger_hour,
    })
    return true


func chain_expansion_cost_yen() -> int:
    return _land_value_policy.current_land_price_yen(
        BASE_LAND_PRICE_YEN, town, float(month_count) / MONTHS_PER_YEAR
    )


func try_expand_chain() -> bool:
    if is_game_over or not customers.all_settled() or _any_restock_task_active():
        return false
    var expansion_cost_yen := chain_expansion_cost_yen()
    if economy.cash_yen < expansion_cost_yen:
        return false
    var new_store_sequence := player_store_count + 1
    var expense: Dictionary = economy.record_explicit_expense(
        "chain_expansion",
        minute_of_day,
        expansion_cost_yen,
        {"new_store_sequence": new_store_sequence}
    )
    player_store_count = new_store_sequence
    _record_event("chain_expanded", {
        "player_store_count": player_store_count,
        "cost_yen": expansion_cost_yen,
        "expense_id": expense["expense_id"],
    })
    return true


func try_relocate_fixture(fixture_id: String, new_origin: Vector2i) -> bool:
    if is_game_over or not customers.all_settled() or _any_restock_task_active():
        return false
    if layout.fixture_origin(fixture_id) == Vector2i(-1, -1):
        return false
    var previous: Array = layout.fixture_snapshot()
    if not layout.try_move_fixture(fixture_id, new_origin):
        return false
    _refresh_interactions()
    if not _required_routes_are_reachable() or not _all_staff_are_walkable():
        layout.restore_fixture_snapshot(previous)
        _refresh_interactions()
        return false
    _record_event("fixture_relocated", {
        "fixture_id": fixture_id,
        "origin_subcell": [new_origin.x, new_origin.y],
    })
    return true


func try_rotate_fixture_clockwise(fixture_id: String) -> bool:
    if is_game_over or not customers.all_settled() or _any_restock_task_active():
        return false
    var previous: Array = layout.fixture_snapshot()
    if not layout.try_rotate_fixture_clockwise(fixture_id):
        return false
    _refresh_interactions()
    if not _required_routes_are_reachable() or not _all_staff_are_walkable():
        layout.restore_fixture_snapshot(previous)
        _refresh_interactions()
        return false
    _record_event("fixture_rotated", {"fixture_id": fixture_id})
    return true


# Replaces the entire store layout with a pre-built sample from
# sample_layouts (task #37). Confirmed first-title evidence: a sample-layout
# loading path exists in the original UI, and loading one is not trivially
# reversible (docs/research/ss-layout-entrance-register-and-chain-
# cannibalization-2026-09-06.md section 3) -- there is no confirmed undo, so
# this client does not add one either. Any fixture id the sample reuses from
# the current layout keeps its existing ownership at no extra cost (this is
# a rearrangement, not a repurchase); any id the sample introduces that the
# current layout does not already have is charged at that catalog entry's
# normal purchase price, same as try_purchase_fixture. To avoid inventing an
# "auto-clear inventory" rule the evidence does not describe, loading a
# sample that would remove a fixture currently holding procured stock is
# rejected outright rather than silently discarding that inventory.
func try_load_sample_layout(sample_id: String) -> bool:
    if is_game_over or not customers.all_settled() or _any_restock_task_active():
        return false
    if not _sample_layout_catalog.has(sample_id):
        return false
    var sample_fixtures: Array = _sample_layout_catalog[sample_id]["fixtures"]
    var checkout_fixture_id := str(config["simulation"]["checkout_fixture_id"])
    var sample_ids: Dictionary = {}
    var total_cost_yen := 0
    for entry in sample_fixtures:
        var fixture_id := str(entry["id"])
        sample_ids[fixture_id] = true
        if str(entry["kind"]) == "checkout" and fixture_id != checkout_fixture_id:
            return false
    if not sample_ids.has(checkout_fixture_id):
        return false
    for entry in sample_fixtures:
        var fixture_id := str(entry["id"])
        if layout.fixtures_by_id.has(fixture_id):
            continue
        var catalog_id := str(entry.get("catalog_id", ""))
        if catalog_id.is_empty() or not _fixture_catalog.has(catalog_id):
            return false
        total_cost_yen += int(_fixture_catalog[catalog_id]["purchase_price_yen"])
    for product in inventory.products.values():
        if not sample_ids.has(str(product.fixture_id)):
            return false
    if economy.cash_yen < total_cost_yen:
        return false
    var candidate_fixtures: Array = []
    for entry in sample_fixtures:
        candidate_fixtures.append((entry as Dictionary).duplicate(true))
    if not layout.fixture_snapshot_is_valid(candidate_fixtures):
        return false
    var previous_fixtures: Array = layout.fixture_snapshot()
    layout.restore_fixture_snapshot(candidate_fixtures)
    _refresh_interactions()
    if not _required_routes_are_reachable() or not _all_staff_are_walkable():
        layout.restore_fixture_snapshot(previous_fixtures)
        _refresh_interactions()
        return false
    var expense: Dictionary = economy.record_explicit_expense(
        "sample_layout_loaded",
        minute_of_day,
        total_cost_yen,
        {"sample_id": sample_id}
    )
    _record_event("sample_layout_loaded", {
        "sample_id": sample_id,
        "expense_id": expense["expense_id"],
        "fixture_count": sample_fixtures.size(),
    })
    return true


func step() -> void:
    if is_game_over:
        return
    _advance_minute_of_day()
    # Every customer still in progress (not just the single most-recently-
    # admitted one) advances its own phase machine this tick (task #36,
    # concurrent customers). The single checkout fixture/staff is still a
    # shared, serialized resource: a customer that finishes shopping joins
    # _checkout_queue instead of starting service immediately, and
    # _dispatch_checkout_queue() below hands the fixture to the next queued
    # customer only once it is free.
    for customer in customers.active_customers():
        _advance_customer(customer)
    _dispatch_checkout_queue()
    _step_restock_tasks()


func _advance_customer(customer) -> void:
    match customer.phase:
        "to_shelf":
            if customer.move_along_route("shopping"):
                customer.shopping_ticks_remaining = _shopping_ticks
                _record_event("customer_reached_product", {
                    "customer_id": customer.customer_id,
                    "product_id": customer.current_product_id(),
                })
        "shopping":
            customer.shopping_ticks_remaining -= 1
            if customer.shopping_ticks_remaining <= 0:
                var product_id: String = customer.current_product_id()
                var line: Dictionary = inventory.try_take_one(product_id)
                if not line.is_empty():
                    customer.add_basket_line(line)
                    _record_event("product_picked", {
                        "customer_id": customer.customer_id,
                        "product_id": product_id,
                    })
                else:
                    _record_event("product_unavailable", {
                        "customer_id": customer.customer_id,
                        "product_id": product_id,
                    })
                customer.advance_plan()
                var next_product_id: String = customer.current_product_id()
                if not next_product_id.is_empty():
                    customer.phase = "to_shelf"
                    customer.route = layout.find_path(
                        customer.position,
                        _product_interaction(next_product_id)
                    )
                elif customer.basket.is_empty():
                    customer.phase = "leaving"
                    customer.route = layout.find_path(customer.position, layout.exit)
                    _record_event("customer_leaving_without_sale", {
                        "customer_id": customer.customer_id,
                    })
                else:
                    customer.phase = "to_checkout"
                    customer.route = layout.find_path(customer.position, _checkout_interaction)
        "to_checkout":
            if customer.move_along_route("waiting_checkout"):
                _checkout_queue.append(customer.customer_id)
                _record_event("customer_queued_for_checkout", {
                    "customer_id": customer.customer_id,
                    "queue_position": _checkout_queue.size(),
                })
        "waiting_checkout":
            pass  # Dequeued by _dispatch_checkout_queue() once the checkout is free.
        "checkout":
            customer.checkout_ticks_remaining -= 1
            if customer.checkout_ticks_remaining <= 0:
                var checkout_staff = staff.checkout_staff()
                if not customer.basket.is_empty():
                    var record: Dictionary = economy.settle_basket(
                        customer.customer_id,
                        minute_of_day,
                        customer.basket
                    )
                    customer.mark_settled(record)
                checkout_staff.state = "idle"
                customer.phase = "leaving"
                customer.route = layout.find_path(customer.position, layout.exit)
                _record_event("checkout_completed", {
                    "customer_id": customer.customer_id,
                    "staff_id": checkout_staff.staff_id,
                    "transaction_id": customer.settled_transaction_id,
                })
        "leaving":
            if customer.move_along_route("done"):
                _record_event("customer_exited", {"customer_id": customer.customer_id})
                _observe_chain_visitor_milestone()
        _:
            push_error("Unknown customer phase: %s" % customer.phase)


# Hands the single checkout fixture's one service slot to the
# longest-waiting queued customer once the currently-serving staff member is
# free. Runs after every customer has taken its own turn this tick, so a
# customer that just joined the queue this same tick can be dispatched
# immediately if the checkout was already idle -- matching this client's
# pre-task-#36 behavior of starting service in the same tick a lone customer
# arrives.
func _dispatch_checkout_queue() -> void:
    var checkout_staff = staff.checkout_staff()
    if checkout_staff.state != "idle" or _checkout_queue.is_empty():
        return
    var customer_id: String = _checkout_queue.pop_front()
    var customer = customers.customer(customer_id)
    customer.phase = "checkout"
    customer.checkout_ticks_remaining = _checkout_timing.required_ticks(
        checkout_staff.register_skill, _checkout_ticks
    )
    checkout_staff.state = "checkout"
    _record_event("checkout_started", {
        "customer_id": customer.customer_id,
        "staff_id": checkout_staff.staff_id,
    })


func clock_text() -> String:
    return "%02d:%02d" % [minute_of_day / 60, minute_of_day % 60]


func snapshot() -> Dictionary:
    var customer = customers.active()
    var checkout_staff = staff.checkout_staff()
    return {
        "minute_of_day": minute_of_day,
        "clock_text": clock_text(),
        "cash_yen": economy.cash_yen,
        "stock_units": inventory.total_stock_units(),
        "inventory": _inventory_snapshot(),
        "customer_id": customer.customer_id,
        "customer_phase": customer.phase,
        "customer_position": customer.position,
        "staff_id": checkout_staff.staff_id,
        "staff_state": checkout_staff.state,
        "staff_position": checkout_staff.position,
        "staff_count": staff.members.size(),
        "customer_basket_count": customer.basket.size(),
        "customer_basket_total_yen": customer.basket_total_yen(),
        "completed_sales": economy.completed_sales,
        "last_sale": economy.last_sale_record(),
        "expenses_yen": economy.recorded_expenses_yen(),
        "event_count": event_log.records.size(),
        "completed_visits": customers.completed_count(),
        "started_visits": customers.customers.size(),
        "last_event": last_event,
        "expected_arrivals_per_minute": demand.expected_arrivals_per_minute(),
        "restock_staff_states": _restock_staff_snapshot(),
        "day_count": day_count,
        "month_count": month_count,
        "is_game_over": is_game_over,
        "game_over_reason": game_over_reason,
        "permits_held": _permits_held.keys(),
        "popularity": popularity,
        "town_population": town.population,
        "town_store_count_including_rivals": town.store_count_including_rivals,
        "land_value_yen": _land_value_policy.current_land_price_yen(
            BASE_LAND_PRICE_YEN, town, float(month_count) / MONTHS_PER_YEAR
        ),
        "internal_rating_value": internal_rating_value,
        "star_rating": star_rating,
        "player_store_count": player_store_count,
        "chain_expansion_cost_yen": chain_expansion_cost_yen(),
        "magazine_or_contest_eligible": _store_events.magazine_or_contest_event_is_eligible(
            town.population, town.store_count_including_rivals
        ),
        "contest_prize_yen": _store_events.compute_contest_prize_yen(
            town.store_count_including_rivals
        ),
        # Every customer still in the store this tick (task #36, concurrent
        # customers), not only the single one the customer_id/customer_phase/
        # customer_basket_* fields above still describe for backward
        # compatibility with existing single-customer callers and tests.
        "active_customers": _active_customers_snapshot(),
    }


func _start_default_customer() -> void:
    var plan: Array[String] = customers.default_plan()
    var customer = customers.admit_default(
        layout.entry,
        layout.find_path(
            layout.entry,
            _product_interaction(plan[0])
        )
    )
    _record_customer_entered(customer)


func _record_customer_entered(customer) -> void:
    _record_event("customer_entered", {
        "customer_id": customer.customer_id,
        "planned_product_ids": customer.planned_product_ids.duplicate(),
    })


func observation_snapshot() -> Dictionary:
    return {
        "schema_version": 1,
        "provisional": true,
        "scenario_id": str(config["scenario_id"]),
        "events": event_log.snapshot(),
        "sales": economy.sale_records.duplicate(true),
        "expenses": economy.expense_records.duplicate(true),
        "inventory": _inventory_snapshot(),
    }


const SAVE_SCHEMA_VERSION := 2

# Deliberately not saved/restored: the active customer's mid-visit walk
# state (position along a route, basket-so-far, checkout progress) and
# staff members' mid-task walk/restock state (position along a route,
# restock_ticks_remaining). Both are transient, sub-representative-day
# animation progress; on load they are simply whatever a fresh reset()
# already produces (an idle staff roster and one freshly-admitted default
# customer), the same as this client's other reset boundaries. Persisting
# an exact mid-route position would need to serialize pathfinding routes
# for very little player-facing value, since the same route recomputes
# deterministically once the game resumes.
func save_state() -> Dictionary:
    return {
        "save_schema_version": SAVE_SCHEMA_VERSION,
        "scenario_id": str(config["scenario_id"]),
        "config_schema_version": int(config["schema_version"]),
        "minute_of_day": minute_of_day,
        "day_count": day_count,
        "month_count": month_count,
        "days_completed_this_month": _days_completed_this_month,
        "cash_at_month_start": _cash_at_month_start,
        "revenue_at_month_start": _revenue_at_month_start,
        "is_game_over": is_game_over,
        "game_over_reason": game_over_reason,
        "clear_condition_met": clear_condition_met,
        "popularity": popularity,
        "internal_rating_value": internal_rating_value,
        "star_rating": star_rating,
        "player_store_count": player_store_count,
        "chain_visitor_milestone": {
            "last_observed_total": _chain_visitor_milestone.last_observed_total,
            "next_threshold": _chain_visitor_milestone.next_threshold,
            "events": _chain_visitor_milestone.events.duplicate(true),
        },
        "permits_held": _permits_held.keys(),
        "promotions_used_this_month": _promotions_used_this_month.keys(),
        "scheduled_promotions": _scheduled_promotions.duplicate(true),
        "fixtures": layout.fixture_snapshot(),
        "inventory": inventory.snapshot(),
        "economy": economy.snapshot(),
        "events": event_log.snapshot(),
    }


# Returns false, without mutating this simulation, when the save data does
# not belong to the currently-loaded config (different scenario_id, or a
# schema_version the running config no longer matches) -- an expected,
# recoverable condition, the same as this client's other try_* actions.
# A structurally corrupted save (missing keys entirely) is not treated as
# this same recoverable case; it asserts, matching _require_config()'s own
# convention for malformed input this client did not itself produce.
func load_state(data: Dictionary) -> bool:
    if str(data.get("scenario_id", "")) != str(config["scenario_id"]):
        return false
    if int(data.get("config_schema_version", -1)) != int(config["schema_version"]):
        return false
    if int(data.get("save_schema_version", -1)) != SAVE_SCHEMA_VERSION:
        return false
    _require_save_data(data)
    if not layout.fixture_snapshot_is_valid(data["fixtures"]):
        return false
    # Clears every subsystem back to its config-derived starting point
    # first (the same subsystems reset() touches, minus admitting a
    # customer) so load_state() is safe to call on a simulation that has
    # already been running, not only a freshly-constructed one, and so a
    # customer is only admitted below once the layout is in its final,
    # loaded state -- admitting one before restoring fixtures could leave
    # its cached route stale against a layout that is about to change.
    layout.reset()
    inventory.reset()
    economy.reset()
    customers.reset()
    staff.reset()
    event_log.reset()
    minute_of_day = int(data["minute_of_day"])
    day_count = int(data["day_count"])
    month_count = int(data["month_count"])
    _days_completed_this_month = int(data["days_completed_this_month"])
    _cash_at_month_start = int(data["cash_at_month_start"])
    _revenue_at_month_start = int(data["revenue_at_month_start"])
    is_game_over = bool(data["is_game_over"])
    game_over_reason = str(data["game_over_reason"])
    clear_condition_met = bool(data["clear_condition_met"])
    popularity = int(data["popularity"])
    internal_rating_value = int(data["internal_rating_value"])
    star_rating = int(data["star_rating"])
    player_store_count = int(data["player_store_count"])
    var milestone_data: Dictionary = data["chain_visitor_milestone"]
    _chain_visitor_milestone = ChainVisitorMilestoneScript.new()
    _chain_visitor_milestone.last_observed_total = int(milestone_data["last_observed_total"])
    _chain_visitor_milestone.next_threshold = int(milestone_data["next_threshold"])
    _chain_visitor_milestone.events.assign(milestone_data["events"])
    _permits_held.clear()
    for permit_id in data["permits_held"]:
        _permits_held[str(permit_id)] = true
    _promotions_used_this_month.clear()
    for key in data["promotions_used_this_month"]:
        _promotions_used_this_month[str(key)] = true
    _scheduled_promotions.clear()
    for scheduled in data["scheduled_promotions"]:
        _scheduled_promotions.append((scheduled as Dictionary).duplicate(true))
    layout.restore_fixture_snapshot(data["fixtures"])
    inventory.restore_snapshot(data["inventory"])
    economy.restore_snapshot(data["economy"])
    event_log.restore_snapshot(data["events"])
    _refresh_interactions()
    _start_default_customer()
    return true


func _record_event(event_type: String, details: Dictionary = {}) -> void:
    event_log.append(event_type, minute_of_day, details)
    last_event = event_type.replace("_", " ")


func _refresh_interactions() -> void:
    _checkout_interaction = layout.interaction_for_fixture(
        str(config["simulation"]["checkout_fixture_id"]),
        "checkout"
    )


func _required_routes_are_reachable() -> bool:
    var cursor: Vector2i = layout.entry
    for product_id in config["customer"]["visit_plan_product_ids"]:
        var interaction := _product_interaction(str(product_id))
        if not layout.has_path(cursor, interaction):
            return false
        cursor = interaction
    return layout.has_path(cursor, _checkout_interaction) and layout.has_path(
        _checkout_interaction,
        layout.exit
    )


func _product_interaction(product_id: String) -> Vector2i:
    var product = inventory.get_product(product_id)
    return layout.interaction_for_fixture(product.fixture_id, "shelf")


func _product_plan_is_valid(product_ids: Array[String]) -> bool:
    if product_ids.is_empty():
        return false
    var seen: Dictionary = {}
    for product_id in product_ids:
        if product_id.is_empty() or seen.has(product_id) or not inventory.products.has(product_id):
            return false
        seen[product_id] = true
    var cursor: Vector2i = layout.entry
    for product_id in product_ids:
        var interaction := _product_interaction(product_id)
        if not layout.has_path(cursor, interaction):
            return false
        cursor = interaction
    return layout.has_path(cursor, _checkout_interaction)


func _inventory_snapshot() -> Array[Dictionary]:
    var rows: Array[Dictionary] = []
    for product_id in inventory.product_order:
        var product = inventory.get_product(product_id)
        rows.append({
            "product_id": product.product_id,
            "fixture_id": product.fixture_id,
            "stock_units": product.stock_units,
            "sale_price_yen": product.sale_price_yen,
        })
    return rows


func _active_customers_snapshot() -> Array[Dictionary]:
    var rows: Array[Dictionary] = []
    for customer in customers.active_customers():
        rows.append({
            "customer_id": customer.customer_id,
            "phase": customer.phase,
            "position": customer.position,
            "basket_count": customer.basket.size(),
        })
    return rows


func _all_staff_are_walkable() -> bool:
    for staff_member in staff.all_staff():
        if not layout.is_walkable(staff_member.position):
            return false
    return true


func _advance_minute_of_day() -> void:
    minute_of_day += _step_game_minutes
    _fire_due_promotions()
    while minute_of_day >= 24 * 60:
        minute_of_day -= 24 * 60
        _handle_day_boundary()
    _fire_due_chain_visitor_milestones()


func _handle_day_boundary() -> void:
    day_count += 1
    _days_completed_this_month += 1
    if _days_completed_this_month >= REPRESENTATIVE_DAYS_PER_MONTH:
        _settle_month_end()


func _settle_month_end() -> void:
    var four_day_net_result_yen: int = economy.cash_yen - _cash_at_month_start
    var month_result_yen: int = four_day_net_result_yen * MONTH_MULTIPLIER
    var adjustment_yen: int = month_result_yen - four_day_net_result_yen
    var record: Dictionary = economy.record_month_end_settlement(
        minute_of_day,
        adjustment_yen,
        {
            "month_number": month_count + 1,
            "four_day_net_result_yen": four_day_net_result_yen,
            "month_result_yen": month_result_yen,
        }
    )
    _record_event("month_end_settlement", {
        "month_number": month_count + 1,
        "four_day_net_result_yen": four_day_net_result_yen,
        "month_result_yen": month_result_yen,
        "settlement_id": record["settlement_id"],
    })
    var four_day_revenue_yen: int = economy.recorded_revenue_yen() - _revenue_at_month_start
    var monthly_sales_yen: int = four_day_revenue_yen * MONTH_MULTIPLIER
    _evaluate_store_rating(monthly_sales_yen)
    month_count += 1
    _days_completed_this_month = 0
    _cash_at_month_start = economy.cash_yen
    _revenue_at_month_start = economy.recorded_revenue_yen()
    _promotions_used_this_month.clear()
    _evaluate_terminal_state()


func _evaluate_store_rating(monthly_sales_yen: int) -> void:
    var service_skills: Array = []
    var security_skills: Array = []
    var cleaning_skills: Array = []
    for staff_member in staff.all_staff():
        service_skills.append(staff_member.service_skill)
        security_skills.append(staff_member.security_skill)
        cleaning_skills.append(staff_member.cleaning_skill)
    var fixture_service_bonuses: Array = []
    for fixture in layout.fixtures:
        var catalog_id := str(fixture.get("catalog_id", ""))
        if catalog_id.is_empty() or not _fixture_catalog.has(catalog_id):
            continue
        var catalog_entry: Dictionary = _fixture_catalog[catalog_id]
        if catalog_entry.has("service_bonus"):
            fixture_service_bonuses.append(int(catalog_entry["service_bonus"]))
    var service_value: float = _store_value.compute_service_value(
        service_skills, fixture_service_bonuses
    )
    var security_value: float = _store_value.compute_security_value(
        security_skills, _store_size_tier
    )
    var cleaning_value: float = _store_value.compute_cleaning_value(
        cleaning_skills, _store_size_tier
    )
    # No price-setting mechanic exists in this vertical slice yet (product
    # sale prices are fixed config values), so price_change_pct is always 0
    # ("no change from baseline") rather than a guessed nonzero value.
    var evaluation: Dictionary = _store_rating.evaluate_monthly_rating_change(
        internal_rating_value, 0, service_value, security_value, cleaning_value, monthly_sales_yen
    )
    internal_rating_value = int(evaluation["next_internal_value"])
    star_rating = _store_rating.star_rank_for_internal_value(internal_rating_value)
    demand.customer_share_percent = float(_customer_share.compute_customer_share_percent(
        popularity,
        service_value,
        cleaning_value,
        security_value,
        inventory.products.size(),
        demand.opening_minutes_per_day
    ))
    _record_event("store_rating_evaluated", {
        "month_number": month_count + 1,
        "monthly_sales_yen": monthly_sales_yen,
        "service_value": service_value,
        "security_value": security_value,
        "cleaning_value": cleaning_value,
        "criteria_met": evaluation["criteria_met"],
        "upgrade_applies": evaluation["upgrade_applies"],
        "downgrade_points": evaluation["downgrade_points"],
        "internal_rating_value": internal_rating_value,
        "star_rating": star_rating,
        "customer_share_percent": demand.customer_share_percent,
    })


func _evaluate_terminal_state() -> void:
    if economy.cash_yen < 0:
        _trigger_game_over("bankrupt")
        return
    if player_store_count >= PLAYER_STORE_COUNT_SCENARIO_TARGET:
        clear_condition_met = true
    var current_year: int = (month_count / MONTHS_PER_YEAR) + 1
    if current_year > GAME_OVER_YEAR_LIMIT and not clear_condition_met:
        _trigger_game_over("time_limit_exceeded")


func _trigger_game_over(reason: String) -> void:
    is_game_over = true
    game_over_reason = reason
    _record_event("game_over", {"reason": reason})


func _fire_due_promotions() -> void:
    if _scheduled_promotions.is_empty():
        return
    var current_day_of_month := _days_completed_this_month + 1
    var current_hour := minute_of_day / 60
    var remaining: Array[Dictionary] = []
    for scheduled in _scheduled_promotions:
        var due_day: int = int(scheduled["trigger_day"])
        var due_hour: int = int(scheduled["trigger_hour"])
        if current_day_of_month > due_day or (
            current_day_of_month == due_day and current_hour >= due_hour
        ):
            _fire_promotion(scheduled)
        else:
            remaining.append(scheduled)
    _scheduled_promotions = remaining


func _fire_promotion(scheduled: Dictionary) -> void:
    var promotion_id: String = str(scheduled["promotion_id"])
    var catalog_entry: Dictionary = _promotion_catalog[promotion_id]
    var cost_yen: int = int(catalog_entry["cost_yen"])
    var popularity_gain: int = int(catalog_entry["popularity_gain"])
    var expense: Dictionary = economy.record_explicit_expense(
        "promotion_cost",
        minute_of_day,
        cost_yen,
        {"promotion_id": promotion_id}
    )
    popularity = min(100, popularity + popularity_gain)
    _record_event("promotion_fired", {
        "promotion_id": promotion_id,
        "popularity_gain": popularity_gain,
        "popularity_after": popularity,
        "expense_id": expense["expense_id"],
    })


func _observe_chain_visitor_milestone() -> void:
    _chain_visitor_milestone.observe_total_visitors(
        customers.completed_count(), day_count + 1, minute_of_day / 60
    )


func _fire_due_chain_visitor_milestones() -> void:
    # Checked after the day-boundary loop above (using the now-current
    # day_count), since the milestone's "next day 00:00" trigger is most
    # naturally read as firing once that day begins -- unlike promotions,
    # whose trigger_day/trigger_hour is checked against the still-current
    # day so a trigger landing on a month's last tick still resolves
    # correctly (decision 0094). This store doesn't simulate overnight
    # hours, so "00:00" in practice means the first tick of the following
    # day, not literal midnight.
    var due: Array[Dictionary] = _chain_visitor_milestone.pop_due(
        day_count + 1, minute_of_day / 60
    )
    for milestone_event in due:
        var gain: int = int(milestone_event["popularity_gain"])
        popularity = min(100, popularity + gain)
        _record_event("chain_visitor_milestone_fired", {
            "threshold_visitors": int(milestone_event["threshold_visitors"]),
            "popularity_gain": gain,
            "popularity_after": popularity,
        })


func _step_restock_tasks() -> void:
    for staff_member in staff.all_staff():
        if staff_member.staff_id == staff.checkout_staff_id:
            continue
        match staff_member.state:
            "to_restock":
                if staff_member.move_along_route("restocking"):
                    staff_member.restock_ticks_remaining = _restock_timing.required_ticks(
                        staff_member.replenishment_skill, _restock_ticks
                    )
                    _record_event("restock_started", {
                        "staff_id": staff_member.staff_id,
                        "product_id": staff_member.restock_target_product_id,
                    })
            "restocking":
                staff_member.restock_ticks_remaining -= 1
                if staff_member.restock_ticks_remaining <= 0:
                    _complete_restock(staff_member)
    _assign_idle_restock_tasks()


func _complete_restock(staff_member) -> void:
    var product_id: String = staff_member.restock_target_product_id
    var product = inventory.get_product(product_id)
    var quantity: int = product.initial_stock_units - product.stock_units
    if quantity > 0:
        var resulting_stock: int = inventory.add_explicit_units(product_id, quantity)
        var total_cost_yen: int = quantity * product.restock_unit_cost_yen
        var expense: Dictionary = economy.record_explicit_expense(
            "inventory_restock",
            minute_of_day,
            total_cost_yen,
            {"product_id": product_id, "quantity": quantity, "staff_id": staff_member.staff_id}
        )
        _record_event("inventory_restock", {
            "product_id": product_id,
            "quantity": quantity,
            "staff_id": staff_member.staff_id,
            "expense_id": expense["expense_id"],
            "resulting_stock_units": resulting_stock,
        })
    staff_member.finish_restock()


func _assign_idle_restock_tasks() -> void:
    if not _restock_task_enabled:
        return
    var claimed_product_ids: Dictionary = {}
    for staff_member in staff.all_staff():
        if staff_member.staff_id != staff.checkout_staff_id and staff_member.state != "idle":
            claimed_product_ids[staff_member.restock_target_product_id] = true
    for product_id in inventory.product_order:
        if claimed_product_ids.has(product_id):
            continue
        if inventory.get_product(product_id).stock_units > _restock_trigger_stock_units_at_or_below:
            continue
        var idle_staff = _find_idle_restock_staff()
        if idle_staff == null:
            return
        idle_staff.begin_restock(product_id, layout.find_path(idle_staff.position, _product_interaction(product_id)))
        claimed_product_ids[product_id] = true


func _find_idle_restock_staff():
    for staff_member in staff.all_staff():
        if staff_member.staff_id != staff.checkout_staff_id and staff_member.state == "idle":
            return staff_member
    return null


func _any_restock_task_active() -> bool:
    for staff_member in staff.all_staff():
        if staff_member.staff_id != staff.checkout_staff_id and staff_member.state != "idle":
            return true
    return false


func _restock_staff_snapshot() -> Array[Dictionary]:
    var rows: Array[Dictionary] = []
    for staff_member in staff.all_staff():
        if staff_member.staff_id == staff.checkout_staff_id:
            continue
        rows.append({
            "staff_id": staff_member.staff_id,
            "state": staff_member.state,
            "position": staff_member.position,
            "restock_target_product_id": staff_member.restock_target_product_id,
        })
    return rows


func _require_save_data(data: Dictionary) -> void:
    for key in [
        "minute_of_day",
        "day_count",
        "month_count",
        "days_completed_this_month",
        "cash_at_month_start",
        "revenue_at_month_start",
        "is_game_over",
        "game_over_reason",
        "clear_condition_met",
        "popularity",
        "internal_rating_value",
        "star_rating",
        "player_store_count",
        "chain_visitor_milestone",
        "permits_held",
        "promotions_used_this_month",
        "scheduled_promotions",
        "fixtures",
        "inventory",
        "economy",
        "events",
    ]:
        if not data.has(key):
            push_error("save data missing required key: %s" % key)
            assert(false)
    var economy_data: Dictionary = data["economy"]
    for key in ["cash_yen", "sale_records", "expense_records", "month_end_records", "next_sale_sequence"]:
        if not economy_data.has(key):
            push_error("save data economy section missing required key: %s" % key)
            assert(false)
    var milestone_data: Dictionary = data["chain_visitor_milestone"]
    for key in ["last_observed_total", "next_threshold", "events"]:
        if not milestone_data.has(key):
            push_error("save data chain_visitor_milestone section missing required key: %s" % key)
            assert(false)


func _require_config() -> void:
    assert(int(config.get("schema_version", -1)) == 14)
    for key in ["store", "fixtures", "sample_layouts", "fixture_catalog", "permits", "product_catalog", "promotions", "products", "economy", "provisional_restock", "staff", "customer", "simulation", "demand", "town"]:
        if not config.has(key):
            push_error("vertical slice config missing required key: %s" % key)
            assert(false)
    assert(config.get("provisional", false) == true)
    var simulation: Dictionary = config["simulation"]
    for key in [
        "start_minute_of_day",
        "tick_seconds",
        "step_game_minutes",
        "shopping_ticks",
        "checkout_ticks",
        "checkout_fixture_id",
        "restock_ticks",
        "restock_trigger_stock_units_at_or_below",
        "restock_task_enabled",
    ]:
        if not simulation.has(key):
            push_error("vertical slice simulation config missing required key: %s" % key)
            assert(false)
    var demand_config: Dictionary = config["demand"]
    for key in [
        "nearby_population",
        "customer_share_percent",
        "daily_visit_rate_per_population",
        "opening_minutes_per_day",
        "bad_weather_visit_multiplier",
        "rng_seed",
    ]:
        if not demand_config.has(key):
            push_error("vertical slice demand config missing required key: %s" % key)
            assert(false)
    for catalog_entry in config["fixture_catalog"]:
        for key in ["catalog_id", "kind", "footprint_tiles", "purchase_price_yen"]:
            if not catalog_entry.has(key):
                push_error("fixture catalog entry missing required key: %s" % key)
                assert(false)
    for permit_entry in config["permits"]:
        for key in ["permit_id", "fee_yen"]:
            if not permit_entry.has(key):
                push_error("permit entry missing required key: %s" % key)
                assert(false)
    for product_entry in config["product_catalog"]:
        for key in ["catalog_id", "sale_price_yen", "restock_unit_cost_yen", "initial_stock_units"]:
            if not product_entry.has(key):
                push_error("product catalog entry missing required key: %s" % key)
                assert(false)
    for promotion_entry in config["promotions"]:
        for key in ["promotion_id", "cost_yen", "popularity_gain", "trigger_day", "trigger_hour"]:
            if not promotion_entry.has(key):
                push_error("promotion entry missing required key: %s" % key)
                assert(false)
    var town_config: Dictionary = config["town"]
    for key in ["population", "store_count_including_rivals"]:
        if not town_config.has(key):
            push_error("town config missing required key: %s" % key)
            assert(false)
    var store_config: Dictionary = config["store"]
    if not store_config.has("size_tier"):
        push_error("store config missing required key: size_tier")
        assert(false)
    for staff_entry in config["staff"]["members"]:
        for key in ["service_skill", "security_skill", "cleaning_skill"]:
            if not staff_entry.has(key):
                push_error("staff member config missing required key: %s" % key)
                assert(false)
