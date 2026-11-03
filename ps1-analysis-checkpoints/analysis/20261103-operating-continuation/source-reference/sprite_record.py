"""41630 raw 36-byte record. Index is full word; count increments independently."""
import struct
def record(initial,x,y,w,h,kind,u,v,clut,ref,rgb,mode):
 b=bytearray(initial);struct.pack_into('<I',b,0,0x1000000)
 for o,z in ((4,x),(6,y),(8,w),(10,h),(12,kind),(16,clut),(18,ref),(24,0),(26,0),(28,4096),(30,4096)):struct.pack_into('<H',b,o,z&65535)
 b[14:16]=bytes((u&255,v&255));b[20:23]=bytes(z&255 for z in rgb) if mode&255 else bytes((128,128,128));struct.pack_into('<I',b,32,0)
 return bytes(b)
