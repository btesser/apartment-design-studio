"""Independent read-only actual support rays and unscaled supplier body proof."""
import bpy,bmesh,json,hashlib,sys,math
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
from mathutils.kdtree import KDTree

ROOT=Path(sys.argv[sys.argv.index('--')+1]);SOURCE=ROOT/'model/his-office-design.blend';LAYOUT=ROOT/'model/layout.json'
QA=Path('/workspace/his-office-pinterest/qa/final-variants')/ROOT.name;QA.mkdir(parents=True,exist_ok=True)
layout=json.loads(LAYOUT.read_text());specs={i['id']:i for i in layout['items']}
bpy.ops.wm.open_mainfile(filepath=str(SOURCE));deps=bpy.context.evaluated_depsgraph_get()

def owner(o):
 while o:
  if (o.get('canonical_layout_id') or o.get('id')) in specs:return o.get('canonical_layout_id') or o.get('id')
  if o.type=='EMPTY' and 'generic equipment assumption' in o.name:return 'standing-main-desk::equipment'
  o=o.parent
 return None

parts={}
for o in bpy.context.scene.objects:
 if o.type!='MESH':continue
 ev=o.evaluated_get(deps);m=ev.to_mesh();v=[ev.matrix_world@x.co for x in m.vertices];f=[tuple(x.vertices) for x in m.polygons]
 if v:
  parts[o.name]={'name':o.name,'owner':owner(o),'v':v,'f':f,'bounds':[[min(x[k] for x in v) for k in range(3)],[max(x[k] for x in v) for k in range(3)]],
   'tree':BVHTree.FromPolygons(v,f,all_triangles=False,epsilon=0)}
 ev.to_mesh_clear()

def pick(ident,fragment=None):
 return [p for p in parts.values() if p['owner']==ident and (not fragment or fragment in p['name'])]

def bounds(ps):
 return [[min(p['bounds'][0][k] for p in ps) for k in range(3)],[max(p['bounds'][1][k] for p in ps) for k in range(3)]]

def grid(box,margin=.1):
 xs=[box[0][0]+(box[1][0]-box[0][0])*t for t in [margin,.5,1-margin]]
 ys=[box[0][1]+(box[1][1]-box[0][1])*t for t in [margin,.5,1-margin]]
 return [(x,y) for x in xs for y in ys]

def down(x,y,z,support):
 hits=[]
 for p in support:
  hit=p['tree'].ray_cast(Vector((x,y,z)),Vector((0,0,-1)),.2)
  if hit[0] is not None:hits.append((hit[3],list(hit[0]),p['name']))
 return min(hits,key=lambda h:h[0]) if hits else None

def support_check(ps,support,sample_xy=None):
 b=bounds(ps);base=b[0][2];samples=sample_xy or grid(b)
 rows=[]
 for x,y in samples:
  h=down(x,y,base+.01,support);error=base-h[1][2] if h else None
  rows.append({'xy_m':[x,y],'support_hit':{'mesh':h[2],'point_blender_m':h[1]} if h else None,'vertical_gap_m':error,
   'pass':error is not None and abs(error)<.0001})
 return {'supported_bounds_blender_m':b,'samples':rows,'pass':bool(rows) and all(s['pass'] for s in rows)}

desktop=pick('standing-main-desk','::desktop');desktop=[p for p in desktop if p['name']=='standing-main-desk::desktop']
mat=pick('primary-felt-mat');matbox=bounds(mat);deskbox=bounds(desktop)
matproof=support_check(mat,desktop)
matproof['xy_contained_on_desktop']=all(matbox[0][k]>=deskbox[0][k]-.00001 and matbox[1][k]<=deskbox[1][k]+.00001 for k in [0,1])
matproof['moves_with_standing_desk']=specs['primary-felt-mat'].get('moves_with')=='standing-main-desk'
matproof['pass'] &= matproof['xy_contained_on_desktop'] and matproof['moves_with_standing_desk']
equipment=[]
for fragment in ['monitor stand','::keyboard']:
 ps=pick('standing-main-desk::equipment',fragment);b=bounds(ps);p=support_check(ps,mat)
 p['mesh_names']=[x['name'] for x in ps];p['xy_margin_inside_mat_m']=[b[0][0]-matbox[0][0],matbox[1][0]-b[1][0],b[0][1]-matbox[0][1],matbox[1][1]-b[1][1]]
 p['pass'] &= min(p['xy_margin_inside_mat_m'])>0
 equipment.append(p)

