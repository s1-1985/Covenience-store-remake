"""65350/6558C outer policy; SDK effects are not reproduced."""
from audio_resources import destination
ADDRESSES=(0x800cd880,0x800cd7e8,0x800cda2e,0x800cd9b8)
def signed16(v):
 v &= 65535
 return v-65536 if v&32768 else v
def initialize(handles,results):
 calls=[]
 if signed16(handles[2])!=-1:return calls
 for index,bank_slot,sequence_slot,count in ((8,3,2,16),(7,1,0,12)):
  calls += [('resource',index,mode) for mode in (1,2,4)]
  bank,sequence=results[index];handles[bank_slot]=bank&65535
  calls += [('sdk',0x8008f000,(destination(index,1),-1)),('sdk',0x8008f4a4,(destination(index,2),signed16(bank))),('sdk',0x8008f564,(1,)),('sdk',0x8008b000,(destination(index,4),signed16(bank),count))]
  handles[sequence_slot]=sequence&65535
  calls += [('sdk',0x8008eb1c,(signed16(sequence),track,127,127)) for track in range(12)]
 return calls
def cleanup(handles):
 if signed16(handles[2])==-1:return []
 calls=[]
 for seq,bank in ((handles[0],handles[1]),(handles[2],handles[3])):
  calls += [('sdk',0x8008ecf4,(signed16(seq),)),('sdk',0x8008d5e8,(signed16(seq),)),('sdk',0x8008ef24,(signed16(bank),))]
 handles[:]=[65535]*4
 return calls

def bootstrap(handles,results):
 """64DA4 resets all six audio handles and current BGM before native65350."""
 handles[:]=[65535]*4
 return [('sdk',0x8008e548,(1,)),('sdk',0x8008d9d0,()),('sdk',0x8008aa60,(127,127))]+initialize(handles,results)
