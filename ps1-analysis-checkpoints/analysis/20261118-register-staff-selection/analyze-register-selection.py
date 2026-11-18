#!/usr/bin/env python3
"""Join original six register masters, 35 staff and selection timing.
Two diagnostic layout metrics plus three original staffing-gate calls.
"""
import argparse,hashlib,json,struct,zipfile,zlib,csv
from pathlib import Path
from unicorn import Uc,UC_ARCH_MIPS,UC_MODE_MIPS32,UC_MODE_LITTLE_ENDIAN
from unicorn.mips_const import *
ROOT=Path(__file__).resolve().parent;S=0x12b2f8;P=0x143ff8;SP=0x801f0000;STOP=0x80001000
SNAP=ROOT.parent/'20261113-new-rival-operation/encoded/evidence/source/opened-snapshots-20261028/TOWN0001-ci-main-34-single.ram.zlib'
ROSTER=ROOT.parent/'20261114-staff-roster-growth-data/staff-roster-data.json'
FIX=ROOT.parent/'20261113-product-stock-data/product-fixture-data.json'
def sha(b):return hashlib.sha256(b).hexdigest()
def put(n,v):(ROOT/n).write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n')
def main():
 ap=argparse.ArgumentParser();ap.add_argument('archive',type=Path);args=ap.parse_args()
 expected=json.loads((ROOT.parent.parent/'archives/20261103-r2/manifest.json').read_text())['sha256'];assert sha(args.archive.read_bytes())==expected
 with zipfile.ZipFile(args.archive) as z:exe=z.read('algorithm-analysis/source/SLPS_007.82')
 assert sha(exe)=='d6a167a1c9e0fe98d7e44e12968caa489ac3eb7ed3b9e46012a188af8432b1fd'
 baseline=zlib.decompress(SNAP.read_bytes());roster=json.loads(ROSTER.read_text());fixtures=json.loads(FIX.read_text())['fixtures']
 def raw(a,b):return exe[a-0x80010000+2048:b-0x80010000+2048]
 spans=[(0x80037f78,0x80038224),(0x80038af0,0x80038b70),(0x80039620,0x800396f8),(0x8002428c,0x80024368),(0x80023c20,0x80024820)]
 proof=[]
 for a,b in spans:
  data=raw(a,b);assert baseline[a&0x1fffffff:b&0x1fffffff]==data;proof.append(dict(start=hex(a),end_exclusive=hex(b),sha256=sha(data)))
 regs=[]
 for f in fixtures:
  if f['flags']&255!=4:continue
  assert raw(0x80099f0c+f['id']*196,0x80099f0c+(f['id']+1)*196)==struct.pack('<49i',*f['raw_words'])
  regs.append(dict(id=f['id'],name=f['name'],master_size=f['size'],cached_width=f['size'][0],additional_staff_block_at_active_count=f['size'][0]-1))
 assert [f['id'] for f in regs]==list(range(37,43))
 profiles=[]
 for p in roster['shared_initial_profiles']:
  c=p['initial_attributes']['customer_service'];skill=p['initial_attributes']['cashier'];counts=[]
  for parity in [0,1]:
   per=[]
   for slot in range(3):
    checkout=[];clean=[]
    for n in range(150):
     t=2*n+parity
     if (t>>1)%3!=slot:continue
     if 2*(t%100)>=2*(100-c):checkout.append(n)
     if t%100>=100-c:clean.append(n)
    assert checkout==clean;per.append(len(checkout))
   counts.append(per)
  profiles.append(dict(id=p['id'],name=p['name'],customer_service=c,cashier=skill,even_clock_passes_per50=counts[0],odd_clock_passes_per50=counts[1],existing_single_cashier_blocks_roll_values=min(100,max(0,2*skill)),additional_cashier_allowed_roll_values=100-min(100,max(0,2*skill))))
 calls=[];layouts=[]
 def machine(kinds):
  u=Uc(UC_ARCH_MIPS,UC_MODE_MIPS32|UC_MODE_LITTLE_ENDIAN);u.mem_map(0,0x200000);u.mem_write(0,baseline)
  def wr(a,v):u.mem_write(a&0x1fffffff,struct.pack('<I',v&0xffffffff))
  for j in range(10):u.mem_write(S+j*5080,b'\0')
  u.mem_write(S,bytes(5080));u.mem_write(S,b'\1');u.mem_write(S+4,struct.pack('<H',1));wr(S+68,20);wr(S+72,20);u.mem_write(S+0xdd8,struct.pack('<3h',0,1,2))
  for (x,y),kind in zip([(2,2),(8,4)],kinds):wr(S+264+y*112+x*4,0x80000000|(kind<<12))
  u.reg_write(UC_MIPS_REG_GP,0x800cd6c4);return u
 def wr(u,a,v):u.mem_write(a&0x1fffffff,struct.pack('<I',v&0xffffffff))
 def rd(u,a,n):return bytes(u.mem_read(a&0x1fffffff,n))
 def word(u,a):return struct.unpack('<I',rd(u,a,4))[0]
 def run(u,a):
  for r,v in [(UC_MIPS_REG_SP,SP),(UC_MIPS_REG_FP,SP),(UC_MIPS_REG_RA,STOP)]:u.reg_write(r,v)
  u.emu_start(a,STOP,count=3000000);assert u.reg_read(UC_MIPS_REG_PC)==STOP;calls.append(hex(a));return u.reg_read(UC_MIPS_REG_V0)
 for kinds in [(40,37),(37,40)]:
  u=machine(kinds);run(u,0x80023c20);xy=[word(u,0xce67c),word(u,0xce680)];width=rd(u,0xce684,1)[0];assert xy==[8,4] and width==fixtures[kinds[1]]['size'][0]
  wr(u,0xcd8ec,0);wr(u,0xcecfc,1);wr(u,0xd6270,0x12345678)
  for j in range(3):u.mem_write(P+j*60+40,bytes([int(j==0)]))
  u.mem_write(P+30,bytes([roster['shared_initial_profiles'][0]['initial_attributes']['cashier']])) # Supply original initial skill14, not evolved saved-RAM value.
  u.reg_write(UC_MIPS_REG_A0,S+0x80000000);u.reg_write(UC_MIPS_REG_A1,P+60+0x80000000)
  ret=run(u,0x80037f78);rng=word(u,0xd6270);assert (ret,rng)==((1,0x12345678) if width==2 else (0,0x0b719151))
  layouts.append(dict(anchors=[dict(xy=[2,2],fixture=kinds[0]),dict(xy=[8,4],fixture=kinds[1])],cached_checkout_xy=xy,cached_checkout_width=width,active_cashiers_supplied=1,other_cashier_id=0,other_cashier_skill=14,gate_result=ret,rng_before='0x12345678',rng_after=hex(rng)))
 # First cashier is accepted by the pre-gate without consuming RNG.
 wr(u,0xcecfc,0);u.mem_write(P+40,b'\0');seed=word(u,0xd6270);ret=run(u,0x80037f78);assert ret==0 and word(u,0xd6270)==seed
 put('register-staff-data.json',dict(registers=regs,profiles=profiles,formulas=dict(checkout_time='2*(uint32(clock)%100) >= 2*(100-signed8(staff+0x20))',equivalent_cleaning_time='uint32(clock)%100 >= 100-signed8(staff+0x20)',rest_reselection='(uint32(clock)>>1)%3 == staff_slot',staffing_gate='if active<=0 accept without RNG; if active>=signed8(cached_width)-1 reject without RNG; otherwise draw roll1..100 and reject if roll<=2*sum(cashier skill of other state1 assigned staff)'),scope='Timing gate opportunities and staffing pre-gate, not task success/fps or sales probabilities. Cashier/clean timing equality exists in prior independent model; newly checked source/formula and35 original profiles.'))
 put('bounded-results.json',dict(layout_cases=layouts,first_cashier=dict(gate_result=0,rng_preserved=True),entries=calls,original_cpu_calls=len(calls),gameplay_callee_replacements=0,original_operating_updates=0,scope='Artificial20x20 single store with two original register anchors; no UI-validity/footprint/route/service test. Staff states/active count diagnostic. Register count is not summed by this cached width gate.'))
 put('source-provenance.json',dict(exe_sha256=sha(exe),archive_sha256=expected,snapshot_sha256=sha(baseline),code_ranges=proof,prior_data={str(p.relative_to(ROOT.parent)):sha(p.read_bytes()) for p in [ROSTER,FIX]},original_formula_bytes={hex(a):raw(a,b).hex() for a,b in spans[:4]}))
 with (ROOT/'staff-selection.csv').open('w',newline='') as f:
  w=csv.writer(f);w.writerow(['id','name','customer_service','cashier','even_windows_per50','odd_windows_per50','blocked_roll_values_when_already_cashier'])
  for p in profiles:w.writerow([p['id'],p['name'],p['customer_service'],p['cashier'],p['even_clock_passes_per50'][0],p['odd_clock_passes_per50'][0],p['existing_single_cashier_blocks_roll_values']])
 print(json.dumps(dict(original_entries=len(calls),registers=len(regs),profiles=len(profiles),widths=[r['cached_checkout_width'] for r in layouts],gate_results=[r['gate_result'] for r in layouts])))
if __name__=='__main__':main()
