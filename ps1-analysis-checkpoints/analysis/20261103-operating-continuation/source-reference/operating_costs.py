"""8001D8AC, D980, DB5C, DBE4, DD7C and daily expense debit fragment."""
import struct
from recovered import i32,truncdiv

def rword(b,a):return struct.unpack_from('<i',b,a)[0]
def hours(store,schedules):return sum(v!=0 for v in schedules[rword(store,0xc78)])
def run_hours(store,mode,schedules):return 24 if mode else hours(store,schedules)
def equipment_cost(store,mode,schedules,rates):
 n=run_hours(store,mode,schedules);total=0
 for y in range(rword(store,0x48)):
  for x in range(rword(store,0x44)):
   v=struct.unpack_from('<I',store,0x108+y*112+x*4)[0];kind=v>>12&1023
   if v&0x80000000 and kind<53:total=i32(total+i32(rates[kind]*n))
 return total

def fixture_cost(store,fixture,mode,schedules):return i32(rword(fixture,8)*run_hours(store,mode,schedules))
def staff_cost(store,staff,slot,mode,schedules):
 v=rword(staff,12)
 if not slot:v=truncdiv(i32(v*130),100)
 return i32(v*run_hours(store,mode,schedules))
def staff_total(store,staff,mode,schedules):
 total=0
 for slot,k in enumerate(struct.unpack_from('<3h',store,0xdd8)):
  if k!=-1:total=i32(total+staff_cost(store,staff[k],slot,mode,schedules))
 return total

def daily_debit(store,staff,schedules,rates,cash):
 word=lambda a,v:struct.pack_into('<I',store,a,v&0xffffffff)
 word(0xd88,equipment_cost(store,0,schedules,rates));word(0xd8c,staff_total(store,staff,0,schedules))
 side=struct.unpack_from('<H',store,4)[0]>>15
 cash[side]=i32(cash[side]-i32(rword(store,0xd88)+rword(store,0xd8c)+rword(store,0xd90)))
 return cash
