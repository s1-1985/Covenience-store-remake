"""Independent bounded offset-table decode of original MSG00 and STAFF banks."""
from pathlib import Path
import struct,hashlib
R=Path(__file__).resolve().parent

def parse_bank(blob):
 first=struct.unpack_from('<I',blob)[0];assert first%4==0 and 0<first<=len(blob)
 offsets=struct.unpack_from('<'+'I'*(first//4),blob);assert tuple(sorted(offsets))==offsets
 assert all(first<=o<len(blob) and o%2==0 for o in offsets)
 messages={}
 for j,start in enumerate(offsets):
  # Offsets may point into overlapping/shared strings; the next offset is not
  # a string boundary. The original terminates at40FF within the file.
  end=len(blob)
  words=list(struct.unpack_from('<'+'H'*((end-start)//2),blob,start));assert 0x40ff in words,(j,start,end)
  messages[j]=words[:words.index(0x40ff)+1]
 return messages
BANKS=[]
for name in ('MSG00.OBJ','STAFF.OBJ'):
 blob=(R/'source'/name).read_bytes();BANKS.append(dict(name=name,blob=blob,messages=parse_bank(blob),sha256=hashlib.sha256(blob).hexdigest()))

def source_messages(read,base):
 prefix=read(base,32)
 matches=[x for x in BANKS if x['blob'][:32]==prefix];assert len(matches)==1,('unknown message bank',hex(base),prefix.hex())
 bank=matches[0];assert read(base,len(bank['blob']))==bank['blob'],('message bank changed',bank['name'])
 return bank
