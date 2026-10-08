"""Read-only full Tria stroke external clearance, with supplier motion tags."""
import bpy
import hashlib
import json
import sys
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree

args=sys.argv[sys.argv.index('--')+1:];ROOT=Path(args[0])
QA=Path('/workspace/his-office-pinterest/qa/final-variants')/ROOT.name
SOURCE=ROOT/'model/his-office-design.blend'
layout=json.loads((ROOT/'model/layout.json').read_text())
mapping=json.loads((ROOT/'model/tria-component-map.json').read_text())
current=mapping['seated_top_m'];limits=mapping['height_range_m']
delta=[h-current for h in limits]
bpy.ops.wm.open_mainfile(filepath=str(SOURCE));deps=bpy.context.evaluated_depsgraph_get()


def ancestor(o,predicate):
    while o:
        if predicate(o):return o
        o=o.parent
    return None


moving={};fixed={};excluded=[]
for o in bpy.context.scene.objects:
    if o.type!='MESH':continue
    desk=ancestor(o,lambda x:(x.get('canonical_layout_id') or x.get('id'))=='standing-main-desk')
    equipment=ancestor(o,lambda x:x.type=='EMPTY' and x.name=='standing-main-desk::generic equipment assumption')
    task=ancestor(o,lambda x:(x.get('canonical_layout_id') or x.get('id'))=='branch-primary')
    if '--exclude-chair' in args and task:
        excluded.append(o.name);continue
    group=o.get('supplier_lift_group')
    factor={'desktop':1,'middle':.5,'fixed':0}.get(group,1 if equipment else 0)
    if desk and factor==0:continue # Its own mechanical feet/outer-column interfaces.
    ev=o.evaluated_get(deps);m=ev.to_mesh();vs=[ev.matrix_world@v.co for v in m.vertices];fs=[tuple(p.vertices) for p in m.polygons]
    if vs:
        p={'points':vs,'faces':fs,'factor':factor,'bounds':[[min(v[k] for v in vs) for k in range(3)],[max(v[k] for v in vs) for k in range(3)]],
           'bvh':BVHTree.FromPolygons(vs,fs,all_triangles=False,epsilon=0)}
        (moving if factor else fixed)[o.name]=p
    ev.to_mesh_clear()


def overlap(a,b):return all(min(a[1][k],b[1][k])-max(a[0][k],b[0][k])>.001 for k in range(3))


candidates=[]
for an,a in moving.items():
    box=[list(a['bounds'][0]),list(a['bounds'][1])];box[0][2]+=delta[0]*a['factor'];box[1][2]+=delta[1]*a['factor']
    for bn,b in fixed.items():
        if overlap(box,b['bounds']):candidates.append((an,bn))
heights=sorted(set([current,limits[0],limits[1],sum(limits)/2]+[limits[0]+(limits[1]-limits[0])*i/48 for i in range(49)]))
hits=[]
for h in heights:
    for an,bn in candidates:
        a,b=moving[an],fixed[bn];dz=(h-current)*a['factor']
        box=[list(a['bounds'][0]),list(a['bounds'][1])];box[0][2]+=dz;box[1][2]+=dz
        if not overlap(box,b['bounds']):continue
        tree=BVHTree.FromPolygons([v+Vector((0,0,dz)) for v in a['points']],a['faces'],all_triangles=False,epsilon=0)
        crossing=tree.overlap(b['bvh'])
        if crossing:hits.append({'top_height_m':h,'moving':an,'fixed':bn,'triangle_surface_pairs':len(crossing)})
out={'source_file':str(SOURCE),'source_sha256':hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
     'layout_sha256':hashlib.sha256((ROOT/'model/layout.json').read_bytes()).hexdigest(),
     'nominal_overall_top_height_range_m':limits,'displayed_top_height_m':current,
     'method':'Supplier-tagged upper parts and generic monitor/keyboard translate by full stroke; middle stages by half; own feet/outer stages fixed. Conservative complete swept bounds first;49 height samples plus seated/mid/endpoints for candidates. No source pose or artifact saved.',
     'moving_parts':[{'mesh':n,'height_factor':p['factor']} for n,p in moving.items()],
     'whole_range_swept_candidates':[list(p) for p in candidates],'heights_sampled_m':heights,'surface_intersections':hits,
     'excluded_pending_task_chair_meshes':excluded,'scope':'Unchanged external furniture/room checkpoint only; owned chair geometry pending' if excluded else 'Final modeled external stroke, including current owned-chair proxy',
     'all_tested_external_clearance_pass':not hits,
     'limits':['Mechanical internals, actuator travel, cable flex/slack, loading, stability, real user body and chair settings are not simulated.',
               'Sampled overlapping swept candidates cannot prove every intermediate state; disjoint whole-range bounds rule out overlap for those proxy parts.',
               'Cat branch offsets and lamp U-base detail remain unpublished/photo-derived field checks.',
               'Internal monitor/table support fit is assessed separately by the static assembly check.']}
(QA/'tria-height-operation.json').write_text(json.dumps(out,indent=2)+'\n')
print(json.dumps({'moving':len(moving),'candidates':out['whole_range_swept_candidates'],'hits':hits,'excluded_chair':excluded}))
