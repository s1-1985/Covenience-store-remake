"""Only COP2 transfers and MVMVA4A486012 used by858BC/859CC.
Arithmetic interpreted in software, not PS1 hardware validation.
Reference: https://github.com/notaz/pcsx_rearmed/blob/master/libpcsxcore/gte.c
FLAG/timing not implemented; CFC2 and all other GTE commands reject.
"""
import struct
from unicorn import UC_HOOK_CODE
import unicorn.mips_const as regs
from cursor_control import s16
from recovered import i32

def vector_product(matrix,vector,clamp=False):
 m=struct.unpack_from('<9h',matrix);out=[sum(m[k*3+j]*s16(vector[j]) for j in range(3))>>12 for k in range(3)]
 return [max(-32768,min(32767,x)) for x in out] if clamp else out

def matrix_product(left,right):
 a=struct.unpack_from('<9h',left);b=struct.unpack_from('<9h',right);result=bytearray(left)
 vals=[max(-32768,min(32767,sum(a[i*3+k]*b[k*3+j] for k in range(3))>>12)) for i in range(3) for j in range(3)]
 struct.pack_into('<9h',result,0,*vals);struct.pack_into('<h',result,18,-1 if vals[8]<0 else 0)
 return bytes(result)

class GTEBridge:
 def __init__(self,u):
  self.c=[0]*32;self.d=[0]*32;self.commands=[];self.transfers=0
  self.handle=u.hook_add(UC_HOOK_CODE,self.step,begin=0x800858bc,end=0x80085a18)
 def step(self,u,a,size,data):
  word=struct.unpack('<I',bytes(u.mem_read(a&0x1fffffff,4)))[0];op=word>>26
  if op not in [0x12,0x32,0x3a]:return
  rt=(word>>16)&31;rd=(word>>11)&31;rs=(word>>21)&31;rr=getattr(regs,f'UC_MIPS_REG_{rt}')
  if op==0x12:
   if word==0x4a486012:
    m=struct.unpack('<10h',struct.pack('<5I',*[x&0xffffffff for x in self.c[:5]]))[:9];v=[s16(self.d[0]),s16(self.d[0]>>16),s16(self.d[1])];self.commands.append((a,list(m),v))
    for k in range(3):
     out=sum(m[3*k+j]*v[j] for j in range(3))>>12;self.d[25+k]=i32(out);self.d[9+k]=max(-32768,min(32767,out))
   elif rs==6:self.c[rd]=s16(u.reg_read(rr)) if rd==4 else u.reg_read(rr)
   elif rs==4:self.d[rd]=u.reg_read(rr)
   elif rs==0:u.reg_write(rr,self.d[rd]&0xffffffff)
   else:raise AssertionError(('unsupported COP2',hex(a),hex(word)))
  else:
   basereg=getattr(regs,f'UC_MIPS_REG_{rs}');address=(u.reg_read(basereg)+s16(word))&0x1fffffff
   if op==0x32:self.d[rt]=struct.unpack('<I',bytes(u.mem_read(address,4)))[0]
   else:u.mem_write(address,struct.pack('<I',self.d[rt]&0xffffffff))
  self.transfers+=int(word!=0x4a486012);u.reg_write(regs.UC_MIPS_REG_PC,a+4)
