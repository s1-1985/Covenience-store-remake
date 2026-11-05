"""Freeze small reference cases from restored analysis commit 2c00ba53.
Usage: python tools/integration/build_operations_fixtures.py <algorithm-analysis>
Only verified pure Python models are used; no CPU or console dependency.
"""
import hashlib, importlib, json, random, struct, sys
from pathlib import Path
root=Path(__file__).resolve().parents[2]
source=Path(sys.argv[1]).resolve();sys.path.insert(0,str(source))
wear=importlib.import_module('floor_wear');sampling=importlib.import_module('staff_candidate_pool')
r=random.Random(78243);floor_cases=[];pool_cases=[]
for i in range(40):
 rows=[[r.choice([0,1,2,4,5,6,9,10,11,14,15,16,17,255]) for _ in range(5)] for _ in range(4)];rows[0][0]=0
 positions=[[r.randrange(10),r.randrange(8)] for _ in range(i%8)]
 previous=r.choice([0,40,69,70,99,100]);seed=r.getrandbits(32);store=bytearray(5080)
 struct.pack_into('<ii',store,0x44,10,8)
 for y,row in enumerate(rows):store[0x50+y*14:0x50+y*14+5]=bytes(row)
 for j,(x,y) in enumerate(positions):store[0xf04+j*32]=2;store[0xf10+j*32]=x;store[0xf11+j*32]=y
 final_seed,pct=wear.update(store,0,previous,seed)
 after=[list(store[0x50+y*14:0x50+y*14+5]) for y in range(4)]
 floor_cases.append(dict(rows=rows,positions=positions,previous=previous,seed=seed,after=after,percentage=pct,final_seed=final_seed))
for i in range(20):
 staff=[bytearray(60) for _ in range(35)]
 for row in staff:
  if r.randrange(3)==0:row[0]=1
 free=[str(j) for j,s in enumerate(staff) if s[:2]==bytes(2)];seed=r.getrandbits(32)
 chosen,final_seed,_=sampling.candidates(staff,seed)
 pool_cases.append(dict(free=free,seed=seed,chosen=list(map(str,chosen)),final_seed=final_seed))
result=dict(analysis_commit='2c00ba53ed5d469b406d498f3d1f9191074679a0',source_sha256={n:hashlib.sha256((source/n).read_bytes()).hexdigest() for n in ['floor_wear.py','staff_candidate_pool.py','recovered.py']},floor_cases=floor_cases,pool_cases=pool_cases)
p=root/'game/tests/fixtures/source_operations.json';p.write_text(json.dumps(result,separators=(',',':'))+'\n');print(p)
