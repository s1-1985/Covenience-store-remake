from check_machine import *
from customer_loop import update
from customer_spawn_core import spawn
from customer_milestones import update as milestone
from text_buffer import TextBuffer
from staff_loop_selected import update as staff_update
from staff_target_chain import target as staff_target
from customer_child_chain import child
from runtime_tables import runtime_product_images
from finance_close import word
from recovered import i32
import random,json
R=Path(__file__).resolve().parent;r=random.Random(78279);S=0x8012b2f8;T=0x80143ff8;M=0x800cecec;A=0x80168000
b=EXE.read_bytes();raw=lambda a,n:b[a-0x80010000+2048:a-0x80010000+2048+n];fixtures=[list(struct.unpack('<49i',raw(0x80099f0c+j*196,196))) for j in range(53)];products=[struct.unpack('<2i',raw(0x8009ce08+j*88,8)) for j in range(27)];images=runtime_product_images([list(struct.unpack('<12i',raw(0x8009ce14+j*88,48))) for j in range(27)]);di=list(struct.unpack('<4i',raw(0x8009940c,16)));outcomes={};choices={};frames=0
profiles=[bytearray(raw(0x800a09d0+j*24,24)) for j in range(144)]
seasons=[struct.unpack('<i',raw(0x8009ce44+j*88,4))[0] for j in range(27)]
dirs=[struct.unpack('<2i',raw(0x8009941c+j*8,8)) for j in range(4)]
calendar=list(struct.unpack('<48b',raw(0x80099d88,48)));times=raw(0x800a1bf4,(max(calendar)+1)*576);appearances=raw(0x800a1b44,176);generated={};notification_counts={'local':0,'global':0}

def actor_fixture(i):
 w=20;h=18;s=bytearray(5080);s[1]=7;s[0]=1;s[0xc77]=1;word(s,0x44,w);word(s,0x48,h);refs=[0,1,2]
 if i%13==0:refs[1]=-1
 if i%17==0:refs[2]=-1
 struct.pack_into('<3h',s,0xdd8,*refs);struct.pack_into('<H',s,4,(i%2)<<15);pool=[bytearray(r.randbytes(60)) for _ in range(35)];meta=bytearray(2948);summary=bytearray(168);word(meta,0,A);word(summary,4,100 if i%2 else 0)
 restkind=48+i%2;checkoutkind=[k for k,f in enumerate(fixtures) if f[0]&255==4][i%len([k for k,f in enumerate(fixtures) if f[0]&255==4])];shelf=[k for k,f in enumerate(fixtures) if f[3]>0 and f[0]&255 in (0,2,5,8)][i%len([k for k,f in enumerate(fixtures) if f[3]>0 and f[0]&255 in (0,2,5,8)])]
 for y in range(h//2):
  for x in range(w//2):s[0x50+y*14+x]=r.choice([0,1,4,5,6,10,11,14,16]) if i%3 else 0
 for y in range(26):
  for x in range(28):struct.pack_into('<h',meta,0x14+y*56+x*2,-2 if x<w and y<h else -1)
 for x,y,k in [(2,2,restkind),(10,2,checkoutkind),(12,10,shelf)]:
  fw,fh=fixtures[k][9:11]
  for yy in range(y,min(h,y+fh*2)):
   for xx in range(x,min(w,x+fw*2)):
    struct.pack_into('<h',meta,0x14+yy*56+xx*2,-1);word(s,0x108+yy*112+xx*4,120)
  word(s,0x108+y*112+x*4,0x80000000|k<<12|120)
 if i%4:
  fw,fh=fixtures[shelf][9:11]
  for yy in range(fh):
   for xx in range(fw):word(s,0x178+(10+yy*2)*112+(12+xx*2)*4,(i%30)<<24|(images[i%27][0]&1023)<<12)
 word(summary,0x18,2);word(summary,0x1c,2);word(summary,0x20,10);word(summary,0x24,2);summary[0x28]=r.choice([1,2,3,4]);word(s,0xc70,i%6)
 for slot in range(3):
  p=pool[slot];p[0x28]=1;p[0x29:0x2c]=bytes([10+slot,1,1]);p[0x2c:0x2f]=p[0x29:0x2c];p[0x2f:0x39]=b'\xff'*10;p[0x18]=100;p[0x19]=50;struct.pack_into('<h',p,6,slot)
  for off in range(0x1a,0x28):p[off]=[0,50,100][(i+slot)%3]
 word(s,0xc68,50);word(summary,8,[0,50,100][i%3])
 for k in range(27):word(summary,0x2c+k*4,50 if k==i%27 else 0);word(s,0xc7c+k*4,0)
 for j in range(20):
  off=0xf04+j*32;p=bytearray(32);p[0]=[1,2,3,4,5,0][(i+j)%6];p[1]=i%27;struct.pack_into('<h',p,2,(i*20+j)%144);struct.pack_into('<I',p,4,100);struct.pack_into('<h',p,8,[0,100,10000][j%3]);struct.pack_into('<h',p,0xa,100 if p[0]==3 else 0);p[0xc:0xf]=bytes([1+j%8,6+j//8,1]);p[0xf:0x1c]=b'\xff'*13;p[0x1c]=j%4;p[0x1d]=0;p[0x1e]=1+j%5;p[0x1f]=j
  if p[0]==1:p[0xc:0xf]=b'\xff'*3
  if p[0]==3 and j%2:p[0xc:0xf]=bytes([10,1,1]);p[0xf:0x12]=p[0xc:0xf]
  s[off:off+32]=p
 word(s,0x1188,998);word(summary,16,50)
 for j in range(144):struct.pack_into('<h',s,0xde4+j*2,5)
 seed=r.getrandbits(32);clock=(i*17)%100;flags=r.randrange(65536);cash=[i32(r.getrandbits(32)),i32(r.getrandbits(32))];u=machine()
 for a,data in [(S,s),(T,b''.join(pool)),(M,meta),(A,summary)]:u.mem_write(a&0x1fffffff,bytes(data))
 for a,v in [(0x800cd8ec,0),(0x800ce60c,1),(0x800d6270,seed),(0x800cd9f8,cash[0]),(0x800cd9fc,cash[1])]:put(u,a,v)
 u.mem_write(0xcd790,struct.pack('<H',flags))
 for j,row in enumerate(images):u.mem_write((0x8009ce14+j*88)&0x1fffffff,struct.pack('<12i',*row))
 other=[bytearray(5080) for _ in range(9)];struct.pack_into('<H',other[0],4,2);u.mem_write((S+5080)&0x1fffffff,b''.join(other))
 order=[0,1,-1]+[-1]*7
 for j,value in enumerate(order):put(u,0x800ce61c+4*j,value)
 total=9998;pending=0;eq=bytearray(8000);eb=bytes([255,64]+[0]*118);Q=0x80137970;B=0x800e4020
 for a,v in [(0x800ce610,1),(0x800ce614,12),(0x800cd930,total),(0x800cd8b8,pending),(0x800cd8c8,0)]:put(u,a,v)
 for a,data in [(Q,eq),(B,eb),(0x80183e00,(R/'source/MSG00.OBJ').read_bytes()),(0x8012b2c8,struct.pack('<5H',101,202,303,404,0x40ff))]:u.mem_write(a&0x1fffffff,bytes(data))
 tb=TextBuffer(eb,0,lambda a,n:bytes(u.mem_read(a&0x1fffffff,n)))
 es=s.copy();ep=[p.copy() for p in pool];em=meta.copy();ec=cash.copy();ef=flags;eseed=seed

 return u
