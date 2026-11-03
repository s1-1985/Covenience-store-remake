"""Independent4152C wait and41374 polling policy; frame raw state supplied."""
from recovered import i32
class InputWait:
 def __init__(self,held,edge,delay,mode,raws,seed,counters):
  self.held=held;self.edge=edge;self.delay=delay;self.mode=mode;self.raws=raws;self.seed=seed;self.counters=list(counters);self.ticks=0;self.calls=[];self.buttons=0;self.directions=0
 def wait(self,count):
  self.calls.append(count);found=0
  for _ in range(max(0,i32(count))):
   raw=self.raws[self.ticks];self.ticks+=1;self.edge=((raw^self.held)&raw)&0xffffffff;self.held=raw
   self.seed=(self.seed*1103515245+12345)&0xffffffff
   if self.mode:self.counters=[(self.counters[0]+1)&65535,(self.counters[1]-1)&65535]
   if self.edge:found=1;break
  self.buttons=self.edge;return found
 def poll(self):
  firstheld=self.held;firstedge=self.edge
  for _ in range(100):
   if self.wait(self.delay):self.directions=self.edge;return 0
   if not self.held:continue
   held=self.held
   if held&firstedge:
    if self.wait(4):self.directions=self.edge;return 0
    held=self.held;self.directions=held&firstedge
    if self.directions:return 1
   if held&firstheld:self.directions=held&firstheld;return 1
  raise ValueError('nonterminating fixture')
