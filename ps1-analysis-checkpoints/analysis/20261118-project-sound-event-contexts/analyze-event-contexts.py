#!/usr/bin/env python3
"""R05: bounded original caller with changed active stores and annual notice.
Not a natural playthrough. No gameplay function replacement; one town CD loader
is substituted with the verified source bytes. Synthetic fields are explicit.
"""
import argparse, hashlib, importlib.util, json, struct, zipfile, zlib
from pathlib import Path
from unicorn import UC_HOOK_CODE, UC_HOOK_MEM_WRITE
from unicorn.mips_const import *
ROOT=Path(__file__).resolve().parent
PREVIOUS=ROOT.parent/'20261117-project-initialization-sound-data/analyze-project-sound.py'
SPEC=importlib.util.spec_from_file_location('prior_project_sound',PREVIOUS)
P=importlib.util.module_from_spec(SPEC);SPEC.loader.exec_module(P)
STORE=0x12b2f8;PROJECT=0xe3c00;ALIAS=P.ALIAS

def sha(b):return hashlib.sha256(b).hexdigest()
def output(name,obj):(ROOT/name).write_text(json.dumps(obj,ensure_ascii=False,indent=2)+'\n')
def read(u,a,n):return bytes(u.mem_read(a&0x1fffffff,n))
def signed(u,a):return struct.unpack('<i',read(u,a,4))[0]
def main():
 ap=argparse.ArgumentParser();ap.add_argument('archive',type=Path);args=ap.parse_args()
 archive_sha=json.loads((ROOT.parent.parent/'archives/20261103-r2/manifest.json').read_text())['sha256']
 assert sha(args.archive.read_bytes())==archive_sha
 with zipfile.ZipFile(args.archive) as z:
  exe=z.read('algorithm-analysis/source/SLPS_007.82');town=z.read('algorithm-analysis/source/TOWNPS.BIN');msg=z.read('algorithm-analysis/source/MSG00.OBJ')
 assert sha(exe)==P.EXE_SHA
 u=P.setup(exe);u.mem_write(0x187e00,town);P.put(u,0x800cd894,0x80187e00)
 resources=[]
 def resource(uc,a,size,data):
  if a==0x800140e8:
   resources.append([uc.reg_read(UC_MIPS_REG_A0),uc.reg_read(UC_MIPS_REG_A1)])
   uc.reg_write(UC_MIPS_REG_PC,uc.reg_read(UC_MIPS_REG_RA))
 h=u.hook_add(UC_HOOK_CODE,resource);u.reg_write(UC_MIPS_REG_A0,0);P.call(u,0x8001a0b8);u.hook_del(h)
 assert resources==[[0,11]]
 u.mem_write(0x183e00,msg)
 # New-map loading does not initialize the separately entered company name.
 name_source=ROOT.parent/"20261113-new-rival-operation/encoded/evidence/source/opened-snapshots-20261028/TOWN0001-ci-main-34-single.ram.zlib"
 name_ram=zlib.decompress(name_source.read_bytes());company_name=name_ram[0x12b2c8:0x12b2c8+40]
 assert bytes.fromhex("ff40") in company_name;u.mem_write(0x12b2c8,company_name)
 # Original reserved-land placement for one 2x2 police box, as in prior report.
 for y in [10,11]:
  for x in [10,11]:
   for reg,value in [(UC_MIPS_REG_A0,x),(UC_MIPS_REG_A1,y),(UC_MIPS_REG_A2,71),(UC_MIPS_REG_A3,0)]:u.reg_write(reg,value)
   P.call(u,0x8001f1c0)
 baseline=read(u,0,0x200000)
 cases=[dict(id='changed_last_active_store',annual=False,threshold=21,previous_sales=0,expected_alias=24,expected_sound=29),
        dict(id='annual_zero_same_threshold',annual=True,threshold=21,previous_sales=0,expected_alias=0,expected_sound=34),
        dict(id='annual_zero_default_threshold',annual=True,threshold=0,previous_sales=0,expected_alias=0,expected_sound=29),
        dict(id='annual_negative_diagnostic',annual=True,threshold=0,previous_sales=-1,expected_alias=-1,expected_sound=34),
        dict(id='annual_positive_default_threshold',annual=True,threshold=0,previous_sales=100,expected_alias=100,expected_sound=29)]
 results=[]
 for case in cases:
  u=P.setup(exe);u.mem_write(0,baseline)
  # Keep original PS store1 (height24); deactivate later rivals diagnostically.
  for j in range(2,10):u.mem_write(STORE+j*5080,b'\0')
  own=STORE+5080
  if case['annual']:
   flags=struct.unpack('<H',read(u,own+4,2))[0]&0x7fff;u.mem_write(own+4,struct.pack('<H',flags));P.put(u,own+0xd0c,case['previous_sales'])
   # Original reservation function, kind6 annual evaluation, no requested sound.
   for reg,value in [(UC_MIPS_REG_A0,6),(UC_MIPS_REG_A1,0),(UC_MIPS_REG_A2,0xffffffff),(UC_MIPS_REG_A3,3)]:u.reg_write(reg,value)
   P.put(u,P.S+16,0);P.call(u,0x8003ecd8)
   queue=read(u,0x137970,8000);slot=next(j for j in range(50) if queue[j*160]);assert queue[slot*160+2]==3
  else:slot=None
  rec=bytearray(read(u,PROJECT,32));struct.pack_into('<h',rec,0,0);struct.pack_into('<4i',rec,4,10,10,11,11);struct.pack_into('<H',rec,20,1);struct.pack_into('<h',rec,30,case['threshold']);u.mem_write(PROJECT,bytes(rec))
  before=read(u,PROJECT,32);P.put(u,ALIAS,0xdeadbeef);writes=[];points=[];notices=[];record_writes=[]
  def trace(uc,access,address,size,value,data):
   a=address&0x1fffffff;pc=uc.reg_read(UC_MIPS_REG_PC)
   if a<ALIAS+4 and a+size>ALIAS:writes.append(dict(pc=hex(pc),size=size,value=value&0xffffffff))
   if a<PROJECT+32 and a+size>PROJECT:record_writes.append(dict(pc=hex(pc),offset=a-PROJECT,size=size,value=value&0xffffffff))
  def point(uc,a,size,data):
   if a in [0x80023474,0x80023490,0x80023498,0x800292b4,0x800292ec]:points.append(dict(pc=hex(a),alias=signed(uc,ALIAS),notice_active=P.word(uc,0x1398b4)))
   if a==0x800292ec:notices.append(dict(kind=uc.reg_read(UC_MIPS_REG_A0),event=uc.reg_read(UC_MIPS_REG_A1),sound=uc.reg_read(UC_MIPS_REG_A2),mode=uc.reg_read(UC_MIPS_REG_A3)))
  u.hook_add(UC_HOOK_MEM_WRITE,trace);u.hook_add(UC_HOOK_CODE,point)
  P.call(u,0x8002346c,0x800234a0)
  compare=next(p for p in points if p['pc']=='0x800292b4')
  assert compare['alias']==case['expected_alias'] and len(notices)==1 and notices[0]['sound']==case['expected_sound'],(case,points,notices)
  assert writes[-1]['pc']==('0x8003f930' if case['annual'] else '0x80023f30')
  assert read(u,PROJECT,2)==b'\xff\xff'
  assert read(u,PROJECT+30,2)==before[30:32]
  assert all(not(e['offset']<32 and e['offset']+e['size']>30) for e in record_writes)
  queued=[]
  for j in range(50):
   entry=read(u,0x137970+160*j,160)
   if entry[0]:
    kind,event,sound=struct.unpack_from('<iii',entry,132)
    queued.append(dict(slot=j,kind=kind,event=event,sound=sound,mode=entry[2]))
  assert any(n['kind']==2 and n['event']==0 and n['sound']==case['expected_sound'] and n['mode']==1 for n in queued)
  results.append(dict(input=case,queued_after=queued,queue_slot=slot,alias_writes=writes,caller_checkpoints=points,completion_notification=notices[0],project_before=before.hex(),project_after=read(u,PROJECT,32).hex(),annual_notice_consumed=slot is not None and read(u,0x137970+160*slot,1)==b'\0',annual_notice_active=P.word(u,0x1398b4),evaluation_annual_sales=signed(u,0xe3bb0)))
 spans=[(0x8002346c,0x800234a0),(0x8003f4c0,0x8003f528),(0x8003f7fc,0x8003f968),(0x8003fe70,0x8003ff00),(0x800292a8,0x80029304)]
 proof=[]
 for a,b in spans:
  raw=exe[a-0x80010000+2048:b-0x80010000+2048];proof.append(dict(start=hex(a),end_exclusive=hex(b),sha256=sha(raw),hex=raw.hex()))
 output('results.json',dict(cases=results,original_entries=dict(town_load=1,reserved_cells=4,annual_reservations=4,caller_prefixes=5,total=14),original_operating_updates=0,gameplay_callee_replacements=0,resource_loader_replacements=1,scope='Injected state and pending completion, single caller prefix; no annual rollover, UI withdrawal/acquisition or natural elapsed days. Threshold21 and negative sales are explicitly diagnostic, not ordinary values established by this experiment.'))
 output('source-provenance.json',dict(exe_sha256=sha(exe),archive_sha256=archive_sha,townps_sha256=sha(town),message_sha256=sha(msg),company_name_source=str(name_source.relative_to(ROOT.parent)),company_name_source_sha256=sha(name_ram),company_name_hex=company_name.hex(),helper_path=str(PREVIOUS.relative_to(ROOT.parent)),helper_sha256=sha(PREVIOUS.read_bytes()),code_ranges=proof))
 print(json.dumps(dict(cases=len(results),sounds=[r['completion_notification']['sound'] for r in results],aliases=[r['caller_checkpoints'][-2]['alias'] for r in results],original_entries=14)))
if __name__=='__main__':main()
