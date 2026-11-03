"""67494/675DC atlas indices and tint; no asset semantic names inferred."""
from settings_visuals import s16
def icon32(x,y,code,color):
 return (x-160,y-112,32,32,13,(code&7)*32,128,0,490,(color,)*3,1)
def portrait48(x,y,code,color):
 z=s16(code);q=abs(z)//5*(-1 if z<0 else 1);rem=z-q*5
 if z==-1:kind,u,v,ref=7,48,136,492
 else:kind=23 if q>=6 else 21;u=rem*48;v=(q-6 if q>=6 else q)*40;ref=494
 return (x-160,y-112,48,40,kind,u,v,0,ref,(color,)*3,1)
