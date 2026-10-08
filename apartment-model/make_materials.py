from PIL import Image,ImageDraw
import numpy as np
from pathlib import Path
p=Path('/workspace/apartment-model');rng=np.random.default_rng(8121)
# Deterministic reconstructed material tiles; never treated as observed texture.
for name,base in [('wood-upper',(174,139,94)),('tile-lower',(80,82,80))]:
 a=np.zeros((512,1024,3),dtype=np.uint8)
 for row in range(8):
  value=rng.uniform(-12,12);noise=rng.normal(0,2,(64,1024,1));color=np.array(base)[None,None,:]+value+noise
  a[row*64:(row+1)*64]=np.clip(color,0,255)
 im=Image.fromarray(a);d=ImageDraw.Draw(im)
 for row in range(8):
  d.line((0,row*64,1024,row*64),fill=tuple(max(0,b-25) for b in base),width=2)
  for xx in range(-512,1024,512):
   x=xx+(row%2)*256;d.line((x,row*64,x,(row+1)*64),fill=tuple(max(0,b-30) for b in base),width=2)
 im.save(p/f'{name}.png')
a=np.zeros((512,1024,3),np.uint8);a[:]=[165,132,106];im=Image.fromarray(a);d=ImageDraw.Draw(im)
for row in range(8):
 for col in range(-1,8):
  x=col*146+(row%2)*73;y=row*64;color=tuple(int(v+rng.uniform(-20,20)) for v in [124,57,33]);d.rectangle((x+4,y+4,x+142,y+59),fill=color)
im.save(p/'brick-upper.png')
