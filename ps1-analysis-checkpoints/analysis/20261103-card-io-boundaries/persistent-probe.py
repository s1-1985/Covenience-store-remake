import sys,zipfile,json,struct
from pathlib import Path
SOURCE=(Path(__file__).resolve().parent.parent/'20261103-native-file-recovery/native-file-analysis.py').read_text()
M={"__name__":"reference"};exec(compile(SOURCE,"native-file-analysis.py","exec"),M)
with zipfile.ZipFile(sys.argv[1]) as z:exe=z.read("algorithm-analysis/source/SLPS_007.82")
rows=[]
for op,func,endpoint in [("read",0x8007ab2c,0x8007e50c),("write",0x8007adf8,0x8007e51c)]:
 for mode in (0,1):
  for ret in (-1,0):
   c=M["Cpu"](exe);env=M["LogicalFiles"](c,{M["PATH"]:bytes(114688)})
   counts={"io_calls":0,"wait_calls":0,"wait_arguments":[]}
   def fail(c):
    counts["io_calls"]+=1
    return ret
   def wait(c):
    counts["wait_calls"]+=1
    if len(counts["wait_arguments"])<3:counts["wait_arguments"].append(c.r[4])
    return 0
   c.hooks[endpoint]=fail;c.hooks[0x80089ca4]=wait
   try:
    result=c.run(func,[mode],limit=200000,stack_pointer=0x801d0000,global_pointer=M["GP"])
    state="returned"
   except TimeoutError:result=None;state="instruction_budget_exhausted"
   assert state=="instruction_budget_exhausted"
   rows.append(dict(operation=op,mode=mode,persistent_result=ret,state=state,return_value=result,steps=c.steps,stopped_pc=hex(c.pc),**counts))
print(json.dumps(rows,separators=(",",":")))
