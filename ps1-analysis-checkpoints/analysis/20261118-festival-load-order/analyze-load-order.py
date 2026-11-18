#!/usr/bin/env python3
"""R02 saved flag -> title demand reconstruction -> play clear, plus RNG context.
Only bounded source entries; excludes card transport, graphics and full main loop.
"""
import argparse,hashlib,importlib.util,json,struct,zipfile
from pathlib import Path
from unicorn import UC_HOOK_CODE,UC_HOOK_MEM_WRITE
from unicorn.mips_const import *
ROOT=Path(__file__).resolve().parent
HELPER=ROOT.parent/'20261117-festival-customer-state-data/analyze-festival-state.py'
spec=importlib.util.spec_from_file_location('prior_festival',HELPER);P=importlib.util.module_from_spec(spec);spec.loader.exec_module(P)
TARGET=P.S+2*5080+0xf04
PAYLOAD=0x187e00;SIZE=0x197ac

def sha(b):return hashlib.sha256(b).hexdigest()
def out(n,v):(ROOT/n).write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n')
def rd(u,a,n):return bytes(u.mem_read(a&0x1fffffff,n))
def unsigned(u,a):return struct.unpack('<I',rd(u,a,4))[0]
def state(u):return dict(festival=P.get(u,0xcda00),customer_hex=rd(u,TARGET,32).hex(),rng=hex(unsigned(u,0xd6270)),clock=P.get(u,0xcd93c),calendar=[P.get(u,0xce608+4*j) for j in range(5)],rebuild=rd(u,0x1398bc,1)[0],view_store=P.get(u,0x13796c))
def chunk(u,entry,end):
 for r,v in [(UC_MIPS_REG_SP,P.SP),(UC_MIPS_REG_FP,P.SP),(UC_MIPS_REG_RA,P.STOP)]:u.reg_write(r,v)
 h=u.hook_add(UC_HOOK_CODE,lambda uc,pc,n,c:uc.emu_stop(),begin=end,end=end)
 u.emu_start(entry,P.STOP,count=30000000);u.hook_del(h);assert u.reg_read(UC_MIPS_REG_PC)==end,(hex(entry),hex(u.reg_read(UC_MIPS_REG_PC)))
