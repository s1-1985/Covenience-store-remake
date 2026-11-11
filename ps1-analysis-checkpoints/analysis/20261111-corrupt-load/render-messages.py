#!/usr/bin/env python3
"""Render actual original message/font records; no complete GPU screen claim."""
import sys,json,base64,hashlib
from pathlib import Path
ROOT=Path(__file__).resolve().parent
algo=Path(sys.argv[1]).resolve();sys.path.insert(0,str(algo))
from check_machine import *
from font_pixels import parse_font,preview_records
from PIL import Image
u=machine();u.reg_write(UC_MIPS_REG_GP,0x800cd6c4)
u.mem_write(0x183e00,(algo/'source/MSG00.OBJ').read_bytes())
for a,n in [(0x143fc0,12),(0x12aa00,1024),(0xdcc80,9216),(0xe3948,32),(0xcd8e4,2),(0xcd8f8,2),(0xcda3c,2)]:u.mem_write(a,bytes(n))
for idx,y in [(0x1e9,40),(0x1f2,100)]:
 for reg,v in zip((UC_MIPS_REG_A0,UC_MIPS_REG_A1,UC_MIPS_REG_A2),(16,y,idx)):u.reg_write(reg,v)
 u.reg_write(UC_MIPS_REG_RA,0x80001000);u.emu_start(0x8004e494,0x80001000,count=3000000)
 assert u.reg_read(UC_MIPS_REG_PC)==0x80001000
assets=json.loads((algo/'font-original-assets.json').read_text())['assets']
fonts=[parse_font(base64.b64decode(x['base64'])) for x in assets]
records=bytes(u.mem_read(0xdcc80,9216));count=struct.unpack('<H',u.mem_read(0xcda3c,2))[0]
preview_records(fonts,records,count).resize((960,720),Image.Resampling.NEAREST).save(ROOT/'original-load-messages.png')
(ROOT/'message-source.json').write_text(json.dumps(dict(message_ids=[0x1e9,0x1f2],glyphs=count,records_sha256=hashlib.sha256(records).hexdigest(),exe_sha256=hashlib.sha256(EXE.read_bytes()).hexdigest(),msg_sha256=hashlib.sha256((algo/'source/MSG00.OBJ').read_bytes()).hexdigest(),limits=['Original message bytes and font pixels; CPU text-only preview, not a complete game screenshot.']),indent=2)+'\n')
