import sys,zipfile,struct,json,hashlib,base64,zlib
from pathlib import Path
SOURCE=(Path(__file__).resolve().parent.parent/"20261103-native-file-recovery/native-file-analysis.py").read_text()
M={"__name__":"file_reference"};exec(compile(SOURCE,"native-file-analysis.py","exec"),M)
path=sys.argv[1]
with zipfile.ZipFile(path) as z:
 exe=z.read("algorithm-analysis/source/SLPS_007.82")
 n=sorted(n for n in z.namelist() if n.startswith("algorithm-analysis/source/operating-save-payloads-20261103/") and n.endswith(".payload.bin"))[0]
 payload=z.read(n)
body=payload+b"\xa5"*9812;BASE=M["BODY"];PATH=M["PATH"];Cpu=M["Cpu"];LogicalFiles=M["LogicalFiles"]
c=Cpu(exe);env=LogicalFiles(c,{});c.write(BASE,body)
for mode in (0,1):assert c.run(0x8007adf8,[mode],limit=1000000,stack_pointer=0x801d0000,global_pointer=M["GP"])==0
initial=bytes(env.files[PATH])
class FaultFiles(LogicalFiles):
 def __init__(self,c,operation,response):
  self.operation=operation;self.response=response;self.injected=False
  super().__init__(c,{PATH:initial})
 def read_file(self,c):
  if self.operation!="read" or self.injected:return super().read_file(c)
  self.injected=True;fd,address,size=c.r[4:7];name,pos=self.fds[fd]
  result=self.response
  if result>0:c.write(address,self.files[name][pos:pos+result]);self.fds[fd][1]+=result
  self.io.append(dict(op="fault_read",fd=fd,file_offset=pos,requested=size,result=result))
  return result
 def write_file(self,c):
  if self.operation!="write" or self.injected:return super().write_file(c)
  self.injected=True;fd,address,size=c.r[4:7];name,pos=self.fds[fd];result=self.response
  if result>0:self.files[name][pos:pos+result]=c.read(address,result);self.fds[fd][1]+=result
  self.io.append(dict(op="fault_write",fd=fd,file_offset=pos,requested=size,result=result))
  return result
records=[]
for operation,function in (("read",0x8007ab2c),("write",0x8007adf8)):
 for response in (-1,0,127,128):
  for mode in (0,1):
   c=Cpu(exe);env=FaultFiles(c,operation,response)
   intended=bytes((v^255) for v in body) if operation=="write" else body
   c.write(BASE,intended if operation=="write" else b"\xcc"*114176)
   ret=c.run(function,[mode],limit=1000000,stack_pointer=0x801d0000,global_pointer=M["GP"])
   start=0 if mode==0 else 89600;end=89600 if mode==0 else 114176
   got=c.read(BASE+start,end-start) if operation=="read" else bytes(env.files[PATH][512+start:512+end])
   want=intended[start:end]
   trace=json.dumps(env.io,separators=(",",":")).encode()
   record=dict(matches_requested_data=got==want,data_sha256=hashlib.sha256(got).hexdigest(),expected_data_sha256=hashlib.sha256(want).hexdigest(),
               first_differences=[dict(offset=start+i,actual=a,expected=b) for i,(a,b) in enumerate(zip(got,want)) if a!=b][:20],
               trace_zlib_base64=base64.b64encode(zlib.compress(trace,9)).decode(),trace_sha256=hashlib.sha256(trace).hexdigest(),
               output_patches=[dict(offset=start+i,value=a) for i,(a,b) in enumerate(zip(got,want)) if a!=b],
               operation=operation,mode=mode,injected_result=response,return_value=ret,steps=c.steps,injected=env.injected,
               io_count=len(env.io),calls=env.io[:8],last_io=env.io[-3:])
   records.append(record)
print(json.dumps([dict(operation=r["operation"],mode=r["mode"],injected_result=r["injected_result"],return_value=r["return_value"],matches_requested_data=r["matches_requested_data"],io_count=r["io_count"],first_differences=r["first_differences"][:2]) for r in records],separators=(",",":")))
print(base64.b64encode(zlib.compress(json.dumps(records,separators=(",",":")).encode(),9)).decode())
