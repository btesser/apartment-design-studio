import json,numpy as np
from shapely.geometry import Polygon,shape,box
from shapely.ops import unary_union,triangulate
geo=json.load(open('/workspace/geometry-audit/geometry.json'))
void=box(*[0,0,1,1])
sv=geo['stair']['upper_floor_void'];void=box(sv[0],sv[2],sv[1],sv[3])
out=[]
def triang(g):
 return [list(t.exterior.coords)[:3] for t in triangulate(g) if g.covers(t.representative_point()) and t.intersection(g).area>t.area-.000001]
def floor_boundary(level):
 g=shape(json.load(open(f'/workspace/apartment-model/{level}_floormesh_boundary.geojson')))
 polys=[q for q in (g.geoms if g.geom_type=='MultiPolygon' else [g]) if q.area>3]
 # Interior floor voids in this scan are occlusions; stair well is explicit carve-out.
 return unary_union([Polygon(q.exterior) for q in polys])
for name,level,z in [('scan-floor-upper','upstairs',1.49),('scan-floor-lower','basement',-1.50)]:
 g=floor_boundary(level)
 if level=='upstairs':g=g.difference(void)
 out.append({'name':name,'type':'floor_underlay','level':level,'z':z,'triangles':triang(g),'area':g.area})
for r in geo['rooms']:
 if r['id']=='bedroom-flex':continue
 g=Polygon(r['outline'])
 if r['level']=='upper':g=g.difference(void)
 out.append({'name':r['id'],'type':'architecture_floor','level':r['level'],'z':r['floor_z_m'],'triangles':triang(g),'area':g.area})
 ceiling=g
 if r['level']=='lower':ceiling=ceiling.difference(void.buffer(.1))
 out.append({'name':r['id'],'type':'ceiling_underlay','level':r['level'],'z':r['ceiling_z_m']+.08,'triangles':triang(ceiling),'area':ceiling.area})
 out.append({'name':r['id'],'type':'architecture_ceiling','level':r['level'],'z':r['ceiling_z_m'],'triangles':triang(ceiling),'area':ceiling.area})
json.dump(out,open('/workspace/apartment-model/plate-geometry.json','w'))
# Keep all inferred/approximate numbers explicitly tagged in reusable viewer metadata.
meta={'coordinate_system':{'native':'Blender Z-up','gltf':'Y-up','transform':'GLTF [x,y,z] = Blender [x,z,-y]','scale':1,'units':'meters','normalization':'none'},'levels':{'lower':{'floor_y':-1.385,'ceiling_y':1.245,'bounds':[-7.9,8.0,-2.9,2.8]},'upper':{'floor_y':1.575,'ceiling_y':4.185,'bounds':[-8.1,8.1,-2.9,3.0]}},'rooms':[],'stair':geo['stair'],'uncertainty':'Wall outlines approximately 0.05–0.12 m; opening positions approximate; no tape-measure validation. Raw metric scan was never stretched.'}
for r in geo['rooms']:
 rr=dict(r);rr['polygon_gltf_xz']=[[x,-y] for x,y in r['outline']];rr['floor_y']=r['floor_z_m'];rr['ceiling_y']=r['ceiling_z_m'];meta['rooms'].append(rr)
json.dump(meta,open('/workspace/apartment-model/model-metadata.json','w'),indent=2)
