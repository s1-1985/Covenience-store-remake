"""Recovered23438 parent sequence using original children, explicit oracle scope."""
from check_machine import *
from main_update_control import update
from recovered import i32
from hud_display import calendar
R=Path(__file__).resolve().parent;B=EXE.read_bytes()
SCHEDULES=[B[0x80099de5-0x80010000+2048+j*45:0x80099de5-0x80010000+2048+j*45+24] for j in range(7)];TONES=struct.unpack_from('<16i',B,0x8009947c-0x80010000+2048)
def run(u,invoke):
 stores=[bytearray(u.mem_read(0x12b2f8+j*5080,5080)) for j in range(10)];g=dict(clock=get(u,0x800cd93c),flags=struct.unpack('<H',u.mem_read(0xcd790,2))[0],index=i32(get(u,0x800cd8ec)),max=u.mem_read(0xcd994,1)[0],regen=u.mem_read(0x1398bc,1)[0]);c=calendar((g['clock']+2)&0xffffffff);order=[0]+[-1]*9;calls=[]
 def child(a,*args):
  put(u,0x800cd93c,g['clock']);put(u,0x800cd8ec,g['index']);u.mem_write(0xcd790,struct.pack('<H',g['flags']))
  for j,s in enumerate(stores):u.mem_write(0x12b2f8+j*5080,bytes(s))
  calls.append([a,[x&0xffffffff for x in args]]);result=invoke(a,*args)
  for j,s in enumerate(stores):s[:]=u.mem_read(0x12b2f8+j*5080,5080)
  g['flags']=struct.unpack('<H',u.mem_read(0xcd790,2))[0];return result
 reason=update(stores,order,g,c[1],c[2],c[3],c[4],SCHEDULES,0,0,0,TONES,child)
 put(u,0x800cd93c,g['clock']);put(u,0x800cd8ec,g['index']);u.mem_write(0xcd790,struct.pack('<H',g['flags']));u.mem_write(0xcd994,bytes([g['max']]));u.mem_write(0x1398bc,bytes([g['regen']]))
 for j,s in enumerate(stores):u.mem_write(0x12b2f8+j*5080,bytes(s))
 return reason,calls
