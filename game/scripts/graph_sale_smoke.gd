extends SceneTree
const Graph=preload("res://scripts/domain/program_graph.gd")
const Sim=preload("res://scripts/vertical_slice_simulation.gd")
const Starting=preload("res://scripts/domain/guide_starting_store.gd")
func _init() -> void:
    var fixture: Dictionary=JSON.parse_string(FileAccess.get_file_as_string("res://tests/fixtures/source_graph.json"))
    fixture.scale_cases.append_array(JSON.parse_string(FileAccess.get_file_as_string("res://tests/fixtures/source_graph_boundaries.json")).scale_cases)
    for case in fixture.scale_cases:
        var actual:=Graph.plan(case.history,case.chain,case.counts)
        for field in ["valid","averages","axis_yen","oldest_first"]:
            if actual[field] is Array:
                assert(actual[field].size()==case.model[field].size())
                for i in actual[field].size(): assert(int(actual[field][i])==int(case.model[field][i]),"Original graph array mismatch "+field)
            else:
                assert(int(actual[field])==int(case.model[field]),"Original graph scalar mismatch "+field)
    assert(Graph.plan([0],[0],[1]).valid==1)
    assert(Graph.plan([1,Graph.MISSING,9000000],[0,0,0],[1,1,1]).valid==1)
    var many: Array=[]
    for i in 70: many.append(i)
    var ones: Array=[]
    for i in 70: ones.append(1)
    assert(Graph.plan(many,many,ones).valid==60)
    assert(Graph.height(-1000000,1000000)==56 and Graph.height(9999,1000000)==0)
    var base: Dictionary=JSON.parse_string(FileAccess.get_file_as_string("res://data/vertical_slice.json"))
    var sim=Sim.new(Starting.apply(base))
    sim.economy.cash_yen=1000000000
    assert(sim.try_buy_store_site(Vector2i(26,12)))
    assert(sim.try_buy_store_site(Vector2i(3,3),"small_top"))
    sim._store_sales_yen=1000000
    sim.economy.record_explicit_expense("staff_wages",0,100000)
    sim.economy.record_explicit_expense("fixture_purchase",0,9000000)
    assert(sim.select_store(1))
    var uid: int=sim._store_uid
    sim._store_sales_yen=3000000
    sim.economy.record_explicit_expense("inventory_restock",0,200000)
    sim.economy.record_explicit_expense("fixture_maintenance",0,100000)
    sim.economy.record_explicit_expense("promotion_cost",0,50000)
    var saved: Dictionary=JSON.parse_string(JSON.stringify(sim.save_state()))
    var clone=Sim.new(Starting.apply(base))
    assert(clone.load_state(saved))
    assert(clone.store_operating_statement(0).month_result_yen==7200000)
    assert(clone.store_operating_statement(1).month_result_yen==21200000)
    var closing=Sim.new(Starting.apply(base))
    assert(closing.load_state(saved))
    closing.select_store(1)
    assert(closing.try_set_business_hours("closed"))
    var pre_sale: Dictionary=closing.month_operating_statement()
    assert(closing.try_sell_store(1))
    assert(closing.month_operating_statement().representative==pre_sale.representative,"Selling must retain current-month sales/expenses and keep refunds capital-only")
    var closing_copy=Sim.new(Starting.apply(base))
    assert(closing_copy.load_state(JSON.parse_string(JSON.stringify(closing.save_state()))))
    assert(closing_copy.month_operating_statement()==closing.month_operating_statement())
    clone._settle_month_end()
    assert(clone.store_field(0,"profit_history")==[7200000])
    assert(clone.store_field(1,"profit_history")==[21200000])
    assert(clone.economy.month_end_records.back().details.month_result_yen==28400000)
    clone.select_store(0)
    assert(clone.graph_data().axis_yen==15000000,"Same-month chain average must affect store axis")
    clone.select_store(1)
    assert(clone.graph_data().axis_yen==22000000)
    var after=Sim.new(Starting.apply(base))
    assert(after.load_state(JSON.parse_string(JSON.stringify(clone.save_state()))))
    after.select_store(1)
    assert(after.profit_history==[21200000] and after._store_uid==uid)
    assert(not after.store_sale_quote(0).allowed)
    assert(after.try_set_business_hours("24h"))
    assert(not after.store_sale_quote(1).allowed,"Open shop must not be sold")
    assert(after.try_set_business_hours("closed"))
    var worker=after.staff.all_staff()[0]
    worker.register_skill=87
    worker.stamina=31
    var worker_id: String=worker.candidate_id
    var origin: Vector2i=after.store_site_origin
    var quote: Dictionary=after.store_sale_quote(1)
    assert(quote.allowed)
    var equipment:=0
    for f in after.layout.fixtures+after.outdoor_fixtures:
        var kind: int=after.program_fixture_kind(f)
        if kind>=0: equipment+=int(after._recovery.fixture_records[kind][1])
    var goods:=0
    for p in after.inventory.products.values(): goods+=p.stock_units*p.restock_unit_cost_yen
    assert(quote.total_yen==after.store_site.start_land_price_yen(origin)+3000000+equipment+goods)
    var cash: int=after.economy.cash_yen
    var rival_cash: int=after._rival_cash_yen
    assert(not after.try_sell_store(1,uid+999))
    assert(after.economy.cash_yen==cash)
    assert(after.try_sell_store(1,uid))
    assert(after.store_count()==1 and after.player_store_count==1)
    assert(after.economy.cash_yen==cash+quote.total_yen and after._rival_cash_yen==rival_cash)
    for point in [origin,origin+Vector2i(1,0),origin+Vector2i(0,1),origin+Vector2i(1,1)]:
        assert(after.program_town.kind(point.x,point.y)==12,"Sold site must become empty land")
    assert(after.source_free_candidates().has(worker_id))
    var released_save: Dictionary=JSON.parse_string(JSON.stringify(after.save_state()))
    var reopened=Sim.new(Starting.apply(base))
    assert(reopened.load_state(released_save))
    assert(reopened.try_dismiss_source_staff("staff-3"))
    assert(reopened.try_hire_candidate("staff-3",worker_id))
    assert(reopened.staff.members["staff-3"].register_skill==87 and reopened.staff.members["staff-3"].stamina==31)
    assert(reopened.try_buy_store_site(origin,"small_top"))
    reopened.select_store(1)
    assert(reopened._store_uid>uid and reopened.profit_history.is_empty(),"New shop must not inherit sold history or UID")
    assert(reopened.customers._id_prefix.ends_with("s%d" % reopened._store_uid))
    var second=Sim.new(Starting.apply(base))
    assert(second.load_state(JSON.parse_string(JSON.stringify(reopened.save_state()))))
    second.select_store(1)
    assert(second.customers._id_prefix==reopened.customers._id_prefix)
    # Current legacy expense cannot be allocated to a store: preserve a gap.
    second.economy.record_explicit_expense("staff_wages",0,10)
    second.economy.expense_records.back().erase("store_uid")
    assert(not second.store_operating_statement(1).complete)
    # Removing a middle shop must preserve the other shop's identity and tags.
    var middle=Sim.new(Starting.apply(base))
    assert(middle.load_state(saved))
    var added:=false
    for y in range(3,45,8):
        for x in range(3,55,8):
            if middle.store_site_quote(Vector2i(x,y)).buildable:
                added=middle.try_buy_store_site(Vector2i(x,y),"small_top")
                if added:break
        if added:break
    assert(added and middle.store_count()==3)
    var third_uid: int=middle.store_field(2,"_store_uid")
    middle.select_store(1)
    middle.try_set_business_hours("closed")
    assert(middle.try_sell_store(1))
    middle.select_store(1)
    assert(middle._store_uid==third_uid and middle.store_count()==2)
    middle.economy.record_explicit_expense("staff_wages",0,20)
    assert(middle.economy.expense_records.back().store_uid==third_uid)
    var middle_copy=Sim.new(Starting.apply(base))
    assert(middle_copy.load_state(JSON.parse_string(JSON.stringify(middle.save_state()))))
    assert(middle_copy.store_field(1,"_store_uid")==third_uid)
    print("GRAPH_SALE_PASS 9 original graph scales, 60 cap, two-store ledger/profit/average/save, main/open/UID guards, asset refund, no rival debit, empty land, retained staff, reopen unique UID/history/prefix, legacy gap")
    quit()
