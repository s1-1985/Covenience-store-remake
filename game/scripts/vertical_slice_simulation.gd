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
const StaffGrowthScript := preload("res://scripts/domain/staff_growth.gd")
const CheckoutAngerScript := preload("res://scripts/domain/checkout_anger.gd")
const TownSpatialScript := preload("res://scripts/domain/town_spatial.gd")
const StoreSiteScript := preload("res://scripts/domain/store_site.gd")
const GuideStartingStoreScript := preload("res://scripts/domain/guide_starting_store.gd")

# CONFIRMED_OFFICIAL, not a guess: the strategy guide states this multiplier
# directly ("1月=4日間×8"; reference_sim/conveni_sim/month_aggregation.py
# mirrors the same citation). What the guide does not state is how each
# representative day's own net result is computed internally; this client,
# like month_aggregation.py, only turns the already-tracked cash change
# across REPRESENTATIVE_DAYS_PER_MONTH days into the displayed monthly figure.
const REPRESENTATIVE_DAYS_PER_MONTH := 4
const MONTH_MULTIPLIER := 8
# Task #104: one-off purchases (land, the store building, buying out a
# rival, fixtures, permits...) are paid once, not part of the four days'
# running 収支 that the guide multiplies by 8. The guide's wording ("4日間の
# 収支を8倍することで、1月の収支が決定する") is about running the store;
# scaling a 20,000,000-yen land purchase to 160,000,000 would bankrupt every
# new game at its first month end, which the guide's own play (start with
# 200,000,000, buy land, keep going) rules out -- an inference, not a
# stated rule. Promotions, stock and wages stay in the x8 as before.
const CAPITAL_EXPENSE_TYPES := [
    "store_site", "store_construction", "chain_expansion", "rival_buyout",
    "rival_investigation", "fixture_purchase", "fixture_sold", "permit_purchase",
    "sample_layout_loaded",
]

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

# Task #65: CONFIRMED_OFFICIAL, re-verified 2026-09-24 directly against a
# 400dpi rescan of the strategy guide's third companion book ("攻略&データ
# ブック", オールテクニックガイド ライバル対策, print page 79): "新規出店時
# の土地代 = 地価（4エリア分）+建物評価額／2". `chain_expansion_cost_yen()`
# previously charged the bare per-area land price with no area multiplier at
# all (an unstated implicit ×1) -- this constant supplies the guide's own
# exact ×4 multiplier for opening a new branch. The "+建物評価額／2" existing-
# building-removal term is not applied here: try_expand_chain() is (per
# decision 0099) a purely abstract economic action with no specific plot or
# existing structure to appraise.
const NEW_BRANCH_LAND_AREA_COUNT := 4

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
# Task #85: separate from _demand_rng so adding weather rolls does not shift
# the existing seeded arrival/product-choice sequence.
var _weather_rng: RandomNumberGenerator
# Index into config["weather"]["categories"] (快晴/晴れ/曇り/雨・雪/荒天).
var weather_category_index := 0

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
# Task #97: staff work in the real game (guide_starting_store.staff_work).
# 0.0 / false keep the prototype scenarios' old behavior.
var _restock_trigger_share_of_full := 0.0
var _cleaning_task_enabled := false
var _stamina_enabled := false
# Task #102: customers come from the buildings around the store and want
# what DATA4 says those buildings want; the month's survey (アンケート).
var _building_demand_enabled := false
# Task #103: business hours (guide_starting_store.business_hours). Empty in
# the prototype scenarios, which stay open all day as before.
var _business_hours: Array = []
var business_hours_id := ""
var _catchment_weights: Dictionary = {}
var survey_bought: Dictionary = {}
var survey_missing: Dictionary = {}
var last_survey: Dictionary = {}
var _stamina_rng := RandomNumberGenerator.new()
# Where customers have walked and nobody has cleaned since (oldest first).
var _dirty_cells: Array[Vector2i] = []
const MAX_DIRTY_CELLS := 24
var _days_completed_this_month: int
var _cash_at_month_start: int
# Task #104: expense_records index where this month began, so the month-end
# settlement can leave one-off purchases out of the x8 (see
# CAPITAL_EXPENSE_TYPES).
var _expense_index_at_month_start := 0
var _revenue_at_month_start: int
var is_game_over: bool
var game_over_reason: String
var clear_condition_met: bool
var _fixture_catalog: Dictionary = {}
var _sample_layout_catalog: Dictionary = {}
var _permit_catalog: Dictionary = {}
var _product_catalog: Dictionary = {}
var _staff_candidate_catalog: Dictionary = {}
var _permits_held: Dictionary = {}
var _promotion_catalog: Dictionary = {}
var _promotions_used_this_month: Dictionary = {}
var _scheduled_promotions: Array[Dictionary] = []
var popularity: int
# Task #53: CONFIRMED_OFFICIAL that a price-setting/margin mechanic exists
# (see try_set_price_policy below for the citation); 0 means "no change
# from the catalog's own list price," matching the guide's own baseline
# framing ("通常は全て40%に設定されており、これが定価と考えられる" --
# the catalog's sale_price_yen values already assume that baseline margin,
# so this client does not re-derive prices from a separate margin input).
var price_change_pct: int
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
var _staff_growth
var _checkout_anger
var _town_spatial
# Task #59: the player's own store's position on the same abstract distance
# scale as `_rival_stores` below, so `TownSpatial.can_acquire_permit_at()`
# has something to measure a permit-exclusion distance from. This client
# has no real town/map spatial simulation (decision 0095/0127), so this is
# just a fixed reference point, not a placed position on an actual map.
var _player_store_position: Vector2i
# Task #95: the 2x2 site the player bought on the guide town map
# (NO_STORE_SITE until then), and the buildings bought and cleared with it.
# store_site is null for configs without guide_town_map.
const NO_STORE_SITE := Vector2i(-1, -1)
var store_site
var store_site_origin := NO_STORE_SITE
var _bought_buildings: Array[int] = []
# Task #104: which of the 「店舗を選んで下さい」 stores stands on the site
# (config["store_types"], guide_store_types); "" for configs without them.
var store_type_id := ""
# Task #59: REMAKE_BALANCED_DEFAULT rival-store roster -- position and
# held permits for each configured rival, used only to enforce the
# CONFIRMED_OFFICIAL permit-exclusion distance rule
# (TownSpatial.can_acquire_permit_at()) against try_purchase_permit().
# Defaults to empty in the default scenario config (a no-op, same
# convention as demand.rival_store_count's own default), since no source
# states how many rivals exist, where they are, or which permits they
# hold -- this array only ever reflects config a caller supplied, never a
# value this client invents on its own. Static for this vertical slice's
# lifetime: no rival AI/spawn loop exists to change it after _init().
var _rival_stores: Array[Dictionary] = []
# Task #101: rival branches the player bought out, now the player's own
# stores ({"id", "position"}), and rivals already investigated.
var owned_branches: Array[Dictionary] = []
var _investigated_rivals: Dictionary = {}
# Task #106: rival branches that withdrew and open again at the next month
# end (guide_town_map.rival_ai): {"id", "left": the site it left}.
var _rivals_to_reopen: Array[Dictionary] = []
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
    for entry in config["staff_candidates"]:
        _staff_candidate_catalog[str(entry["candidate_id"])] = entry
    layout = StoreLayoutScript.new(config["store"], config["fixtures"])
    inventory = InventoryCatalogScript.new(config["products"])
    economy = EconomyStateScript.new(config["economy"])
    customers = CustomerRosterScript.new(config["customer"])
    staff = StaffRosterScript.new(config["staff"])
    event_log = RuntimeEventLogScript.new()
    _demand_rng = RandomNumberGenerator.new()
    _weather_rng = RandomNumberGenerator.new()
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
    store_type_id = str(config.get("store_type_id", ""))
    _store_events = StoreEventsScript.new()
    _checkout_timing = CheckoutTimingScript.new()
    _restock_timing = RestockTimingScript.new()
    _staff_growth = StaffGrowthScript.new()
    _checkout_anger = CheckoutAngerScript.new()
    _town_spatial = TownSpatialScript.new()
    _player_store_position = _vec2i_from_array(config["town"]["player_store_position"])
    if config.has("guide_town_map"):
        store_site = StoreSiteScript.new(config["guide_town_map"])
    _load_rivals()
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
    _restock_trigger_share_of_full = float(simulation.get("restock_trigger_share_of_full", 0.0))
    _cleaning_task_enabled = bool(simulation.get("cleaning_task_enabled", false))
    _stamina_enabled = bool(simulation.get("stamina_enabled", false))
    _building_demand_enabled = bool(simulation.get("building_demand_enabled", false))
    _business_hours = simulation.get("business_hours", [])
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
    _dirty_cells.clear()
    _reset_stamina()
    _load_rivals()
    if not _business_hours.is_empty():
        _apply_business_hours(str(config["simulation"]["business_hours_default_id"]))
    survey_bought.clear()
    survey_missing.clear()
    last_survey = {}
    _clear_store_site()
    _cash_at_month_start = economy.cash_yen
    _revenue_at_month_start = economy.recorded_revenue_yen()
    _expense_index_at_month_start = economy.expense_records.size()
    is_game_over = false
    game_over_reason = ""
    clear_condition_met = false
    _permits_held.clear()
    _promotions_used_this_month.clear()
    _scheduled_promotions.clear()
    popularity = 0
    price_change_pct = 0
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
    _weather_rng.seed = int(config["weather"]["rng_seed"])
    _roll_weather()
    _refresh_interactions()
    _start_opening_customer()


# The customer already inside when a game starts or loads. Task #105: not
# while the store is closed (a new real game starts at 00:00, before its
# AM7:00 opening) -- nobody is inside a closed store.
func _start_opening_customer() -> void:
    if is_open_now():
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


# Task #52: an explicit player action, confirmed by the strategy guide
# (book p.35, CONFIRMED_OFFICIAL, directly re-read): "怒りやすいお客さん
# は、おじさんやおじいさんに多い。もしレジ前の混雑にこの人が混じってい
# たら、カーソルをこの人に合わせて決定ボタン。怒り出すまえに"つまみだ
# す"を選んで、お店の外に出してしまうといいぞ。" Selecting a customer
# who is in the checkout queue or being served and choosing to eject them
# removes them from the store before they can trigger the (task #51,
# store-wide) checkout-anger penalty, at the cost of forfeiting their
# purchase entirely. Scoped to "waiting_checkout"/"checkout" only, matching
# the guide's own "レジ前の混雑" (checkout-front congestion) framing -- a
# customer still shopping elsewhere in the store isn't eligible. Whether an
# already-picked-up basket's units return to shelf stock on ejection is not
# stated by any source; this project's own REMAKE_BALANCED_DEFAULT choice
# is that they do not (the customer simply leaves with whatever they were
# already holding), since this client has no other "undo a pick-up"
# mechanic anywhere to reuse instead of inventing one -- ejecting a
# customer who already filled their basket is a real shrinkage cost, not a
# free do-over.
func try_eject_customer(customer_id: String) -> bool:
    if is_game_over or not customers.customers.has(customer_id):
        return false
    var ejected_customer = customers.customer(customer_id)
    if ejected_customer.phase != "waiting_checkout" and ejected_customer.phase != "checkout":
        return false
    if ejected_customer.phase == "waiting_checkout":
        _checkout_queue.erase(customer_id)
    else:
        staff.checkout_staff().state = "idle"
    ejected_customer.phase = "leaving"
    ejected_customer.route = layout.find_path(ejected_customer.position, layout.exit)
    _record_event("customer_ejected", {
        "customer_id": customer_id,
        "had_unsettled_basket": not ejected_customer.basket.is_empty(),
    })
    return true


