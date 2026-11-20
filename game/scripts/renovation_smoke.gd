extends SceneTree
const Sim=preload("res://scripts/vertical_slice_simulation.gd")
const Start=preload("res://scripts/domain/guide_starting_store.gd")
func _initialize() -> void:
    var base: Dictionary=JSON.parse_string(FileAccess.get_file_as_string("res://data/vertical_slice.json"))
    var evidence: Dictionary=JSON.parse_string(FileAccess.get_file_as_string("res://tests/fixtures/source_renovation.json"))
    var s=Sim.new(Start.apply(base))
    s.economy.cash_yen=1000000000
    assert(s.try_buy_store_site(Vector2i(26,12)))
    var types: Array=s.store_types()
    var original: String=s.store_type_id
    for old in types:
        s.store_type_id=str(old.id)
        for i in 6:
            assert(s.renovation_price_yen(str(types[i].id))==int(evidence.cases[i].fee_yen))
    s.store_type_id=original
    s.try_set_business_hours("24h")
    var before: Dictionary=s.save_state()
    assert(not s.try_renovate_store(str(types[2].id)))
    assert(JSON.stringify(s.save_state())==JSON.stringify(before),"Open-store refusal must not mutate the simulation")
    s.try_set_business_hours("closed")
    var uid: int=s._store_uid
    s.economy.cash_yen=11999999
    before=s.save_state()
    assert(not s.try_renovate_store(str(types[2].id)))
    # edit_refusal is presentation state and is not part of the save.
    assert(JSON.stringify(s.save_state())==JSON.stringify(before))
    s.economy.cash_yen=12000000
    assert(not s.try_renovate_store(str(types[2].id),uid+1))
    assert(not s.try_renovate_store(str(types[2].id),uid,"stale-type"))
    var person=s.staff.members["staff-1"]
    person.register_skill=87
    person.stamina=31
    var candidate: String=person.candidate_id
    s.customers._next_sequence=70
    var permit_count: int=s._permits_held.size()
    var count: int=s.economy.expense_records.size()
    assert(s.try_renovate_store(str(types[2].id),uid,original))
    assert(s.economy.cash_yen==0 and s.economy.expense_records.size()==count+1)
    assert(s.economy.expense_records[-1].expense_type=="store_renovation")
    assert(s.customers._next_sequence==70 and s._permits_held.size()==permit_count)
    assert(s.staff.members["staff-1"].register_skill==87 and s.staff.members["staff-1"].stamina==31)
    assert(s.staff.members["staff-1"].candidate_id==candidate)
    # All six actual migrations, including a same-type rebuild and a
    # shrink, keep source staff inside the new floor and discard old goals.
    for entry in types:
        s.economy.cash_yen=1000000000
        var cost: int=s.renovation_price_yen(str(entry.id))
        count=s.economy.expense_records.size()
        assert(s.try_renovate_store(str(entry.id)))
        assert(s.economy.cash_yen==1000000000-cost and s.economy.expense_records.size()==count+1)
        assert(s.store_type_id==str(entry.id) and s._store_uid==uid)
        for employee in s.staff.all_staff():
            assert(employee.source_goal==Vector2i(-1,-1) and employee.route.is_empty())
            assert(Rect2i(0,0,s.layout.width_subcells,s.layout.height_subcells).has_point(employee.position))
        var saved: Dictionary=JSON.parse_string(JSON.stringify(s.save_state()))
        var clone=Sim.new(Start.apply(base))
        assert(clone.load_state(saved))
        assert(clone.store_type_id==s.store_type_id and clone.layout.width_subcells==s.layout.width_subcells)
        assert(clone.economy.cash_yen==s.economy.cash_yen and clone.staff.members["staff-1"].register_skill==87)
    assert(s.try_buy_store_site(Vector2i(3,3),"small_top"))
    s.select_store(1)
    var branch_uid: int=s._store_uid
    s.try_set_business_hours("closed")
    assert(s.try_renovate_store(str(types[2].id),branch_uid))
    assert(int(s.economy.expense_records[-1].store_uid)==branch_uid)
    s.try_set_business_hours("24h")
    for i in 160: s.step()
    print("RENOVATION_PASS 36 fee pairs, open/cash/UID guards, same-size and shrinking, single payment, staff skills/goals, sequence, branch and JSON replay")
    quit()
