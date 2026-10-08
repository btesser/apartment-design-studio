from pathlib import Path
import numpy as np, json
import matplotlib;matplotlib.use('Agg')
import matplotlib.pyplot as plt
from scipy.signal import find_peaks
for floor,ids in [('basement',range(11)),('upstairs',range(11,22))]:
 vv=[];cc=[];nn=[];aa=[];tt=[]
 for i in ids:
  d=np.load(f'/workspace/geometry-audit/Mesh_{i}.npz');v=d['v'];f=d['f'];t=v[f];n=np.cross(t[:,1]-t[:,0],t[:,2]-t[:,0]);a=np.linalg.norm(n,axis=1)/2;n=n/np.maximum(a[:,None]*2,1e-12)
  vv.append(v);cc.append(t.mean(1));nn.append(n);aa.append(a);tt.append(t)
 v=np.concatenate(vv);c=np.concatenate(cc);n=np.concatenate(nn);a=np.concatenate(aa);t=np.concatenate(tt)
 np.savez_compressed(f'/workspace/geometry-audit/{floor}_surface.npz',v=v,c=c,n=n,a=a,t=t)
 h=np.abs(n[:,2])>.95
 bins=np.arange(-2,5,.01);hist,edges=np.histogram(c[h,2],bins=bins,weights=a[h]);ii=find_peaks(hist,distance=12,prominence=.5)[0];peaks=sorted([(round(float(edges[i]+.005),3),round(float(hist[i]),3)) for i in ii],key=lambda x:-x[1]);print(floor,'HORIZONTAL PEAKS',peaks[:20])
 fig,axs=plt.subplots(3,1,figsize=(16,12));axs[0].bar(edges[:-1],hist,width=.01);axs[0].set_title(floor+' horizontal surface area by Z elevation');axs[0].set_xlim(-2,5)
 for ax,zband in zip(axs[1:], [(-1.6,0.9) if floor=='basement' else (1.5,4.5),(-1.7,-1.2) if floor=='basement' else (1.4,1.8)]):
  q=(c[:,2]>zband[0])&(c[:,2]<zband[1]);ax.scatter(c[q,0],c[q,1],c=c[q,2],s=np.maximum(a[q]*500,0.15),cmap='viridis');ax.set_aspect('equal');ax.set_xlim(-9,9);ax.set_ylim(-3.5,3.5);ax.grid();ax.set_title('surface centers, Z '+str(zband))
 plt.tight_layout();fig.savefig(f'/workspace/geometry-audit/{floor}_surface_analysis.png',dpi=160)
 # Area histogram of wall normals projected to XY folded modulo 90 degrees
 q=np.abs(n[:,2])<.2;angles=np.arctan2(n[q,1],n[q,0]);angles=(angles+np.pi/4)%(np.pi/2)-np.pi/4
 hist2,ee=np.histogram(np.rad2deg(angles),bins=np.arange(-45,45,.2),weights=a[q]);best=np.argmax(hist2);print(floor,'wall angle dominant',round((ee[best]+ee[best+1])/2,2),'degree')
