import numpy as np
import matplotlib;matplotlib.use('Agg')
import matplotlib.pyplot as plt
for floor in ['upstairs','basement']:
 d=np.load('/workspace/geometry-audit/'+floor+'_surface.npz');c=d['c'];n=d['n'];a=d['a']
 fig,axs=plt.subplots(3,1,figsize=(20,12))
 bands=[(2,2.7),(3,3.7),(4,4.5)] if floor=='upstairs' else [(-1,-.4),(-.3,.3),(.5,1.0)]
 for ax,b in zip(axs,bands):
  q=(c[:,2]>b[0])&(c[:,2]<b[1])&(np.abs(n[:,2])<.5)&(a>.0001)
  ax.scatter(c[q,0],c[q,1],c=np.arctan2(n[q,1],n[q,0]),cmap='twilight',s=np.maximum(a[q]*500,.2));ax.set_aspect('equal');ax.set_xlim(-8.8,8.8);ax.set_ylim(-3.3,3.3);ax.set_xticks(np.arange(-8,9,.5));ax.set_yticks(np.arange(-3,4,.5));ax.grid();ax.set_title(floor+' vertical normals band '+str(b))
 plt.tight_layout();fig.savefig('/workspace/geometry-audit/'+floor+'_wallmap.png',dpi=200)
