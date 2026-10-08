"""Independent read-only actual component QA; never saves a scene."""
import bpy
import hashlib
import itertools
import json
import sys
from collections import Counter
from pathlib import Path
from mathutils.bvhtree import BVHTree

ROOT = Path('/workspace/his-office-pinterest')
args = sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else []
source = Path(args[0]) if args else ROOT/'model/his-office-pinterest-design.blend'
bpy.ops.wm.open_mainfile(filepath=str(source))
layout_path = ROOT/'model/layout.json'
layout = json.loads(layout_path.read_text())
specs = {i['id']: i for i in layout['items']}
aliases = {'kept-uplift-desk':'uplift-main-desk', 'kept-honeywell-02e-pro':'honeywell-lamp',
           'kept-muttros-cat-tree':'muttros-cat-tree', 'branch-pro-task-chair-1':'branch-primary'}
aliases.update({i:i for i in specs if i not in aliases.values()})
deps = bpy.context.evaluated_depsgraph_get()

def group(obj):
    cur=obj
    while cur:
        if cur.name in aliases:
            return aliases[cur.name]
        if 'generic equipment assumption' in cur.name:
            return cur.name.split('::')[0]+'::equipment'
        cur=cur.parent
    return None

parts={}
for obj in bpy.context.scene.objects:
    if obj.type!='MESH':
        continue
    ev=obj.evaluated_get(deps)
    mesh=ev.to_mesh()
    pts=[ev.matrix_world@v.co for v in mesh.vertices]
    if not pts:
        ev.to_mesh_clear(); continue
    faces=[tuple(p.vertices) for p in mesh.polygons]
    lo=[min(v[k] for v in pts) for k in range(3)]
    hi=[max(v[k] for v in pts) for k in range(3)]
    bvh=BVHTree.FromPolygons(pts,faces,all_triangles=False,epsilon=0)
    g=group(obj)
    cols=[c.name for c in obj.users_collection]
    parts[obj.name]={'group':g,'role':obj.get('role',''),'collections':cols,
                     'bounds':[lo,hi],'bvh':bvh,'vertices':len(pts),'polygons':len(faces)}
    ev.to_mesh_clear()

root_checks=[]
for scene_id, canonical_id in aliases.items():
    obj=bpy.data.objects.get(scene_id)
    target=specs[canonical_id]['position_blender_m']
    actual=list(obj.matrix_world.translation) if obj else None
    delta=max(abs(a-b) for a,b in zip(actual,target)) if actual else None
    root_checks.append({'root':scene_id,'layout_id':canonical_id,'canonical':target,'actual':actual,
                        'max_delta_m':delta,'pass':delta is not None and delta<1e-5})

def overlaps(a,b):
    return [min(a['bounds'][1][k],b['bounds'][1][k])-max(a['bounds'][0][k],b['bounds'][0][k]) for k in range(3)]

tested=0
intersections=[]
for (an,a),(bn,b) in itertools.combinations(parts.items(),2):
    # Only different proposal products, or a proposal against measured shell/fixed features.
    if not a['group'] and not b['group']:
        continue
    if a['group']==b['group']:
        continue
    depth=overlaps(a,b)
    if any(d<=.001 for d in depth):
        continue # Ignore numerical/contact-only <1mm bounding overlap.
    tested+=1
    crosses=a['bvh'].overlap(b['bvh'])
    if not crosses:
        continue
    groups=[a['group'],b['group']]
    expected='rug' in groups
    reason='Soft rug pad is intentionally under rolling chair/cat support; pad deformation is not simulated.' if expected else None
    # Monitor/display/keyboard pieces touch the associated desk by design.
    for x,y in [(a,b),(b,a)]:
        if x['group'] and x['group'].endswith('::equipment') and y['group']==x['group'].split('::')[0]:
            expected=True; reason='Generic monitor/keyboard support on its intended desktop.'
    intersections.append({'a':an,'b':bn,'groups':groups,'roles':[a['role'],b['role']],
                          'bbox_overlap_depth_m':depth,'triangle_surface_pairs':len(crosses),
                          'expected_support_or_soft_contact':expected,'reason':reason})

compact=[]
for name,p in parts.items():
    compact.append({'name':name,**{k:v for k,v in p.items() if k!='bvh'}})
out={'source_file':str(source),'source_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),
     'layout_sha256':hashlib.sha256(layout_path.read_bytes()).hexdigest(),
     'method':'Read-only native Blender evaluated world-space parts; AABB overlap >1mm in all three axes followed by exact mesh-triangle BVH overlap. No scene saved.',
     'limits':['Surface test does not detect a fully contained solid without crossing boundaries.',
               'Source walls/fixtures and owned product subcomponents have documented measurement/photo-proxy uncertainty. Export transform tolerance does not imply site accuracy.',
               'Rug-pad support is soft contact; compressed textile/rolling-caster contact is not mechanically simulated.',
               'Closed observed door leaves tested in their current modeled state. Open-door circulation is assessed separately.'],
     'canonical_root_position_parity':root_checks,
     'all_roots_match_canonical':all(x['pass'] for x in root_checks),
     'mesh_count':len(parts),'mesh_role_counts':dict(Counter(p['role'] for p in parts.values())),
     'broad_phase_nontrivial_pairs_tested':tested,
     'surface_intersections':intersections,
     'unintended_surface_intersection_count':sum(not x['expected_support_or_soft_contact'] for x in intersections),
     'parts':compact}
path=ROOT/'qa/integrated-mesh-checks.json'
path.write_text(json.dumps(out,indent=2)+'\n')
print(json.dumps({'proof':str(path),'roots_pass':out['all_roots_match_canonical'],'meshes':len(parts),'broad_pairs':tested,
                  'unintended_surface_intersections':out['unintended_surface_intersection_count'],
                  'intersections':intersections}))
