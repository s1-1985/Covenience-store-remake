#!/usr/bin/env python3
"""Static disc data: building -> mix -> shopping profile -> appearance -> texels.
No emulation, simulated day, or source RAM checkpoint is used.
"""
import argparse, collections, csv, hashlib, io, json, runpy, struct
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
from capstone import Cs,CS_ARCH_MIPS,CS_MODE_MIPS32,CS_MODE_LITTLE_ENDIAN
ROOT=Path(__file__).resolve().parent
PREVIOUS=ROOT.parent/'20261113-disc-data-extraction'
DISC_SHA='8d8eda789c5a2fe892a4722719b0466dd7d126eed6cd99ad05a807d81b57d1c1'
EXE_SHA='d6a167a1c9e0fe98d7e44e12968caa489ac3eb7ed3b9e46012a188af8432b1fd'
STATS=['shopping_importance','price_weight','distance_weight','service_weight','stamina','quickness','manners','focus','weekday_share','holiday_share']
PRODUCTS=['cold_drink','hot_drink','alcohol','bento','bread','instant_food','snacks','books','tobacco','ice_cream','stationery','electronics','vegetables','fish','meat','retort_food','seasoning','frozen_food','oden','daily_goods','copy_paper','parcel_delivery_form','medicine','underwear','event_goods','chinese_steamed_bun','source_special_26']
def sha(b):return hashlib.sha256(b).hexdigest()
def js(name,data):
 p=ROOT/name;p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n')
