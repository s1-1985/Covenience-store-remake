"""Export recovered PS1 data to Godot; argument: restored algorithm-analysis."""
import json,struct,sys,hashlib
from pathlib import Path
from PIL import Image
ROOT=Path(__file__).resolve().parents[2];source=Path(sys.argv[1]).resolve();sys.path.insert(0,str(source))
from town_mutation import descriptors
from town_monthly import monthly,population
exe=(source/'source/SLPS_007.82').read_bytes()
assert hashlib.sha256(exe).hexdigest()=='d6a167a1c9e0fe98d7e44e12968caa489ac3eb7ed3b9e46012a188af8432b1fd'
raw=lambda a,n:exe[a-0x80010000+2048:a-0x80010000+2048+n]
table=descriptors(json.loads((source/'town-building-tables.json').read_text())['buildings'])
groups=json.loads((source/'demand-tables.json').read_text())['groups']
data=(source/'source/TOWN0001.BIN').read_bytes();town=data[17:24017]
cells=[list(struct.unpack_from('<hbbbbh',town,i*8)) for i in range(3000)]
fixtures=[list(struct.unpack('<49i',raw(0x80099f0c+i*196,196))) for i in range(53)]
products=[list(struct.unpack('<2i',raw(0x8009ce08+i*88,8))) for i in range(27)]
recovery={'source_exe_sha256':hashlib.sha256(exe).hexdigest(),'town_cells':cells,'buildings':[{k:r[k] for k in ('id','name','lower','upper','category','width','height','attribute','groups')} for r in table],'groups':groups,'initial_population':population(town,0,groups),'initial_cash':struct.unpack_from('<2i',data,1),'fixture_records':fixtures,'products':products,'hours':[list(raw(0x80099de5+i*45,24)) for i in range(7)],'source_notes':'CONFIRMED_BINARY: SLPS_007.82; town_monthly.py, town_mutation.py, staff_energy.py, checkout.py, inventory_callers.py. No EXE/BIOS/CPU interpreter exported.'}
(ROOT/'game/data/ps1_recovered.json').write_text(json.dumps(recovery,ensure_ascii=False,separators=(',',':'))+'\n')
assets=ROOT/'game/assets/ps1';assets.mkdir(exist_ok=True)
old=ROOT/'assets/raw/ps1_disc_analysis_v1'
tex=Image.open(old/'images/TIM0_TOWN_PR1.png');cel=json.loads((old/'cells.json').read_text())
atlas=Image.new('RGBA',(512,80))
for c in cel:
 u,v=c['u'],c['v']-96;t=tex.crop((u,v,u+8,v+8))
 if c['flip_x']:t=t.transpose(Image.Transpose.FLIP_LEFT_RIGHT)
 if c['flip_y']:t=t.transpose(Image.Transpose.FLIP_TOP_BOTTOM)
 atlas.paste(t,((c['id']%64)*8,(c['id']//64)*8))
atlas.save(assets/'town_tiles.png')
for r in table:
 if r['category']<=1:continue
 im=Image.new('RGBA',(r['width']*8,r['height']*8))
 for y in range(r['height']):
  for x in range(r['width']):
   k=r['lower']+y*r['width']+x;im.paste(atlas.crop(((k%64)*8,(k//64)*8,(k%64)*8+8,(k//64)*8+8)),(x*8,y*8))
 im.save(assets/('building_%02d.png'%r['id']))
cases=[]
stores=[dict(active=1,rect=[26,12,27,13],value=500000,c74=0,c75=0,c76=0),dict(active=1,rect=[43,12,44,13],value=700000,c74=0,c75=0,c76=0)]
for seed,level in [(0,0),(1,0),(7,0),(7,20)]:
 before=bytearray(town)
 if level:
  for i in range(3000):before[i*8+2]=level
 state=dict(seed=seed,month=1,stage=1,hour=0,subhour=0,reference=100,divisor=10000,tier=0,mode=0,progress_flags=0,progress_counter=0,dirty=0,history=[0]*60)
 after=before.copy();out,events,actions=monthly(after,table,groups,stores,[0,1],state)
 cases.append(dict(seed=seed,level=level,stores=stores,sha256=hashlib.sha256(after).hexdigest(),final_seed=out['seed'],population=out['history'][0],tier=out['tier'],actions=actions))
folder=ROOT/'game/tests/fixtures';folder.mkdir(exist_ok=True)
(folder/'recovered_town.json').write_text(json.dumps(cases,separators=(',',':'))+'\n')
print('Exported original 60x50 town, 72 building records, 640 tiles and source fixtures')
# Interior image indices: original 5670C tile_record and +60 conversion.
meta=json.loads((source/'interior-display-source-tables.json').read_text())
textures=[Image.open(old/('images/TIM0_SYOP_S0%d.png'%i)) for i in range(3)]
def source_tile(code):
 page=next(i for i,t in enumerate([256,512,768]) if code<=t)
 u,v=(code&15)*16,code&240
 return textures[page].crop((u,v,u+16,v+16))
interior=Image.new('RGBA',(1024,1024));regions={}
for i,f in enumerate(fixtures):
 w,h=f[9:11]
 for rot,direction in enumerate([0,3,1,2]):
  image=Image.new('RGBA',((h if rot&1 else w)*16,(w if rot&1 else h)*16))
  for y in range(h):
   for x in range(w):
    tile_id=f[11+y*3+x]
    if tile_id<0:continue
    code=int(meta['tiles'][str(tile_id)][direction])+60
    xx,yy= [(x,y),(h-1-y,x),(w-1-x,h-1-y),(y,w-1-x)][rot]
    image.paste(source_tile(code),(xx*16,yy*16))
  index=i*4+rot;px,py=(index%16)*64,(index//16)*64
  interior.paste(image,(px,py));regions['fixture_%d_%d'%(i,rot)]=[px,py,image.width,image.height]
product_ids=['cold_drink','hot_drink','alcohol','bento','bread','instant_food','snacks','books','tobacco','ice_cream','stationery','electronics','vegetables','fish','meat','retort_food','seasoning','frozen_food','oden','daily_goods','copy_paper','parcel_delivery_form','medicine','underwear','event_goods','chinese_steamed_bun']
for i,pid in enumerate(product_ids):
 base=meta['product_images'][i][0]*3+360
 for level in range(3):
  index=i*3+level;px,py=(index%64)*16,896+(index//64)*16
  interior.paste(source_tile(base+level),(px,py));regions['product_%s_%d'%(pid,level)]=[px,py,16,16]
interior.save(assets/'interior_atlas.png')
source_tile(0).save(assets/'floor.png')
__import__('shutil').copy2(old/'images/TIM0_MAN0.png',assets/'people.png')
catalog=json.loads((ROOT/'game/data/vertical_slice.json').read_text())['fixture_catalog']
indices=[45,46,47,0,27,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,22,24,25,26,28,29,30,31,32,50,51,52,48,49]
recovery['fixture_kind']={c['catalog_id']:k for c,k in zip(catalog,indices)}
recovery['sprite_regions']=regions
(ROOT/'game/data/ps1_recovered.json').write_text(json.dumps(recovery,ensure_ascii=False,separators=(',',':'))+'\n')
print('Exported original people, directional equipment and three stock stages')

recovery['compatibility_boundaries']={'evidence_note': 'REMAKE_BALANCED_DEFAULT: Native town, costs and work gates are recovered. Actor pathfinding/queue geometry, opening interior arrangement and staff allocation, random rival size/layout choices, induction timing/cost presentation, touch UI and audio remain client bridges; the whole game trajectory is not source-equivalent.'}
(ROOT/'game/data/ps1_recovered.json').write_text(json.dumps(recovery,ensure_ascii=False,separators=(',',':'))+'\n')
