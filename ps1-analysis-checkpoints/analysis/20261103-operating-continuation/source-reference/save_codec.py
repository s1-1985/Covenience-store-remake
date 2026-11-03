"""8006B81C/8006BC40 fixed RAM snapshot payload; no memory-card transport."""
import struct
BASE=0x80187e00;CHECKSUM_OFFSET=0x197a8;SIZE=CHECKSUM_OFFSET+4
# (payload offset, RAM address, byte count), in exact original write order.
FIELDS=[(0,0x800cd948,1),(1,0x800cd8a0,1),(2,0x800cd8a8,1),(4,0x8012b2c8,40),(0x2c,0x800cd8d0,2),(0x30,0x800cd93c,4),(0x35,0x800cd8a9,1),(0x36,0x800cd834,1),(0x37,0x800cd836,1),(0x38,0x800cd835,1),(0x3c,0x800cd9f8,4),(0x40,0x800cd9fc,4),(0x44,0x800cd9a8,4),(0x48,0x800cd9a0,4),(0x4c,0x80137968,0x1f58),(0x1fa4,0x800cd98c,1),(0x1fa5,0x800cd8dc,1),(0x1fa8,0x800cd89c,4),(0x1fac,0x801398f0,24000),(0x7d6c,0x800cd904,4),(0x7d70,0x800cd994,1),(0x7d72,0x800cd9e0,2),(0x7d74,0x800cd9e2,2),(0x7d78,0x800e3c00,32),(0x7d98,0x80143ff8,2100),(0x85cc,0x800e3688,10),(0x85d8,0x800cd930,4),(0x85dc,0x800df080,32),(0x85fc,0x800da970,32),(0x861c,0x800d8f68,32),(0x863c,0x800e36a8,240),(0x872c,0x800e3c28,240),(0x881c,0x800e43d0,60),(0x8858,0x8012b2f8,50800),(0x14ec8,0x800cda00,4),(0x14ecc,0x800cd8b8,4),(0x14ed0,0x8013f6c0,0x48d8)]

def checksum(payload):return sum(payload[:CHECKSUM_OFFSET])&0xffffffff

def encode(payload,read):
 for offset,address,length in FIELDS:payload[offset:offset+length]=read(address,length)
 struct.pack_into('<I',payload,CHECKSUM_OFFSET,checksum(payload))
 return payload

def decode(payload,write):
 # Caller performs checksum acceptance. This routine itself accepts arbitrary bytes.
 for offset,address,length in FIELDS:write(address,bytes(payload[offset:offset+length]))

def valid(payload):return checksum(payload)==struct.unpack_from('<I',payload,CHECKSUM_OFFSET)[0]
