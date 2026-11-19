#!/usr/bin/env python3
"""Export the two original title atlases; input is the recovered source folder.
No generated artwork, executable or archive becomes an app dependency.
"""
import hashlib,json,struct,sys
from pathlib import Path
from PIL import Image
ROOT=Path(__file__).resolve().parents[2]
def export(source):
 out=ROOT/'game/assets/ps1/ui'; hashes={}
 for name in ['TITL0','TITL1']:
  b=(Path(source)/(name+'.TIM')).read_bytes()
  assert struct.unpack_from('<II',b)==(16,9)
  size,_,_,cw,ch=struct.unpack_from('<I4H',b,8);assert (cw,ch)==(256,1)
  palette=struct.unpack_from('<256H',b,20)
  p=8+size;size,_,_,w,h=struct.unpack_from('<I4H',b,p)
  assert (w,h)==(128,256 if name=='TITL0' else 200)
  image=Image.new('RGBA',(w*2,h))
  image.putdata([tuple(((palette[i]>>s)&31)*255//31 for s in (0,5,10))+(0 if palette[i]==0 else 255,) for i in b[p+12:p+size]])
  image.save(out/(name.lower()+'.png'))
  hashes[name+'.TIM']=hashlib.sha256(b).hexdigest()
 (out/'title-source.json').write_text(json.dumps({'source_commit':'3249582e2889fc6dcc70d77f8eba9d54cb385ee3','sha256':hashes,'evidence':'Original title 80057BD4/80058388/80058AEC/80059254; prior archive title-parent-verification-20261028. KABEE CEL 4x4 repeating UV(0..48,72..120) matches KYOU field crop.','menu_texts':['はじめから','つづきから'],'menu_text_positions':[[124,74],[124,90]],'highlight':[48,74,224,16],'cursor':[186,86],'source_logo_rect':[0,0,256,160],'final_logo_position':[32,25],'menu_source_rect':[0,32,256,160],'menu_position':[32,24],'intro_ticks':125,'transition_strip_count':10,'transition_strip_height':16,'timing_note':'60 Hz NTSC animation ticks. Startup company movie and scenario introduction are outside this title implementation.'},ensure_ascii=False,indent=2)+'\n')
if __name__=='__main__':export(sys.argv[1])
