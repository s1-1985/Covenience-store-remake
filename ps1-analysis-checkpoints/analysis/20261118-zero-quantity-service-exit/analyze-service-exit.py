#!/usr/bin/env python3
"""Bounded service/accounting/exit consequences of the observed zero headcount.
Synthetic register rendezvous; no natural route or full festival replay claim.
"""
import argparse,hashlib,json,struct,zipfile
from pathlib import Path
from unicorn import Uc,UC_ARCH_MIPS,UC_MODE_MIPS32,UC_MODE_LITTLE_ENDIAN,UC_HOOK_CODE,UC_HOOK_MEM_WRITE
from unicorn.mips_const import *
ROOT=Path(__file__).resolve().parent
PRIOR=ROOT.parent/'20261118-festival-empty-slot-lifecycle/results.json'
S=0x12b2f8;P=0x143ff8;M=0xcecec;SP=0x801f0000;STOP=0x80001000

def sha(b):return hashlib.sha256(b).hexdigest()
def out(n,x):(ROOT/n).write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n')
def wr(u,a,v):u.mem_write(a&0x1fffffff,struct.pack('<I',v&0xffffffff))
def rd(u,a,n):return bytes(u.mem_read(a&0x1fffffff,n))
def word(u,a):return struct.unpack('<i',rd(u,a,4))[0]
def person(u,j):
 b=rd(u,S+0xf04+32*j,32)
 return dict(raw_hex=b.hex(),state=b[0],profile=struct.unpack_from('<h',b,2)[0],quantity=b[30],wallet=struct.unpack_from('<h',b,8)[0],cart=struct.unpack_from('<h',b,10)[0],position=list(struct.unpack_from('<3b',b,12)),goal=list(struct.unpack_from('<3b',b,15)))
def state(u):return dict(customers=[person(u,j) for j in range(2)],cash=word(u,0xcd9f8),revenue=word(u,S+0xd98),completion_flags=struct.unpack('<H',rd(u,0xcd790,2))[0],cashier_busy=[word(u,M+4+4*j) for j in range(3)],present=word(u,0xce65c+20),visitors=word(u,S+0x1188))
def machine(exe,record,q):
 u=Uc(UC_ARCH_MIPS,UC_MODE_MIPS32|UC_MODE_LITTLE_ENDIAN);u.mem_map(0,0x200000);u.mem_write(0x10000,exe[2048:]);u.reg_write(UC_MIPS_REG_GP,0x800cd6c4)
 u.mem_write(S,bytes(5080));u.mem_write(S,b'\1');wr(u,S+68,14);wr(u,S+72,14);wr(u,S+0xc70,0);u.mem_write(S+4,struct.pack('<H',1));u.mem_write(S+0xdd8,struct.pack('<3h',0,-1,-1))
 wr(u,S+0x108+2*112+2*4,0x80000000|(37<<12));wr(u,0xcd8ec,0);wr(u,0xcd9f8,10000);wr(u,0xd6270,0)
 u.mem_write(P,bytes(60));u.mem_write(P+40,bytes([1,3,1,1]));u.mem_write(P+30,b'\x64');u.mem_write(P+24,b'\x64\x64')
 for j,quantity in [(0,q),(1,1)]:
  b=bytearray(record);b[0]=3;b[1]=255;struct.pack_into('<h',b,10,250);b[12:15]=bytes([3+j,4,0]);b[15:18]=b[12:15];b[18:28]=b'\xff'*10;b[30]=quantity
  if j==1:b[28]=100
  u.mem_write(S+0xf04+32*j,bytes(b));wr(u,S+0x108+4*112+(3+j)*4,640<<12)
 return u

def post(u):
 f=SP-0x58;wr(u,f+0x58,S+0x80000000);wr(u,f+0x54,STOP);wr(u,f+0x50,SP)
 for r,v in [(UC_MIPS_REG_SP,f),(UC_MIPS_REG_FP,f),(UC_MIPS_REG_RA,STOP)]:u.reg_write(r,v)
 u.emu_start(0x80032814,STOP,count=1000000);assert u.reg_read(UC_MIPS_REG_PC)==STOP

