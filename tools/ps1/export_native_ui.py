#!/usr/bin/env python3
"""Regenerate native PS UI atlases from the existing analysis archive.
Usage: python tools/ps1/export_native_ui.py SOURCE.zip
The archive is a build input only. No original executable is shipped/run.
Metadata mappings are retained in game/assets/ps1/ui/*.json.
"""
from pathlib import Path
import hashlib,json,struct,sys,zipfile
from PIL import Image
from psmoji import TABLE
ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'game/assets/ps1/ui'
def main(archive):
    OUT.mkdir(parents=True,exist_ok=True)
    z=zipfile.ZipFile(archive)
    hashes={}
    def tim(name):
        b=z.read('algorithm-analysis/source/'+name+'.TIM')
        hashes[name+'.TIM']=hashlib.sha256(b).hexdigest()
        magic,flags=struct.unpack_from('<II',b)
        assert magic==16 and flags in (8,9)
        length,_,_,cw,ch=struct.unpack_from('<I4H',b,8)
        assert ch==1
        pal=struct.unpack_from('<%dH'%cw,b,20)
        p=8+length
        length,_,_,width,height=struct.unpack_from('<I4H',b,p)
        pixels=b[p+12:p+length]
        if flags==8: pixels=bytes(n for v in pixels for n in (v&15,v>>4))
        image=Image.new('RGBA',(width*(4 if flags==8 else 2),height))
        image.putdata([tuple(((pal[n]>>shift)&31)*255//31 for shift in (0,5,10))+(0 if pal[n]==0 else 255,) for n in pixels])
        return image
    for bank in range(2): tim('PSMOJI%d'%bank).save(OUT/('font_%d.png'%bank))
    (OUT/'glyphs.json').write_text(json.dumps({s:i for i,s in enumerate(TABLE) if s and len(s)==1},ensure_ascii=False))
    for name,source in [('fixtures','CASE_T00'),('portraits_0','KAO01'),('portraits_1','KAO02'),('stores','SHOPTYP1')]: tim(source).save(OUT/(name+'.png'))
    ky=tim('KYOU')
    for name,rect in [('paper',(160,32,176,48)),('field',(0,72,64,136)),('cursor',(96,16,112,32)),('vacant',(48,136,96,176))]: ky.crop(rect).save(OUT/(name+'.png'))
    # CONFIRMED_VISUAL palette adaptation: the owner's HUD is beige; the
    # original strip uses blue. Preserve grain/geometry, adapt only colors.
    hud=ky.crop((96,184,256,208)).convert('RGB')
    colors=[]
    for rgb in hud.get_flattened_data():
        delta=(sum(rgb)/3-210)*.30
        colors.append(tuple(max(0,min(255,round(k+delta))) for k in (229,224,199)))
    hud.putdata(colors);hud.save(OUT/'hud.png')
    (OUT/'source-hashes.json').write_text(json.dumps(hashes,indent=2)+'\n')
    print('Exported 11 UI atlases/textures; no runtime disc dependency.')
if __name__=='__main__': main(sys.argv[1])
