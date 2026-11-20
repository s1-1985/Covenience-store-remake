"""Decode original celebration and festival artwork; no synthetic pixels.
Run from the repository root. Native 320x240 positioning comes from52A88/52DBC.
"""
from pathlib import Path
import hashlib,json,struct
from PIL import Image
ROOT=Path(__file__).resolve().parents[2]
source=ROOT/'assets/raw/ps1_disc_analysis_v1/files/TIM0'
out=ROOT/'game/assets/ps1/ui';out.mkdir(exist_ok=True)
def tim(name):
 b=(source/name).read_bytes();assert struct.unpack_from('<II',b)==(16,9)
 n,_,_,cw,ch=struct.unpack_from('<I4H',b,8);assert (cw,ch)==(256,1)
 palette=struct.unpack_from('<256H',b,20);p=8+n;n,_,_,w,h=struct.unpack_from('<I4H',b,p)
 im=Image.new('RGBA',(w*2,h));im.putdata([tuple(((palette[i]>>s)&31)*255//31 for s in (0,5,10))+(0 if palette[i]==0 else 255,) for i in b[p+12:p+n]])
 return im,hashlib.sha256(b).hexdigest()
im,ih=tim('IOLE.TIM');im.save(out/'calendar_idols.png')
im,fh=tim('PS_CM1.TIM');im.crop((192,128,224,160)).save(out/'calendar_festival.png')
b=(ROOT/'assets/raw/ps1_disc_analysis_v1/files/SLPS_007.82').read_bytes()
raw=lambda a,n:b[a-0x80010000+2048:a-0x80010000+2048+n]
assert struct.unpack('<4H',raw(0x800983d0+18*8,8))==(832,352,128,144)
assert struct.unpack('<4H',raw(0x800983d0+16*8,8))==(832,352,128,160)
metadata={'evidence_note':'REMAKE_BALANCED_DEFAULT: map120 source draw-wait calls to120 native rendered UI updates, accept field tap as0x60, restart the voice after reload; game rules/artwork/bounds remain recovered.','source_exe_sha256':hashlib.sha256(b).hexdigest(),'source_sha256':{'IOLE.TIM':ih,'PS_CM1.TIM':fh},'evidence':'52A88/52DBC sprite/paper/text positions; 983D0 resource16/18 VRAM rects; sprite29 page base(832,256); festival UV192,224 relative uploaded y352 -> crop192,128. Native text uses readable font.','festival':{'resource':16,'sound':58,'icon_rect':[48,56,32,32],'paper_rect':[48,48,224,64],'text_position':[80,64],'message':470},'celebration':{'resource':18,'sound':59,'variants':[{'source':[0,0,120,144],'destination':[8,48,120,144]},{'source':[120,0,96,144],'destination':[8,48,96,144]}],'paper_rect':[80,96,240,64],'text_position':[96,112],'message':471},'wait_calls':120,'timing_note':'Original 120 draw-wait calls then source audio idle or input mask0x60; native adapter counts120 rendered presentation updates, independently of simulation speed. Not a proved fixed two-second source duration.'}
(out/'calendar-source.json').write_text(json.dumps(metadata,ensure_ascii=False,indent=2)+'\n')
print('Exported original calendar sprites')
