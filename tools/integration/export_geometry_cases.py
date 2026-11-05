"""Export small golden cases from the separately verified PS1 analysis models."""
import argparse,importlib,sys,json,random,struct
from pathlib import Path
p=argparse.ArgumentParser();p.add_argument('analysis',type=Path);args=p.parse_args();sys.path.insert(0,str(args.analysis.resolve()))
m=importlib.import_module('movement');codec=importlib.import_module('route_codec');sides=importlib.import_module('use_sides');store_map=importlib.import_module('store_map')
r=random.Random(0x248b0);routes=[];uses=[];maps=[]
for i in range(60):
 w,h=r.randrange(3,15),r.randrange(3,15);grid=[[-1 if r.randrange(5)==0 else -2 for x in range(w)]for y in range(h)]
 sx,sy=r.randrange(w),r.randrange(h);gx,gy=r.randrange(w),r.randrange(h);grid[sy][sx]=0;grid[gy][gx]=10000+r.randrange(4)
 code,goal,out=m.generic_route(grid,w,h,sx,sy);case=dict(width=w,height=h,start=[sx,sy],grid=grid,result=code)
 if code==0:
  packed,start,runs=codec.encode_route(out,w,h,*goal);case.update(goal=list(goal),packed=list(packed),route_start=list(start),gradient=out)
 routes.append(case)
for orientation in range(4):
 for category in range(11):
  for mode in range(2):
   grid=[[-2]*10 for _ in range(10)];grid[1][4]=-1
   out=sides.mark_use_sides(grid,10,10,2,2,orientation,category,2,1,mode)
   uses.append(dict(orientation=orientation,category=category,mode=mode,expected=out))
for i in range(24):
 w,h=12,12;room=[4,4];roomsize=[1,1];floor=[[16]*6 for _ in range(6)]
 for y in range(1,5):
  for x in range(1,5):floor[y][x]=r.choice([0,0,0,28,32])
 blocked=[[r.randrange(w),r.randrange(h)] for _ in range(18)];blocked += [[x,y]for y in range(4,6)for x in range(4,6)]
 store=bytearray(4000);meta=bytearray(3000);summary=bytearray(40);struct.pack_into('<ii',store,0x44,w,h);struct.pack_into('<ii',summary,0x18,*room)
 for y,row in enumerate(floor):store[0x50+y*14:0x50+y*14+6]=bytes(row)
 for x,y in blocked:struct.pack_into('<I',store,0x108+y*112+x*4,1)
 fixtures=[[0]*11];fixtures[0][9:11]=roomsize
 # Room cell needs fixture kind zero while retaining low-bit occupancy.
 count=store_map.rebuild(store,meta,summary,fixtures,m.DIRECTIONS,0,True)
 out=[[struct.unpack_from('<h',meta,20+y*56+x*2)[0]for x in range(w)]for y in range(h)]
 maps.append(dict(width=w,height=h,floor=floor,blocked=blocked,room=room,room_size=roomsize,expected=out,unreachable=count))
out=Path(__file__).resolve().parents[2]/'game/data/source_geometry_cases.json';out.write_text(json.dumps(dict(source='2c00ba53 movement.py/route_codec.py/use_sides.py/store_map.py',routes=routes,sides=uses,maps=maps),separators=(',',':'))+'\n')
print(f'{len(routes)} routes, {len(uses)} side masks, {len(maps)} working maps')
