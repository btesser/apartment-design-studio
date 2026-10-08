"""Read-only owned lamp head topology and unchanged product-root checks."""
import bpy,hashlib,json
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
ROOT=Path('/workspace/his-office-redesign');source=ROOT/'model/his-office-design.blend'
bpy.ops.wm.open_mainfile(filepath=str(source));deps=bpy.context.evaluated_depsgraph_get()
root=bpy.data.objects['kept-honeywell-02e-pro']; center=list(root.matrix_world.translation)
bvhs=[]; bounds=[]
for o in bpy.context.scene.objects:
    p=o
    while p and p!=root:p=p.parent
    if p is None or o.type!='MESH':continue
    ev=o.evaluated_get(deps);me=ev.to_mesh();vs=[ev.matrix_world@v.co for v in me.vertices]
    fs=[tuple(p.vertices) for p in me.polygons]
    bvhs.append((o.name,BVHTree.FromPolygons(vs,fs,all_triangles=False,epsilon=0)))
    bounds.append([[min(v[k] for v in vs) for k in range(3)],[max(v[k] for v in vs) for k in range(3)]])
    ev.to_mesh_clear()
cases=[]
for x in [-.03,0,.03]:
    for y in [-.1,0,.1]:cases.append((x,y,None))
cases.extend([(-.075,0,'Narrow parallel LED light bar'),(.075,0,'Narrow parallel LED light bar'),(-.135018,0,'Rectangular panel long rim'),(.135018,0,'Rectangular panel long rim')])
results=[]
for x,y,expect in cases:
    origin=Vector((center[0]+x,center[1]+y,3.8));hits=[]
    for name,bvh in bvhs:
        pt,n,i,d=bvh.ray_cast(origin,Vector((0,0,-1)),.5)
        if pt is not None:hits.append((d,name,list(pt)))
    first=min(hits) if hits else None
    ok=(first is None) if expect is None else bool(first and first[1].startswith(expect))
    results.append({'ray_origin_blender_m':list(origin),'expected':expect or 'Open aperture; no lamp head hit within0.5m downward ray','first_hit':{'name':first[1],'point':first[2]} if first else None,'pass':ok})
actual=[[min(b[0][k] for b in bounds) for k in range(3)],[max(b[1][k] for b in bounds) for k in range(3)]]
out={'source_file':str(source),'source_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'root_native_m':center,
     'actual_whole_lamp_bounds_blender_m':actual,'expected_overall_dimensions_m':[.288036,.610108,1.9685],
     'method':'Read-only evaluated owned-lamp mesh BVH;9 vertical rays through central aperture plus2 LED-bar and2 perimeter positive-control rays. No model saved.',
     'cases':results,'all_cases_pass':all(r['pass'] for r in results),
     'source':'Exact Honeywell02E Pro ASINB0C3BVYTXP source photograph shows an open rectangular perimeter and two narrow diffusers.',
     'limits':['Fine lamp frame/base profiles remain photo-derived review approximations; test verifies restored head topology, not exact manufactured dimensions.']}
p=ROOT/'qa/lamp-aperture-check.json';p.write_text(json.dumps(out,indent=2)+'\n')
print(json.dumps({'proof':str(p),'pass':out['all_cases_pass'],'bounds':actual,'failures':[r for r in results if not r['pass']]}))
