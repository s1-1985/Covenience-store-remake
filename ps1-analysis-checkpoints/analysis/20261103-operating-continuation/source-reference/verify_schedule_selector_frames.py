"""45FFC actual menu input/font/window/rect/cursor/audio/packet chains."""
from caller_connection_harness import fixture,Memory
from category_frame_harness import CategoryFrameRunner
from check_machine import *
from schedule_selector_control import run
from menu_generator_monitor import MenuGeneratorMonitor
from input_wait import InputWait
from cursor_control import render
from recovered import i32
from unicorn import UC_HOOK_CODE
import itertools,json,gc,hashlib
R=Path(__file__).resolve().parent
def seq(steps):return [0]+[v for step in steps for v in (step,0)]
STREAMS=(seq([0x4000,32]),seq([0x2000,0x4000,32]),seq([0x2000]*6+[0x4000,32]),seq([0x8000]*4+[0x4000,32]),seq([0x4000,0x2000,32]),seq([64,0x4000,32]),seq([32,0x4000,32]),seq([0xa000,0x4000,32]),seq([0x5000,32]),seq([0x4000,0x2000,0x8000,0x1000,0x2000,0x4000,32]),[0]+[0x2000]*20+seq([0x4000,32]),[0]+[0x4000]*10+seq([0x1000,0x8000,0x4000,32]))
TRACE={0x80018940:2,0x80017b18:3,0x800157b4:0,0x800155d0:2,0x800469a8:1,0x8004e938:2,0x800182d0:4,0x80041374:1,0x80065000:0,0x8004ea68:0}
def compare(style,bank,delay,pattern):
 u=fixture(0,0,0,style,(50000000,60000000),(0,0,0,0));m=Memory(u);put(u,0x800cd9dc,0);put(u,0x800cd8fc,delay);m.write(0xcda3c,bytes(2));m.write(0xcda34,bytes(2));m.write(0xcda14,bytes(2));m.write(0xcda46,bytes(2));put(u,0x800cd990,0);raws=list(STREAMS[pattern])+[0]*200
 v=machine();v.mem_write(0,bytes(u.mem_read(0,0x200000)));v.reg_write(UC_MIPS_REG_GP,0x800cd6c4);fp=0x801effc0;v.reg_write(UC_MIPS_REG_FP,fp);v.reg_write(UC_MIPS_REG_SP,fp)
 runners=[CategoryFrameRunner(z,bank,{}) for z in (u,v)];monitors=[MenuGeneratorMonitor(z,r) for z,r in zip((u,v),runners)];traces=[[],[]];inputs=[[],[]];hooks=[]
 for r in runners:r.contexts.append(dict(address=0x80045ffc,raws=raws,tick=0))
 for which,z in enumerate((u,v)):
  def observe(z,a,n,d,which=which):
   r=runners[which];args=[z.reg_read(reg) for reg in (UC_MIPS_REG_A0,UC_MIPS_REG_A1,UC_MIPS_REG_A2,UC_MIPS_REG_A3)[:TRACE[a]]]
   if a==0x800155d0:args[1]&=65535
   if a in (0x80017b18,0x800182d0):args[2]&=255
   traces[which].append([a,args])
   if a==0x80041374:
    tick=r.contexts[-1]['tick'];iw=InputWait(get(z,0x800cd9cc),get(z,0x800cd9c0),i32(get(z,0x800cd8fc)),get(z,0x800cd990),raws[tick:],get(z,0x800d6270),(struct.unpack('<H',Memory(z).read(0xcd7d0,2))[0],struct.unpack('<H',Memory(z).read(0xcd8e4,2))[0]));iw.poll()
    def check():assert r.contexts[-1]['tick']==tick+iw.ticks and [get(z,a) for a in (0x800cd9cc,0x800cd9c0,0x800cda28,0x800cda0c,0x800d6270)]==[iw.held,iw.edge,iw.buttons,iw.directions,iw.seed];inputs[which].append([iw.buttons,iw.directions,iw.ticks,iw.seed])
    r.onreturn(z.reg_read(UC_MIPS_REG_RA),check)
   if a==0x8004e938:
    want=render(Memory(z).read(0xdae38,40),args[0]-3,args[1]-3)
    def check():assert Memory(z).read(0xdae38,40)==want
    r.onreturn(z.reg_read(UC_MIPS_REG_RA),check)
  for a in TRACE:hooks.append((z,z.hook_add(UC_HOOK_CODE,observe,begin=a,end=a)))
 u.reg_write(UC_MIPS_REG_RA,0x80001000);u.emu_start(0x80045ffc,0x80001000,count=5000000);assert u.reg_read(UC_MIPS_REG_PC)==0x80001000;runners[0].flush(0x80001000)
 def child(a,*args):
  for reg,value in zip((UC_MIPS_REG_A0,UC_MIPS_REG_A1,UC_MIPS_REG_A2,UC_MIPS_REG_A3),args):v.reg_write(reg,value&0xffffffff)
  v.reg_write(UC_MIPS_REG_RA,0x80001000);v.emu_start(a,0x80001000,count=1000000);assert v.reg_read(UC_MIPS_REG_PC)==0x80001000;runners[1].flush(0x80001000);return i32(v.reg_read(UC_MIPS_REG_V0))
 answer,states=run(Memory(v),child);assert answer==i32(u.reg_read(UC_MIPS_REG_V0)) and traces[0]==traces[1] and inputs[0]==inputs[1] and monitors[0].checks==monitors[1].checks and runners[0].frames==runners[1].frames and runners[0].sounds==runners[1].sounds,('selector',style,bank,delay,pattern,answer,i32(u.reg_read(UC_MIPS_REG_V0)),[(i,a,b) for i,(a,b) in enumerate(zip(traces[0],traces[1])) if a!=b][:3])
 hashes=[]
 for a,n in ((0xcd700,0x380),(0xdae38,40),(0x14a180,32*36),(0xe0fe0,256*36),(0xdcc80,4096),(0x143fc0,12),(0x12aa00,1024)):
  x=Memory(u).read(a,n);y=Memory(v).read(a,n);assert x==y,('selector region',hex(a),[(i,b,c) for i,(b,c) in enumerate(zip(x,y)) if b!=c][:4]);hashes.append(hashlib.sha256(x).hexdigest())
 row=[style,bank,delay,pattern,answer,states,hashes,traces[0],inputs[0],monitors[0].checks,runners[0].frames,runners[0].sounds]
 for mon in monitors:mon.dispose()
 for r in runners:r.dispose()
 for z,h in hooks:z.hook_del(h)
 return row
