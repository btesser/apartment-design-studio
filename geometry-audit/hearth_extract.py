import numpy as np,json
from shapely.geometry import Polygon,MultiPoint,mapping
from shapely.ops import unary_union
s=np.load('/workspace/geometry-audit/upstairs_surface.npz');c=s['c'];n=s['n'];a=s['a'];t=s['t']
zfloor=.010231*c[:,0]-.012961*c[:,1]+1.506812
q=(c[:,0]>4.9)&(c[:,0]<6.40)&(c[:,1]<-2.30)&(c[:,1]>-3.1)&(c[:,2]>1.61)&(c[:,2]<1.675)&(np.abs(n[:,2])>.85)&((c[:,2]-zfloor)>.025)
tri=t[q];polys=[Polygon(v[:,:2]) for v in tri];union=unary_union(polys);hull=union.convex_hull.simplify(.02,preserve_topology=True)
out={'id':'her-measured-hearth-top','coordinates_blender_xy':[[round(float(x),4),round(float(y),4)] for x,y in list(hull.exterior.coords)[:-1]],'z_top_median':round(float(np.median(c[q,2])),4),'z_top_range':[float(c[q,2].min()),float(c[q,2].max())],'observed_area_m2':float(union.area),'conservative_hull_area_m2':float(hull.area),'source_selection':'Raw scan near-horizontal faces X4.9..6.4,Y-3.1..-2.3,Z1.61..1.675 with height>local fitted floor+.025m. Convex hull of actual raised patch support; simplify2cm. This includes only measured raised floor-level patch, not extrapolated entire hearth rectangle.','confidence':'Raw scan uncertain/missing left support; use shallow separate inferred infill over measured footprint, not enlarge to full chimney width.'}
json.dump(out,open('/workspace/geometry-audit/her-hearth-polygon.json','w'),indent=2)
print(json.dumps(out,indent=2))