def main():
 ap=argparse.ArgumentParser();ap.add_argument('archive',type=Path);a=ap.parse_args()
 expected=json.loads((ROOT.parent.parent/'archives/20261103-r2/manifest.json').read_text())['sha256'];assert sha(a.archive.read_bytes())==expected
 with zipfile.ZipFile(a.archive) as z:exe=z.read('algorithm-analysis/source/SLPS_007.82');town=z.read('algorithm-analysis/source/TOWN0001.BIN')
 assert sha(exe)==P.EXE_SHA
 baseline,initial=P.fixture(exe,town);u=P.machine(exe,baseline)
 for j in [1,2]:P.put(u,P.S+5080*j+0xc78,0)
 P.put(u,0xcd93c,44640);P.call(u,0x80023c20);P.put(u,0xcda00,1);P.put(u,0xd6270,2)
 start=state(u);assert rd(u,TARGET,32)==bytes(32) and start['calendar']==[1,8,4,0,0]
 P.call(u,0x8006b81c);payload=rd(u,PAYLOAD,SIZE)
 check=struct.unpack_from('<I',payload,0x197a8)[0];assert check==sum(payload[:0x197a8])&0xffffffff
 assert struct.unpack_from('<I',payload,0x14ec8)[0]==1
 # Verify the original decoder, not an unrelated raw input left in live RAM.
 P.put(u,0xcda00,0);u.mem_write(TARGET,b'\x77')
 for j in range(5):P.put(u,0xce608+4*j,-99)
 before_decode=state(u);P.call(u,0x8006bc40);after_decode=state(u)
 assert after_decode['festival']==1 and rd(u,TARGET,32)==bytes(32) and after_decode['rng']=='0x2' and after_decode['calendar']==[-99]*5
 alias=[];flag_writes=[];calls=[]
 def mem(uc,access,addr,size,value,data):
  addr&=0x1fffffff;pc=uc.reg_read(UC_MIPS_REG_PC)
  if addr<TARGET+2 and addr+size>TARGET:alias.append(dict(pc=hex(pc),size=size,value=value&65535))
  if addr<0xcda04 and addr+size>0xcda00:flag_writes.append(dict(pc=hex(pc),size=size,value=value&0xffffffff))
 def code(uc,pc,n,data):
  word=unsigned(uc,pc)
  if word>>26==3:calls.append(dict(pc=hex(pc),target=hex(0x80000000|((word&0x3ffffff)<<2))))
 h=u.hook_add(UC_HOOK_MEM_WRITE,mem);c=u.hook_add(UC_HOOK_CODE,code)
 chunk(u,0x80012d44,0x80012d68);after_title=state(u)
 assert alias==[dict(pc='0x80026868',size=2,value=1)]
 assert after_title['festival']==1 and rd(u,TARGET,32)==b'\1'+bytes(31)
 assert after_title['calendar']==[1,8,4,0,0]
 assert [x for x in calls if x['pc'] in ['0x80012d58','0x80012d60']]==[dict(pc='0x80012d58',target='0x80023c20'),dict(pc='0x80012d60',target='0x8002619c')]
 before_prologue=rd(u,P.S,50800);chunk(u,0x8005cd60,0x8005cdcc);after_prologue=state(u)
 assert after_prologue['festival']==0 and after_prologue['rebuild']==1 and after_prologue['view_store']==-1
 assert rd(u,P.S,50800)==before_prologue and rd(u,TARGET,32)==b'\1'+bytes(31)
 assert flag_writes==[dict(pc='0x8005cd84',size=4,value=0)]
 u.hook_del(h);u.hook_del(c)
 # Main normally calls3CEAC before per-store customers. Check the actual intervening
 # RNG transition once; do not assume the prior isolated customer's RNG phase.
 before_notify=state(u);stores=rd(u,P.S,50800);queue=rd(u,0x137970,8000);draws=[]
 hook=u.hook_add(UC_HOOK_CODE,lambda uc,pc,n,c:draws.append(hex(pc)),begin=0x8007e648,end=0x8007e648)
 P.call(u,0x8003ceac);u.hook_del(hook);after_notify=state(u)
 seed=int(before_notify['rng'],16);expected_rng=(seed*1103515245+12345)&0xffffffff
 assert len(draws)==1 and unsigned(u,0xd6270)==expected_rng
 assert rd(u,P.S,50800)==stores and rd(u,0x137970,8000)==queue
 out('results.json',dict(input_scope='Controlled TOWN0001 initial rivals1/2 schedule0; nativecalendar fromclock44640; festival1 andseed2 supplied. Original encoder generated checksum-valid payload; not a save made viaordinary UI or anaturally elapsed festival.',save_load=dict(source=start,payload_size=SIZE,payload_sha256=sha(payload),checksum=check,checksum_valid=True,flag_payload_offset='0x14ec8',before_decode=before_decode,after_decode=after_decode),title_tail=dict(entry='0x80012d44',end_exclusive='0x80012d68',after=after_title,first_customer_writes=alias,top_native_calls=[x for x in calls if x['pc'] in ['0x80012d58','0x80012d60']]),play_entry=dict(entry='0x8005cd60',end_exclusive='0x8005cdcc beforegraphicscall',after=after_prologue,flag_writes=flag_writes,all_store_pool_bytes_preserved=True),intervening_notice=dict(entry='0x8003ceac',before=before_notify,after=after_notify,original_rng_draws=len(draws),all_store_pool_and_queue_bytes_preserved=True),original_entries=dict(bootstrap_town_metrics=3,boundary_metrics=1,encode_decode=2,title_tail=1,play_prologue=1,notice=1,total=9),whole_operating_updates=0,gameplay_callee_replacements=0,resource_loader_replacements=1,limitations=['Card UI/BIOS/read/checksum acceptance path not executed; host checks the original encoder checksum.','Title paths resource/graphics/reconstruction calls before12D44 not executed; do not claim whole load UI reachability or preservation by all skipped paths.','Play entry stops before graphics/BGM, no full main/normal admissions/per-store customer loop.','No corrupted record existed in the source payload; alias occurs during the selected reconstruction tail.','Seed2 is a controlled current-runtime input, not a saved deterministic seed.']))
 spans=[(0x80012d44,0x80012d78),(0x8005cd60,0x8005cdd4),(0x8006bbb8,0x8006bbd0),(0x8006bfd8,0x8006bff0),(0x8003ceac,0x8003cf80),(0x800234b8,0x800234fc),(0x80026844,0x80026878)]
 out('source-provenance.json',dict(exe_sha256=sha(exe),archive_sha256=expected,town_sha256=sha(town),helper_path=str(HELPER.relative_to(ROOT.parent)),helper_sha256=sha(HELPER.read_bytes()),code_ranges=[dict(start=hex(lo),end_exclusive=hex(hi),sha256=sha(exe[lo-0x80010000+2048:hi-0x80010000+2048])) for lo,hi in spans],prior_models=['20261103-operating-continuation/source-reference/save_codec.py','20261103-operating-continuation/source-reference/title_load_control.py','20261103-operating-continuation/source-reference/mainplay_entry.py','20261103-operating-continuation/source-reference/main_update_control.py'],novelty='Known individual serialization/title/main rules connected to original festival demand alias, resetordering and interveningRNG. Not new generic save/clock/RNG rules.'))
 print(json.dumps(dict(entries=9,saved_flag=1,loaded_flag=after_decode['festival'],title_customer_state=rd(u,TARGET,1)[0],play_flag=after_prologue['festival'],notice_rng_draws=len(draws))))
if __name__=='__main__':main()