func demand_admit_if_due() -> bool:
    if is_game_over or not customers.can_admit() or not is_open_now():
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


# Task #87: the real-time game loop. Before this, main.gd only ran the
# arrival roll (tick_idle_for_demand) once every admitted customer had
# left, and step() never admitted anyone -- so no matter how busy the store
# was, customers entered strictly one visit at a time. The original fills
# the store with many shoppers at once (a single gameplay-video frame,
# assets/raw/conveni_additional_assets_v1/reference/video_900s.png, shows
# about eight customers inside a small store simultaneously). step() and
# tick_idle_for_demand() keep their narrower semantics for the existing
# scripted smoke scenarios.
func tick() -> void:
    if is_game_over:
        return
    step()
    if customers.can_admit_concurrent() and is_open_now() and demand.customer_arrives_this_minute():
        _start_default_customer()


# Task #80: CONFIRMED_OFFICIAL (docs/research/strategy-guide-third-companion-
# book-full-extraction-2026-09-24.md, PDF1 p.68-71 Q&A: manual restock
# "stunts staff 補充 growth") -- unlike _complete_restock() (the autonomous
# staff-restock task, decision 0089), this deliberately does not call
# _staff_growth.apply_replenish_growth(): a player-initiated restock must
# not grant the same 補充 skill growth an autonomous staff restock does.
# This asymmetry already existed (task #38, before this rule was confirmed
# in the source above) and needed no code change once the rule was found --
# only this comment, to record that the match is intentional, not
# coincidental.
func apply_explicit_restock(
    product_id: String,
    staff_id: String,
    quantity: int,
    total_cost_yen: int
) -> bool:
    # Task #97: no longer waits for every customer to leave -- during
    # opening hours the store is almost never empty, so the button could
    # effectively never be used. Adding units to a shelf does not touch any
    # route or basket (a customer reads the stock when reaching the shelf).
    if is_game_over or quantity <= 0 or total_cost_yen < 0:
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
    # Task #100: allowed while customers are in the store -- this changes
    # no fixture, route or basket (during opening hours the store is almost
    # never empty, so waiting for it blocked the action for good).
    if is_game_over:
        return false
    if has_permit(permit_id) or not _permit_catalog.has(permit_id):
        return false
    if not _can_acquire_permit(permit_id):
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


# Task #59: CONFIRMED_OFFICIAL rule (guide book page 9) that a permit
# cannot be acquired within that permit's exclusion distance of another
# store already holding it. `_rival_stores` is the only other-store source
# this client has (no multi-store placement mechanic exists for the
# player's own chain, see try_expand_chain()'s own note), so this only
# checks against configured rivals; it defaults to a no-op (permit always
# acquirable) when `_rival_stores` is empty, which is the default scenario
# config's own setting.
func _can_acquire_permit(permit_id: String) -> bool:
    return _can_acquire_permit_at(permit_id, _player_store_position)


func _can_acquire_permit_at(permit_id: String, position: Vector2i) -> bool:
    var exclusion_distance_tiles: int = int(_permit_catalog[permit_id]["exclusion_distance_tiles"])
    var holder_positions: Array[Vector2i] = []
    for rival in _rival_stores:
        if (rival["permits_held"] as Array).has(permit_id):
            holder_positions.append(rival["position"])
    return _town_spatial.can_acquire_permit_at(
        exclusion_distance_tiles, position, holder_positions
    )


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
        # Task #68: this is the exact catalog_id this call already looked up
        # catalog_entry with, not a guess -- store_view.gd uses it to pick
        # the matching product overlay sprite.
        "catalog_id": catalog_id,
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


# Task #53: a price-setting/margin mechanic is CONFIRMED_OFFICIAL, directly
# re-read from the strategy guide (クイックリファレンス book pages 5-6):
# "商品価格を決定して下さい。利益率の割合。通常は全て40%に設定されており、
# これが定価と考えられる。個別に設定" (a global profit-margin percentage,
# defaulting to 40% -- this client's product_catalog sale_price_yen values
# already assume that baseline) and a screenshot showing "全商品平均利益率
# 20% / 全体に設定 <20%OFFに> / 個別に設定" (a global "all items X% off"
# slider, plus a per-item override). This client only ports the GLOBAL
# slider, not the per-item override -- REMAKE_BALANCED_DEFAULT scope choice,
# not a claim that per-item pricing doesn't exist in the original. The
# confirmed section-8 fact that merchandise price is one factor in customer
# monopoly/footfall is deliberately NOT wired here: no source states a
# price-to-demand formula, so demand_policy.gd's arrival rate stays
# unaffected by price_change_pct (inventing that link would be a much
# larger, unconfirmed addition, not this task's narrow scope of finally
# consuming the price_change_pct field store_rating.gd has awaited since
# task #27). The lower bound of -100 (a 100% markdown, i.e. free) is this
# project's own REMAKE_BALANCED_DEFAULT sanity floor -- no source states a
# minimum, but a price below 0% of list price is not a meaningful discount.
func try_set_price_policy(new_price_change_pct: int) -> bool:
    # Task #100: allowed while customers are in the store -- this changes
    # no fixture, route or basket (during opening hours the store is almost
    # never empty, so waiting for it blocked the action for good).
    if is_game_over:
        return false
    if new_price_change_pct < -100:
        return false
    var previous_price_change_pct := price_change_pct
    price_change_pct = new_price_change_pct
    _record_event("price_policy_changed", {
        "previous_price_change_pct": previous_price_change_pct,
        "price_change_pct": price_change_pct,
    })
    return true


# Scales a product's own list price (product_catalog's confirmed
# sale_price_yen) by the currently configured price_change_pct, floored to
# a whole yen and never negative. Called once per unit at the moment a
# customer picks it up (inventory.try_take_one()'s own CONFIRMED_OFFICIAL
# unit_price_yen is the pre-discount list price), so the price actually
# charged reflects whatever price_change_pct was in effect at pickup time,
# not at checkout time.
func _apply_price_policy(list_price_yen: int) -> int:
    return max(0, int(floor(float(list_price_yen) * (100 + price_change_pct) / 100.0)))


func try_purchase_promotion(promotion_id: String) -> bool:
    # Task #100: allowed while customers are in the store -- this changes
    # no fixture, route or basket (during opening hours the store is almost
    # never empty, so waiting for it blocked the action for good).
    if is_game_over:
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


# Task #56: CONFIRMED_OFFICIAL (docs/research/quick-reference-guide-part1-
# 2026-09-19.md, directly re-read book p.6) that the 35-person
# staff_candidates pool (task #32) is an actual hiring pool a player draws
# from, not just reference lore -- but no hiring/firing UI has ever called
# into it. This client's staff.members roster is a fixed 2 slots (matching
# the guide's own "店員は2人まで雇用できる" ordinary-case cap, a manager/
# 店長 role and the rare "スーパー社員" headcount-of-3 promotion are both
# out of scope, see the decision doc), so "hiring" here means replacing
# whoever currently occupies an existing slot with a different candidate,
# not adding a third slot. Guarded the same way every other roster-
# affecting action already is (customers.all_settled()); additionally
# rejects hiring a candidate who is already employed in the OTHER slot
# (the same real person can't occupy both), and an unknown staff_id/
# candidate_id. Any accumulated skill growth (task #48) the outgoing
# occupant had is discarded -- see StaffState.hire()'s own comment.
func try_hire_candidate(staff_id: String, candidate_id: String) -> bool:
    if is_game_over or not customers.all_settled():
        return false
    var previous_candidate_id := ""
    if staff.members.has(staff_id):
        previous_candidate_id = staff.members[staff_id].candidate_id
    if not _apply_hire(staff_id, candidate_id):
        return false
    _record_event("staff_hired", {
        "staff_id": staff_id,
        "candidate_id": candidate_id,
        "previous_candidate_id": previous_candidate_id,
    })
    return true


# Shared by try_hire_candidate() (guarded, player-facing) and load_state()
# (unguarded, since load_state() already resets every subsystem to a known
# state before reapplying saved facts -- see its own comment).
func _apply_hire(staff_id: String, candidate_id: String) -> bool:
    if not staff.members.has(staff_id) or not _staff_candidate_catalog.has(candidate_id):
        return false
    for existing_staff_member in staff.all_staff():
        if existing_staff_member.staff_id != staff_id and existing_staff_member.candidate_id == candidate_id:
            return false
    staff.members[staff_id].hire(_staff_candidate_catalog[candidate_id])
    # A newly hired member arrives rested (first-title wiki: fire and
    # re-hire gives a full 体力).
    var hired = staff.members[staff_id]
    hired.stamina_max = int(_staff_candidate_catalog[candidate_id].get("stamina", 0))
    hired.stamina = hired.stamina_max
    hired.exhausted = false
    return true


func _load_rivals() -> void:
    _rival_stores.clear()
    owned_branches.clear()
    _investigated_rivals.clear()
    _rivals_to_reopen.clear()
    for rival_entry in config["town"].get("rival_stores", []):
        _rival_stores.append(_rival_store(str(rival_entry["id"]), _vec2i_from_array(rival_entry["position"]), 0))


func _rival_store(rival_id: String, position: Vector2i, deficit_months: int) -> Dictionary:
    var rival_permits_held: Array[String] = []
    for rival_entry in config["town"].get("rival_stores", []):
        if str(rival_entry["id"]) == rival_id:
            rival_permits_held.assign(rival_entry.get("permits_held", []))
    return {
        "id": rival_id,
        "position": position,
        "permits_held": rival_permits_held,
        "deficit_months": deficit_months,
    }


# Task #106: rivals losing money, withdrawing and opening again elsewhere
# (evidence in guide_town_map.rival_ai.evidence_note). At each month end:
# a branch that withdrew at the previous month end opens again on the best
# vacant site, while the town has fewer than town_store_limit stores
# (CONFIRMED_OFFICIAL 10, rivals included); then each rival loses the month
# when the player's stores press it hard enough -- REMAKE_BALANCED_DEFAULT:
# StoreSite.rival_pressure() >= deficit_pressure_threshold -- and withdraws
# after withdraw_after_deficit_months losing months in a row (the guide's
# 半年). PROVISIONAL: the 本店 holds on while the rival has a branch, and a
# withdrawn 本店 never comes back.
func _rival_ai() -> Dictionary:
    if not config.has("guide_town_map"):
        return {}
    return config["guide_town_map"].get("rival_ai", {})


func _player_store_origins() -> Array:
    var origins: Array = [store_site_origin]
    for branch in owned_branches:
        origins.append(branch["position"])
    return origins


func _rival_is_head(rival_id: String) -> bool:
    return str(_rival_guide_entry(rival_id).get("role", "branch")) == "head"


func rival_deficit_months(rival_id: String) -> int:
    var index := _rival_index(rival_id)
    return 0 if index < 0 else int(_rival_stores[index]["deficit_months"])


