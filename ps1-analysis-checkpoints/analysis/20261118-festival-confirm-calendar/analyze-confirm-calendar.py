#!/usr/bin/env python3
"""Six bounded original-code entries; no UI or full operating replay."""
import argparse,hashlib,json,struct,zipfile,zlib
from pathlib import Path
from unicorn import Uc,UC_ARCH_MIPS,UC_MODE_MIPS32,UC_MODE_LITTLE_ENDIAN,UC_HOOK_CODE
from unicorn.mips_const import *
ROOT=Path(__file__).resolve().parent
S=0x12b2f8;SP=0x801f0000;STOP=0x80001000
SNAP=ROOT.parent/'20261113-new-rival-operation/encoded/evidence/source/opened-snapshots-20261028/TOWN0001-ci-main-34-single.ram.zlib'
def sha(b):return hashlib.sha256(b).hexdigest()
def put(n,v):(ROOT/n).write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n')
def main():
 ap=argparse.ArgumentParser();ap.add_argument('archive',type=Path);a=ap.parse_args()
 archive=a.archive.read_bytes();expected=json.loads((ROOT.parent.parent/'archives/20261103-r2/manifest.json').read_text())['sha256'];assert sha(archive)==expected
 with zipfile.ZipFile(a.archive) as z:exe=z.read('algorithm-analysis/source/SLPS_007.82')
 assert sha(exe)=='d6a167a1c9e0fe98d7e44e12968caa489ac3eb7ed3b9e46012a188af8432b1fd'
 base=zlib.decompress(SNAP.read_bytes());assert len(base)==0x200000
 ranges=[(0x800209f8,0x80021ad0),(0x80076308,0x80076474),(0x8003dda8,0x8003e000),(0x80022d28,0x80023000),(0x80019eb4,0x8001a100),(0x80023448,0x80023460),(0x80023c20,0x80024820),(0x80029334,0x80029450),(0x80062c90,0x80062cc4),(0x800631b4,0x80063208),(0x800636f0,0x80063714)]
 proof=[]
 for lo,hi in ranges:
  b=exe[lo-0x80010000+2048:hi-0x80010000+2048];assert base[lo&0x1fffffff:hi&0x1fffffff]==b
  proof.append(dict(start=hex(lo),end_exclusive=hex(hi),sha256=sha(b)))
 u=Uc(UC_ARCH_MIPS,UC_MODE_MIPS32|UC_MODE_LITTLE_ENDIAN);u.mem_map(0,0x200000);u.mem_write(0,base);u.reg_write(UC_MIPS_REG_GP,0x800cd6c4)
 def rd(a,n):return bytes(u.mem_read(a&0x1fffffff,n))
 def wr(a,v):u.mem_write(a&0x1fffffff,struct.pack('<I',v&0xffffffff))
 def word(a):return struct.unpack('<i',rd(a,4))[0]
 calls=[]
 def run(pc,args=(),end=STOP,frame=SP):
  for r,v in [(UC_MIPS_REG_SP,frame),(UC_MIPS_REG_FP,frame),(UC_MIPS_REG_RA,STOP)]:u.reg_write(r,v)
  for r,v in zip([UC_MIPS_REG_A0,UC_MIPS_REG_A1,UC_MIPS_REG_A2,UC_MIPS_REG_A3],args):u.reg_write(r,v)
  h=u.hook_add(UC_HOOK_CODE,lambda uc,a,n,c:uc.emu_stop(),begin=end,end=end)
  u.emu_start(pc,STOP,count=30000000);u.hook_del(h);assert u.reg_read(UC_MIPS_REG_PC)==end,(hex(pc),hex(u.reg_read(UC_MIPS_REG_PC)))
  calls.append(dict(entry=hex(pc),stop=hex(end)));return u.reg_read(UC_MIPS_REG_V0)
 # Valid fixture/product choice already established in preceding report.
 f=SP-0x70;wr(f+0x10,15);wr(f+0x14,f+0x60);run(0x800209f8,[S+0x80000000,10,2,10000],frame=f)
 cost=word(f+0x60);cells=rd(S+0x108,28*24*4)
 # Editor entry normally saves staff selections here. Preserve actual input IDs.
 staff=list(struct.unpack('<3H',rd(S+0xdd8,6)))
 for j,v in enumerate(staff):wr(0xe35e0+4*j,v)
 f=SP-0x40;wr(f+0x40,S+0x80000000);wr(f+0x3c,STOP);wr(f+0x38,SP)
 ret=run(0x80076308,frame=f);assert ret==0
 assert rd(S+0x108,28*24*4)==cells
 run(0x80023c20);accepted_stock=word(0xce65c+0x2c+15*4);assert accepted_stock==40
 # Restore operating baseline before independent calendar question.
 u.mem_write(0,base);wr(0xcd93c,44638)
 run(0x80023448,end=0x80023460);assert word(0xcd93c)==44640
 run(0x80023c20);calendar=[word(0xce608+4*j) for j in range(5)]
 assert calendar==[1,8,4,0,0],calendar
 stock15=word(0xce65c+0x2c+15*4)
 wr(0xcda00,9);run(0x80029334,end=0x800293c4);assert word(0xcda00)==0
 put('results.json',dict(price_confirmation=dict(method='static original control flow',parent='0x80062C90 calls 0x80062CFC; nonnegative return commits schedule at0x80062CC0',start_button_mask='0x800',accepted_path=['0x800631C0','0x800631CC sound','0x800631D4','0x800636F0 returns0'],cancel_mask='0x40',cancel_return=-1,correction='Child is price setting, not hiring; START acceptance path has no staff requirement or mandatory price edit.'),editor_accept=dict(original_stock_change_cost=cost,staff_input_ids=staff,entry='0x80076308',return_value=ret,product15_stock_after_accept=accepted_stock,all_2688_floor_bytes_preserved=True,floor_sha256=sha(cells),scope='Original successful editor tail only. No whole UI, parent final ledger, permit commit, or later operating persistence claim.'),calendar=dict(input_tick=44638,tick_after_original_increment=44640,derived_year_month_stage_hour_minute=calendar,finance_reached='0x800293C4',festival_switch_at_stop=0,meaning='Real calendar decoding reaches festival presentation branch. Stop before presentation; switch1 is only assigned after presentation at0x8002944C.',scope='Tick supplied at boundary; no elapsed-day playthrough, event blocker, festival movie or demand replay.'),bounded_entries=calls,gameplay_callee_replacements=0,full_operating_updates=0))
 put('source-provenance.json',dict(archive_sha256=expected,exe_sha256=sha(exe),snapshot=str(SNAP.relative_to(ROOT.parent)),snapshot_sha256=sha(base),code_ranges=proof))
 print(json.dumps(dict(entries=len(calls),editor_return=ret,cost=cost,calendar=calendar)))
if __name__=='__main__':main()
