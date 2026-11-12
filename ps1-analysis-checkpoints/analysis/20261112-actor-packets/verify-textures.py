#!/usr/bin/env python3
"""Bind observed native packets to bytes inside MAN0.TIM without rasterization."""
import hashlib,json,struct,sys,zlib
from pathlib import Path
ROOT=Path(__file__).resolve().parent
algo=Path(sys.argv[1]).resolve()
def sha(b):return hashlib.sha256(b).hexdigest()
blob=(algo/'source/MAN0.TIM').read_bytes()
manifest=json.loads((algo/'tim-source-transfer-manifest.json').read_text())
def rows(x):
    if isinstance(x,dict):
        if x.get('file')=='\\TIM0\\MAN0.TIM;1':yield x
        else:
            for v in x.values():yield from rows(v)
    elif isinstance(x,list):
        for v in x:yield from rows(v)
entry,=rows(manifest)
assert sha(blob)==entry['sha256']=='6a7349c4fc655fb6b2d441f5332d07481329e03391816849da62485a3ffb2ae4'
magic,flags=struct.unpack_from('<2I',blob);assert magic==16 and flags==9
palette_size,px,py,pw,ph=struct.unpack_from('<I4H',blob,8)
pixel_offset=8+palette_size
pixel_size,x,y,ww,height=struct.unpack_from('<I4H',blob,pixel_offset)
assert (px,py,pw,ph)==(0,480,256,1) and (x,y,ww,height)==(0,0,128,176)
assert entry['destination_pixel_rectangle']==[320,0,128,256] and entry['palette_destination_rectangle']==[0,493,256,1]
indices=blob[pixel_offset+12:pixel_offset+pixel_size];palette=blob[20:532]
assert len(indices)==256*176 and len(palette)==512
proof=json.loads(zlib.decompress((ROOT/'results.json.zlib').read_bytes()))
assert proof['all_passed']
unique={};count=0
for frame in proof['cases']:
    for packet in frame['packets']:
        tag,mode,color,xy,uv,wh=struct.unpack('<6I',bytes.fromhex(packet['packet_hex']))
        assert ((mode>>7)&3)==1 # native draw-mode is 8-bit indexed
        pagex,pagey=(mode&15)*64,((mode>>4)&1)*256
        clut=uv>>16;clutx,cluty=(clut&63)*16,(clut>>6)&511
        assert [pagex,pagey]==[320,0] and [clutx,cluty]==[0,493]
        u,v=uv&255,(uv>>8)&255;w,h=wh&65535,wh>>16
        assert w==h==16 and u+w<=256 and v+h<=176
        cells=b''.join(indices[(v+dy)*256+u:(v+dy)*256+u+w] for dy in range(h))
        # Preserve exact PS1 15-bit color plus STP, without choosing alpha/blending.
        colors=b''.join(palette[k*2:k*2+2] for k in cells)
        image=packet['source_actor']['image']
        rec=dict(image=image,uv=[u,v],size=[w,h],pixel_indices_sha256=sha(cells),color_words_sha256=sha(colors),
                 pixel_indices_hex=cells.hex(),ps1_color_words_hex=colors.hex())
        assert image not in unique or unique[image]==rec
        unique[image]=rec;count+=1
assert count==proof['packets']==544
output=dict(all_passed=True,native_packets_checked=count,unique_observed_images=len(unique),source_file='source/MAN0.TIM',
            source_sha256=sha(blob),source_dimensions=[256,176],requested_upload_dimensions=[256,256],
            palette_source_xy=[0,480],palette_destination_xy=[0,493],texture_page_xy=[320,0],
            cases=[unique[k] for k in sorted(unique)],
            limits=['Exact source texel indices and original 16-bit palette words, not GPU rasterization or alpha/semitransparency emulation.',
                    'The archived native upload requests 256 rows although the TIM file contains 176. All observed samples end at or before row 176; no missing rows are invented.',
                    'Only the 14 observed image codes are bound here. Code acceptance range 640..819 does not prove every code has bytes in this TIM.'])
(ROOT/'texture-results.json.zlib').write_bytes(zlib.compress((json.dumps(output,indent=2)+'\n').encode(),9))
(ROOT/'texture-summary.json').write_text(json.dumps({k:v for k,v in output.items() if k!='cases'},indent=2)+'\n')
print(json.dumps({k:output[k] for k in ('all_passed','native_packets_checked','unique_observed_images')}))