func _step_rivals_at_month_end() -> void:
    var ai := _rival_ai()
    if ai.is_empty() or store_site == null or not has_store_site():
        return
    var changed := false
    var reopening: Array[Dictionary] = _rivals_to_reopen.duplicate()
    _rivals_to_reopen.clear()
    # A store opened just now has not traded a month yet.
    var opened_now: Array[String] = []
    for waiting in reopening:
        var rival_id := str(waiting["id"])
        var site := NO_STORE_SITE
        if player_store_count + _rival_stores.size() < int(ai["town_store_limit"]):
            site = store_site.best_open_site(
                _rival_positions() + _player_store_origins(), _bought_buildings, [waiting["left"]]
            )
        if site == NO_STORE_SITE:
            _rivals_to_reopen.append(waiting)
            continue
        _rival_stores.append(_rival_store(rival_id, site, 0))
        _investigated_rivals.erase(rival_id)
        opened_now.append(rival_id)
        changed = true
        _record_event("rival_opened", {"rival_id": rival_id, "position": [site.x, site.y]})
    var has_branch := false
    for rival in _rival_stores:
        if not _rival_is_head(str(rival["id"])):
            has_branch = true
    var withdrawing: Array[String] = []
    for rival in _rival_stores:
        if opened_now.has(str(rival["id"])):
            continue
        var pressure: float = store_site.rival_pressure(
            rival["position"], _player_store_origins(), price_change_pct,
            int(ai["full_effect_price_cut_pct"]), _bought_buildings
        )
        if pressure >= float(ai["deficit_pressure_threshold"]):
            rival["deficit_months"] = int(rival["deficit_months"]) + 1
        else:
            rival["deficit_months"] = 0
        if int(rival["deficit_months"]) < int(ai["withdraw_after_deficit_months"]):
            continue
        if _rival_is_head(str(rival["id"])) and has_branch:
            continue
        withdrawing.append(str(rival["id"]))
    for rival_id in withdrawing:
        var index := _rival_index(rival_id)
        var months := int(_rival_stores[index]["deficit_months"])
        var left: Vector2i = _rival_stores[index]["position"]
        _rival_stores.remove_at(index)
        _investigated_rivals.erase(rival_id)
        if not _rival_is_head(rival_id):
            _rivals_to_reopen.append({"id": rival_id, "left": left})
        changed = true
        _record_event("rival_withdrew", {"rival_id": rival_id, "deficit_months": months})
    if changed:
        _apply_store_site(store_site_origin, [])


# Task #101: investigating and buying out a rival (evidence in
# guide_town_map.rival_actions.evidence_note). Only rivals placed on the
# guide town map carry the guide's data; others cannot be bought.
func _rival_guide_entry(rival_id: String) -> Dictionary:
    if not config.has("guide_town_map"):
        return {}
    for entry in config["guide_town_map"].get("rival_stores", []):
        if str(entry["id"]) == rival_id:
            return entry
    return {}


func rival_at(tile: Vector2i) -> String:
    for rival in _rival_stores:
        var origin: Vector2i = rival["position"]
        if tile.x >= origin.x and tile.x < origin.x + 2 and tile.y >= origin.y and tile.y < origin.y + 2:
            return str(rival["id"])
    return ""


func rival_is_buyable(rival_id: String) -> bool:
    return bool(_rival_guide_entry(rival_id).get("buyable", false))


# REMAKE_BALANCED_DEFAULT: the guide's start price grown by the land price's
# yearly rate (the price is CONFIRMED to rise with the years and the
# store's sales; the formula is not recovered).
func rival_buyout_price_yen(rival_id: String) -> int:
    var guide_data: Dictionary = _rival_guide_entry(rival_id).get("guide_data", {})
    if not rival_is_buyable(rival_id) or not guide_data.has("buyout_yen"):
        return 0
    return int(round(float(guide_data["buyout_yen"]) * land_price_growth_factor()))


func rival_investigation_cost_yen() -> int:
    if not config.has("guide_town_map"):
        return 0
    return int(config["guide_town_map"]["rival_actions"]["investigation_cost_yen"])


func rival_investigated(rival_id: String) -> bool:
    return _investigated_rivals.has(rival_id)


func try_investigate_rival(rival_id: String) -> bool:
    if is_game_over or _rival_guide_entry(rival_id).is_empty() or rival_investigated(rival_id):
        return false
    if _rival_index(rival_id) < 0 or economy.cash_yen < rival_investigation_cost_yen():
        return false
    var expense: Dictionary = economy.record_explicit_expense(
        "rival_investigation", minute_of_day, rival_investigation_cost_yen(), {"rival_id": rival_id}
    )
    _investigated_rivals[rival_id] = true
    _record_event("rival_investigated", {"rival_id": rival_id, "expense_id": expense["expense_id"]})
    return true


func try_buy_out_rival(rival_id: String) -> bool:
    var index := _rival_index(rival_id)
    if is_game_over or index < 0 or not rival_is_buyable(rival_id):
        return false
    var price := rival_buyout_price_yen(rival_id)
    if economy.cash_yen < price:
        return false
    var expense: Dictionary = economy.record_explicit_expense(
        "rival_buyout", minute_of_day, price, {"rival_id": rival_id}
    )
    var bought: Dictionary = _rival_stores[index]
    _rival_stores.remove_at(index)
    owned_branches.append({"id": rival_id, "position": bought["position"]})
    player_store_count += 1
    # The store is no longer a competitor: the player's own store keeps the
    # customers it shared with it (REMAKE_BALANCED_DEFAULT: the branch's own
    # sales are not simulated, like the chain-expansion action).
    if has_store_site():
        _apply_store_site(store_site_origin, [])
    _record_event("rival_bought_out", {
        "rival_id": rival_id,
        "cost_yen": price,
        "player_store_count": player_store_count,
        "expense_id": expense["expense_id"],
    })
    return true


func _rival_index(rival_id: String) -> int:
    for index in _rival_stores.size():
        if str(_rival_stores[index]["id"]) == rival_id:
            return index
    return -1


# Task #103 (evidence in guide_starting_store.business_hours.evidence_note):
# customers arrive only while open; wages and upkeep already scale with
# demand.opening_minutes_per_day (_scale_yen_to_configured_business_hours),
# so a closed day (臨時休業) costs none of them. Customers already inside
# at closing time finish their visit.
func business_hours_presets() -> Array:
    return _business_hours


func _business_hours_preset(preset_id: String) -> Dictionary:
    for preset in _business_hours:
        if str(preset["id"]) == preset_id:
            return preset
    return {}


static func open_minutes(preset: Dictionary) -> int:
    var open := int(preset["open"])
    var close := int(preset["close"])
    if close == open:
        return 0
    return close - open if close > open else 24 * 60 - open + close


func is_open_now() -> bool:
    if _business_hours.is_empty():
        return true
    var preset := _business_hours_preset(business_hours_id)
    var open := int(preset["open"])
    var close := int(preset["close"])
    if open_minutes(preset) == 0:
        return false
    if close > open:
        return minute_of_day >= open and minute_of_day < close
    return minute_of_day >= open or minute_of_day < close


func _apply_business_hours(preset_id: String) -> void:
    business_hours_id = preset_id
    demand.opening_minutes_per_day = open_minutes(_business_hours_preset(preset_id))


func try_set_business_hours(preset_id: String) -> bool:
    if is_game_over or _business_hours_preset(preset_id).is_empty() or preset_id == business_hours_id:
        return false
    var previous := business_hours_id
    _apply_business_hours(preset_id)
    _record_event("business_hours_changed", {"previous": previous, "business_hours": preset_id})
    return true


func has_store_site() -> bool:
    return store_site_origin != NO_STORE_SITE


func _clear_store_site() -> void:
    store_site_origin = NO_STORE_SITE
    _bought_buildings.clear()
    _player_store_position = _vec2i_from_array(config["town"]["player_store_position"])
    demand.nearby_population = int(config["demand"]["nearby_population"])
    demand.rival_store_count = maxi(0, town.store_count_including_rivals - 1)


# Land price growth since the start of the game: LandValuePolicy's yearly
# rate (REMAKE_BALANCED_DEFAULT, remake_land_value.ANNUAL_INFLATION_RATE).
func land_price_growth_factor() -> float:
    return _land_value_policy.time_inflation_factor(float(month_count) / MONTHS_PER_YEAR)


# Task #95: what buying the 2x2 site at `origin` costs now, whether it may
# be bought, and which tobacco/alcohol/medicine permits a store there could
# still get (the ○/× of the original's land popup, guide p.10). Other
# stores are the configured rivals, whose positions are map squares here.
func store_site_quote(origin: Vector2i) -> Dictionary:
    if store_site == null:
        return {"buildable": false, "reason": "no_town_map"}
    var others: Array = []
    for rival in _rival_stores:
        others.append(rival["position"])
    for branch in owned_branches:
        others.append(branch["position"])
    var result: Dictionary = store_site.quote(origin, land_price_growth_factor(), others, _bought_buildings)
    var permits := {}
    for permit_id in _permit_catalog:
        permits[permit_id] = _can_acquire_permit_at(str(permit_id), origin)
    result["permits_available"] = permits
    result["nearby_population"] = store_site.nearby_population(
        origin, int(config["demand"]["nearby_population"]), _bought_buildings + result["bought_buildings"],
        _rival_positions()
    )
    return result


# Task #95: buy the site and put the store on it. Pays the land plus half
# the value of any building on it (CONFIRMED_OFFICIAL formula, see
# StoreSite), clears those buildings, and sets the store's nearby population
# from the site. Only once per game (a new store elsewhere is a separate,
# not yet built flow).
func try_buy_store_site(origin: Vector2i, type_id := "") -> bool:
    if is_game_over or store_site == null or has_store_site():
        return false
    var site_quote := store_site_quote(origin)
    if type_id.is_empty():
        type_id = store_type_id
    var construction_yen := 0
    if not store_types().is_empty():
        if not store_type_is_selectable(type_id):
            return false
        construction_yen = store_type_price_yen(type_id)
    if (
        not bool(site_quote["buildable"])
        or economy.cash_yen < int(site_quote["total_yen"]) + construction_yen
    ):
        return false
    if type_id != store_type_id:
        _build_store_type(type_id)
    var expense: Dictionary = economy.record_explicit_expense(
        "store_site",
        minute_of_day,
        int(site_quote["total_yen"]),
        {
            "origin": [origin.x, origin.y],
            "land_yen": int(site_quote["land_yen"]),
            "building_yen": int(site_quote["building_yen"]),
        }
    )
    _apply_store_site(origin, site_quote["bought_buildings"])
    _record_event("store_site_bought", {
        "origin": [origin.x, origin.y],
        "cost_yen": int(site_quote["total_yen"]),
        "expense_id": expense["expense_id"],
    })
    if construction_yen > 0:
        var construction: Dictionary = economy.record_explicit_expense(
            "store_construction", minute_of_day, construction_yen, {"store_type_id": type_id}
        )
        _record_event("store_built", {
            "store_type_id": type_id,
            "cost_yen": construction_yen,
            "expense_id": construction["expense_id"],
        })
    return true


# Task #104: the six stores of 「店舗を選んで下さい」 (guide_store_types:
# CONFIRMED_VISUAL that only the two small ones can be picked at the start,
# CONFIRMED_OFFICIAL sizes and prices).
func store_types() -> Array:
    return config.get("store_types", [])


func store_type_is_selectable(type_id: String) -> bool:
    var entry := GuideStartingStoreScript.store_type_entry(config, type_id)
    return bool(entry.get("selectable_at_start", false)) and entry.has("layout")


func store_type_price_yen(type_id: String) -> int:
    var entry := GuideStartingStoreScript.store_type_entry(config, type_id)
    return int(entry.get("construction_price_yen", 0))


# Replaces the store (floor, fixtures, shelves and their stock, staff posts)
# with store type `type_id`'s opening layout. Only before the store opens:
# anything that happened inside the old floor (a customer, dirt, layout
# edits) goes with it; hired staff stay hired.
func _build_store_type(type_id: String) -> void:
    var roster: Array[Dictionary] = _staff_roster_snapshot()
    GuideStartingStoreScript.apply_store_type(config, type_id)
    store_type_id = type_id
    _sample_layout_catalog.clear()
    for entry in config["sample_layouts"]:
        _sample_layout_catalog[str(entry["sample_id"])] = entry
    layout = StoreLayoutScript.new(config["store"], config["fixtures"])
    inventory = InventoryCatalogScript.new(config["products"])
    customers = CustomerRosterScript.new(config["customer"])
    staff = StaffRosterScript.new(config["staff"])
    for roster_entry in roster:
        var candidate_id := str(roster_entry["candidate_id"])
        if staff.members.has(str(roster_entry["staff_id"])) and _staff_candidate_catalog.has(candidate_id):
            staff.members[str(roster_entry["staff_id"])].hire(_staff_candidate_catalog[candidate_id])
    _store_size_tier = str(config["store"]["size_tier"])
    assert(_store_value.STORE_SIZE_VALUE_MULTIPLIER.has(_store_size_tier))
    _checkout_queue.clear()
    _dirty_cells.clear()
    _reset_stamina()
    _refresh_interactions()
    assert(_all_staff_are_walkable() and _required_routes_are_reachable())
    _start_opening_customer()


