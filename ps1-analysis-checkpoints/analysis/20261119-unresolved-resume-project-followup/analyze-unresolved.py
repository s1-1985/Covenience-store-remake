#!/usr/bin/env python3
"""R02/R05 only: resume logic body and two further project-sound contexts.
Controlled source inputs, not a natural playthrough. No gameplay callee patches.
"""
import argparse,hashlib,importlib.util,json,struct,zipfile
from pathlib import Path
from unicorn import UC_HOOK_CODE,UC_HOOK_MEM_WRITE
from unicorn.mips_const import *
ROOT=Path(__file__).resolve().parent
HELPER=ROOT.parent/'20261118-festival-load-order/analyze-load-order.py'
spec=importlib.util.spec_from_file_location('prior_load',HELPER);L=importlib.util.module_from_spec(spec);spec.loader.exec_module(L);P=L.P
S=P.S;TARGET=S+2*5080+0xf04;QUEUE=0x137970;PROJECT=0xe3c00;ALIAS=(P.SP-36)&0x1fffffff
ENTRIES=[]
def sha(b):return hashlib.sha256(b).hexdigest()
def out(n,v):(ROOT/n).write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n')
def rd(u,a,n):return bytes(u.mem_read(a&0x1fffffff,n))
def signed(u,a):return struct.unpack('<i',rd(u,a,4))[0]
def call(u,a):
    P.call(u,a);ENTRIES.append({'entry':hex(a),'kind':'whole_function'})
def chunk(u,a,b,frame=None):
    if frame is None:L.chunk(u,a,b)
    else:
        for r,v in [(UC_MIPS_REG_SP,frame),(UC_MIPS_REG_FP,frame),(UC_MIPS_REG_RA,P.STOP)]:u.reg_write(r,v)
        h=u.hook_add(UC_HOOK_CODE,lambda uc,pc,n,c:uc.emu_stop(),begin=b,end=b)
        u.emu_start(a,P.STOP,count=30000000);u.hook_del(h)
        assert u.reg_read(UC_MIPS_REG_PC)==b,(hex(a),hex(u.reg_read(UC_MIPS_REG_PC)))
    ENTRIES.append({'entry':hex(a),'end':hex(b),'kind':'selected_original_block'})
def actor(u):
    b=rd(u,TARGET,32)
    return {'raw_hex':b.hex(),'state':b[0],'profile':struct.unpack_from('<h',b,2)[0],'quantity':b[30],'wanted':b[1],'wallet':struct.unpack_from('<h',b,8)[0],'deadline':struct.unpack_from('<I',b,4)[0],'position':list(struct.unpack_from('<3b',b,12)),'goal':list(struct.unpack_from('<3b',b,15)),'route_hex':b[18:28].hex(),'visitors':signed(u,S+2*5080+0x1188),'summary_present':signed(u,0xce65c+2*168+20),'clock':signed(u,0xcd93c),'festival':signed(u,0xcda00),'rebuild':rd(u,0x1398bc,1)[0]}
def queue(u):
    rows=[]
    for i in range(50):
        b=rd(u,QUEUE+160*i,160)
        if b[0]:rows.append({'slot':i,'mode':b[2],'kind':struct.unpack_from('<i',b,132)[0],'sound':struct.unpack_from('<i',b,140)[0]})
    return rows

def logic_tick(u):
    # Advance clock with original prologue and retain its actual stack frame.
    # Only the HUD/GPU record producer at23464 is excluded from this update.
    before=actor(u);chunk(u,0x80023438,0x80023460);writes=[];calls=[]
    checkpoints={0x8002346c,0x80023474,0x80023490,0x80023498,0x800234a0,0x800234a8,0x800234b0,0x800234e8,0x800234f0}
    def code(uc,pc,n,ctx):
        if pc in checkpoints:calls.append(hex(pc))
    def memory(uc,access,a,n,v,ctx):
        a&=0x1fffffff
        if a<TARGET+32 and a+n>TARGET:writes.append({'pc':hex(uc.reg_read(UC_MIPS_REG_PC)),'offset':a-TARGET,'bytes':n,'value':v&((1<<(8*n))-1)})
    h=u.hook_add(UC_HOOK_CODE,code);m=u.hook_add(UC_HOOK_MEM_WRITE,memory)
    u.emu_start(0x8002346c,P.STOP,count=10000000);u.hook_del(h);u.hook_del(m)
    assert u.reg_read(UC_MIPS_REG_PC)==P.STOP,hex(u.reg_read(UC_MIPS_REG_PC))
    ENTRIES.append({'entry':'0x8002346c','kind':'logic_body_to_original_function_return','excluded':'HUD23464'})
    return {'before':before,'after':actor(u),'body_checkpoints':calls,'customer_writes':writes}

