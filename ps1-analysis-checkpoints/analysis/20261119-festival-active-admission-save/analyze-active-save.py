#!/usr/bin/env python3
"""R02: native-created pending admission and post-festival save window.
Selected source blocks with explicit diagnostic setup, not ordinary UI replay.
"""
import argparse,hashlib,importlib.util,json,struct,zipfile
from pathlib import Path
from unicorn import UC_HOOK_CODE,UC_HOOK_MEM_WRITE
from unicorn.mips_const import *
ROOT=Path(__file__).resolve().parent
HELPER=ROOT.parent/'20261118-festival-empty-slot-lifecycle/analyze-empty-slot.py'
spec=importlib.util.spec_from_file_location('prior_empty',HELPER);E=importlib.util.module_from_spec(spec);spec.loader.exec_module(E);P=E.P
S=E.S;TARGET=S+0xf04;LOG=[]
def sha(b):return hashlib.sha256(b).hexdigest()
def save(n,d):(ROOT/n).write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n')
def rd(u,a,n):return E.rd(u,a,n)
def call(u,a):P.call(u,a);LOG.append({'entry':hex(a),'end':'original_return'})
def block(u,a,b,frame=None,args=()):
 f=P.SP if frame is None else frame
 for r,v in [(UC_MIPS_REG_SP,f),(UC_MIPS_REG_FP,f),(UC_MIPS_REG_RA,P.STOP)]:u.reg_write(r,v)
 for r,v in zip((UC_MIPS_REG_A0,UC_MIPS_REG_A1,UC_MIPS_REG_A2,UC_MIPS_REG_A3),args):u.reg_write(r,v)
 h=u.hook_add(UC_HOOK_CODE,lambda uc,pc,n,c:uc.emu_stop(),begin=b,end=b)
 u.emu_start(a,P.STOP,count=30000000);u.hook_del(h);assert u.reg_read(UC_MIPS_REG_PC)==b,(hex(a),hex(u.reg_read(UC_MIPS_REG_PC)))
 LOG.append({'entry':hex(a),'end':hex(b)})
def info(u):return {'clock':P.get(u,0xcd93c),'calendar':[P.get(u,0xce608+4*j) for j in range(5)],'festival':P.get(u,0xcda00)}
def post(u):
 f=P.SP-0x58;P.put(u,f+0x58,S+0x80000000);P.put(u,f+0x54,P.STOP);P.put(u,f+0x50,P.SP)
 handlers=[]
 h=u.hook_add(UC_HOOK_CODE,lambda uc,pc,n,c:handlers.append(P.HANDLERS[pc]) if pc in P.HANDLERS and pc!=0x80032c68 else None,begin=0x800329bc,end=0x80032c68)
 block(u,0x80032814,P.STOP,f);u.hook_del(h);return handlers

