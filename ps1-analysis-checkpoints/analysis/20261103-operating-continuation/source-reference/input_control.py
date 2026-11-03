"""1310C interrupt bookkeeping,13DDC edges,659BC init,65A1C repeats."""
from recovered import i32
GP=0x800cd6c4

def interrupt(s,raw):
 s[0x800cd9d8]=raw&0xffffffff
 if s[0x800cd7e0]==0:s[0x800cd7e0]=raw&0xffffffff
 s[GP+4]=(s[GP+4]+1)&0xffffffff
 if i32(s[GP+8])>0:s[GP+8]=(s[GP+8]-1)&0xffffffff
 if i32(s[0x801398b8])>0:s[0x801398b8]=(s[0x801398b8]-1)&0xffffffff

def edges(s):
 new=s[0x800cd9d8];old=s[0x800cd9cc]
 s[0x800cd9c0]=((new^old)&new)&0xffffffff;s[0x800cd9cc]=new

def initialize(s,delay):
 s[0x800cd850]=s[0x800cd9cc];s[0x800cd824]=s[0x800cd9cc];s[0x800cd884]=0
 s[0x800cd85c]=delay&0xffffffff;s[0x800cd9f0]=delay&0xffffffff

def repeat(s):
 now=s[0x800cd9cc];prior=s[0x800cd824];delay=s[0x800cd85c]
 if now==prior and now!=0:
  if i32(s[GP+8])>0:s[0x800cd884]=0;s[0x800cd850]=0
  else:
   s[0x800cd850]=now;s[0x800cd884]=s[0x800cd9c0];s[GP+8]=delay
 else:
  s[GP+8]=(delay+(4 if now==0 else 0))&0xffffffff
  s[0x800cd850]=now;s[0x800cd824]=now;s[0x800cd884]=s[0x800cd9c0]

def modal_mask(s):
 if s[0x801398b4]!=0:
  s[0x800cd884]&=0xf00c;s[0x800cd850]&=0xf00c
