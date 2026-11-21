extends SceneTree
const Sim = preload("res://scripts/vertical_slice_simulation.gd")
const Start = preload("res://scripts/domain/guide_starting_store.gd")
const Statement = preload("res://scripts/domain/operating_statement.gd")

func setup():
    var config: Dictionary = JSON.parse_string(FileAccess.get_file_as_string("res://data/vertical_slice.json"))
    var s = Sim.new(Start.apply(config))
    assert(s.try_buy_store_site(Vector2i(26,12)))
    s.notifications.reset()
    return s

func _initialize() -> void:
    var cases: Dictionary = JSON.parse_string(FileAccess.get_file_as_string("res://tests/fixtures/source_finance_width.json"))
    for row in cases.rows:
        var plan: Dictionary = Statement.project(row.representative, true)
        for field in row.monthly:
            assert(int(plan.monthly[field]) == int(row.monthly[field]), "Each monthly column is a signed32 word")
        assert(int(plan.four_day_net_result_yen) == int(row.profit))
        assert(int(plan.month_result_yen) == int(row.monthly_profit))
        assert(int(plan.adjustment_yen) == int(row.adjustment))
        assert(Statement.close_cash(int(row.cash_before),int(plan.adjustment_yen)) == int(row.cash_after))
    assert(Statement.project({"sales_yen":400000000}).month_result_yen == 3200000000, "Older prototype width remains explicit")
    for sales in [1000,400000,268435456,400000000,2147483648]:
        var s = setup()
        s._store_sales_yen = sales
        s.economy.cash_yen = 1000
        s.minute_of_day = 0
        var before: Dictionary = s.month_operating_statement()
        assert(before.monthly.sales_yen == Statement.signed32(sales*8))
        assert(s.store_operating_statement(0).monthly.sales_yen == before.monthly.sales_yen)
        var copy = setup()
        assert(copy.load_state(JSON.parse_string(JSON.stringify(s.save_state()))))
        assert(copy.month_operating_statement() == before)
        copy._settle_month_end()
        var cash: int = Statement.close_cash(1000,int(before.adjustment_yen))
        assert(copy.economy.cash_yen == cash)
        assert(copy.profit_history[0] == int(before.month_result_yen))
        assert(copy._annual_sales_yen == int(before.monthly.sales_yen))
        var ratings: Array = copy.event_log.records.filter(func(row): return row.event_type == "store_rating_evaluated")
        assert(int(ratings.back().details.monthly_sales_yen) == Statement.signed32(sales), "Source rating reads unscaled D48")
        var details: Dictionary = copy.economy.month_end_records.back().details
        assert(int(details.cash_after_adjustment_yen) == cash)
        assert(int(details.month_sales_yen) == int(before.monthly.sales_yen))
        assert(copy.is_game_over == (cash < 0))
        var replay = setup()
        assert(replay.load_state(JSON.parse_string(JSON.stringify(copy.save_state()))))
        # JSON decodes every number as float; compare both decoded trees.
        assert(JSON.parse_string(JSON.stringify(replay.economy.month_end_records)) == JSON.parse_string(JSON.stringify(copy.economy.month_end_records)))
        assert(replay.economy.cash_yen == cash and replay.profit_history == copy.profit_history)
    # A saved calendar continuation from <=0.8.11 contains an unbounded old
    # projection. Recompute only its explicit representative ledger, once.
    var old = setup()
    old.minute_of_day = 0
    old.economy.cash_yen = 1000
    var prepared: Dictionary = Statement.project({"sales_yen":400000000})
    prepared.one_off_yen = 0
    old._settle_month_end({"capital":0,"statement":prepared})
    assert(old.economy.cash_yen == -1494966296)
    assert(old.economy.month_end_records.back().details.month_result_yen == -1094967296)
    print("FINANCE_WIDTH_PASS 24 existing-model cases, five signed columns/profit/cash, native close/graphs/annual/bankruptcy/JSON, old continuation, prototype compatibility")
    quit()
