from check_machine import *
R=Path(__file__).resolve().parent;payload=EXE.read_bytes()
def raw(a,n):return payload[a-0x80010000+2048:a-0x80010000+2048+n]
DESCRIPTORS=[raw(0x80099f0c+k*196,196) for k in range(53)];IMAGES=[struct.unpack('<12i',raw(0x8009ce14+j*88,48)) for j in range(27)];ids=set()
for desc in DESCRIPTORS:
 w,h=struct.unpack_from('<ii',desc,36)
 for y in range(h):
  for x in range(w):ids.add(struct.unpack_from('<i',desc,44+y*12+x*4)[0])
TILES={z:struct.unpack('<4i',raw(0x8009c7a0+z*16,16)) for z in ids};rows=[]
PRODUCTS=[struct.unpack('<2i',raw(0x8009ce08+j*88,8)) for j in range(27)];FIXTURES=[list(struct.unpack('<49i',z)) for z in DESCRIPTORS]
