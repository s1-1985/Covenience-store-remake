"""Rules grounded in 8003EAD4, 8002A864, 8005A228 and 8006D8EC."""
from recovered import i32
from town_growth import s8

def store_milestone(stores,mode,flags,pending):
 count=sum(bool(s['active']) and not s['flags']&0x8000 for s in stores[:10])
 if count%5:return count,flags,pending,False
 if count==10 and s8(mode)==1:return count,flags|2,1,False
 return count,flags,pending,True

def terminal_guard(cash,counter,short_counter,mode,pending):
 if i32(cash)<0 or i32(counter)>=99 or ((short_counter+32768)%65536-32768)>=99:return 255,4
 return mode&255,pending&0xffffffff

def menu_limit(flags):return 4 if s8(flags)==7 else 3

def presentation_plan(pending):
 if pending not in range(5):raise ValueError('Original table access only modeled for indices 0..4')
 return dict(scene=[0,1,2,2,3][pending],extra_flow=pending<4)