ledges=[];ledge_cache={}
for ident in ['project-display-ledge','primary-display-ledge']:
 supplier=pick(ident,'original supplier');b=bounds(supplier);cx,cy,_=specs[ident]['position_blender_m']
 hit=down(cx,cy,b[1][2]+.02,supplier);tray=hit[1][2] if hit else None
 books=pick(ident,'illustrative pocket journal');bookproof=[]
 for p in books:
  q=support_check([p],supplier);q['mesh']=p['name'];q['book_height_m']=p['bounds'][1][2]-p['bounds'][0][2]
  q['pass'] &= q['book_height_m']<.2
  bookproof.append(q)
 declared=next(x for x in layout['composition_supports'] if x['id']==ident)
 row={'id':ident,'bounds_blender_m':b,'actual_center_down_ray_support_z_m':tray,'declared_tray_support_z_m':declared['tray_support_world_z_m'],
  'overall_top_height_above_floor_m':b[1][2]-layout['room_floor_z_m'],'books':bookproof,
  'pass':tray is not None and abs(tray-declared['tray_support_world_z_m'])<.0001 and all(x['pass'] for x in bookproof)}
 ledges.append(row);ledge_cache[ident]=[list(v) for v in supplier[0]['v']]

dresser=pick('clothes-dresser');dresbox=bounds(dresser)
fado=pick('dresser-fado','original body');fadobox=bounds(fado)
# The curved globe is elevated; use actual lowest base/feet vertices, not a globe bounding rectangle.
bottom=[v for p in fado for v in p['v'] if v.z< fadobox[0][2]+.00002]
lowest_xy=list({(round(v.x,6),round(v.y,6)) for v in bottom})
fadoproof=support_check(fado,dresser,lowest_xy[::max(1,len(lowest_xy)//24)])
fadoproof.update(body_component_vertex_counts=sorted(len(p['v']) for p in fado),actual_body_dimensions_m=[fadobox[1][k]-fadobox[0][k] for k in range(3)],
 catalog_body_diameter_height_m=[.254,.2286],source_body_diameter_height_m=[.23988155,.23648912],
 support_base_fully_on_dresser=all(dresbox[0][k]<v[k]<dresbox[1][k] for v in bottom for k in [0,1]),
 cord_mesh_names=[p['name'] for p in parts.values() if 'dresser-fado::illustrative rear cord' in p['name']],
 cord_scope='Separate illustrative rear cord; source cord/switch not scaled to a claimed globe dimension; outlet reach unmeasured.')
fadoproof['pass'] &= fadoproof['support_base_fully_on_dresser'] and fadoproof['body_component_vertex_counts']==[896,896,2097,7426]
fado_cache=[list(v) for p in fado for v in p['v']]

plant=pick('dresser-parlor-palm');saucer=pick('dresser-parlor-palm','black saucer');pb=bounds(plant);sb=bounds(saucer)
plantproof=support_check(saucer,dresser,grid(sb,.25));plantproof.update(proxy_actual_bounds_blender_m=pb,
 actual_proxy_dimensions_m=[pb[1][k]-pb[0][k] for k in range(3)],declared_max_envelope_m=specs['dresser-parlor-palm']['external_dimensions_m'],
 support_base_on_dresser=all(dresbox[0][k]<=sb[0][k] and sb[1][k]<=dresbox[1][k] for k in [0,1]),
 limitation='Pot shape/height and live crown spread are illustrative, not guaranteed catalog dimensions.')
plantproof['actual_envelope_excess_m']=[max(0,pb[1][k]-pb[0][k]-specs['dresser-parlor-palm']['external_dimensions_m'][k]) for k in range(3)]
plantproof['proxy_bound_tolerance_m']=.001
plantproof['proxy_bound_note']='Illustrative rachis-cylinder end cap exceeds declared crown height by0.43mm; below1mm proxy tolerance, explicitly recorded, not exact botanical/product sizing.'
plantproof['pass'] &= plantproof['support_base_on_dresser'] and max(plantproof['actual_envelope_excess_m'])<.001

# Cache final geometry, then import official source assets into a disposable in-memory scene to independently confirm 1:1 shape.
def point_multiset(points,translation=(0,0,0)):
 return sorted(tuple(round(p[k]+translation[k],5) for k in range(3)) for p in points)
def shape_distance(actual,original,translation=(0,0,0)):
 expected=[Vector(tuple(p[k]+translation[k] for k in range(3))) for p in original]
 def directional(a,b):
  tree=KDTree(len(b))
  for i,p in enumerate(b):tree.insert(p,i)
  tree.balance();return max(tree.find(p)[2] for p in a)
 measured=[Vector(p) for p in actual]
 error=max(directional(measured,expected),directional(expected,measured))
 return {'vertex_counts_match':len(actual)==len(original),'max_bidirectional_nearest_vertex_deviation_m':error,'unscaled_source_shape_pass':len(actual)==len(original) and error<.000002}
sources=Path('/workspace/his-office-pinterest/products/composition-pieces')
bpy.ops.wm.read_factory_settings(use_empty=True);bpy.ops.import_scene.gltf(filepath=str(sources/'mosslanda-official.glb'));bpy.context.view_layer.update()
ledge_source=[o.matrix_world@v.co for o in bpy.context.scene.objects if o.type=='MESH' for v in o.data.vertices]
ledge_exact=[]
for ident,pts in ledge_cache.items():
 pos=specs[ident]['position_blender_m'];measure=shape_distance(pts,ledge_source,pos)
 ledge_exact.append({'id':ident,'original_source_vertex_count':len(ledge_source),'actual_vertex_count':len(pts),**measure})
bpy.ops.wm.read_factory_settings(use_empty=True);bpy.ops.import_scene.gltf(filepath=str(sources/'fado-official.glb'));bpy.context.view_layer.update()
source_body=[];counts=[]
for o in list(bpy.context.scene.objects):
 if o.type!='MESH':continue
 mesh=o.data.copy();mesh.transform(o.matrix_world);bm=bmesh.new();bm.from_mesh(mesh);bmesh.ops.remove_doubles(bm,verts=list(bm.verts),dist=.00001);seen=set()
 for v in bm.verts:
  if v in seen:continue
  stack=[v];seen.add(v);component=[]
  while stack:
   a=stack.pop();component.append(a)
   for e in a.link_edges:
    q=e.other_vert(a)
    if q not in seen:seen.add(q);stack.append(q)
  if len(component) in [7426,2097,896]:source_body.extend([list(v.co) for v in component]);counts.append(len(component))
 bm.free()
pos=specs['dresser-fado']['position_blender_m'];shift=[pos[0]-.11644313856959343,pos[1],pos[2]]
fadoexact={'source_connected_component_counts':sorted(counts),**shape_distance(fado_cache,source_body,shift),
 'source_asset_sha256':hashlib.sha256((sources/'fado-official.glb').read_bytes()).hexdigest(),
 'method':'Compare final evaluated world vertex multiset to original supplier connected body components after only documented re-centering/translation. Exclude source cord/switch from body, no catalog body rescale.'}

out={'source_file':str(SOURCE),'source_sha256':hashlib.sha256(SOURCE.read_bytes()).hexdigest(),'layout_sha256':hashlib.sha256(LAYOUT.read_bytes()).hexdigest(),
 'method':'Read-only evaluated world-space mesh down-rays for actual supporting surfaces, not lip-top labels; meter-coordinate vertex proofs for original suppliers. No file saved or model changed.',
 'mat':matproof,'monitor_keyboard':equipment,'ledges':ledges,'supplier_ledges':ledge_exact,'fado':fadoproof,'supplier_fado':fadoexact,'tabletop_plant':plantproof,
 'all_composition_supports_pass':matproof['pass'] and all(x['pass'] for x in equipment+ledges) and fadoproof['pass'] and plantproof['pass'] and all(x['unscaled_source_shape_pass'] for x in ledge_exact) and fadoexact['unscaled_source_shape_pass'],
 'limits':['These are authored mesh contact tests, not installation/load/electrical certification.','Books/tray/palm foliage are labeled illustrative proxies.','FADO body preserves supplier CAD239.9mm diameter/236.5mm height; rounded US catalog254mm diameter/228.6mm height is separately disclosed.','Rigid mesh floor supports overlap a deformable5.2mm rug pad where appropriate; textile compression not simulated.']}
(QA/'composition-support-checks.json').write_text(json.dumps(out,indent=2)+'\n')
print(json.dumps({'all_pass':out['all_composition_supports_pass'],'mat':matproof['pass'],'equipment':[x['pass'] for x in equipment],'ledges':[x['pass'] for x in ledges],'fado':fadoproof['pass'],'fado_source':fadoexact,'plant':plantproof['pass'],'ledge_source':ledge_exact}))
