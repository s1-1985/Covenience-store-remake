"""Meaning of terminal guard fields: calendar year cache and store serial allocator."""
from progression import terminal_guard
from town_mutation import place,rebuild_flags

def year_cache(clock):return (clock&0xffffffff)//69120+1
def increment_serial(value):return (value+1)&65535
def candidate_serial(value):return increment_serial(value)
def restore_serial_max(current,store_flags):
 owner=(store_flags>>15)&1;serial=store_flags&0x7fff
 old=(current[owner]+32768)%65536-32768
 if old<serial:current[owner]=serial
 return current

def activate_store(town,table,stores,index,seed):
 s=stores[index];kind=3 if s['flags']&0x8000 else 0
 if (s['flags']&255)>=2:kind+=1
 s['active']=1
 seed=place(town,s['rect'][0],s['rect'][1],kind,0,table,seed)
 rebuild_flags(town,stores)
 return seed,kind
