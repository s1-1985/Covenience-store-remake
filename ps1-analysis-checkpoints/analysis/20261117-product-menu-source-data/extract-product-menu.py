#!/usr/bin/env python3
"""Join known product submenu rules to original master, messages and 32px pixels.
No original CPU execution. Existing formulas are not new gameplay discoveries.
"""
import argparse, collections, hashlib, json, runpy, struct, zipfile
from pathlib import Path
from PIL import Image, ImageDraw
from capstone import Cs, CS_ARCH_MIPS, CS_MODE_MIPS32, CS_MODE_LITTLE_ENDIAN
ROOT=Path(__file__).resolve().parent
EXE_SHA='d6a167a1c9e0fe98d7e44e12968caa489ac3eb7ed3b9e46012a188af8432b1fd'
def sha(b): return hashlib.sha256(b).hexdigest()
def put(n,x): (ROOT/n).write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n')
def main():
    ap=argparse.ArgumentParser(); ap.add_argument('archive',type=Path); args=ap.parse_args()
    manifest=json.loads((ROOT.parent.parent/'archives/20261103-r2/manifest.json').read_text())
    assert sha(args.archive.read_bytes())==manifest['sha256']
    z=zipfile.ZipFile(args.archive); exe=z.read('algorithm-analysis/source/SLPS_007.82'); assert sha(exe)==EXE_SHA
    def raw(a,n): return exe[a-0x80010000+2048:a-0x80010000+2048+n]
    for n in ['source','source-reference']: (ROOT/n).mkdir(exist_ok=True)
    prior=json.loads((ROOT.parent/'20261113-product-stock-data/product-fixture-data.json').read_text())
    bindings=json.loads((ROOT.parent/'20261117-texture-runtime-binding-data/texture-bindings.json').read_text())['rows']
    sheets={}; provenance=[]
    for image_id in [1,2]:
        row=bindings[image_id]; name=Path(row['path']).name; b=z.read('algorithm-analysis/source/'+name)
        assert sha(b)==row['source_sha256'] and struct.unpack_from('<II',b)==(16,9)
        clen,cx,cy,cw,ch=struct.unpack_from('<I4H',b,8); assert (cw,ch)==(256,1)
        pal=struct.unpack_from('<256H',b,20); p=8+clen
        plen,px,py,pw,ph=struct.unpack_from('<I4H',b,p); pix=b[p+12:p+plen]
        assert p+plen==len(b) and len(pix)==pw*ph*2 and [pw,ph]==row['destination_pixel_rect_words'][2:]
        rgba=[tuple(((w>>s)&31)*255//31 for s in (0,5,10))+(0 if w==0 else 255,) for w in pal]
        im=Image.new('RGBA',(pw*2,ph)); im.putdata([rgba[n] for n in pix])
        sheets[image_id]=dict(palette=pal,pixels=pix,width=pw*2,height=ph,image=im)
        provenance.append(dict(image_id=image_id,file=name,source_sha256=sha(b),size_pixels=[pw*2,ph],palette_sha256=sha(b[20:8+clen]),destination_pixel_rect_words=row['destination_pixel_rect_words'],destination_clut_rect_words=row['destination_clut_rect_words']))
    assert sheets[1]['palette']==sheets[2]['palette']
    dec=runpy.run_path(str(ROOT.parent/'20261114-staff-roster-growth-data/source-reference/psmoji.py'))['decode']
    msg=z.read('algorithm-analysis/source/MSG00.OBJ'); products=[]; images={}; labeldata=bytearray(); labelrows=[]
    for p in prior['products']:
        pid=p['id']; original=raw(0x8009cdf0+88*pid,88)
        first=struct.unpack_from('<i',original,36)[0]; assert first==p['disc_image_ids'][0]
        runtime=first*3+360; cell=81 if pid==20 else 80 if pid==25 else first
        image_id=1 if cell<64 else 2; local=cell if cell<64 else cell-64
        kind=27 if image_id==1 else 29; sx=local%8*32; sy=local//8*32; sh=sheets[image_id]
        assert sx+32<=sh['width'] and sy+32<=sh['height']
        dest=bindings[image_id]['destination_pixel_rect_words']
        assert ((kind&15)*128+sx-dest[0]*2,((kind>>4)&1)*256+sy-dest[1])==(sx,sy)
        idx=b''.join(sh['pixels'][(sy+y)*sh['width']+sx:(sy+y)*sh['width']+sx+32] for y in range(32))
        colors=b''.join(struct.pack('<H',sh['palette'][v]) for v in idx)
        message_id=71+pid; off=struct.unpack_from('<I',msg,message_id*4)[0]; cs=[]
        while True:
            c=struct.unpack_from('<H',msg,off+2*len(cs))[0]; cs.append(c)
            if c==0x40ff: break
            assert c<672 and len(cs)<50
        label=dec(cs); labelbytes=msg[off:off+len(cs)*2]
        labelrows.append(dict(product=pid,message_id=message_id,source_offset=off,packed_offset=len(labeldata),bytes=len(labelbytes),codes=cs,text=label,sha256=sha(labelbytes))); labeldata.extend(labelbytes)
        products.append(dict(product=pid,master_name=p['name'],display_label=label,message_id=message_id,disc_first_image=first,runtime_first_image=runtime,icon_cell=cell,special_override=pid in (20,25),source_image_id=image_id,source_file=Path(bindings[image_id]['path']).name,source_rect=[sx,sy,32,32],draw_kind=kind,uv=[sx,sy],clut_xy=[0,488],indices_sha256=sha(idx),raw_color_words_sha256=sha(colors),source_complete=True))
        images[pid]=sh['image'].crop((sx,sy,sx+32,sy+32))
    (ROOT/'source/product-labels-71-97.bin').write_bytes(labeldata)
    put('product-labels.json',dict(source='/DAT/MSG00.OBJ',source_sha256=sha(msg),packed_file='source/product-labels-71-97.bin',rows=labelrows))
    put('product-menu-crops.json',dict(rows=products,sources=provenance,source_policy='Raw BGR555/STP words preserved by hashes. Preview uses simple alpha for zero color; not PS GPU compositing.'))
    put('display-label-differences.json',dict(rows=[dict(product=p['product'],master_name=p['master_name'],display_label=p['display_label'],message_id=p['message_id']) for p in products if p['master_name']!=p['display_label']],rule='The selected product label comes from MSG00 message71+product, not the Shift-JIS product master name. Preserve both source forms.'))
    menus=[]; refs=collections.Counter()
    for f in prior['fixtures']:
        b=raw(0x80099f0c+f['id']*196,196); assert list(struct.unpack('<49i',b))==f['raw_words']
        choices=[]
        # Scan the original sentinel, including word33 after a full12-choice list.
        for i in range(13):
            pid=struct.unpack_from('<i',b,84+i*4)[0]
            if pid==-1: break
            assert i<12 and 0<=pid<27
            refs[pid]+=1; col=i%4; row=i//4
            choices.append(dict(slot=i,product=pid,message_id=71+pid,icon_argument_xy=[64+40*col,72+40*row],icon_screen_xy=[80+40*col,88+40*row],icon_record_xy=[-80+40*col,-24+40*row],cursor_argument_xy=[100+40*col,108+40*row]))
        else: raise AssertionError('missing original choice terminator')
        assert [c['product'] for c in choices]==f['allowed_product_ids']
        menus.append(dict(fixture=f['id'],name=f['name'],choices=choices,count=len(choices),first_sentinel_word=21+len(choices),scope='Master-backed choices, not proof every fixture enters this submenu in natural play.'))
    put('fixture-menu-layouts.json',dict(rows=menus,grid_columns=4,grid_max_rows=3,cell_pitch_pixels=[40,40],icon_size_pixels=[32,32],helper_screen_offset=[16,16],source='0x80068D18..0x80068DB8 ->0x80069438; helper records x-144,y-96, rather than usual x-160,y-112.'))
    flagrows=[]
    gates=[(8,0xc74,'たばこ',1),(2,0xc75,'酒類',2),(22,0xc76,'薬品',3)]
    for bits in range(8):
        flags=[(bits>>i)&1 for i in range(3)]; blocked=[dict(product=p,reason=reason) for (p,off,name,reason),v in zip(gates,flags) if v==0]
        flagrows.append(dict(flags=flags,blocked=blocked,disabled_choice_occurrences=sum(refs[x['product']] for x in blocked)))
    put('selection-permission-data.json',dict(gates=[dict(product=p,store_byte_offset=off,label=name,rejection_reason=reason) for p,off,name,reason in gates],combinations=flagrows,enabled_rgb=[128]*3,disabled_rgb=[64]*3,visibility='Denied items stay in their slots with darker modulation; confirm branches to0x80065080 rather than returning the product. Cursor navigation does not skip denied items.',flag_semantics='This report uses raw zero/nonzero permission bytes; it does not infer how each permission is acquired.',source_rule='Known interior_submenu.py and raw0x80068C14..0x80068D18 /0x80069000..0x80069254.'))
    atlas=Image.new('RGB',(9*108,3*112),(36,38,42)); d=ImageDraw.Draw(atlas)
    for i,p in enumerate(products):
        x=i%9*108+6; y=i//9*112+24; pic=images[p['product']].resize((64,64),Image.Resampling.NEAREST); atlas.paste(pic,(x,y),pic)
        d.text((x,y-18),f"P{p['product']:02} cell{p['icon_cell']}",fill='white'); d.text((x,y+68),f"src{p['source_image_id']} {p['source_rect'][:2]}",fill='#bbbbbb')
    atlas.save(ROOT/'product-menu-source-preview.png')
    example=Image.new('RGBA',(208,192),(36,38,42,255))
    for c in menus[0]['choices']: example.alpha_composite(images[c['product']],(c['icon_screen_xy'][0]-56,c['icon_screen_xy'][1]-24))
    example.save(ROOT/'fixture0-product-grid-preview.png')
    spans=[('product_icon_helper',0x80069438,0x8006966c),('product_selection_menu',0x80068978,0x80069438)]
    evidence=[]; asm=[]; cs=Cs(CS_ARCH_MIPS,CS_MODE_MIPS32|CS_MODE_LITTLE_ENDIAN)
    for name,a,e in spans:
        b=raw(a,e-a); fn='source/'+name+'.bin'; (ROOT/fn).write_bytes(b); evidence.append(dict(file=fn,start=hex(a),end_exclusive=hex(e),sha256=sha(b)))
        asm.append('# '+name); asm.extend(f'{x.address:08x}: {x.bytes.hex()} {x.mnemonic} {x.op_str}' for x in cs.disasm(b,a))
    (ROOT/'product-menu-readers.asm').write_text('\n'.join(asm)+'\n')
    (ROOT/'source-reference/interior_submenu.py').write_bytes(z.read('algorithm-analysis/interior_submenu.py'))
    put('android-product-menu-bridge.json',dict(status='analysis_only',android_code_changed=False,products='product-menu-crops.json',menus='fixture-menu-layouts.json',permissions='selection-permission-data.json',labels='product-labels.json',window=dict(screen_xy=[56,24],size_cells=[13,12],size_pixels=[208,192]),selected_product_label=dict(screen_xy=[120,56],message_id='71+product'),navigation=dict(order=['up','down','right','left'],up='index>=4: -4',down='index<8 and index+4<count: +4',right='index not in3,7,11 and index+1<count: +1',left='index not in0,4,8: -1',wrapping=False),limitations=['Master choices are not natural play reachability.','Preview contains icon grid only, not original full window/text/cursor/GPU.','Do not use32px menu imagery as16px interior inventory sprites.','Flag writers/acquisition and natural current-store permission values are outside this report.']))
    put('source-provenance.json',dict(archive_sha256=manifest['sha256'],exe_sha256=EXE_SHA,master_dependencies='20261113-product-stock-data/product-fixture-data.json',images=provenance,raw_exe_ranges=evidence,known_before='Product masters,fixturechoices,iconformula,permissiongates and navigation already recovered. New work joins actual27menu crops,27message labels and53master layouts.',original_cpu_calls=0))
    put('summary.json',dict(products=len(products),product_menu_crops=len(products),source_images=2,fixture_masters=len(menus),nonempty_fixture_menus=sum(x['count']>0 for x in menus),choice_occurrences=sum(refs.values()),max_choices=max(x['count'] for x in menus),special_icon_overrides=[dict(product=p['product'],disc_first_image=p['disc_first_image'],menu_icon_cell=p['icon_cell']) for p in products if p['special_override']],permission_combinations=8,original_cpu_calls=0,operating_updates=0,android_code_changed=False))
    print((ROOT/'summary.json').read_text())
if __name__=='__main__': main()
