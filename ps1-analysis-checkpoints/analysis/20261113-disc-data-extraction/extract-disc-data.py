#!/usr/bin/env python3
"""Static ISO/TIM/layout extraction. Never executes original CPU instructions."""
import argparse, collections, hashlib, json, struct
from pathlib import Path
from PIL import Image, ImageChops, ImageDraw
DISC_SHA='8d8eda789c5a2fe892a4722719b0466dd7d126eed6cd99ad05a807d81b57d1c1'
EXE_SHA='d6a167a1c9e0fe98d7e44e12968caa489ac3eb7ed3b9e46012a188af8432b1fd'
ROOT=Path(__file__).resolve().parent

def sha(b):return hashlib.sha256(b).hexdigest()
def write_json(name,data):
 p=ROOT/name;p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n')
def record(b):
 n=b[32];lba,size=struct.unpack_from('<II',b,2)[0],struct.unpack_from('<I',b,10)[0]
 assert lba==struct.unpack_from('>I',b,6)[0] and size==struct.unpack_from('>I',b,14)[0]
 return dict(lba=lba,bytes=size,flags=b[25],name=b[33:33+n])
def iso(raw):
 def read(lba,size):return b''.join(raw[(lba+j)*2352+24:(lba+j)*2352+2072] for j in range((size+2047)//2048))[:size]
 pvd=read(16,2048);assert pvd[:7]==b'\x01CD001\x01';out=[]
 def walk(r,parent):
  data=read(r['lba'],r['bytes']);pos=0
  while pos<len(data):
   n=data[pos]
   if not n:pos=(pos//2048+1)*2048;continue
   c=record(data[pos:pos+n]);pos+=n
   if c['name'] in (b'\0',b'\1'):continue
   path=parent+'/'+c.pop('name').decode('ascii').split(';')[0]
   if c['flags']&2:walk(c,path)
   else:out.append(dict(path=path,**c))
 walk(record(pvd[156:156+pvd[156]]),'');return out,read

def tim(blob):
 magic,flags=struct.unpack_from('<2I',blob);assert magic==16
 mode=flags&7;pos=8;palette=[];clut=None
 if flags&8:
  length,x,y,w,h=struct.unpack_from('<I4H',blob,pos);assert length==12+2*w*h
  palette=list(struct.unpack_from('<'+'H'*(w*h),blob,pos+12));clut=dict(x=x,y=y,width=w,height=h,words=palette);pos+=length
 length,x,y,w,h=struct.unpack_from('<I4H',blob,pos);pixels=blob[pos+12:pos+length];assert pos+length==len(blob) and len(pixels)==w*h*2
 width=w*4 if mode==0 else w*2 if mode==1 else w
 if mode==0:indices=[v for x in pixels for v in (x&15,x>>4)]
 elif mode==1:indices=list(pixels)
 else:raise ValueError('Unexpected TIM mode '+str(mode))
 assert len(indices)==width*h
 colors=palette[:16 if mode==0 else 256]
 def rgba(word):
  c=[((word>>s)&31)*255//31 for s in (0,5,10)]
  return tuple(c+[0 if word==0 else 255])
 im=Image.new('RGBA',(width,h));im.putdata([rgba(colors[v]) for v in indices])
 return dict(mode=mode,flags=flags,width=width,height=h,source_pixel_rect=[x,y,w,h],palette_rect=[clut[k] for k in ('x','y','width','height')],palette_sha256=sha(blob[20:pos]),pixel_bytes_sha256=sha(pixels),palette_words=palette,pixel_data_offset=pos+12,pixel_data_bytes=len(pixels)),im,indices

def main():
 p=argparse.ArgumentParser();p.add_argument('disc',type=Path);args=p.parse_args();raw=args.disc.read_bytes();assert sha(raw)==DISC_SHA
 rows,read=iso(raw);by={r['path']:r for r in rows};payload=lambda name:read(by[name]['lba'],by[name]['bytes'])
 exe=payload('/SLPS_007.82');assert sha(exe)==EXE_SHA
 def at(a,n):return exe[a-0x80010000+2048:a-0x80010000+2048+n]
 inventory=[];images={};tim_rows=[]
 for r in rows:
  sectors=range(r['lba'],r['lba']+(r['bytes']+2047)//2048)
  forms=collections.Counter('form2' if raw[j*2352+18]&32 else 'form1' for j in sectors)
  d=payload(r['path']);entry=dict(**r,sector_forms=dict(forms),iso_projection_sha256=sha(d))
  if r['path'].endswith('.TIM'):
   meta,im,_=tim(d);images[r['path']]=im;tim_rows.append(dict(path=r['path'],source_sha256=sha(d),**meta));entry['format']='TIM'
  elif r['path']=='/3MIN.BIN':entry.update(format='zero_payload',nonzero_bytes=sum(x!=0 for x in d))
  elif r['path']=='/SOUND.XA':entry['format']='XA_interleaved_raw_sectors';entry['projection_note']='ISO2048 projection is not the XA audio payload.'
  else:entry['format']=r['path'].rsplit('.',1)[-1]
  inventory.append(entry)
 write_json('disc-inventory.json',dict(disc_sha256=DISC_SHA,disc_bytes=len(raw),files=inventory))
 write_json('tim-catalog.json',dict(source_disc_sha256=DISC_SHA,files=tim_rows,preview_policy='First CLUT palette; PS1 word0 transparent, other words opaque. STP and all raw words preserved; no claim of GPU blending equivalence.'))
 pairs=[('/TIM0/CASE_T00.TIM','/TIM0/CASE_T01.TIM'),('/TIM0/SYOP_S00.TIM','/TIM0/SYOP_S03.TIM')];differences=[]
 for left,right in pairs:
  a=payload(left);b=payload(right);ma,ia,aa=tim(a);mb,ib,bb=tim(b);assert ia.size==ib.size
  changed=[(j%ia.width,j//ia.width) for j,(x,y) in enumerate(zip(aa,bb)) if x!=y]
  tiles=collections.Counter((x//16,y//16) for x,y in changed)
  differences.append(dict(baseline=left,alternate=right,same_palette=ma['palette_words']==mb['palette_words'],changed_pixel_indices=len(changed),changed_tiles=[dict(x=x,y=y,pixels=n) for (x,y),n in sorted(tiles.items())],index_difference_bbox=[min(x for x,y in changed),min(y for x,y in changed),max(x for x,y in changed)+1,max(y for x,y in changed)+1]))
  stem=Path(right).stem;out=ROOT/'source';out.mkdir(exist_ok=True);(out/(stem+'.TIM')).write_bytes(b);images[right].save(out/(stem+'.png'))
  stp=Image.new('L',ib.size);stp.putdata([255 if mb['palette_words'][i]&0x8000 else 0 for i in bb]);stp.save(out/(stem+'-stp.png'))
 write_json('alternate-textures.json',dict(pairs=differences))
 contact=Image.new('RGB',(800,1056),(32,32,32));draw=ImageDraw.Draw(contact)
 for row,(left,right) in enumerate(pairs):
  for col,name in enumerate((left,right)):
   im=images[name].resize((384,int(images[name].height*1.5)),Image.Resampling.NEAREST);x=col*400+8;y=row*528+24
   draw.text((x,row*528+5),name,fill='white');contact.paste(im,(x,y),im)
 contact.save(ROOT/'alternate-textures-preview.png')
 # File record layout matches the source layout structures, including unused tail bytes.
 external=payload('/DAT/SHOP0302.BIN');w,h,unknown=struct.unpack_from('<3i',external);assert 0<w<=28 and 0<h<=26
 floor=[[external[12+y*14+x] for x in range(w//2)] for y in range(h//2)]
 words=[[struct.unpack_from('<I',external,194+y*112+x*4)[0] for x in range(w)] for y in range(h)]
 desc=[struct.unpack('<49i',at(0x80099f0c+i*196,196)) for i in range(53)]
 anchors=[]
 for y,line in enumerate(words):
  for x,v in enumerate(line):
   if not v&0x80000000:continue
   kind=v>>12&1023;rotation=v>>22&3;stock=words[y+1][x] if y+1<h else 0
   anchors.append(dict(x=x,y=y,kind=kind,rotation=rotation,raw_word=f'{v:08x}',stock_word_below=f'{stock:08x}',raw_stock_image=(stock>>12)&1023,raw_stock_quantity=(stock>>24)&127,descriptor_words=list(desc[kind]) if kind<53 else None))
 embedded=[]
 for j in range(30):
  row=at(0x800a2074+j*3108,3108);same_dimensions=struct.unpack_from('<2i',row)==(w,h)
  embedded.append(dict(index=j,width=struct.unpack_from('<i',row)[0],height=struct.unpack_from('<i',row,4)[0],matching_dimensions=same_dimensions,shared_prefix_bytes_compared=min(len(external),len(row)),different_bytes_after_alignment=sum(a!=b for a,b in zip(row,external[:194]+b'\0\0'+external[194:])),exact_equal_after_alignment=row==external[:194]+b'\0\0'+external[194:]))
 (ROOT/'source/SHOP0302.BIN').write_bytes(external)
 write_json('external-layout.json',dict(source='/DAT/SHOP0302.BIN',source_sha256=sha(external),bytes=len(external),width_subcells=w,height_subcells=h,header_word_at_8=unknown,floor=floor,grid_words=[[f'{x:08x}' for x in line] for line in words],anchors=anchors,tail_offset=194+h*112,tail_hex=external[194+h*112:].hex(),embedded_layout_comparison=embedded,exact_embedded_matches=[x['index'] for x in embedded if x['exact_equal_after_alignment']],grid_offset=194,embedded_grid_offset=196,interpretation_note='External file is3106 bytes; embedded layout records are3108. Active24x24 grid fits entirely. Grid starts at194, versus196 in embedded records. Last224 bytes are preserved as tail, never filled with invented data. Inserting two zero alignment bytes at194 makes the complete file equal to embedded layout16, with no other transformation. Anchor descriptors are source EXE rows; shop-floor/header field naming limited to known readers.'))
 # Link every file to literal path occurrences, without assuming absence proves dead code.
 references=[]
 for name in by:
  needle=name.replace('/','\\').encode('ascii')+b';1\0';hits=[];pos=0
  while (pos:=exe.find(needle,pos))!=-1:hits.append(dict(exe_file_offset=pos,ram_address=hex(0x80010000+pos-2048)));pos+=1
  references.append(dict(path=name,exact_iso_path_string_hits=hits))
 write_json('exe-file-path-references.json',dict(source_exe_sha256=EXE_SHA,files=references,limits='Literal exact filename search only; no-reference files can still be opened by constructed names.'))
 summary=dict(disc_files=len(rows),tim_files=len(tim_rows),source_exe_sha256=EXE_SHA,source_disc_sha256=DISC_SHA,zero_padding=next(x for x in inventory if x['path']=='/3MIN.BIN'),new_alternate_textures=differences,external_layout=dict(width=w,height=h,anchor_count=len(anchors),nonwall_anchors=sum(a['kind']<53 for a in anchors)),runtime_cpu_updates=0)
 write_json('summary.json',summary);print(json.dumps({k:v for k,v in summary.items() if k not in ('zero_padding','new_alternate_textures')},ensure_ascii=False))
if __name__=='__main__':main()
