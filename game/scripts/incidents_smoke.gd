extends SceneTree
const Sim=preload("res://scripts/vertical_slice_simulation.gd")
const Start=preload("res://scripts/domain/guide_starting_store.gd")
const Rule=preload("res://scripts/domain/program_incidents.gd")
const RNG=preload("res://scripts/domain/program_random.gd")
const Customer=preload("res://scripts/domain/customer_state.gd")
func setup():
    var base:Dictionary=JSON.parse_string(FileAccess.get_file_as_string("res://data/vertical_slice.json"))
    var s=Sim.new(Start.apply(base));s.economy.cash_yen=1000000000
    assert(s.try_buy_store_site(Vector2i(26,12)))
    for cell in s.program_town.cells:
        if int(cell[0])>=60 and int(cell[0])<=69:cell[0]=12
    for p in s.staff.all_staff():p.security_skill=0;p.stamina=70
    s._store_visitor_heads=2000;s._store_sales_last_month=1000000
    s._store_sales_yen=s._store_sales_at_day_start+100000;s.popularity=100
    var person=Customer.new({"id":"incident-customer"})
    person.source_native=true;person.phase="to_shelf";person.source_state=1
    person.visit={"manners":30};s.customers.customers[person.customer_id]=person
    assert(s.incident_possible())
    return s
func _initialize() -> void:
    var fixture:Dictionary=JSON.parse_string(FileAccess.get_file_as_string("res://tests/fixtures/source_incidents.json"))
    for row in fixture.financial:
        assert(Rule.financial_gate(bool(row.rival),int(row.security),int(row.popularity),int(row.heads),int(row.last_sales),int(row.sales))==bool(row.allowed))
    for row in fixture.assets:
        assert(Rule.eligible(false,0,100,2000,1000000,100000,int(row.value))==bool(row.allowed))
    for row in fixture.chances:
        var rng=RNG.new();rng.seed=int(row.seed)
        assert(Rule.draw(rng)==int(row.kind) and rng.seed==int(row.seed_after))
    for row in fixture.tails:
        var s=setup()
        for i in 3:
            if not row.slots.map(func(v):return int(v)).has(i):s.staff.members.erase("staff-%d" % (i+1))
        s.internal_rating_value=42;s.popularity=99
        var tasks:Dictionary={}
        for p in s.staff.all_staff():
            p.source_state=2;p.source_goal=Vector2i(6,6);p.route.assign([Vector2i(5,6)])
            tasks[p.staff_id]=p.candidate_id
        s._finish_source_incident()
        assert(s.internal_rating_value==42 and s.popularity==int(row.popularity_after))
        for p in s.staff.all_staff():
            assert(p.stamina==0 and p.source_state==2 and p.source_goal==Vector2i(6,6) and p.route==[Vector2i(5,6)] and p.candidate_id==tasks[p.staff_id])
    var robbery:Dictionary={};var both:Dictionary={}
    for row in fixture.chances:
        if bool(row.robbery) and not bool(row.fire):robbery=row
        if bool(row.robbery) and bool(row.fire):both=row
    # Financial rejection consumes no RNG, including the true caller path.
    var s=setup();s._store_visitor_heads=1999;s._program_rng.seed=int(robbery.seed)
    s._step_incidents();assert(s._program_rng.seed==int(robbery.seed))
    # Customer rejection comes AFTER drawing, not before.
    s=setup();s.customers.customers["incident-customer"].visit.manners=31;s._program_rng.seed=int(robbery.seed)
    s._step_incidents();assert(s._program_rng.seed==int(robbery.seed_after) and s.popularity==100)
    # A selected robbery posts the loss and then applies the common tail.
    s=setup();s._program_rng.seed=int(robbery.seed)
    var cash:int=s.economy.cash_yen;var count:int=s.layout.fixtures.size()
    var rating:int=s.internal_rating_value
    s._step_incidents()
    assert(s.economy.cash_yen==cash-800000 and s.store_sales_today_yen()==0)
    assert(s.popularity==5 and s.internal_rating_value==rating and s.layout.fixtures.size()==count)
    assert(s.customers.active_customers().size()==1 and s._program_rng.seed==int(robbery.seed_after))
    for p in s.staff.all_staff():assert(p.stamina==0)
    var clone=setup();assert(clone.load_state(JSON.parse_string(JSON.stringify(s.save_state()))))
    assert(clone.popularity==5 and clone.store_sales_today_yen()==0 and clone.economy.cash_yen==s.economy.cash_yen)
    for p in clone.staff.all_staff():assert(p.stamina==0)
    # One component at the expanded rectangle edge blocks. Outside does not.
    s=setup();var origin:Vector2i=s.store_site_origin
    var edge:Vector2i=origin-Vector2i(7,7)
    var outside:Vector2i=edge-Vector2i.ONE
    s.program_town.cells[outside.y*60+outside.x][0]=60
    assert(not s._source_incident_blocked(0))
    s.program_town.cells[edge.y*60+edge.x][0]=63
    assert(s._source_incident_blocked(0) and not s._source_incident_blocked(1))
    # Fire overrides robbery; blocking that fire must not fall back to robbery.
    s=setup();s.program_town.cells[(s.store_site_origin.y-1)*60+s.store_site_origin.x][0]=69
    s._program_rng.seed=int(both.seed);cash=s.economy.cash_yen
    s._step_incidents()
    assert(s.economy.cash_yen==cash and s.popularity==100 and s._program_rng.seed==int(both.seed_after))
    # Rival children cannot suffer incidents or consume incident RNG.
    s=setup();s.config.simulation.rival_child=true;s._program_rng.seed=int(robbery.seed)
    s._step_incidents();assert(s._program_rng.seed==int(robbery.seed) and s.popularity==100)
    print("INCIDENTS_PASS 27 original excerpts; finance-before-RNG, post-roll customer/facility guards, fire precedence, robbery common tail and JSON")
    quit()