func _apply_store_site(origin: Vector2i, bought: Array) -> void:
    store_site_origin = origin
    _player_store_position = origin
    for index in bought:
        if not _bought_buildings.has(int(index)):
            _bought_buildings.append(int(index))
    demand.nearby_population = store_site.nearby_population(
        origin, int(config["demand"]["nearby_population"]), _bought_buildings, _rival_positions()
    )
    _catchment_weights = store_site.catchment_building_weights(origin, _rival_positions(), _bought_buildings)
    # Task #98: on the town map, rivals take customers where their
    # catchments overlap the store's (nearby_population above), so the flat
    # per-rival dilution is not applied on top.
    demand.rival_store_count = 0


func _rival_positions() -> Array:
    var positions: Array = []
    for rival in _rival_stores:
        positions.append(rival["position"])
    return positions


# The HUD's land value: the bought site's own land price today (task #95),
# or the town-wide figure when no site has been bought.
func _current_land_value_yen() -> int:
    if has_store_site():
        return int(round(float(store_site.start_land_price_yen(store_site_origin)) * land_price_growth_factor()))
    return _land_value_policy.current_land_price_yen(
        BASE_LAND_PRICE_YEN, town, float(month_count) / MONTHS_PER_YEAR
    )


func bought_buildings() -> Array[int]:
    return _bought_buildings.duplicate()


func chain_expansion_cost_yen() -> int:
    return _land_value_policy.current_land_price_yen(
        BASE_LAND_PRICE_YEN, town, float(month_count) / MONTHS_PER_YEAR
    ) * NEW_BRANCH_LAND_AREA_COUNT


func try_expand_chain() -> bool:
    # Task #100: allowed while customers are in the store -- this changes
    # no fixture, route or basket (during opening hours the store is almost
    # never empty, so waiting for it blocked the action for good).
    if is_game_over:
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


# Task #78: CONFIRMED_OFFICIAL that "入れ替え" (swap) exists as one of the
# interior-edit screen's 5 top-level commands, alongside 配置/移動/売却/
# 終了 (official PS screenshot ss02, docs/research/menu-hierarchy-
# evidence-2026-09-05.md / official-ui-state-reconstruction-2026-09-05.md),
# directly re-checked 2026-09-24 following the user's question about
# recreation fidelity drift. No source describes what exactly "入れ替え"
# does interactively beyond the command's name/existence, so this client's
# own reading -- exchanging two already-placed fixtures' positions in one
# atomic step, distinct from 移動's single-fixture relocate -- is this
# project's own REMAKE_BALANCED_DEFAULT interpretation, not a recovered
# original rule. Chosen because it is the one reading that is NOT already
# achievable via two sequential try_relocate_fixture() calls (a fully
# packed layout can leave no empty cell for either fixture to move
# through), which is the only sense in which a distinct third command is
# actually necessary alongside 配置/移動.
func try_swap_fixtures(fixture_id_a: String, fixture_id_b: String) -> bool:
    if is_game_over or not customers.all_settled() or _any_restock_task_active():
        return false
    var previous: Array = layout.fixture_snapshot()
    if not layout.try_swap_fixture_positions(fixture_id_a, fixture_id_b):
        return false
    _refresh_interactions()
    if not _required_routes_are_reachable() or not _all_staff_are_walkable():
        layout.restore_fixture_snapshot(previous)
        _refresh_interactions()
        return false
    _record_event("fixtures_swapped", {"fixture_id_a": fixture_id_a, "fixture_id_b": fixture_id_b})
    return true


# Task #78: CONFIRMED_OFFICIAL that "売却" (sell) exists as one of the
# interior-edit screen's 5 top-level commands (same ss02/menu-hierarchy
# citation as try_swap_fixtures() above). No source states the refund
# percentage a sold fixture actually returns, so FIXTURE_SELL_REFUND_
# PERCENT below is this project's own REMAKE_BALANCED_DEFAULT choice
# (half the catalog purchase price back, half lost -- a plausible middle
# ground between "no refund" and "full refund", not a recovered original
# value). Restricted to fixtures with a real fixture_catalog origin (no
# purchase_price_yen exists to refund from otherwise -- the prototype
# scenario's pre-catalog checkout-1/shelf-1/shelf-2 are not sellable),
# never the checkout fixture itself (this client's architecture assumes
# exactly one, config["simulation"]["checkout_fixture_id"], with no
# mechanic to reassign it), and never a fixture still holding procured
# stock -- same "reject rather than silently discard inventory" precedent
# try_load_sample_layout() already established, rather than inventing an
# auto-clear rule the evidence does not describe.
const FIXTURE_SELL_REFUND_PERCENT := 50


func try_sell_fixture(fixture_id: String) -> bool:
    if is_game_over or not customers.all_settled() or _any_restock_task_active():
        return false
    if not layout.fixtures_by_id.has(fixture_id):
        return false
    if fixture_id == str(config["simulation"]["checkout_fixture_id"]):
        return false
    var fixture: Dictionary = layout.fixtures_by_id[fixture_id]
    var catalog_id := str(fixture.get("catalog_id", ""))
    if catalog_id.is_empty() or not _fixture_catalog.has(catalog_id):
        return false
    for product in inventory.products.values():
        if str(product.fixture_id) == fixture_id:
            return false
    var previous: Array = layout.fixture_snapshot()
    if not layout.try_remove_fixture(fixture_id):
        return false
    _refresh_interactions()
    if not _required_routes_are_reachable() or not _all_staff_are_walkable():
        layout.restore_fixture_snapshot(previous)
        _refresh_interactions()
        return false
    var refund_yen: int = int(_fixture_catalog[catalog_id]["purchase_price_yen"]) * FIXTURE_SELL_REFUND_PERCENT / 100
    var expense: Dictionary = economy.record_explicit_expense(
        "fixture_sold",
        minute_of_day,
        -refund_yen,
        {"catalog_id": catalog_id, "instance_id": fixture_id}
    )
    _record_event("fixture_sold", {
        "catalog_id": catalog_id,
        "instance_id": fixture_id,
        "refund_yen": refund_yen,
        "expense_id": expense["expense_id"],
    })
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
    _note_dirty_cells()
    _step_cleaning_tasks()
    _step_staff_rest()


# Task #66: CONFIRMED_OFFICIAL passage-width rule, re-verified 2026-09-24 at
# 400dpi (quick reference guide, 店舗 section, book page 5): "1マス通路...
# 客や店員が2人並んで通れる幅。すれ違えるので混雑しにくい" / "1/2マス通路...
# 客や店員1人が通れる幅。すれ違うことができず、混雑しやすい。" This client's
# grid already splits every tile into `subcells_per_tile=2` subcells
# (store_layout.gd/reference_sim's store_grid.py) for exactly this reason,
# though until now that comment called the 0.5-tile granularity itself
# unconfirmed; it is confirmed now, and the rule it exists to support was
# simply never wired -- no two actors ever blocked each other's movement.
#
# Rather than compute an explicit corridor-width value (which would need a
# direction-aware geometric analysis the guide does not spell out further),
# this reproduces the same outcome as an emergent property of exclusive
# subcell occupancy: no two actors (customer or staff) may occupy the same
# subcell at once. A 2-subcell-wide (1 masu) passage always has a free
# parallel subcell for a second actor, so movement there is never blocked
# (matches "passable, does not congest"); a 1-subcell-wide (1/2 masu)
# corridor has nowhere for an oncoming actor to step aside, so movement
# blocks until the cell clears (matches "cannot pass, congests easily").
#
# A blocked actor waits in place rather than re-routing this tick. First-
# title evidence separately confirms multiple routes CAN let customers
# detour around congestion (PROJECT_MEMORY.md section 4), but does not say
# whether an individual blocked actor reroutes or simply waits its turn, so
# this project is not inventing that decision; "wait, retry next tick" is
# the minimal REMAKE_BALANCED_DEFAULT choice for this pass. A pathological
# store layout with only ever a single 1-wide route between two points
# could in principle deadlock two actors approaching each other -- this is
# a known, accepted limitation of this MVP, not silently worked around.
func _subcell_is_free_for(mover, target: Vector2i) -> bool:
    # Every fixture's interaction cell is a deliberate exception, not a
    # physical aisle subject to the passage-width rule. The checkout
    # interaction cell is the clearest case (task #36): every queued
    # customer's logical position converges on this single point
    # (store_view.gd offsets them only cosmetically for rendering), so
    # exclusive occupancy there would silently break the FIFO queue itself
    # (a second customer could never finish "arriving" to be enqueued).
    # Discovered by CI (task #66) that the same reasoning applies to shelf
    # interaction cells too: this smoke suite's shared-plan concurrency
    # scenario has two customers wanting the same product, so the second
    # customer would otherwise be blocked at the shelf's single interaction
    # point for the entire duration of the first customer's shopping_ticks
    # -- a "browsing the same shelf" contention this project has no evidence
    # for and is not modeling, as opposed to genuine aisle-corridor passing.
    for fixture in layout.fixtures_by_id.values():
        if target == _vec2i_from_array(fixture["interaction_subcell"]):
            return true
    for customer in customers.active_customers():
        if customer != mover and customer.position == target:
            return false
    for staff_member in staff.all_staff():
        # The checkout staff member is permanently stationed behind the
        # register (never assigned a route; state stays idle/checkout for
        # the whole simulation) rather than walking the floor like a
        # restocking staff member or a customer. Discovered by CI (task
        # #66): the default scenario's checkout staff start_subcell sits
        # immediately next to the checkout interaction cell, and without
        # this exemption a customer's ordinary route to/from a shelf could
        # be permanently blocked by staff who can structurally never step
        # aside -- unlike a genuinely passing pedestrian, which is what the
        # guide's passage-width rule is about. Same reasoning as the
        # checkout-interaction-cell exemption above, extended to the fixed
        # post next to it.
        if staff_member.staff_id == staff.checkout_staff_id:
            continue
        # Discovered by CI (task #66): an idle non-checkout staff member's
        # start_subcell is just a static home-base marker, not a modeled
        # physical stance -- this client has no "step aside while idle"
        # behavior, so treating an idle staff member as a permanent
        # obstacle is over-inventing beyond the guide's rule (which is
        # about two actors actively contending for the same aisle, not
        # furniture). A demonstrable case: relocating a shelf during this
        # smoke suite's own fixture-editing test shifted a customer route
        # to pass through idle staff-2's fixed position, permanently
        # blocking every subsequent visit. A staff member actively working
        # (to_restock/restocking) IS out on the floor and remains a real
        # obstacle, consistent with the guide's "客や店員が" wording.
        if staff_member.state == "idle":
            continue
        if staff_member != mover and staff_member.position == target:
            return false
    return true


func _try_move_along_route(mover, next_phase: String) -> bool:
    if not mover.route.is_empty() and not _subcell_is_free_for(mover, mover.route[0]):
        if not _try_detour(mover):
            return false
    return mover.move_along_route(next_phase)


