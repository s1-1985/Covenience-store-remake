"""Recovered140E8 modes1/2/4 metadata policy and independent SDK retry plan."""
MODES={1:dict(table=0x800985d0,cache=0x800e39c8,pointer=0x800cd81c),2:dict(table=0x800985f4,cache=0x800e3870,pointer=0x800cd814),4:dict(table=0x80098618,cache=0x800e3798,pointer=0x800cd810)}

def destination(index,mode):
 if mode==2:return 0x80187e00
 if mode==1:return 0x8016c200 if index==7 else 0x80170600 if index==8 else 0x80180a00
 if mode==4:return 0x8016b600 if index==7 else 0x8016ee00 if index==8 else 0x80174200
 raise ValueError(mode)

def load_plan(index,mode,name,size,cached,failures):
 search,control,read,busy=failures;calls=[]
 if not cached:calls.extend(('search',name) for _ in range(search+1))
 sectors=((size+2047)&0xffffffff)>>11
 calls.extend(('control',2) for _ in range(control+1))
 for j in range(read+1):
  calls.append(('read',sectors,destination(index,mode),128))
  if j<read:calls.append(('control',2))
 for _ in range(busy):calls.extend([('sync',1),('wait',0)])
 calls.append(('sync',1))
 return calls
