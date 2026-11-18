#!/usr/bin/env python3
"""Static presentation control and three original post-presentation entries."""
import argparse,hashlib,json,struct,zipfile,zlib
from pathlib import Path
from unicorn import Uc,UC_ARCH_MIPS,UC_MODE_MIPS32,UC_MODE_LITTLE_ENDIAN,UC_HOOK_CODE
from unicorn.mips_const import UC_MIPS_REG_SP,UC_MIPS_REG_FP,UC_MIPS_REG_RA,UC_MIPS_REG_GP,UC_MIPS_REG_PC
ROOT=Path(__file__).resolve().parent
SNAP=ROOT.parent/'20261113-new-rival-operation/encoded/evidence/source/opened-snapshots-20261028/TOWN0001-ci-main-34-single.ram.zlib'
S=0x12b2f8;SP=0x801f0000;STOP=0x80001000
def sha(b):return hashlib.sha256(b).hexdigest()
def put(n,v):(ROOT/n).write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n')
def main():
 ap=argparse.ArgumentParser();ap.add_argument('archive',type=Path);a=ap.parse_args()
 expected=json.loads((ROOT.parent.parent/'archives/20261103-r2/manifest.json').read_text())['sha256'];assert sha(a.archive.read_bytes())==expected
 with zipfile.ZipFile(a.archive) as z:exe=z.read('algorithm-analysis/source/SLPS_007.82')
 assert sha(exe)=='d6a167a1c9e0fe98d7e44e12968caa489ac3eb7ed3b9e46012a188af8432b1fd'
 base=zlib.decompress(SNAP.read_bytes());assert len(base)==0x200000
 def raw(lo,hi):return exe[lo-0x80010000+2048:hi-0x80010000+2048]
 ranges=[(0x80052270,0x80052410),(0x80052a88,0x80052d00),(0x800645ac,0x800645d8),(0x800234a0,0x800234e8),(0x80029444,0x8002a8e0),(0x8002a8e0,0x8002bd54),(0x8002bd54,0x8002e13c)]
 proofs=[]
 for lo,hi in ranges:
  b=raw(lo,hi);assert base[lo&0x1fffffff:hi&0x1fffffff]==b
  proofs.append(dict(start=hex(lo),end_exclusive=hex(hi),sha256=sha(b)))
 # Exact branch/call words relevant to newly connected presentation path.
 expected_words={0x800523e4:0x0c014aa2,0x80052a98:0x2404003a,0x80052c40:0x28430078,0x80052c54:0x0c006297,0x80052c80:0x0c01916b,0x80052cac:0x30620060,0x80052cb8:0x0c019154,0x80029444:0x24020001,0x8002944c:0xac22da00}
 for addr,w in expected_words.items():assert int.from_bytes(raw(addr,addr+4),'little')==w,hex(addr)
 put('source-words.json',{hex(lo):[hex(int.from_bytes(raw(pc,pc+4),'little')) for pc in range(lo,hi,4)] for lo,hi in ranges[:4]})
 u=Uc(UC_ARCH_MIPS,UC_MODE_MIPS32|UC_MODE_LITTLE_ENDIAN);u.mem_map(0,0x200000);u.mem_write(0,base);u.reg_write(UC_MIPS_REG_GP,0x800cd6c4)
 def rd(a,n):return bytes(u.mem_read(a&0x1fffffff,n))
 def wr(a,v):u.mem_write(a&0x1fffffff,struct.pack('<I',v&0xffffffff))
 def word(a):return struct.unpack('<i',rd(a,4))[0]
 for addr,v in [(0xcd93c,44640),(0xce608,1),(0xce60c,8),(0xce610,4),(0xce614,0),(0xce618,0)]:wr(addr,v)
 calls=[]
 for entry in [0x80029444,0x8002a8e0,0x8002bd54]:
  frame=SP-0x40 if entry==0x80029444 else SP
  for r,v in [(UC_MIPS_REG_SP,frame),(UC_MIPS_REG_FP,frame),(UC_MIPS_REG_RA,STOP)]:u.reg_write(r,v)
  if entry==0x80029444:
   wr(frame+0x3c,STOP);wr(frame+0x38,SP);wr(frame+0x30,0);u.mem_write((frame+0x34)&0x1fffffff,b'\0\1\1')
  prior=rd(S,50800);summary=rd(0xce61c,1720);cash=[word(0xcd9f8+4*j) for j in range(2)];rng=word(0xd6270);tick=word(0xcd93c);nested=[]
  def hook(uc,pc,n,c):
   w=int.from_bytes(rd(pc,4),'little')
   if w>>26==3:
    target=0x80000000|((w&0x3ffffff)<<2)
    if target not in nested:nested.append(target)
  h=u.hook_add(UC_HOOK_CODE,hook);u.emu_start(entry,STOP,count=3000000);u.hook_del(h);assert u.reg_read(UC_MIPS_REG_PC)==STOP
  after=rd(S,50800);first=[prior[j*5080+0xf04:j*5080+0xf24]==after[j*5080+0xf04:j*5080+0xf24] for j in range(4)];floor=[prior[j*5080+0x108:j*5080+0xb88]==after[j*5080+0x108:j*5080+0xb88] for j in range(4)]
  assert all(first) and all(floor) and summary==rd(0xce61c,1720) and word(0xcda00)==1 and tick==word(0xcd93c)
  if entry!=0x80029444:assert prior==after and not nested
  changes={str(j):[k for k in range(5080) if prior[j*5080+k]!=after[j*5080+k]] for j in range(4)}
  calls.append(dict(entry=hex(entry),stop=hex(STOP),first_customer_32bytes_preserved=first,floor_2688bytes_preserved=floor,all_store_pool_bytes_preserved=prior==after,summary_1720bytes_preserved=True,festival_switch=word(0xcda00),tick=tick,rng_before=rng,rng_after=word(0xd6270),company_cash_before=cash,company_cash_after=[word(0xcd9f8+4*j) for j in range(2)],changed_store_byte_offsets=changes,unique_nested_calls=[hex(x) for x in nested]))
 put('results.json',dict(presentation_control=dict(method='Static original branch reading, not whole presentation execution',dispatch_kind=2,entry='0x80052A88',sound_request=58,minimum_draw_wait_calls=120,wait_callee='0x80018A5C',termination_predicate='0x800645AC returns int(word800B8CB4==0 and word800B8CAC!=0); existing voice-state rule reused',when_predicate_zero='return via0x80052CE8',when_predicate_one='draw once then if word800CD7E0 &0x60 stop voice at64550 and play65000; otherwise clear input and repeat',direct_nonstack_store='Only word800CD7E0 input clear at52C7C/52CDC in52A88..52D00. This does not establish no writes in callees.',simulation_calls_in_direct_body=0),post_presentation=calls,main_order=['29334 finance (sets festival1 after presentation)','2A8E0 rival','2BD54 town','hour/minute0 gate','2619C demand'],rival_town_gate='Both require stage1/hour0/minute0; festival stage4 skips bodies',original_bounded_entries=3,gameplay_callee_replacements=0,whole_operating_updates=0,scope='Existing4storeRAM with diagnostic calendar; enter after presentation. No presentation/ordinaryUI/acquisition setup/natural festival/demand replay. First slots in saved input are not synthetic state6.'))
 put('source-provenance.json',dict(archive_sha256=expected,exe_sha256=sha(exe),snapshot=str(SNAP.relative_to(ROOT.parent)),snapshot_sha256=sha(base),verified_ranges=proofs,known_before=['Festival date/switch and main caller order','645AC generic voice-state predicate','Conditional out-of-catalog firstcustomer alias'],new_connections=['Festival-specific display timing/exit branch','Original post-presentation finance preserves alias operands in saved RAM','Stage4 bypasses actual rival/town update bodies']))
 print(json.dumps(dict(entries=len(calls),cash_before=calls[0]['company_cash_before'],cash_after=calls[0]['company_cash_after'],changed_bytes=sum(len(x) for x in calls[0]['changed_store_byte_offsets'].values()))))
if __name__=='__main__':main()
