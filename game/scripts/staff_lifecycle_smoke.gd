extends SceneTree
const Sim=preload("res://scripts/vertical_slice_simulation.gd")
const Start=preload("res://scripts/domain/guide_starting_store.gd")
func setup():
    var base:Dictionary=JSON.parse_string(FileAccess.get_file_as_string("res://data/vertical_slice.json"))
    var s=Sim.new(Start.apply(base))
    s.economy.cash_yen=1000000000
    assert(s.try_buy_store_site(Vector2i(26,12)))
    return s
func _initialize() -> void:
    var fixture:Dictionary=JSON.parse_string(FileAccess.get_file_as_string("res://tests/fixtures/source_staff_lifecycle.json"))
    for row in fixture.cases:
        var s=setup()
        var ids:Array=s.source_staff_assignment()
        ids.append(s.source_free_candidates()[0])
        for i in 3:
            var p=s.staff.members["staff-%d" % (i+1)]
            p.stamina_max=80+i;p.stamina=1;p.source_assignment_experience=10+i
            p.source_state=3;p.source_goal=Vector2i(7,7);p.register_skill=57+i
        s._unassigned_staff[ids[3]]={"stamina_max":83,"stamina":1,"source_assignment_experience":13,"register_skill":60}
        var unchanged=s.staff.members["staff-3"]
        var draft:Array=[]
        for index in row.new_slots: draft.append("" if int(index)<0 else ids[int(index)])
        assert(s.try_assign_source_staff(draft))
        assert(s.staff.members["staff-3"]==unchanged and unchanged.source_state==3 and unchanged.source_goal==Vector2i(7,7))
        for expected in row.people:
            var index:int=int(expected.id)
            var p=null
            if expected.new_slot != null:
                p=s.staff.members["staff-%d" % (int(expected.new_slot)+1)]
                assert(p.candidate_id==ids[index])
                assert(p.stamina==int(expected.energy_after))
                assert(p.source_assignment_experience==int(expected.experience_after))
                assert(p.register_skill==57+index)
                if expected.old_slot != expected.new_slot:
                    assert(p.source_state==0 and p.source_goal==Vector2i(-1,-1) and p.route.is_empty())
            else:
                assert(int(s._unassigned_staff[ids[index]].stamina)==int(expected.energy_after))
        # No-op must preserve a person's complete current work state.
        assert(s.try_assign_source_staff(draft))
        assert(s.staff.members["staff-3"]==unchanged and unchanged.stamina==1)
    var fresh=setup()
    var fresh_id:String=fresh.source_free_candidates()[0]
    assert(fresh.source_free_candidates().has(fresh_id))
    assert(fresh.try_dismiss_source_staff("staff-2"))
    var initial:int=fresh._candidate_figures(fresh_id).source_assignment_experience
    assert(fresh.try_hire_candidate("staff-2",fresh_id))
    assert(fresh.staff.members["staff-2"].stamina==int(fresh._candidate_figures(fresh_id).source_initial_stamina))
    assert(fresh.staff.members["staff-2"].source_assignment_experience==initial+1)
    var s=setup()
    var p=s.staff.members["staff-2"]
    var id:String=p.candidate_id
    p.register_skill=91;p.service_skill=88;p.salary_yen_per_day_24h=12345
    p.stamina=1;p.source_assignment_experience=9;p.register_skill_growth_ceiling=96
    assert(s.try_dismiss_source_staff("staff-2"))
    assert(int(s._unassigned_staff[id].stamina)==p.stamina_max)
    var clone=setup();assert(clone.load_state(JSON.parse_string(JSON.stringify(s.save_state()))))
    assert(clone.try_hire_candidate("staff-2",id))
    p=clone.staff.members["staff-2"]
    assert(p.register_skill==91 and p.service_skill==88 and p.salary_yen_per_day_24h==12345)
    assert(p.source_assignment_experience==10 and p.register_skill_growth_ceiling==96 and p.stamina==p.stamina_max)
    var loaded=setup();assert(loaded.load_state(JSON.parse_string(JSON.stringify(clone.save_state()))))
    assert(loaded.staff.members["staff-2"].source_assignment_experience==10,"Loading must not increment experience")
    assert(loaded.staff.members["staff-2"].register_skill_growth_ceiling==96)
    # Duplicate or foreign/unknown IDs must reject before releasing anyone.
    var before:Array=loaded.source_staff_assignment()
    assert(not loaded.try_assign_source_staff([before[0],before[0],before[2]]))
    assert(not loaded.try_assign_source_staff([before[0],"missing-candidate",before[2]]))
    assert(loaded.source_staff_assignment()==before)
    # Same-store swaps recover stamina and increment, cross-store transfers do neither.
    assert(loaded.try_transfer_source_staff(0,"staff-1",0,"staff-2"))
    p=loaded.staff.members["staff-1"]
    assert(p.source_assignment_experience==11 and p.stamina==p.stamina_max)
    assert(loaded.try_buy_store_site(Vector2i(3,3),"small_top"))
    p=loaded.store_field(0,"staff").members["staff-1"]
    p.stamina=2
    var experience:int=p.source_assignment_experience
    assert(loaded.try_transfer_source_staff(0,"staff-1",1,"staff-2"))
    assert(loaded.store_field(1,"staff").members["staff-2"]==p and p.stamina==2 and p.source_assignment_experience==experience)
    print("STAFF_LIFECYCLE_PASS four source transactions, unchanged work, two-pass swap, cached rehire, JSON, transfer distinction, invalid drafts")
    quit()
