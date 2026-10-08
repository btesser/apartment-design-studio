import json,pathlib,numpy as np,contextlib,io,runpy
from shapely.geometry import Polygon,MultiPoint
with contextlib.redirect_stdout(io.StringIO()):api=runpy.run_path('/workspace/independent-qa/audit_artifacts.py')
root=pathlib.Path('/workspace');j,b=api['read_glb'](root/'apartment-furniture/furniture.glb');hearth=json.load(open(root/'apartment-model/hearth-geometry.json'));poly=Polygon(hearth['source']['coordinates_blender_xy']);meshes={}
def visit(index,parent):
 n=j['nodes'][index];m=parent@api['matrix'](n);name=n.get('name','');pts=[]
 if 'mesh'in n and name.startswith('her-loveseat::'):
  for p in j['meshes'][n['mesh']]['primitives']:
   v=api['accessor'](j,b,p['attributes']['POSITION']);v=v@m[:3,:3].T+m[:3,3];pts.append(v[:,[0,2,1]]*np.array([1,-1,1]))
  meshes[name]=np.concatenate(pts)
 for child in n.get('children',[]):visit(child,m)
for node in j['scenes'][j.get('scene',0)]['nodes']:visit(node,np.eye(4))
supports=[];body=[]
for name,v in meshes.items():
 if name.startswith('her-loveseat::foot'):
  shape=MultiPoint(v[:,:2]).convex_hull;supports.append({'mesh':name,'source':'actual exported GLB support vertices','clearance_m':shape.distance(poly),'intersection_m2':shape.intersection(poly).area,'lowest_z_m':float(v[:,2].min()),'highest_z_m':float(v[:,2].max())})
 else:body.append(float(v[:,2].min()))
report={'support_meshes':supports,'all_supports_clear':all(s['intersection_m2']<1e-8 for s in supports),'min_support_clearance_m':min(s['clearance_m'] for s in supports),'body_lowest_z_m':min(body),'maximum_observed_hearth_z_m':max(hearth['source']['z_top_range']),'body_vertical_clearance_above_hearth_m':min(body)-max(hearth['source']['z_top_range']),'hearth_hull_observed_area_m2':hearth['source']['observed_area_m2'],'hearth_hull_filled_area_m2':hearth['source']['conservative_hull_area_m2']}
json.dump(report,open(root/'independent-qa/hearth-actual-geometry.json','w'),indent=2);print(json.dumps(report,indent=2))