def reserve(u,mode):
    # Source-supported mode; sound -1 suppresses device playback explicitly.
    u.mem_write(0xe4020,b'\xff\x40'+bytes(118));P.put(u,P.SP+16,0)
    for r,v in [(UC_MIPS_REG_A0,0),(UC_MIPS_REG_A1,0),(UC_MIPS_REG_A2,0xffffffff),(UC_MIPS_REG_A3,mode)]:u.reg_write(r,v)
    call(u,0x8003ecd8)
def pending(u):
    b=bytearray(rd(u,PROJECT,32));struct.pack_into('<h',b,0,0);struct.pack_into('<4i',b,4,10,10,11,11);struct.pack_into('<H',b,20,1);u.mem_write(PROJECT,bytes(b));assert b[30:32]==bytes(2)
def project_prefix(u):
    writes=[];notices=[]
    def memory(uc,access,a,n,v,ctx):
        a&=0x1fffffff
        if a<ALIAS+4 and a+n>ALIAS:writes.append({'pc':hex(uc.reg_read(UC_MIPS_REG_PC)),'bytes':n,'value':v&0xffffffff})
    def code(uc,pc,n,ctx):
        if pc==0x800292ec:notices.append({'kind':uc.reg_read(UC_MIPS_REG_A0),'event':uc.reg_read(UC_MIPS_REG_A1),'sound':uc.reg_read(UC_MIPS_REG_A2),'mode':uc.reg_read(UC_MIPS_REG_A3)})
    h=u.hook_add(UC_HOOK_MEM_WRITE,memory);m=u.hook_add(UC_HOOK_CODE,code)
    chunk(u,0x8002346c,0x800234a0);u.hook_del(h);u.hook_del(m)
    return {'alias_writes':writes,'comparison_value':signed(u,ALIAS),'notices':notices,'notice_active':signed(u,0x1398b4),'project_after':rd(u,PROJECT,32).hex(),'queue_after':queue(u)}

