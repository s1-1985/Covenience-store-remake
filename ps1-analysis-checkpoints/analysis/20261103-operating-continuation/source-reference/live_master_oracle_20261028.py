"""Generalize the existing independent parent oracle to source multi-store/audio state."""
from main_update_native_oracle import *
from store_order import store_order
def run(u,invoke):
    stores=[bytearray(u.mem_read(0x12b2f8+j*5080,5080)) for j in range(10)]
    g=dict(clock=get(u,0x800cd93c),flags=struct.unpack('<H',u.mem_read(0xcd790,2))[0],index=i32(get(u,0x800cd8ec)),max=u.mem_read(0xcd994,1)[0],regen=u.mem_read(0x1398bc,1)[0])
    c=calendar((g['clock']+2)&0xffffffff);order,_=store_order(stores,-1);calls=[]
    enabled=struct.unpack('<b',u.mem_read(0xcd834,1))[0]
    channel=struct.unpack('<h',u.mem_read(0xcd7f8,2))[0];extra=struct.unpack('<h',u.mem_read(0xcd8d0,2))[0]
    def child(a,*args):
        put(u,0x800cd93c,g['clock']);put(u,0x800cd8ec,g['index']);u.mem_write(0xcd790,struct.pack('<H',g['flags']))
        for j,s in enumerate(stores):u.mem_write(0x12b2f8+j*5080,bytes(s))
        calls.append([a,[x&0xffffffff for x in args]]);result=invoke(a,*args)
        for j,s in enumerate(stores):s[:]=u.mem_read(0x12b2f8+j*5080,5080)
        g['flags']=struct.unpack('<H',u.mem_read(0xcd790,2))[0]
        # Original rival manager may rebuild the active-store list at this
        # boundary. The same master update iterates that rebuilt list.
        if a==0x8002a8e0:order[:]=store_order(stores,-1)[0]
        return result
    reason=update(stores,order,g,c[1],c[2],c[3],c[4],SCHEDULES,enabled,channel,extra,TONES,child)
    put(u,0x800cd93c,g['clock']);put(u,0x800cd8ec,g['index']);u.mem_write(0xcd790,struct.pack('<H',g['flags']));u.mem_write(0xcd994,bytes([g['max']]));u.mem_write(0x1398bc,bytes([g['regen']]))
    for j,s in enumerate(stores):u.mem_write(0x12b2f8+j*5080,bytes(s))
    return reason,calls
