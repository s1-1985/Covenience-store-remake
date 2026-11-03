"""Original86244/86348 sector to three BCD bytes and reverse; signed wrap retained."""
from recovered import i32

def trunc(n,d):return (abs(n)//d)*(-1 if n<0 else 1)
def bcd(n):q=trunc(n,10);return ((q<<4)+(n-q*10))&255

def encode(sector):
 n=i32((sector+150)&0xffffffff);seconds=trunc(n,75);minute=trunc(seconds,60)
 return bytes([bcd(minute),bcd(seconds-minute*60),bcd(n-seconds*75)])
def decode(data):
 m,s,f=[(x>>4)*10+(x&15) for x in data[:3]]
 return ((m*60+s)*75+f-150)&0xffffffff
