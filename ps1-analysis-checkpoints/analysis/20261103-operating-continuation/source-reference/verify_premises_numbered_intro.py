"""Non-first-store original6DEA4..6DF8C intro fragment, text/input/packet proof."""
from caller_connection_harness import fixture,Memory
from category_frame_harness import CategoryFrameRunner,MESSAGES
from check_machine import *
from text_controls import ExpandBuffer,expand_stream
from text_render import render_selected
from window_tiles import window,apply_window
from input_wait import InputWait
from recovered import i32
from unicorn import UC_HOOK_CODE
import itertools,random,hashlib,json,gc
R=Path(__file__).resolve().parent;FP=0x801ed000
STREAMS=([0,32],[0,64],[0,0x1000,0,12,0,32])
def raw_words(m,address):
 out=[]
 for j in range(100):
  word=struct.unpack('<H',m.read(address+2*j,2))[0];out.append(word)
  if word==0x40ff:return out
 raise AssertionError('raw text terminator')
def compare(ident,style,bank,delay,pattern,held):
 u=fixture(0,0,0,style,(50000000,60000000),(1,2,3,4));m=Memory(u);r=random.Random(20261013+style)
 glyphs=r.randbytes(4096);win=r.randbytes(64*36);buffer=r.randbytes(1024);copy=r.randbytes(256);state=m.read(0x143fc0,12)
 for address,data in ((0xdcc80,glyphs),(0xe0fe0,win),(0x12aa00,buffer),(0xe3948,copy)):m.write(address,data)
 m.write(0xcda3c,struct.pack('<H',3));m.write(0xcd8e4,bytes(2));m.write(0xcda34,bytes(2));m.write(0xcda14,bytes(2));put(u,0x800cd9dc,6)
 put(u,FP+0x2c,ident);put(u,FP+0x24,0);m.write(FP+0x60,m.read(0x80010c44,10));u.reg_write(UC_MIPS_REG_SP,FP);u.reg_write(UC_MIPS_REG_FP,FP)
 raws=list(STREAMS[pattern])+[0]*100
 for address,value in ((0x800cd9cc,held),(0x800cd9c0,held),(0x800cd8fc,delay),(0x800cd990,0),(0x800d6270,0x12345678)):put(u,address,value)
 iw=InputWait(held,held,delay,0,raws,0x12345678,(struct.unpack('<H',m.read(0xcd7d0,2))[0],0))
 for polls in range(1,26):
  iw.poll()
  if iw.buttons&96:break
 else:raise AssertionError('fixture dismissal')
 ew=bytearray(win);apply_window(ew,0,window(48,48,14,4,0));count=3;flags=0
 texts=[(368,64,64,None),(271,80,64,raw_words(m,0x800b95d4)),(271,120,80,raw_words(m,0x800b95f4))]
 for index,x,y,words in texts:
  if words:
   source=struct.pack('<'+'H'*len(words),*words);copy=source+copy[len(source):]
  eb=ExpandBuffer(buffer,0);consumed=expand_stream(MESSAGES[index],eb,{'variable':{},'two':{}},{(0x400a,0):words} if words else {},0,ident);buffer=bytes(eb.data)
  codes=list(struct.unpack_from('<'+'H'*eb.pos,buffer,64));tail,n,state,flags=render_selected(codes,style,x,y,flags,state,glyphs[count*36:],False);glyphs=glyphs[:count*36]+tail;count+=n
 runner=CategoryFrameRunner(u,bank,{0x800656f8:[raws]});precleanup=[]
 def observe(z,a,n,d):
  assert m.read(0xdcc80,4096)==glyphs and m.read(0xe0fe0,len(win))==bytes(ew) and m.read(0x12aa00,1024)==buffer and m.read(0xe3948,256)==copy and m.read(0x143fc0,12)==state and m.read(0xcd8e4,2)==struct.pack('<H',flags)
  assert [struct.unpack('<H',m.read(a,2))[0] for a in (0xcda46,0xcda3c)]==[56,count];precleanup.append(count)
 h=u.hook_add(UC_HOOK_CODE,observe,begin=0x80065974,end=0x80065974)
 stop=u.hook_add(UC_HOOK_CODE,lambda z,a,n,d:z.emu_stop(),begin=0x8006df8c,end=0x8006df8c)
 u.emu_start(0x8006dea4,0,count=3000000);assert u.reg_read(UC_MIPS_REG_PC)==0x8006df8c and precleanup==[count],('fragment endpoint',hex(u.reg_read(UC_MIPS_REG_PC)),precleanup,count,len(runner.frames),runner.contexts)
 assert get(u,FP+0x24)==1 and get(u,0x800cd938)==ident and get(u,0x800cd9dc)==6
 assert [struct.unpack('<H',m.read(a,2))[0] for a in (0xcda14,0xcda34,0xcda3c,0xcda46)]==[0]*4
 assert [get(u,a) for a in (0x800cd9cc,0x800cd9c0,0x800cda28,0x800d6270)]==[iw.held,iw.edge,iw.buttons,iw.seed] and len(runner.frames)==iw.ticks and not runner.contexts
 row=[ident,style,bank,delay,pattern,held,iw.buttons,iw.ticks,polls,count,hashlib.sha256(glyphs+bytes(ew)+buffer+copy).hexdigest(),runner.frames]
 u.hook_del(h);u.hook_del(stop);runner.dispose();return row
if __name__=='__main__':
 rows=[]
 for args in itertools.product((2,10,32767),range(3),range(2),(1,3),range(3),(0,32)):
  rows.append(compare(*args))
  if len(rows)%36==0:print('passed',len(rows),flush=True);gc.collect()
 out=dict(total=len(rows),all_passed=True,frames_verified=sum(len(x[11]) for x in rows),cases=rows,raw_streams=STREAMS,limits=['Original6DEA4..6DF8C non-first-store state0 fragment with actualEXE header/raw text,MSG368 store number,67338/271 text wrappers,656F8/41374 raw input ->native packets ->65974 countersclear ->state1','216 cases: three controlled store numbers,three font styles,two buffers/delays,three raw streams,two initialheld states;32767 robustnessfixture not proven normal reachable storeid','Unlike41A60 firstintro,656F8 dismisses only newbutton bits32/64; direction/rotation bits keep waiting; doesnotinvoke65000/65040 itself','Independent fullglyph/window/text/rawcopy/font flags,count append,InputWait/RNG/frame stream/OT/allocation; original priorcount3 andmask6 are supplied preconditions','Fragment localheader/storeid supplied; whole6DD18 nonfirst path and normalboot remain, no GPU pixels/Unicode meaning claim'])
 (R/'premises-numbered-intro-verification.json').write_text(json.dumps(out,separators=(',',':')));print(json.dumps({k:v for k,v in out.items() if k not in ('cases','raw_streams')}))