def main(archive):
 z=zipfile.ZipFile(archive);exe=z.read('algorithm-analysis/source/SLPS_007.82');town=z.read('algorithm-analysis/source/TOWN0001.BIN');assert sha(exe)==P.EXE_SHA
 base,_=P.fixture(exe,town);LOG.extend({'entry':hex(a),'scope':'reused_bootstrap'} for a in [0x8005c858,0x8001a0b8,0x80023c20])
 u=P.machine(exe,base)
 for j in [1,2]:P.put(u,P.S+5080*j+0xc78,0)
 P.put(u,0xcd93c,44640);call(u,0x80023c20);P.put(u,0xd6270,2);call(u,0x8002619c)
 assert rd(u,TARGET,32)==bytes(32) and P.get(u,0xcda00)==0
 P.put(u,0xcd8ec,2);u.mem_write(0x1398bc,b'\1');f=P.SP-0x40;P.put(u,f+0x24,S+0x80000000);P.put(u,f+0x18,0)
 block(u,0x80023670,0x800238ac,f)
 P.put(u,0xd6270,0);block(u,0x800319ac,0x80032814,args=[S+0x80000000])
 normal=E.view(u);assert (normal['state'],normal['profile'],normal['quantity'])==(1,60,2)
 assert normal['visitors']==normal['summary_present']==2 and normal['position']==[-1]*3
 ready=rd(u,0,0x200000);cases=[]
 for flag in [0,1]:
  u=P.machine(exe,ready);P.put(u,0xcda00,flag);P.put(u,0xd6270,2);writes=[]
  def mem(uc,access,a,n,v,c):
   a&=0x1fffffff
   if a<TARGET+2 and a+n>TARGET:writes.append({'pc':hex(uc.reg_read(UC_MIPS_REG_PC)),'bytes':n,'value':v&65535})
  h=u.hook_add(UC_HOOK_MEM_WRITE,mem);call(u,0x8002619c);u.hook_del(h)
  after_demand=E.view(u);handlers=post(u);after_loop=E.view(u)
  if flag:
   assert writes==[{'pc':'0x80026868','bytes':2,'value':2}]
   assert after_demand['state']==2 and after_demand['raw_hex'][2:]==normal['raw_hex'][2:]
   assert (after_loop['state'],after_loop['wanted'],after_loop['wallet'],after_loop['deadline'])==(2,255,0,0)
   assert after_loop['position']==[-1]*3 and after_loop['goal']==[-1]*3 and after_loop['route_hex']=='ff'*10
   assert 'entry' not in handlers
  else:
   assert not writes and (after_loop['state'],after_loop['wanted'],after_loop['wallet'],after_loop['deadline'])==(2,5,3000,44700)
   assert after_loop['position']==[0,0,1]
  cases.append({'festival':flag,'after_demand':after_demand,'after_one_post_spawn_loop':after_loop,'handlers':handlers,'first_record_demand_writes':writes})
 # Begin exactly after festival presentation, not by injecting flag1.
 # This source tail and frame layout are reused from the prior presentation report.
 u=P.machine(exe,ready);P.put(u,0xcd93c,44640);call(u,0x80023c20)
 f=P.SP-0x40;P.put(u,f+0x3c,P.STOP);P.put(u,f+0x38,P.SP);P.put(u,f+0x30,0);u.mem_write((f+0x34)&0x1fffffff,b'\0\1\1')
 block(u,0x80029444,P.STOP,f);after_tail=info(u);assert after_tail['festival']==1
 tail=rd(u,0,0x200000)
 # Retain flag through the first actual two-minute clock advance and finance gate.
 block(u,0x80023438,0x80023460);call(u,0x80023c20);before_finance=info(u);call(u,0x80029334);after_finance=info(u)
 assert before_finance==after_finance and after_finance['clock']==44642 and after_finance['festival']==1
 # Enter original post-menu selection dispatch with returned choice5 specified.
 # No card/UI function or return is stubbed; stop before 4EEB8 card interaction.
 u.reg_write(UC_MIPS_REG_V0,5);dispatch=[]
 h=u.hook_add(UC_HOOK_CODE,lambda uc,pc,n,c:dispatch.append(hex(pc)) if pc in {0x80060070,0x800601f0,0x80062484,0x80062494,0x8006b81c} else None)
 block(u,0x80060034,0x8006249c,P.SP-0x40);u.hook_del(h)
 payload=rd(u,0x187e00,0x197ac);check=struct.unpack_from('<I',payload,0x197a8)[0]
 assert check==sum(payload[:0x197a8])&0xffffffff and struct.unpack_from('<I',payload,0x14ec8)[0]==1
 encoded={'payload_sha256':sha(payload),'checksum':check,'saved_clock':struct.unpack_from('<I',payload,0x30)[0],'saved_festival':1,'source_dispatch':dispatch,'stop':'before card UI4EEB8, no physical card write claimed'}
 # Nonmidnight saved input -> original decode -> unconditional title rebuild.
 encoded_customer=E.view(u);call(u,0x8006bc40);decoded_customer=E.view(u)
 assert decoded_customer['raw_hex']==encoded_customer['raw_hex']
 P.put(u,0xd6270,2);writes=[]
 h=u.hook_add(UC_HOOK_MEM_WRITE,lambda uc,access,a,n,v,c:writes.append({'pc':hex(uc.reg_read(UC_MIPS_REG_PC)),'bytes':n,'value':v&65535}) if (a&0x1fffffff)<TARGET+2 and (a&0x1fffffff)+n>TARGET else None)
 block(u,0x80012d44,0x80012d68);u.hook_del(h);title_customer=E.view(u)
 assert writes==[{'pc':'0x80026868','bytes':2,'value':2}]
 assert title_customer['state']==2 and title_customer['raw_hex'][2:]==decoded_customer['raw_hex'][2:]
 nonmidnight_title={'saved_customer':encoded_customer,'decoded_customer':decoded_customer,'after_title_rebuild':title_customer,'first_record_writes':writes,'clock':P.get(u,0xcd93c),'rng_note':'seed2 explicitly supplied after decode; not a serialized RNG claim'}
 # Second endpoint only: source clock + calendar + source midnight reset.
 u=P.machine(exe,tail);P.put(u,0xcd93c,46078);block(u,0x80023438,0x80023460);call(u,0x80023c20);next_midnight=info(u)
 block(u,0x80029334,0x8002939c);after_reset=info(u)
 assert next_midnight['clock']==46080 and next_midnight['calendar']==[1,9,1,0,0] and after_reset['festival']==0
 save('results.json',{'target':'R02','native_normal_admission':normal,'active_record_comparison':cases,'save_window':{'after_original_festival_tail':after_tail,'first_nonmidnight_before_finance':before_finance,'after_finance':after_finance,'encoded_from_original_menu_dispatch':encoded,'nonmidnight_title_rebuild':nonmidnight_title,'next_midnight_before_reset':next_midnight,'after_original_midnight_reset':after_reset},'original_entry_log':LOG,'final_reproducer_entries':len(LOG),'whole_operating_updates':0,'gameplay_callee_replacements':0,'resource_loader_substitutions':1,'limits':['The first customer record is created by native ordinary admission; no customer bytes are injected or copied into its slot.','Schedules0 and RNG seeds are controlled. Festival switch1 is specified in active-record comparison; a natural festival UI trajectory is not established.','Post-spawn loops isolate existing records from further admissions. One loop per branch only; no permanent freeze or natural frequency claim.','Festival presentation is not run; save-window test begins at original post-presentation tail. Next-midnight endpoint clock46078 is specified, not a full day replay.','Title rebuild is entered after decode, excluding card/graphics before it. seed2 explicitly supplied; random state is not saved.',
'Menu returned choice5 is specified at original postselection dispatch. Whole menu/input/card/successful file write is not run.','No new direct source write to customer quantity/budget/position/deadline was introduced by this reproducer.']})
 spans=[('normal_admission',0x800319ac,0x80032814),('dispatch_and_entry',0x80032814,0x80032c6c),('festival_alias_write',0x80026844,0x80026878),('clock_and_finance_gate',0x80023438,0x800234ec),('festival_flag_gate',0x80029334,0x80029450),('menu_postselection',0x80060034,0x80060078),('menu_card_action',0x800601f0,0x80060204),('card_action_encoder',0x80062484,0x800624a4)]
 save('source-provenance.json',{'exe_sha256':sha(exe),'town_sha256':sha(town),'archive_sha256':sha(archive.read_bytes()),'helper_path':str(HELPER.relative_to(ROOT.parent)),'helper_sha256':sha(HELPER.read_bytes()),'source_ranges':[{'name':n,'start':hex(a),'end_exclusive':hex(b),'sha256':sha(exe[a-0x80010000+2048:b-0x80010000+2048])} for n,a,b in spans],'menu_jump_table_10b40':[hex(v) for v in struct.unpack_from('<6I',exe,0x10b40-0x10000+2048)],'known_before':['festival flag producer and codec offsets','isolated injected states change dispatch','normal admission fields and entry initialization'],'new_connections':['native-created pending admission -> demand alias -> entry initializer skipped','post-presentation source flag -> next two-minute finance gate -> original menu dispatch encoder','next source midnight clears retained flag before following events','nonmidnight44642 save/decode/title rebuild advances native-created first state1 to2']})
 print(json.dumps({'active_customer_control_budget':cases[0]['after_one_post_spawn_loop']['wallet'],'festival_customer_budget':cases[1]['after_one_post_spawn_loop']['wallet'],'saved_flag':encoded['saved_festival'],'next_midnight_flag':after_reset['festival'],'entries':len(LOG)}))
if __name__=='__main__':
 ap=argparse.ArgumentParser();ap.add_argument('archive',type=Path);main(ap.parse_args().archive)
