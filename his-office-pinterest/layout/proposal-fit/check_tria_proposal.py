"""Read-only candidate fit. Never opens/saves Blender or writes canonical/model files."""
import json,hashlib,copy,importlib.util,math
from pathlib import Path
import numpy as np
import trimesh
from shapely.geometry import Polygon,LineString,box
ROOT=Path('/workspace/his-office-pinterest');D=ROOT/'layout/proposal-fit';P=ROOT/'products/standing-desk-candidates';lp=ROOT/'model/layout.json';old=json.loads(lp.read_text());specs={i['id']:i for i in old['items']};floor=old['room_floor_z_m'];native=json.loads((ROOT/'layout/chair-transfer-native-check.json').read_text());rp=Path('/workspace/his-office-redesign/geometry/room-measurements.json');room=Polygon(json.loads(rp.read_text())['outline_blender_xy_m']);features=json.loads(Path('/workspace/his-office-redesign/geometry/fixed-features.json').read_text())['features']
spec=importlib.util.spec_from_file_location('routing','/workspace/his-office-redesign/qa/check_routing.py');routing=importlib.util.module_from_spec(spec);spec.loader.exec_module(routing)
source=P/'branch-tria-official-48x27-woodgrain-white.glb';candidate=trimesh.load(source,force='scene',process=False);gltf=json.loads((P/'branch-tria-gltf.json').read_text());extras={n.get('name'):n.get('extras',{}) for n in gltf['nodes']};desktop_bounds=candidate.geometry[candidate.graph['desktop'][1]].bounds;top_center_z=(desktop_bounds[0,2]+desktop_bounds[1,2])/2;source_top_h=float(desktop_bounds[1,1]);source_floor=float(candidate.bounds[0,1]);published_min=.6477;published_max=1.24206
# glTF→Blender Z-up: [x,y,z]→[x,−z,y], centered on actual desktop footprint.
M=np.array([[1,0,0],[0,0,-1],[0,1,0]],float)
def source_extras(name):
 if name in extras:return extras[name]
 keys=[k for k in extras if k and name.startswith(k+'_')]
 return extras[max(keys,key=len)] if keys else {}
product_parts=[]
for name in candidate.graph.nodes_geometry:
 tf,gn=candidate.graph[name];vs=trimesh.transform_points(candidate.geometry[gn].vertices,tf);vs[:,2]-=top_center_z;v=vs@M.T
 product_parts.append({'name':name,'lift':source_extras(name).get('lift','unknown'),'role':source_extras(name).get('role','unknown'),'lo':v.min(0),'hi':v.max(0)})
assert all(p['lift'] in ['desktop','middle','fixed'] for p in product_parts),'Every split source primitive must inherit correct source lift group'
# Read the frozen room export and retain all fixed sources except superseded UPLIFT and moving equipment.
scene_path=ROOT/'model/his-office-pinterest-design.glb';scene=trimesh.load(scene_path,force='scene',process=False);parents=scene.graph.transforms.parents
aliases={'kept-uplift-desk':'uplift-main-desk','kept-honeywell-02e-pro':'honeywell-lamp','kept-muttros-cat-tree':'muttros-cat-tree','branch-pro-task-chair-1':'branch-primary'};aliases.update({i:i for i in specs})
def group(n):
 seen=set()
 while n and n not in seen:
  seen.add(n)
  if 'generic equipment assumption' in n:return n.split('::')[0]+'::equipment'
  if n in aliases:return aliases[n]
  n=parents.get(n)
 return None
fixed=[];equipment=[]
for name in scene.graph.nodes_geometry:
 g=group(name)
 if g=='uplift-main-desk':continue
 if g=='rug' or 'sky' in name.lower() or 'backdrop' in name.lower():continue
 tf,gn=scene.graph[name];vs=trimesh.transform_points(scene.geometry[gn].vertices,tf)@M.T;b={'name':name,'group':g,'lo':vs.min(0),'hi':vs.max(0)}
 if g=='uplift-main-desk::equipment':equipment.append(b)
 else:fixed.append(b)
def bbox_overlap(a,b):return np.minimum(a['hi'],b['hi'])-np.maximum(a['lo'],b['lo'])
def gap_xy(a,b):
 dx=max(b['lo'][0]-a['hi'][0],a['lo'][0]-b['hi'][0],0);dy=max(b['lo'][1]-a['hi'][1],a['lo'][1]-b['hi'][1],0);return math.hypot(dx,dy)
