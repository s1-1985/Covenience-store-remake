"""Recovered title128B4 control; external UI/resource children supplied."""
import struct

def title_load(read,write,call,rectangles):
 call(0x8005c79c);call(0x80065974);call(0x80018a5c);call(0x80018a5c)
 call(0x80018940,210,0);call(0x8004ea68);call(0x80013448)
 if call(0x80051174,0)!=0:
  call(0x80065974);call(0x80018a5c);call(0x80018a5c)
  write(0x800cd6c4,b'\x02');call(0x8004ea68);return 'load_nonzero'
 call(0x8004ea68);call(0x8006bc40);call(0x80065974);call(0x8005c61c)
 if read(0x800cd8a8,1)==b'\xff':
  call(0x80065974);call(0x80018a5c);call(0x80018a5c)
  write(0x800cd6c4,b'\x02');return 'saved_minus_one'
 for resource in (14,15,1,2):
  call(0x800140e8,resource,0)
  words=rectangles(resource)
  call(0x80013eac,0x80187e00,*words)
 call(0x80065b3c,10,11,29,25);call(0x8006653c)
 write(0x8013796c,bytes(4));write(0x801398bc,b'\x01')
 call(0x80023c20);call(0x8002619c);call(0x80041a08)
 write(0x800cd6c4,b'\x07');return 'resume'
