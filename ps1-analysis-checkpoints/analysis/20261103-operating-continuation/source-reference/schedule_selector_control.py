"""Independent complete45FFC navigation, seven schedules, bottom OK/cancel."""
import struct
def run(m,child):
 child(0x80018940,4,1);child(0x80017b18,32|(48<<16),16|(6<<16),0);child(0x800157b4)
 for index,x,y in ((41,64,64),(49,48,80),(51,88,96),(9,112,112),(270,112,80),(269,248,80)):child(0x800155d0,index|(x<<16),y)
 m.write(0x800cd798,m.read(0x800cda3c,2));child(0x800469a8,44);child(0x80018940,2,1);child(0x8004e938,248,91);child(0x80018940,16,1)
 m.write(0x800cda14,struct.pack('<H',child(0x800182d0,106|(112<<16),36|(16<<16),0,0)))
 row=col=0;choice=2;states=[]
 def cursor(x=None,dy=0,dx=0):
  cx,cy=struct.unpack('<2H',m.read(0x800dae3c,4));m.write(0x800dae3c,struct.pack('<2H',((cx+dx) if x is None else x)&65535,(cy+dy)&65535))
 for _ in range(100):
  child(0x80041374,0);dirs=m.word(0x800cda0c);buttons=m.word(0x800cda28)
  if dirs&0x1000 and row==1:row=0;cursor(88,-32)
  if dirs&0x4000 and row==0:row=1;cursor(-21 if col==0 else 33,32)
  if dirs&0x2000:
   if row==0:choice=(choice+1)%7;child(0x800469a8,choice+42)
   elif col==0:child(0x800182d0,160|(112<<16),36|(16<<16),0,0);cursor(dx=54);col=1
  if dirs&0x8000:
   if row==0:choice=(choice-1)%7;child(0x800469a8,choice+42)
   elif col==1:child(0x800182d0,106|(112<<16),36|(16<<16),0,0);cursor(dx=-54);col=0
  states.append([row,col,choice,dirs,buttons])
  if row==1 and buttons&32:child(0x80065000);child(0x8004ea68);return 0 if col else choice+1,states
 raise AssertionError('schedule selector nontermination')
