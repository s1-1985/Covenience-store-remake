#!/usr/bin/env python3
"""Connect original festival demand write to the first customer state dispatch.
Bounded diagnostic inputs, not a naturally reached August playthrough.
"""
import argparse,hashlib,json,struct,zipfile,zlib
from pathlib import Path
from unicorn import Uc,UC_ARCH_MIPS,UC_MODE_MIPS32,UC_MODE_LITTLE_ENDIAN,UC_HOOK_CODE,UC_HOOK_MEM_WRITE
from unicorn.mips_const import UC_MIPS_REG_SP,UC_MIPS_REG_FP,UC_MIPS_REG_GP,UC_MIPS_REG_RA,UC_MIPS_REG_PC,UC_MIPS_REG_A0,UC_MIPS_REG_A1,UC_MIPS_REG_A2,UC_MIPS_REG_V0
ROOT=Path(__file__).resolve().parent;S=0x12b2f8;STOP=0x80001000;SP=0x801f0000
EXE_SHA='d6a167a1c9e0fe98d7e44e12968caa489ac3eb7ed3b9e46012a188af8432b1fd'
SNAPSHOT=ROOT.parent/'20261113-new-rival-operation/encoded/evidence/source/opened-snapshots-20261028/TOWN0001-ci-main-34-single.ram.zlib'
HANDLERS={0x800329bc:'entry',0x80032abc:'shopping_state2',0x80032b18:'checkout',0x80032b8c:'shopping_state4',0x80032c0c:'exit',0x80032c68:'no_state_handler'}
def sha(b):return hashlib.sha256(b).hexdigest()
def js(n,x):(ROOT/n).write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n')
def put(u,a,v):u.mem_write(a&0x1fffffff,struct.pack('<I',v&0xffffffff))
def get(u,a):return struct.unpack('<i',u.mem_read(a&0x1fffffff,4))[0]
def machine(exe,memory=None):
 u=Uc(UC_ARCH_MIPS,UC_MODE_MIPS32|UC_MODE_LITTLE_ENDIAN);u.mem_map(0,0x200000);u.mem_write(0,memory) if memory is not None else u.mem_write(0x10000,exe[2048:]);u.reg_write(UC_MIPS_REG_GP,0x800cd6c4);return u
def call(u,a,n=30000000):
 for r,v in [(UC_MIPS_REG_SP,SP),(UC_MIPS_REG_FP,SP),(UC_MIPS_REG_RA,STOP)]:u.reg_write(r,v)
 u.emu_start(a,STOP,count=n);assert u.reg_read(UC_MIPS_REG_PC)==STOP,(hex(a),hex(u.reg_read(UC_MIPS_REG_PC)))
def snapshot_info(u):
 return dict(order=[get(u,0xce61c+4*i) for i in range(10)],stock_alias_values=[get(u,0xce4cc+168*i) for i in range(10)],active=[dict(slot=i,flags=struct.unpack('<H',u.mem_read(S+5080*i+4,2))[0],schedule=get(u,S+5080*i+0xc78),stock15=get(u,0xce65c+168*i+0x2c+15*4)) for i in range(10) if u.mem_read(S+5080*i,1)[0]])
def fixture(exe,town):
 u=machine(exe);call(u,0x8005c858) # original one-time image/fixture runtime conversion
 u.mem_write(0x187e00,town);put(u,0xcd894,0x80187e00);u.reg_write(UC_MIPS_REG_A0,0);io=[]
 def resource(uc,a,n,c):
  if a==0x800140e8:io.append([uc.reg_read(UC_MIPS_REG_A0),uc.reg_read(UC_MIPS_REG_A1)]);uc.reg_write(UC_MIPS_REG_PC,uc.reg_read(UC_MIPS_REG_RA))
 h=u.hook_add(UC_HOOK_CODE,resource);call(u,0x8001a0b8);u.hook_del(h);assert io==[[0,11]]
 call(u,0x80023c20);return bytes(u.mem_read(0,0x200000)),snapshot_info(u)
