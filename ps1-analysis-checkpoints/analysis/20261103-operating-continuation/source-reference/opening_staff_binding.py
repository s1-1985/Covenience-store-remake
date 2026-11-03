"""Independent 716BC/71384/70F48 staff selection mutations (PS1 SLPS00782).
No payroll debit occurs in these three routines. UI and invalid IDs excluded.
Pool scans in the native code are unbounded: require a sentinel/matching ID.
"""
import struct
from recovered import i32
from staff_rest import enter_rest
SELECTED=0x8012ab48
POOL=0x8012b030
STAFF=0x80143ff8

def s16(m,a):return struct.unpack('<h',m.read(a,2))[0]
def hset(m,a,v):m.write(a,struct.pack('<H',v&65535))
def selected(m,row):return i32(m.word(SELECTED+4*row))
def pool_index(m,predicate):
 for j in range(14):
  if predicate(i32(m.word(POOL+4*j))):return j
 raise ValueError('Native scan would leave the 14-slot candidate array')

def assign(m,store,row,candidate):
 old=selected(m,row)
 if old!=-1:
  hset(m,STAFF+old*60,0)
  j=pool_index(m,lambda x:x==-1);m.wordset(POOL+4*j,old)
 m.wordset(SELECTED+4*row,candidate)
 if candidate!=-1:
  hset(m,STAFF+candidate*60,s16(m,store+4))
  j=pool_index(m,lambda x:x==candidate);m.wordset(POOL+4*j,-1)
  while i32(m.word(POOL+4*(j+1)))!=-1:
   if j>=13:raise ValueError('Native compaction outside 14 slots')
   m.wordset(POOL+4*j,m.word(POOL+4*(j+1)));m.wordset(POOL+4*(j+1),-1);j+=1

def remove(m,store,row):
 old=selected(m,row)
 if old!=-1:hset(m,STAFF+old*60,0)
 original=s16(m,store+0xdd8+row*2)
 if original!=-1:hset(m,STAFF+original*60,s16(m,store+4))
 j=pool_index(m,lambda x:x==-1);m.wordset(POOL+j*4,old)
 m.wordset(SELECTED+row*4,original)
 # Exact original scan: it continues after shifting, so adjacent duplicates
 # can be skipped. Last slot is reset on every outer iteration.
 for j in range(14):
  if i32(m.word(POOL+4*j))==original:
   for k in range(j,13):m.wordset(POOL+4*k,m.word(POOL+4*(k+1)))
  m.wordset(POOL+13*4,-1)

def commit(m,store,rest=None):
 table=m.read(0x800cd758,6)
 for row in range(3):
  old=s16(m,store+0xdd8+row*2)
  if old==-1 or old==selected(m,row):continue
  p=STAFF+old*60;hset(m,p,0);m.byteset(p+0x19,m.byte(p+0x18))
  state,x,y=struct.unpack('<bbb',m.read(p+0x28,3))
  if state and x!=-1 and y!=-1:m.wordset(store+0x108+y*112+x*4,0)
  m.byteset(p+0x28,0)
 for row in range(3):
  old=s16(m,store+0xdd8+row*2);new=selected(m,row)
  if old==new:continue
  hset(m,store+0xdd8+row*2,new);new=s16(m,store+0xdd8+row*2)
  if new==-1:continue
  p=STAFF+new*60;hset(m,p,s16(m,store+4));m.byteset(p+0x28,0);m.write(p+0x29,b'\xff\xff')
  kind=struct.unpack('<b',m.read(p+4,1))[0]
  idx=row*2+kind
  if not 0<=idx<6:raise ValueError('Native type lookup reads outside six-byte table')
  hset(m,p+6,struct.unpack('<b',table[idx:idx+1])[0])
  if rest is not None:rest(store,row,0)
  m.wordset(p+0x14,m.word(p+0x14)+1)

def native_rest_model(m,store,row,mode,dimensions,offsets):
 sid=s16(m,store+0xdd8+row*2);p=STAFF+sid*60
 w=i32(m.word(store+0x44));h=i32(m.word(store+0x48))
 words={(x,y):m.word(store+0x108+y*112+x*4) for y in range(h) for x in range(w)}
 ret,record=enter_rest(w,h,words,dimensions,row,mode,m.read(p,60),offsets)
 m.write(p,record);return ret
