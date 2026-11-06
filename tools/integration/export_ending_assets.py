"""Extract ending artwork and constructor arguments from the original source.

Offline only: needs Pillow and Unicorn; neither is an app/runtime dependency.
Uses original scene setup with resource/drawing/audio boundaries intercepted.
Source: analysis 2c00ba53, source_other_scene_monitor and source_credits_monitor.
"""
import hashlib
import json
from pathlib import Path
import struct
import sys

from PIL import Image
from unicorn import UC_HOOK_CODE
sys.path.insert(0, sys.argv[1])
from check_machine import machine, EXE
from unicorn.mips_const import *
from sprite_record import record

root = Path(__file__).resolve().parents[2]
source = Path(sys.argv[1])
exe = EXE.read_bytes()
assert hashlib.sha256(exe).hexdigest() == 'd6a167a1c9e0fe98d7e44e12968caa489ac3eb7ed3b9e46012a188af8432b1fd'
raw = lambda a, n: exe[a - 0x80010000 + 2048:a - 0x80010000 + 2048 + n]
tables = json.loads((source / 'tim-vram-tables.json').read_text())
out = root / 'game/assets/ending'
out.mkdir(parents=True, exist_ok=True)
window_sets = {}

def texture(index, alternate=None):
    row = tables[index]
    name = row['file'].split('\\')[-1].split(';')[0]
    b = (source / 'source' / name).read_bytes()
    flags = struct.unpack_from('<I', b, 4)[0]
    assert flags & 7 == 1 and flags & 8, (name, flags)
    plen, _, _, pw, ph = struct.unpack_from('<I4H', b, 8)
    palette = b[20:20+pw*ph*2] if alternate is None else alternate
    pos = 8 + plen
    _, _, _, width, height = struct.unpack_from('<I4H', b, pos)
    pixels = b[pos+12:]
    colors = []
    for i in range(len(palette)//2):
        v = struct.unpack_from('<H', palette, i*2)[0]
        colors.append(((v & 31)*255//31, ((v>>5)&31)*255//31,
                       ((v>>10)&31)*255//31, 0 if v == 0 else 255))
    im = Image.new('RGBA', (width*2, height))
    im.putdata([colors[v] for v in pixels[:width*2*height]])
    return im

def scene_setup(index, start, end, credits=False):
    u = machine()
    constructors = []
    loads = []
    windows = []
    window_sets[str(index)] = windows
    targets = set()
    for address in range(start, end, 4):
        instruction = struct.unpack('<I', raw(address, 4))[0]
        if instruction >> 26 == 3:
            targets.add(0x80000000 | ((instruction & 0x3ffffff) << 2))
    def read(a,n): return bytes(u.mem_read(a & 0x1fffffff,n))
    def observe(z,a,n,_):
        if a not in targets: return
        args = [z.reg_read(v) for v in (UC_MIPS_REG_A0,UC_MIPS_REG_A1,UC_MIPS_REG_A2,UC_MIPS_REG_A3)]
        if a == 0x800140e8:
            loads.append(args[0])
        elif a == 0x80017b18:
            windows.append(dict(x=args[0]&65535,y=args[0]>>16,
                                width=args[1]&65535,height=args[1]>>16))
        elif a == 0x80013f7c:
            row = tables[args[0]]
            z.mem_write(args[1] & 0x1fffffff, struct.pack('<4H', *row['pixels']))
            z.mem_write(args[2] & 0x1fffffff, struct.pack('<4H', *row['palette']))
        elif a == 0x80041630:
            kind,tx,ty,clut,ref,r,g,b = struct.unpack_from('<HBBHH3B',read(z.reg_read(UC_MIPS_REG_SP)+16,28))
            mode = struct.unpack('<I',read(z.reg_read(UC_MIPS_REG_SP)+40,4))[0]
            xy,wh = args[2],args[3]
            entry=dict(slot=args[0],x=(xy&65535)-65536 if xy&32768 else xy&65535,
                       y=(xy>>16)-65536 if xy&0x80000000 else xy>>16,
                       width=wh&65535,height=wh>>16,page=kind,u=tx,v=ty,clut=clut,ref=ref)
            # Match original VRAM rectangle to its page/CLUT and crop.
            pagex=(kind&15)*64;pagey=(kind&16)*16
            matches=[i for i in loads if tables[i]['palette'][1] == ref and
                     tables[i]['pixels'][0] == pagex + tx//2 and
                     tables[i]['pixels'][1] <= pagey+ty]
            assert matches, entry
            resource=matches[-1];rect=tables[resource]['pixels']
            left=(pagex-rect[0])*2+tx;top=pagey+ty-rect[1]
            image=texture(resource).crop((left,top,left+entry['width'],top+entry['height']))
            name=f'scene{index}_{args[0]}.png';image.save(out/name)
            entry.update(resource=resource,image=name)
            if index in (1,2) and ref == 494:
                entry['palettes']=[]
                for j,address in enumerate((0x800988f8,0x800987f8)):
                    name=f'scene{index}_{args[0]}_palette{j}.png'
                    # Source uploads only 128 of the 256 palette entries.
                    palette=bytearray((source/'source'/tables[resource]['file'].split('\\')[-1].split(';')[0]).read_bytes()[20:532])
                    palette[:256]=raw(address,256)
                    texture(resource,palette).crop((left,top,left+entry['width'],top+entry['height'])).save(out/name)
                    entry['palettes'].append(name)
            constructors.append(entry)
            pool=0xdae60+args[0]*36
            u.mem_write(pool,record(read(0x80000000+pool,36),xy&65535,xy>>16,wh&65535,wh>>16,kind,tx,ty,clut,ref,(r,g,b),mode))
        elif credits and a == 0x80017718:
            z.emu_stop();return
        z.reg_write(UC_MIPS_REG_V0,0)
        z.reg_write(UC_MIPS_REG_PC,z.reg_read(UC_MIPS_REG_RA))
    u.hook_add(UC_HOOK_CODE,observe)
    u.reg_write(UC_MIPS_REG_RA,0x80001000)
    u.emu_start(start,0x80001000,count=10000000)
    assert constructors
    return constructors

scenes={}
for index,(start,end) in enumerate([(0x800546ac,0x80054aa8),(0x80054aa8,0x80055368),(0x80055368,0x80055c38),(0x80055c38,0x800561cc)]):
    scenes[str(index)]=scene_setup(index,start,end)
scenes['credits']=scene_setup(4,0x80056ff0,0x80057820,True)
messages=root/'assets/raw/ps1_disc_analysis_v1/messages'
atlas=Image.new('RGBA',(384,102*16))
for index in range(102):
    im=Image.open(messages/f'STAFF-{index:03d}.png');atlas.paste(im,(0,index*16))
atlas.save(out/'credits.png')
for index in range(472,476):
    Image.open(messages/f'MSG00-{index:03d}.png').save(out/f'message_{index}.png')
data=dict(source_exe_sha256=hashlib.sha256(exe).hexdigest(),source='analysis 2c00ba53',
          scenes=scenes,windows=window_sets,credits_page_lines=list(raw(0x80010ab0,20)),
          credits_slide_frames=164,credits_hold_frames=186,credits_final_slide_frames=120,scene_audio_dispatcher_ids=[60,60,60,61],credits_bgm_id=6,
          evidence_note='CONFIRMED_BINARY: native constructor parameters and original TIM palettes; credit glyph bitmaps from STAFF.OBJ. Native CPU used only offline to extract bounded setup, all external APIs intercepted. APK uses only Godot/data/PNG. REMAKE_BALANCED_DEFAULT: next button acknowledges source voice completion for touch input; scene/credit frames use 60 Hz presentation time; original window geometry uses a temporary flat panel. GPU semi-transparency and physical audio/vsync timing are not reproduced.')
assert sum(data['credits_page_lines'])==100
(root/'game/data/source_endings.json').write_text(json.dumps(data,separators=(',',':'))+'\n')
print('Extracted four original ending scenes and 102 credit lines', {k:len(v)for k,v in scenes.items()})
