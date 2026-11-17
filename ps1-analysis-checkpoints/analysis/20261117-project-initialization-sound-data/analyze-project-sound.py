#!/usr/bin/env python3
"""Original town initialization and project completion through native caller prefix.
Requires verified split archive restored from ../../archives/20261103-r2.
No BIOS, rendering, audio device, patched gameplay functions or long day loop.
"""
import argparse,hashlib,json,struct,zipfile
from pathlib import Path
from unicorn import Uc,UC_ARCH_MIPS,UC_MODE_MIPS32,UC_MODE_LITTLE_ENDIAN,UC_HOOK_CODE,UC_HOOK_MEM_WRITE
from unicorn.mips_const import UC_MIPS_REG_SP,UC_MIPS_REG_FP,UC_MIPS_REG_GP,UC_MIPS_REG_RA,UC_MIPS_REG_PC,UC_MIPS_REG_A0,UC_MIPS_REG_A1,UC_MIPS_REG_A2,UC_MIPS_REG_A3
ROOT=Path(__file__).resolve().parent;S=0x801f0000;ALIAS=(S-36)&0x1fffffff;PROJECT=0xe3c00
EXE_SHA='d6a167a1c9e0fe98d7e44e12968caa489ac3eb7ed3b9e46012a188af8432b1fd'
def sha(b):return hashlib.sha256(b).hexdigest()
def js(n,x):(ROOT/n).write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n')
def put(u,a,x):u.mem_write(a&0x1fffffff,struct.pack('<I',x&0xffffffff))
def word(u,a):return struct.unpack('<I',u.mem_read(a&0x1fffffff,4))[0]
def setup(exe):
 u=Uc(UC_ARCH_MIPS,UC_MODE_MIPS32|UC_MODE_LITTLE_ENDIAN);u.mem_map(0,0x200000);u.mem_write(0x10000,exe[2048:]);u.reg_write(UC_MIPS_REG_GP,0x800cd6c4);return u
def call(u,entry,stop=0x80001000):
 for r,v in [(UC_MIPS_REG_SP,S),(UC_MIPS_REG_FP,S),(UC_MIPS_REG_RA,0x80001000)]:u.reg_write(r,v)
 u.emu_start(entry,stop,count=2000000)
 assert u.reg_read(UC_MIPS_REG_PC)==stop,(hex(entry),hex(u.reg_read(UC_MIPS_REG_PC)))
