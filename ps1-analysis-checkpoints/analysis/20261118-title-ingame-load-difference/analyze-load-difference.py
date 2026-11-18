#!/usr/bin/env python3
"""Same encoded input, selected title versus accepted in-game load tails.
Card/graphics/BGM are not executed. No UI return values or callees are patched.
"""
import argparse,hashlib,importlib.util,json,struct,zipfile
from pathlib import Path
from unicorn import UC_HOOK_CODE,UC_HOOK_MEM_WRITE
from unicorn.mips_const import *
ROOT=Path(__file__).resolve().parent
HELPER=ROOT.parent/'20261117-festival-customer-state-data/analyze-festival-state.py'
spec=importlib.util.spec_from_file_location('prior_festival',HELPER);P=importlib.util.module_from_spec(spec);spec.loader.exec_module(P)
TARGET=P.S+2*5080+0xf04;QUEUE=0x137970

def sha(b):return hashlib.sha256(b).hexdigest()
def out(n,v):(ROOT/n).write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n')
def rd(u,a,n):return bytes(u.mem_read(a&0x1fffffff,n))
def view(u):return dict(festival=P.get(u,0xcda00),customer_hex=rd(u,TARGET,32).hex(),active_queue_slots=[j for j in range(50) if rd(u,QUEUE+160*j,1)[0]],notice_active=P.get(u,0x1398b4),notice_timer=P.get(u,0x1398b8),notice_index=P.get(u,0x1398b0),calendar=[P.get(u,0xce608+4*j) for j in range(5)],rng=hex(P.get(u,0xd6270)&0xffffffff))
def chunk(u,entry,end,frame):
 for r,v in [(UC_MIPS_REG_SP,frame),(UC_MIPS_REG_FP,frame),(UC_MIPS_REG_RA,P.STOP)]:u.reg_write(r,v)
 h=u.hook_add(UC_HOOK_CODE,lambda uc,pc,n,c:uc.emu_stop(),begin=end,end=end);u.emu_start(entry,P.STOP,count=30000000);u.hook_del(h);assert u.reg_read(UC_MIPS_REG_PC)==end,(hex(entry),hex(u.reg_read(UC_MIPS_REG_PC)))
