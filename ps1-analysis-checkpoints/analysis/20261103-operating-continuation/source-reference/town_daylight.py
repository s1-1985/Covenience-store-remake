"""Original66234 RGB bytes from unsigned minute clock; native19FCC/1A03C."""
def rgb(clock,prior):
 t=clock&0xffffffff;hour=(t//60)%24;minute=t%60
 if hour in (4,5):values=[68+30*(hour-4)+minute//2]*3
 elif hour==17:values=[minute-128,-128-minute//2,-128-minute//2]
 elif hour==18:values=[-68-2*minute,98-minute//2,98-minute//2]
 elif 6<=hour<=16:values=[128]*3
 else:values=[68]*3
 return bytes(v&255 for v in values)
