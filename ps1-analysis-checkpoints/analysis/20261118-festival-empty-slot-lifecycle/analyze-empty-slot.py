#!/usr/bin/env python3
"""Three R02 followups: phantom entry, admission accounting, stale destination.
Original post-spawn code, not a full operating update/natural festival replay.
"""
import argparse,hashlib,importlib.util,json,struct,zipfile
from pathlib import Path
from unicorn import UC_HOOK_CODE,UC_HOOK_MEM_WRITE
from unicorn.mips_const import *
ROOT=Path(__file__).resolve().parent
HELPER=ROOT.parent/'20261117-festival-customer-state-data/analyze-festival-state.py'
spec=importlib.util.spec_from_file_location('prior_festival',HELPER);P=importlib.util.module_from_spec(spec);spec.loader.exec_module(P)
S=P.S+2*5080;SUMMARY=0xce65c+2*168;META=0xcecec+2*2948

def sha(b):return hashlib.sha256(b).hexdigest()
def save(n,v):(ROOT/n).write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n')
def rd(u,a,n):return bytes(u.mem_read(a&0x1fffffff,n))
def view(u):
 b=rd(u,S+0xf04,32);return dict(raw_hex=b.hex(),state=b[0],wanted=b[1],profile=struct.unpack_from('<h',b,2)[0],deadline=struct.unpack_from('<I',b,4)[0],wallet=struct.unpack_from('<h',b,8)[0],cart_unit_value=struct.unpack_from('<h',b,10)[0],position=list(struct.unpack_from('<3b',b,12)),goal=list(struct.unpack_from('<3b',b,15)),route_hex=b[18:28].hex(),quantity=b[30],appearance=b[31],visitors=P.get(u,S+0x1188),summary_present=P.get(u,SUMMARY+20),cash=[P.get(u,0xcd9f8),P.get(u,0xcd9fc)],dirty_flag=rd(u,S+1,1)[0])
def enter(u,pc,end,frame,args=()):
 for r,v in [(UC_MIPS_REG_SP,frame),(UC_MIPS_REG_FP,frame),(UC_MIPS_REG_RA,P.STOP)]:u.reg_write(r,v)
 for r,v in zip((UC_MIPS_REG_A0,UC_MIPS_REG_A1,UC_MIPS_REG_A2,UC_MIPS_REG_A3),args):u.reg_write(r,v)
 h=u.hook_add(UC_HOOK_CODE,lambda uc,a,n,c:uc.emu_stop(),begin=end,end=end)
 u.emu_start(pc,P.STOP,count=3000000);u.hook_del(h);assert u.reg_read(UC_MIPS_REG_PC)==end,(hex(pc),hex(u.reg_read(UC_MIPS_REG_PC)))
