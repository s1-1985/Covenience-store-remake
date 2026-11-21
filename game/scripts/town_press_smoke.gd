extends SceneTree
const Sim=preload("res://scripts/vertical_slice_simulation.gd")
const Start=preload("res://scripts/domain/guide_starting_store.gd")
const Press=preload("res://scripts/domain/program_town_press.gd")
const RNG=preload("res://scripts/domain/program_random.gd")
func setup():
    var base:Dictionary=JSON.parse_string(FileAccess.get_file_as_string("res://data/vertical_slice.json"))
    var s=Sim.new(Start.apply(base));s.economy.cash_yen=1000000000
    assert(s.try_buy_store_site(Vector2i(26,12)))
    for point in [Vector2i(3,3),Vector2i(40,3),Vector2i(3,35),Vector2i(40,35),Vector2i(15,40)]:
        if s.town_store_count()>=5:break
        s.try_buy_store_site(point,"small_top")
    assert(s.town_store_count()==5,str([s.town_store_count(),s.store_count()]))
    return s
func _initialize() -> void:
    var fixture:Dictionary=JSON.parse_string(FileAccess.get_file_as_string("res://tests/fixtures/source_town_press.json"))
    for row in fixture.selections:
        var entries:Array=[]
        for i in row["values"].size():entries.append({"index":i,"value":int(row["values"][i])})
        var rng=RNG.new();rng.seed=int(row.seed)
        var winner:Dictionary=Press.choose(entries,str(row.kind),rng)
        assert((int(winner.get("index",-1)))==int(row.winner) and rng.seed==int(row.seed_after))
    var s=setup();var home:int=s.active_store
    # Rival contest uses real running ratings and its separate company book.
    s._for_each_store(func():s.internal_rating_value=5)
    for rival in s._rival_stores:s._program_rival_simulation(rival).internal_rating_value=10
    var rival:Dictionary=s._rival_stores[-1];var child=s._program_rival_simulation(rival)
    var shared_seed:int=s._program_rng.seed
    var events_before:int=child.event_log.records.size()
    child._step_town_press()
    assert(s._program_rng.seed==shared_seed and child.event_log.records.size()==events_before,"Global press must run once, not once per rival child")
    child.internal_rating_value=100
    var own_cash:int=s.economy.cash_yen;var other_cash:int=s._rival_cash_yen
    var own_expenses:int=s.economy.expense_records.size();var child_expenses:int=child.economy.expense_records.size()
    s.notifications.reset();assert(s._run_town_press("contest"))
    assert(s._rival_cash_yen==other_cash+50000000 and s.economy.cash_yen==own_cash and s.economy.expense_records.size()==own_expenses)
    assert(child.economy.expense_records.size()==child_expenses+1 and child.economy.expense_records[-1].amount_yen==-50000000)
    var notice:Dictionary=s.consume_source_notice()
    assert(notice.kind==0 and notice.parameter==1 and notice.context.details.rival_id==str(rival.id))
    assert(s.active_store==home)
    var manager=child.staff.members[str(child.config.staff.manager_staff_id)]
    # Magazine growth clamps only the two original figure_keys, no instant recovery.
    for row in fixture.growth:
        var figure_key:String={"popular":"education","clean":"agility","service":"sociability","cheap":"stamina"}[str(row.kind)]
        var raises:Dictionary=child._candidate_raises.get(manager.candidate_id,{})
        raises.academic_background=int(row.before)-int(child._staff_candidate_catalog[manager.candidate_id].academic_background)
        raises[figure_key]=int(row.before)-int(child._staff_candidate_catalog[manager.candidate_id][figure_key])
        child._candidate_raises[manager.candidate_id]=raises
        manager.stamina=0
        child._raise_manager(["academic_background",figure_key],2)
        assert(int(child._candidate_figures(manager.candidate_id).academic_background)==int(row.after))
        assert(int(child._candidate_figures(manager.candidate_id)[figure_key])==int(row.after) and manager.stamina==0)
    # Force a popular rival award through the real parent event path.
    s._for_each_store(func():s.popularity=5)
    for other in s._rival_stores:s._program_rival_simulation(other).popularity=10
    child.popularity=100
    var before:int=int(child._candidate_figures(manager.candidate_id).education)
    assert(s._run_town_press("popular"))
    assert(int(child._candidate_figures(manager.candidate_id).education)==mini(100,before+2))
    assert(s._candidate_figures(manager.candidate_id).education==child._candidate_figures(manager.candidate_id).education)
    # Cleaning competition uses employees, not guide's fixed figure.
    for person in child.staff.all_staff():person.cleaning_skill=100
    assert(s._press_rival_value("clean",rival)==int(child._store_values().cleaning))
    assert(s._press_rival_value("contest",rival)==100)
    # Only actual stocked categories contribute to native price value.
    s.select_store(0)
    for product_id in s.inventory.product_order:
        var category:String=s.inventory.get_product(product_id).catalog_id
        s.product_price_settings[category]=0
    assert(s._press_value("cheap")==100-s.source_shelf_price_percent())
    assert(s._press_value("cheap")!=-s.price_change_pct)
    s._for_each_store(func():
        for product_id in s.inventory.product_order:
            s.product_price_settings[s.inventory.get_product(product_id).catalog_id]=100)
    for other in s._rival_stores:
        var other_sim=s._program_rival_simulation(other)
        for product_id in other_sim.inventory.product_order:
            other_sim.product_price_settings[other_sim.inventory.get_product(product_id).catalog_id]=100
    for product_id in s.inventory.product_order:s.product_price_settings[s.inventory.get_product(product_id).catalog_id]=0
    var own_manager=s.staff.members[str(s.config.staff.manager_staff_id)]
    var academic:int=s._manager_academic();var maximum:int=int(s._candidate_figures(own_manager.candidate_id).stamina)
    assert(s._run_town_press("cheap"))
    assert(s.event_log.records[-1].details.store_index==0 and s._manager_academic()==mini(100,academic+2))
    assert(int(s._candidate_figures(own_manager.candidate_id).stamina)==mini(100,maximum+2))
    # Player contest is isolated from the rival company and credits the winner.
    s._for_each_store(func():s.internal_rating_value=5)
    s.internal_rating_value=100
    for other in s._rival_stores:s._program_rival_simulation(other).internal_rating_value=10
    own_cash=s.economy.cash_yen;other_cash=s._rival_cash_yen
    assert(s._run_town_press("contest"))
    assert(s.economy.cash_yen==own_cash+50000000 and s._rival_cash_yen==other_cash)
    var saved:Dictionary=JSON.parse_string(JSON.stringify(s.save_state()))
    var clone=Sim.new(Start.apply(JSON.parse_string(FileAccess.get_file_as_string("res://data/vertical_slice.json"))));assert(clone.load_state(saved))
    assert(clone._rival_cash_yen==s._rival_cash_yen)
    var restored=clone._program_rival_simulation(clone._rival_stores[clone._rival_index(str(rival.id))])
    assert(restored._candidate_figures(manager.candidate_id)==child._candidate_figures(manager.candidate_id))
    assert(clone._candidate_figures(manager.candidate_id)==s._candidate_figures(manager.candidate_id))
    var education:int=int(clone._candidate_figures(manager.candidate_id).education)
    assert(clone.try_buy_out_rival(str(rival.id)))
    clone.select_store(clone.store_count()-1)
    var purchased=clone.staff.members[str(clone.config.staff.manager_staff_id)]
    assert(purchased.candidate_id==manager.candidate_id and int(clone._candidate_figures(purchased.candidate_id).education)==education)
    print("TOWN_PRESS_PASS 90 source selections/4 company payments/16 growth excerpts; native rival values, stock prices, both owners, notices, store restoration and JSON")
    quit()
