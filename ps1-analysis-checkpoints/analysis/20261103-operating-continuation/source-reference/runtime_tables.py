"""8005C858: destructive startup conversion of disk tables into image indices."""
from recovered import i32
from event_queue import reset

def bootstrap(queue,state,appearance,images):
 reset(queue,state)
 appearance=[[i32(v+60) for v in row] for row in appearance]
 images=[[v if v==-1 else i32(v*3+360) for v in row] for row in images]
 return appearance,images

def runtime_product_images(images):return [[v if v==-1 else i32(v*3+360) for v in row] for row in images]