def placed(p,cx,cy,height,mode='pose'):
 factor=1 if p['lift']=='desktop' else .5 if p['lift']=='middle' else 0
 delta=(height-source_top_h)*factor;offset=np.array([cx,cy,floor+delta-source_floor]);return {'name':p['name'],'lift':p['lift'],'role':p['role'],'lo':p['lo']+offset,'hi':p['hi']+offset}
scenarios=[]
for dx in [0,.02,.035,.04]:
 cx=-6.95+dx;cy=-.131;parts_seated=[placed(p,cx,cy,.74) for p in product_parts];parts_swept=[]
 for p in product_parts:
  a=placed(p,cx,cy,published_min);b=placed(p,cx,cy,published_max);parts_swept.append({'name':p['name'],'lift':p['lift'],'role':p['role'],'lo':np.minimum(a['lo'],b['lo']),'hi':np.maximum(a['hi'],b['hi'])})
 # Existing illustrative monitor/keyboard move with new tabletop across height range.
 for p in equipment:
  lo=p['lo']+np.array([dx,0,published_min-.74]);hi=p['hi']+np.array([dx,0,published_max-.74]);parts_swept.append({'name':p['name'],'lift':'desktop-equipment-proxy','role':'equipment','lo':lo,'hi':hi})
 candidates=[]
 for p in parts_swept:
  for f in fixed:
   depth=bbox_overlap(p,f)
   if np.all(depth>.001):candidates.append({'candidate_part':p['name'],'fixed_part':f['name'],'fixed_group':f['group'],'bbox_overlap_depth_m':depth.tolist()})
 feet=[p for p in parts_seated if p['name'] in ['foot_left','foot_right']];lamp_parts=[p for p in fixed if p['group']=='honeywell-lamp' and p['lo'][2]<floor+.1];lamp_gap=min(gap_xy(p,f) for p in feet for f in lamp_parts)
 top=next(p for p in parts_seated if p['name']=='desktop');bench=specs['secondary-workspace'];bench_left=bench['position_blender_m'][0]-bench['external_dimensions_m'][0]/2;bench_gap=bench_left-top['hi'][0]
 lowcat=[p for p in fixed if p['group']=='muttros-cat-tree' and 'Low side wicker basket' in p['name']];minimum_top=placed(next(p for p in product_parts if p['name']=='desktop'),cx,cy,published_min);cat_gap=min(minimum_top['lo'][2]-p['hi'][2] for p in lowcat)
 # Primary chair transfer with unchanged waypoints, replacing old UPLIFT low parts only.
 path=LineString(native['waypoints_blender_xy_m']);radius=native['chair_caster_diameter_m']/2;floor_shapes=[]
 for p in native['floor_obstacles']:
  if p['group']=='uplift-main-desk':continue
  lo,hi=p['world_bounds_m'];floor_shapes.append((p['name'],box(lo[0],lo[1],hi[0],hi[1])))
 for p in product_parts:
  pp=placed(p,cx,cy,published_min)
  if pp['lo'][2]<=floor+.20 and pp['hi'][2]>=floor:
   floor_shapes.append(('Tria::'+p['name'],box(pp['lo'][0],pp['lo'][1],pp['hi'][0],pp['hi'][1])))
 gaps=[{'obstacle':n,'continuous_caster_clearance_m':path.distance(s)-radius} for n,s in floor_shapes]
 # Conservative human routing with desk externalCAD envelope replacingold desktop only.
 routes=[]
 for label,pull in [('working',0),('primary45cm_pullback',.45)]:
  test=copy.deepcopy(old)
  for i in test['items']:
   if i['id']=='uplift-main-desk':i['position_blender_m']=[cx,cy,floor];i['external_dimensions_m']=[1.2,.685,.74]
   if i['kind']=='task_chair':i['position_blender_m'][1]-=pull
  obs=routing.nominal_obstacles(test,features);routes.append({'state':label,'checks':[routing.check(room,obs,r) for r in [.25,.275,.30]]})
 scenarios.append({'center_blender_m':[cx,cy,floor],'desk_only_x_shift_m':dx,'CAD_top_bounds_blender_m':[top['lo'].tolist(),top['hi'].tolist()],'nominal_lamp_Ubase_to_desk_feet_gap_m':lamp_gap,'top_to_project_bench_x_gap_m':float(bench_gap),'top_rear_to_nominal_white_wall_y_gap_m':float(.31-top['hi'][1]),'cat_low_basket_to_tabletop_underside_at_lowest_published_height_m':cat_gap,'full_height_swept_bbox_candidates_against_frozen_other_parts':candidates,'swept_bbox_disjoint_from_all_frozen_other_parts':not candidates,'chair_transfer_floor_clear':all(g['continuous_caster_clearance_m']>=0 for g in gaps),'chair_transfer_min_floor_component_clearance_m':min(g['continuous_caster_clearance_m'] for g in gaps),'chair_transfer_component_clearances':gaps,'nominal_human_routes':routes})
