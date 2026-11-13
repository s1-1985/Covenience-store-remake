#!/usr/bin/env python3
"""Static disc extraction: floor tile variants, staffing score, stain/clean rules.
No original CPU execution, long-run simulation, or assumed fixture failure model.
"""
import argparse, collections, hashlib, json, runpy, struct
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
from capstone import Cs,CS_ARCH_MIPS,CS_MODE_MIPS32,CS_MODE_LITTLE_ENDIAN
ROOT=Path(__file__).resolve().parent
DISC_SHA='8d8eda789c5a2fe892a4722719b0466dd7d126eed6cd99ad05a807d81b57d1c1'
EXE_SHA='d6a167a1c9e0fe98d7e44e12968caa489ac3eb7ed3b9e46012a188af8432b1fd'
def sha(b):return hashlib.sha256(b).hexdigest()
def js(name,data):(ROOT/name).write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n')
def main():
    ap=argparse.ArgumentParser();ap.add_argument('disc',type=Path);args=ap.parse_args();disc=args.disc.read_bytes();assert sha(disc)==DISC_SHA
    lib=runpy.run_path(str(ROOT.parent/'20261113-disc-data-extraction/extract-disc-data.py'));files,read=lib['iso'](disc);by={r['path']:r for r in files}
    def payload(name):r=by[name];return read(r['lba'],r['bytes'])
    exe=payload('/SLPS_007.82');assert sha(exe)==EXE_SHA
    def at(a,n):return exe[a-0x80010000+2048:a-0x80010000+2048+n]
    (ROOT/'source').mkdir(exist_ok=True)
    denominators=list(struct.unpack('<6i',at(0x80098d10,24)));assert denominators==[150,150,165,165,180,180]
    layouts=[];prefixes=bytearray();allcounts=collections.Counter()
    for i in range(30):
        a=0x800a2074+i*3108;b=at(a,194);w,h=struct.unpack_from('<2i',b);assert w<=28 and h<=26 and w%2==h%2==0
        counts=collections.Counter(b[12+y*14+x] for y in range(h//2) for x in range(w//2));allcounts.update(counts)
        layouts.append(dict(id=i,address=hex(a),size_subcells=[w,h],prefix_sha256=sha(b),floor_counts=dict(sorted(counts.items()))));prefixes+=b
    assert all(v not in allcounts for v in list(range(1,5))+list(range(6,10))+list(range(11,16)))
    (ROOT/'source/layout-floor-prefixes.bin').write_bytes(prefixes)
    js('layout-floor-counts.json',dict(source_base='0x800a2074',layout_stride=3108,prefix_bytes=194,packed_prefix_file='source/layout-floor-prefixes.bin',floor_offset_in_layout=12,floor_row_stride=14,layouts=layouts,total_counts=dict(sorted(allcounts.items())),normal_base_floor_ids=[0,5,10],note='All30 built-in layouts contain no dirty floor variants1..4,6..9,11..14 and no code15. This is a source-template inventory, not a claim about all later game states.'))
    tim=payload('/TIM0/SYOP_S00.TIM');meta,im,indices=lib['tim'](tim);tiles=[];rawtiles=bytearray()
    canvas=Image.new('RGB',(500,8*94+38),'#dedede');draw=ImageDraw.Draw(canvas);font=ImageFont.truetype('/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc',15)
    draw.text((8,6),'原床タイル0～35（ラベルは内部ID）',font=font,fill='black')
    for code in range(36):
        u=(code&15)*16;v=(code>>4)*16;ix=bytes(indices[(v+y)*meta['width']+u+x] for y in range(16) for x in range(16));rawtiles+=ix
        tiles.append(dict(code=code,uv=[u,v],indices_sha256=sha(ix),normal_family=code//5 if code<15 else None,variant=code%5 if code<15 else None,cleaning_target=0<=code<15 and code%5!=0,counted_as_floor=0<=code<16,counted_clean=0<=code<16 and code%5==0))
        x=code%5*100+10;y=code//5*94+38;draw.text((x,y),str(code),font=font,fill='black');tile=im.crop((u,v,u+16,v+16)).resize((64,64),Image.Resampling.NEAREST);canvas.paste(tile,(x,y+22),tile)
    canvas.save(ROOT/'floor-tiles.png');(ROOT/'source/floor-tile-indices.bin').write_bytes(rawtiles);(ROOT/'source/floor-palette.bin').write_bytes(struct.pack('<256H',*meta['palette_words'][:256]))
    js('floor-tile-map.json',dict(source_tim='/TIM0/SYOP_S00.TIM',source_tim_sha256=sha(tim),source_dimensions=[meta['width'],meta['height']],tiles=tiles,palette_note='Original16-bit palette words preserved. PNG treats word0 as transparent; it is a reference atlas, not full PS1 blending emulation.'))
    score_examples=[dict(level=i,assigned_skills=[50,50,50],score=min(100,150*100//denominators[i])) for i in range(6)]
    # Source-arithmetic boundary example; this is not an executed game trace.
    examples=dict(staffing=score_examples,warning_boundary=dict(floor_tiles=10,clean_before=7,visual_percent_before=70,staff_score=60,eligible_customer_on_clean_floor=True,stains_added=1,clean_after=6,visual_percent_after=60,counter_increments_this_call=False,reason='Counter compares percentage computed before stain write.'),same_floor_variants=[dict(code=c,cleaned_to=c//5*5,stain_choices=list(range(c//5*5+1,c//5*5+5))) for c in range(15)])
    js('derived-examples.json',dict(scope='Arithmetic examples derived from source rules, not gameplay captures.',**examples))
    js('android-floor-cleaning-bridge.json',dict(schema_version=1,source_disc_sha256=DISC_SHA,source_exe_sha256=EXE_SHA,store_fields={'floor_base':'0x4c','floor_grid':'0x50;14-byte row stride','width_subcells':'0x44','height_subcells':'0x48','staff_refs':'0xdd8;3*i16','store_level':'0xc70','dirty_floor_counter':'0x12e4;u8 storage, signed read by adviser'},staff_fields={'cleaning_skill':'0x21; signed byte','target_selection_phase_skill':'0x20; signed byte, semantic label not assigned here'},cleanliness_metric=dict(source_function='0x8002287c',summary_field='+4',denominators=denominators,formula='min(100, trunc_toward_zero(sum(assigned staff cleaning skill)*100 / denominator[level]))',includes='All3 assigned refs except-1; this score function does not filter by task, rest or energy.',not_equal_to='Fraction of clean floor images'),visual_floor=dict(count='0<=signed_tile<16',clean='tile%5==0',percentage='trunc_toward_zero(clean_count*100/floor_count)',normal_material_bases=[0,5,10],stain_variants='base+1..base+4 are alternative patterns selected by one rand()%4; not progressive dirt levels'),stain_update=dict(function='0x80031498',gate='minute field800ce618==0',condition='staff-derived summary+4 < current visual floor percentage',target='First active customer in slots0..19 whose floor cell has code0..15 and remainder0 mod5.',coordinate='signed customer x/y divided by2 with truncation toward zero',write='base=trunc(tile/5)*5; tile=base+rand()%4+1; dirty cache byte+1=0; stop after one successful stain.',counter='If pre-stain visual percentage<70, increment store+12e4 modulo256; independent of whether a new stain was added.'),cleaning_target=dict(function='0x80039618',tile_gate='0<=tile<15 and tile%5!=0',phase_gate='Reject selection when clock%100 <100-signed_staff_byte20.',mark='Mark accessible half-cells in each dirty full floor tile as10001; reservations can exclude another cleaner target.'),clean_action=dict(function='0x80038894',turn='On clock&7==0, direction changes through[1,0,2,3].',random_gate='First rand()%5 must equal0; then another rand()%100+1 must be<=cleaning_skill.',write='tile=trunc_toward_zero(tile/5)*5; cache dirty byte+1=0',on_success='Parent sets sound flag0x800, clears staff target and applies cleaning skill growth.'),advice=dict(function='0x8003b570',own_store_only=True,threshold='signed dirty counter>=4, then rand()%100+1<=manager leadership byte1d',resets='Counters12e1..12e4 reset at minute0 and hour divisible by4, or after advice; rare branch has additional resets.',note='Threshold is not a count of dirty tiles and not an elapsed-hours field.'),unconfirmed='A general fixture breakage/repair system has not been established by these floor/cleaning functions; do not add one from this report.'))
    spans=[('cleaning_score',0x8002287c,0x80022a18),('score_to_summary',0x80023d70,0x80023dcc),('floor_wear',0x80031498,0x800319ac),('clean_action',0x80038894,0x80038ad8),('clean_target',0x80039618,0x8003a3f4),('floor_render',0x800561cc,0x8005643c),('store_advice',0x8003b570,0x8003bf28)]
    md=Cs(CS_ARCH_MIPS,CS_MODE_MIPS32|CS_MODE_LITTLE_ENDIAN);asm=[];ranges=[]
    for name,a,end in spans:
        b=at(a,end-a);(ROOT/'source'/f'{name}.bin').write_bytes(b);ranges.append(dict(name=name,address=hex(a),bytes=len(b),sha256=sha(b)));asm.append(f'\n# {name} {a:#x}..{end:#x}')
        asm.extend(f'{x.address:08x}: {x.bytes.hex()} {x.mnemonic} {x.op_str}' for x in md.disasm(b,a))
    (ROOT/'source/cleaning-denominators.bin').write_bytes(at(0x80098d10,24));ranges.append(dict(name='cleaning_denominators',address='0x80098d10',bytes=24,sha256=sha(at(0x80098d10,24))))
    (ROOT/'floor-readers.asm').write_text('\n'.join(asm)+'\n');js('source-ranges.json',ranges)
    js('summary.json',dict(normal_floor_materials=3,variants_per_material=5,renderable_floor_codes=36,builtin_layouts=30,cleanliness_metric='Assigned employee cleaning skills and store level, not observed clean-tile percentage.',new_work='Connected the staffing metric producer to the floor-stain consumer; decoded floor image families and all30 initial-layout usage; recorded pre-stain warning boundary and whole-tile cleanup.',already_known='Isolated cleaning_score, floor_wear and clean_floor algorithms existed in earlier models. This report links their semantics and actual image data.',unconfirmed='Generic fixture wear/breakage/repair behavior.',original_cpu_updates=0))
    print(json.dumps(dict(layouts=30,normal_floor_codes=[0,5,10],denominators=denominators,score_examples=score_examples)))
if __name__=='__main__':main()
