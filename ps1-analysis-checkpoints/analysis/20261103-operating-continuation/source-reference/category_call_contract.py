"""Four originalcaller slices around75514, preserving distinct financial/rollback policies."""
from recovered import i32
PATHS=[dict(start=0x8005dd04,ends=(0x8005ded0,),storeoff=0x18,argoff=0x24,stateoff=0x2c,cancelstate=5,acceptstate=4,backup=(0x1c,0x20),returnoff=0x28),dict(start=0x80061508,ends=(0x800616d8,),storeoff=0x28,argoff=0x20,stateoff=0x24,cancelstate=-1,acceptstate=2,backup=(0x14,0x18),returnoff=0x1c),dict(start=0x80063f84,ends=(0x80063e98,0x80064090),storeoff=0x1410,argoff=None,stateoff=None,backup=None,returnoff=0x20),dict(start=0x80060ab4,ends=(0x80060b5c,),storeoff=0x44,argoff=None,stateoff=None,backup=None)]
FEES=(0x800cd840,0x800cd7e4,0x800cd8d8,0x800cd998)
def run(mem,pathid,fp,call):
 p=PATHS[pathid];store=mem.word(fp+p['storeoff']);cash=mem.word(0x800cd9f8);capital=mem.word(0x800d8f68)
 if pathid<2:
  for off,value in zip(p['backup'],(cash,capital)):mem.wordset(fp+off,value)
 elif pathid==2:
  mem.wordset(0x800cd8b4,cash);mem.wordset(0x800cd8c4,capital);call(0x8007e57c,fp+0x28,store,5080)
 argument=1 if pathid==3 else 0 if pathid==2 else mem.word(fp+p['argoff']);answer=i32(call(0x80075514,store,argument))
 if pathid==3:mem.byteset(0x801398bc,1);return answer,p['ends'][0]
 mem.wordset(fp+p['returnoff'],answer)
 if pathid<2:
  mem.wordset(0x800cd9f8,mem.word(fp+p['backup'][0]));mem.wordset(0x800d8f68,mem.word(fp+p['backup'][1]))
 else:
  mem.wordset(0x800cd9f8,mem.word(0x800cd8b4));mem.wordset(0x800d8f68,mem.word(0x800cd8c4))
 if answer==-1:
  for a in FEES if pathid<2 else FEES[2:]:call(0x8001cbc4,store,i32(-mem.word(a)))
  if pathid==2:
   call(0x8007e57c,store,fp+0x28,5080);mem.write(store+0xc74,mem.read(fp+0x1400,3));return answer,p['ends'][0]
  mem.wordset(fp+p['stateoff'],p['cancelstate'])
 else:
  if pathid<2:call(0x8001ca7c,store,mem.word(0x800cd8e0),0);call(0x8001cbc4,store,mem.word(0x800cd978));mem.wordset(fp+p['stateoff'],p['acceptstate'])
  else:return answer,p['ends'][1]
 return answer,p['ends'][0]
