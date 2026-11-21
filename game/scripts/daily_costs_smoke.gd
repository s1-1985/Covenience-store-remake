extends SceneTree
const Sim = preload("res://scripts/vertical_slice_simulation.gd")
const Start = preload("res://scripts/domain/guide_starting_store.gd")
const Costs = preload("res://scripts/domain/program_operating_costs.gd")
const Width = preload("res://scripts/domain/operating_statement.gd")
func setup():
    var config: Dictionary = JSON.parse_string(FileAccess.get_file_as_string("res://data/vertical_slice.json"))
    var s = Sim.new(Start.apply(config))
    s.economy.cash_yen = 1000000000
    assert(s.try_buy_store_site(Vector2i(26,12)))
    return s
func _initialize() -> void:
    var fixture: Dictionary = JSON.parse_string(FileAccess.get_file_as_string("res://tests/fixtures/source_daily_costs.json"))
    for row in fixture.staff:
        var total := 0
        for i in row.wages.size():
            var got: int = Costs.wage(int(row.wages[i]),i==0,int(row.hours))
            assert(got == int(row.per_staff[i]))
            total = Width.signed32(total+got)
        assert(total == int(row.total))
    for row in fixture.equipment:
        var rates: Array = []
        for i in 53:
            rates.append([0,0,int(row.rates[i]) if i<row.rates.size() else 0])
        assert(Costs.maintenance(row.kinds,rates,int(row.hours)) == int(row.total))
    var s = setup()
    s.demand.opening_minutes_per_day = 8*60
    for worker in s.staff.all_staff():
        worker.salary_yen_per_day_24h = 2147483647*24
    var total := 0
    for worker in s.staff.all_staff():
        total=Width.signed32(total+Costs.wage(2147483647,worker.staff_id=="staff-1",8))
    s.economy.cash_yen = 1000
    var count: int = s.economy.expense_records.size()
    s._apply_daily_staff_wages()
    assert(total < 0 and s.economy.expense_records.size() == count+1)
    assert(int(s.economy.expense_records.back().amount_yen) == total, "Negative source cost is not silently discarded")
    assert(s.economy.cash_yen == Width.signed32(1000-total))
    assert(int(s.month_operating_statement().representative.wages_yen) == total)
    var copy = setup()
    assert(copy.load_state(JSON.parse_string(JSON.stringify(s.save_state()))))
    assert(copy.economy.cash_yen == s.economy.cash_yen)
    assert(int(copy.month_operating_statement().representative.wages_yen) == total)
    # Native maintenance must exclude class53 without touching its table row.
    for i in s._recovery.fixture_records.size():
        s._recovery.fixture_records[i][2]=0
    s._recovery.fixture_records[0][2]=2147483647
    s.layout.fixtures.assign([{"source_kind":0},{"source_kind":53}])
    s.outdoor_fixtures=[]
    s.demand.opening_minutes_per_day=8*60
    s.economy.cash_yen=1000
    s._apply_daily_fixture_maintenance()
    assert(int(s.economy.expense_records.back().amount_yen) == -8)
    assert(s.economy.cash_yen == 1008)
    count=s.economy.expense_records.size()
    s.demand.opening_minutes_per_day=0
    s._apply_daily_fixture_maintenance()
    s._apply_daily_staff_wages()
    assert(s.economy.expense_records.size()==count and s.economy.cash_yen==1008)
    print("DAILY_COSTS_PASS 21 existing-model cases, manager intermediate width, signed expense/cash, native month/JSON, kind53 exclusion, closed-store zero")
    quit()
