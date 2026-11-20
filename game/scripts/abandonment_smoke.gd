extends SceneTree
const Sim=preload("res://scripts/vertical_slice_simulation.gd")
const Starting=preload("res://scripts/domain/guide_starting_store.gd")
const Customer=preload("res://scripts/domain/customer_state.gd")
const People=preload("res://scripts/domain/program_people.gd")
const SKILLS=["register_skill","replenishment_skill","service_skill","cleaning_skill","security_skill"]
func setup():
    var base:Dictionary=JSON.parse_string(FileAccess.get_file_as_string("res://data/vertical_slice.json"))
    var s=Sim.new(Starting.apply(base))
    s.economy.cash_yen=1000000000
    assert(s.try_buy_store_site(Vector2i(26,12)))
    return s
func customer(s,amount:int=610,heads:int=3):
    var p=Customer.new({"id":"abandonment-customer"})
    p.source_native=true;p.source_state=3;p.phase="waiting_checkout"
    p.position=s.layout.entry;p.budget_left=190;p.group_size=heads
    p.visit={"stamina":5,"quickness":100}
    if amount>0:
        p.basket.append({"product_id":s.inventory.product_order[0],"unit_price_yen":amount,"quantity":heads})
    s.customers.customers[p.customer_id]=p
    return p
func _initialize() -> void:
    var fixture:Dictionary=JSON.parse_string(FileAccess.get_file_as_string("res://tests/fixtures/source_abandonment.json"))
    var s=setup()
    var roster:Dictionary=s.staff.members.duplicate()
    for row in fixture.cases:
        s.staff.members=roster.duplicate()
        for i in 3:
            var person=s.staff.members["staff-%d" % (i+1)]
            for k in 5:person.set(SKILLS[k],int(fixture.base_skills[i][k]))
            if not row.slots.map(func(n):return int(n)).has(i):s.staff.members.erase("staff-%d" % (i+1))
        s.customers.reset();s.economy.reset();s.economy.cash_yen=100000
        var p=customer(s,int(row.cart_before),int(row.heads))
        p.set_meta("checkout_patience",int(row.patience_before))
        s.internal_rating_value=int(row.rating_before);s.popularity=66
        s._notice_counts.angry=int(row.counter_before)
        s._program_rng.seed=int(row.seed)
        var sales:int=s._store_sales_yen
        var departed:bool=s._program_wait_at_checkout(p,false,bool(row.force))
        assert(departed==not bool(row.continues))
        assert(int(p.get_meta("checkout_patience"))==int(row.patience_after))
        assert(s.economy.cash_yen-100000==int(row.cash_delta))
        assert(s._store_sales_yen-sales==int(row.sales_delta))
        assert(p.basket_total_yen()==int(row.cart_after)*int(row.heads))
        assert(p.budget_left==int(row.budget_after))
        assert(s.internal_rating_value==int(row.rating_after) and s.popularity==int(row.popularity_after))
        assert(s._notice_counts.angry==int(row.counter_after) and s._program_rng.seed==int(row.seed_after),str(row)+" GOT "+str(s._notice_counts.angry)+" / "+str(s._program_rng.seed))
        for i in 3:
            if not s.staff.members.has("staff-%d" % (i+1)):continue
            for k in 5:assert(int(s.staff.members["staff-%d" % (i+1)].get(SKILLS[k]))==int(row.skills_after[i][k]))
    # Posting empties the unpaid cart immediately; another call cannot pay it twice.
    s=setup()
    var p=customer(s)
    p.set_meta("checkout_patience",0)
    var cash:int=s.economy.cash_yen
    assert(s._program_wait_at_checkout(p,false))
    assert(p.basket.is_empty() and s.economy.cash_yen==cash+1830)
    assert(s._program_wait_at_checkout(p,false))
    assert(s.economy.cash_yen==cash+1830 and s.economy.sale_records.size()==1)
    # Another legitimately acquired batch by the same visitor is independently
    # payable. Ordinary/prototype duplicate-customer safeguards stay enabled.
    p.basket.append({"product_id":s.inventory.product_order[0],"unit_price_yen":110,"quantity":3})
    s._settle_source_basket(p)
    assert(s.economy.cash_yen==cash+2160 and p.settled_total_yen==2160 and p.budget_left==190)
    assert(s.economy.sale_records[0].customer_id==p.customer_id and s.economy.sale_records[1].customer_id==p.customer_id)
    var paid_clone=setup();assert(paid_clone.load_state(JSON.parse_string(JSON.stringify(s.save_state()))))
    var paid_customer=paid_clone.customers.customers[p.customer_id]
    paid_customer.basket.append({"product_id":paid_clone.inventory.product_order[0],"unit_price_yen":100,"quantity":3})
    paid_clone._settle_source_basket(paid_customer)
    assert(paid_customer.settled_total_yen==2460 and paid_clone.economy.cash_yen==cash+2460)
    # The original exit routine has no wait/abandonment call: a blocked
    # departing shoplifter must retain unpaid goods without producing sales.
    s=setup();p=customer(s);p.source_state=5;p.phase="leaving"
    p.position=Vector2i(3,3);p.source_goal=Vector2i(5,3)
    p.route.assign([Vector2i(4,3)])
    s.staff.members["staff-1"].position=Vector2i(4,3)
    s.staff.members["staff-1"].source_state=1
    p.set_meta("checkout_patience",0)
    cash=s.economy.cash_yen
    People.move(s,p,0,false)
    assert(s.economy.cash_yen==cash and p.basket_total_yen()==1830 and int(s._notice_counts.angry)==0)
    # Mid-wait JSON resumes with the same RNG, skills, rating, money and count.
    s=setup();p=customer(s);p.set_meta("checkout_patience",1)
    s._notice_counts.angry=126;s._program_rng.seed=2
    var clone=setup();assert(clone.load_state(JSON.parse_string(JSON.stringify(s.save_state()))))
    var q=clone.customers.customers[p.customer_id]
    assert(s._program_wait_at_checkout(p,false)==clone._program_wait_at_checkout(q,false))
    assert(s._program_rng.seed==clone._program_rng.seed and s.economy.cash_yen==clone.economy.cash_yen)
    assert(s._staff_state_snapshot()==clone._staff_state_snapshot())
    assert(s._notice_counts==clone._notice_counts)
    # A queued visitor with an unreachable register must force departure.
    s=setup();p=customer(s);p.set_meta("checkout_patience",99)
    for f in s.layout.fixtures.duplicate():
        if str(f.get("kind",""))=="checkout":
            s.layout.fixtures.erase(f);s.layout.fixtures_by_id.erase(str(f.id))
    p.source_goal=Vector2i(-1,-1)
    People.customer(s,p)
    assert(p.source_state==5 and p.basket.is_empty() and int(p.get_meta("checkout_patience"))==0)
    print("ABANDONMENT_PASS 132 original cases, forced/normal wait RNG, skill floors, saturation, cart clear, repeated batch, JSON, unreachable checkout")
    quit()