def main():
 ap=argparse.ArgumentParser();ap.add_argument('archive',type=Path);a=ap.parse_args()
 expected=json.loads((ROOT.parent.parent/'archives/20261103-r2/manifest.json').read_text())['sha256'];assert sha(a.archive.read_bytes())==expected
 with zipfile.ZipFile(a.archive) as z:exe=z.read('algorithm-analysis/source/SLPS_007.82')
 assert sha(exe)=='d6a167a1c9e0fe98d7e44e12968caa489ac3eb7ed3b9e46012a188af8432b1fd'
 prior=json.loads(PRIOR.read_text());record=bytes.fromhex(prior['post_spawn_steps'][-1]['after']['raw_hex']);assert record[30]==0 and record[0]==2
 # Six source register master dimensions were established previously; verify chosen37.
 row=struct.unpack_from('<49i',exe,0x99f0c+37*196-0x10000+2048);assert (row[0]&255,row[9],row[10])==(4,2,1)
 results=[];zero_after=None
 for quantity in [0,1]:
  u=machine(exe,record,quantity);before=state(u);service=[];revenues=[];writes=[]
  def code(uc,pc,n,data):
   if pc==0x8003839c:service.append(dict(customer_pointer=hex(uc.reg_read(UC_MIPS_REG_A1)),busy_before=word(uc,M+4)))
   if pc==0x8001ca7c:revenues.append(dict(amount=uc.reg_read(UC_MIPS_REG_A1),mode=uc.reg_read(UC_MIPS_REG_A2)))
  def memory(uc,access,addr,size,value,data):
   addr&=0x1fffffff
   if addr==M+4:writes.append(dict(pc=hex(uc.reg_read(UC_MIPS_REG_PC)),value=value))
  u.hook_add(UC_HOOK_CODE,code);u.hook_add(UC_HOOK_MEM_WRITE,memory);post(u);after=state(u)
  assert after['cash']-before['cash']==250*quantity and after['revenue']==250*quantity
  assert after['customers'][0]['state']==4 and after['customers'][0]['cart']==0
  assert after['customers'][1]['state']==3 and after['customers'][1]['cart']==250
  assert after['cashier_busy']==[1,0,0] and after['completion_flags']&0x200
  assert [s['busy_before'] for s in service]==[0,1] and revenues==[dict(amount=250*quantity,mode=1)]
  assert writes==[dict(pc='0x8003871c',value=1)]
  results.append(dict(quantity=quantity,before=before,after=after,service_entries=service,revenue_entries=revenues,cashier_busy_writes=writes))
  if quantity==0:zero_after=rd(u,S+0xf04,32)
 # Connected post-checkout record; only exit state/position/goal are staged.
 u=machine(exe,record,0);u.mem_write(S+0xf24,bytes(32));b=bytearray(zero_after);b[0]=5;b[12:15]=bytes([0,1,2]);b[15:18]=b[12:15];b[18:28]=b'\xff'*10;u.mem_write(S+0xf04,bytes(b))
 # Remove synthetic old service occupants, place one actor at a boundary exit.
 wr(u,S+0x108+4*112+3*4,0);wr(u,S+0x108+4*112+4*4,0);cell=S+0x108+112;wr(u,cell,640<<12)
 before=state(u);before_cell=word(u,cell);post(u);after=state(u)
 assert after['customers'][0]['state']==0 and after['customers'][0]['position']==[0,1,2] and after['customers'][0]['goal']==[-1]*3
 assert word(u,cell)==0 and after['cash']==before['cash'] and after['revenue']==0 and after['present']==0 and after['visitors']==0
 u.reg_write(UC_MIPS_REG_SP,SP);u.reg_write(UC_MIPS_REG_FP,SP);u.reg_write(UC_MIPS_REG_RA,STOP);u.reg_write(UC_MIPS_REG_A0,S+0x80000000);u.emu_start(0x800330e4,STOP,count=10000);assert u.reg_read(UC_MIPS_REG_PC)==STOP;slot=u.reg_read(UC_MIPS_REG_V0);assert slot==0
 out('results.json',dict(service_cases=results,exit_case=dict(before=before,after=after,occupancy_before=before_cell,occupancy_after=word(u,cell),free_slot_after_exit=slot),original_entries=dict(post_spawn_loops=3,free_slot=1,total=4),full_operating_updates=0,gameplay_callee_replacements=0,limits=['Diagnostic checkout/exit rendezvous, basket250 and cashier skill100; no proof the festival-created actor reaches these positions/cart naturally.','Artificial14x14 store with one native register37 anchor; no placement UI/whole footprint validity claim.','Next customer at a different adjacent cell with patience100; two service requests in one loop.','Reused zero-quantity record came from prior alias experiment; do not count its creation again.']))
 spans=[(0x80032814,0x800330e4),(0x80035128,0x80035338),(0x80035818,0x8003594c),(0x80038660,0x80038898),(0x800330e4,0x800331b4),(0x8001ca7c,0x8001cbc4)]
 out('source-provenance.json',dict(exe_sha256=sha(exe),archive_sha256=expected,prior_path=str(PRIOR.relative_to(ROOT.parent)),prior_sha256=sha(PRIOR.read_bytes()),zero_quantity_source_record_hex=record.hex(),register_master=dict(id=37,size=[row[9],row[10]],flags=row[0]),source_ranges=[dict(start=hex(lo),end_exclusive=hex(hi),sha256=sha(exe[lo-0x80010000+2048:hi-0x80010000+2048])) for lo,hi in spans],known_before='Standalone checkout multiplication, staff busy flag, exit position commit and free-slot formulas in existing r2. New observedzeroquantity-to-service/blocking/exit connections, not new ordinary formulas.'))
 print(json.dumps(dict(original_entries=4,service_cash_deltas=[r['after']['cash']-r['before']['cash'] for r in results],second_customer_states=[r['after']['customers'][1]['state'] for r in results],exit_state=after['customers'][0]['state'],free_slot=slot)))
if __name__=='__main__':main()
