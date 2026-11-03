import sys,zipfile,json,zlib,base64,hashlib
from pathlib import Path
SOURCE=(Path(__file__).resolve().parent.parent/'20261103-native-file-recovery/native-file-analysis.py').read_text()
M={"__name__":"reference"};exec(compile(SOURCE,"native-file-analysis.py","exec"),M)
with zipfile.ZipFile(sys.argv[1]) as z:exe=z.read("algorithm-analysis/source/SLPS_007.82")
rows=[]
for op,func in [("read",0x8007ab2c),("write",0x8007adf8)]:
 for mode in (0,1):
  for endpoint,address in (("open",0x8007e4ec),("seek",0x8007e4fc),("close",0x8007e52c)):
   for frequency in ("once","persistent"):
    c=M["Cpu"](exe);env=M["LogicalFiles"](c,{M["PATH"]:bytes(114688)});calls=[0]
    normal=c.hooks[address]
    def failed(c):
     calls[0]+=1
     if frequency=="persistent" or calls[0]==1:
      env.io.append(dict(op="fault_"+endpoint,args=c.r[4:7],result=-1));return -1
     return normal(c)
    c.hooks[address]=failed
    try:ret=c.run(func,[mode],limit=200000,stack_pointer=0x801d0000,global_pointer=M["GP"]);state="returned"
    except TimeoutError:ret=None;state="instruction_budget_exhausted"
    trace=json.dumps(env.io,separators=(",",":")).encode()
    rows.append(dict(operation=op,mode=mode,endpoint=endpoint,frequency=frequency,state=state,return_value=ret,
                     calls=calls[0],steps=c.steps,open_handles={str(k):dict(name=v[0].decode(),position=v[1]) for k,v in env.fds.items()},
                     first_io=env.io[:5],last_io=env.io[-3:],trace_sha256=hashlib.sha256(trace).hexdigest(),
                     trace_zlib_base64=base64.b64encode(zlib.compress(trace,9)).decode()))
print(json.dumps([{k:v for k,v in r.items() if k not in ("trace_zlib_base64","first_io","last_io")} for r in rows],separators=(",",":")))
print(base64.b64encode(zlib.compress(json.dumps(rows,separators=(",",":")).encode(),9)).decode())
