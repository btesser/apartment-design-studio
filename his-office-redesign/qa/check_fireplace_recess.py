"""Read-only architectural ray tests for the repaired recessed closed arch."""
import bpy
import hashlib
import json
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree

ROOT=Path('/workspace/his-office-redesign');source=ROOT/'model/his-office-design.blend'
bpy.ops.wm.open_mainfile(filepath=str(source))
deps=bpy.context.evaluated_depsgraph_get();bvhs=[]
for obj in bpy.context.scene.objects:
    if obj.type!='MESH' or obj.get('role') not in ['architecture','fixed_fixture']:continue
    ev=obj.evaluated_get(deps);mesh=ev.to_mesh()
    vs=[ev.matrix_world@v.co for v in mesh.vertices];fs=[tuple(p.vertices) for p in mesh.polygons]
    if vs:bvhs.append((obj.name,BVHTree.FromPolygons(vs,fs,all_triangles=False,epsilon=0)))
    ev.to_mesh_clear()

cases=[(x,z,'Observed recessed white arched fireplace infill',-2.835)
       for x in [-5.535,-5.315,-5.095] for z in [1.75,2.10,2.32]]
cases.append((-5.315,2.43,'Observed recessed white arched fireplace infill',-2.835))
cases += [(x,z,'Observed brick chimney projection',-2.722) for x,z in [(-5.69,2.02),(-4.94,2.02),(-5.315,2.53)]]
results=[]
for x,z,expected,y in cases:
    origin=Vector((x,-2.0,z));direction=Vector((0,-1,0));hits=[]
    for name,bvh in bvhs:
        location,normal,index,distance=bvh.ray_cast(origin,direction,2)
        if location is not None:hits.append((distance,name,list(location)))
    nearest=min(hits) if hits else None
    ok=bool(nearest and nearest[1]==expected and abs(nearest[2][1]-y)<.0001)
    results.append({'ray_origin_blender_m':list(origin),'expected_first_object':expected,'expected_surface_y_m':y,
                    'actual_first_hit':{'object':nearest[1],'point_blender_m':nearest[2]} if nearest else None,'pass':ok})
out={'source_file':str(source),'source_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),
     'method':'Read-only evaluated architecture/fixed-fixture mesh BVH rays from room toward brick wall;10 points within the arch plus3 outside test first visible surfaces.',
     'expected_recess_depth_m':.113,'all_cases_pass':all(r['pass'] for r in results),'cases':results,
     'limits':['Tests repaired proxy topology and measured plane offsets, not exact raw arch curve or masonry detailing. Numerical tolerance is model verification, not site measurement accuracy.']}
p=ROOT/'qa/fireplace-recess-check.json';p.write_text(json.dumps(out,indent=2)+'\n')
print(json.dumps({'proof':str(p),'pass':out['all_cases_pass'],'failures':[r for r in results if not r['pass']]}))
