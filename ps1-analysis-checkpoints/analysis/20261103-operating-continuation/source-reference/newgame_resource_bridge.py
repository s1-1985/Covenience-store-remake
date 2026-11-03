"""Native140E8/13F7C/13EAC/52D00 with CD SDK and GPU request endpoints.
This replays requestedpayloads into softwareVRAM; it isnot a GPU rasterizer.
"""
from check_machine import *
from caller_connection_harness import Memory
from cd_position import encode
from tim_transfer import PIXEL_RECTS,PALETTE_RECTS,requests
from unicorn import UC_HOOK_CODE
import json,hashlib,base64
R=Path(__file__).resolve().parent;BUF=0x80187e00;BUF_SIZE=0x14000
ASSETS={}
for row in json.loads((R/'newgame-sector-assets-20261016.json').read_text())['assets']:
 blob=(R/row['source_file']).read_bytes();sector=blob+base64.b64decode(row['padding_base64']);assert hashlib.sha256(blob).hexdigest()==row['sha256'] and hashlib.sha256(sector).hexdigest()==row['sector_sha256'];desc=encode(row['lba'])+b'\0'+struct.pack('<I',len(blob))+row['path'].replace('\\','/').split(';')[0].rsplit('/',1)[1].encode().ljust(16,b'\0');ASSETS[row['index'],row['mode']]={**row,'blob':blob,'sector':sector,'descriptor':desc}
for i,mode in ((6,8),(16,7),(17,9)):
 ASSETS[i,mode]={**ASSETS[i,0],'mode':mode}
