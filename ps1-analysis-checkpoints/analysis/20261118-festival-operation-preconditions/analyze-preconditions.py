#!/usr/bin/env python3
"""Connect three R02 setup preconditions on an existing operating RAM input.
Original transaction/inventory/metrics/demand code; no UI or elapsed-days claim.
"""
import argparse,hashlib,json,struct,zipfile,zlib
from pathlib import Path
from unicorn import Uc,UC_ARCH_MIPS,UC_MODE_MIPS32,UC_MODE_LITTLE_ENDIAN,UC_HOOK_CODE,UC_HOOK_MEM_WRITE
from unicorn.mips_const import UC_MIPS_REG_SP,UC_MIPS_REG_FP,UC_MIPS_REG_GP,UC_MIPS_REG_RA,UC_MIPS_REG_PC,UC_MIPS_REG_A0,UC_MIPS_REG_A1,UC_MIPS_REG_A2,UC_MIPS_REG_A3,UC_MIPS_REG_V0
ROOT=Path(__file__).resolve().parent;S=0x12b2f8;SP=0x801f0000;STOP=0x80001000
SNAP=ROOT.parent/'20261113-new-rival-operation/encoded/evidence/source/opened-snapshots-20261028/TOWN0001-ci-main-34-single.ram.zlib'
def sha(b):return hashlib.sha256(b).hexdigest()
def put(n,x):(ROOT/n).write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n')
def main():
 ap=argparse.ArgumentParser();ap.add_argument('archive',type=Path);args=ap.parse_args();expected=json.loads((ROOT.parent.parent/'archives/20261103-r2/manifest.json').read_text())['sha256'];assert sha(args.archive.read_bytes())==expected
 z=zipfile.ZipFile(args.archive);exe=z.read('algorithm-analysis/source/SLPS_007.82');assert sha(exe)=='d6a167a1c9e0fe98d7e44e12968caa489ac3eb7ed3b9e46012a188af8432b1fd'
 compressed=SNAP.read_bytes();baseline=zlib.decompress(compressed);assert len(baseline)==0x200000
 def raw(a,n):return exe[a-0x80010000+2048:a-0x80010000+2048+n]
 ranges=[(0x8001b320,0x8001b678),(0x8001bd78,0x8001bf4c),(0x8001cbc4,0x8001ccc0),(0x8001de5c,0x8001e1c8),(0x800209f8,0x80021ad0),(0x80023c20,0x80024820),(0x8002619c,0x80027378),(0x80061214,0x800612a0),(0x80062cb4,0x80062cc4),(0x800691c0,0x800691f8)]
 for a,e in ranges:assert baseline[a&0x1fffffff:e&0x1fffffff]==raw(a,e-a),(hex(a),'RAMcode differs')
 u=Uc(UC_ARCH_MIPS,UC_MODE_MIPS32|UC_MODE_LITTLE_ENDIAN);u.mem_map(0,0x200000);u.mem_write(0,baseline);u.reg_write(UC_MIPS_REG_GP,0x800cd6c4)
 def rd(a,n):return bytes(u.mem_read(a&0x1fffffff,n))
 def word(a):return struct.unpack('<i',rd(a,4))[0]
 def hword(a):return struct.unpack('<H',rd(a,2))[0]
 def wr(a,v):u.mem_write(a&0x1fffffff,struct.pack('<I',v&0xffffffff))
 def pointer(j):return S+5080*j
 calls=[]
 def run(a,values=(),end=STOP,frame=SP):
  for r,v in [(UC_MIPS_REG_SP,frame),(UC_MIPS_REG_FP,frame),(UC_MIPS_REG_RA,STOP)]:u.reg_write(r,v)
  for r,v in zip((UC_MIPS_REG_A0,UC_MIPS_REG_A1,UC_MIPS_REG_A2,UC_MIPS_REG_A3),values):u.reg_write(r,v&0xffffffff)
  def stop_at_boundary(uc,pc,n,c):
   if pc==end:uc.emu_stop()
  hook=u.hook_add(UC_HOOK_CODE,stop_at_boundary,begin=end,end=end)
  u.emu_start(a,STOP,count=30000000);u.hook_del(hook);assert u.reg_read(UC_MIPS_REG_PC)==end,(hex(a),hex(u.reg_read(UC_MIPS_REG_PC)))
  ret=u.reg_read(UC_MIPS_REG_V0);ret=ret if ret<0x80000000 else ret-0x100000000;calls.append(dict(entry=hex(a),stop=hex(end)));return ret
 def operands():return dict(order=list(struct.unpack('<10i',rd(0xce61c,40))),slots=[dict(slot=j,owner=hword(pointer(j)+4),schedule=word(pointer(j)+0xc78),stock15=word(0xce65c+168*j+0x2c+60),invalid_stock=word(0xce65c+168*j-400)) for j in range(4)])
 before=operands();assert before['order'][0]==0 and before['slots'][2]['owner']==2 and before['slots'][3]['owner']==0x8003
 # Three existing preconditions: playerstores alreadyexist, targetisnot enemyHQ,
 # and original quotes fit actual current cash. Selection/confirmation UI excluded.
 target=pointer(3);rect=list(struct.unpack('<4i',rd(target+8,16)));cash_before=word(0xcd9f8);rival_before=word(0xcd9fc)
 land=run(0x8001dfd0,rect);assets=run(0x8001de5c,[target+0x80000000,0]);price=(land+assets)*2;assert price>0 and cash_before>=price and hword(target+4)&255!=1 and rd(target+2,1)==b'\0'
 frame=SP-0x38;wr(frame+0x18,target+0x80000000);wr(0xcd800,price);run(0x80061214,end=0x800612a0,frame=frame)
 assert hword(target+4)==3 and word(0xcd9f8)==cash_before-price and word(0xcd9fc)==rival_before+price
 acquisition=dict(target_slot=3,old_owner=0x8003,new_owner=hword(target+4),rect=rect,land=land,assets=assets,price=price,player_cash_before=cash_before,player_cash_after=word(0xcd9f8),rival_cash_before=rival_before,rival_cash_after=word(0xcd9fc),source_commit='0x80061214..0x800612A0',scope='Originalpayment/owner/account/staff/town/metrics block after a hypothetical validUIconfirmation; no UI decision injected ascallee return.')
 # Onlythe newly owned store gets schedule0. No rival schedule is overridden.
 schedules_before=[word(pointer(j)+0xc78) for j in range(4)];frame=SP-0x28;wr(frame+0x28,target+0x80000000);wr(frame+0x14,0);run(0x80062cb4,end=0x80062cc4,frame=frame)
 schedules_after=[word(pointer(j)+0xc78) for j in range(4)];assert schedules_after==[2,2,2,0]
 for a,v in [(0xce60c,8),(0xce610,4),(0xce614,0),(0xce618,0),(0xcda00,1),(0xd6270,2)]:wr(a,v)
 run(0x80023c20);before_inventory=operands();wr(0xd6270,2);selection_without_stock=run(0x80026a64,[0x800a1750,15,14]);assert selection_without_stock==-1
 # An actually presentfixture0 at10,2 permitsproduct15 accordingto itsrawlist.
 fixture_word=word(S+0x108+2*112+10*4)&0xffffffff;assert fixture_word&0x80000000 and (fixture_word>>12&1023)==0
 choices=struct.unpack('<12i',raw(0x80099f0c+84,48));assert 15 in choices
 frame=SP-0x70;wr(frame+0x10,15);wr(frame+0x14,frame+0x60);cash_pre_stock=word(0xcd9f8);run(0x800209f8,[S+0x80000000,10,2,10000],frame=frame);cost=word(frame+0x60);assert cash_pre_stock>=cost
 run(0x800691c0,end=0x800691f8,frame=frame);assert word(0xcd9f8)==cash_pre_stock-cost
 run(0x80023c20);after_inventory=operands();assert after_inventory['slots'][0]['stock15']>0 and after_inventory['slots'][3]['invalid_stock']==after_inventory['slots'][0]['stock15']
 prior_first=[rd(pointer(j)+0xf04,32) for j in range(4)];selected=[];writes=[];pending=[None]
 def selector(uc,a,n,c):
  if a==0x80026778:pending[0]=dict(x=uc.reg_read(UC_MIPS_REG_A1),y=uc.reg_read(UC_MIPS_REG_A2)) if uc.reg_read(UC_MIPS_REG_A0)==0x800a1750 else None
  elif a==0x80026780 and pending[0] is not None:
   v=uc.reg_read(UC_MIPS_REG_V0);selected.append(dict(**pending[0],store=v if v<10 else -1));pending[0]=None
 def memory(uc,access,a,n,v,c):
  a&=0x1fffffff
  for j in range(4):
   p=pointer(j)+0xf04
   if a<p+2 and a+n>p:writes.append(dict(pc=hex(uc.reg_read(UC_MIPS_REG_PC)),slot=j,address=hex(a),bytes=n,value_low16=v&65535))
 h=u.hook_add(UC_HOOK_CODE,selector,begin=0x80026778,end=0x80026780);w=u.hook_add(UC_HOOK_MEM_WRITE,memory,begin=S,end=S+50800-1);wr(0xd6270,2);run(0x8002619c);u.hook_del(h);u.hook_del(w)
 after_first=[rd(pointer(j)+0xf04,32) for j in range(4)]
 assert selected==[dict(x=39,y=10,store=-1),dict(x=15,y=14,store=3)]
 assert len(writes)==1 and writes[0]['pc']=='0x80026868' and writes[0]['slot']==3
 assert int.from_bytes(after_first[3][:2],'little')==(int.from_bytes(prior_first[3][:2],'little')+1)&65535
 assert after_first[3][2:]==prior_first[3][2:] and all(after_first[j]==prior_first[j] for j in range(3))
 put('results.json',dict(input_kind='Existingoperating RAM atclock24560 plus boundedoriginal transaction/stock/hour commit blocks. Festivalcalendar/switch/seed supplieddiagnostically. Not anatural fullUI/dayplaythrough.',baseline_operands=before,acquisition=acquisition,schedule=dict(before=schedules_before,after=schedules_after,chosen_index=0,choice_is_in_original_0_to_6_range=True,commit='0x80062CB4..0x80062CC4',only_changed_slot=3,all_rival_schedules_preserved=True),before_product_change=dict(operands=before_inventory,selector_profile144_cell15_14=selection_without_stock),product_change=dict(store=0,fixture=0,xy=[10,2],selected_product=15,listed_in_original_fixture_choices=True,computed_cost=cost,cash_before=cash_pre_stock,cash_after=word(0xcd9f8),source_stock='0x800209F8 amount10000',source_temporary_charge='0x800691C0..0x800691F8',scope='Originalstockandtemporary UIcharge; no editorfinalconfirm/ledgerfinish replay.'),after_product_change_operands=after_inventory,festival_invalid_selector_calls=selected,first_customer_writes=writes,first_customers_before=[x.hex() for x in prior_first],first_customers_after=[x.hex() for x in after_first],bounded_entries=calls,original_full_operating_updates=0,gameplay_callee_replacements=0))
 put('source-provenance.json',dict(exe_sha256=sha(exe),archive_sha256=expected,snapshot_path=str(SNAP.relative_to(ROOT.parent)),compressed_snapshot_sha256=sha(compressed),snapshot_sha256=sha(baseline),code_ranges_verified_against_original=[dict(start=hex(a),end_exclusive=hex(e),sha256=sha(raw(a,e-a))) for a,e in ranges],earlier_evidence=['../20261116-festival-profile-boundary-data/README.md','../20261117-festival-customer-state-data/README.md','../20261116-acquisition-sale-data/README.md'],known_before='Invalidschedule/stockalias formulas andtransaction/hour/product rules decoded; newcombinedoriginal-operation prerequisites withrivalhours preserved.'))
 print(json.dumps(dict(entries=len(calls),price=price,cost=cost,invalid_stock=after_inventory['slots'][3]['invalid_stock'],selected=selected,writes=writes),ensure_ascii=False))
if __name__=='__main__':main()
