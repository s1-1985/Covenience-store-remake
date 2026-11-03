from checkout import service_gate

def fixture_at(width,height,cells,dimensions,x,y):
 result=(-1,-1)
 for cy in range(height):
  for cx in range(width):
   word=cells.get((cx,cy),0);kind=(word>>12)&1023
   if not word&0x80000000 or kind>=53:continue
   w,h=dimensions[kind]
   if ((word>>22)&3)>=2:w,h=h,w
   if cx<=x<cx+2*w and cy<=y<cy+2*h:result=(cx,cy)
 return result

def cashier_service(width,height,cells,dimensions,directions,customer,staff,busy,threshold,manager,seed):
 staff=[dict(s) if s else None for s in staff];busy=list(busy)
 def front(x,y,d):
  dx,dy=directions[d]
  return fixture_at(width,height,cells,dimensions,x+dx,y+dy)
 target=front(*customer)
 if target==(-1,-1):return 1,staff,busy,seed
 for j,s in enumerate(staff):
  if s is None or s[0x28]!=1:continue
  at=front(s[0x29],s[0x2a],s[0x2b])
  if at==(-1,-1) or at!=target or busy[j]!=0:continue
  busy[j]=1
  ret,staff[j],seed=service_gate(s,threshold,manager,seed)
  return ret,staff,busy,seed
 return 1,staff,busy,seed
