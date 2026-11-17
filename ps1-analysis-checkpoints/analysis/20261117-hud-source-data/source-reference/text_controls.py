"""16580 selected command expansion, preserving raw padding/stack behavior."""
import struct
from cursor_control import s16
from recovered import i32

def trunc(v,d):return abs(v)//d*(-1 if v<0 else 1)
def digits_signed(v):
 if not v:return [0]
 out=[]
 while v:
  q=trunc(v,10);out.append((v-q*10)&65535);v=q
 return out
class ExpandBuffer:
 def __init__(self,data,pos,basehalf=32):self.data=bytearray(data);self.pos=pos;self.basehalf=basehalf
 def write(self,p,v):struct.pack_into('<H',self.data,2*(self.basehalf+p),v&65535)
 def emit(self,v):self.write(self.pos,v);self.pos=i32(self.pos+1)
 def append(self,words):
  for c in words:
   if c==0x40ff:break
   self.emit(c)
 def backward(self,digits):
  p=self.pos-1
  for j,c in enumerate(digits):
   self.write(p,c);p-=1
   if (j+1)%3==0 and j+1<len(digits):self.write(p,0x2c);p-=1
 def number_padded(self,value,width):
  v=i32(value)
  if v<0:self.emit(0x2e);v=i32(-v)
  for j in range(max(0,s16(width))):self.emit(0x3e)
  self.backward(digits_signed(v))
 def number_variable(self,value):
  v=i32(value)
  if v==-2147483648:v=0
  if v<0:self.emit(0x2e);v=-v
  self.emit(0x24);digits=digits_signed(v);self.pos+=len(digits)+(len(digits)-1)//3;self.backward(digits)
 def two_digits(self,value):
  v=i32(value);self.emit(0);self.emit(0);p=self.pos-1
  for j in range(2):
   q=trunc(v,10);self.write(p,v-q*10);v=q
   if not v:break
   p-=1
 def rating(self,value):
  for j in range(5):self.emit(0x28b if j<s16(value) else 0x28c)

def expand_stream(stream,buffer,values,strings,rating,number):
 """Selected16580 dispatch; caller supplies raw tables and string slots."""
 p=0
 while p<len(stream):
  code=stream[p];p+=1
  if not code&0x4000:buffer.emit(code);continue
  if code in [0x4003,0x4004,0x4005,0x4007,0x4009]:arg=s16(stream[p]);p+=1
  if code==0x4002:buffer.emit(code)
  elif code==0x40ff:buffer.emit(code);break
  elif code==0x4003:buffer.number_padded(number,arg)
  elif code==0x4004:buffer.number_variable(values['variable'][arg])
  elif code==0x4009:buffer.two_digits(values['two'][arg])
  elif code==0x400c:buffer.rating(rating)
  elif code in [0x4005,0x4006,0x4007,0x400a]:buffer.append(strings[(code,arg if code in [0x4005,0x4007] else 0)])
 return p
