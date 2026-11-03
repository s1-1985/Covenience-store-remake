"""Extend native menu packet verification with unscaled enabled/disabled tiled backgrounds."""
from category_frame_harness import *
from tiled_render_general import tiled_general
from scaled_background import scaled_background
from matrix_scale import scale_matrix
from gte_subset import GTEBridge,vector_product
class BackgroundCategoryRunner(CategoryFrameRunner):
 def __init__(self,*args,allow_scaled=False,**kwargs):
  super().__init__(*args,**kwargs);self.allow_scaled=allow_scaled;self.packet_capacity=144000 if allow_scaled else 65536
  if allow_scaled:self.bridge=GTEBridge(self.u)
 def dispose(self):
  if self.allow_scaled:self.u.hook_del(self.bridge.handle)
  super().dispose()
 def hook(self,u,a,n,d):
  if a!=0x80018a5c:return super().hook(u,a,n,d)
  c=self.contexts[-1] if self.contexts else None;raw=0
  if c:
   assert c['tick']<len(c['raws']),('raws exhausted',hex(c['address']),c['tick'],self.phase_entries,hex(u.reg_read(UC_MIPS_REG_RA)));raw=c['raws'][c['tick']];c['tick']+=1
  put(u,0x800cd9d8,raw);mask=get(u,0x800cd9dc);counts={addr:struct.unpack('<H',u.mem_read(addr&0x1fffffff,2))[0] for bit,base,addr,fix,depth in GROUPS if addr};links=[0xffffff]*16;stream=bytearray();draw=[]
  scale=struct.unpack('<h',u.mem_read(0xe442c,2))[0]
  for fn,base,ot,depth in dispatch(mask,self.buffer,counts,scale):
   record=bytes(u.mem_read(base&0x1fffffff,36))
   if fn==0x80084830:part=packet(record,160,120,links[depth])
   else:
    assert fn==0x80083b4c or (self.allow_scaled and fn==0x80083338),'scaled backgrounds require explicit softwareGTE option'
    addr=struct.unpack_from('<I',record,20)[0]&0x1fffffff;header=bytes(u.mem_read(addr,16));tp,ip=struct.unpack_from('<II',header,8);cols,rows=struct.unpack_from('<HH',header,2);indices=list(struct.unpack('<'+'H'*(cols*rows),u.mem_read(ip&0x1fffffff,cols*rows*2)));tiles=[bytes(u.mem_read((tp+j*8)&0x1fffffff,8)) for j in range(max([i for i in indices if i!=65535],default=-1)+1)]
    if fn==0x80083b4c:
     full,used,_,_=tiled_general(record,header,tiles,indices,160,120,self.buf+len(stream),links[depth],bytes(self.packet_capacity-len(stream)))
    else:
     sx,sy=struct.unpack_from('<2h',record,28);matrix,_=scale_matrix(bytes(u.mem_read(0x12b010,32)),sx,sy,4096)
     full,used,_=scaled_background(record,header,tiles,indices,160,120,self.buf+len(stream),links[depth],bytes(self.packet_capacity-len(stream)),lambda x,y:vector_product(matrix,[x,y,0]))
    part=full[:used]
   draw.append((base,depth,bool(part)))
   if part:links[depth]=(self.buf+len(stream))&0xffffff;stream.extend(part)
  assert len(stream)<self.packet_capacity-16;self.expected_stream=bytes(stream);self.expected_links=links;self.current_frame=[mask,raw,c['address'] if c else 0,draw]
