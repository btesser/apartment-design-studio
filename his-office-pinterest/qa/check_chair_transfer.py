"""Read-only occasional transfer of the one chair to the clear project bench."""
import bpy
import hashlib
import json
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree

BASE=Path('/workspace/his-office-pinterest')
SOURCE=BASE/'model/his-office-pinterest-design.blend'
layout=json.loads((BASE/'model/layout.json').read_text())
chair_spec=next(i for i in layout['items'] if i['id']=='branch-primary')
start=chair_spec['position_blender_m']
# Retained empty knee bay on the right side of LEFT ALEX pedestal.
end=[-5.4,-.8,start[2]]
delta=Vector(end)-Vector(start)
bpy.ops.wm.open_mainfile(filepath=str(SOURCE));deps=bpy.context.evaluated_depsgraph_get()

def is_chair(o):
    while o:
        if o.name=='branch-pro-task-chair-1':return True
        o=o.parent
    return False

parts={}
for o in bpy.context.scene.objects:
    if o.type!='MESH' or o.name.startswith('rug::') or o.get('role')=='presentation_only':continue
    ev=o.evaluated_get(deps);m=ev.to_mesh()
    vs=[ev.matrix_world@v.co for v in m.vertices];fs=[tuple(f.vertices) for f in m.polygons]
    if vs:
        parts[o.name]={'moving':is_chair(o),'vs':vs,'fs':fs,
                       'bounds':[[min(v[k] for v in vs) for k in range(3)],
                                 [max(v[k] for v in vs) for k in range(3)]],
                       'bvh':BVHTree.FromPolygons(vs,fs,all_triangles=False,epsilon=0)}
    ev.to_mesh_clear()

def overlap(a,b):return all(min(a[1][k],b[1][k])-max(a[0][k],b[0][k])>.001 for k in range(3))

pairs=[]
for an,a in parts.items():
    if not a['moving']:continue
    swept=[[a['bounds'][0][k]+min(0,delta[k]) for k in range(3)],
           [a['bounds'][1][k]+max(0,delta[k]) for k in range(3)]]
    for bn,b in parts.items():
        if not b['moving'] and overlap(swept,b['bounds']):pairs.append((an,bn))
hits=[]
samples=[i/32 for i in range(33)]
for t in samples:
    shift=t*delta
    for an,bn in pairs:
        a,b=parts[an],parts[bn]
        bounds=[[a['bounds'][j][k]+shift[k] for k in range(3)] for j in range(2)]
        if not overlap(bounds,b['bounds']):continue
        tree=BVHTree.FromPolygons([v+shift for v in a['vs']],a['fs'],all_triangles=False,epsilon=0)
        crossing=tree.overlap(b['bvh'])
        if crossing:hits.append({'transfer_fraction':t,'chair_part':an,'fixed_part':bn,'triangle_surface_pairs':len(crossing)})
out={'source_file':str(SOURCE),'source_sha256':hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
     'canonical_layout_sha256':hashlib.sha256((BASE/'model/layout.json').read_bytes()).hexdigest(),
     'start_blender_m':start,'end_blender_m':end,'chair_rotation_changed':False,
     'method':'Actual evaluated primary-chair meshes translated along a straight lateral path to the project-bench right knee bay. Whole swept bounds versus fixed scene, then33 triangle-BVH samples for overlapping candidates. No scene saved.',
     'whole_sweep_candidates':[list(p) for p in pairs],'transfer_fractions_tested':samples,
     'surface_intersections':hits,'no_sampled_unintended_intersections':not hits,
     'limits':['Proxy furniture only: user bodies, real caster direction, cable slack and chair adjustment are not dynamically simulated.',
               'Sampled overlapping swept candidates cannot establish a mathematical guarantee between samples.',
               'Occasional bench use shares the one chair; no simultaneous second seated workstation is proposed.']}
(BASE/'qa/chair-transfer-operation.json').write_text(json.dumps(out,indent=2)+'\n')
print(json.dumps({'candidates':out['whole_sweep_candidates'],'hits':hits}))
