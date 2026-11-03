import sys,zipfile,zlib,json,hashlib,struct
from pathlib import Path
SOURCE=(Path(__file__).resolve().parent.parent/'20261103-native-file-recovery/native-file-analysis.py').read_text()
module={"__name__":"file_reference"}
exec(compile(SOURCE,"native-file-analysis.py","exec"),module)
path=sys.argv[1]
sys.path.insert(0,path+"/algorithm-analysis")
from save_codec import BASE,SIZE,FIELDS,encode,valid
rows=[];files={}
with zipfile.ZipFile(path) as z:
 exe=z.read("algorithm-analysis/source/SLPS_007.82")
 for name in ["TOWN0001-nov3-two-own-nextday-single","TOWN0001-nov3-r2-24h-07-single"]:
  ram=zlib.decompress(z.read("algorithm-analysis/source/opened-snapshots-20261028/"+name+".ram.zlib"))
  c=module["Cpu"](exe);c.mem[:]=ram;env=module["LogicalFiles"](c,files)
  expected=bytes(encode(bytearray(c.read(BASE,SIZE)),c.read));seed=c.read(0x800d6270,4)
  enc=c.run(0x8006b81c,[],limit=15000000,stack_pointer=0x801d0000,global_pointer=0x800cd6c4)
  body=c.read(BASE,114176);assert body[:SIZE]==expected and valid(expected)
  for function in [0x8007adf8,0x8007ab2c]:
   if function==0x8007ab2c:c.write(BASE,b"\xcc"*114176)
   for mode in [0,1]:assert c.run(function,[mode],limit=1000000,stack_pointer=0x801d0000,global_pointer=0x800cd6c4)==0
  assert c.read(BASE,114176)==body
  payload=c.read(BASE,SIZE)
  for offset,address,size in FIELDS:c.write(address,b"\xcc"*size)
  c.run(0x8006bc40,[],limit=1000000,stack_pointer=0x801d0000,global_pointer=0x800cd6c4)
  assert all(c.read(address,size)==payload[offset:offset+size] for offset,address,size in FIELDS)
  assert c.read(0x800d6270,4)==seed
  files=env.files
  rows.append(dict(source=name,passed=True,body_sha256=hashlib.sha256(body).hexdigest(),decoded_fields=len(FIELDS),tail_sha256=hashlib.sha256(body[SIZE:]).hexdigest()))
print(json.dumps(rows))
