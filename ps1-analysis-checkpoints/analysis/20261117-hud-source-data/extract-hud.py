#!/usr/bin/env python3
"""Bind known HUD producers to original message bytes, font pixels and background.
Static extraction only; no original CPU execution.
"""
import argparse, hashlib, json, runpy, struct, zipfile
from pathlib import Path
from PIL import Image, ImageDraw
from capstone import Cs, CS_ARCH_MIPS, CS_MODE_MIPS32, CS_MODE_LITTLE_ENDIAN
ROOT = Path(__file__).resolve().parent
EXE_SHA = 'd6a167a1c9e0fe98d7e44e12968caa489ac3eb7ed3b9e46012a188af8432b1fd'
def sha(b): return hashlib.sha256(b).hexdigest()
def put(n, x): (ROOT/n).write_text(json.dumps(x, ensure_ascii=False, indent=2)+'\n')
def main():
    ap=argparse.ArgumentParser(); ap.add_argument('archive', type=Path); args=ap.parse_args()
    manifest=json.loads((ROOT.parent.parent/'archives/20261103-r2/manifest.json').read_text())
    assert sha(args.archive.read_bytes()) == manifest['sha256']
    z=zipfile.ZipFile(args.archive); exe=z.read('algorithm-analysis/source/SLPS_007.82')
    assert sha(exe)==EXE_SHA
    def raw(a,n): return exe[a-0x80010000+2048:a-0x80010000+2048+n]
    (ROOT/'source').mkdir(exist_ok=True)
    dec=runpy.run_path(str(ROOT.parent/'20261114-staff-roster-growth-data/source-reference/psmoji.py'))['decode']
    msg=z.read('algorithm-analysis/source/MSG00.OBJ'); messages=[]; glyphs=set(range(10))|{0x24,0x2c,0x2e}
    for i in range(60,71):
        p=struct.unpack_from('<I',msg,i*4)[0]; cs=[]; tokens=[]; j=0
        while True:
            c=struct.unpack_from('<H',msg,p+2*j)[0]; cs.append(c); j+=1
            if c in (0x4009,0x4004):
                a=struct.unpack_from('<H',msg,p+2*j)[0]; cs.append(a); j+=1
                tokens.append(dict(command=hex(c),argument=a,field=(['year','month','stage_day','hour','minute'][a] if c==0x4009 else 'money')))
            elif c==0x40ff: break
            else:
                assert c<672; glyphs.add(c); tokens.append(dict(glyph=c,text=dec([c])))
        assert j<32
        b=msg[p:p+2*j]; fn=f'source/message-{i}.bin'; (ROOT/fn).write_bytes(b)
        messages.append(dict(id=i,offset=p,byte_length=len(b),codes=cs,tokens=tokens,source_file=fn,sha256=sha(b)))
    assert messages[0]['codes']==[0x4009,0,0xe4,0xe5,0x4009,1,0xe6,0x4009,2,0xe7,0x40ff]
    assert messages[1]['codes']==[0x4009,3,0x2b,0x4009,4,0x4004,0,0x40ff]
    put('hud-messages.json',dict(source='/DAT/MSG00.OBJ',source_sha256=sha(msg),rows=messages,scope='Commands and their arguments are parsed before glyph collection; argument0 is not an extra visible zero.'))
    # Indexed 4-bit source font; use original raw palette words rather than Unicode fonts.
    fontrows=[]; fontimages=[]; fonts=[]
    for bank in range(2):
        name=f'PSMOJI{bank}.TIM'; b=z.read('algorithm-analysis/source/'+name)
        assert struct.unpack_from('<II',b)==(16,8)
        clen,cx,cy,cw,ch=struct.unpack_from('<I4H',b,8); assert (cw,ch)==(16,1)
        pal=struct.unpack_from('<16H',b,20); p=8+clen
        plen,px,py,pw,ph=struct.unpack_from('<I4H',b,p)
        assert (pw,ph)==(64,256) and p+plen==len(b)
        pix=bytes(v for x in b[p+12:] for v in (x&15,x>>4))
        rgba=[tuple(((w>>s)&31)*255//31 for s in (0,5,10))+(0 if w==0 else 255,) for w in pal]
        im=Image.new('RGBA',(256,256)); im.putdata([rgba[v] for v in pix]); fontimages.append(im); fonts.append((pix,pal))
        fontrows.append(dict(file=name,source_sha256=sha(b),source_size_pixels=[256,256],source_pixel_rect_words=[px,py,pw,ph],source_clut_rect_words=[cx,cy,cw,ch]))
    assert fonts[0][1]==fonts[1][1]
    crops=[]; atlas=Image.new('RGB',(10*78,((len(glyphs)+9)//10)*66),(35,35,35)); d=ImageDraw.Draw(atlas)
    for i,c in enumerate(sorted(glyphs)):
        bank=c//336; k=c%336; u=k%21*12; v=k//21*16; pix,pal=fonts[bank]
        indices=b''.join(pix[(v+y)*256+u:(v+y)*256+u+12] for y in range(15))
        colors=b''.join(struct.pack('<H',pal[n]) for n in indices)
        crops.append(dict(glyph=c,text=dec([c]),font_bank=bank,source_rect=[u,v,12,15],draw_kind=15 if bank==0 else 31,clut_xy=[0,480],indices_sha256=sha(indices),raw_color_words_sha256=sha(colors)))
        x=i%10*78+5; y=i//10*66+18; pic=fontimages[bank].crop((u,v,u+12,v+15)).resize((24,30),Image.Resampling.NEAREST)
        atlas.paste(pic,(x,y),pic); d.text((x,y-14),f'{c:03x}',fill='white')
    atlas.save(ROOT/'hud-glyph-source-preview.png')
    put('hud-font-crops.json',dict(fonts=fontrows,glyphs=crops,scope='Fixed 12x15 glyph record path only. Digits0..9, money prefix/sign/separator plus literal HUD text. Not all font glyphs or style2. Raw BGR555/STP preserved by hashes; PNG is a reference, not PS GPU compositing.'))
    # Known HUD background producer: two identical 160x24 sprites.
    b=z.read('algorithm-analysis/source/KYOU.TIM'); assert struct.unpack_from('<II',b)==(16,9)
    clen,cx,cy,cw,ch=struct.unpack_from('<I4H',b,8); pal=struct.unpack_from('<256H',b,20); p=8+clen
    plen,px,py,pw,ph=struct.unpack_from('<I4H',b,p); pix=b[p+12:p+plen]
    assert (pw*2,ph)==(256,240) and (cx,cy)==(0,480)
    binding=json.loads((ROOT.parent/'20261117-texture-runtime-binding-data/texture-bindings.json').read_text())['rows'][8]
    assert binding['source_sha256']==sha(b) and binding['destination_pixel_rect_words'][:2]==[448,0] and binding['destination_clut_rect_words'][:2]==[0,492]
    indices=b''.join(pix[(184+y)*256+96:(184+y)*256+256] for y in range(24))
    rgba=[tuple(((w>>s)&31)*255//31 for s in (0,5,10))+(0 if w==0 else 255,) for w in pal]
    tile=Image.new('RGBA',(160,24)); tile.putdata([rgba[n] for n in indices]); bg=Image.new('RGBA',(320,24)); bg.paste(tile,(0,0)); bg.paste(tile,(160,0)); bg.save(ROOT/'hud-background-source-preview.png')
    background=dict(source_file='KYOU.TIM',source_sha256=sha(b),source_rect=[96,184,160,24],draw_kind=7,uv=[96,184],clut_xy=[0,492],indices_sha256=sha(indices),raw_color_words_sha256=sha(b''.join(struct.pack('<H',pal[n]) for n in indices)),records=[dict(screen_xy=[i*160,0],record_xy=[-160+i*160,-112],size=[160,24]) for i in range(2)],screen_origin=[160,112],source_rows=[184,207],original_image_height=240,requested_upload_height=256)
    put('hud-background.json',background)
    weather=json.loads((ROOT.parent/'20261116-weather-demand-data/monthly-weather-hud.json').read_text())
    put('android-hud-bridge.json',dict(status='analysis_only',android_code_changed=False,background=background,
        text_calls=[dict(order=0,message_id=60,screen_xy=[8,6],record_xy=[-152,-106]),dict(order=1,message_id='62 + monthly selector',screen_xy=[108,6],record_xy=[-52,-106]),dict(order=2,message_id=61,screen_xy=[152,6],record_xy=[-8,-106])],
        calendar_cache=dict(address='0x8014C270',fields=['year','month','stage_day','hour','minute'],source_tick='unsigned32 at0x800CD93C',year='((t * 0xF2B9D649) >> 48) + 1',month='(((t >> 7) * 0x05B05B08) >> 32) % 12 + 1',stage_day='((((t >> 5) * 0x05B05B06) >> 32) & 3) + 1',hour='(((t * 0x88888889) >> 37) % 24)',minute='(t - 60 * ((t * 0x88888889) >> 37)) & 0xFFFFFFFF',warning='Source stage_day1..4 is shown with 日. Do not substitute a real-world28..31day month.'),
        money=dict(source='signed32 at0x800CD9F8 copiedto0x800E4000',command='0x4004,slot0',format='Variable width; glyph0x24 prefix, glyph0x2C every3 digits, optional preceding glyph0x2E for negative; INT32_MIN maps to0 in recovered source routine.',prefix=dec([0x24]),separator=dec([0x2c]),negative=dec([0x2e]),anchor='Immediately after HH:MM; no separate money anchor or fixed money field width in message61.'),
        two_digit_command=dict(command='0x4009',rule='Emit two zero glyphs; write at most two decimal digits from the right. Years>=100 lose higher digits in this formatter. Valid calendar values are nonnegative.',note='This is known original expansion behavior, not a newly discovered gameplay rule.'),
        weather_months=[dict(month=r['month'],messages=[x['message'] for x in r['hud']]) for r in weather['months']],
        glyphs='hud-font-crops.json',messages='hud-messages.json',limitations=['No natural HUD screen execution or full GPU image reconstructed.','No assumption of the current global text style; 12x15 glyph crop coverage is for the fixed record path, style2 bank layout is outside this report.','No proof of all money/year ranges during normal play, clipping, or screen overlap.']))
    spans=[('hud_producer',0x8004095c,0x800411b8),('calendar_readers',0x80019eb4,0x8001a098),('fixed_text_path',0x800153ec,0x800155d0),('glyph_record',0x80015fcc,0x800162d4)]
    cs=Cs(CS_ARCH_MIPS,CS_MODE_MIPS32|CS_MODE_LITTLE_ENDIAN); evidence=[]; asm=[]
    for name,a,e in spans:
        b=raw(a,e-a); fn='source/'+name+'.bin'; (ROOT/fn).write_bytes(b); evidence.append(dict(file=fn,start=hex(a),end_exclusive=hex(e),sha256=sha(b)))
        asm.append('# '+name); asm.extend(f'{x.address:08x}: {x.bytes.hex()} {x.mnemonic} {x.op_str}' for x in cs.disasm(b,a))
    (ROOT/'hud-readers.asm').write_text('\n'.join(asm)+'\n')
    (ROOT/'source/message-pointers-60-70.bin').write_bytes(msg[60*4:71*4])
    refs=['hud_display.py','text_controls.py','text_render.py','font_pixels.py']
    (ROOT/'source-reference').mkdir(exist_ok=True)
    for name in refs: (ROOT/'source-reference'/name).write_bytes(z.read('algorithm-analysis/'+name))
    for name in ['text-control-expansion.asm','text-glyph-render.asm']:
        (ROOT/'source-reference'/name).write_bytes(z.read('algorithm-analysis/evidence/'+name))
    put('source-provenance.json',dict(archive_sha256=manifest['sha256'],exe_sha256=EXE_SHA,msg_sha256=sha(msg),exe_ranges=evidence,known_before='HUD call positions,calendar/expansion/font formulas and weather selectors already recovered. New contribution is raw11messages plus required literal/dynamic glyph and background pixel binding.',original_cpu_calls=0))
    put('summary.json',dict(raw_messages=11,required_glyph_crops=len(crops),font_banks=2,background_source_crops=1,background_draw_records=2,text_call_anchors=3,original_cpu_calls=0,operating_updates=0,android_code_changed=False))
    print((ROOT/'summary.json').read_text())
if __name__=='__main__': main()