def sb(b,i):return struct.unpack_from('<b',b,i)[0]
def sj(b):return b.split(b'\0',1)[0].decode('shift_jis')
def main():
 ap=argparse.ArgumentParser();ap.add_argument('disc',type=Path);args=ap.parse_args();disc=args.disc.read_bytes();assert sha(disc)==DISC_SHA
 inventory=json.loads((PREVIOUS/'disc-inventory.json').read_text());assert inventory['disc_sha256']==DISC_SHA
 files={r['path']:r for r in inventory['files']}
 def source(name):
  r=files[name];b=b''.join(disc[(r['lba']+j)*2352+24:(r['lba']+j)*2352+2072] for j in range((r['bytes']+2047)//2048))[:r['bytes']]
  assert sha(b)==r['iso_projection_sha256'];return b
 exe=source('/SLPS_007.82');assert sha(exe)==EXE_SHA
 def raw(addr,n):return exe[addr-0x80010000+2048:addr-0x80010000+2048+n]
 (ROOT/'source').mkdir(exist_ok=True)
 regions=[('building-master',0x8009da10,69*56),('customer-mixes',0x8009ff1c,137*20),('shopping-profiles',0x800a09d0,144*24),('appearance-descriptors',0x800a1750,44*23),('appearance-choices',0x800a1b44,44*4)]
 ranges=[]
 for name,addr,n in regions:
  b=raw(addr,n);(ROOT/'source'/(name+'.bin')).write_bytes(b);ranges.append(dict(name=name,address=hex(addr),bytes=n,sha256=sha(b)))
 assert 0x8009ff1c+137*20==0x800a09d0 and 0x800a09d0+144*24==0x800a1750
 assert 0x800a1750+44*23==0x800a1b44
 direction_images=list(struct.unpack('<4i',raw(0x8009940c,16)))
 movements=[list(struct.unpack('<2i',raw(0x8009941c+k*8,8))) for k in range(4)]
 role_looks=list(raw(0x800cd758,6));directions=['up','down','left','right']
 actors=[]
 for i in range(44):
  b=raw(0x800a1750+i*23,23);name=sj(b[:21]);looks=list(raw(0x800a1b44+i*4,4));frames=[]
  for d in range(4):
   image_index=i*4+direction_images[d]
   frames.append(dict(direction=d,direction_name=directions[d],movement_delta=movements[d],image_code=640+image_index,uv=[(image_index&15)*16,image_index&240],size=[16,16]))
  actors.append(dict(id=i,address=hex(0x800a1750+i*23),raw_hex=b.hex(),name=name,metadata_byte21=b[21],metadata_byte22=b[22],sex_candidate='female' if b[21] else 'male',age_candidate=b[22],metadata_semantic_status='Sex/age inferred from labels and values; original code readers for this23-byte descriptor table have not been identified.',appearance_options_for_profile_group=looks,frames=frames))
 assert all(0<=j<44 for a in actors for j in a['appearance_options_for_profile_group'])
 profiles=[]
 for i in range(144):
  b=raw(0x800a09d0+i*24,24);group,hour,stay,budget=struct.unpack_from('<4h',b);assert 0<=group<38 and 0<=hour<24
  products=[sb(b,k) for k in range(8,12)];opts=actors[group]['appearance_options_for_profile_group'];weight=collections.Counter(opts)
  profiles.append(dict(id=i,address=hex(0x800a09d0+i*24),raw_hex=b.hex(),appearance_group=group,group_label=actors[group]['name'],appearance_option_ids=opts,appearance_choices=[dict(id=k,name=actors[k]['name'],slots=v,out_of=4) for k,v in sorted(weight.items())],start_hour=hour,stay_minutes=stay,budget_yen=budget,product_ids=products,primary_product=PRODUCTS[products[0]],arrival_mode=sb(b,12),stats={name:sb(b,13+j) for j,name in enumerate(STATS)},byte23=b[23]))
 mixes=[]
 for i in range(137):
  b=raw(0x8009ff1c+i*20,20);pairs=[]
  for slot in range(5):
   pid,qty=struct.unpack_from('<2h',b,slot*4);pairs.append(dict(slot=slot,profile_id=pid,heads=qty,sentinel=pid==-1,valid_profile=0<=pid<144))
  mixes.append(dict(id=i,address=hex(0x8009ff1c+i*20),raw_hex=b.hex(),entries=pairs,source_population_heads=sum(x['heads'] for x in pairs if not x['sentinel']),valid_profile_heads=sum(x['heads'] for x in pairs if x['valid_profile'])))
 buildings=[]
 for i in range(69):
  b=raw(0x8009da10+i*56,56);name=sj(b[:24]);w,h,lower,upper=struct.unpack_from('<4i',b,24);category=struct.unpack_from('<h',b,40)[0];ids=list(struct.unpack_from('<5h',b,42))
  assert all(x==-1 or 0<=x<137 for x in ids)
  counts=collections.Counter(x for x in ids if x!=-1)
  buildings.append(dict(id=i,address=hex(0x8009da10+i*56),raw_hex=b.hex(),name=name,extension_named_entry=name.startswith('拡張'),size=[w,h],tile_range=[lower,upper],category=category,mix_slots=ids,mix_options=[dict(mix_id=k,slots=v,out_of=5,source_population_heads=mixes[k]['source_population_heads'],valid_profile_heads=mixes[k]['valid_profile_heads']) for k,v in sorted(counts.items())],message_index=struct.unpack_from('<h',b,52)[0],word54=struct.unpack_from('<h',b,54)[0]))
 invalid=[dict(mix_id=m['id'],**e) for m in mixes for e in m['entries'] if not e['sentinel'] and not e['valid_profile']]
 assert invalid==[dict(mix_id=136,slot=3,profile_id=144,heads=1,sentinel=False,valid_profile=False)]
 worlds=[]
 for name in ('TOWN0001','TOWN0002','TOWN0003','TOWNPS'):
  b=source('/DAT/'+name+'.BIN');assert len(b)==76707;town=b[17:24017];full=valid=0;affected=[];hist=collections.Counter()
  for k in range(3000):
   tile,=struct.unpack_from('<h',town,k*8);mix,=struct.unpack_from('<h',town,k*8+6)
   if mix==-1:continue
   assert 0<=mix<137;hist[mix]+=1;full+=mixes[mix]['source_population_heads'];valid+=mixes[mix]['valid_profile_heads']
   if mixes[mix]['source_population_heads']!=mixes[mix]['valid_profile_heads']:
    kind=next((d for d in buildings if d['tile_range'][0]<=tile<=d['tile_range'][1]),None)
    affected.append(dict(x=k%60,y=k//60,tile=tile,mix_id=mix,building_id=kind['id'] if kind else None,building_name=kind['name'] if kind else None))
  worlds.append(dict(file=name+'.BIN',source_sha256=sha(b),source_population_heads=full,heads_if_invalid_profile_entries_are_dropped=valid,difference=full-valid,affected_cells=affected,mix_cell_histogram=dict(sorted(hist.items()))))
 assert [(x['source_population_heads'],x['difference']) for x in worlds]==[(2179,2),(1880,1),(1424,0),(2839,1)]
 # Row144 is not a hidden shopper: its bytes start the next table's first label.
 phantom=raw(0x800a09d0+144*24,24);assert phantom[:23]==raw(0x800a1750,23)
 assert sb(phantom,8)==-111
 anomaly=dict(known_before_this_work='The prior Android table exporter already excluded mix136 profile144. This work identifies the adjacent source bytes, native rejection path, and the different population semantics.',reference=invalid[0],mix136=mixes[136],buildings_with_this_mix=[dict(id=b['id'],name=b['name'],mix_slots=b['mix_slots']) for b in buildings if 136 in b['mix_slots']],profile144_address='0x800a1750',bytes_if_misread_as_profile=phantom.hex(),first_23_bytes_decode_to=actors[0]['name'],interpreted_primary_product_signed8=sb(phantom,8),normal_native_path=['800265D0: read signed profile ID from a mix','800265E0..800265EC: skip only the -1 sentinel at this stage','80026628: weather gate reads profile+13','80026674..80026680: signed primary product byte passed to80027328','80027344..8002736C: negative or>=27 product returns2','80026688..80026694: return2 skips allocation for this mix entry'],normal_path_outcome='No valid145th profile. The negative product ID is rejected in the ordinary filtered path. Population80020498 still adds the mix head count because it only skips profile ID-1.',nonzero_800cda00_path='80026600 can bypass the filter block. Reachability and gameplay effects of that exceptional state are not established here; no corruption is claimed.',population_versus_demand_policy='Preserve the original heads for population; exclude invalid profile rows from purchasable customer data. Do not delete the pair from the population mix or invent a145th shopper.')
 field_layout=[dict(offset=0,type='i16',field='appearance_group'),dict(offset=2,type='i16',field='start_hour; original selection also reads signed byte+2'),dict(offset=4,type='i16',field='stay_minutes'),dict(offset=6,type='i16',field='budget_yen'),dict(offset=8,type='4*i8',field='primary and3 extra product IDs;-1 is absent'),dict(offset=12,type='i8',field='arrival_mode'),* [dict(offset=13+i,type='i8',field=k) for i,k in enumerate(STATS)],dict(offset=23,type='u8',field='byte23; no semantic assigned')]
 js('customer-data.json',dict(schema_version=1,source_disc_sha256=DISC_SHA,source_exe_sha256=EXE_SHA,source_ranges=ranges,appearance_descriptor_schema=dict(address='0x800a1750',stride=23,count=44,name_field_bytes=21,metadata_offsets=[21,22],metadata_status='inferred semantics; static values confirmed'),profile_schema=dict(address='0x800a09d0',stride=24,count=144,fields=field_layout),buildings=buildings,mixes=mixes,profiles=profiles,appearances=actors,staff_appearance_slots=[dict(slot=i,male_id=role_looks[i*2],female_id=role_looks[i*2+1]) for i in range(3)],worlds=worlds,invalid_reference=anomaly))
 js('android-customer-bridge.json',dict(schema_version=1,source_exe_sha256=EXE_SHA,source_disc_sha256=DISC_SHA,population_heads_by_mix=[m['source_population_heads'] for m in mixes],valid_shopping_profile_heads_by_mix=[m['valid_profile_heads'] for m in mixes],appearance_names=[a['name'] for a in actors],appearance_options_by_group=[a['appearance_options_for_profile_group'] for a in actors],direction_image_offsets=direction_images,staff_role_appearance_pairs=[role_looks[i*2:i*2+2] for i in range(3)],profile_to_appearance_group=[p['appearance_group'] for p in profiles],world_starting_population={w['file']:w['source_population_heads'] for w in worlds},invalid_references=invalid,notes=['Population sums original mix heads even if the profile reference is invalid. Normal shopping data only uses profile IDs0..143.', 'Appearance descriptor age/sex candidates are omitted because their runtime semantic use is unconfirmed.', 'No EXE, original CPU, BIOS or source RAM state is required to read this JSON.']))
 csvfile=io.StringIO();writer=csv.writer(csvfile);writer.writerow(['profile_id','group_id','group_label','appearance_options','start_hour','stay_minutes','budget_yen','primary','extras','arrival_mode',*STATS])
 for x in profiles:writer.writerow([x['id'],x['appearance_group'],x['group_label'],' / '.join(a['name']+':'+str(a['slots'])+'/4' for a in x['appearance_choices']),x['start_hour'],x['stay_minutes'],x['budget_yen'],x['primary_product'],','.join(str(i) for i in x['product_ids'][1:] if i!=-1),x['arrival_mode'],*[x['stats'][k] for k in STATS]])
 (ROOT/'shopping-profiles.csv').write_text('\ufeff'+csvfile.getvalue(),encoding='utf-8')
 js('profile144-analysis.json',anomaly)
 # Source disassembly is evidence of field readers, not a running game test.
 cs=Cs(CS_ARCH_MIPS,CS_MODE_MIPS32|CS_MODE_LITTLE_ENDIAN);asm=[];words=[]
 for start,end,label in [(0x80020498,0x800206ac,'population'),(0x800265ac,0x8002686c,'demand profile handling'),(0x80027328,0x800273a0,'product guard')]:
  asm.append('# '+label)
  for ins in cs.disasm(raw(start,end-start),start):
   asm.append(f'{ins.address:08x} {ins.bytes.hex():8} {ins.mnemonic:8} {ins.op_str}');words.append(dict(address=hex(ins.address),bytes=ins.bytes.hex()))
 (ROOT/'customer-readers.asm').write_text('\n'.join(asm)+'\n');js('reader-words.json',dict(source_exe_sha256=EXE_SHA,instructions=words))
 # Exact original sprite pixels are shown only to make the recovered IDs legible.
 tools=runpy.run_path(str(PREVIOUS/'extract-disc-data.py'));meta,man,indices=tools['tim'](source('/TIM0/MAN0.TIM'));assert (meta['width'],meta['height'])==(256,176)
 (ROOT/'source/MAN0.TIM').write_bytes(source('/TIM0/MAN0.TIM'))
 texture_frames=[];duplicates=collections.defaultdict(list)
 for actor in actors:
  for frame in actor['frames']:
   u,v=frame['uv'];cells=bytes(indices[(v+y)*256+u+x] for y in range(16) for x in range(16));palette_words=b''.join(struct.pack('<H',meta['palette_words'][x]) for x in cells)
   texture_frames.append(dict(appearance_id=actor['id'],image_code=frame['image_code'],direction_name=frame['direction_name'],uv=frame['uv'],indices_sha256=sha(cells),palette_color_words_sha256=sha(palette_words)))
   duplicates[sha(cells)].append(frame['image_code'])
 customer_looks=sorted({j for r in profiles for j in r['appearance_option_ids']});employee_looks=sorted(set(role_looks));all_looks=sorted(set(customer_looks+employee_looks))
 assert customer_looks==list(range(38)) and employee_looks==list(range(38,44)) and all_looks==list(range(44))
 initial_staff=[]
 for name in ('TOWN0001','TOWN0002','TOWN0003','TOWNPS'):
  b=source('/DAT/'+name+'.BIN');staff=[]
  for i in range(35):
   record=b[24017+i*54:24017+(i+1)*54];appearance=struct.unpack_from('<h',record,5)[0];assert 0<=appearance<44
   staff.append(dict(id=i,owner_flags=struct.unpack_from('<H',record)[0],actual_age_byte=record[3],sex_byte=record[4],body_appearance=appearance))
  initial_staff.append(dict(file=name+'.BIN',staff=staff))
 js('person-texture-map.json',dict(source_tim_sha256=sha(source('/TIM0/MAN0.TIM')),dimensions=[256,176],customer_appearance_ids=customer_looks,staff_role_appearance_ids=employee_looks,all_source_table_appearance_ids=all_looks,image_code_min=640,image_code_max=815,all_frames_within_source_image=True,unique_index_tiles=len(duplicates),identical_index_tile_image_codes=[v for v in duplicates.values() if len(v)>1],frames=texture_frames,initial_staff_maps=initial_staff,accepted_but_absent_image_codes=[816,817,818,819],scope='All144 profile appearance choices, six staff-role look IDs and140 initial packed staff records were decoded. These sources only produce appearances0..43. Other code paths were not exhaustively proved unreachable. Descriptor age candidates are not actual NPC ages.',preview_policy='PNG uses decoded source palette, word0 transparent; STP blending is not reproduced.'))
 contact=Image.new('RGB',(896,11*76),(235,235,235));draw=ImageDraw.Draw(contact)
 fontpath=Path('/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc');font=ImageFont.truetype(str(fontpath),12) if fontpath.exists() else ImageFont.load_default()
 for a in actors:
  x=(a['id']%4)*224;y=(a['id']//4)*76;draw.text((x+4,y+2),f"{a['id']:02d} {a['name']}",fill=(0,0,0),font=font)
  for k,frame in enumerate(a['frames']):
   u,v=frame['uv'];assert u+16<=256 and v+16<=176
   im=man.crop((u,v,u+16,v+16)).resize((32,32),Image.Resampling.NEAREST);contact.paste(im,(x+8+k*48,y+23),im);draw.text((x+8+k*48,y+57),frame['direction_name'],fill=(30,30,30))
 contact.save(ROOT/'appearance-contact-sheet.png')
 # Inventory all direct address encodings; absence is not a proof of dead code.
 region=(0x800a1750,0x800a1b44);pointer_hits=[]
 for off in range(2048,len(exe)-4,4):
  value=struct.unpack_from('<I',exe,off)[0]
  if region[0]<=value<region[1]:pointer_hits.append(dict(address=hex(0x80010000+off-2048),target=hex(value)))
 js('summary.json',dict(source_disc_sha256=DISC_SHA,building_rows=69,base_building_rows=59,extension_named_rows=10,mixes=137,shopping_profiles=144,appearance_descriptors=44,appearance_frames=176,appearance_metadata_semantics='sex/age candidates only; no original reader identified',appearance_descriptor_pointer_word_hits=pointer_hits,world_populations=[{k:x[k] for k in ('file','source_population_heads','heads_if_invalid_profile_entries_are_dropped','difference','affected_cells')} for x in worlds],normal_product_guard_excludes_profile144=True,source_cpu_updates=0,known_before=['144 shopping profiles','137 mixes','invalid profile144 reference in mix136'],newly_resolved=['23-byte appearance descriptor boundary, names and candidate metadata','Full building/mix/profile/appearance relationship exported without collapsing duplicate slots','Profile144 aliases the next table label, and ordinary product guard excludes it','Population must retain the invalid entry; dropping it changes the original map totals']))
 print(json.dumps(dict(buildings=69,mixes=137,profiles=144,appearances=44,frames=176,populations=[(x['file'],x['source_population_heads'],x['difference']) for x in worlds],source_cpu_updates=0),ensure_ascii=False))
if __name__=='__main__':main()