def main():
 ap=argparse.ArgumentParser();ap.add_argument('archive',type=Path);args=ap.parse_args()
 archive_manifest=json.loads((ROOT.parent.parent/'archives/20261103-r2/manifest.json').read_text());assert sha(args.archive.read_bytes())==archive_manifest['sha256']
 z=zipfile.ZipFile(args.archive);exe=z.read('algorithm-analysis/source/SLPS_007.82');assert sha(exe)==EXE_SHA
 msg=z.read('algorithm-analysis/source/MSG00.OBJ');master=json.loads((ROOT.parent/'20261115-town-project-data/project-master.json').read_text())['rows']
 init=[];results=[];source_inputs=[];starts=[]
 # Bounded original start-record block: source writes, not a replay of menu selection.
 for row in master:
  u=setup(exe);u.mem_write(PROJECT,b'\xff\xff'+bytes(30));put(u,0x800cd8d4,0x800e3c00)
  frame=S-0xb0;put(u,frame+0x80,row['selection']//10);put(u,frame+0x84,row['selection']%10)
  width,height=row['footprint'];rect=[10,10,9+width,9+height];u.mem_write(0xe3658,struct.pack('<4i',*rect))
  u.reg_write(UC_MIPS_REG_SP,frame);u.reg_write(UC_MIPS_REG_FP,frame);u.hook_add(UC_HOOK_CODE,lambda *args:None);u.emu_start(0x8006af54,0x8006b03c,count=10000)
  # Unicorn MIPS can report last executed PC at a straight-line end boundary.
  assert u.reg_read(UC_MIPS_REG_PC) in (0x8006b038,0x8006b03c)
  rec=bytes(u.mem_read(PROJECT,32));assert struct.unpack_from('<h',rec)[0]==row['selection'] and list(struct.unpack_from('<4i',rec,4))==rect
  assert rec[2:4]==bytes(2) and rec[22:32]==bytes(10) and 4<=struct.unpack_from('<H',rec,20)[0]<=8
  starts.append(dict(selection=row['selection'],name=row['name'],record_after=rec.hex(),threshold=struct.unpack_from('<h',rec,30)[0],countdown=struct.unpack_from('<H',rec,20)[0],entry='0x8006af54',stop='0x8006b03c',scope='Original record-write basic blocks and RNG; UI, cost confirmation and land placement excluded.'))
 for mapname in ['TOWN0001','TOWN0002','TOWN0003','TOWNPS']:
  town=z.read('algorithm-analysis/source/'+mapname+'.BIN');source_inputs.append(dict(path='algorithm-analysis/source/'+mapname+'.BIN',bytes=len(town),sha256=sha(town)))
  u=setup(exe);u.mem_write(0x187e00,town);put(u,0x800cd894,0x80187e00);u.mem_write(PROJECT,b'\xa5'*32);resource_calls=[];init_writes=[]
  def resource(uc,a,size,ctx):
   if a==0x800140e8:
    resource_calls.append([uc.reg_read(UC_MIPS_REG_A0),uc.reg_read(UC_MIPS_REG_A1)])
    uc.reg_write(UC_MIPS_REG_PC,uc.reg_read(UC_MIPS_REG_RA))
  def record_write(uc,access,address,size,value,ctx):
   a=address&0x1fffffff
   if a<PROJECT+32 and a+size>PROJECT:init_writes.append(dict(pc=hex(uc.reg_read(UC_MIPS_REG_PC)),offset=a-PROJECT,size=size,value=value))
  h=u.hook_add(UC_HOOK_CODE,resource);w=u.hook_add(UC_HOOK_MEM_WRITE,record_write);u.reg_write(UC_MIPS_REG_A0,0);call(u,0x8001a0b8);u.hook_del(h);u.hook_del(w)
  record=bytes(u.mem_read(PROJECT,32));assert record==b'\xff\xff'+bytes(30) and resource_calls==[[0,11]]
  init.append(dict(map=mapname,before_hex='a5'*32,after_hex=record.hex(),resource_calls=resource_calls,project_writes=init_writes))
  u.mem_write(0x183e00,msg);baseline=bytes(u.mem_read(0,0x200000))
  for row in master:
   u=setup(exe);u.mem_write(0,baseline);width,height=row['footprint'];x,y=10,10
   # Reuse original reserved-land placement, but bypass menu, affordability and waiting days.
   for yy in range(y,y+height):
    for xx in range(x,x+width):
     for r,v in [(UC_MIPS_REG_A0,xx),(UC_MIPS_REG_A1,yy),(UC_MIPS_REG_A2,71),(UC_MIPS_REG_A3,0)]:u.reg_write(r,v)
     call(u,0x8001f1c0)
   pending=bytearray(u.mem_read(PROJECT,32));struct.pack_into('<h',pending,0,row['selection']);struct.pack_into('<4i',pending,4,x,y,x+width-1,y+height-1);struct.pack_into('<H',pending,20,1);u.mem_write(PROJECT,bytes(pending));assert pending[30:32]==b'\0\0'
   put(u,ALIAS,0xdeadbeef);alias_writes=[];record_writes=[];points=[];calls=[]
   def trace(uc,access,address,size,value,ctx):
    a=address&0x1fffffff;pc=uc.reg_read(UC_MIPS_REG_PC)
    if a<ALIAS+4 and a+size>ALIAS:alias_writes.append(dict(pc=hex(pc),address=hex(a),size=size,value=value&0xffffffff))
    if a<PROJECT+32 and a+size>PROJECT:record_writes.append(dict(pc=hex(pc),offset=a-PROJECT,size=size,value=value&0xffffffff))
   def point(uc,a,size,ctx):
    if a in [0x80023474,0x80023490,0x80023498,0x800292b4,0x800292ec]:
     points.append(dict(pc=hex(a),alias_value=struct.unpack('<i',uc.mem_read(ALIAS,4))[0],threshold=struct.unpack('<h',uc.mem_read(PROJECT+30,2))[0]))
    if a==0x800292ec:calls.append(dict(type=uc.reg_read(UC_MIPS_REG_A0),event=uc.reg_read(UC_MIPS_REG_A1),sound=uc.reg_read(UC_MIPS_REG_A2),flag=uc.reg_read(UC_MIPS_REG_A3),fifth=word(uc,uc.reg_read(UC_MIPS_REG_SP)+16)))
   u.hook_add(UC_HOOK_MEM_WRITE,trace);u.hook_add(UC_HOOK_CODE,point);call(u,0x8002346c,0x800234a0)
   end=bytes(u.mem_read(PROJECT,32));assert end[:2]==b'\xff\xff' and end[20:22]==b'\0\0' and end[30:32]==b'\0\0'
   assert len(calls)==1 and calls[0]['sound']==29 and calls[0]['type']==2
   assert alias_writes and alias_writes[-1]['value']==20
   assert all(e['pc']=='0x80023f30' and e['value']>0 for e in alias_writes)
   assert not any(e['offset']<32 and e['offset']+e['size']>30 for e in record_writes)
   assert {p['pc'] for p in points}=={'0x80023474','0x80023490','0x80023498','0x800292b4','0x800292ec'}
   results.append(dict(map=mapname,selection=row['selection'],facility=row['name'],footprint=row['footprint'],pending_before=pending.hex(),record_after=end.hex(),alias_writes=alias_writes,record_writes=record_writes,caller_checkpoints=points,completion_notification=calls[0],town_sha256_after=sha(bytes(u.mem_read(0x1398f0,24000))),clock=word(u,0x800cd93c),calendar=dict(stage=word(u,0x800ce610),hour=word(u,0x800ce614),subhour=word(u,0x800ce618))))
  print(mapname+': 18 original completions passed',flush=True)
 js('start-record-preservation.json',starts);js('initialization.json',init);js('completion-caller-results.json',results)
 spans=[('project_initializer',0x8001b004,0x8001b08c),('caller_prefix',0x80023438,0x800234a8),('metric_height_writer',0x80023ef0,0x80023f38),('completion',0x80029020,0x80029334),('project_record_start',0x8006af54,0x8006b03c),('save_record_copy',0x8006ba38,0x8006ba5c),('load_record_copy',0x8006be58,0x8006be7c)]
 for name,a,e in spans:(ROOT/'source'/f'{name}.bin').write_bytes(exe[a-0x80010000+2048:e-0x80010000+2048])
 js('source-ranges.json',dict(exe_sha256=EXE_SHA,archive_sha256=archive_manifest['sha256'],message_sha256=sha(msg),inputs=source_inputs,ranges=[dict(file='source/'+n+'.bin',start=hex(a),end_exclusive=hex(e),sha256=sha((ROOT/'source'/f'{n}.bin').read_bytes())) for n,a,e in spans]))
 js('summary.json',dict(original_town_loads=4,start_record_blocks=18,catalog_completions=72,natural_elapsed_days=0,original_main_prefix='0x8002346c..0x800234a0',gameplay_callee_replacements=0,resource_loader_replacements=4,sound_codes=sorted(set(r['completion_notification']['sound'] for r in results)),threshold_initialization='All32 project bytes zeroed, then selection=-1.',last_alias_writer='80023f30, last initial active store height20, survives event/predecessor/completion children in these cases.',scope='Original four-map initial states plus injected pending projects, at original initial clock. Not purchased via UI, not a natural playthrough; no annual/remodeled/save-import coverage. R05 remains open outside this scope.'))
if __name__=='__main__':main()
