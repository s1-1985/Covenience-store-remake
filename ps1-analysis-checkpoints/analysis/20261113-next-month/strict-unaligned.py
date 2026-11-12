"""Strict little-endian MIPS-I merge loads/stores, including load-delay merging."""
import struct

def extend(Base):
 class MergeCpu(Base):
  def step(self):
   w=struct.unpack('<I',self.read(self.pc,4))[0];op=w>>26
   if op not in (34,38,42,46):return super().step()
   pc=self.pc;offset=pc-0x80010000+0x800
   assert self.read(pc,4)==self.exe[offset:offset+4],('modified merge instruction',hex(pc))
   self.visited[pc]=w
   rs,rt=(w>>21)&31,(w>>16)&31;imm=w&65535;imm=imm if imm<32768 else imm-65536
   address=(self.r[rs]+imm)&0xffffffff;aligned=address&~3;k=address&3
   memory=struct.unpack('<I',self.read(aligned,4))[0];value=self.r[rt];load=None
   if op in (34,38):
    # Paired LWL/LWR merge against the pending value when their Rt matches.
    if self.pending_load is not None and self.pending_load[0]==rt:value=self.pending_load[1]
    value=((value&(0x00ffffff>>(8*k)))|(memory<<(8*(3-k)))) if op==34 else ((value&((0xffffff00<<(8*(3-k)))&0xffffffff))|(memory>>(8*k)))
    load=(rt,value&0xffffffff)
   else:
    result=((memory&((0xffffff00<<(8*k))&0xffffffff))|(value>>(8*(3-k)))) if op==42 else ((memory&(0x00ffffff>>(8*(3-k))))|(value<<(8*k)))
    self.write(aligned,struct.pack('<I',result&0xffffffff))
   if self.pending_load is not None:
    reg,old=self.pending_load
    if reg:self.r[reg]=old&0xffffffff
   self.r[0]=0;self.pending_load=load;self.pc,self.npc=self.npc,(self.npc+4)&0xffffffff;self.steps+=1
 return MergeCpu
