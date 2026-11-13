#!/usr/bin/env python3
"""Statically decode EXE resource references and relate them to physical disc files."""
import argparse, hashlib, json, struct
from pathlib import Path
from capstone import Cs, CS_ARCH_MIPS, CS_MODE_MIPS32, CS_MODE_LITTLE_ENDIAN
ROOT=Path(__file__).resolve().parent
p=argparse.ArgumentParser();p.add_argument('exe',type=Path);a=p.parse_args();exe=a.exe.read_bytes()
assert hashlib.sha256(exe).hexdigest()=='d6a167a1c9e0fe98d7e44e12968caa489ac3eb7ed3b9e46012a188af8432b1fd'
def raw(addr,n):return exe[addr-0x80010000+2048:addr-0x80010000+2048+n]
def word(addr):return struct.unpack('<I',raw(addr,4))[0]
def text(addr):return raw(addr,len(exe))[0:raw(addr,len(exe)).index(b'\0')].decode('ascii')
def save(name,obj):(ROOT/name).write_text(json.dumps(obj,ensure_ascii=False,indent=2)+'\n')
physical={x['path']:x for x in json.loads((ROOT/'disc-inventory.json').read_text())['files']}
cs=Cs(CS_ARCH_MIPS,CS_MODE_MIPS32|CS_MODE_LITTLE_ENDIAN)
spans=[(0x80013f7c,0x800140e8),(0x80014154,0x80014238),(0x80014278,0x800142ac)]
asm=[];instructions=[]
for start,end in spans:
 for ins in cs.disasm(raw(start,end-start),start):
  asm.append(f'{ins.address:08x} {ins.bytes.hex():8} {ins.mnemonic:8} {ins.op_str}')
  instructions.append(dict(address=hex(ins.address),bytes=ins.bytes.hex(),mnemonic=ins.mnemonic,operands=ins.op_str))
(ROOT/'resource-reader.asm').write_text('\n'.join(asm)+'\n')
paths=[]
for index in range(34):
 ptr=word(0x8009863c+index*4);name=text(ptr);path=name.removesuffix(';1').replace('\\','/')
 row=dict(id=index,path_pointer=hex(ptr),pointer_entry_address=hex(0x8009863c+index*4),path=path,exists_on_disc=path in physical)
 if index<32:
  row.update(pixel_rectangle_address=hex(0x800983d0+index*8),pixel_rectangle=list(struct.unpack('<4H',raw(0x800983d0+index*8,8))),palette_rectangle_address=hex(0x800984d0+index*8),palette_rectangle=list(struct.unpack('<4H',raw(0x800984d0+index*8,8))))
 else:
  row.update(standalone_rectangle_in_32_entry_banks=False,following_memory_if_indexed_as_pixel_rect=list(struct.unpack('<4H',raw(0x800983d0+index*8,8))),note='Filename pointer is present, but there is no separate corresponding row in the32-entry pixel/CLUT banks. This alone does not prove all call paths are dead.')
 paths.append(row)
assert all(x['exists_on_disc'] for x in paths)
assert paths[32]['path']=='/TIM0/SYOP_S03.TIM' and paths[33]['path']=='/TIM0/CASE_T01.TIM'
legacy=[]
for index in range(24):
 ptr=word(0x800986e8+index*4);name=text(ptr);path=name.removesuffix(';1').replace('\\','/')
 legacy.append(dict(id=index,path=path,pointer_entry_address=hex(0x800986e8+index*4),exists_on_disc=path in physical,basename_matches=[n for n in physical if Path(n).name==Path(path).name]))
assert not any(x['exists_on_disc'] for x in legacy)
assert legacy[12]['path']=='/DAT1/SHOP0302.BIN' and legacy[12]['basename_matches']==['/DAT/SHOP0302.BIN']
layouts=json.loads((ROOT/'external-layout.json').read_text());assert layouts['exact_embedded_matches']==[16]
# Re-read all descriptor words rather than deriving icon IDs from their names.
icon_rows=[]
for kind in range(53):
 icon=word(0x80099f0c+kind*196+80)
 icon_rows.append(dict(fixture_kind=kind,descriptor_address=hex(0x80099f0c+kind*196),icon_index_word20=icon,atlas_32px_rect=[(icon%8)*32,(icon//8)*32,32,32]))
assert [x['fixture_kind'] for x in icon_rows if x['icon_index_word20']==54]==[45]
pairs=json.loads((ROOT/'alternate-textures.json').read_text())['pairs'];case=pairs[0]
x0,y0,x1,y1=case['index_difference_bbox'];assert 192<=x0<x1<=224 and 192<=y0<y1<=224
case.update(changed_32px_icon_slots=[54],descriptor_referencing_slot=[45])
save('fixture-icon-map.json',dict(source_exe_sha256=hashlib.sha256(exe).hexdigest(),descriptor_stride=196,icon_field_offset=80,rows=icon_rows,alternate_case_texture_difference=case))
save('resource-tables.json',dict(source_exe_sha256=hashlib.sha256(exe).hexdigest(),tim_filename_pointer_bank='0x8009863c',tim_filename_rows=paths,pixel_rectangle_bank='0x800983d0',clut_rectangle_bank='0x800984d0',rectangle_rows=32,legacy_external_layout_pointer_bank='0x800986e8',legacy_external_layout_rows=legacy,source_instructions=instructions,notes=['Static parsing/disassembly only; no original CPU execution or gameplay update.', 'All34 TIM filenames are present on disc; two filenames extend beyond the32 defined standalone VRAM rectangle entries.', 'All24 literal DAT1/DAT2 layout paths are absent. SHOP0302 exists under DAT and equals embedded layout16 after insertion of two alignment bytes.', 'Do not silently treat basename matches or absent VRAM rows as a complete runtime-load proof.']))
print(json.dumps(dict(tim_paths=len(paths),rectangle_rows=32,absent_legacy_paths=len(legacy),external_embedded_match=16,changed_fixture_icon_slot=54,changed_fixture_descriptor=45)))
