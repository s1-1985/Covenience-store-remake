"""Reuse previously recovered runtime conversion; now execute originalstartup caller."""
from check_machine import *
from interior_catalog import IMAGES as DISC_IMAGES,TILES as DISC_TILES,raw
from runtime_tables import runtime_product_images
from recovered import i32
IMAGES=runtime_product_images(DISC_IMAGES)
TILES={key:tuple(i32(v+60) for v in row) for key,row in DISC_TILES.items()}
def startup(u):
 u.emu_start(0x80011c80,0x80011c88,count=500000)
 assert u.reg_read(UC_MIPS_REG_PC) in (0x80011c88,0x80011c84)
 for j,row in enumerate(IMAGES):assert tuple(struct.unpack('<12i',u.mem_read(0x9ce14+j*88,48)))==tuple(row)
 for j in range(101):assert tuple(struct.unpack('<4i',u.mem_read(0x9c7a0+j*16,16)))==tuple(i32(v+60) for v in struct.unpack('<4i',raw(0x8009c7a0+j*16,16)))
