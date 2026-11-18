#!/usr/bin/env python3
"""Six original bounded entries for staff year/transfer connection questions."""
import argparse,struct,json,hashlib,zipfile,zlib
from pathlib import Path
from unicorn import Uc,UC_ARCH_MIPS,UC_MODE_MIPS32,UC_MODE_LITTLE_ENDIAN,UC_HOOK_CODE,UC_HOOK_MEM_READ,UC_HOOK_MEM_WRITE
from unicorn.mips_const import *
ROOT=Path(__file__).resolve().parent;STAFF=0x143ff8;STORE=0x12b2f8;SP=0x801f0000;STOP=0x80001000
FIELDS=[(0,2),(2,1),(3,1),(4,1),(6,2),(8,2),(12,4),(16,4),(20,4)]+[(a,1) for a in range(24,47)]+[(47,10)]
SNAP=ROOT.parent/'20261113-new-rival-operation/encoded/evidence/source/opened-snapshots-20261028/TOWN0001-ci-main-34-single.ram.zlib'
PACK=ROOT.parent/'20261114-staff-roster-growth-data/source/TOWNPS-staff-packed.bin'
def sha(b):return hashlib.sha256(b).hexdigest()
def put(n,v):(ROOT/n).write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n')
def main():
 ap=argparse.ArgumentParser();ap.add_argument('archive',type=Path);args=ap.parse_args()
 expected=json.loads((ROOT.parent.parent/'archives/20261103-r2/manifest.json').read_text())['sha256'];assert sha(args.archive.read_bytes())==expected
 with zipfile.ZipFile(args.archive) as z:exe=z.read('algorithm-analysis/source/SLPS_007.82')
 assert sha(exe)=='d6a167a1c9e0fe98d7e44e12968caa489ac3eb7ed3b9e46012a188af8432b1fd'
 base=zlib.decompress(SNAP.read_bytes());packed=PACK.read_bytes();assert len(packed)==35*54
 roster=bytearray(2100)
 for j in range(35):
  k=0
  for off,n in FIELDS:roster[j*60+off:j*60+off+n]=packed[j*54+k:j*54+k+n];k+=n
 ranges=[(0x80019eb4,0x8001a0b8),(0x80023c20,0x80024820),(0x8002a2f8,0x8002a47c),(0x80072774,0x80072f20),(0x8007220c,0x800722fc),(0x8007275c,0x80072774),(0x8003dda8,0x8003e0b4),(0x8001c8dc,0x8001ca7c)]
 proofs=[]
 for lo,hi in ranges:
  b=exe[lo-0x80010000+2048:hi-0x80010000+2048];assert base[lo&0x1fffffff:hi&0x1fffffff]==b
  proofs.append(dict(start=hex(lo),end_exclusive=hex(hi),sha256=sha(b)))
 calls=[]
 def machine():
  u=Uc(UC_ARCH_MIPS,UC_MODE_MIPS32|UC_MODE_LITTLE_ENDIAN);u.mem_map(0,0x200000);u.mem_write(0,base);u.mem_write(STAFF,bytes(roster));u.reg_write(UC_MIPS_REG_GP,0x800cd6c4);return u
 def wr(u,a,v):u.mem_write(a&0x1fffffff,struct.pack('<I',v&0xffffffff))
 def rd(u,a,n):return bytes(u.mem_read(a&0x1fffffff,n))
 def word(u,a):return struct.unpack('<i',rd(u,a,4))[0]
 def run(u,entry,end=STOP,frame=SP):
  for r,v in [(UC_MIPS_REG_SP,frame),(UC_MIPS_REG_FP,frame),(UC_MIPS_REG_RA,STOP)]:u.reg_write(r,v)
  h=u.hook_add(UC_HOOK_CODE,lambda uc,a,n,c:uc.emu_stop(),begin=end,end=end)
  u.emu_start(entry,STOP,count=3000000);u.hook_del(h);assert u.reg_read(UC_MIPS_REG_PC)==end,(hex(entry),hex(u.reg_read(UC_MIPS_REG_PC)))
  calls.append(dict(entry=hex(entry),stop=hex(end)));return u.reg_read(UC_MIPS_REG_V0)
 # Q1: Does the initial FFFF/69120 pair unlock at first one-year boundary?
 u=machine();wr(u,0xcd93c,69120);run(u,0x80023c20);calendar=[word(u,0xce608+4*j) for j in range(5)];assert calendar==[2,1,1,0,0]
 before=rd(u,STAFF,2100);access=[]
 def watch(uc,typ,address,n,value,c):
  a=address&0x1fffffff
  for j in range(35):
   lo=STAFF+60*j+16
   if a<lo+4 and a+n>lo:access.append(dict(pc=hex(uc.reg_read(UC_MIPS_REG_PC)),staff=j,kind=typ))
 h1=u.hook_add(UC_HOOK_MEM_READ,watch);h2=u.hook_add(UC_HOOK_MEM_WRITE,watch)
 run(u,0x8002a2f8,end=0x8002a47c);u.hook_del(h1);u.hook_del(h2);after=rd(u,STAFF,2100);p=27*60
 assert after[p:p+2]==before[p:p+2]==b'\xff\xff' and after[p+16:p+20]==before[p+16:p+20]==struct.pack('<I',69120) and after[p+3]==before[p+3]+1 and not access
 year=dict(tick=69120,calendar=calendar,staff27_owner_before=65535,staff27_owner_after=65535,staff27_word16_before=69120,staff27_word16_after=69120,age_before=before[p+3],age_after=after[p+3],changed_roster_offsets=[j for j in range(2100) if before[j]!=after[j]],word16_accesses=access,scope='Original year-aging block only after original metric calendar decode. Not full annual evaluation or elapsed playthrough.')
 def setup(selection,old):
  u=machine()
  for j in range(6):
   q=STAFF+j*60;u.mem_write(q,struct.pack('<H',1+old.index(j)//3 if j in old else 0));u.mem_write(q+25,b'\x01');u.mem_write(q+40,bytes([1,2+j%3,2,0,3,3,0]));wr(u,q+20,10+j)
  for j in range(2):
   b=bytearray(5080);b[0]=1;struct.pack_into('<H',b,4,j+1);struct.pack_into('<ii',b,68,28,26);struct.pack_into('<3h',b,0xdd8,*old[j*3:j*3+3]);struct.pack_into('<I',b,264+6*112+6*4,0x80000000|(48<<12)|120)
   for k in range(3):struct.pack_into('<I',b,264+2*112+(2+k)*4,0x80000000|(650<<12))
   u.mem_write(STORE+j*5080,bytes(b))
  wr(u,0xcd970,2);wr(u,0xe4328,0);wr(u,0xe432c,1)
  for j,v in enumerate(selection):wr(u,0xe3ed8+j*4,v)
  return u
 def transfer(selection,expected_ret,old=None,swap=False):
  old=old or [0,1,2,3,4,5]
  u=setup(old if swap else selection,old)
  if swap:
   # Original swap primitive: store0 manager <-> store1 empty third slot.
   prior_staff=rd(u,STAFF,2100);prior_store=rd(u,STORE,10160)
   for a,v in [(0xcd9c4,0),(0xcd9c8,1),(0xcd9ac,0),(0xcd9b0,2)]:wr(u,a,v)
   run(u,0x80072dbc)
   assert [word(u,0xe3ed8+4*j) for j in range(6)]==selection
   assert rd(u,STAFF,2100)==prior_staff and rd(u,STORE,10160)==prior_store
  before=rd(u,STAFF,2100);ret=run(u,0x80072774);after=rd(u,STAFF,2100);assert ret==expected_ret
  for j in range(35):
   assert after[j*60+16:j*60+24]==before[j*60+16:j*60+24] and after[j*60+25]==before[j*60+25]
  assert after[27*60:28*60]==before[27*60:28*60]
  ids=[list(struct.unpack('<3h',rd(u,STORE+j*5080+0xdd8,6))) for j in range(2)];assert ids==[selection[:3],selection[3:]]
  result=dict(original_roles_before=old,selection_created_by_original_swap=swap,selected=selection,returned_missing_manager_index_plus1=ret,actual_roles_after=ids,staff0_current_energy=after[25],staff3_current_energy=after[3*60+25],staff0_experience=word(u,STAFF+20),staff3_experience=word(u,STAFF+3*60+20),all_energy_word16_experience_preserved=True,staff27_whole_record_preserved=True,changed_staff_fields={str(j):[k for k in range(60) if before[j*60+k]!=after[j*60+k]] for j in range(6)})
  return u,result
 _,valid=transfer([3,1,2,0,4,5],0)
 u,invalid=transfer([-1,1,2,3,4,0],1,old=[0,1,2,3,4,-1],swap=True)
 # Error-dialog continuation goes back to input; cancellation jumps to epilogue.
 # Enter after cancel sound; no UI/audio replacement and no full UI replay.
 before_staff=rd(u,STAFF,2100);before_store=rd(u,STORE,10160);frame=SP-0x28;wr(u,frame+0x24,STOP);wr(u,frame+0x20,SP)
 run(u,0x800722f4,frame=frame);assert rd(u,STAFF,2100)==before_staff and rd(u,STORE,10160)==before_store
 invalid['cancel_return_tail_restores_data']=False;invalid['cancel_entry_scope']='After original cancel sound; 722F4 jump to7275C epilogue. UI/dialog/sound not executed.'
 put('results.json',dict(year_boundary=year,cross_store_valid=valid,missing_manager_then_cancel_tail=invalid,bounded_entries=calls,original_full_operating_updates=0,gameplay_callee_replacements=0,known_before='72774 two-pass assignments andpostwritevalidation inexistingstaff_transfer_binding model; same-store70F48 recovery/experience known. New cross-entry contrast, caller cancel connection andfirst-year FFFF/word16 boundary.',scope='Diagnostic inputs. Original store/staff/calendars are not one naturally played state. No whole UI, elapsed year, APK or universal unavailability claim.'))
 put('source-provenance.json',dict(archive_sha256=expected,exe_sha256=sha(exe),snapshot_sha256=sha(base),snapshot=str(SNAP.relative_to(ROOT.parent)),staff_packed_sha256=sha(packed),staff_packed=str(PACK.relative_to(ROOT.parent)),code_ranges_verified_against_original=proofs))
 print(json.dumps(dict(entries=len(calls),year=year['calendar'],owner27=year['staff27_owner_after'],word16=year['staff27_word16_after'],age=[year['age_before'],year['age_after']],valid_energy=valid['staff0_current_energy'],invalid_return=invalid['returned_missing_manager_index_plus1'])))
if __name__=='__main__':main()