CACHE_MODES=(0,7,8,9)
DESTINATIONS={0:BUF,11:BUF,6:0x801fd000,8:0x8015ea00,7:0x801f1600,9:0x80162e00,10:0x80183e00}
POINTERS={0:0x800cd890,11:0x800cd894,6:0x800cd858,8:0x800cd890,7:0x800cd890,9:0x800cd890,10:0x800cd888}
PALETTES=(0x80098ab8,0x800989f8,0x80098a38,0x80098a78)
def digest(b):return hashlib.sha256(b).hexdigest()
class NativeNewgameResources:
 def __init__(self,u,runner=None,cached=False,failures=(0,0,0,0),native_gpu=False,preserve_cache=False,stack_floor=None):
  self.u=u;self.m=Memory(u);self.runner=runner;self.failures=failures;self.hooks=[];self.callbacks={};self.returnhooks={};self.loads=[];self.transfers=[];self.rectangles=[];self.trace=[];self.pending=[];self.active=None;self.last=None;self.vram=bytearray(1024*512*2);self.cache_checks=[];self.sdk_wait_external=runner is not None;self.shadow=None;self.buffer_asset=None;self.shadows={};self.buffer_assets={};self.native_gpu=native_gpu;self.gpu_probe=None
  self.stack_floor=stack_floor;self.tim_skips=[]
  if not preserve_cache:self.m.write(0x8012ab60,bytes(32*24))
  if cached and not preserve_cache:
   for (index,mode),a in ASSETS.items():
    if mode==0:self.m.write(0x8012ab60+index*24,a['descriptor'])
  for a in(0x800140e8,0x80013f7c,0x80013eac,0x80052d00,0x80080ca0,0x80087b18,0x80085e10,0x800889c4,0x80088acc):self.hooks.append(u.hook_add(UC_HOOK_CODE,self.hook,begin=a,end=a))
  if not self.sdk_wait_external:self.hooks.append(u.hook_add(UC_HOOK_CODE,self.hook,begin=0x80089ca4,end=0x80089ca4))
  if native_gpu:
   from native_upload_probe import NativeUploadProbe
   self.gpu_probe=NativeUploadProbe(u,self.onreturn)
 def onreturn(self,a,fn):
  if self.runner:self.runner.onreturn(a,fn);return
  if a not in self.returnhooks:self.returnhooks[a]=self.u.hook_add(UC_HOOK_CODE,lambda z,a,n,d:self.flush(a),begin=a,end=a)
  self.callbacks.setdefault(a,[]).append(fn)
 def flush(self,a):
  while self.callbacks.get(a):self.callbacks[a].pop()()
 def returned(self,z,value):z.reg_write(UC_MIPS_REG_V0,value&0xffffffff);z.reg_write(UC_MIPS_REG_PC,z.reg_read(UC_MIPS_REG_RA))
 def hook(self,z,a,n,d):
  m=self.m;a0=z.reg_read(UC_MIPS_REG_A0);a1=z.reg_read(UC_MIPS_REG_A1);a2=z.reg_read(UC_MIPS_REG_A2);a3=z.reg_read(UC_MIPS_REG_A3)
  if a==0x800140e8:
   key=(a0,a1);assert key in ASSETS,('unexpected resource',key);asset=ASSETS[key];self.last=asset;cache=bytearray(m.read(0x8012ab60,768));hit=a1 in CACHE_MODES and int.from_bytes(cache[a0*24+4:a0*24+8],'little')!=0;dest=DESTINATIONS[a1];capacity=min(BUF_SIZE,0x200000-(dest&0x1fffffff),0x4000 if a1==10 else BUF_SIZE);assert len(asset['sector'])<=capacity;expected=bytearray(m.read(dest,capacity));expected[:len(asset['sector'])]=asset['sector'];expectedcache=bytearray(cache)
   if self.stack_floor is not None:
    assert dest<self.stack_floor;capacity=min(capacity,self.stack_floor-dest);assert len(asset['sector'])<=capacity;expected=expected[:capacity]
   if a1 in CACHE_MODES:expectedcache[a0*24:a0*24+24]=asset['descriptor']
   state=dict(asset=asset,counts=[0,0,0,0],hit=hit,expected=expected,destination=dest);self.active=state
   def checkload():
    assert m.word(POINTERS[key[1]])==dest and m.read(dest,capacity)==expected and m.read(0x800e42b0,24)==asset['descriptor'] and m.read(0x8012ab60,768)==expectedcache,('load',key)
    fs,fc,fr,fb=self.failures;assert state['counts']==[0 if hit else fs+1,fc+1+fr,fr+1,fb+1],(key,state['counts'],self.failures)
    self.loads.append([list(key),hit,list(state['counts']),digest(expected),digest(expectedcache)]);self.cache_checks.append([key,hit,digest(m.read(0x8012ab60,768))]);self.active=None
    for oldbase,oldshadow in list(self.shadows.items()):
     begin=max(oldbase,dest);end=min(oldbase+len(oldshadow),dest+len(asset['sector']))
     if begin<end:
      patched=bytearray(oldshadow);patched[begin-oldbase:end-oldbase]=asset['sector'][begin-dest:end-dest];self.shadows[oldbase]=bytes(patched)
    self.shadows[dest]=bytes(expected);self.buffer_assets[dest]=asset
    if dest==BUF:self.shadow=bytes(expected);self.buffer_asset=asset
   self.onreturn(z.reg_read(UC_MIPS_REG_RA),checkload);return
  if a==0x80013f7c:
   pixel=struct.pack('<4H',*PIXEL_RECTS[a0]);pal=struct.pack('<4H',*PALETTE_RECTS[a0])
   def checkrect():assert m.read(a1,8)==pixel and m.read(a2,8)==pal;self.rectangles.append([a0,list(PIXEL_RECTS[a0]),list(PALETTE_RECTS[a0])])
   self.onreturn(z.reg_read(UC_MIPS_REG_RA),checkrect);return
  if a==0x80052d00:
   rect=[a1,a2,a3,m.word(z.reg_read(UC_MIPS_REG_SP)+16)]
   if a0 in (0x800987f8,0x800988f8) and rect==[0,494,128,1]:
    blob=EXE.read_bytes();payload=blob[a0-0x80010000+2048:a0-0x80010000+2048+256]
    assert m.read(a0,256)==payload
    self.pending.append((struct.pack('<4H',*rect),a0,payload,{'kind':'EXE_scenario_palette','address':hex(a0)}));return
   index=m.byte(0x800cd948);assert index<4 and a0==PALETTES[index] and [a1,a2,a3,m.word(z.reg_read(UC_MIPS_REG_SP)+16)]==[48,492,32,1],('palette',index,hex(a0));blob=EXE.read_bytes();payload=blob[a0-0x80010000+2048:a0-0x80010000+2048+64];self.pending.append((struct.pack('<4H',48,492,32,1),a0,payload,{'kind':'EXE_palette','map':index}));return
  if a==0x80013eac:
   assert a0 in self.buffer_assets and self.buffer_assets[a0]['mode'] in CACHE_MODES,('TIMbuffer',hex(a0),self.last and [self.last['index'],self.last['mode']],hex(z.reg_read(UC_MIPS_REG_RA)))
   asset=self.buffer_assets[a0];previous=m.read(0x800e3eb8,28);pixel=struct.pack('<2I',a1,a2);pal=struct.pack('<2I',a3,m.word(z.reg_read(UC_MIPS_REG_SP)+16));expected=self.shadows[a0]
   # Later audio/other resource loads can overlap the last TIM. Original13EE8
   # tests the live magic and silently returns on non-TIM data. The last asset
   # tag alone is not evidence that its original header remains in this RAM.
   assert m.read(a0,4)==expected[:4],('TIM header shadow',hex(a0))
   desc,req=requests(expected,a0,pixel,pal,previous)
   if int.from_bytes(expected[:4],'little')!=16:self.tim_skips.append(dict(buffer=hex(a0),magic=int.from_bytes(expected[:4],'little'),last_tag=[asset['index'],asset['mode']],caller=hex(z.reg_read(UC_MIPS_REG_RA)),descriptor_sha256=digest(previous)))
   for j,(rect,ptr) in enumerate(req):
    _,_,w,h=struct.unpack('<4H',rect);size=w*h*2;off=ptr-a0;assert 0<=off and off+size<=len(expected);filepart=min(size,max(0,asset['bytes']-off));padpart=min(size-filepart,max(0,asset['sector_bytes']-max(asset['bytes'],off)));retained=size-filepart-padpart;origin=dict(kind='TIM_pixels' if j==0 else 'TIM_palette',resource=asset['index'],offset=off,file_bytes=filepart,sector_padding_bytes=padpart,retained_buffer_bytes=retained);self.pending.append((rect,ptr,expected[off:off+size],origin))
   def checktim():assert m.read(0x800e3eb8,28)==desc and not self.pending
   self.onreturn(z.reg_read(UC_MIPS_REG_RA),checktim);return
  if a==0x80080ca0:
   assert self.pending,('unexpected upload',hex(a0),hex(a1));rect,ptr,payload,origin=self.pending.pop(0);actualrect=m.read(a0,8);actual=m.read(a1,len(payload));assert actualrect==rect and a1==ptr and actual==payload,('upload',origin)
   x,y,w,h=struct.unpack('<4H',rect);assert x+w<=1024 and y+h<=512
   for yy in range(h):self.vram[((y+yy)*1024+x)*2:((y+yy)*1024+x+w)*2]=payload[yy*w*2:(yy+1)*w*2]
   self.transfers.append([list(struct.unpack('<4H',rect)),ptr,len(payload),digest(payload),origin])
   if not self.native_gpu:self.returned(z,0)
   return
  if a==0x80089ca4:self.trace.append(['wait',a0]);self.returned(z,0);return
  assert self.active,('CD call outside resource',hex(a));state=self.active;asset=state['asset'];fs,fc,fr,fb=self.failures
  if a==0x80087b18:
   assert (a0,bytes(m.read(a1,64)).split(b'\0')[0].decode())==(0x800e42b0,asset['path']);state['counts'][0]+=1;value=int(state['counts'][0]>fs)
   if value:m.write(a0,asset['descriptor'])
   self.trace.append(['search',asset['path'],value])
  elif a==0x80085e10:
   assert [a0,a1,a2]==[2,0x800e42b0,0] and m.read(a1,24)==asset['descriptor'];state['counts'][1]+=1;value=int(state['counts'][1]>fc);self.trace.append(['control',value])
  elif a==0x800889c4:
   assert [a0,a1,a2]==[len(asset['sector'])//2048,state['destination'],128];state['counts'][2]+=1;value=int(state['counts'][2]>fr)
   if value:m.write(a1,asset['sector'])
   self.trace.append(['read',a0,value,asset['sector_sha256']])
  elif a==0x80088acc:
   assert [a0,a1]==[1,0];state['counts'][3]+=1;value=int(state['counts'][3]<=fb);self.trace.append(['sync',value])
  self.returned(z,value)
 def dispose(self):
  if self.gpu_probe:self.gpu_probe.dispose()
  for h in self.hooks+list(self.returnhooks.values()):self.u.hook_del(h)
  self.hooks=[];self.returnhooks={}
