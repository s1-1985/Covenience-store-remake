"""Native title ->51174 confirmation ->51524 checksum ->128B4 decode/rebuild.

The payload is produced by original6B81C from the verified opened town. Card
initialization/read endpoints supply that payload; no physical card is modeled.
"""
from opened_snapshot_harness_20261029 import *
from title_flow_20261028 import TitleMenuMonitor,GP
from title_intro_monitor_20261028 import TitleIntroMonitor
from title_load_control import title_load
from save_codec import BASE,SIZE,encode,valid,FIELDS,checksum,CHECKSUM_OFFSET
from verify_schedule_selector_frames import seq
from unicorn import UC_HOOK_CODE
from recovered import i32
from load_confirmation_20261029 import LoadConfirmationMonitor
from load_read_control_20261030 import LoadReadMonitor
DIRECT={0x8005c79c:0,0x80065974:0,0x80018a5c:0,0x80018940:2,0x8004ea68:0,0x80013448:0,
        0x80051174:1,0x8006bc40:0,0x8005c61c:0,0x800140e8:2,0x80013eac:5,0x80065b3c:4,
        0x8006653c:0,0x80023c20:0,0x8002619c:0,0x80041a08:0}
def payload(name):
    root=R/'source/opened-snapshots-20261028';ram=zlib.decompress((root/(name+'.ram.zlib')).read_bytes())
    u=machine();u.mem_write(0,ram);m=Memory(u)
    wanted=bytes(encode(bytearray(m.read(BASE,SIZE)),m.read))
    u.reg_write(UC_MIPS_REG_SP,0x801ffee0);u.reg_write(UC_MIPS_REG_FP,0x801ffee0);u.reg_write(UC_MIPS_REG_RA,0x80001000)
    u.emu_start(0x8006b81c,0x80001000,count=15000000)
    assert u.reg_read(UC_MIPS_REG_PC)==0x80001000 and m.read(BASE,SIZE)==wanted and valid(wanted)
    return wanted
