#!/usr/bin/env python3
"""Two short original-code calls for the previously untested R02 state6 tail.
Synthetic post-corruption input; no natural festival or gameplay-day claim.
"""
import argparse,hashlib,json,struct,zipfile
from pathlib import Path
from unicorn import Uc,UC_ARCH_MIPS,UC_MODE_MIPS32,UC_MODE_LITTLE_ENDIAN,UC_HOOK_CODE,UC_HOOK_MEM_WRITE
from unicorn.mips_const import UC_MIPS_REG_SP,UC_MIPS_REG_FP,UC_MIPS_REG_GP,UC_MIPS_REG_RA,UC_MIPS_REG_PC,UC_MIPS_REG_A0,UC_MIPS_REG_V0
ROOT=Path(__file__).resolve().parent;STORE=0x12b2f8;SP=0x801f0000;STOP=0x80001000
def sha(b):return hashlib.sha256(b).hexdigest()
def put(n,x):(ROOT/n).write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n')
def main():
 ap=argparse.ArgumentParser();ap.add_argument('archive',type=Path);args=ap.parse_args()
 expected=json.loads((ROOT.parent.parent/'archives/20261103-r2/manifest.json').read_text())['sha256'];assert sha(args.archive.read_bytes())==expected;z=zipfile.ZipFile(args.archive)
 exe=z.read('algorithm-analysis/source/SLPS_007.82');assert sha(exe)=='d6a167a1c9e0fe98d7e44e12968caa489ac3eb7ed3b9e46012a188af8432b1fd'
 u=Uc(UC_ARCH_MIPS,UC_MODE_MIPS32|UC_MODE_LITTLE_ENDIAN);u.mem_map(0,0x200000);u.mem_write(0x10000,exe[2048:]);u.reg_write(UC_MIPS_REG_GP,0x800cd6c4)
 def write32(a,v):u.mem_write(a&0x1fffffff,struct.pack('<I',v&0xffffffff))
 store=bytearray(5080);store[0]=1;store[1]=0xa5;struct.pack_into('<ii',store,0x44,14,14);struct.pack_into('<i',store,0xc70,0)
 p=bytearray(32);p[0:2]=bytes([6,255]);struct.pack_into('<h',p,2,0);struct.pack_into('<hh',p,8,5678,1234);p[12:15]=bytes([2,2,1]);p[15:18]=b'\xff'*3;p[30]=2
 store[0xf04:0xf24]=p;cell=0x108+2*112+2*4;struct.pack_into('<I',store,cell,642<<12);u.mem_write(STORE,bytes(store));write32(0xcd8ec,0)
 for i in range(3):write32(0xcf860+i*4,99)
 frame=SP-0x58;write32(frame+0x58,0x80000000+STORE);write32(frame+0x54,STOP);write32(frame+0x50,SP)
 u.reg_write(UC_MIPS_REG_SP,frame);u.reg_write(UC_MIPS_REG_FP,frame);u.reg_write(UC_MIPS_REG_RA,STOP)
 handlers={0x800329bc:'entry',0x80032abc:'shopping2',0x80032b18:'checkout',0x80032b8c:'shopping4',0x80032c0c:'exit'};hits=[];branches=[];writes=[];instructions=[0]
 def code(uc,a,n,c):
  instructions[0]+=1
  if a in handlers:hits.append(dict(pc=hex(a),handler=handlers[a]))
  if a in (0x80032c68,0x80032d58,0x80032d60):branches.append(hex(a))
 def memory(uc,access,a,n,v,c):
  a&=0x1fffffff
  if STORE<=a<STORE+5080:writes.append(dict(pc=hex(uc.reg_read(UC_MIPS_REG_PC)),address=hex(a),bytes=n,value=v))
 h=u.hook_add(UC_HOOK_CODE,code);w=u.hook_add(UC_HOOK_MEM_WRITE,memory)
 u.emu_start(0x80032814,STOP,count=20000);assert u.reg_read(UC_MIPS_REG_PC)==STOP
 u.hook_del(h);u.hook_del(w);after=bytes(u.mem_read(STORE,5080));scratch=struct.unpack('<3i',u.mem_read(0xcf860,12))
 assert after==bytes(store) and not hits and not writes and branches==['0x80032c68','0x80032d58'] and scratch==(2,2,1)
 tail=dict(start='0x80032814',returned_to=hex(STOP),instructions=instructions[0],customer_before_hex=p.hex(),customer_after_hex=after[0xf04:0xf24].hex(),store_before_sha256=sha(store),store_after_sha256=sha(after),store_writes=writes,child_handlers=hits,tail_branches=branches,old_position_copied_to_scratch=list(scratch),wallet_before_after=[5678,struct.unpack_from('<h',after,0xf04+8)[0]],cart_before_after=[1234,struct.unpack_from('<h',after,0xf04+10)[0]],dirty_flag_before_after=[165,after[1]],occupancy_word_before_after=[642<<12,struct.unpack_from('<I',after,cell)[0]])
 # Original slot finder: firststate6 followed byninezero states. It must skip0.
 u.reg_write(UC_MIPS_REG_SP,SP);u.reg_write(UC_MIPS_REG_FP,SP);u.reg_write(UC_MIPS_REG_RA,STOP);u.reg_write(UC_MIPS_REG_A0,STORE+0x80000000)
 u.emu_start(0x800330e4,STOP,count=10000);assert u.reg_read(UC_MIPS_REG_PC)==STOP;slot=u.reg_read(UC_MIPS_REG_V0);assert slot==1 and bytes(u.mem_read(STORE,5080))==after
 put('state6-results.json',dict(input_kind='Synthetic firstslot state6 withvalid oldcoordinates,nonzero wallet/cart andexistingoccupancy. Othernine slots inactive. State6 creationitself isreusedfrompreviousfestival report,notrerun here.',post_spawn_call=tail,free_slot_call=dict(start='0x800330E4',first_state=6,other_states=[0]*9,returned_slot=slot,store_unchanged=True),original_cpu_calls=2,original_operating_updates=0,callee_replacements=0,limitations=['No naturalfestivalreachability proof.','No full-frame drawing or video.','No interveningday/reset/resize/other-event writes modelled.']))
 refs=[]
 for a,e in [(0x80032884,0x800328a4),(0x800328d0,0x80032998),(0x80032c68,0x80032d60),(0x800330b0,0x800330e4),(0x800330e4,0x800331b4)]:
  b=exe[a-0x80010000+2048:e-0x80010000+2048];refs.append(dict(start=hex(a),end_exclusive=hex(e),sha256=sha(b),raw_hex=b.hex()))
 put('source-evidence.json',dict(archive_sha256=expected,exe_sha256=sha(exe),raw_ranges=refs,prior_creation_evidence='../20261117-festival-customer-state-data/README.md',existing_models=[dict(path=n,sha256=sha(z.read('algorithm-analysis/'+n))) for n in ['customer_loop.py','customer_position.py','customer_spawn_core.py']],novelty='Post-spawn tailand free-slot behavior understate6, previouslystopped beforetail. Ordinaryloop/position/spawn formulas alreadyknown. Rawranges embeddedonlyforminimal conditionalproof; no copied RAM.'))
 print(json.dumps(dict(state6_preserved=after[0xf04]==6,all_store_bytes_unchanged=after==bytes(store),first_free_slot=slot,original_cpu_calls=2,operating_updates=0)))
if __name__=='__main__':main()
