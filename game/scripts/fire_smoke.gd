extends SceneTree
const Fire=preload("res://scripts/domain/program_fire.gd")
const RNG=preload("res://scripts/domain/program_random.gd")
const Sim=preload("res://scripts/vertical_slice_simulation.gd")
const Start=preload("res://scripts/domain/guide_starting_store.gd")
const Customer=preload("res://scripts/domain/customer_state.gd")
const People=preload("res://scripts/domain/program_people.gd")
func digest(grid:Array) -> String:
    var bytes:=PackedByteArray();bytes.resize(grid.size()*grid[0].size()*4)
    var at:=0
    for row in grid:
        for value in row:
            bytes.encode_u32(at,int(value)&0xffffffff);at+=4
    var hash:=HashingContext.new();hash.start(HashingContext.HASH_SHA256);hash.update(bytes)
    return hash.finish().hex_encode()
func inputs(kind:int,rotation:int,descriptors:Array) -> Dictionary:
    var floors:Array=[];var grid:Array=[]
    for y in 13:
        var row:Array=[]
        for x in 14:row.append([0,5,10,15,16,28,255,34][(x+y*3)%8])
        floors.append(row)
    for y in 26:
        var row:Array=[];row.resize(28);row.fill(0);row[13]=1;grid.append(row)
    grid[20][24]=0x80000000|(53<<12)
    if kind>=0:
        var width:=int(descriptors[kind][9])*2;var height:=int(descriptors[kind][10])*2
        if rotation>=2:
            var old:=width;width=height;height=old
        for y in range(2,2+height):
            for x in range(2,2+width):grid[y][x]=1
        grid[2][2]=0x80000000|(kind<<12)|(rotation<<22)
    for p in [Vector2i(0,0),Vector2i(27,25),Vector2i(5,5)]:
        if int(grid[p.y][p.x])==0:grid[p.y][p.x]=650<<12
    return {"floors":floors,"grid":grid}
func setup():
    var base:Dictionary=JSON.parse_string(FileAccess.get_file_as_string("res://data/vertical_slice.json"))
    var s=Sim.new(Start.apply(base));s.economy.cash_yen=1000000000
    assert(s.try_buy_store_site(Vector2i(26,12)))
    return s
func _initialize() -> void:
    var tables:Dictionary=JSON.parse_string(FileAccess.get_file_as_string("res://data/ps1_recovered.json"))
    var fixture:Dictionary=JSON.parse_string(FileAccess.get_file_as_string("res://tests/fixtures/source_fire.json"))
    for row in fixture.cases:
        var input:=inputs(int(row.kind),int(row.rotation),tables.fixture_records)
        var rng=RNG.new();rng.seed=int(row.seed)
        var result:Dictionary=Fire.scan(input.grid,input.floors,tables.fixture_records,rng)
        assert(rng.seed==int(row.seed_after) and int(result.floor_writes)==int(row.floor_writes))
        assert(result.burned.has(Vector2i(2,2))==bool(row.burned))
        assert(digest(input.grid)==str(row.grid_after_sha256))
        for y in 13:
            for x in 14:assert(int(input.floors[y][x])==int(row.floor_after[y][x]))
        for point in fixture.customer_positions:Fire.clear_customer_image(input.grid,Vector2i(int(point[0]),int(point[1])))
        assert(digest(input.grid)==str(row.grid_after_customers_sha256))
    var s=setup();s._store_sales_yen=s._store_sales_at_day_start+100000
    s._parking_used=3;s.popularity=99;s.internal_rating_value=42
    var people:Array=[]
    for i in 20:
        var p=Customer.new({"id":"fire-customer-%d" % i});p.source_native=true;p.source_state=3;p.phase="waiting_checkout"
        p.position=Vector2i(-1,-1);p.budget_left=190;p.group_size=3;p.visit={"arrival":"自動車"}
        p.basket.append({"product_id":s.inventory.product_order[0],"quantity":3,"unit_price_yen":610})
        s.customers.customers[p.customer_id]=p;people.append(p)
    var staff_data:Dictionary={}
    for person in s.staff.all_staff():
        person.source_state=2;person.stamina=50;person.source_goal=Vector2i(6,6);person.route.assign([Vector2i(5,6)])
        staff_data[person.staff_id]=person.candidate_id
    var expected:Array[String]=[]
    for f in s.layout.fixtures:
        var category:int=int(tables.fixture_records[s.program_fixture_kind(f)][0])&255
        if category in [4,6]:expected.append(str(f.id))
    var cash:int=s.economy.cash_yen;var sales:int=s._store_sales_yen
    var expenses:int=s.economy.expense_records.size()
    s._run_fire()
    assert(s.economy.cash_yen==cash and s.economy.expense_records.size()==expenses and s._store_sales_yen==sales)
    assert(s.popularity==5 and s.internal_rating_value==42 and s.layout.fixtures.size()==expected.size(),str([s.popularity,s.internal_rating_value,s.layout.fixtures.size(),expected.size()]))
    for f in s.layout.fixtures:assert(expected.has(str(f.id)))
    for product in s.inventory.products.values():assert(expected.has(product.fixture_id))
    for p in people:assert(p.source_state==0 and p.phase=="done" and p.budget_left==190 and p.basket_total_yen()==1830)
    assert(s.customers.active_customers().is_empty() and s._parking_used==3)
    for p in s.staff.all_staff():
        assert(p.candidate_id==staff_data[p.staff_id] and p.stamina==0 and p.source_state==2 and p.source_goal==Vector2i(6,6) and p.route==[Vector2i(5,6)])
    var clone=setup();assert(clone.load_state(JSON.parse_string(JSON.stringify(s.save_state()))))
    assert(clone.config.store.source_fire_recount)
    for y in s.config.store.source_floor.size():
        for x in s.config.store.source_floor[y].size():assert(int(clone.config.store.source_floor[y][x])==int(s.config.store.source_floor[y][x]))
    assert(clone.layout.fixtures.size()==s.layout.fixtures.size() and clone.economy.cash_yen==cash)
    # Native derived parking recount happens on the next operating update;
    # surviving workers then recover naturally, without dangling fixture access.
    for sim in [s,clone]:
        sim.try_set_business_hours("closed")
        for i in 40:sim.tick()
        assert(sim._parking_used==0 and not sim.config.store.has("source_fire_recount"))
    assert(s._program_rng.seed==clone._program_rng.seed)
    print("FIRE_PASS 213 original scans + 213 customer cleanups; all53 fixtures/all rotations; exact floors/grid/RNG; native aftermath and JSON continuation")
    quit()