if __name__=='__main__':
 rows=[]
 for args in itertools.product(range(3),range(2),(1,3),range(12)):
  rows.append(compare(*args))
  if len(rows)%24==0:print('passed',len(rows),flush=True);gc.collect()
 out=dict(total=len(rows),all_passed=True,frames_verified=sum(len(x[10]) for x in rows),cases=rows,raw_streams=STREAMS,limits=['Complete original45FFC ->raw41374/4152C/native text/window/rectangle/cursor/469A8/audio ->native packetstream/16OT/allocation ->return; independent whole navigation,InputWait and all producer buffers','144 fixtures: three fontstyles x2buffers x2poll delays x12 rawstreams; seven options start2 and wrap0..6; opposingdirections,longhold,row transitions','Button64 alone does not dismiss; button32 on top row ignored; bottom OK returns choice+1, bottomcancel returns0; direction processing up/down/right/left beforeconfirm','Native window32,48 16x6, MSG41/49/51/9/270/269 anddynamic42..48; index269 glyph unavailableUnicode semantics not inferred','Upper62BD8/62CFC resource/staff/prices and whole612CC normalreachability/hardware remain; this suite mask0 initially,no originaltown background'])
 (R/'schedule-selector-frames-verification.json').write_text(json.dumps(out,separators=(',',':')));print(json.dumps({k:v for k,v in out.items() if k not in ('cases','raw_streams')}))
