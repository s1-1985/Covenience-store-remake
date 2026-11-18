#!/usr/bin/env python3
"""Three previously unconnected state6 consequences, six short original calls.
Controlled inputs only. No natural festival, UI replay or day progression.
"""
import argparse,hashlib,json,struct,zipfile
from pathlib import Path
from unicorn import Uc,UC_ARCH_MIPS,UC_MODE_MIPS32,UC_MODE_LITTLE_ENDIAN,UC_HOOK_CODE
from unicorn.mips_const import UC_MIPS_REG_SP,UC_MIPS_REG_FP,UC_MIPS_REG_GP,UC_MIPS_REG_RA,UC_MIPS_REG_PC,UC_MIPS_REG_A0,UC_MIPS_REG_A1,UC_MIPS_REG_V0
ROOT=Path(__file__).resolve().parent;STORE=0x12b2f8;SP=0x801f0000;STOP=0x80001000
def sha(b):return hashlib.sha256(b).hexdigest()
def put(n,x):(ROOT/n).write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n')
def main():
 ap=argparse.ArgumentParser();ap.add_argument('archive',type=Path);args=ap.parse_args()
 manifest=json.loads((ROOT.parent.parent/'archives/20261103-r2/manifest.json').read_text());assert sha(args.archive.read_bytes())==manifest['sha256'];z=zipfile.ZipFile(args.archive)
 exe=z.read('algorithm-analysis/source/SLPS_007.82');assert sha(exe)=='d6a167a1c9e0fe98d7e44e12968caa489ac3eb7ed3b9e46012a188af8432b1fd'
 def raw(a,n):return exe[a-0x80010000+2048:a-0x80010000+2048+n]
 mode3=next(i for i in range(144) if raw(0x800a09d0+i*24+12,1)==bytes([3]));profile=raw(0x800a09d0+mode3*24,24)
 u=Uc(UC_ARCH_MIPS,UC_MODE_MIPS32|UC_MODE_LITTLE_ENDIAN);u.mem_map(0,0x200000);u.mem_write(0x10000,exe[2048:]);u.reg_write(UC_MIPS_REG_GP,0x800cd6c4)
 def wr(a,v):u.mem_write(a&0x1fffffff,struct.pack('<I',v&0xffffffff))
 def mem(a,n):return bytes(u.mem_read(a&0x1fffffff,n))
 def regs(frame):
  u.reg_write(UC_MIPS_REG_SP,frame);u.reg_write(UC_MIPS_REG_FP,frame);u.reg_write(UC_MIPS_REG_RA,STOP)
 calls=[]
 def run(entry,end=STOP):
  hit=[]
  def code(uc,a,n,c):
   if a==end:uc.emu_stop()
   w=int.from_bytes(uc.mem_read(a&0x1fffffff,4),'little')
   if w>>26==3:hit.append(dict(pc=hex(a),target=hex((a&0xf0000000)|((w&0x3ffffff)<<2))))
  h=u.hook_add(UC_HOOK_CODE,code);u.emu_start(entry,end,count=200000);u.hook_del(h);assert u.reg_read(UC_MIPS_REG_PC)==end,(hex(entry),hex(u.reg_read(UC_MIPS_REG_PC)))
  calls.append(dict(entry=hex(entry),stop=hex(end),direct_calls=hit));return hit
 base=bytearray(5080);base[0]=1;base[1]=0xa5;struct.pack_into('<ii',base,0x44,14,14);struct.pack_into('<i',base,0xc70,0);struct.pack_into('<3h',base,0xdd8,-1,-1,-1)
 p=bytearray(32);p[:2]=bytes([6,255]);struct.pack_into('<h',p,2,mode3);struct.pack_into('<hh',p,8,5678,1234);p[12:15]=bytes([2,2,1]);p[15:18]=b'\xff'*3;p[30]=2;base[0xf04:0xf24]=p
 floor=0x50+1*14+1;cell=0x108+2*112+2*4;struct.pack_into('<I',base,cell,(642<<12)|120)
 parking=[]
 for state in [6,0]:
  b=bytearray(base);b[0xf04]=state;u.mem_write(STORE,bytes(b));regs(SP);u.reg_write(UC_MIPS_REG_A0,STORE+0x80000000);run(0x80022bf4);ret=u.reg_read(UC_MIPS_REG_V0);assert ret==(2 if state else 0) and mem(STORE,5080)==bytes(b)
  parking.append(dict(state=state,profile=mode3,arrival_mode=3,quantity=2,returned_used_parking=ret,store_unchanged=True))
 put('parking-effect.json',dict(cases=parking,source_entry='0x80022BF4',source_metric_call='0x80023DB8 -> store_working_summary+0x14',conclusion='Invalid nonzero state6 still contributes quantity to parking use when its validprofile arrivalmode==3. Mode3 condition matters; not allstate6customers consume parking.',limits='Controlled input; not naturalfestivalreachability or entire subsequentstoreselector run.'))
 clerk=[]
 for tile in [0,16]:
  b=bytearray(base);b[floor]=tile;u.mem_write(STORE,bytes(b));regs(SP);u.reg_write(UC_MIPS_REG_A0,STORE+0x80000000);u.reg_write(UC_MIPS_REG_A1,0x80143ff8);run(0x80038224);ret=u.reg_read(UC_MIPS_REG_V0);assert ret==(0 if tile==0 else 1) and mem(STORE,5080)==bytes(b)
  clerk.append(dict(state=6,floor_tile=tile,customer_xy=[2,2],return_value=ret,meaning='relevantcustomerexists' if ret==0 else 'norelevantcustomers',store_unchanged=True))
 put('clerk-effect.json',dict(cases=clerk,source_entry='0x80038224',source_callers=['0x80037488','0x80038B78'],conclusion='State6passes state>=2 test; floor!=16 causes checkoutrelevantcustomer result0. Staff37490 thereby skips its no-customer targetclear branch; actualemployeepermanentbusy notestablished.',limits='Onlyoriginal predicate executed. No fullstaffassignment or service success claim.'))
 u.mem_write(STORE,bytes(base));frame=SP-0x40;wr(frame+0x40,STORE+0x80000000);regs(frame)
 hit=run(0x8007579c,0x80075930);assert not hit;cleared=mem(STORE,5080);expected=bytearray(base);expected[0xf04]=0;struct.pack_into('<I',expected,cell,120);assert cleared==bytes(expected)
 # Enter actual cancel-copy block after the UI has returned-1. The existing
 # parent snapshot is explicitly supplied; do not claim the UI was replayed.
 parent=SP-0x1410;u.mem_write((parent+0x28)&0x1fffffff,bytes(base));wr(parent+0x1410,STORE+0x80000000);regs(parent);hit=run(0x80064040,0x80064058);assert hit==[dict(pc='0x80064050',target='0x8007e57c')]
 restored=mem(STORE,5080);assert restored==bytes(base)
 put('editor-reset-and-cancel.json',dict(before=dict(customer_hex=p.hex(),store_sha256=sha(base),occupancy_word=(642<<12)|120),editor_entry_clear=dict(start='0x8007579C',stop='0x80075930',customer_hex=cleared[0xf04:0xf24].hex(),state=cleared[0xf04],wallet=struct.unpack_from('<h',cleared,0xf0c)[0],unsettled_cart=struct.unpack_from('<h',cleared,0xf0e)[0],occupancy_word=struct.unpack_from('<I',cleared,cell)[0],changed_offsets=[i for i,(a,b) in enumerate(zip(base,cleared)) if a!=b],store_sha256=sha(cleared)),cancel_restore=dict(start='0x80064040',stop='0x80064058',bytes=5080,original_memcpy='0x8007E57C',restored_state=restored[0xf04],store_sha256=sha(restored),all_bytes_restored=True),source_parent='0x80063FA4 snapshot ->0x80063FC4 editor ->0x80063FF8 cancelbranch ->0x80064050 restore',conclusion='Editorentry clear includesstate6 andremoves itsoccupancy imagebits; existingstorecancel restores entire5080byte snapshot includingstate6. Openingthen cancelling isnot a durable reset ofthisstate.',limits='Two isolated originalblocks plus originalmemcpy. Parent snapshot supplied directly; no UI/fee/ledger/confirm-success replay. No settlement/refund claim beyond rawcartbytes.'))
 spans=[(0x80022c78,0x80022cec),(0x80023db4,0x80023dcc),(0x800382a8,0x80038360),(0x80037480,0x800374bc),(0x80038b70,0x80038b94),(0x800757d0,0x8007582c),(0x80075900,0x80075914),(0x80063fa4,0x80063fcc),(0x80063ff0,0x80064000),(0x80064040,0x80064058)]
 put('source-evidence.json',dict(exe_sha256=sha(exe),archive_sha256=manifest['sha256'],mode3_profile=dict(id=mode3,address=hex(0x800a09d0+24*mode3),raw_hex=profile.hex()),raw_ranges=[dict(start=hex(a),end_exclusive=hex(e),sha256=sha(raw(a,e-a)),raw_hex=raw(a,e-a).hex()) for a,e in spans],existing_rule_sources=[dict(path=n,sha256=sha(z.read('algorithm-analysis/'+n))) for n in ['staff_work.py','customer_spawn_core.py']],known_before='Ordinaryparking/checkoutpredicate andeditor snapshot/cancel alreadydecoded. Newjoin is theseoperations appliedtoR02corruptedstate6; previousreport onlypostspawn/freeslot.'))
 put('summary.json',dict(processed_questions=3,original_cpu_calls=len(calls),calls=calls,original_full_operating_updates=0,original_gameplay_callee_replacements=0,natural_festival_reachability=False,android_code_changed=False,tracked_open_issues_resolved=0));assert len(calls)==6
 print(json.dumps(dict(processed_questions=3,original_calls=len(calls),parking=[x['returned_used_parking'] for x in parking],clerk=[x['return_value'] for x in clerk],cleared_state=cleared[0xf04],cancel_restored_state=restored[0xf04])))
if __name__=='__main__':main()