def main(archive):
    z=zipfile.ZipFile(archive);exe=z.read('algorithm-analysis/source/SLPS_007.82');town=z.read('algorithm-analysis/source/TOWN0001.BIN');msg=z.read('algorithm-analysis/source/MSG00.OBJ');assert sha(exe)==P.EXE_SHA
    # Existing bootstrap helper: fixture conversion, verified CD-provided town,
    # metrics. Its three original entries are counted as bootstrap, not new tests.
    base,_=P.fixture(exe,town)
    ENTRIES.extend([{'entry':hex(pc),'kind':'existing_bootstrap'} for pc in [0x8005c858,0x8001a0b8,0x80023c20]])
    u=P.machine(exe,base)
    for j in [1,2]:P.put(u,S+5080*j+0xc78,0)
    P.put(u,0xcd93c,44640);call(u,0x80023c20);P.put(u,0xcda00,1);P.put(u,0xd6270,2)
    call(u,0x8006b81c);payload=rd(u,0x187e00,0x197ac);assert sum(payload[:0x197a8])&0xffffffff==struct.unpack_from('<I',payload,0x197a8)[0]
    encoded=rd(u,0,0x200000);resume=[]
    for route in ['title','ingame_accepted']:
        u=P.machine(exe,encoded);call(u,0x8006bc40);decoded=actor(u);assert decoded['state']==0
        if route=='title':
            chunk(u,0x80012d44,0x80012d68);chunk(u,0x8005cd60,0x8005cdcc)
        else:
            chunk(u,0x800624d0,0x80062588,P.SP-0x28);chunk(u,0x80062598,0x800625b4,P.SP-0x28)
        reconstructed=actor(u);steps=[]
        for i in range(2 if route=='title' else 1):steps.append(logic_tick(u))
        if route=='title':
            assert reconstructed['state']==1 and steps[0]['after']['state']==1
            assert steps[1]['after']['state']==2 and steps[1]['after']['quantity']==0 and steps[1]['after']['wallet']==500
            assert steps[1]['after']['clock']==44644 and steps[1]['after']['deadline']==44764
        else:assert reconstructed['state']==0
        assert not any(w['pc']=='0x80026868' for step in steps for w in step['customer_writes'])
        resume.append({'route':route,'decoded':decoded,'after_reconstruction':reconstructed,'logic_updates':steps})
    # R05 uses the same source town plus original reserved land. Pending project
    # and queue are explicit diagnostics, not claimed original UI reachability.
    u=P.machine(exe,base);u.mem_write(0x183e00,msg);u.mem_write(0x12b2c8,b'\xff\x40'+bytes(38))
    for y in [10,11]:
        for x in [10,11]:
            for r,v in [(UC_MIPS_REG_A0,x),(UC_MIPS_REG_A1,y),(UC_MIPS_REG_A2,71),(UC_MIPS_REG_A3,0)]:u.reg_write(r,v)
            call(u,0x8001f1c0)
    project_base=rd(u,0,0x200000);projects=[]
    for active in [False,True]:
        u=P.machine(exe,project_base);reserve(u,2)
        if active:P.put(u,0x1398b4,1)
        before_queue=queue(u);pending(u);case=project_prefix(u)
        assert case['comparison_value']==20 and case['notices']==[{'kind':2,'event':0,'sound':29,'mode':1}]
        assert all(w['pc']=='0x80023f30' for w in case['alias_writes'])
        projects.append({'case':'monthly_already_active' if active else 'monthly_pending','before_queue':before_queue,**case})
    # Advance the R05 negative-value frontier: previous-year revenue is produced
    # by original finance from strictly positive monthly ledger input.
    u=P.machine(exe,project_base);own=S+5080
    for j in range(2,10):u.mem_write(S+5080*j,b'\0')
    u.mem_write(own+4,struct.pack('<H',1));P.put(u,0xcd93c,69120);call(u,0x80023c20)
    P.put(u,own+0xd38,299000000);P.put(u,own+0xd48,300000000);P.put(u,0xcd9f8,100000000);P.put(u,0xcd8b8,0)
    call(u,0x80029334)
    finance={'input_month_expense':299000000,'input_month_revenue':300000000,'year_revenue_after':signed(u,own+0xd0c),'net_history_after':signed(u,own+0x12e8),'cash_after':signed(u,0xcd9f8),'ending_flag':rd(u,0xcd948,1)[0],'calendar':[signed(u,0xce608+4*i) for i in range(5)]}
    assert finance['year_revenue_after']==-1894967296 and finance['net_history_after']>0 and finance['cash_after']>0 and finance['ending_flag']==0
    # Explicitly isolate annual consumption and suppress requested audio.
    for j in range(50):u.mem_write(QUEUE+j*160,b'\0')
    P.put(u,0x1398b4,0);reserve(u,3);pending(u);overflow=project_prefix(u)
    assert overflow['comparison_value']==finance['year_revenue_after'] and overflow['notices'][0]['sound']==34
    projects.append({'case':'positive_monthly_finance_overflow','finance':finance,'explicit_setup':['own store flags1, other stores inactive','positive monthly ledger values injected','queue active bytes cleared; annual mode3 reserved with sound-1','pending police box injected; record+30 stays original0'],**overflow})
    out('results.json',{'tracked_targets':['R02','R05'],'resume':resume,'projects':projects,'payload_sha256':sha(payload),'original_entry_log':ENTRIES,'original_entries_in_final_reproducer':len(ENTRIES),'operating_logic_body_updates':3,'whole_hud_inclusive_updates':0,'gameplay_callee_replacements':0,'resource_loader_substitutions':1,'ordinary_UI_reachability_established':False,'scope':'Five final cases only; exploratory runs preceded this reproducible run. No source first-customer or route bytes were directly patched. Initial schedules/calendar/flag/seed and finance inputs are diagnostic.'})
    spans=[('main_clock',0x80023438,0x8002346c),('main_logic_calls',0x8002346c,0x80023504),('main_logic_return',0x80023bd8,0x80023c20),('entry_state_initialization',0x800329bc,0x80032ab8),('monthly_notification_branch',0x8003f644,0x8003f7fc),('annual_alias_sum',0x8003f7fc,0x8003f968),('monthly_scale',0x80029918,0x80029dfc)]
    proof=[]
    for name,a,b in spans:
        raw=exe[a-0x80010000+2048:b-0x80010000+2048];proof.append({'name':name,'start':hex(a),'end_exclusive':hex(b),'sha256':sha(raw),'hex':raw.hex()})
    out('source-provenance.json',{'exe_sha256':sha(exe),'archive_sha256':sha(archive.read_bytes()),'town_sha256':sha(town),'msg_sha256':sha(msg),'helper':str(HELPER.relative_to(ROOT.parent)),'helper_sha256':sha(HELPER.read_bytes()),'ranges':proof,'known_before':['title versus accepted in-game reconstruction order','isolated zero-headcount entry and checkout outcomes','R05 annual alias writes and negative diagnostic sound34'],'new_scope':['actual first and second resumed logic bodies, HUD excluded','monthly mode2 and already-active notice preceding project completion','positive monthly ledger -> original finance overflow -> annual comparison negative -> sound34']})
    print(json.dumps({'resume_states':[[s['after']['state'] for s in r['logic_updates']] for r in resume],'logic_body_updates':3,'project_sounds':[p['notices'][0]['sound'] for p in projects],'finance_year_revenue':finance['year_revenue_after'],'entries':len(ENTRIES),'fully_resolved_tracked_issues':0}))
if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('archive',type=Path);main(ap.parse_args().archive)