def demand_case(exe,baseline,name,schedule,bypass,old_state=None,dispatch=False):
 u=machine(exe,baseline);before_info=snapshot_info(u);changes=[]
 for slot in range(10):
  if u.mem_read(S+5080*slot,1)[0] and get(u,S+5080*slot+0xc78)!=schedule:
   changes.append(dict(address=hex(S+5080*slot+0xc78),old=get(u,S+5080*slot+0xc78),new=schedule));put(u,S+5080*slot+0xc78,schedule)
 call(u,0x80023c20) # update derived operands after schedule changes
 # Calendar and festival switch are controlled diagnostic inputs; native finance/UI is not run.
 for a,v in [(0xce60c,8),(0xce610,4),(0xce614,0),(0xce618,0),(0xcda00,bypass),(0xd6270,2)]:put(u,a,v)
 target=S+2*5080+0xf04
 if old_state is not None:u.mem_write(target,bytes([old_state,255]))
 records_before=[bytes(u.mem_read(S+i*5080+0xf04,32)) for i in range(10)]
 invalid=[];writes=[];pending=[None]
 def selector(uc,a,n,c):
  if a==0x80026778:
   pending[0]=dict(x=uc.reg_read(UC_MIPS_REG_A1),y=uc.reg_read(UC_MIPS_REG_A2)) if uc.reg_read(UC_MIPS_REG_A0)==0x800a1750 else None
  elif a==0x80026780 and pending[0] is not None:
   d=uc.reg_read(UC_MIPS_REG_V0);invalid.append(dict(**pending[0],selected_slot=d if d<10 else -1));pending[0]=None
 def write(uc,access,a,n,v,c):
  a&=0x1fffffff
  for slot in range(10):
   p=S+slot*5080+0xf04
   if a<p+2 and a+n>p:
    writes.append(dict(pc=hex(uc.reg_read(UC_MIPS_REG_PC)),slot=slot,address=hex(a),size=n,before_hex=bytes(uc.mem_read(a,n)).hex(),written_low16=v&65535))
 h=u.hook_add(UC_HOOK_CODE,selector,begin=0x80026778,end=0x80026780);w=u.hook_add(UC_HOOK_MEM_WRITE,write,begin=S,end=S+50800-1);call(u,0x8002619c);u.hook_del(h);u.hook_del(w)
 records_after=[bytes(u.mem_read(S+i*5080+0xf04,32)) for i in range(10)]
 regular=[]
 for i in range(10):
  if u.mem_read(S+i*5080,1)[0]:
   counts=struct.unpack('<144h',u.mem_read(S+i*5080+0xde4,288));total=get(u,S+i*5080+0xde0);assert total==sum(counts);regular.append(dict(slot=i,total=total,sum_of_144_regular_counts=sum(counts)))
 if name.startswith('initial') and schedule==0 and bypass:
  assert invalid==[dict(x=39,y=10,selected_slot=-1),dict(x=15,y=14,selected_slot=2)],(name,invalid)
  assert len(writes)==1 and writes[0]['pc']=='0x80026868' and writes[0]['slot']==2
  expected=(int.from_bytes(records_before[2][:2],'little')+1)&65535;assert int.from_bytes(records_after[2][:2],'little')==expected
  assert records_after[2][2:]==records_before[2][2:]
 else:
  assert not writes
 result=dict(name=name,schedule_override=schedule,festival_switch=bypass,rng_seed=2,calendar=dict(month=8,stage=4,hour=0,subhour=0),source_info_before_changes=before_info,schedule_changes=changes,invalid_profile_selector_calls=invalid,first_customer_writes=writes,changed_first_records=[dict(slot=i,before_hex=b.hex(),after_hex=a.hex()) for i,(b,a) in enumerate(zip(records_before,records_after)) if a!=b],regular_demand_totals=regular,dispatch=None)
 if dispatch:
  # Enter exact post-spawn block with its parent stack frame; stop before first handler runs.
  put(u,0xcd8ec,2);frame=SP-0x58;put(u,frame+0x58,0x8012b2f8+5080*2);put(u,frame+0x54,STOP);put(u,frame+0x50,SP);u.reg_write(UC_MIPS_REG_SP,frame);u.reg_write(UC_MIPS_REG_FP,frame);hit=[]
  def stop(uc,a,n,c):
   if a in HANDLERS:hit.append(dict(address=hex(a),handler=HANDLERS[a],state=uc.mem_read(target,1)[0]));uc.emu_stop()
  h=u.hook_add(UC_HOOK_CODE,stop,begin=0x800329bc,end=0x80032c68);u.emu_start(0x80032814,STOP,count=100000);u.hook_del(h)
  assert len(hit)==1;state=records_after[2][0];expected=list(HANDLERS.values())[state-1] if 1<=state<=5 else 'no_state_handler';assert hit[0]['handler']==expected
  result['dispatch']=dict(**hit[0],scope='Original branch selection only, stopped before its handler executes; no purchase/checkout/exit effect claimed.')
 return result