def main():
 ap=argparse.ArgumentParser();ap.add_argument('archive',type=Path);a=ap.parse_args()
 expected=json.loads((ROOT.parent.parent/'archives/20261103-r2/manifest.json').read_text())['sha256'];assert sha(a.archive.read_bytes())==expected
 with zipfile.ZipFile(a.archive) as z:exe=z.read('algorithm-analysis/source/SLPS_007.82');town=z.read('algorithm-analysis/source/TOWN0001.BIN')
 assert sha(exe)==P.EXE_SHA
 baseline,_=P.fixture(exe,town);u=P.machine(exe,baseline)
 for j in [1,2]:P.put(u,P.S+5080*j+0xc78,0)
 P.put(u,0xcd93c,44640);P.call(u,0x80023c20);P.put(u,0xcda00,1);P.put(u,0xd6270,2)
 # An original pending completion-style notice with a valid empty text terminator.
 u.mem_write(0xe4020,b'\xff\x40'+bytes(118));P.put(u,P.SP+16,0)
 for r,v in [(UC_MIPS_REG_A0,2),(UC_MIPS_REG_A1,0),(UC_MIPS_REG_A2,29),(UC_MIPS_REG_A3,1)]:u.reg_write(r,v)
 P.call(u,0x8003ecd8);assert view(u)['active_queue_slots']==[1]
 P.call(u,0x8006b81c);payload=rd(u,0x187e00,0x197ac);assert struct.unpack_from('<I',payload,0x197a8)[0]==sum(payload[:0x197a8])&0xffffffff
 baseline=rd(u,0,0x200000);source=view(u);assert rd(u,TARGET,32)==bytes(32)
 results=[]
 for route in ['title','ingame_accepted']:
  u=P.machine(exe,baseline);P.call(u,0x8006bc40);decoded=view(u);queue_before=rd(u,QUEUE,8000);stores_before=rd(u,P.S,50800);queue_writes=[];alias=[];flag_writes=[]
  def memory(uc,access,addr,size,value,data):
   addr&=0x1fffffff;pc=uc.reg_read(UC_MIPS_REG_PC)
   if QUEUE<=addr<QUEUE+8000 and (addr-QUEUE)%160==0:queue_writes.append(dict(pc=hex(pc),slot=(addr-QUEUE)//160,size=size,value=value))
   if addr<TARGET+2 and addr+size>TARGET:alias.append(dict(pc=hex(pc),size=size,value=value&65535))
   if addr<0xcda04 and addr+size>0xcda00:flag_writes.append(dict(pc=hex(pc),size=size,value=value&0xffffffff))
  h=u.hook_add(UC_HOOK_MEM_WRITE,memory)
  if route=='title':
   after_reset=None;chunk(u,0x80012d44,0x80012d68,P.SP)
  else:
   # Original block after decode/graphics setup and beforeBGM restore; no child skipped
   # via a forged return. A separate original metrics/demand block follows.
   chunk(u,0x800624d0,0x80062588,P.SP-0x28);after_reset=view(u)
   assert rd(u,P.S,50800)==stores_before and after_reset['festival']==0
   assert after_reset['active_queue_slots']==[] and [after_reset[k] for k in ['notice_active','notice_timer','notice_index']]==[0,0,0]
   chunk(u,0x80062598,0x800625b4,P.SP-0x28)
  u.hook_del(h);after=view(u);queue_after=rd(u,QUEUE,8000)
  if route=='title':
   assert after['festival']==1 and rd(u,TARGET,32)==b'\1'+bytes(31) and after['active_queue_slots']==[1]
   assert alias==[dict(pc='0x80026868',size=2,value=1)] and not queue_writes and not flag_writes
   assert queue_after==queue_before
  else:
   assert after['festival']==0 and rd(u,TARGET,32)==bytes(32) and not after['active_queue_slots'] and not alias
   assert queue_writes==[dict(pc='0x8006251c',slot=j,size=1,value=0) for j in range(50)]
   assert flag_writes==[dict(pc='0x80062560',size=4,value=0)]
   assert all(queue_before[j*160+1:(j+1)*160]==queue_after[j*160+1:(j+1)*160] for j in range(50))
  results.append(dict(route=route,decoded=decoded,after_reset=after_reset,after=after,queue_active_byte_writes=queue_writes,customer_alias_writes=alias,festival_writes=flag_writes,notice_slot1_before=queue_before[160:320].hex(),notice_slot1_after=queue_after[160:320].hex()))
 # Original parent branch: only dialog return1 enters decode/reset/rebuild branch.
 def raw(a,b):return exe[a-0x80010000+2048:b-0x80010000+2048]
 branch=int.from_bytes(raw(0x800624b8,0x800624bc),'little');offset=struct.unpack('<h',struct.pack('<H',branch&65535))[0];target=(0x800624bc+4*offset)&0xffffffff
 assert branch>>26==5 and target==0x800625c4
 parent_calls=[]
 for pc in range(0x80062484,0x800626bc,4):
  w=int.from_bytes(raw(pc,pc+4),'little')
  if w>>26==3:parent_calls.append(dict(pc=hex(pc),target=hex(0x80000000|((w&0x3ffffff)<<2))))
 assert not any(c['target'] in ['0x8006bc40','0x80023c20','0x8002619c'] for c in parent_calls if int(c['pc'],16)>=target)
 out('results.json',dict(source=source,payload_sha256=sha(payload),payload_size=len(payload),same_payload_used_for_both_routes=True,cases=results,parent_acceptance_gate=dict(method='Static verified native instructions; dialog UI and non1 branch not executed',decision_pc='0x800624b8',word=hex(branch),condition='if dialog_return !=1 branch to625C4',non1_target=hex(target),load_block='0x800624c0..0x800625c4',common_tail='0x800625c4..0x800626bc',direct_jal_calls=parent_calls),original_entries=dict(bootstrap_town_metrics=3,changed_clock_metrics=1,notice_reservation=1,encoding=1,decodes=2,title_tail=1,ingame_blocks=2,total=11),whole_operating_updates=0,gameplay_callee_replacements=0,resource_loader_replacements=1,limits=['Controlled schedules0,flag1,clock44640,seed2,clean customer and pending notice; not normal saves created throughcardUI.','Title graphics/prereconstruction and ingame graphics/BGM omitted by entering selected original blocks, not by patching callee returns.','No whole load dialog, true card I/O, first resumed main or natural festival replay.','Non1 paths include other dialog outcomes; no claim all such outcomes are cancellation or no state changes.']))
 spans=[(0x80062484,0x800624d0),(0x800624d0,0x80062588),(0x80062598,0x800625c4),(0x800625c4,0x800626bc),(0x80012d44,0x80012d68)]
 out('source-provenance.json',dict(exe_sha256=sha(exe),archive_sha256=expected,town_sha256=sha(town),helper_path=str(HELPER.relative_to(ROOT.parent)),helper_sha256=sha(HELPER.read_bytes()),code_ranges=[dict(start=hex(lo),end_exclusive=hex(hi),sha256=sha(raw(lo,hi)),hex=raw(lo,hi).hex()) for lo,hi in spans],known_before='Generic save/card/menu paths were tested in existingr2 and20261105-play-save. Priorfestival report onlybounded title tail. New same-input festival andpendingnotice comparison plus acceptance-block connection.'))
 print(json.dumps(dict(entries=11,title_customer=results[0]['after']['customer_hex'][:2],ingame_customer=results[1]['after']['customer_hex'][:2],queue_slots=[r['after']['active_queue_slots'] for r in results],non1_branch=hex(target))))
if __name__=='__main__':main()
