extends SceneTree

const Simulation := preload("res://scripts/vertical_slice_simulation.gd")
const Guide := preload("res://scripts/domain/guide_starting_store.gd")
const Statement := preload("res://scripts/domain/operating_statement.gd")
const ConfigPath := "res://data/vertical_slice.json"


func _initialize() -> void:
    Engine.set_meta("legacy_guide_fixture", true)
    call_deferred("_run")


var failures := 0


func _check(ok: bool, message: String) -> void:
    if not ok:
        failures += 1
        push_error(message)


func _run() -> void:
    var examples: Array = JSON.parse_string(FileAccess.get_file_as_string("res://tests/fixtures/operating_statement.json"))
    for example in examples:
        var projected := Statement.project(example["representative"])
        _check(projected["four_day_net_result_yen"] == example["profit"], "source ledger profit")
        _check(projected["month_result_yen"] == example["monthly_profit"], "source monthly projection")
        _check(projected["adjustment_yen"] == example["cash_adjustment"], "source cash adjustment")
    var config: Dictionary = JSON.parse_string(FileAccess.get_file_as_string(ConfigPath))
    config["economy"]["initial_cash_yen"] = 100000000
    config = Guide.apply(config)
    var sim = Simulation.new(config)
    # Explicit source-ledger setup: exercise actual client expense, robbery,
    # save/load and month-close paths, not a second copy of their formulas.
    sim._store_sales_yen = 1000
    var lines: Array[Dictionary] = [{"product_id": "fixture-sale", "quantity": 1, "unit_price_yen": 1000}]
    sim.economy.settle_basket("fixture-customer", 0, lines)
    sim.economy.record_explicit_expense("fixture_purchase", 0, 20000)
    sim.economy.record_explicit_expense("contest_prize", 0, -50000)
    sim.economy.record_explicit_expense("inventory_restock", 0, 100)
    sim.economy.record_explicit_expense("staff_wages", 0, 200)
    sim.economy.record_explicit_expense("fixture_maintenance", 0, 300)
    sim.economy.record_explicit_expense("promotion_cost", 0, 400)
    var before: Dictionary = sim.month_operating_statement()
    _check(before["four_day_net_result_yen"] == 0, "capital purchases and prizes must not enter operating profit")
    sim._run_robbery()
    var statement: Dictionary = sim.month_operating_statement()
    _check(statement["representative"]["sales_yen"] == 0, "robbed takings must leave the sales ledger")
    _check(statement["four_day_net_result_yen"] == -1000, "robbery cash loss must not be charged seven more times")
    _check(statement["one_off_yen"] == -22000, "prize, capital and robbery remain one-off cash flows")
    var cash: int = sim.economy.cash_yen
    var saved: Dictionary = sim.save_state()
    var restored = Simulation.new(config)
    _check(restored.load_state(saved), "current save remains compatible")
    _check(restored.month_operating_statement() == statement, "midmonth save keeps the operating ledger")
    var home: int = restored.active_store
    restored._settle_month_end()
    _check(restored.active_store == home, "reading and closing a statement must preserve the selected store")
    _check(restored.economy.cash_yen == cash - 7000, "apply only seven further operating losses")
    var details: Dictionary = restored.economy.month_end_records.back()["details"]
    _check(details["month_sales_yen"] == 0 and details["month_result_yen"] == -8000, "closed report must use booked sales")
    _check(details["operating_statement"]["monthly"]["goods_yen"] == 800, "closed report retains its cost breakdown")
    _check(details["cash_before_adjustment_yen"] == cash, "retain cash before adjustment")
    _check(details["cash_after_adjustment_yen"] == restored.economy.cash_yen, "retain cash after adjustment")
    _check(restored.month_operating_statement()["four_day_net_result_yen"] == 0, "next month starts with an empty ledger")
    var after_close: Dictionary = restored.save_state()
    var reopened = Simulation.new(config)
    _check(reopened.load_state(after_close), "month-end report save loads")
    _check(reopened.economy.month_end_records == restored.economy.month_end_records, "closed breakdown survives save/load")
    var multi_config: Dictionary = JSON.parse_string(FileAccess.get_file_as_string(ConfigPath))
    multi_config = Guide.apply(multi_config)
    var multi = Simulation.new(multi_config)
    multi.economy.cash_yen = 1000000000
    _check(multi.try_buy_store_site(Vector2i(13, 21), "small_top"), "open the real first store")
    _check(multi.try_buy_out_rival("rival-02"), "add the real second store")
    multi._store_sales_yen = 1200
    _check(multi.select_store(1), "select second store")
    multi._store_sales_yen = 3400
    _check(multi.month_operating_statement()["representative"]["sales_yen"] == 4600, "statement includes all owned stores")
    _check(multi.active_store == 1, "reading the statement keeps the second store selected")
    var multi_copy = Simulation.new(multi_config)
    _check(multi_copy.load_state(multi.save_state()), "multistore midmonth load")
    _check(multi_copy.month_operating_statement()["representative"]["sales_yen"] == 4600, "multistore ledger survives save/load")
    multi._settle_month_end()
    _check(multi.active_store == 1, "month close keeps the second store selected")
    _check(multi.month_operating_statement()["representative"]["sales_yen"] == 0, "month close resets every store ledger")
    if failures > 0:
        quit(1)
        return
    print("Operating statement: source examples, one-off cash, robbery, month close and save/load passed")
    quit(0)
