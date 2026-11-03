"""16-bit message builder recovered from 8006CDE0/CE14/D204/D3F8/D644/D758."""
import struct
from recovered import i32
class TextBuffer:
    def __init__(self,data,pos,read):self.data=bytearray(data);self.pos=pos;self.read=read
    def word(self,value):struct.pack_into('<H',self.data,self.pos*2,value&65535)
    def emit(self,value):self.word(value);self.pos+=1
    def reset(self):self.pos=0;self.word(0x40ff)
    def prefix(self,flags):
        if flags&4:self.reset()
        if flags&1:self.emit(0x24)
    def finish(self,flags):
        if flags&2:self.emit(0x4002)
        self.word(0x40ff)
    def append(self,address,flags):
        self.prefix(flags)
        while True:
            value=struct.unpack('<H',self.read(address,2))[0];address+=2
            self.word(value)
            if value==0x40ff:break
            self.pos+=1
        self.finish(flags)
    def lookup(self,index,flags):
        address=0x80183e00+struct.unpack('<I',self.read(0x80183e00+index*4,4))[0]
        self.append(address,flags)
    def number(self,value,flags):
        if flags&4:self.reset()
        value=i32(value)
        if value==-2147483648:value=0
        if value<0:self.emit(0x2e);value=-value
        elif flags&16 and value:self.emit(0x3c)
        if flags&1:self.emit(0x24)
        digits=str(value)
        for j,c in enumerate(digits):
            self.emit(int(c))
            remain=len(digits)-j-1
            if remain and remain%3==0:self.emit(0x2c)
        self.finish(flags)
    def store_name(self,address,flags,rival_type):
        storeflags=struct.unpack('<H',self.read(address+4,2))[0]
        if storeflags&0x8000:self.lookup(rival_type+362,flags&4)
        else:self.append(0x8012b2c8,flags&4)
        if flags&8:
            number=storeflags&255
            if number==1:self.lookup(12,flags&2)
            else:
                self.number(number,0);self.append(0x800cd748,flags&2)
    def rating(self,value):
        """Original6D644 appends exactly five filled/empty rating glyph IDs."""
        value=i32(value)
        for j in range(5):self.emit(0x28b if j<value else 0x28c)
        self.word(0x40ff)
    def milestones(self,calls,text,stores_base=0x8012b2f8,rival_type=0):
        self.data=bytearray(text)
        for call in calls:
            if call[0]=='reset':self.reset()
            elif call[0]=='store':self.store_name(stores_base+call[1]*5080,call[2],rival_type)
            else:self.append(call[1],call[2])
        return bytes(self.data)