# Task #87: CONFIRMED_COMMUNITY (PROJECT_MEMORY.md section 4, from the
# first-title wiki's 内装 page): "Multiple routes can allow customers to
# detour around congestion." When the next cell is taken, look for another
# route to the same goal around everyone currently standing in the way and
# take it if its first step is free; otherwise keep waiting (a 1/2-masu
# corridor with no way around still congests, per the passage-width rule
# above). Once customers could shop concurrently (tick()), the old "always
# wait" behavior let two shoppers heading at each other block forever.
func _try_detour(mover) -> bool:
    var goal: Vector2i = mover.route[mover.route.size() - 1]
    var occupied: Dictionary = {}
    for customer in customers.active_customers():
        if customer != mover and not _subcell_is_free_for(mover, customer.position):
            occupied[customer.position] = true
    for staff_member in staff.all_staff():
        if staff_member != mover and not _subcell_is_free_for(mover, staff_member.position):
            occupied[staff_member.position] = true
    var detour: Array[Vector2i] = layout.find_path_avoiding(mover.position, goal, occupied)
    if detour.is_empty() or not _subcell_is_free_for(mover, detour[0]):
        return false
    mover.route = detour
    return true


func _advance_customer(customer) -> void:
    match customer.phase:
        "to_shelf":
            if _try_move_along_route(customer, "shopping"):
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
                    line["unit_price_yen"] = _apply_price_policy(int(line["unit_price_yen"]))
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
            if _try_move_along_route(customer, "waiting_checkout"):
                _checkout_queue.append(customer.customer_id)
                _record_event("customer_queued_for_checkout", {
                    "customer_id": customer.customer_id,
                    "queue_position": _checkout_queue.size(),
                })
        "waiting_checkout":
            pass  # Dequeued by _dispatch_checkout_queue() once the checkout is free.
        "checkout":
            customer.checkout_ticks_remaining -= 1
            # Task #49/#51: a checkout service running unusually long
            # (relative to the confirmed CheckoutTiming reference duration)
            # angers the customer exactly once per checkout, applying the
            # confirmed -2 penalty. Task #51 corrected the penalty's scope:
            # the strategy guide, directly re-read (book pp.34-35,
            # "お客さんに怒られると店員全員の能力が下がってしまう"),
            # states CONFIRMED_OFFICIAL that an angry customer lowers EVERY
            # active staff member's ability, not only the one who served
            # them -- task #49 had scoped this down to the serving staff
            # member alone, a REMAKE_BALANCED_DEFAULT simplification this
            # stronger, officially-tier evidence now supersedes.
            if not customer.checkout_anger_triggered:
                var elapsed_ticks: int = (
                    customer.checkout_assigned_ticks - customer.checkout_ticks_remaining
                )
                if elapsed_ticks > _checkout_anger.trigger_ticks(_checkout_ticks):
                    customer.checkout_anger_triggered = true
                    var angry_checkout_staff = staff.checkout_staff()
                    var skills_by_staff: Dictionary = {}
                    for angered_staff_member in staff.all_staff():
                        skills_by_staff[angered_staff_member.staff_id] = (
                            _checkout_anger.apply_penalty(angered_staff_member)
                        )
                    # Task #65: the guide's own confirmed per-event rating
                    # modifier ("お客に怒られる=1/6の確率で-1", store_rating.gd's
                    # ANGRY_CUSTOMER_DOWNGRADE_PROBABILITY_*/DOWNGRADE_POINTS)
                    # was defined but never rolled anywhere, since no angry-
                    # customer trigger existed in this client when it was
                    # first ported (decision 0096). checkout_anger_triggered
                    # (task #49) is that trigger now, so this reuses the
                    # shared demand RNG for the roll -- the same "one shared
                    # random stream, not a new one per mechanic" convention
                    # task #55's incidental-want-product draw already
                    # established for this client.
                    var rating_penalty_applied := (
                        _demand_rng.randi_range(
                            1, StoreRatingScript.ANGRY_CUSTOMER_DOWNGRADE_PROBABILITY_DENOMINATOR
                        ) <= StoreRatingScript.ANGRY_CUSTOMER_DOWNGRADE_PROBABILITY_NUMERATOR
                    )
                    if rating_penalty_applied:
                        internal_rating_value = max(0, min(
                            100,
                            internal_rating_value + StoreRatingScript.ANGRY_CUSTOMER_DOWNGRADE_POINTS
                        ))
                        star_rating = _store_rating.star_rank_for_internal_value(internal_rating_value)
                    _record_event("checkout_anger_triggered", {
                        "customer_id": customer.customer_id,
                        "staff_id": angry_checkout_staff.staff_id,
                        "elapsed_ticks": elapsed_ticks,
                        "skills_by_staff": skills_by_staff,
                        "rating_penalty_applied": rating_penalty_applied,
                        "internal_rating_value": internal_rating_value,
                    })
            if customer.checkout_ticks_remaining <= 0:
                var checkout_staff = staff.checkout_staff()
                if not customer.basket.is_empty():
                    var record: Dictionary = economy.settle_basket(
                        customer.customer_id,
                        minute_of_day,
                        customer.basket
                    )
                    customer.mark_settled(record)
                    for line in customer.basket:
                        var bought_product = inventory.get_product(str(line["product_id"]))
                        if bought_product != null and not bought_product.catalog_id.is_empty():
                            survey_bought[bought_product.catalog_id] = (
                                int(survey_bought.get(bought_product.catalog_id, 0)) + int(line["quantity"])
                            )
                checkout_staff.state = "idle"
                _spend_stamina(checkout_staff)
                customer.phase = "leaving"
                customer.route = layout.find_path(customer.position, layout.exit)
                _record_event("checkout_completed", {
                    "customer_id": customer.customer_id,
                    "staff_id": checkout_staff.staff_id,
                    "transaction_id": customer.settled_transaction_id,
                })
                # Task #48: a completed checkout task is a confirmed work-
                # growth trigger (register_skill/service_skill), applied
                # whether or not the customer actually bought anything --
                # the guide's growth model is about performing the work
                # task, not the resulting transaction.
                var checkout_growth: Array[Dictionary] = _staff_growth.apply_checkout_growth(
                    checkout_staff
                )
                if not checkout_growth.is_empty():
                    _record_event("staff_skill_growth", {
                        "staff_id": checkout_staff.staff_id,
                        "task": "checkout",
                        "skills": checkout_growth,
                    })
        "leaving":
            if _try_move_along_route(customer, "done"):
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
    # Task #88: a checkout staff member walking back from the break room
    # (guide p.16) cannot ring anyone up until they are back behind the
    # register -- queued customers wait meanwhile, which is exactly why the
    # guide advises keeping the register close to the break room.
    if not checkout_staff.rest_phase.is_empty() or checkout_staff.position != checkout_staff.home_position():
        return
    var customer_id: String = _checkout_queue.pop_front()
    var customer = customers.customer(customer_id)
    customer.phase = "checkout"
    customer.checkout_ticks_remaining = _checkout_timing.required_ticks(
        checkout_staff.register_skill, _checkout_ticks
    )
    customer.checkout_assigned_ticks = customer.checkout_ticks_remaining
    checkout_staff.state = "checkout"
    _record_event("checkout_started", {
        "customer_id": customer.customer_id,
        "staff_id": checkout_staff.staff_id,
    })


func clock_text() -> String:
    return "%02d:%02d" % [minute_of_day / 60, minute_of_day % 60]


