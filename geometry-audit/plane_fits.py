import numpy as np,json
p='/workspace/geometry-audit/';g=json.load(open(p+'geometry.json'))
from matplotlib.path import Path
out=[]
for r in g['rooms']:
 floor='upstairs' if r['level']=='upper' else 'basement';d=np.load(p+floor+'_surface.npz');c=d['c'];n=d['n'];a=d['a'];inside=Path(r['outline']).contains_points(c[:,:2]);h=np.abs(n[:,2])>.95
 for typ,z in [('floor',r['floor_z_m']),('ceiling',r['ceiling_z_m'])]:
  q=inside&h&(np.abs(c[:,2]-z)<.16)&(a>.00001)
  cc=c[q];w=a[q];A=np.c_[cc[:,:2],np.ones(len(cc))]
  if len(cc)<10:continue
  for _ in range(4):
   coef=np.linalg.lstsq(A*np.sqrt(w[:,None]),cc[:,2]*np.sqrt(w),rcond=None)[0];e=cc[:,2]-A@coef;m=np.abs(e)<max(.018,np.quantile(np.abs(e),.8));A=A[m];cc=cc[m];w=w[m]
  coef=np.linalg.lstsq(A*np.sqrt(w[:,None]),cc[:,2]*np.sqrt(w),rcond=None)[0];e=cc[:,2]-A@coef
  out.append({'room':r['id'],'surface':typ,'z_equation':'z = a*x + b*y + c','abc':[round(float(v),6) for v in coef],'weighted_rms_m':round(float(np.sqrt(np.average(e*e,weights=w))),4),'support_area_m2':round(float(w.sum()),3),'support_triangles':len(w),'warning':'Local robust fit to measured near-horizontal faces; use as evidence, not unseen room-wide plane validation.'})
json.dump(out,open(p+'surface_plane_fits.json','w'),indent=2)
print(json.dumps(out,indent=2))
