"""Read-only sit/stand upper-assembly clearance check; no source pose changed."""
import bpy
import hashlib
import json
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree

ROOT=Path('/workspace/his-office-pinterest')
source=ROOT/'model/his-office-pinterest-design.blend'
bpy.ops.wm.open_mainfile(filepath=str(source))
research=json.loads((Path('/workspace/his-office-redesign/products/keepers/keepers-research.json')).read_text())
height_range=research['products']['desk']['dimensions']['overall_height_range_with_confirmed_top']['meters']
layout=json.loads((ROOT/'model/layout.json').read_text())
current=next(i['external_dimensions_m'][2] for i in layout['items'] if i['id']=='uplift-main-desk')
delta_range=[h-current for h in height_range]
deps=bpy.context.evaluated_depsgraph_get()

def belongs(o, name):
    while o:
        if o.name==name:return True
        o=o.parent
    return False

move_words=['solid wood barkline top','V2 upper stage','Underside side bracket',
            'triangular stability brace','Hidden upper crossbar','grommet covers','Height keypad']
moving={}; fixed={}
for obj in bpy.context.scene.objects:
    if obj.type!='MESH':continue
    own=belongs(obj,'kept-uplift-desk')
    is_equipment=belongs(obj,'uplift-main-desk::generic equipment assumption')
    is_moving=is_equipment or (own and any(w in obj.name for w in move_words))
    if own and not is_moving:continue # Own feet and telescoping stages are not external obstacles.
    ev=obj.evaluated_get(deps); mesh=ev.to_mesh()
    pts=[ev.matrix_world@v.co for v in mesh.vertices]
    faces=[tuple(p.vertices) for p in mesh.polygons]
    if pts:
        bounds=[[min(v[k] for v in pts) for k in range(3)],[max(v[k] for v in pts) for k in range(3)]]
        data={'points':pts,'faces':faces,'bounds':bounds,'bvh':BVHTree.FromPolygons(pts,faces,all_triangles=False,epsilon=0)}
        (moving if is_moving else fixed)[obj.name]=data
    ev.to_mesh_clear()

def overlaps(a,b):
    return all(min(a[1][k],b[1][k])-max(a[0][k],b[0][k])>.001 for k in range(3))

swept=[]
for an,a in moving.items():
    box=[list(a['bounds'][0]),list(a['bounds'][1])]
    box[0][2]+=delta_range[0];box[1][2]+=delta_range[1]
    for bn,b in fixed.items():
        if overlaps(box,b['bounds']):swept.append((an,bn))

samples=sorted(set([height_range[0],current,(height_range[0]+height_range[1])/2,height_range[1]]+
                   [height_range[0]+(height_range[1]-height_range[0])*i/32 for i in range(33)]))
hits=[]
for height in samples:
    dz=height-current
    for an,bn in swept:
        a=moving[an];b=fixed[bn]
        bounds=[list(a['bounds'][0]),list(a['bounds'][1])]
        bounds[0][2]+=dz;bounds[1][2]+=dz
        if not overlaps(bounds,b['bounds']):continue
        av=BVHTree.FromPolygons([v+Vector((0,0,dz)) for v in a['points']],a['faces'],all_triangles=False,epsilon=0)
        crosses=av.overlap(b['bvh'])
        if crosses:hits.append({'top_height_m':height,'moving':an,'fixed':bn,'triangle_surface_pairs':len(crosses)})

cat_lamp_pairs=[list(p) for p in swept if belongs(bpy.data.objects[p[1]],'kept-muttros-cat-tree') or belongs(bpy.data.objects[p[1]],'kept-honeywell-02e-pro')]
out={'source_file':str(source),'source_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),
     'layout_sha256':hashlib.sha256((ROOT/'model/layout.json').read_bytes()).hexdigest(),
     'official_source':'Official V2 C-frame specification PDF, 24.3–49.9-inch frame range plus 1.75-inch Pheasantwood top.',
     'nominal_overall_top_height_range_m':height_range,'displayed_top_height_m':current,
     'method':'No model saved. Upper desktop/side brackets/braces/crossbar/keypad/grommets and equipment translated vertically; feet fixed. Whole-range swept world bounds first, then evaluated triangle BVH at endpoints,current,midpoint,and33 evenly spaced height samples for remaining candidates.',
     'moving_parts':list(moving),'whole_range_swept_candidates':[list(p) for p in swept],
     'cat_or_lamp_whole_range_swept_candidates':cat_lamp_pairs,
     'heights_sampled_m':samples,'surface_intersections':hits,
     'limits':['Does not validate actual actuator/cable travel, load ratings, dynamic stability or mechanical telescoping internals.',
               'Unpublished cat-tree branch offsets and lamp U-base geometry remain field checks.',
               'Swept boxes conclusively rule out intersections only where they are disjoint. Sampled triangle checks cannot prove all intermediate clearances for overlapping swept candidates.',
               'Chair arms may need adjustment/tucking when changing desk height; no seated ergonomics certification.'],
     'cat_lamp_clear_in_proxy_for_full_nominal_range':len(cat_lamp_pairs)==0}
p=ROOT/'qa/desk-height-operation.json';p.write_text(json.dumps(out,indent=2)+'\n')
print(json.dumps({'proof':str(p),'moving_parts':len(moving),'swept_candidates':out['whole_range_swept_candidates'],
                  'cat_lamp_whole_range_clear':out['cat_lamp_clear_in_proxy_for_full_nominal_range'],'hits':hits}))
