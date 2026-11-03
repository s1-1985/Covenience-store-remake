"""Record actual original transfer-profile MSG296 daily display versus slot cost formula."""
from check_machine import *
from caller_connection_harness import Memory
from recovered import i32
from operating_costs import staff_cost
from unicorn import UC_HOOK_CODE
class SourceTransferWageMonitor:
 def __init__(self,u):
  self.u=u;self.checks=[]
  def observe(z,a,n,d):
   ra=z.reg_read(UC_MIPS_REG_RA);right=0x80074150<=ra<0x800752c0
   if not (0x80073100<=ra<0x800752c0) or z.reg_read(UC_MIPS_REG_A2)!=296:return
   m=Memory(z);index=m.word(0x800cd9c8 if right else 0x800cd9c4);row=m.word(0x800cd9b0 if right else 0x800cd9ac);p=m.word(0x800cda1c if right else 0x800cda18)
   sid=struct.unpack('<i',m.read(0x800e3ed8+index*12+row*4,4))[0];assert sid>=0
   person=m.read(0x80143ff8+sid*60,60);store=m.read(p,5080);schedule=struct.unpack_from('<i',store,0xc78)[0];hours=struct.unpack('<b',m.read(0x800cd750+schedule,1))[0];base=struct.unpack_from('<i',person,12)[0];value=i32(m.word(0x800e4000));assert value==i32(base*hours)
   schedules=[list(m.read(0x80099de5+45*j,24)) for j in range(7)]
   self.checks.append(dict(side='right' if right else 'left',store_slot=(p-0x8012b2f8)//5080,row=row,staff_id=sid,schedule=schedule,display_hours=hours,base=base,actual_MSG296_value=value,cost_if_assigned_to_slot=staff_cost(store,person,row,0,schedules),label='MSG296 original glyph preview reads yen/day; display excludes first-slot130 percent multiplier'))
  self.h=u.hook_add(UC_HOOK_CODE,observe,begin=0x8004e494,end=0x8004e494)
 def dispose(self):self.u.hook_del(self.h)
