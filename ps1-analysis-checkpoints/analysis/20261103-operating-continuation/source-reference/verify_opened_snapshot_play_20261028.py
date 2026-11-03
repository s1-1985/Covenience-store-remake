"""Continue from a verified native opening snapshot without replaying startup each run."""
from check_machine import *
from caller_connection_harness import Memory
from category_background_frame_harness import BackgroundCategoryRunner
from menu_generator_monitor import MenuGeneratorMonitor
from staff_visual_monitor import StaffVisualMonitor
from opening_lifecycle_monitor import OpeningLifecycleMonitor
from land_town_monitor import LandTownMonitor
from title_resources_20261028 import NativeNewgameResources,ASSETS,BUF
from async_initial_voice_bridge import AsyncInitialVoice
from native_upload_probe import PATCHES
from title_opening_play_connection_20261028 import Connection
from source_spawn_monitor_20261028 import SourceSpawnMonitor
from verify_schedule_selector_frames import seq
from unicorn import UC_HOOK_CODE
import json,zlib,hashlib,gc
R=Path(__file__).resolve().parent
def compare(name='TOWN0001',iterations=60,actions=None,operation=False,native_music=False,progress_file=None,progress_snapshot=None,finance_monitor=False,input_plans=None,customer_monitor=False,refill_monitor=False,finance_display_frames=None,event_monitor=False,whole_town_monitor=False,acquisition_monitor=False,operation_parent_monitor=False,staff_loop_monitor=False):
    root=R/'source/opened-snapshots-20261028';meta=json.loads((root/(name+'.json')).read_text())
    ram=zlib.decompress((root/(name+'.ram.zlib')).read_bytes());assert hashlib.sha256(ram).hexdigest()==meta['ram_sha256']
    assert hashlib.sha256(EXE.read_bytes()).hexdigest()==meta['source_executable_sha256']
    from interior_catalog import IMAGES as DISC_IMAGES
    from runtime_tables import runtime_product_images
    images=[list(struct.unpack_from('<12i',ram,0x9ce14+88*k)) for k in range(27)]
    once=runtime_product_images(DISC_IMAGES)
    provenance='single_conversion' if images==once else 'double_conversion' if images==runtime_product_images(once) else 'other'
    exe_tables=EXE.read_bytes()
    tile_provenance=all(struct.unpack_from('<4i',ram,0x9c7a0+k*16)==
                        tuple(v+60 for v in struct.unpack_from('<4i',exe_tables,0x9c7a0-0x10000+2048+k*16))
                        for k in range(101))
    if 'single' in name:assert provenance=='single_conversion' and tile_provenance,name
    transfers=[];selections=[];customers=[];refills=[];events=[];consumers=[];monthly_screens=[];notification_displays=[]
    units=[];runners=[];resources=[];voices=[];monitors=[];spawns=[];finances=[]
    c=Connection(iterations=iterations,raws=[0]*(iterations*20+2000),actions=actions,native_music=native_music)
    c.progress_file=progress_file
    c.resume_play=meta.get('phase')=='play_iteration_end';c.completed_before=meta.get('completed_iterations',0)
    c.progress_snapshot=progress_snapshot;c.parent_snapshot_sha256=meta['ram_sha256']
    c.title=[meta['title'],meta['title']]
    for which in range(2):
        u=machine();u.mem_write(0,ram)
        for k,v in meta['registers'].items():u.reg_write(int(k),v)
        # Snapshot contains the old explicit hardware-probe NOPs; restore source
        # before installing the fresh probe so its reversible patches stay valid.
        exe=EXE.read_bytes()
        for a in PATCHES:Memory(u).write(a,exe[a-0x80010000+2048:a-0x80010000+2052])
        plans={0x80065690:[[0]*200 for _ in range(300)],0x800656f8:[seq([32])+[0]*200 for _ in range(300)]}
        if input_plans:plans.update(input_plans)
        if operation:plans[0x80060418]=[seq([64])+[0]*100 for _ in range(20)]
        r=BackgroundCategoryRunner(u,meta['bank'],plans,allow_scaled=True,table_address=0x800e3b20+64*meta['bank'])
        if input_plans and 0x80077de4 in input_plans:
            from source_interior_selection_monitor_20261030 import SourceInteriorSelectionMonitor
            selection=SourceInteriorSelectionMonitor(u,r);selections.append(selection);monitors.append(selection)
        if input_plans and 0x80071ddc in input_plans:
            from source_transfer_monitor_20261030 import SourceTransferMonitor
            transfer=SourceTransferMonitor(u,r);transfers.append(transfer);monitors.append(transfer)
            from source_full_transfer_monitor_20261103 import SourceFullTransferMonitor
            from transfer_profile_monitor import TransferProfileMonitor
            from source_transfer_wage_monitor_20261103 import SourceTransferWageMonitor
            monitors.extend([SourceFullTransferMonitor(u,r),TransferProfileMonitor(u,r),SourceTransferWageMonitor(u)])
        resource=NativeNewgameResources(u,r,native_gpu=True,preserve_cache=True,stack_floor=0x801ff000)
        resource.shadows={int(a,16):bytes.fromhex(b) for a,b in meta['resource_shadows'].items()}
        resource.buffer_assets={int(a,16):ASSETS[tuple(k)] for a,k in meta['resource_assets'].items()}
        resource.shadow=resource.shadows.get(BUF);resource.buffer_asset=resource.buffer_assets.get(BUF)
        voice=AsyncInitialVoice(u,r,base=None,profile=meta['bank']);voice.registered=meta['voice_registered'];voice.allowed_voices=range(131)
        monitors += [MenuGeneratorMonitor(u,r,192,9216,272),StaffVisualMonitor(u,r),OpeningLifecycleMonitor(u,r),LandTownMonitor(u,r)]
        if staff_loop_monitor:
            from source_staff_loop_monitor_20261103 import SourceStaffLoopMonitor
            monitors.append(SourceStaffLoopMonitor(u,r))
        if whole_town_monitor:
            from source_town_monthly_monitor_20261102 import SourceTownMonthlyMonitor
            monitors.append(SourceTownMonthlyMonitor(u,r))
        if acquisition_monitor:
            from source_acquisition_monitor_20261102 import SourceAcquisitionMonitor
            from source_store_milestone_monitor_20261102 import SourceStoreMilestoneMonitor
            monitors.extend([SourceAcquisitionMonitor(u,r),SourceStoreMilestoneMonitor(u,r)])
        if operation_parent_monitor:
            from source_operation_parent_monitor_20261103 import SourceOperationParentMonitor
            monitors.append(SourceOperationParentMonitor(u,r))
        spawn=SourceSpawnMonitor(u);spawns.append(spawn)
        if event_monitor:
            from source_event_reservation_monitor_20261031 import SourceEventReservationMonitor
            event=SourceEventReservationMonitor(u,r);events.append(event);monitors.append(event)
            from source_event_consumer_monitor_20261031 import SourceEventConsumerMonitor
            consumer=SourceEventConsumerMonitor(u,r);consumers.append(consumer);monitors.append(consumer)
            from source_monthly_screen_monitor_20261031 import SourceMonthlyScreenMonitor
            screen=SourceMonthlyScreenMonitor(u,r);monthly_screens.append(screen);monitors.append(screen)
            from source_notification_display_monitor_20261031 import SourceNotificationDisplayMonitor
            display=SourceNotificationDisplayMonitor(u,r);notification_displays.append(display);monitors.append(display)
        if refill_monitor:
            from source_refill_monitor_20261030 import SourceRefillMonitor
            refill=SourceRefillMonitor(u,r);refills.append(refill);monitors.append(refill)
        if customer_monitor:
            from source_customer_loop_monitor_20261030 import SourceCustomerLoopMonitor
            customer=SourceCustomerLoopMonitor(u,r);customers.append(customer);monitors.append(customer)
        if finance_monitor:
            from source_finance_monitor_20261029 import SourceFinanceMonitor
            finance=SourceFinanceMonitor(u,r,pending_display_frames=finance_display_frames);finances.append(finance);monitors.append(finance)
        if native_music:
            from native_music_bridge_20261029 import NativeMusic
            c.music_bridges.append(NativeMusic(u,resource))
        def boundary(z,a,n,d,which=which):
            regs=(UC_MIPS_REG_A0,UC_MIPS_REG_A1,UC_MIPS_REG_A2)[:2 if a==0x80065100 else 3]
            (c.music if a==0x80065100 else c.volume)[which].append([z.reg_read(reg) for reg in regs])
            if native_music:return
            z.reg_write(UC_MIPS_REG_V0,0);z.reg_write(UC_MIPS_REG_PC,z.reg_read(UC_MIPS_REG_RA))
        for a in (0x80065100,0x8008eaec):c.hooks.append((u,u.hook_add(UC_HOOK_CODE,boundary,begin=a,end=a)))
        units.append(u);runners.append(r);resources.append(resource);voices.append(voice)
    result=c.after_opening(units,runners,resources,voices)
    assert spawns[0].checks==spawns[1].checks
    if finances:
        assert finances[0].checks==finances[1].checks and finances[0].time_gates==finances[1].time_gates
        assert finances[0].ui_checks==finances[1].ui_checks
        result['midnight_finance_checks']=finances[0].checks;result['finance_time_gate_count']=finances[0].time_gates
        result['finance_early_ui_checks']=finances[0].ui_checks
    if transfers:
        assert transfers[0].checks==transfers[1].checks
        result['transfer_binding_checks']=transfers[0].checks
        full=[mon.checks for mon in monitors if isinstance(mon,SourceFullTransferMonitor)]
        profiles=[mon.checks for mon in monitors if isinstance(mon,TransferProfileMonitor)]
        assert full[0]==full[1] and profiles[0]==profiles[1]
        result.update(full_transfer_checks=full[0],transfer_profile_checks=profiles[0])
        wages=[mon.checks for mon in monitors if isinstance(mon,SourceTransferWageMonitor)]
        assert wages[0]==wages[1];result['transfer_wage_checks']=wages[0]
    if selections:
        assert selections[0].checks==selections[1].checks
        result['interior_selection_checks']=selections[0].checks
    if customers:
        assert customers[0].checks==customers[1].checks
        result['customer_loop_checks']=customers[0].checks
    if refills:
        assert refills[0].checks==refills[1].checks and refills[0].postings==refills[1].postings
        result['restock_checks']=refills[0].checks
        result['stock_posting_checks']=refills[0].postings
        result['accounting_write_trace']=refills[0].accounting_writes
    if events:
        assert events[0].checks==events[1].checks
        result['event_reservation_checks']=events[0].checks
        assert consumers[0].checks==consumers[1].checks
        result['event_consumer_checks']=consumers[0].checks
        assert monthly_screens[0].checks==monthly_screens[1].checks
        result['monthly_screen_checks']=monthly_screens[0].checks
        assert notification_displays[0].checks==notification_displays[1].checks
        result['notification_display_checks']=notification_displays[0].checks
    result['placement_checks']=[r.placement_checks for r in runners]
    assert result['placement_checks'][0]==result['placement_checks'][1]
    result['ui_phases']=[r.phase_entries for r in runners]
    assert result['ui_phases'][0]==result['ui_phases'][1]
    result['lifecycle_checks']=[m.checks for m in monitors if isinstance(m,OpeningLifecycleMonitor)]
    assert result['lifecycle_checks'][0]==result['lifecycle_checks'][1]
    result['runtime_table_provenance']=provenance
    if staff_loop_monitor:
        checks=[mon.checks for mon in monitors if isinstance(mon,SourceStaffLoopMonitor)]
        assert len(checks)==2 and checks[0]==checks[1];result['whole_staff_loop_checks']=checks[0]
    if whole_town_monitor:
        checks=[mon.checks for mon in monitors if isinstance(mon,SourceTownMonthlyMonitor)]
        assert len(checks)==2 and checks[0]==checks[1]
        result['whole_monthly_town_checks']=checks[0]
    if acquisition_monitor:
        acq=[mon for mon in monitors if isinstance(mon,SourceAcquisitionMonitor)]
        goal=[mon for mon in monitors if isinstance(mon,SourceStoreMilestoneMonitor)]
        assert acq[0].checks==acq[1].checks and acq[0].input_checks==acq[1].input_checks and acq[0].selection_checks==acq[1].selection_checks
        assert goal[0].checks==goal[1].checks
        result.update(acquisition_checks=acq[0].checks,acquisition_inputs=acq[0].input_checks,acquisition_selections=acq[0].selection_checks,milestone_checks=goal[0].checks,tim_skips=resources[0].tim_skips)
    if operation_parent_monitor:
        ops=[mon.checks for mon in monitors if isinstance(mon,SourceOperationParentMonitor)]
        assert ops[0]==ops[1];result['operation_parent_checks']=ops[0]
    result['single_conversion_appearance_verified']=tile_provenance
    result.update(snapshot=name,snapshot_sha256=meta['ram_sha256'],source_spawn_checks=spawns[0].checks,
                  frames=runners[0].frames,resource_loads=resources[0].loads,resource_transfers=resources[0].transfers,
                  voice_starts=voices[0].starts,voice_updates=voices[0].updates,
                  limits=['CPU RAM/register snapshot at source opening return12860 or verified play iteration end5D5A4; phase is recorded in metadata.',
                          'Original wrapper/dispatcher/play resumes; independent parent/input/render/spawn policies plus native children.',
                          'New hardware adapters reinstall controlled SDK endpoints. Prior physical VRAM/audio playback is not restored or proven.',
                          'No native gameplay field/clock injection between opening and iterations. Actions schedule raw frame inputs.'])
    for m in monitors+spawns+resources+voices:m.dispose()
    for r in runners:r.dispose()
    return result
if __name__=='__main__':
    import argparse
    p=argparse.ArgumentParser();p.add_argument('--town',default='TOWN0001');p.add_argument('--iterations',type=int,default=60);p.add_argument('--scenario',choices=('idle','views','pause'),default='idle');a=p.parse_args()
    actions=None if a.scenario=='idle' else ({0:64,2:16,4:32,6:128,8:64,10:12,12:12,14:16,16:32} if a.scenario=='views' else {0:0x800,4:0x800})
    row=compare(a.town,a.iterations,actions,a.scenario=='views')
    out=dict(total=1,all_passed=True,iterations_verified=a.iterations,frames_verified=len(row['frames']),cases=[row],limits=row['limits'])
    (R/f'opened-snapshot-{a.town}-{a.scenario}-{a.iterations}-verification-20261028.json').write_text(json.dumps(out,separators=(',',':')))
    print('source snapshot play passed',a.town,a.scenario,a.iterations,'clock',row['steps'][-1]['clock'],flush=True)
