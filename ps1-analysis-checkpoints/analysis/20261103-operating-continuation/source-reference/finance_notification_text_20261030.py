"""29334 notification text in original call order, independent of native builder."""
from text_buffer import TextBuffer
from recovered import truncdiv

class FinanceNotificationText:
    def __init__(self,data,pos,read,rival_type):
        self.builder=TextBuffer(data,pos,read);self.rival_type=rival_type;self.calls=[]
    def __call__(self,spec):
        t=self.builder
        if spec[0]=='manager':
            _,slot,sales=spec
            t.store_name(0x8012b2f8+slot*5080,14,self.rival_type)
            self.calls.append(['store_name',slot,14])
            t.append(0x80098e9c,0);self.calls.append(['append',0x80098e9c,0])
            large=sales>99999999;value=truncdiv(sales,100000000 if large else 1000000)
            t.number(value,0);self.calls.append(['number',value,0])
            address=0x80098eb0 if large else 0x80098ec4
            t.append(address,0);self.calls.append(['append',address,0])
        else:
            assert spec[0] in ('monthly','annual')
            address=0x80099208 if spec[0]=='monthly' else 0x80099228
            t.append(address,4);self.calls.append(['append',address,4])
        return bytes(t.data)
