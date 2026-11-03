from unicorn import Uc,UC_ARCH_MIPS,UC_MODE_MIPS32,UC_MODE_LITTLE_ENDIAN
from unicorn.mips_const import *
from pathlib import Path
import struct
SOURCE=Path(__file__).resolve().parent/'source'
EXE=SOURCE/'SLPS_007.82'
def machine():
 u=Uc(UC_ARCH_MIPS,UC_MODE_MIPS32|UC_MODE_LITTLE_ENDIAN);u.mem_map(0,0x200000);u.mem_write(0x10000,EXE.read_bytes()[0x800:]);u.reg_write(UC_MIPS_REG_SP,0x801f0000);u.reg_write(UC_MIPS_REG_FP,0x801f0000);return u
def put(u,a,x):u.mem_write(a&0x1fffffff,struct.pack('<I',x&0xffffffff))
def get(u,a):return struct.unpack('<I',u.mem_read(a&0x1fffffff,4))[0]
