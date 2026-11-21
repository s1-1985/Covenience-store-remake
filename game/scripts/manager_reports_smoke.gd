extends SceneTree
const Sim=preload("res://scripts/vertical_slice_simulation.gd")
const Start=preload("res://scripts/domain/guide_starting_store.gd")
const Reports=preload("res://scripts/domain/program_manager_reports.gd")
const RNG=preload("res://scripts/domain/program_random.gd")
const People=preload("res://scripts/domain/program_people.gd")
const Customer=preload("res://scripts/domain/customer_state.gd")
func setup():
    var base:Dictionary=JSON.parse_string(FileAccess.get_file_as_string("res://data/vertical_slice.json"))
    var s=Sim.new(Start.apply(base));s.economy.cash_yen=1000000000
    assert(s.try_buy_store_site(Vector2i(26,12)))
    s.minute_of_day=1
    return s
func _initialize() -> void:
    var fixture:Dictionary=JSON.parse_string(FileAccess.get_file_as_string("res://tests/fixtures/source_manager_reports.json"))
    var order:Array=[]
    for i in 27:order.append(str(i))
    for row in fixture.selections:
        var counts:Dictionary={};var stocked:Array=[]
        # Deliberately reverse insertion order and stock order.
        for i in range(26,-1,-1):
            counts[str(i)]=int(row.counts[i])
            if int(row.stock[i])>0:stocked.append(str(i))
        var got:Dictionary=Reports.candidates(counts,stocked,order)
        assert(got.best==str(int(row.best)) and got.worst==("" if int(row.worst)==27 else str(int(row.worst))))
    var s=setup();var id:String=s.inventory.product_order[0];var product=s.inventory.get_product(id)
    var category:String=product.catalog_id
    var f:Dictionary=s.layout.fixtures_by_id[product.fixture_id]
    for row in fixture.acquisitions:
        s._sold_counts={category:int(row.before)};s.survey_bought={};product.stock_units=int(row.stock)
        var p=Customer.new({"id":"report-pick"});p.source_native=true;p.source_state=2;p.phase="shopping"
        p.source_wanted=category;p.group_size=int(row.heads);p.budget_left=99999;p.visit={"quickness":100,"manners":100}
        p.position=s._vec2i_from_array(f.origin_subcell)+Vector2i(0,2);p.source_goal=p.position;p.source_direction=0;p.source_goal_direction=0
        var cash:int=s.economy.cash_yen
        People.customer(s,p)
        assert(int(s._sold_counts.get(category,0))==int(row.after),"Report count belongs to pickup, not payment")
        if not bool(row.failed):
            assert(not p.basket.is_empty() and s.economy.cash_yen==cash)
            s._settle_source_basket(p)
            assert(int(s._sold_counts[category])==int(row.after),"Checkout must not count again")
            s._settle_source_basket(p)
            assert(int(s._sold_counts[category])==int(row.after))
    # Report counters remain isolated per store and survive JSON.
    s=setup();id=s.inventory.product_order[0];product=s.inventory.get_product(id);category=product.catalog_id
    s._record_source_survey_pick(id,3)
    var first:Dictionary=s._sold_counts.duplicate()
    assert(s.try_buy_store_site(Vector2i(3,3),"small_top"));s.select_store(1)
    assert(s._sold_counts.is_empty());s._record_source_survey_pick(str(s.inventory.product_order[0]),5)
    var second:Dictionary=s._sold_counts.duplicate();s.select_store(0);assert(s._sold_counts==first)
    var clone=setup();assert(clone.load_state(JSON.parse_string(JSON.stringify(s.save_state()))))
    assert(clone._sold_counts==first);clone.select_store(1);assert(clone._sold_counts==second)
    # Rare gate clears report counts, never the separate monthly surveys.
    s=setup();id=s.inventory.product_order[0];category=s.inventory.get_product(id).catalog_id
    var manager=s.staff.members[str(s.config.staff.manager_staff_id)]
    s._staff_candidate_catalog[manager.candidate_id].academic_background=100
    var rare_seed:int=-1;var rng=RNG.new()
    for seed in 200000:
        rng.seed=seed
        if rng.randi_range(1,8192)==1:
            rare_seed=seed;break
    assert(rare_seed>=0)
    s._sold_counts={category:199};s.survey_bought={category:7};s.survey_missing={category:9}
    s._notice_counts={"angry":0,"sold_out":1,"cars":0,"dirty":0};s._report_rng.seed=rare_seed
    s._step_manager_reports()
    assert(s._sold_counts.is_empty() and s.survey_bought=={category:7} and s.survey_missing=={category:9} and s._notice_counts.sold_out==0)
    # Both rare report branches use canonical candidates, then clear counts.
    for coin in [0,1]:
        var chosen:int=-1
        for candidate in 200000:
            rng.seed=candidate
            if rng.randi_range(1,8192)!=1:continue
            rng.randi_range(1,100)
            if rng.randi_range(0,1)==coin:
                chosen=candidate;break
        assert(chosen>=0)
        for product_id in s.inventory.product_order:s.inventory.get_product(product_id).stock_units=40
        var stock:Array=s._stocked_categories()
        assert(stock.size()>=2)
        s._sold_counts={str(stock[1]):200}
        var expected:Dictionary=Reports.candidates(s._sold_counts,stock,s.config.source_catalog.product_ids)
        var before:int=s.event_log.records.size();s._report_rng.seed=chosen
        s._step_manager_reports()
        var emitted:Array=s.event_log.records.slice(before).filter(func(e):return e.event_type=="sales_report")
        assert(emitted.size()==1 and emitted[0].details.product==(expected.best if coin==0 else expected.worst) and emitted[0].details.selling_well==(coin==0))
        assert(s._sold_counts.is_empty() and s.survey_bought=={category:7})
    var direct=Customer.new({"id":"direct-report"})
    var line:Dictionary={"product_id":id,"quantity":1,"unit_price_yen":100}
    s._sold_counts={category:17};s._settle_source_immediate(direct,line)
    assert(s._sold_counts=={category:17},"Direct settlement also must not count twice")
    # Rival guard precedes even the four-hour clear and dirty/RNG branches.
    s.config.simulation.rival_child=true;s.minute_of_day=0;s._notice_counts={"angry":127,"sold_out":100,"cars":100,"dirty":4};s._sold_counts={category:500}
    var notices:Dictionary=s._notice_counts.duplicate();var seed:int=s._report_rng.seed;var events:int=s.event_log.records.size()
    s._step_manager_reports()
    assert(s._notice_counts==notices and s._sold_counts=={category:500} and s._report_rng.seed==seed and s.event_log.records.size()==events)
    print("MANAGER_REPORTS_PASS 44 original selections/4 pickup excerpts; u32/ties/stock, pickup before payment, no double count, store JSON, rare clear, rival RNG guard")
    quit()
