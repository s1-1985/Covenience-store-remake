"""Recovered65100 BGM switching outer control; resource/audio APIs explicit."""
from recovered import i32

def s16(n):n&=65535;return n if n<32768 else n-65536

def change(s,requested,loop,bank_result,sequence_result):
 requested=i32(requested);calls=[]
 if i32(s['current'])==requested:return calls
 def close():
  calls.extend([(0x8008ecf4,(s16(s['sequence']),)),(0x8008d5e8,(s16(s['sequence']),)),(0x8008ef24,(s16(s['bank']),)),(0x80089ca4,(0,))])
 if requested!=-1:
  if requested==6:calls.append((0x8006558c,()))
  calls.append((0x800140e8,(requested,2)))
  if i32(s['current'])!=-1:close()
  calls.extend([(0x800140e8,(requested,1)),(0x800140e8,(requested,4)),(0x8008f000,(s['vh_data'],-1))])
  s['bank']=bank_result&65535
  calls.extend([(0x8008f4a4,(s['vb_data'],s16(s['bank']))),(0x8008f564,(1,)),(0x8008b458,(s['seq_data'],s16(s['bank'])))])
  s['sequence']=sequence_result&65535
  calls.extend([(0x8008aa60,(127,127)),(0x8008ea44,(s16(s['sequence']),1,s16(loop))),(0x8008eaec,(s16(s['sequence']),100,100))])
 elif i32(s['current'])!=-1:close()
 s['current']=requested&0xffffffff
 return calls
