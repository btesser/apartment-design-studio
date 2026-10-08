import numpy as np,json
from scipy.signal import find_peaks
zones={'upstairs':{'his-office':[-8,-3.1,-2.8,.3],'living':[-3,3.6,-2.8,.3],'her-office':[4.3,7.9,-2.75,.85],'kitchen':[-7.9,-2.2,1.3,2.1],'bathroom':[-1.3,1.2,.45,2.75],'entry':[1.3,3.65,.4,1.8]},'basement':{'music-gym':[-7.4,-3.8,-2.5,.4],'bedroom-flex':[-3.7,-.7,-2.4,.6],'basement-lounge':[-.7,4,-2.4,1.85],'lower-kitchen':[5.8,7.7,-2.0,2.0],'stair':[2.3,5.0,1.8,2.8]}}
out={}
for floor,zz in zones.items():
 d=np.load('/workspace/geometry-audit/'+floor+'_surface.npz');c=d['c'];n=d['n'];a=d['a']
 for room,b in zz.items():
  q=(c[:,0]>b[0])&(c[:,0]<b[1])&(c[:,1]>b[2])&(c[:,1]<b[3])&(np.abs(n[:,2])>.95)
  hist,edges=np.histogram(c[q,2],bins=np.arange(-2,5,.01),weights=a[q]);ii=find_peaks(hist,distance=12,prominence=.1)[0];peaks=sorted([(round(float(edges[i]+.005),3),round(float(hist[i]),3)) for i in ii],key=lambda x:-x[1])[:10]
  out[room]={'sampling_bounds':b,'horizontal_area_peaks':peaks};print(room,peaks)
json.dump(out,open('/workspace/geometry-audit/zone_horizontal_peaks.json','w'),indent=2)
