extends SceneTree
const Sim=preload("res://scripts/vertical_slice_simulation.gd")
const Start=preload("res://scripts/domain/guide_starting_store.gd")
const Rule=preload("res://scripts/domain/program_inspection.gd")
func _initialize() -> void:
    var base:Dictionary=JSON.parse_string(FileAccess.get_file_as_string("res://data/vertical_slice.json"))
    var fixture:Dictionary=JSON.parse_string(FileAccess.get_file_as_string("res://tests/fixtures/source_inspection.json"))
    for row in fixture.resets:
        assert(Rule.expires(int(row.period),int(row.hour),int(row.subhour))==(int(row.flag_after)==0))
    for row in fixture.transactions:
        assert(Rule.fee(int(row.flag_before))==int(row.fee))
        assert(Rule.affordable(int(row.cash_before),int(row.fee))==bool(row.allowed))
    var s=Sim.new(Start.apply(base))
    s.economy.cash_yen=1000000000
    assert(s.try_buy_store_site(Vector2i(26,12)))
    assert(s.try_buy_store_site(Vector2i(3,3),"small_top"))
    s.try_set_business_hours("closed");s.select_store(1);s.try_set_business_hours("closed");s.select_store(0)
    var hq:String=s._rival_stores[0].id
    var branch:String=s._rival_stores[1].id
    s.economy.cash_yen=499999
    var count:int=s.economy.expense_records.size()
    assert(not s.try_investigate_rival(hq) and s.economy.expense_records.size()==count)
    s.economy.cash_yen=500000
    var rival_cash:int=s._rival_cash_yen
    var seed:int=s._program_rng.seed
    var operating:int=s.month_operating_statement().month_result_yen
    var special:int=s.month_operating_statement().one_off_yen
    var quote:Dictionary=s.source_rival_action_quote(hq,"investigate")
    assert(quote.allowed and int(quote.cost_yen)==500000)
    var changed:Dictionary=quote.duplicate(true);changed.serial=int(changed.serial)+1
    assert(not s.try_investigate_rival(hq,changed))
    assert(s.economy.cash_yen==500000 and not s.rival_investigated(hq))
    assert(s.try_investigate_rival(hq,quote))
    assert(s.rival_investigated(hq) and s.economy.cash_yen==0 and s._rival_cash_yen==rival_cash)
    assert(s._program_rng.seed==seed,"Inspection must not reroll gameplay")
    assert(s.month_operating_statement().month_result_yen==operating and s.month_operating_statement().one_off_yen==special+500000)
    assert(not s.try_investigate_rival(hq) and s.economy.expense_records.size()==count+1)
    assert(int(s.source_rival_action_quote(hq,"investigate").cost_yen)==0)
    s.economy.cash_yen=500000
    quote=s.source_rival_action_quote(branch,"investigate")
    s.select_store(1)
    assert(not s.try_investigate_rival(branch,quote))
    s.select_store(0)
    var index:int=s._rival_index(branch)
    var serial:int=s._rival_stores[index].serial
    s._rival_stores[index].serial=serial+1
    assert(not s.try_investigate_rival(branch,quote))
    s._rival_stores[index].serial=serial
    assert(s.try_investigate_rival(branch,quote))
    var saved:Dictionary=JSON.parse_string(JSON.stringify(s.save_state()))
    var clone=Sim.new(Start.apply(base));assert(clone.load_state(saved))
    assert(clone.rival_investigated(hq) and clone.rival_investigated(branch),"Load keeps current inspection flags")
    s.minute_of_day=1438;s._days_completed_this_month=0
    s._advance_minute_of_day()
    assert(s.rival_investigated(hq) and s.rival_investigated(branch),"Ordinary midnight must preserve flags")
    s.minute_of_day=1438;s._days_completed_this_month=3
    s._advance_minute_of_day()
    assert(not s.rival_investigated(hq) and not s.rival_investigated(branch))
    s.economy.cash_yen=500000
    assert(not s.try_investigate_rival(branch,quote),"Previous month confirmation is stale")
    assert(s.try_investigate_rival(hq) and s.economy.cash_yen==0)
    assert(s.economy.expense_records.filter(func(e):return e.expense_type=="rival_investigation").size()==3)
    # Existing native buyout: direct without prior inspection, exact cash,
    # old-owner credit, inherited staff/layout/stock/hours/prices/permits.
    var bought=Sim.new(Start.apply(base))
    assert(bought.try_buy_store_site(Vector2i(26,12)))
    var rid:String=bought._rival_stores[1].id
    var child=bought._program_rival_simulation(bought._rival_stores[1])
    var inventory:int=child.inventory.total_stock_units()
    var hours:String=child.business_hours_id
    var prices:Dictionary=child.product_price_settings.duplicate()
    var people:Array=[]
    for person in child.staff.all_staff():people.append([person.candidate_id,person.register_skill,person.replenishment_skill,person.stamina,person.salary_yen_per_day_24h])
    var fee:int=bought.rival_buyout_price_yen(rid)
    # Reused primary TOWN0001 static quote, not a new original execution.
    assert(fee==46721490)
    bought.economy.cash_yen=fee
    quote=bought.source_rival_action_quote(rid,"buyout")
    assert(quote.allowed and int(quote.cost_yen)==fee)
    var wrong:Dictionary=quote.duplicate(true);wrong.cost_yen=fee-1
    assert(not bought.try_buy_out_rival(rid,wrong) and bought.store_count()==1)
    var seller:int=bought._rival_cash_yen
    assert(bought.try_buy_out_rival(rid,quote))
    assert(bought.economy.cash_yen==0 and bought._rival_cash_yen==seller+fee and bought.store_count()==2)
    assert(bought._rival_index(rid)<0 and not bought.rival_investigated(rid))
    bought.select_store(1)
    assert(bought.inventory.total_stock_units()==inventory and bought.business_hours_id==hours and bought.product_price_settings==prices)
    var transferred:Array=[]
    for person in bought.staff.all_staff():transferred.append([person.candidate_id,person.register_skill,person.replenishment_skill,person.stamina,person.salary_yen_per_day_24h])
    assert(transferred==people)
    assert(bought._store_visitor_heads==0 and bought.profit_history.is_empty())
    assert(not bought.try_buy_out_rival(rid,quote))
    assert(not s.source_rival_action_quote(hq,"buyout").allowed)
    print("INSPECTION_PASS 26 original excerpts, exact cash, one-off fee not seller income, duplicate prevention, UID/serial/month stale guards, ordinary midnight/month expiry/save, direct buyout and retained staff/stock/hours")
    quit()
