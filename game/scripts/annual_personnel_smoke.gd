extends SceneTree
const Sim=preload("res://scripts/vertical_slice_simulation.gd")
const Start=preload("res://scripts/domain/guide_starting_store.gd")
const Rule=preload("res://scripts/domain/program_annual_personnel.gd")
const RNG=preload("res://scripts/domain/program_random.gd")
func setup():
    var base:Dictionary=JSON.parse_string(FileAccess.get_file_as_string("res://data/vertical_slice.json"))
    var s=Sim.new(Start.apply(base));s.economy.cash_yen=1000000000
    assert(s.try_buy_store_site(Vector2i(26,12)))
    assert(s.try_buy_store_site(Vector2i(3,3),"small_top"))
    s._for_each_store(func():s.try_set_business_hours("closed"))
    for rival in s._rival_stores:s._program_rival_simulation(rival)
    s.notifications.reset()
    return s
func traits(s,age:int) -> void:
    for id in s.config.source_scenario.staff_order:
        var raises:Dictionary=s._candidate_raises.get(id,{})
        raises.age_years=age-int(s._staff_candidate_catalog[id].age_years)
        s._candidate_raises[id]=raises
func _initialize() -> void:
    var evidence:Dictionary=JSON.parse_string(FileAccess.get_file_as_string("res://tests/fixtures/source_annual_personnel.json"))
    assert(Rule.DEFAULT_RAISE_PERCENT==int(evidence.default_percent))
    for row in evidence.wages:
        var wages:Array=[]
        for value in row.before:wages.append(int(value))
        for ref in row.assignments:
            if int(ref)>=0:wages[int(ref)]=Rule.wage(int(wages[int(ref)]))
        for i in 3:assert(wages[i]==int(row.after[i]))
    for row in evidence.ages:
        var rng=RNG.new();rng.seed=int(row.seed)
        for i in 35:
            var result:Dictionary=Rule.age_person(int(row.before[i]),rng)
            assert(result.age==int(row.after[i].age) and result.boosted==bool(row.after[i].boosted))
        assert(rng.seed==int(row.seed_after))
    var s=setup();s.month_count=12
    var own=s.staff.members["staff-1"]
    var child=s._program_rival_simulation(s._rival_stores[0]);var other=child.staff.members["staff-1"]
    own.stamina=17;own.register_skill=21;own.source_state=2
    other.stamina=13;other.cleaning_skill=23;other.source_state=2
    var own_ceiling:int=own.register_skill_growth_ceiling;var other_ceiling:int=other.cleaning_skill_growth_ceiling
    var own_hourly:int=own.salary_yen_per_day_24h/24;var rival_hourly:int=other.salary_yen_per_day_24h/24
    # A free retained person is aged and can boost, but is not given a raise.
    var free_id:String=s.source_free_candidates()[0]
    s._unassigned_staff[free_id]={"stamina":11,"stamina_max":int(s._candidate_figures(free_id).stamina),"salary_yen_per_day_24h":int(s._staff_candidate_catalog[free_id].salary_yen_per_day_24h)}
    var free_wage:int=s._unassigned_staff[free_id].salary_yen_per_day_24h
    traits(s,126)
    var seed:int=s._program_rng.seed
    var active:int=s.active_store
    s._apply_source_annual_personnel(1)
    assert(s._program_rng.seed==seed and s.active_store==active,"127-year boost consumes no RNG and preserves selected store")
    for id in s.config.source_scenario.staff_order:
        var figures:Dictionary=s._candidate_figures(id)
        assert(figures.age_years==127)
        for field in ["stamina","education","agility","sociability","academic_background"]:assert(int(figures[field])==100)
        assert(child._candidate_figures(id).age_years==127)
    assert(own.stamina_max==100 and own.stamina==17 and own.register_skill==21 and own.source_state==2)
    assert(other.stamina_max==100 and other.stamina==13 and other.cleaning_skill==23 and other.source_state==2)
    assert(own.register_skill_growth_ceiling==own_ceiling and other.cleaning_skill_growth_ceiling==other_ceiling)
    assert(own.salary_yen_per_day_24h==Rule.wage(own_hourly)*24)
    assert(other.salary_yen_per_day_24h==Rule.wage(rival_hourly)*24)
    assert(int(s._candidate_figures(own.candidate_id).salary_yen_per_day_24h)==own.salary_yen_per_day_24h)
    assert(s._unassigned_staff[free_id].stamina_max==100 and s._unassigned_staff[free_id].stamina==11 and s._unassigned_staff[free_id].salary_yen_per_day_24h==free_wage)
    # Rival children only roll their local annual ledger, never world people.
    var rival_wage:int=other.salary_yen_per_day_24h
    child.month_count=12;child._annual_review(false)
    assert(other.salary_yen_per_day_24h==rival_wage and s._program_rng.seed==seed)
    var saved:Dictionary=JSON.parse_string(JSON.stringify(s.save_state()))
    var clone=setup();assert(clone.load_state(saved))
    var cloned_child=clone._program_rival_simulation(clone._rival_stores[0])
    assert(cloned_child._candidate_figures(free_id).age_years==127)
    var clone_seed:int=clone._program_rng.seed
    clone._apply_source_annual_personnel(1)
    assert(clone._program_rng.seed==clone_seed and clone.staff.members["staff-1"].salary_yen_per_day_24h==own.salary_yen_per_day_24h)
    # Shared metadata remains shared immediately after JSON and later awards.
    var shared:Dictionary=clone._candidate_raises[other.candidate_id]
    shared.education=80-int(clone._staff_candidate_catalog[other.candidate_id].education)
    cloned_child._raise_manager(["education"],2)
    assert(clone._candidate_figures(other.candidate_id).education==82)
    clone.select_store(0)
    var id:String=clone.staff.members["staff-2"].candidate_id
    var wage:int=clone.staff.members["staff-2"].salary_yen_per_day_24h
    assert(clone.try_dismiss_source_staff("staff-2"))
    assert(int(clone._candidate_figures(id).salary_yen_per_day_24h)==wage)
    var assignment:Array=clone.source_staff_assignment();assignment[1]=id
    assert(clone.try_assign_source_staff(assignment))
    assert(clone.staff.members["staff-2"].salary_yen_per_day_24h==wage and clone.staff.members["staff-2"].stamina_max==100)
    # Exact world35 order/RNG, including unassigned people and rival employees.
    var mixed:Dictionary=evidence.ages[-1]
    var order:Array=clone.config.source_scenario.staff_order
    for i in 35:
        var raises:Dictionary=clone._candidate_raises.get(str(order[i]),{})
        raises.age_years=int(mixed.before[i])-int(clone._staff_candidate_catalog[str(order[i])].age_years)
        clone._candidate_raises[str(order[i])]=raises
    clone._program_rng.seed=int(mixed.seed);clone.month_count=24
    clone._apply_source_annual_personnel(2)
    assert(clone._program_rng.seed==int(mixed.seed_after))
    for i in 35:assert(int(clone._candidate_figures(str(order[i])).age_years)==int(mixed.after[i].age))
    # A branch withdrawn after this year's finance releases the same
    # person/wage into the pool rather than dropping the runtime record.
    var withdrawn:Dictionary=clone._rival_stores[-1]
    var departing=clone._program_rival_simulation(withdrawn).staff.all_staff()[0]
    var departing_id:String=departing.candidate_id
    var departing_wage:int=departing.salary_yen_per_day_24h
    withdrawn.monthly_profit_yen=-1;withdrawn.deficit_months=5
    clone._program_rival_monthly()
    assert(clone._rival_index(str(withdrawn.id))<0 and clone.source_free_candidates().has(departing_id))
    assert(int(clone._unassigned_staff[departing_id].salary_yen_per_day_24h)==departing_wage)
    var bad:Dictionary=saved.duplicate(true);bad.source_hourly_wages={"unknown":1};assert(not clone.load_state(bad))
    bad=saved.duplicate(true);bad.source_annual_personnel_year=1.5;assert(not clone.load_state(bad))
    var legacy:Dictionary=saved.duplicate(true);legacy.erase("source_hourly_wages");legacy.erase("source_annual_personnel_year")
    var old=setup();assert(old.load_state(legacy))
    var old_seed:int=old._program_rng.seed;old._apply_source_annual_personnel(1)
    assert(old._program_rng.seed==old_seed,"Old saved year already passed; do not replay aging")
    var base:Dictionary=JSON.parse_string(FileAccess.get_file_as_string("res://data/vertical_slice.json"))
    var inactive=Sim.new(Start.apply(base));traits(inactive,126)
    var inactive_person=inactive.staff.members["staff-1"]
    var inactive_wage:int=inactive_person.salary_yen_per_day_24h
    var inactive_energy:int=inactive_person.stamina
    inactive._apply_source_annual_personnel(1)
    assert(inactive_person.salary_yen_per_day_24h==inactive_wage and inactive_person.stamina==inactive_energy and inactive_person.stamina_max==100)
    print("ANNUAL_PERSONNEL_PASS 51 original excerpts, one global35 age/RNG loop, both-company wages, unchanged current stamina/skills, shared traits, free retained person, JSON/rehire/legacy")
    quit()
