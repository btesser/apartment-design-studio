"""Read-only two-chair pullback proxy check, without saving changed positions."""
import bpy
import hashlib
import json
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree

import sys
variant_args=sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else sys.argv[1:]
ROOT=Path(variant_args[0])
QA=Path('/workspace/his-office-pinterest/qa/final-variants')/ROOT.name
QA.mkdir(parents=True,exist_ok=True)
source=ROOT/'model/his-office-design.blend'
bpy.ops.wm.open_mainfile(filepath=str(source));deps=bpy.context.evaluated_depsgraph_get()
chair_names=['branch-pro-task-chair-1']

def chair_owner(o):
    while o:
        if o.name in chair_names:return o.name
        o=o.parent
    return None

parts={}
for obj in bpy.context.scene.objects:
    if obj.type!='MESH':continue
    if obj.name.startswith('rug::') or obj.get('role')=='presentation_only':continue
    ev=obj.evaluated_get(deps);mesh=ev.to_mesh()
    vs=[ev.matrix_world@v.co for v in mesh.vertices];fs=[tuple(p.vertices) for p in mesh.polygons]
    if vs:
        lo=[min(v[k] for v in vs) for k in range(3)];hi=[max(v[k] for v in vs) for k in range(3)]
        parts[obj.name]={'chair':chair_owner(obj),'vs':vs,'fs':fs,'bounds':[lo,hi],
                         'bvh':BVHTree.FromPolygons(vs,fs,all_triangles=False,epsilon=0)}
    ev.to_mesh_clear()

def overlap(a,b):return all(min(a[1][k],b[1][k])-max(a[0][k],b[0][k])>.001 for k in range(3))
fixed={n:p for n,p in parts.items() if not p['chair']};moving={n:p for n,p in parts.items() if p['chair']}
candidates=[]
for an,a in moving.items():
    bounds=[list(a['bounds'][0]),list(a['bounds'][1])];bounds[0][1]-=.45
    for bn,b in fixed.items():
        if overlap(bounds,b['bounds']):candidates.append((an,bn))
hits=[]
steps=[.45*i/16 for i in range(17)]
for dy in steps:
    for an,bn in candidates:
        a=moving[an];b=fixed[bn]
        bounds=[list(a['bounds'][0]),list(a['bounds'][1])];bounds[0][1]-=dy;bounds[1][1]-=dy
        if not overlap(bounds,b['bounds']):continue
        av=BVHTree.FromPolygons([v+Vector((0,-dy,0)) for v in a['vs']],a['fs'],all_triangles=False,epsilon=0)
        crosses=av.overlap(b['bvh'])
        if crosses:hits.append({'backward_translation_m':dy,'chair_part':an,'fixed_part':bn,'triangle_surface_pairs':len(crosses)})
out={'source_file':str(source),'source_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),
     'canonical_layout_sha256':hashlib.sha256((ROOT/'model/layout.json').read_bytes()).hexdigest(),
     'method':'Native evaluated actual task-chair meshes translated backwards up to45cm. Full swept AABB versus fixed scene parts, then17 triangle-BVH samples for remaining candidates. Rug soft contacts omitted. Only one retained task chair is moved.',
     'whole_sweep_candidates':[list(x) for x in candidates],'translations_tested_m':steps,
     'surface_intersections':hits,'no_sampled_unintended_intersections':not hits,
     'limits':['Chair rolling/caster orientation, rug compression, user bodies and unmeasured real product differences are not dynamically simulated.',
               'Sampled tests for overlapping swept bounds do not prove every intermediate pose; disjoint swept bounds rule out the other obstacles for the proxy.',
               'Dresser drawers are closed during this test; full open drawer and pullback standing clearance is separately qualified.']}
p=QA/'chair-pullback-operation.json';p.write_text(json.dumps(out,indent=2)+'\n')
print(json.dumps({'proof':str(p),'candidates':out['whole_sweep_candidates'],'hits':hits}))
