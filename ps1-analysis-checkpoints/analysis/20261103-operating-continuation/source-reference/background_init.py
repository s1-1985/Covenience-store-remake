"""19460 background header and36byte record initializer, original viewport words."""
import struct
from cursor_control import s16
VIEWPORT=[0, 0, 480, 400, 0, 0, 320, 240, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 1, 2, 2, 2, 2, 2, 3, 3, 3, 4, 5, 6, 7, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 20, 21, 22, 23, 23, 23, 23, 23, 24, 24, 24, 24, 24, 24, 24, 25, 26, 27, 28, 29, 30, 30, 30, 31, 32, 32, 33, 34, 35, 35, 35, 36, 37, 38, 39, 40, 41, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, -32737, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, -1024, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, -128, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, -31760, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, -6409, 0, 0, -1024, -13698, -13506, -13474, -11521, -9505, -13442, -13473, -11489, -11489, -9505, -13410, -9473, -11457, -11457, -9473, -13410, -13409, -11425, -9441, -11425, -9441, -13409, -11393, -9409, -9409, -11393, -9377, -11361, -11361, -9377, -9345, -11329, -11329, -9345, -11297, -9313, -11297, -9313, -9281, -9281, -9249, -9249, -9217, -9217, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
def initialize_background(source,images,type_arg,header,record,source_address):
 h=bytearray(header);b=bytearray(record)
 struct.pack_into('<HH',h,2,source[0],source[1]);h[0]=source[2];h[1]=source[3]
 struct.pack_into('<II',h,8,images&0xffffffff,(source_address+4)&0xffffffff)
 k=((type_arg&255)*4)&255
 x,y,w,height=VIEWPORT[k:k+4]
 struct.pack_into('<I',b,0,0x01000000)
 struct.pack_into('<4H',b,4,x&65535,y&65535,w&65535,height&65535)
 struct.pack_into('<HH',b,12,0,0);b[16:19]=bytes([128]*3)
 struct.pack_into('<I',b,20,0x800e3da8)
 def half(v):return (abs(v)//2)*(-1 if v<0 else 1)
 struct.pack_into('<HHHHI',b,24,half(w)&65535,half(height)&65535,4096,4096,0)
 return bytes(h),bytes(b)