func snapshot() -> Dictionary:
    var checkout_staff = staff.checkout_staff()
    # Task #105: before the first customer of the day there is none.
    var customer = null
    if not customers.active_customer_id.is_empty():
        customer = customers.active()
    return {
        "minute_of_day": minute_of_day,
        "clock_text": clock_text(),
        "weather_display_label": weather_display_label(),
        "cash_yen": economy.cash_yen,
        "stock_units": inventory.total_stock_units(),
        "inventory": _inventory_snapshot(),
        "customer_id": customer.customer_id if customer != null else "",
        "customer_phase": customer.phase if customer != null else "none",
        "customer_position": customer.position if customer != null else layout.entry,
        "staff_id": checkout_staff.staff_id,
        "staff_state": checkout_staff.state,
        "staff_position": checkout_staff.position,
        "staff_count": staff.members.size(),
        "staff_roster": _staff_roster_snapshot(),
        "customer_basket_count": customer.basket.size() if customer != null else 0,
        "customer_basket_total_yen": customer.basket_total_yen() if customer != null else 0,
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
        # Task #75: the UI previously never displayed day/month progression
        # at all (only the intra-day clock_text). REPRESENTATIVE_DAYS_PER_
        # MONTH is the same CONFIRMED_OFFICIAL 4-day-per-month figure
        # _settle_month_end() already uses, so exposing this counter here
        # lets the UI show "day X of 4 this month" without inventing a
        # second calendar concept.
        "days_completed_this_month": _days_completed_this_month,
        "is_game_over": is_game_over,
        "game_over_reason": game_over_reason,
        "clear_condition_met": clear_condition_met,
        "permits_held": _permits_held.keys(),
        "popularity": popularity,
        "price_change_pct": price_change_pct,
        "town_population": town.population,
        "town_store_count_including_rivals": town.store_count_including_rivals,
        "land_value_yen": _current_land_value_yen(),
        "store_site_origin": [store_site_origin.x, store_site_origin.y],
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


# Task #55: CONFIRMED_OFFICIAL (docs/research/quick-reference-guide-part1-
# 2026-09-19.md, directly re-read book p.9): "顧客は購入希望の品を求めて
# 来店する。希望の品を購入した後、時間が許せばそのほかの商品も購入する。
# それぞれの顧客に3品程度の「ついでに欲しい品」があるので、それらを揃え
# ておくことも大切だ。" Every demand-driven customer now also wants
# roughly 3 additional in-stock products beyond their primary destination
# plan, purchased after it via the exact same existing plan/pickup
# machinery -- no new phase or mechanic was needed, only extending the
# plan array before admission. This client models no customer-patience/
# time-budget mechanic at all (PROJECT_MEMORY.md section 7's own standing
# HYPOTHESIS, still unconfirmed), so "時間が許せば" (if time allows) is
# simplified to "always" here, matching how the primary plan is already
# handled unconditionally -- REMAKE_BALANCED_DEFAULT, since inventing a
# time-budget/abandonment mechanic instead would be a much larger,
# unconfirmed addition than this task's narrow scope. The exact count (3,
# not "roughly 3") and the selection method (a uniform random draw from
# currently-stocked products, reusing the shared demand RNG rather than a
# new stream) are also this project's own REMAKE_BALANCED_DEFAULT choices:
# the guide's own bar chart of relative per-category incidental-purchase
# weight is single-playthrough example data, not a confirmed general
# game-data table, so it is deliberately not used as a weighting scheme.
# Deliberately scoped to demand-driven admission only (this function,
# covering both the automatic tick_idle_for_demand() path and the manual
# "Admit next customer" button, which both call this): the explicit/
# observed customer path (start_explicit_customer()) exists specifically
# to replay a caller-supplied EXACT plan and must stay uninflated by
# invented items.
const INCIDENTAL_WANT_PRODUCT_COUNT := 3


func _start_default_customer() -> void:
    var plan: Array[String] = customers.default_plan()
    if _building_demand_enabled and has_store_site():
        plan = _building_customer_plan()
        if plan.is_empty():
            return
    else:
        plan.append_array(_select_incidental_want_product_ids(plan))
    var customer = customers.admit_default(
        layout.entry,
        layout.find_path(
            layout.entry,
            _product_interaction(plan[0])
        ),
        plan
    )
    _record_customer_entered(customer)


# Task #102. CONFIRMED_OFFICIAL (guide DATA4, p.92-95): each building has
# its 主なほしい品物, and buildings in the 「朝から夜だけ客のいる建物」 list
# send no customers late at night (朝=7-11時 ... 夜=20-23時, 深夜=24-3時,
# 早朝=4-6時). Guide p.6: the store's customers are the residents of the
# buildings around it. REMAKE_BALANCED_DEFAULT: which building a customer
# comes from (chance in proportion to its squares in the store's catchment,
# shared with rivals like the nearby population), that they want up to
# INCIDENTAL_WANT_PRODUCT_COUNT of its wanted categories, that a category the
# store does not carry (or has sold out on every shelf) is noted in the
# month's survey instead, and that a customer who would find nothing does
# not come in. Real game only (staff_work.building_demand_enabled).
func _building_customer_plan() -> Array[String]:
    var night := minute_of_day < 7 * 60
    var candidates: Array = []
    var total := 0.0
    for index in _catchment_weights:
        var profile: Dictionary = store_site.building_profile(int(index))
        if night and not bool(profile.get("overnight", false)):
            continue
        candidates.append([int(index), float(_catchment_weights[index])])
        total += float(_catchment_weights[index])
    var plan: Array[String] = []
    if candidates.is_empty() or total <= 0.0:
        return plan
    var roll := _demand_rng.randf() * total
    var origin_index: int = int(candidates[candidates.size() - 1][0])
    for candidate in candidates:
        roll -= float(candidate[1])
        if roll <= 0.0:
            origin_index = int(candidate[0])
            break
    var wanted: Array = (store_site.building_profile(origin_index)["wanted"] as Array).duplicate()
    while not wanted.is_empty() and plan.size() < INCIDENTAL_WANT_PRODUCT_COUNT:
        var category := str(wanted.pop_at(_demand_rng.randi_range(0, wanted.size() - 1)))
        var shelves: Array[String] = []
        for product_id in inventory.product_order:
            var product = inventory.get_product(product_id)
            if product.catalog_id == category and product.stock_units > 0:
                shelves.append(product_id)
        if shelves.is_empty():
            survey_missing[category] = int(survey_missing.get(category, 0)) + 1
            continue
        plan.append(shelves[_demand_rng.randi_range(0, shelves.size() - 1)])
    return plan


func _select_incidental_want_product_ids(exclude_product_ids: Array[String]) -> Array[String]:
    var candidates: Array[String] = []
    for product_id in inventory.product_order:
        if not exclude_product_ids.has(product_id):
            candidates.append(product_id)
    var selected: Array[String] = []
    while not candidates.is_empty() and selected.size() < INCIDENTAL_WANT_PRODUCT_COUNT:
        var index: int = _demand_rng.randi_range(0, candidates.size() - 1)
        selected.append(candidates[index])
        candidates.remove_at(index)
    return selected


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


const SAVE_SCHEMA_VERSION := 9

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
#
# Also not saved/restored as of task #48: any register_skill/service_skill/
# replenishment_skill/cleaning_skill/security_skill growth staff members
# accumulated from completed work (StaffGrowth). load_state()'s staff.reset()
# call restores every skill to its config-derived starting value, same as
# every other subsystem this function's own comment already promises to
# clear "back to its config-derived starting point" -- so a save/load round
# trip currently reverts accumulated skill growth rather than preserving it.
# Extending the save format to persist current skill values is explicitly
# out of scope for task #48 (see decision 0117).
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
        "expense_index_at_month_start": _expense_index_at_month_start,
        "is_game_over": is_game_over,
        "game_over_reason": game_over_reason,
        "clear_condition_met": clear_condition_met,
        "popularity": popularity,
        "price_change_pct": price_change_pct,
        "internal_rating_value": internal_rating_value,
        "star_rating": star_rating,
        "player_store_count": player_store_count,
        # Task #95 (schema 6): the bought site and the buildings cleared for it.
        "store_site_origin": [store_site_origin.x, store_site_origin.y],
        "bought_buildings": _bought_buildings.duplicate(),
        # Task #101 (schema 7): rivals bought out and rivals investigated.
        "bought_rival_ids": owned_branches.map(func(branch): return str(branch["id"])),
        "investigated_rival_ids": _investigated_rivals.keys(),
        # Task #106 (schema 9): where each rival stands now, its losing
        # months, and the branches waiting to open again.
        "rival_stores": _rival_stores.map(func(rival): return {
            "id": str(rival["id"]),
            "position": [rival["position"].x, rival["position"].y],
            "deficit_months": int(rival["deficit_months"]),
        }),
        "rivals_to_reopen": _rivals_to_reopen.map(func(waiting): return {
            "id": str(waiting["id"]),
            "left": [waiting["left"].x, waiting["left"].y],
        }),
        # Task #103 (schema 8).
        "business_hours_id": business_hours_id,
        # Task #104 (schema 9): which store stands on the site.
        "store_type_id": store_type_id,
        "weather_category_index": weather_category_index,
        "chain_visitor_milestone": {
            "last_observed_total": _chain_visitor_milestone.last_observed_total,
            "next_threshold": _chain_visitor_milestone.next_threshold,
            "events": _chain_visitor_milestone.events.duplicate(true),
        },
        "permits_held": _permits_held.keys(),
        "promotions_used_this_month": _promotions_used_this_month.keys(),
        "scheduled_promotions": _scheduled_promotions.duplicate(true),
        # Task #56: which candidate currently occupies each roster slot is
        # now player-changeable (try_hire_candidate()), so it can no longer
        # be assumed to always match config's own static staff.members --
        # persisted here so a load reapplies any hire the config-derived
        # staff.reset() below would otherwise silently revert.
        "staff_roster": _staff_roster_snapshot(),
        # Task #107 (schema 9): each staff member's grown skills and 体力,
        # and this month's and last month's survey, which a load used to
        # put back to their starting values.
        "staff_state": _staff_state_snapshot(),
        "survey": {
            "bought": survey_bought.duplicate(),
            "missing": survey_missing.duplicate(),
            "last": last_survey.duplicate(true),
        },
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
    # Task #104: the saved store may be another type than the one this
    # simulation stands in; build that one first (and put this one back if
    # the save does not fit it after all).
    var saved_type := str(data["store_type_id"])
    var previous_type := store_type_id
    if saved_type != store_type_id:
        if saved_type.is_empty() or not GuideStartingStoreScript.store_type_entry(config, saved_type).has("layout"):
            return false
        _build_store_type(saved_type)
    if not layout.fixture_snapshot_is_valid(data["fixtures"]):
        if previous_type != store_type_id:
            _build_store_type(previous_type)
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
    # Task #74: reset() itself clears this right after the same five calls
    # above, but load_state() had never done so -- a save taken while a
    # second customer was queued at checkout (_checkout_queue non-empty)
    # left that customer_id behind after customers.reset() had already
    # discarded the actual customer record, so the next
    # _dispatch_checkout_queue() call would null-dereference it. Found by
    # directly auditing this function against reset()'s own gap-clearing.
    _checkout_queue.clear()
    # Task #56: staff.reset() above restores every slot to its config-
    # derived DEFAULT candidate, undoing any try_hire_candidate() swap the
    # player made since starting. Reapply the saved roster directly via
    # StaffState.hire() (not the guarded _apply_hire()/try_hire_candidate()
    # path): that path's cross-slot collision check compares against
    # every OTHER slot's CURRENT candidate, which can spuriously reject a
    # legitimate two-slot swap reload if applied one entry at a time right
    # after a reset (e.g. slot A's saved candidate can momentarily still
    # match slot B's not-yet-overwritten default). Saved data was only
    # ever produced by a hire that already passed that check when it
    # happened, so re-trusting it here (the same convention
    # _require_save_data() already applies to every other field) is safe.
    for roster_entry in data["staff_roster"]:
        var roster_staff_id := str(roster_entry["staff_id"])
        var roster_candidate_id := str(roster_entry["candidate_id"])
        if staff.members.has(roster_staff_id) and _staff_candidate_catalog.has(roster_candidate_id):
            staff.members[roster_staff_id].hire(_staff_candidate_catalog[roster_candidate_id])
    event_log.reset()
    _reset_stamina()
    _restore_staff_state(data["staff_state"])
    survey_bought = _counts(data["survey"]["bought"])
    survey_missing = _counts(data["survey"]["missing"])
    last_survey = {}
    if not (data["survey"]["last"] as Dictionary).is_empty():
        last_survey = {
            "bought": _counts(data["survey"]["last"]["bought"]),
            "missing": _counts(data["survey"]["last"]["missing"]),
        }
    minute_of_day = int(data["minute_of_day"])
    day_count = int(data["day_count"])
    month_count = int(data["month_count"])
    _days_completed_this_month = int(data["days_completed_this_month"])
    _cash_at_month_start = int(data["cash_at_month_start"])
    _revenue_at_month_start = int(data["revenue_at_month_start"])
    _expense_index_at_month_start = int(data["expense_index_at_month_start"])
    is_game_over = bool(data["is_game_over"])
    game_over_reason = str(data["game_over_reason"])
    clear_condition_met = bool(data["clear_condition_met"])
    popularity = int(data["popularity"])
    price_change_pct = int(data["price_change_pct"])
    internal_rating_value = int(data["internal_rating_value"])
    star_rating = int(data["star_rating"])
    player_store_count = int(data["player_store_count"])
    _load_rivals()
    for rival_id in data["bought_rival_ids"]:
        var rival_index := _rival_index(str(rival_id))
        if rival_index >= 0:
            owned_branches.append({"id": str(rival_id), "position": _rival_stores[rival_index]["position"]})
            _rival_stores.remove_at(rival_index)
    _rival_stores.clear()
    for rival_data in data["rival_stores"]:
        _rival_stores.append(_rival_store(
            str(rival_data["id"]), _vec2i_from_array(rival_data["position"]), int(rival_data["deficit_months"])
        ))
    for waiting in data["rivals_to_reopen"]:
        _rivals_to_reopen.append({"id": str(waiting["id"]), "left": _vec2i_from_array(waiting["left"])})
    for rival_id in data["investigated_rival_ids"]:
        _investigated_rivals[str(rival_id)] = true
    if not _business_hours.is_empty():
        _apply_business_hours(str(data["business_hours_id"]))
    _clear_store_site()
    var saved_site := _vec2i_from_array(data["store_site_origin"])
    if saved_site != NO_STORE_SITE and store_site != null:
        _apply_store_site(saved_site, data["bought_buildings"])
    _apply_weather(int(data["weather_category_index"]))
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
    _start_opening_customer()
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
    # Task #89: with no fixed default plan (the guide starting store), any
    # stocked product can be a visit's want, so every shelf must stay
    # reachable from the entrance.
    if (config["customer"]["visit_plan_product_ids"] as Array).is_empty():
        for product_id in inventory.product_order:
            if not layout.has_path(layout.entry, _product_interaction(product_id)):
                return false
    return layout.has_path(cursor, _checkout_interaction) and layout.has_path(
        _checkout_interaction,
        layout.exit
    )


func _vec2i_from_array(value: Array) -> Vector2i:
    return Vector2i(int(value[0]), int(value[1]))


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


const SAVED_STAFF_FIELDS := [
    "service_skill", "security_skill", "cleaning_skill", "register_skill",
    "replenishment_skill", "stamina", "exhausted",
]


# Survey counts come back from a JSON save as floats.
func _counts(source: Dictionary) -> Dictionary:
    var result := {}
    for key in source:
        result[str(key)] = int(source[key])
    return result


func _staff_state_snapshot() -> Array[Dictionary]:
    var rows: Array[Dictionary] = []
    for staff_member in staff.all_staff():
        var row := {"staff_id": staff_member.staff_id}
        for field in SAVED_STAFF_FIELDS:
            row[field] = staff_member.get(field)
        rows.append(row)
    return rows


func _restore_staff_state(rows: Array) -> void:
    for row in rows:
        var staff_id := str(row["staff_id"])
        if not staff.members.has(staff_id):
            continue
        var staff_member = staff.members[staff_id]
        for field in SAVED_STAFF_FIELDS:
            if field == "exhausted":
                staff_member.exhausted = bool(row[field])
            else:
                staff_member.set(field, int(row[field]))


func _staff_roster_snapshot() -> Array[Dictionary]:
    var rows: Array[Dictionary] = []
    for staff_member in staff.all_staff():
        rows.append({
            "staff_id": staff_member.staff_id,
            "candidate_id": staff_member.candidate_id,
            "display_name": staff_member.display_name,
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
    _apply_daily_fixture_maintenance()
    _apply_daily_staff_wages()
    if _days_completed_this_month >= REPRESENTATIVE_DAYS_PER_MONTH:
        _settle_month_end()
    # After _settle_month_end() so a month rollover rolls from the new
    # month's row.
    _roll_weather()


# Task #85: the per-month category weights are CONFIRMED_OFFICIAL (see
# config["weather"]["evidence_note"]). REMAKE_BALANCED_DEFAULT: rolling
# exactly once per day (at start and at each day boundary) is this
# project's own placeholder -- the original can change weather mid-day
# but no source states how often.
func _roll_weather() -> void:
    var weights: Array = config["weather"]["monthly_percentages"][month_count % MONTHS_PER_YEAR]
    var roll := _weather_rng.randi_range(1, 100)
    var cumulative := 0
    for index in range(weights.size()):
        cumulative += int(weights[index])
        if roll <= cumulative:
            _apply_weather(index)
            return
    _apply_weather(weights.size() - 1)


func _apply_weather(category_index: int) -> void:
    weather_category_index = category_index
    demand.is_bad_weather = config["weather"]["bad_weather_categories"].has(weather_category())


func weather_category() -> String:
    return str(config["weather"]["categories"][weather_category_index])


func weather_display_label() -> String:
    return str(config["weather"]["display_labels"][weather_category_index])


# Task #50: both maintenance_yen_per_day and salary_yen_per_day_24h are
# stated by the strategy guide to be a 24-hour-basis daily figure that is
# actually charged in proportion to the store's configured business hours,
# not a flat per-day amount -- CONFIRMED_OFFICIAL, independently stated
# twice for wages and once for maintenance
# (docs/research/quick-reference-guide-part1-2026-09-19.md section 1.2:
# "維持費...営業時間に応じて、毎日売上げから差し引かれる" / "人件費...時給
# ×営業時間...営業時間0時間の臨時休業日は、日給表示も0円"). demand.
# opening_minutes_per_day is this client's own single existing "configured
# business hours" quantity (DemandPolicy already uses it to spread expected
# arrivals across the open window), so it is reused here rather than
# inventing a second one. The floor-rounding to a whole yen amount below is
# this project's own REMAKE_BALANCED_DEFAULT choice -- the guide states the
# proportional relationship but never an explicit sub-yen rounding rule --
# matching the same floor-and-clamp convention CheckoutTiming/RestockTiming
# already use for their own invented scaling shapes.
func _scale_yen_to_configured_business_hours(value_at_24h_basis: int) -> int:
    const MINUTES_PER_24H_DAY := 24 * 60
    return int(floor(
        float(value_at_24h_basis) * demand.opening_minutes_per_day / float(MINUTES_PER_24H_DAY)
    ))


# Task #46/#50: maintenance_yen_per_day exists as CONFIRMED_OFFICIAL data on
# every fixture_catalog entry. This sums, across every currently-owned
# fixture that actually has a fixture_catalog origin (skipping the
# prototype scenario's shelf-1/shelf-2/checkout-1, which predate the
# catalog system and have no confirmed maintenance figure to charge), each
# fixture's own 24h-basis maintenance_yen_per_day scaled down to the
# store's configured opening_minutes_per_day (see
# _scale_yen_to_configured_business_hours above), and deducts the total
# once per simulated day. This happens inside the 4-simulated-day window
# _settle_month_end() later reads via economy.cash_yen's own delta, so it
# is automatically included in that month's x8 projection with no separate
# scaling logic of its own. A day with nothing to charge (the prototype
# scenario's own two starting fixtures, before any catalog fixture is
# purchased) records no expense at all rather than a redundant zero-yen
# entry every single day.
func _apply_daily_fixture_maintenance() -> void:
    var total_maintenance_yen := 0
    for fixture in layout.fixtures:
        var catalog_id := str(fixture.get("catalog_id", ""))
        if catalog_id.is_empty() or not _fixture_catalog.has(catalog_id):
            continue
        var catalog_entry: Dictionary = _fixture_catalog[catalog_id]
        if catalog_entry.has("maintenance_yen_per_day"):
            total_maintenance_yen += _scale_yen_to_configured_business_hours(
                int(catalog_entry["maintenance_yen_per_day"])
            )
    if total_maintenance_yen <= 0:
        return
    var expense: Dictionary = economy.record_explicit_expense(
        "fixture_maintenance", minute_of_day, total_maintenance_yen
    )
    _record_event("fixture_maintenance_charged", {
        "total_maintenance_yen": total_maintenance_yen,
        "expense_id": expense["expense_id"],
    })


# Task #47/#50: salary_yen_per_day_24h exists as CONFIRMED_OFFICIAL data on
# every active staff.members entry (task #32 duplicated it, along with the
# five skills, from its bound staff_candidates card). This charges every
# active staff member's own 24h-basis salary_yen_per_day_24h scaled down to
# the store's configured opening_minutes_per_day (see
# _scale_yen_to_configured_business_hours above) once per simulated day.
# This client still has no shift/hours-worked tracking for individual staff
# (StaffState is a task-based idle/to_restock/restocking/checkout state
# machine, not a clocked shift), but that is no longer needed here: the
# guide's own formula scales by the *store's* configured business hours,
# not by how many of those hours each individual staff member personally
# worked, so no new per-staff tracking has to be invented to apply it. Same
# "no expense on a zero-total day" choice as fixture maintenance, though in
# practice this client always has at least the two starting staff members,
# so that branch is unreachable today -- kept for parity and so it remains
# correct if a future hiring/firing UI ever lets the roster go empty.
func _apply_daily_staff_wages() -> void:
    var total_wages_yen := 0
    for staff_member in staff.all_staff():
        total_wages_yen += _scale_yen_to_configured_business_hours(
            staff_member.salary_yen_per_day_24h
        )
    if total_wages_yen <= 0:
        return
    var expense: Dictionary = economy.record_explicit_expense(
        "staff_wages", minute_of_day, total_wages_yen
    )
    _record_event("staff_wages_charged", {
        "total_wages_yen": total_wages_yen,
        "expense_id": expense["expense_id"],
    })


func _capital_spent_this_month_yen() -> int:
    var total := 0
    for index in range(_expense_index_at_month_start, economy.expense_records.size()):
        var record: Dictionary = economy.expense_records[index]
        if CAPITAL_EXPENSE_TYPES.has(str(record["expense_type"])):
            total += int(record["amount_yen"])
    return total


func _settle_month_end() -> void:
    var capital_yen := _capital_spent_this_month_yen()
    var four_day_net_result_yen: int = economy.cash_yen - _cash_at_month_start + capital_yen
    var month_result_yen: int = four_day_net_result_yen * MONTH_MULTIPLIER
    var adjustment_yen: int = month_result_yen - four_day_net_result_yen
    var record: Dictionary = economy.record_month_end_settlement(
        minute_of_day,
        adjustment_yen,
        {
            "month_number": month_count + 1,
            "four_day_net_result_yen": four_day_net_result_yen,
            "month_result_yen": month_result_yen,
            "capital_yen": capital_yen,
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
    last_survey = {"bought": survey_bought.duplicate(), "missing": survey_missing.duplicate()}
    survey_bought.clear()
    survey_missing.clear()
    month_count += 1
    _days_completed_this_month = 0
    _cash_at_month_start = economy.cash_yen
    _revenue_at_month_start = economy.recorded_revenue_yen()
    _expense_index_at_month_start = economy.expense_records.size()
    _promotions_used_this_month.clear()
    _step_rivals_at_month_end()
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
    # Task #53: price_change_pct now reflects the player's own configured
    # price policy (try_set_price_policy()) instead of always being 0.
    var evaluation: Dictionary = _store_rating.evaluate_monthly_rating_change(
        internal_rating_value,
        price_change_pct,
        service_value,
        security_value,
        cleaning_value,
        monthly_sales_yen
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


# Task #88: CONFIRMED_OFFICIAL, strategy guide p.16 (PDF1 page 6,
# 「レジの場所」): 「お客さんがいないとき店員は休憩室で休んでいる。だから
# レジと休憩室の距離が近いほうが、すぐにレジに向かうことができて便利なのだ。」
# While no customer is in the store, every idle staff member walks to the
# break room's door and rests there; as soon as a customer is in the store
# again they walk back to their post (the checkout staff member back behind
# the register, see _dispatch_checkout_queue()). A staff member called to a
# restock task leaves the cycle immediately (begin_restock() clears
# rest_phase). Not modeled yet: stamina (guide p.17: 「休憩室は、疲れた店員
# のスタミナを回復する大事な場所」, community wiki: stamina 0 -> back to the
# break room until fully recovered), so break_room_1 and break_room_2
# currently behave the same. A store with no break room keeps every staff
# member at their post.
func _step_staff_rest() -> void:
    var door := _break_room_door()
    var store_is_empty: bool = customers.all_settled()
    for staff_member in staff.all_staff():
        if staff_member.state != "idle":
            continue
        var wants_rest: bool = (store_is_empty or staff_member.exhausted) and door != NO_BREAK_ROOM_DOOR
        if wants_rest:
            if staff_member.position == door:
                _recover_stamina(staff_member)
                if staff_member.rest_phase != "resting":
                    staff_member.rest_phase = "resting"
                    staff_member.route.clear()
                    _record_event("staff_rest_started", {"staff_id": staff_member.staff_id})
                continue
            if staff_member.rest_phase != "to_break_room" or not _route_ends_at(staff_member, door):
                staff_member.route = layout.find_path(staff_member.position, door)
                staff_member.rest_phase = "to_break_room"
            _step_staff_walk(staff_member)
        else:
            if staff_member.rest_phase.is_empty():
                continue
            var home: Vector2i = staff_member.home_position()
            if staff_member.position == home:
                staff_member.rest_phase = ""
                staff_member.route.clear()
                continue
            if staff_member.rest_phase != "to_post" or not _route_ends_at(staff_member, home):
                if staff_member.rest_phase == "resting" or staff_member.rest_phase == "to_break_room":
                    _record_event("staff_returning_to_post", {"staff_id": staff_member.staff_id})
                staff_member.route = layout.find_path(staff_member.position, home)
                staff_member.rest_phase = "to_post"
            if _step_staff_walk(staff_member) and staff_member.position == home:
                staff_member.rest_phase = ""


const NO_BREAK_ROOM_DOOR := Vector2i(-1, -1)

# Task #99: stamina. CONFIRMED_COMMUNITY (first-title staff wiki, docs/
# research/behavior-rules-evidence-2026-09-05.md section 7): checkout,
# restocking and cleaning use up 体力; at 0 the staff member goes back to
# the break room and rests there until fully recovered; resting recovers 1
# at a time, with a chance of 2 that rises with 敏捷性 (about 90% at 100,
# an observed figure). Each member's maximum is their CONFIRMED_OFFICIAL
# printed 体力 (staff_candidates). REMAKE_BALANCED_DEFAULT: each finished
# task (one checkout, one shelf refilled, one spot cleaned) costs 1; resting
# recovers once per game minute, +2 with chance 0.9 x 敏捷性 / 100 (a straight
# line through the one observed point). Only in the real game
# (guide_starting_store.staff_work.stamina_enabled). Not saved: after a load
# everyone starts rested, like the other mid-task staff state.
func _reset_stamina() -> void:
    _stamina_rng.seed = int(config["demand"]["rng_seed"]) + 99
    for staff_member in staff.all_staff():
        var candidate: Dictionary = _staff_candidate_catalog.get(staff_member.candidate_id, {})
        staff_member.stamina_max = int(candidate.get("stamina", 0))
        staff_member.stamina = staff_member.stamina_max
        staff_member.exhausted = false


func _spend_stamina(staff_member) -> void:
    if not _stamina_enabled or staff_member.stamina_max <= 0:
        return
    staff_member.stamina = maxi(0, staff_member.stamina - 1)
    if staff_member.stamina == 0 and not staff_member.exhausted:
        staff_member.exhausted = true
        _record_event("staff_exhausted", {"staff_id": staff_member.staff_id})


func _recover_stamina(staff_member) -> void:
    if not _stamina_enabled or staff_member.stamina >= staff_member.stamina_max:
        if staff_member.exhausted and staff_member.stamina >= staff_member.stamina_max:
            staff_member.exhausted = false
        return
    var agility := int(_staff_candidate_catalog.get(staff_member.candidate_id, {}).get("agility", 0))
    var gain := 2 if _stamina_rng.randf() < 0.9 * float(agility) / 100.0 else 1
    staff_member.stamina = mini(staff_member.stamina_max, staff_member.stamina + gain)
    if staff_member.stamina >= staff_member.stamina_max:
        staff_member.exhausted = false


func _break_room_door() -> Vector2i:
    for fixture in layout.fixtures:
        if str(fixture["kind"]) == "break_room":
            return _vec2i_from_array(fixture["interaction_subcell"])
    return NO_BREAK_ROOM_DOOR


func _route_ends_at(mover, goal: Vector2i) -> bool:
    return not mover.route.is_empty() and mover.route[mover.route.size() - 1] == goal


# One step along a staff member's rest-cycle route, with the same
# occupancy/detour rules as every other mover. Returns true once the route
# is used up. A route cell that became blocked (the player moved a fixture
# while staff were resting) forces a fresh path next tick.
func _step_staff_walk(mover) -> bool:
    if mover.route.is_empty():
        return true
    var next_cell: Vector2i = mover.route[0]
    if not layout.is_walkable(next_cell) and next_cell != mover.route[mover.route.size() - 1]:
        mover.route.clear()
        mover.rest_phase = "stale"
        return false
    if not _subcell_is_free_for(mover, next_cell):
        if not _try_detour(mover):
            return false
    mover.position = mover.route.pop_front()
    return mover.route.is_empty()


func _step_restock_tasks() -> void:
    for staff_member in staff.all_staff():
        if staff_member.staff_id == staff.checkout_staff_id:
            continue
        match staff_member.state:
            "to_restock":
                if _try_move_along_route(staff_member, "restocking"):
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
    # Task #48: a completed restock task is a confirmed work-growth
    # trigger (replenishment_skill/cleaning_skill/security_skill),
    # applied whether or not any units actually needed restocking (the
    # guide's growth model is about performing the work task, not its
    # economic result) -- same rationale as checkout growth above.
    var restock_growth: Array[Dictionary] = _staff_growth.apply_replenish_growth(staff_member)
    if not restock_growth.is_empty():
        _record_event("staff_skill_growth", {
            "staff_id": staff_member.staff_id,
            "task": "replenish",
            "skills": restock_growth,
        })
    staff_member.finish_restock()
    _spend_stamina(staff_member)


func _assign_idle_restock_tasks() -> void:
    if not _restock_task_enabled:
        return
    var claimed_product_ids: Dictionary = {}
    for staff_member in staff.all_staff():
        if staff_member.staff_id != staff.checkout_staff_id and staff_member.state in ["to_restock", "restocking"]:
            claimed_product_ids[staff_member.restock_target_product_id] = true
    for product_id in inventory.product_order:
        if claimed_product_ids.has(product_id):
            continue
        if inventory.get_product(product_id).stock_units > restock_trigger_units(inventory.get_product(product_id)):
            continue
        var idle_staff = _find_idle_restock_staff()
        if idle_staff == null:
            return
        idle_staff.begin_restock(product_id, layout.find_path(idle_staff.position, _product_interaction(product_id)))
        claimed_product_ids[product_id] = true


# Task #97: the stock level at or below which a staff member goes to refill
# a shelf. The guide/community only say staff notice shelves going down and
# refill them on their own (docs/research/inventory-restock-boundary-
# 2026-09-05.md section 2: exact trigger unknown). REMAKE_BALANCED_DEFAULT:
# in the real game (restock_trigger_share_of_full = 8/9) a staff member
# goes once the shelf picture has lost an item (store_view.gd shows 9 items
# per tile); the prototype scenarios keep the fixed unit threshold.
func restock_trigger_units(product) -> int:
    return maxi(
        _restock_trigger_stock_units_at_or_below,
        int(floor(float(product.initial_stock_units) * _restock_trigger_share_of_full))
    )


# Task #97: cleaning. CONFIRMED: staff clean the store on their own
# (behavior-rules-evidence, first-title FAQ: they even clean and restock
# while closed), and cleaning grows 清掃 and セキュリティ (guide p.26
# 「仕事内容とパラメータ変化の関係」). REMAKE_BALANCED_DEFAULT: what needs
# cleaning -- the floor squares customers have walked on since they were
# last cleaned -- how long one spot takes (the restock duration scaled by
# the cleaner's own cleaning_skill, same shape as RestockTiming), and that
# restocking and resting come first.
func _note_dirty_cells() -> void:
    if not _cleaning_task_enabled:
        return
    for customer in customers.active_customers():
        var cell: Vector2i = customer.position
        if _dirty_cells.has(cell) or not layout.is_walkable(cell):
            continue
        _dirty_cells.append(cell)
        if _dirty_cells.size() > MAX_DIRTY_CELLS:
            _dirty_cells.remove_at(0)


func dirty_cells() -> Array[Vector2i]:
    return _dirty_cells.duplicate()


func _step_cleaning_tasks() -> void:
    if not _cleaning_task_enabled:
        return
    for staff_member in staff.all_staff():
        if staff_member.staff_id == staff.checkout_staff_id:
            continue
        match staff_member.state:
            "to_clean":
                if _step_staff_walk(staff_member):
                    if staff_member.rest_phase == "stale":
                        staff_member.state = "idle"
                        continue
                    staff_member.state = "cleaning"
                    staff_member.restock_ticks_remaining = _restock_timing.required_ticks(
                        staff_member.cleaning_skill, _restock_ticks
                    )
            "cleaning":
                staff_member.restock_ticks_remaining -= 1
                if staff_member.restock_ticks_remaining <= 0:
                    _dirty_cells.erase(staff_member.position)
                    var growth: Array[Dictionary] = _staff_growth.apply_clean_growth(staff_member)
                    _record_event("staff_cleaned", {
                        "staff_id": staff_member.staff_id,
                        "cell": [staff_member.position.x, staff_member.position.y],
                    })
                    if not growth.is_empty():
                        _record_event("staff_skill_growth", {
                            "staff_id": staff_member.staff_id,
                            "task": "clean",
                            "skills": growth,
                        })
                    staff_member.state = "idle"
                    # Walk back to the post afterwards (see _step_staff_rest).
                    staff_member.rest_phase = "stale"
                    _spend_stamina(staff_member)
    # Refilling comes first: while a shelf is waiting for someone, a staff
    # member who just became free is left for _assign_idle_restock_tasks().
    if customers.all_settled() or _shelf_waiting_for_restock():
        return
    for staff_member in staff.all_staff():
        if staff_member.staff_id == staff.checkout_staff_id or staff_member.state != "idle" or staff_member.exhausted:
            continue
        var target := _next_dirty_cell_for(staff_member)
        if target == NO_BREAK_ROOM_DOOR:
            return
        staff_member.route = layout.find_path(staff_member.position, target)
        staff_member.rest_phase = ""
        staff_member.state = "to_clean"


func _shelf_waiting_for_restock() -> bool:
    if not _restock_task_enabled:
        return false
    var claimed: Dictionary = {}
    for staff_member in staff.all_staff():
        if staff_member.state in ["to_restock", "restocking"]:
            claimed[staff_member.restock_target_product_id] = true
    for product_id in inventory.product_order:
        var product = inventory.get_product(product_id)
        if not claimed.has(product_id) and product.stock_units <= restock_trigger_units(product):
            return true
    return false


# The oldest dirty square nobody is already heading to or standing on.
func _next_dirty_cell_for(cleaner) -> Vector2i:
    var claimed := {}
    for staff_member in staff.all_staff():
        if staff_member != cleaner and (staff_member.state == "to_clean" or staff_member.state == "cleaning"):
            if not staff_member.route.is_empty():
                claimed[staff_member.route[staff_member.route.size() - 1]] = true
            claimed[staff_member.position] = true
    for cell in _dirty_cells:
        if not claimed.has(cell) and layout.is_walkable(cell):
            return cell
    return NO_BREAK_ROOM_DOOR


func _find_idle_restock_staff():
    for staff_member in staff.all_staff():
        if staff_member.staff_id != staff.checkout_staff_id and staff_member.state == "idle" and not staff_member.exhausted:
            return staff_member
    return null


func _any_restock_task_active() -> bool:
    for staff_member in staff.all_staff():
        if staff_member.staff_id != staff.checkout_staff_id and staff_member.state in ["to_restock", "restocking"]:
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
        "expense_index_at_month_start",
        "is_game_over",
        "game_over_reason",
        "clear_condition_met",
        "popularity",
        "price_change_pct",
        "internal_rating_value",
        "star_rating",
        "player_store_count",
        "store_site_origin",
        "bought_buildings",
        "bought_rival_ids",
        "investigated_rival_ids",
        "rival_stores",
        "rivals_to_reopen",
        "business_hours_id",
        "store_type_id",
        "weather_category_index",
        "chain_visitor_milestone",
        "permits_held",
        "promotions_used_this_month",
        "scheduled_promotions",
        "staff_roster",
        "staff_state",
        "survey",
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
    assert(int(config.get("schema_version", -1)) == 15)
    for key in ["store", "fixtures", "sample_layouts", "fixture_catalog", "permits", "product_catalog", "promotions", "products", "economy", "provisional_restock", "staff", "staff_candidates", "customer", "simulation", "demand", "weather", "town"]:
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
    var weather_config: Dictionary = config["weather"]
    for key in ["categories", "monthly_percentages", "display_labels", "bad_weather_categories", "rng_seed"]:
        if not weather_config.has(key):
            push_error("vertical slice weather config missing required key: %s" % key)
            assert(false)
    assert(weather_config["monthly_percentages"].size() == MONTHS_PER_YEAR)
    for month_row in weather_config["monthly_percentages"]:
        assert(month_row.size() == weather_config["categories"].size())
        var month_total := 0
        for percent in month_row:
            month_total += int(percent)
        assert(month_total == 100)
    assert(weather_config["display_labels"].size() == weather_config["categories"].size())
    for catalog_entry in config["fixture_catalog"]:
        for key in ["catalog_id", "kind", "footprint_tiles", "purchase_price_yen"]:
            if not catalog_entry.has(key):
                push_error("fixture catalog entry missing required key: %s" % key)
                assert(false)
    for permit_entry in config["permits"]:
        for key in ["permit_id", "fee_yen", "exclusion_distance_tiles"]:
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
    for key in ["population", "store_count_including_rivals", "player_store_position"]:
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