def main():
 ap=argparse.ArgumentParser();ap.add_argument('archive',type=Path);args=ap.parse_args();arch=json.loads((ROOT.parent.parent/'archives/20261103-r2/manifest.json').read_text());assert sha(args.archive.read_bytes())==arch['sha256'];z=zipfile.ZipFile(args.archive);exe=z.read('algorithm-analysis/source/SLPS_007.82');assert sha(exe)==EXE_SHA;town=z.read('algorithm-analysis/source/TOWN0001.BIN')
 baseline,info=fixture(exe,town)
 rows=[demand_case(exe,baseline,'initial_control_24h_no_festival',2,0),demand_case(exe,baseline,'initial_control_24h_festival',2,1),demand_case(exe,baseline,'initial_control_schedule0_no_festival',0,0)]
 for state in range(6):rows.append(demand_case(exe,baseline,f'initial_schedule0_festival_old_state{state}',0,1,state,True))
 compressed=SNAPSHOT.read_bytes();live=zlib.decompress(compressed);assert len(live)==0x200000
 # Snapshot CPU state is not reused; only complete saved RAM is input to bounded functions.
 for a,e in [(0x8002619c,0x80027378),(0x80032814,0x80032c6c)]:assert live[a&0x1fffffff:e&0x1fffffff]==exe[a-0x80010000+2048:e-0x80010000+2048]
 u=machine(exe,live);call(u,0x80023c20);live=bytes(u.mem_read(0,0x200000));rows.append(demand_case(exe,live,'saved_operating_state_schedule0_festival',0,1))
 js('cases.json',rows);js('initial-source-operands.json',info)
 js('source-provenance.json',dict(exe_sha256=EXE_SHA,archive_sha256=arch['sha256'],town_archive_entry='algorithm-analysis/source/TOWN0001.BIN',town_sha256=sha(town),saved_operating_state=dict(path=str(SNAPSHOT.relative_to(ROOT.parent.parent)),compressed_sha256=sha(compressed),ram_sha256=sha(zlib.decompress(compressed)),clock=struct.unpack_from('<i',zlib.decompress(compressed),0xcd93c)[0]),fixture_policy='Original table bootstrap5C858, original packed-town loader with external resource substitution, original metrics. Uniform schedules and calendar/festival switch/state bytes are controlled inputs, not user UI actions or naturally elapsed dates.'))
 spans=[('demand_and_selector',0x8002619c,0x80027378),('customer_dispatch',0x80032814,0x80032c6c),('customer_state_jump_table',0x80010918,0x8001092c),('adjacent_profile144_text',0x800a1750,0x800a1768),('festival_flag_producer',0x80029394,0x80029450)]
 for n,a,e in spans:(ROOT/'source'/f'{n}.bin').write_bytes(exe[a-0x80010000+2048:e-0x80010000+2048])
 js('source-ranges.json',[dict(file='source/'+n+'.bin',start=hex(a),end_exclusive=hex(e),sha256=sha((ROOT/'source'/f'{n}.bin').read_bytes())) for n,a,e in spans])
 js('summary.json',dict(demand_cases=len(rows),state_dispatch_cases=6,gameplay_callee_replacements=0,external_resource_replacements=1,natural_operating_updates=0,new_result='Original full2619C writes1 into first-customer state at slot2 from mix136 invalid profile144 under controlled schedule0/festival input; native dispatch changes entry/shopping/checkout/exit branch, and oldstate5 becomes6 outside five handlers.',controls='Default schedule2 and non-festival inputs produce no alias writes. Saved live four-store state with first order0 and zero stock15 atstore0 produces no alias writes in this seed/input.',remaining='Natural festival reachability after legitimate schedule/ownership/inventory changes and actual downstream visual/financial outcomes remain unconfirmed. R02 remains open, narrowed.'))
 print((ROOT/'summary.json').read_text())
if __name__=='__main__':main()
