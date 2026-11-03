"""Independent72DBC tentative swap /72774 cross-store staff commit."""
import struct
from opening_staff_binding import STAFF,s16,hset
S=0x8012b2f8;ORDER=0x800e4328;TEMP=0x800e3ed8

def swap(m):
 left=m.word(0x800cd9c4);right=m.word(0x800cd9c8);lr=m.word(0x800cd9ac);rr=m.word(0x800cd9b0)
 a=TEMP+left*12+lr*4;b=TEMP+right*12+rr*4
 av=m.word(a);m.wordset(a,m.word(b));m.wordset(b,av)

def commit(m,rest=None):
 count=m.word(0x800cd970);table=m.read(0x800cd758,6)
 for k in range(count):
  store=S+m.word(ORDER+k*4)*5080;m.wordset(0x800cda18,store)
  for row in range(3):
   old=s16(m,store+0xdd8+row*2);new=struct.unpack('<i',m.read(TEMP+k*12+row*4,4))[0]
   if old==-1 or old==new:continue
   p=STAFF+old*60;hset(m,p,0)
   state,x,y=struct.unpack('<bbb',m.read(p+0x28,3))
   if state and x!=-1 and y!=-1:m.wordset(store+0x108+y*112+x*4,0)
   m.byteset(p+0x28,0)
 for k in range(count):
  store=S+m.word(ORDER+k*4)*5080;m.wordset(0x800cda18,store)
  for row in range(3):
   old=s16(m,store+0xdd8+row*2);new=struct.unpack('<i',m.read(TEMP+k*12+row*4,4))[0]
   if old==new:continue
   hset(m,store+0xdd8+row*2,new);new=s16(m,store+0xdd8+row*2)
   if new==-1:continue
   p=STAFF+new*60;hset(m,p,s16(m,store+4));m.byteset(p+0x28,0);m.write(p+0x29,b'\xff\xff')
   kind=struct.unpack('<b',m.read(p+4,1))[0];hset(m,p+6,struct.unpack('<b',table[row*2+kind:row*2+kind+1])[0])
   if rest is not None:rest(store,row,0)
 # Validation follows the writes; this return does not roll them back.
 for k in range(count):
  if m.word(TEMP+k*12)==0xffffffff:return k+1
 return 0
