"""Independent5CD60 prologue policy tofirst5CE34 iteration; BGM child explicit."""
from pathlib import Path
import struct
B=(Path(__file__).resolve().parent/'source/SLPS_007.82').read_bytes()
def run(m,call):
 for addr,value in((0x800cd8b8,0),(0x800cda00,0),(0x800cd9b4,-1),(0x8013796c,-1),(0x800cd7f4,0),(0x800cd9a4,0)):m.wordset(addr,value)
 m.byteset(0x801398bc,1);call(0x80065b3c,0,0,15,15);call(0x80062a4c,2,0)
 index=m.byte(0x800cd8a9);index=index if index<128 else index-256;identifier=struct.unpack_from('<I',B,0x80099864-0x80010000+2048+index*4)[0]
 call(0x80065100,identifier,0)
