"""Read-only final-scene floor-obstacle extraction and actual chair transfer sweep check."""
import bpy,json,hashlib,sys,math
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
ROOT=Path('/workspace/his-office-pinterest');source=ROOT/'model/his-office-pinterest-design.blend';lp=ROOT/'model/layout.json'
bpy.ops.wm.open_mainfile(filepath=str(source));deps=bpy.context.evaluated_depsgraph_get();layout=json.loads(lp.read_text());specs={i['id']:i for i in layout['items']};floor=layout['room_floor_z_m']
aliases={'kept-uplift-desk':'uplift-main-desk','kept-honeywell-02e-pro':'honeywell-lamp','kept-muttros-cat-tree':'muttros-cat-tree','branch-pro-task-chair-1':'branch-primary'}
aliases.update({i:i for i in specs})
def owner(o):
 while o:
  if o.name in aliases:return aliases[o.name]
  o=o.parent
 return None
parts={}
for obj in bpy.context.scene.objects:
 if obj.type!='MESH' or obj.get('role')=='presentation_only' or obj.name.startswith('rug::'):continue
 ev=obj.evaluated_get(deps);mesh=ev.to_mesh();vs=[ev.matrix_world@v.co for v in mesh.vertices];fs=[tuple(p.vertices) for p in mesh.polygons]
 if vs:
  lo=[min(v[k] for v in vs) for k in range(3)];hi=[max(v[k] for v in vs) for k in range(3)];g=owner(obj)
  parts[obj.name]={'group':g,'bounds':[lo,hi],'vs':vs,'fs':fs,'bvh':BVHTree.FromPolygons(vs,fs,all_triangles=False,epsilon=0)}
 ev.to_mesh_clear()
chair={n:p for n,p in parts.items() if p['group']=='branch-primary'};fixed={n:p for n,p in parts.items() if p['group']!='branch-primary'}
start=specs['branch-primary']['position_blender_m'][:2];target=[-5.4225,-.60]
waypoints=[start,[start[0],start[1]-.10],[target[0],start[1]-.10],target]
def intersect_bounds(a,b):return all(min(a[1][k],b[1][k])-max(a[0][k],b[0][k])>.001 for k in range(3))
def moved(bounds,delta):return [[v[k]+delta[k] for k in range(3)] for v in bounds]
hits=[];candidate_records=[];sample_count=0
for sn,(a,b) in enumerate(zip(waypoints,waypoints[1:])):
 da=Vector((a[0]-start[0],a[1]-start[1],0));db=Vector((b[0]-start[0],b[1]-start[1],0))
 candidates=[]
 for cn,c in chair.items():
  aa=moved(c['bounds'],da);bb=moved(c['bounds'],db);swept=[[min(aa[0][k],bb[0][k]) for k in range(3)],[max(aa[1][k],bb[1][k]) for k in range(3)]]
  for fn,f in fixed.items():
   if intersect_bounds(swept,f['bounds']):candidates.append((cn,fn))
 candidate_records.append({'segment':sn+1,'waypoint_from_m':a,'waypoint_to_m':b,'candidate_pairs':[list(p) for p in candidates]})
 # 20mm maximum center step, min3samplepoints per segment
 steps=max(2,math.ceil(math.dist(a,b)/.02))
 for k in range(steps+1):
  delta=da+(db-da)*(k/steps);sample_count+=1
  for cn,fn in candidates:
   c=chair[cn];f=fixed[fn]
   if not intersect_bounds(moved(c['bounds'],delta),f['bounds']):continue
   cb=BVHTree.FromPolygons([v+delta for v in c['vs']],c['fs'],all_triangles=False,epsilon=0)
   pairs=cb.overlap(f['bvh'])
   if pairs:hits.append({'segment':sn+1,'sample':k,'center_m':[start[0]+delta.x,start[1]+delta.y],'chair_part':cn,'fixed_part':fn,'triangle_surface_pairs':len(pairs)})
floor_parts=[]
for n,p in fixed.items():
 if p['group'] in ['uplift-main-desk','secondary-workspace','honeywell-lamp','muttros-cat-tree','clothes-dresser','visitor-chair'] and p['bounds'][0][2]<=floor+.20 and p['bounds'][1][2]>=floor:
  floor_parts.append({'name':n,'group':p['group'],'world_bounds_m':p['bounds'],'floor_selection_note':'Conservative wholeXY part AABB if part enters lowest20cm abovefloor; excludes overhead desktop but includes whole low-reaching leg/condo projection.'})
out={'source_file':str(source),'source_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'layout_file':str(lp),'layout_sha256':hashlib.sha256(lp.read_bytes()).hexdigest(),'waypoints_blender_xy_m':waypoints,'chair_start_center_m':start,'bench_seated_center_m':target,'floor_z_m':floor,'chair_caster_diameter_m':specs['branch-primary']['rolling_base_diameter_m'],'floor_obstacles':floor_parts,'native_swept_AABB_candidates':candidate_records,'native_sample_count':sample_count,'native_maximum_center_step_m':.02,'native_surface_intersections':hits,'native_no_sampled_unintended_intersections':not hits,'limits':['Whole scene surface-BVH tests at <=20mm path samples; not a mathematical continuum proof for overlapping swept candidates.','Surface tests do not establish every possible fully contained solid.','No user body, moving caster swivel, compressed rug, cable slack or force/friction model.','Dresser and ALEX drawers remain closed during chair transfer; sequential clothes-drawer operation still required.','Nominal measured/model furniture positions; actual scan uncertainty and owned-product proxy limits remain.']}
p=ROOT/'layout/chair-transfer-native-check.json';p.write_text(json.dumps(out,indent=2)+'\n');print(json.dumps({'proof':str(p),'sample_count':sample_count,'candidates':sum(len(r['candidate_pairs']) for r in candidate_records),'hits':hits,'floor_parts':len(floor_parts)}))
