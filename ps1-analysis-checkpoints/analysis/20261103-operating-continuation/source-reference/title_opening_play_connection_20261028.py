"""Retain native title/opening caller frames, then enter play on the actually opened town.

The reference side keeps independent opening/entry/iteration/master-parent policies.
Child actors remain original native code; physical SDKs remain explicit adapters.
"""
from check_machine import *
from caller_connection_harness import Memory
from title_resources_20261028 import ASSETS
from title_flow_20261028 import TitleMenuMonitor,GP
from title_intro_monitor_20261028 import TitleIntroMonitor
from verify_schedule_selector_frames import seq
from mainplay_entry import run as main_entry
from mainplay_iteration import iteration
from live_master_oracle_20261028 import run as master_update
from main_update_control import ARGS
from verify_mainplay_iteration import CALLS
from recovered import i32
from unicorn import UC_HOOK_CODE
import hashlib,json,zlib

class Connection:
    def __init__(self,iterations=4,raws=None,title_cancel=False,actions=None,native_music=False):
        self.iterations=iterations;self.raws=raws if raws is not None else [0]*1000
        self.title_cancel=title_cancel;self.hooks=[];self.monitors=[];self.title=[];self.music=[[],[]];self.volume=[[],[]]
        self.actions=actions;self.snapshot_name=None
        self.native_music=native_music;self.music_bridges=[]
        self.progress_file=None
        self.resume_play=False;self.completed_before=0;self.progress_snapshot=None;self.parent_snapshot_sha256=None
        self.entry_from_load=False
    def augment_plans(self,plans):
        plans[0x80057bd4]=[[0]*2000 for _ in range(2 if self.title_cancel else 1)]
        plans[0x80059254]=([seq([64])+[0]*20] if self.title_cancel else [])+[seq([32])+[0]*20]
    def before_opening(self,units,runners,resources,voices,startup_parent):
        assert len(resources)==len(voices)==2
        for which,(u,r,resource,voice) in enumerate(zip(units,runners,resources,voices)):
            voice.allowed_voices=range(131);resource.stack_floor=0x801ff000
            if self.native_music:
                from native_music_bridge_20261029 import NativeMusic
                self.music_bridges.append(NativeMusic(u,resource))
            menu=TitleMenuMonitor(u,r);intro=TitleIntroMonitor(u,r);self.monitors += [menu,intro]
            states=[];armed=[False];start_ticks=[]
            def hook(z,a,n,d,which=which,r=r,states=states,armed=armed,start_ticks=start_ticks):
                if a==0x80065100:
                    self.music[which].append([z.reg_read(UC_MIPS_REG_A0),z.reg_read(UC_MIPS_REG_A1)])
                    if self.native_music:return
                    z.reg_write(UC_MIPS_REG_V0,0);z.reg_write(UC_MIPS_REG_PC,z.reg_read(UC_MIPS_REG_RA));return
                if a==0x8008eaec:
                    self.volume[which].append([z.reg_read(reg) for reg in (UC_MIPS_REG_A0,UC_MIPS_REG_A1,UC_MIPS_REG_A2)])
                    if self.native_music:return
                    z.reg_write(UC_MIPS_REG_V0,0);z.reg_write(UC_MIPS_REG_PC,z.reg_read(UC_MIPS_REG_RA));return
                if a==0x80011c40:states.append(Memory(z).byte(GP));return
                if a==0x80057bd4:armed[0]=False;return
                if a==0x80057eb8 and not armed[0]:
                    c=r.contexts[-1];tick=c['tick']+1;c['raws'][tick]=0x800;start_ticks.append(tick);armed[0]=True
            for a in (0x80065100,0x8008eaec,0x80011c40,0x80057bd4,0x80057eb8):self.hooks.append((u,u.hook_add(UC_HOOK_CODE,hook,begin=a,end=a)))
            if not startup_parent:Memory(u).byteset(GP,1)
            u.reg_write(UC_MIPS_REG_SP,0x801ffee0);u.reg_write(UC_MIPS_REG_FP,0x801ffee0)
            u.emu_start(0x80011c80 if startup_parent else 0x80011c30,0x8005d5c4,count=100000000)
            assert u.reg_read(UC_MIPS_REG_PC)==0x8005d5c4 and states==[1,2,5]
            assert u.reg_read(UC_MIPS_REG_RA)==0x80012860
            self.title.append(dict(states=states,navigation=menu.checks,transitions=intro.checks,start_input_ticks=start_ticks,
                                   opening_entry_SP=u.reg_read(UC_MIPS_REG_SP),opening_entry_RA=u.reg_read(UC_MIPS_REG_RA)))
            print('connected title -> opening',which,flush=True)
        assert self.title[0]==self.title[1] and self.music[0]==self.music[1]
        # Reference oracle executes children at the opening function's frame depth.
        v=units[1];v.reg_write(UC_MIPS_REG_SP,v.reg_read(UC_MIPS_REG_SP)-0x38);v.reg_write(UC_MIPS_REG_FP,v.reg_read(UC_MIPS_REG_SP))
    def after_opening(self,units,runners,resources,voices):
        u,v=units
        if self.entry_from_load:
            assert u.reg_read(UC_MIPS_REG_PC)==0x8005cd60 and Memory(u).byte(GP)==Memory(v).byte(GP)==7
        elif self.resume_play:
            assert u.reg_read(UC_MIPS_REG_PC)==0x8005d5a4 and Memory(u).byte(GP)==Memory(v).byte(GP)==7
        else:
            assert u.reg_read(UC_MIPS_REG_PC)==0x80012860 and i32(u.reg_read(UC_MIPS_REG_V0))==0
            assert Memory(u).byte(GP)==Memory(v).byte(GP)==5
        opening_store=bytes(u.mem_read(0x12b2f8,5080));opening_town=bytes(u.mem_read(0x1398f0,24000))
        assert opening_store==bytes(v.mem_read(0x12b2f8,5080)) and opening_store[0]==1
        # Native hiring leaves +1 set; source CPU resumes must retain it.
        assert opening_store[1] in (0,1) if (self.resume_play or self.entry_from_load) else opening_store[1]==0
        opening_clock=get(u,0x800cd93c);opening_cash=get(u,0x800cd9f8)
        if self.snapshot_name:
            root=Path(__file__).resolve().parent/'source'/'opened-snapshots-20261028';root.mkdir(exist_ok=True)
            ram=bytes(u.mem_read(0,0x200000));regs=list(range(UC_MIPS_REG_0,UC_MIPS_REG_31+1))+[UC_MIPS_REG_HI,UC_MIPS_REG_LO,UC_MIPS_REG_PC]
            meta=dict(name=self.snapshot_name,bank=runners[0].buffer,ram_sha256=hashlib.sha256(ram).hexdigest(),
                      registers={str(k):u.reg_read(k) for k in regs},title=self.title[0],
                      voice_registered=voices[0].registered,source_executable_sha256=hashlib.sha256(EXE.read_bytes()).hexdigest(),
                      resource_shadows={hex(a):b.hex() for a,b in resources[0].shadows.items()},
                      resource_assets={hex(a):[b['index'],b['mode']] for a,b in resources[0].buffer_assets.items()},
                      limits=['Snapshot at native opening return12860 after independent opening state/region checks.',
                              'Contains emulator SDK/probe setup; not a hardware emulator save-state.'])
            (root/(self.snapshot_name+'.ram.zlib')).write_bytes(zlib.compress(ram,9))
            (root/(self.snapshot_name+'.json')).write_text(json.dumps(meta,separators=(',',':')))
        print('connected actual opened store -> play',opening_clock,opening_cash,flush=True)
        # Native side resumes the original successful opening epilogue and dispatcher.
        if not self.resume_play:
            if not self.entry_from_load:u.emu_start(0x80012860,0x8005cd60,count=100000)
            assert u.reg_read(UC_MIPS_REG_PC)==0x8005cd60 and Memory(u).byte(GP)==7
            assert u.reg_read(UC_MIPS_REG_RA)==0x80012da8 and bytes(u.mem_read(0x12b2f8,5080))==opening_store
            Memory(v).byteset(GP,7) # Independent wrapper policy for result0, not native-side injection.
            v.reg_write(UC_MIPS_REG_SP,u.reg_read(UC_MIPS_REG_SP)-0x60);v.reg_write(UC_MIPS_REG_FP,v.reg_read(UC_MIPS_REG_SP))
        else:
            v.reg_write(UC_MIPS_REG_SP,u.reg_read(UC_MIPS_REG_SP));v.reg_write(UC_MIPS_REG_FP,u.reg_read(UC_MIPS_REG_FP))
        outer=[[],[]];native_master=[];active=[False];reasons=[];hooks=[]
        calls=dict(CALLS);calls.update({0x80065b3c:4,0x80065100:2})
        step_index=[0];contexts=[]
        def set_action(which,step):
            if self.actions is not None:
                c=contexts[which];c['raws'][c['tick']]=self.actions.get(step,0)
        def observe(z,a,n,d):
            if a==0x8005ce34:set_action(0,step_index[0]);return
            ra=z.reg_read(UC_MIPS_REG_RA)
            if a in calls and 0x8005cd60<=ra<0x8005d5b4:
                outer[0].append([a,[z.reg_read(reg) for reg in (UC_MIPS_REG_A0,UC_MIPS_REG_A1,UC_MIPS_REG_A2,UC_MIPS_REG_A3)[:calls[a]]]])
            if a==0x80023438:
                active[0]=True;runners[0].onreturn(ra,lambda:active.__setitem__(0,False))
            if active[0] and a in ARGS and 0x80023438<=ra<0x80023c20:
                native_master.append([a,[z.reg_read(reg) for reg in (UC_MIPS_REG_A0,UC_MIPS_REG_A1,UC_MIPS_REG_A2)[:ARGS[a]]]])
        for a in set(calls)|set(ARGS)|{0x8005ce34}:hooks.append(u.hook_add(UC_HOOK_CODE,observe,begin=a,end=a))
        for r in runners:
            c=dict(address=0x8005cd60,raws=list(self.raws),tick=0);r.contexts.append(c);contexts.append(c)
        def invoke(a,*args):
            for reg,value in zip((UC_MIPS_REG_A0,UC_MIPS_REG_A1,UC_MIPS_REG_A2,UC_MIPS_REG_A3),args):v.reg_write(reg,value&0xffffffff)
            v.reg_write(UC_MIPS_REG_RA,0x80001000);v.emu_start(a,0x80001000,count=100000000)
            assert v.reg_read(UC_MIPS_REG_PC)==0x80001000,('child stop',hex(a),hex(v.reg_read(UC_MIPS_REG_PC)))
            runners[1].flush(0x80001000);return i32(v.reg_read(UC_MIPS_REG_V0))
        def child(a,*args):
            outer[1].append([a,[x&0xffffffff for x in args]])
            if a==0x80023438:
                reason,trace=master_update(v,invoke);reasons.append(reason)
                assert trace==native_master[-len(trace):],('master calls',trace,native_master[-len(trace):]);return 0
            return invoke(a,*args)
        steps=[];frame_start=len(runners[0].frames);loop_stops=[]
        def loop_stop(z,a,n,d):
            loop_stops.append([step_index[0],a,z.reg_read(UC_MIPS_REG_PC)])
            z.emu_stop()
        hooks.append(u.hook_add(UC_HOOK_CODE,loop_stop,begin=0x8005d5a4,end=0x8005d5a4))
        for step in range(self.iterations):
            step_index[0]=step
            pc=0x8005cd60 if step==0 and not self.resume_play else 0x8005ce34
            u.emu_start(pc,0x80001000,count=100000000)
            assert len(loop_stops)==step+1 and loop_stops[-1][:2]==[step,0x8005d5a4],('native iteration stop',step,hex(u.reg_read(UC_MIPS_REG_PC)),
                'view',get(u,0x800cd97c),'input',get(u,0x800cd884),'contexts',[(hex(q['address']),q['tick'],len(q['raws'])) for q in runners[0].contexts],
                'last calls',[(hex(a),args) for a,args in outer[0][-15:]])
            runners[0].flush(0x8005d5a4)
            if step==0 and not self.resume_play:main_entry(Memory(v),child)
            set_action(1,step)
            child(0x80065974);assert iteration(Memory(v),child)=='next'
            assert outer[0]==outer[1],('outer calls',step,outer[0][-12:],outer[1][-12:])
            assert runners[0].frames==runners[1].frames and runners[0].sounds==runners[1].sounds,('frames/sounds',step)
            assert voices[0].updates==voices[1].updates and voices[0].starts==voices[1].starts,('voices',step)
            assert self.music[0]==self.music[1] and self.volume[0]==self.volume[1]
            hashes=[]
            for a,n in ((0x12b2f8,50800),(0x143ff8,2100),(0xcecec,29480),(0xce608,1764),(0xcd700,0x380),(0x1398f0,24000),(0x137968,8024),(0x1398b0,64),(0xd6270,4),(0xdf0a0,4096),(0xe4410,64),(0xdcc80,9216)):
                actual=bytes(u.mem_read(a,n));expected=bytes(v.mem_read(a,n))
                assert actual==expected,('play memory',step,hex(a),[(hex(a+j),b,c) for j,(b,c) in enumerate(zip(actual,expected)) if b!=c][:4])
                hashes.append([a,n,hashlib.sha256(actual).hexdigest()])
            steps.append(dict(iteration=step,clock=get(u,0x800cd93c),cash=get(u,0x800cd9f8),view=get(u,0x800cd97c),
                              selected=get(u,0x8013796c),processed_input=get(u,0x800cd884),raw_tick=contexts[0]['tick'],pause=get(u,0x800cd7f4),
                              town_cursor=list(struct.unpack('<2h',u.mem_read(0xcda42,4))),town_scale=get(u,0x800cd9a4),
                              active_slots=[j for j in range(10) if u.mem_read(0x12b2f8+j*5080,1)[0]],regions=hashes))
            if step%30==0 or self.actions is not None:print('connected play verified',step+1,'clock',get(u,0x800cd93c),'view',get(u,0x800cd97c),'pause',get(u,0x800cd7f4),'next input',get(u,0x800cd884),flush=True)
            if self.progress_file and (step%30==0 or step+1==self.iterations):
                Path(self.progress_file).write_text(json.dumps(dict(all_passed=False,completed_iterations=step+1,
                    requested_iterations=self.iterations,steps=steps,
                    note='Intermediate per-iteration comparisons only. Final frame/resource/voice completion checks remain pending.'),separators=(',',':')))
            if self.progress_snapshot and (step%30==0 or step+1==self.iterations):
                assert resources[0].loads==resources[1].loads and resources[0].transfers==resources[1].transfers
                assert resources[0].vram==resources[1].vram
                if self.music_bridges:assert self.music_bridges[0].proof()==self.music_bridges[1].proof()
                root=Path(__file__).resolve().parent/'source/opened-snapshots-20261028'
                ram=bytes(u.mem_read(0,0x200000));regs=list(range(UC_MIPS_REG_0,UC_MIPS_REG_31+1))+[UC_MIPS_REG_HI,UC_MIPS_REG_LO,UC_MIPS_REG_PC]
                meta=dict(name=self.progress_snapshot,phase='play_iteration_end',completed_iterations=self.completed_before+step+1,
                          parent_snapshot_sha256=self.parent_snapshot_sha256,bank=runners[0].buffer,ram_sha256=hashlib.sha256(ram).hexdigest(),
                          registers={str(k):u.reg_read(k) for k in regs},title=self.title[0],voice_registered=voices[0].registered,
                          source_executable_sha256=hashlib.sha256(EXE.read_bytes()).hexdigest(),
                          resource_shadows={hex(a):b.hex() for a,b in resources[0].shadows.items()},
                          resource_assets={hex(a):[b['index'],b['mode']] for a,b in resources[0].buffer_assets.items()},
                          verified_steps=steps,limits=['Source CPU RAM/register snapshot after paired independent parent/frame/voice/resource comparisons.',
                                                      'Intermediate checkpoint, not proof of completion of the requested longer trajectory.',
                                                      'Past physical VRAM/audio and SDK timing are not restored. Only CPU state and known resource shadows are restored.'])
                (root/(self.progress_snapshot+'.ram.zlib')).write_bytes(zlib.compress(ram,9))
                (root/(self.progress_snapshot+'.json')).write_text(json.dumps(meta,separators=(',',':')))
        assert resources[0].loads==resources[1].loads and resources[0].transfers==resources[1].transfers and resources[0].vram==resources[1].vram
        for r,c in zip(runners,contexts):assert r.contexts[-1] is c;r.contexts.pop()
        for h in hooks:u.hook_del(h)
        music_proof=None
        if self.music_bridges:
            music_proof=self.music_bridges[0].proof()
            assert music_proof==self.music_bridges[1].proof()
            for bridge in self.music_bridges:bridge.dispose()
        for m in self.monitors:m.dispose()
        for z,h in self.hooks:z.hook_del(h)
        return dict(title=self.title[0],opening_store_sha256=hashlib.sha256(opening_store).hexdigest(),
                    opening_town_sha256=hashlib.sha256(opening_town).hexdigest(),opening_clock=opening_clock,opening_cash=opening_cash,
                    state_sequence=[7] if self.resume_play else [1,2,6,7] if self.entry_from_load else [1,2,5,7],mainplay_RA=hex(0x80012da8),steps=steps,outer_calls=outer[0],master_calls=native_master,native_loop_stop_observations=loop_stops,
                    completed_before=self.completed_before,resumed_play=self.resume_play,
                    master_reasons=reasons,play_frames=len(runners[0].frames)-frame_start,music_requests=self.music[0],volume_requests=self.volume[0],
                    actions=self.actions,native_music=music_proof,final_resource_vram_sha256=hashlib.sha256(resources[0].vram).hexdigest())