def compare(scenario='cancel',name='TOWN0001-music',supplied_payload=None,audit_runtime_tables=False):
    assert scenario in ('success','cancel','bad_checksum','saved_minus_one','presentation_saved','right_cancel','read_error','init_retry','confirm_cancel','left_right_confirm','right_left',*(f'init_error_{i}' for i in range(1,6)))
    success_path=scenario in ('success','confirm_cancel','left_right_confirm','right_left','init_retry')
    init_status=int(scenario.rsplit('_',1)[1]) if scenario.startswith('init_error_') else 1 if scenario=='init_retry' else 0
    read_status=1 if scenario=='read_error' else 0
    if supplied_payload is not None:
        assert scenario=='presentation_saved' and valid(supplied_payload) and supplied_payload[2]==255
        supplied=bytes(supplied_payload)
    else:supplied=payload(name)
    presentation_proof=None
    if scenario=='presentation_saved' and supplied_payload is None:
        from presentation_save_payload_20261030 import make
        supplied,presentation_proof=make(name,native_prompt=True)
    flagged_save=scenario in ('saved_minus_one','presentation_saved')
    if scenario=='saved_minus_one':
        b=bytearray(supplied);b[2]=255;struct.pack_into('<I',b,CHECKSUM_OFFSET,checksum(b));supplied=bytes(b);assert valid(supplied)
    if scenario=='bad_checksum':
        b=bytearray(supplied);b[0x3c]^=1;supplied=bytes(b);assert not valid(supplied)
    plans={0x80057bd4:[[0]*2000],0x80059254:[seq([0x4000,32])+[0]*100],
           0x80051174:[seq([64] if scenario=='cancel' else [0x2000,32] if scenario=='right_cancel' else [0x60] if scenario=='confirm_cancel' else [0xa020] if scenario=='left_right_confirm' else [0x2000,0x8000,32] if scenario=='right_left' else [32,32] if scenario=='init_retry' else [32,64])+[0]*200],
           0x80051524:[[0]*300 for _ in range(2)],0x80065690:[[0]*200 for _ in range(30)],
           0x800656f8:[seq([32])+[0]*200 for _ in range(30)]}
    units=[restore(name,plans) for _ in range(2)];hooks=[];traces=[[],[]];cards=[[],[]];states=[[],[]];monitors=[];confirmations=[];messages=[[],[]];read_monitors=[]
    def runtime_tables(z):
        m=Memory(z)
        return b''.join(m.read(0x8009ce14+j*88,48) for j in range(27)),m.read(0x8009c7a0,101*16)
    runtime_before=[runtime_tables(unit[0]) for unit in units] if audit_runtime_tables else None
    for which,(u,r,res,voice,music,menu,meta) in enumerate(units):
        m=Memory(u);m.byteset(GP,1)
        monitor=TitleMenuMonitor(u,r);intro=TitleIntroMonitor(u,r);monitors.extend([monitor,intro]);armed=[False];attempt_count=[0]
        read_monitor=LoadReadMonitor(u,r,[1,0] if scenario=='init_retry' else init_status,read_status,valid(supplied));read_monitors.append(read_monitor);monitors.append(read_monitor)
        confirmation=LoadConfirmationMonitor(u,r);confirmations.append(confirmation);monitors.append(confirmation)
        def observe(z,a,n,d,which=which,r=r,m=m,armed=armed,attempt_count=attempt_count):
            if a==0x80011c40:states[which].append(m.byte(GP));return
            if a==0x80057eb8:
                if not armed[0]:
                    c=r.contexts[-1];c['raws'][c['tick']+1]=0x800;armed[0]=True
                return
            if a==0x80051524:
                attempt_count[0]+=1;return
            if a in (0x8007b1f8,0x8007ab2c):
                arg=z.reg_read(UC_MIPS_REG_A0);cards[which].append([a,arg]);m.byteset(0x800cd820,(0 if scenario=='init_retry' and attempt_count[0]>1 else init_status) if a==0x8007b1f8 else read_status)
                if a==0x8007ab2c and arg==1 and not read_status:m.write(BASE,supplied)
                z.reg_write(UC_MIPS_REG_V0,0);z.reg_write(UC_MIPS_REG_PC,z.reg_read(UC_MIPS_REG_RA));return
            if a==0x8005188c:
                assert m.read(BASE,SIZE)==supplied
                r.onreturn(z.reg_read(UC_MIPS_REG_RA),lambda: cards[which].append(['checksum',z.reg_read(UC_MIPS_REG_V0)]));return
            if a==0x80051838:
                c=r.contexts[-1]
                if not c.get('ack_armed'):
                    assert c['address']==0x80051524
                    c['raws'][c['tick']:c['tick']+3]=[0,64,0];c['ack_armed']=True
                return
            ra=z.reg_read(UC_MIPS_REG_RA)
            if a==0x8004e494 and 0x80050fc8<=ra<0x8005188c:
                messages[which].append(z.reg_read(UC_MIPS_REG_A2));return
            if which==0 and 0x800128b4<=ra<0x80012d78:
                args=[z.reg_read(reg) for reg in (UC_MIPS_REG_A0,UC_MIPS_REG_A1,UC_MIPS_REG_A2,UC_MIPS_REG_A3)[:DIRECT[a]]]
                if DIRECT[a]==5:args.append(m.word(z.reg_read(UC_MIPS_REG_SP)+16))
                traces[0].append([a,args])
        for a in (0x80011c40,0x80057eb8,0x8007b1f8,0x8007ab2c,0x8005188c,0x80051838,0x8004e494,0x80051524,*DIRECT):hooks.append((u,u.hook_add(UC_HOOK_CODE,observe,begin=a,end=a)))
        u.reg_write(UC_MIPS_REG_SP,0x801ffee0);u.reg_write(UC_MIPS_REG_FP,0x801ffee0)
        u.emu_start(0x80011c30,0x800128b4,count=100000000)
        assert u.reg_read(UC_MIPS_REG_PC)==0x800128b4 and states[which]==[1,2,6]
        print('native title -> load',scenario,which,flush=True)
    u,r=units[0][:2];v,rr=units[1][:2];return_pc=u.reg_read(UC_MIPS_REG_RA)
    v.reg_write(UC_MIPS_REG_SP,u.reg_read(UC_MIPS_REG_SP)-0x30);v.reg_write(UC_MIPS_REG_FP,v.reg_read(UC_MIPS_REG_SP))
    try:u.emu_start(0x800128b4,return_pc,count=150000000)
    except Exception:
        print('load diagnostic',hex(u.reg_read(UC_MIPS_REG_PC)),[(hex(c['address']),c['tick']) for c in r.contexts],cards[0],flush=True);raise
    assert u.reg_read(UC_MIPS_REG_PC)==return_pc,('native load stop',scenario,hex(u.reg_read(UC_MIPS_REG_PC)),r.phase_entries,[(hex(c['address']),c['tick']) for c in r.contexts])
    r.flush(return_pc)
    def invoke(a,*args,record=True):
        if record:traces[1].append([a,[x&0xffffffff for x in args]])
        for reg,value in zip((UC_MIPS_REG_A0,UC_MIPS_REG_A1,UC_MIPS_REG_A2,UC_MIPS_REG_A3),args):v.reg_write(reg,value&0xffffffff)
        for j,value in enumerate(args[4:]):put(v,v.reg_read(UC_MIPS_REG_SP)+16+j*4,value)
        v.reg_write(UC_MIPS_REG_RA,0x80001000);v.emu_start(a,0x80001000,count=100000000)
        assert v.reg_read(UC_MIPS_REG_PC)==0x80001000,('reference child stop',hex(a),hex(v.reg_read(UC_MIPS_REG_PC)))
        rr.flush(0x80001000);return i32(v.reg_read(UC_MIPS_REG_V0))
    def rect(index):
        invoke(0x80013f7c,index,0x801fff40,0x801fff48,record=False)
        return struct.unpack('<4I',Memory(v).read(0x801fff40,16))
    branch=title_load(Memory(v).read,Memory(v).write,invoke,rect)
    assert traces[0]==traces[1],('load parent calls',traces)
    assert r.frames==rr.frames and r.sounds==rr.sounds
    assert cards[0]==cards[1]
    assert read_monitors[0].checks==read_monitors[1].checks
    assert confirmations[0].checks==confirmations[1].checks and confirmations[0].inputs==confirmations[1].inputs
    expected_cards=[] if scenario in ('cancel','right_cancel') else [[0x8007b1f8,1]] if init_status else [[0x8007b1f8,1],[0x8007ab2c,0],[0x8007ab2c,1]]
    if expected_cards and not (init_status or read_status):expected_cards.append(['checksum',0 if (success_path or flagged_save) else 0xffffffff])
    if scenario=='init_retry':expected_cards=[[0x8007b1f8,1],[0x8007b1f8,1],[0x8007ab2c,0],[0x8007ab2c,1],['checksum',0]]
    assert cards[0]==expected_cards,('card branches',cards[0],expected_cards)
    assert messages[0]==messages[1]
    if init_status or read_status:
        expected_message={1:0x1e0,2:0x1e1,3:0x1f5,4:0x1dd,5:0x1df}.get(init_status,0x1ec)
        assert expected_message in messages[0],('error message',messages[0])
        attempts=[p['attempt'] for p in confirmations[0].checks if p['action']=='attempt']
        assert attempts==([1,0] if scenario=='init_retry' else [init_status if init_status else -1]),attempts
    hashes=[]
    for a,n in ((0x12b2f8,50800),(0x143ff8,2100),(0xcecec,29480),(0xce608,1764),(0xcd700,0x380),(0x1398f0,24000),
                (0x137968,8024),(0x1398b0,64),(0xd6270,4),(0xdf0a0,4096),(0xe4410,64),(0xdcc80,9216),(0xdb2e0,182*36)):
        x=Memory(u).read(a,n);y=Memory(v).read(a,n);assert x==y,('load memory',hex(a),[(hex(a+j),b,c) for j,(b,c) in enumerate(zip(x,y)) if b!=c][:4])
        hashes.append([a,n,hashlib.sha256(x).hexdigest()])
    assert Memory(u).byte(GP)==Memory(v).byte(GP)==(7 if success_path else 2)
    assert branch==('resume' if success_path else 'saved_minus_one' if flagged_save else 'load_nonzero')
    for pos in (2,3,4,5):
        first=units[0][pos];second=units[1][pos]
        if pos==2:assert first.loads==second.loads and first.transfers==second.transfers and first.vram==second.vram
        if pos==3:assert first.starts==second.starts and first.updates==second.updates
        if pos==4:assert first.proof()==second.proof()
        if pos==5:assert first.checks==second.checks
    load_state=Memory(u).byte(GP);play=None;return_to_title=None
    if success_path:
        from title_opening_play_connection_20261028 import Connection
        u.emu_start(return_pc,0x8005cd60,count=100000)
        assert u.reg_read(UC_MIPS_REG_PC)==0x8005cd60 and states[0]==[1,2,6,7]
        c=Connection(iterations=4,native_music=True);c.entry_from_load=True
        c.title=[dict(states=[1,2,6]),dict(states=[1,2,6])];c.music_bridges=[unit[4] for unit in units]
        play=c.after_opening((u,v),[unit[1] for unit in units],[unit[2] for unit in units],[unit[3] for unit in units])
    else:
        # Original dispatcher return and next title resource load, on native side.
        # The paired parent comparison above ends at128B4's return.
        start=len(units[0][2].loads)
        stop=u.hook_add(UC_HOOK_CODE,lambda z,a,n,d:z.emu_stop(),begin=0x80012778,end=0x80012778)
        u.emu_start(return_pc,0x80012778,count=10000000);u.hook_del(stop)
        assert u.reg_read(UC_MIPS_REG_PC)==0x80012778 and states[0]==[1,2,6,2]
        reloaded=units[0][2].loads[start:];assert [q[0] for q in reloaded]==[[10,0],[11,0],[1,6],[0,5]]
        return_to_title=dict(state=Memory(u).byte(GP),stop_pc=hex(0x80012778),reloaded=reloaded)
    out=dict(scenario=scenario,snapshot=name,payload_sha256=hashlib.sha256(supplied).hexdigest(),payload_valid=valid(supplied),
             branch=branch,presentation_proof=presentation_proof,state=load_state,title_states=states[0],calls=traces[0],card_calls=cards[0],regions=hashes,
             resumed_play=play,return_to_title=return_to_title,
             frames=r.frames,error_fixture=dict(init_status=init_status,read_status=read_status),message_ids=messages[0],load_read_checks=read_monitors[0].checks,confirmation_checks=confirmations[0].checks,confirmation_inputs=confirmations[0].inputs,
             resource_loads=units[0][2].loads,transfers=units[0][2].transfers,native_music=units[0][4].proof(),
             limits=['Entry CPU state derives from actual opened source town; title entry state1 is an explicit fixture, not an original game-exit path.',
                     'Native title/51174/51524/5188C/128B4, original payload encode/decode, resources and CPU rendering run; parent128B4 independently modeled.',
                     'Card7B1F8/7AB2C endpoints supply completion and original-encoded payload; card file headers and physical transport not modeled.',
                     'Independent control/bytes/frame models share original child functions. Physical GPU/SPU/IRQ remain outside coverage.'])
    if audit_runtime_tables:
        after=[runtime_tables(unit[0]) for unit in units]
        assert after==runtime_before and after[0]==after[1],('title/load runtime table conversion',name)
        out['runtime_tables_preserved_after_resume']=dict(products27x12_sha256=hashlib.sha256(after[0][0]).hexdigest(),appearance101x4_sha256=hashlib.sha256(after[0][1]).hexdigest(),both_cpus=True)
    if flagged_save:
        if supplied_payload is not None:
            out['external_payload_supplied']=True
            out['limits'].append('Exact externally suppliedFF payload from a separately recorded original encode trajectory; this title test does not generate/rewrite it. The linked producer proof establishes its controlled provenance; not natural scenario completion.')
        else:out['limits'].append('FF saved flag is a controlled branch fixture, not a natural full scenario completion. presentation_saved obtains it from original6DAF0/66FCC raw-input confirmation, post-confirmation continuation and original encoder; saved_minus_one edits payload and recomputes checksum.')
    for z,h in hooks:z.hook_del(h)
    for mon in monitors:mon.dispose()
    for unit in units:
        for item in unit[2:6]:item.dispose()
        unit[1].dispose()
    return out
if __name__=='__main__':
    import sys
    scenario=sys.argv[1] if len(sys.argv)>1 else 'cancel'
    row=compare(scenario)
    out=dict(total=1,all_passed=True,frames_verified=len(row['frames']),cases=[row],limits=row['limits'])
    (R/f'title-native-load-{scenario}-verification-20261029.json').write_text(json.dumps(out,separators=(',',':')))
    print('native title load passed',scenario,len(row['frames']),flush=True)
