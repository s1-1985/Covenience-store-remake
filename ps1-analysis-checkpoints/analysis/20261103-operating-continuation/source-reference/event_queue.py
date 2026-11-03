"""8003ECD8 complete reservation, 8003EF44 modes 1/2/3/default, 8005C79C reset."""
import struct
from recovered import i32,owner_rating
from town_growth import s8
BASE=0x80137970;STRIDE=160;SLOTS=50

def reserve(queue,kind,parameter,sound,mode,variant,text):
 mode=s8(mode);start=0 if mode==5 else 1
 for slot in range(start,50):
  k=slot*160
  if queue[k]:continue
  queue[k]=1;queue[k+1]=variant&255;queue[k+2]=mode&255
  struct.pack_into('<III',queue,k+132,kind&0xffffffff,parameter&0xffffffff,sound&0xffffffff)
  queue[k+4:k+124]=text[:120]
  return slot
 return -1

def reset(queue,state):
 for slot in range(50):queue[slot*160]=0
 state.update({0x80137968:0,0x8013796c:0,0x801398b0:0,0x801398b4:0,0x801398b8:0})

def sound_request(sound):
 if sound==-1:return []
 if sound in (100,101,119,110):return [{100:28,101:29,119:8,110:7}[sound]]
 return [sound] if sound<100 else []

def consume(queue,state,text,clock,stores=None,population=None):
 """Mode3 requires original store records and population aggregated from town data."""
 sounds=[]
 if state[0x801398b4]!=0:return text,sounds,None
 state[0x801398b0]=0
 for slot in range(50):
  k=slot*160
  if not queue[k]:continue
  state[0x801398b0]=slot
  kind,parameter,sound=struct.unpack_from('<iii',queue,k+132)
  state[0x800e3be4]=kind&0xffffffff;state[0x800e3be8]=parameter&0xffffffff
  if kind<7:text=bytes(queue[k+4:k+124])
  state[0x800cd7ec]=2 if kind==3 else 1 if kind in (1,2,4,5,6,7,8) else 0
  sounds=sound_request(sound);mode=s8(queue[k+2]);variant=s8(queue[k+1])
  if mode==1:
   state.update({0x800e3bd8:56,0x800e3bda:104,0x800e3bdc:17,0x800e3bde:6,0x800e3be0:0,0x801398b8:{4:280,5:390,6:360,7:1,8:1}.get(kind,60),0x801398b4:1})
  elif mode==2:
   early=(clock//69120+1<2 and (clock//5760)%12+1<3)
   curr1,prev1=state[0x800e3c28],state[0x800e3c2c];curr2,prev2=state[0x800da974],state[0x800da978]
   values=[curr1,0 if early else (curr1-prev1)&0xffffffff,curr2,0 if early else (curr2-prev2)&0xffffffff,state[0x800e36a8],(state[0x800e36a8]-state[0x800e36ac])&0xffffffff]
   for j in range(5):
    if values[j]==0x80000000:values[j]=0
   for j,value in enumerate(values):state[0x800e3620+j*4]=value
   state[0x801398b8]=240;state[0x801398b4]=1
  elif mode==3:
   if stores is None or population is None:raise ValueError('Mode3 needs stores and town population')
   result=owner_rating(stores,state[0x800cd930],population)
   for a,value in zip((0x800e3ba8,0x800e3bac,0x800e3bb0,0x800e3bb4,0x800e3bb8),(result['stores'],state[0x800cd930],result['annual_sales'],population,result['mean_rating'])):state[a]=value&0xffffffff
   for j,value in enumerate(result['parts']):state[0x800e3bc0+j*4]=value
   state[0x800cd80c]=result['total']
   mode_value=s8(state[0x800cd948])
   if result['total']==100 and mode_value in (2,3):
    state[0x800cd8a0]|=4 if mode_value==2 else 8
    state[0x800cd9b4]=mode_value
   state[0x801398b8]=240;state[0x801398b4]=1
  queue[k]=0
  return text,sounds,slot
 state[0x801398b0]=50
 return text,sounds,None
