"""Recovered 80064914 CD audio state machine; SDK results are explicit inputs.
Command numbers retained as numbers; no hardware timing assumptions.
"""
from recovered import i32
SELF=0x80064914

def step(s,sync_results,position_result,position_bytes):
 calls=[];results=iter(sync_results)
 if s['disabled']!=0:return calls
 def sync():
  value=next(results)&0xffffffff;calls.append(('sync',1));return value
 def command(n,p=None):calls.append(('command',n,p))
 def position():calls.append(('position',s['start']));return position_bytes
 status=s['status']
 if status&2:
  result=sync()
  if result==5:command(13,s['mode'])
  elif result==2:s['status']=4;command(14,b'\xc9')
 elif status&4:
  result=sync()
  if result==5:command(14,b'\xc9')
  elif result==2:s['status']=64;s['current']=s['start'];command(2,position())
 elif status&64:
  result=sync()
  if result==5:command(2,b'\xc9')
  elif result==2:s['status']=16;s['current']=s['start'];position();command(21)
 elif status&16:
  result=sync()
  if result==5:position();command(21)
  elif result==2:s['status']=32;command(12)
 elif status&32:
  result=sync()
  if result==5:s['status']=32;command(12)
  elif result==2:
   s['status']=1;s['current']=s['start'];position();command(6);s['delay']=20
 elif status&1:
  if s['delay']!=0:s['delay']=(s['delay']-1)&0xffffffff
  else:
   result=sync()
   if result==5:command(6);s['retry']=1
   elif result==2:
    if s['retry']==1:command(17);s['retry']=0
    elif i32(s['current'])>=i32(s['end']):command(11);s['status']=128
    else:
     calls.append(('read_position',))
     if i32(position_result)>0:s['current']=position_result&0xffffffff
     command(17);s['delay']=5
 else:
  if status&128:
   result=sync()
   if result==5:command(11)
   elif result==2:command(9);s['status']=8
  # Native fallthrough reads updated status and may poll a second time.
  if s['status']&8:
   result=sync()
   if result==5:command(9)
   elif result==2:
    if s['callback']:calls.append(('restore_callback',s['callback']))
    s['status']=0
 if s['callback'] and s['callback']!=SELF:calls.append(('callback',s['callback']))
 return calls