def main():
 ap=argparse.ArgumentParser();ap.add_argument('archive',type=Path);a=ap.parse_args()
 expected=json.loads((ROOT.parent.parent/'archives/20261103-r2/manifest.json').read_text())['sha256'];assert sha(a.archive.read_bytes())==expected
 with zipfile.ZipFile(a.archive) as z:exe=z.read('algorithm-analysis/source/SLPS_007.82');town=z.read('algorithm-analysis/source/TOWN0001.BIN')
 assert sha(exe)==P.EXE_SHA
 baseline,initial=P.fixture(exe,town);u=P.machine(exe,baseline)
 # Reuse established controlled schedule/festival preconditions; no new reachability claim.
 for j in [1,2]:P.put(u,P.S+5080*j+0xc78,0)
 P.call(u,0x80023c20)
 for addr,v in [(0xce60c,8),(0xce610,4),(0xce614,0),(0xce618,0),(0xcda00,1),(0xd6270,2)]:P.put(u,addr,v)
 initial_view=view(u);assert rd(u,S+0xf04,32)==bytes(32)
 alias_writes=[]
 def alias(uc,access,addr,size,value,data):
  addr&=0x1fffffff
  if addr<S+0xf06 and addr+size>S+0xf04:alias_writes.append(dict(pc=hex(uc.reg_read(UC_MIPS_REG_PC)),size=size,value=value&65535))
 h=u.hook_add(UC_HOOK_MEM_WRITE,alias);P.call(u,0x8002619c);u.hook_del(h)
 after_demand=view(u);assert alias_writes==[dict(pc='0x80026868',size=2,value=1)] and after_demand['state']==1
 P.put(u,0xcd8ec,2)
 # Main's preparation needs the rebuild flag when starting from newly loaded town RAM.
 u.mem_write(0x1398bc,b'\1');frame=P.SP-0x40;P.put(u,frame+0x24,S+0x80000000);P.put(u,frame+0x18,0)
 enter(u,0x80023670,0x800238ac,frame)
 assert rd(u,S+0xc77,1)==b'\1'
 ready=rd(u,0,0x200000);counts=rd(u,S+0xde4,288);rows=[]
 for step in range(3):
  before=view(u);before_grid=rd(u,S+0x108,2688);writes=[];handlers=[]
  def memory(uc,access,addr,size,value,data):
   addr&=0x1fffffff
   if S+0x108<=addr<S+0xb88:writes.append(dict(pc=hex(uc.reg_read(UC_MIPS_REG_PC)),offset=addr-S,size=size,value=value&0xffffffff))
  def code(uc,pc,n,data):
   if pc in P.HANDLERS and pc != 0x80032c68:handlers.append(P.HANDLERS[pc])
  w=u.hook_add(UC_HOOK_MEM_WRITE,memory);h=u.hook_add(UC_HOOK_CODE,code,begin=0x800329bc,end=0x80032c68)
  frame=P.SP-0x58;P.put(u,frame+0x58,S+0x80000000);P.put(u,frame+0x54,P.STOP);P.put(u,frame+0x50,P.SP)
  enter(u,0x80032814,P.STOP,frame);u.hook_del(w);u.hook_del(h)
  after=view(u);assert after['quantity']==0 and after['visitors']==0 and after['summary_present']==0 and rd(u,S+0xde4,288)==counts
  assert after['cash']==initial_view['cash']
  rows.append(dict(step=step+1,before=before,after=after,handlers=handlers,occupancy_writes=writes,grid_changed_bytes=sum(x!=y for x,y in zip(before_grid,rd(u,S+0x108,2688)))))
 assert [r['after']['state'] for r in rows]==[1,2,2]
 assert rows[1]['after']['wallet']==500 and rows[1]['after']['deadline']==120 and rows[1]['after']['wanted']==4
 assert rows[1]['after']['position']==[0,1,3] and rows[1]['after']['goal']==[0,0,0] and rows[1]['after']['route_hex']=='00'*10
 assert rows[2]['after']['position']==[0,0,0] and rows[2]['after']['wallet']==500
 # One original normal-admission control from same prepared state. Stop BEFORE loop.
 control=P.machine(exe,ready);control.mem_write(S+0xf04,bytes(32));P.put(control,0xd6270,0);control_before=view(control)
 enter(control,0x800319ac,0x80032814,P.SP,[S+0x80000000]);control_after=view(control)
 assert control_after['state']==1 and control_after['profile']==41 and control_after['quantity']==1
 assert control_after['visitors']==1 and control_after['summary_present']==1
 assert control_after['position']==[-1]*3 and control_after['goal']==[-1]*3 and control_after['route_hex']=='ff'*10
 profile=control_after['profile'];before_count=struct.unpack_from('<h',ready,S+0xde4+2*profile)[0];after_count=struct.unpack('<h',rd(control,S+0xde4+2*profile,2))[0];assert before_count-after_count==1
 result=dict(input_scope='Original newly loaded TOWN0001, controlled schedules0 for rivals1/2, festival switch1, month8/stage4/hour0,seed2. Empty slot record unmodified before demand. Main prep rebuild flag1 supplied. No natural festival/acquisition/UI replay.',initial_customer=initial_view,after_demand=after_demand,alias_writes=alias_writes,post_spawn_steps=rows,normal_admission_control=dict(seed=0,before=control_before,after=control_after,demand_profile=profile,demand_before=before_count,demand_after=after_count,stop='0x80032814 before loop'),original_entries=dict(bootstrap_loader_metrics=3,changed_schedule_metrics=1,demand=1,main_store_preparation=1,post_spawn=3,normal_admission=1,total=10),gameplay_callee_replacements=0,resource_loader_replacements=1,full_operating_updates=0,limits=['Post-spawn calls deliberately isolate one corrupted record from ordinary admissions and staff updates.','No natural elapsed days or actual festival presentation.','No sale/completed checkout/full lifecycle or permanent freeze claim.','Profile0 and appearance0 are stale empty-record fields, not new actual customer profile144.'])
 save('results.json',result)
 spans=[(0x80023670,0x800238b8),(0x80026844,0x80026878),(0x80031e60,0x800320d0),(0x80032814,0x800330e4),(0x800331b4,0x800340fc),(0x800340fc,0x800341a4)]
 save('source-provenance.json',dict(exe_sha256=sha(exe),archive_sha256=expected,town_sha256=sha(town),helper_path=str(HELPER.relative_to(ROOT.parent)),helper_sha256=sha(HELPER.read_bytes()),source_ranges=[dict(start=hex(lo),end_exclusive=hex(hi),sha256=sha(exe[lo-0x80010000+2048:hi-0x80010000+2048])) for lo,hi in spans],profile0_hex=exe[0xa09d0-0x10000+2048:0xa09d0-0x10000+2048+24].hex(),prior_independent_model_scope='Normal spawn, entry and movement formulas already in r2; newly composed with actual demand alias and compared with one original normal admission.'))
 print(json.dumps(dict(post_states=[r['after']['state'] for r in rows],phantom_quantity=rows[-1]['after']['quantity'],normal_quantity=control_after['quantity'],original_entries=10)))
if __name__=='__main__':main()