oldarea=1.0668*.762;newarea=1.19888*.6858
out={'status':'READ-ONLY PROPOSAL FIT — awaiting user design direction; no Blender or canonical layout changed','source_inputs':[{'path':str(p),'sha256':hashlib.sha256(p.read_bytes()).hexdigest()} for p in [source,P/'branch-tria-gltf.json',P/'branch-tria.json',P/'branch-tria-specs.pdf',P/'branch-tria-geometry-measurements.json',lp,scene_path,ROOT/'layout/chair-transfer-native-check.json']],'coordinate_conversion':'Supplier GLB metresY-up→native Blender[x,−z,y], source depth recentered on actual desktop. No model rescaling;1.1mm catalog/CAD rounding disclosed. Floor translated to1.575m.','published_dimensions_m':[1.19888,.6858],'supplier_CAD_desktop_dimensions_m':[float(desktop_bounds[1,0]-desktop_bounds[0,0]),float(desktop_bounds[1,2]-desktop_bounds[0,2])],'supplier_CAD_top_thickness_m':float(desktop_bounds[1,1]-desktop_bounds[0,1]),'supplier_CAD_seated_top_height_m':source_top_h,'published_height_range_m':[published_min,published_max],'moving_proxy_assumption':'Official supplier parttags desktop/middle/fixed, with split material primitives inheriting the longest source node prefix;  external sweptbounds use fulltopdelta, halfdelta for middle, zero for fixed. No mechanism internals, assembly loading, cable flex or real motion certified.','actual_area_comparison':{'owned_UPLIFT42x30_area_m2':oldarea,'published_Tria47_2x27_area_m2':newarea,'difference_m2':newarea-oldarea,'percent_gain':100*(newarea/oldarea-1),'width_difference_m':1.19888-1.0668,'depth_difference_m':.6858-.762},'supplier_part_lift_groups':[{'name':p['name'],'lift':p['lift'],'role':p['role']} for p in product_parts],'scenarios':scenarios,'recommendation':'Current center is nominally collision-free by conservative externalpart sweep but leaves fragile26.5mm lamp-base/desk-foot clearance. If Tria chosen, provisionally shift only desk≈35mm right tocenter[-6.915,−.131] to balance lamp-foot and bench-top gaps around6cm. Keep cat, lamp, bench, architecture and primarychair unchanged. This candidate changes proportions/style rather than meaningfully increasing toparea.','limits':['This read-only offline candidate assessment is not a final Blender integration or installation approval.','Source GLB is exact48×27 nominal geometry but Woodgrain/White appearance; selected BlackOak/Charcoal would require clearly disclosed rematerialization using actualphotos after user chooses direction.','CAD tabletop1.200×.685m versus published1.19888×.6858m is ~1mm source rounding; CAD remains undistorted.','Lamp Ubase and cat branch forms remain photo proxies with unpublished details; small numerical gaps cannot establish actualinstalled clearance.','Generalized room outline5–12cm; opening detail3–6cm. Field measurement required.','Swept disjoint AABBs establish proxy geometric separation from other source parts; any reported overlaps are candidates requiring actual triangle/pose verification.','Proposed human routing uses conservative top envelopes and planning circles, not accessibility/code verification.','Chair transfer floor sweep retains verifiedcheckpointpath; actual3D chair motion must be retested against Tria after user choice.','Monitor/keyboard are generic illustrative user-equipment proxies moved with top, not verified actual hardware.','Keep drawers closed during transfer; prior open clothesdrawer+fullchairpullback rearroute restriction remains.']}
p=D/'branch-tria-proposal-fit.json';p.write_text(json.dumps(out,indent=2)+'\n')
print(json.dumps({'area':out['actual_area_comparison'],'scenarios':[{'shift_m':s['desk_only_x_shift_m'],'lamp_gap_m':s['nominal_lamp_Ubase_to_desk_feet_gap_m'],'bench_gap_m':s['top_to_project_bench_x_gap_m'],'cat_low_gap_m':s['cat_low_basket_to_tabletop_underside_at_lowest_published_height_m'],'sweep_candidates':s['full_height_swept_bbox_candidates_against_frozen_other_parts'],'chair_transfer_clear':s['chair_transfer_floor_clear'],'route60_all_states':all(v['checks'][-1]['continuous_nominal_route'] for v in s['nominal_human_routes'])}for s in scenarios]},indent=2))
