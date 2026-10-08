"""Read-only actual Aeron proxy pullback, staged transfer and full-turn checks."""
import bpy
import hashlib
import json
import math
import sys
from pathlib import Path
from mathutils import Vector,Matrix
from mathutils.bvhtree import BVHTree

args=sys.argv[sys.argv.index('--')+1:];ROOT=Path(args[0])
QA=Path('/workspace/his-office-pinterest/qa/final-variants')/ROOT.name
SOURCE=ROOT/'model/his-office-design.blend';LAYOUT=ROOT/'model/layout.json'
PREFLIGHT=Path('/workspace/his-office-pinterest/layout/geometry-fit-preflight/owned-aeron-bounded-preflight.json')
layout=json.loads(LAYOUT.read_text());preflight=json.loads(PREFLIGHT.read_text())
chairs=[i for i in layout['items'] if i.get('kind') in ['task_chair','owned_task_chair','owned_primary_task_chair']]
assert len(chairs)==1,'Exactly one office task chair required'
spec=chairs[0];start=Vector(spec['position_blender_m'])
bpy.ops.wm.open_mainfile(filepath=str(SOURCE));deps=bpy.context.evaluated_depsgraph_get()


def owns(o):
    while o:
        if (o.get('canonical_layout_id') or o.get('id'))==spec['id']:return True
        o=o.parent
    return False


parts={}
for o in bpy.context.scene.objects:
    if o.type!='MESH' or o.name.startswith('rug::') or o.get('role')=='presentation_only':continue
    ev=o.evaluated_get(deps);m=ev.to_mesh();vs=[ev.matrix_world@v.co for v in m.vertices];fs=[tuple(p.vertices) for p in m.polygons]
    if vs:
        parts[o.name]={'moving':owns(o),'vs':vs,'fs':fs,'bounds':[[min(v[k] for v in vs) for k in range(3)],[max(v[k] for v in vs) for k in range(3)]],
                       'bvh':BVHTree.FromPolygons(vs,fs,all_triangles=False,epsilon=0)}
    ev.to_mesh_clear()
moving={n:p for n,p in parts.items() if p['moving']};fixed={n:p for n,p in parts.items() if not p['moving']}
assert moving,'Owned chair root has no active meshes'


def overlap(a,b):return all(min(a[1][k],b[1][k])-max(a[0][k],b[0][k])>.001 for k in range(3))


route=preflight['max_arm_profile']['bench_transfer_and_rotation']
waypoints=[Vector((x,y,start.z)) for x,y in route['candidate_waypoints_xy_m']]
assert (waypoints[0]-start).length<1e-5,'Operation witness must start at final canonical chair pose'
translation_results=[]
for segment,(a,b) in enumerate(zip(waypoints,waypoints[1:])):
    initial=a-start;delta=b-a;pairs=[]
    for an,p in moving.items():
        box=[[p['bounds'][0][k]+initial[k]+min(0,delta[k]) for k in range(3)],
             [p['bounds'][1][k]+initial[k]+max(0,delta[k]) for k in range(3)]]
        for bn,q in fixed.items():
            if overlap(box,q['bounds']):pairs.append((an,bn))
    hits=[]
    for step in range(33):
        shift=initial+delta*(step/32)
        for an,bn in pairs:
            p,q=moving[an],fixed[bn]
            box=[[p['bounds'][j][k]+shift[k] for k in range(3)] for j in range(2)]
            if not overlap(box,q['bounds']):continue
            tree=BVHTree.FromPolygons([v+shift for v in p['vs']],p['fs'],all_triangles=False,epsilon=0)
            crossing=tree.overlap(q['bvh'])
            if crossing:hits.append({'sample_fraction':step/32,'chair_part':an,'fixed_part':bn,'triangle_surface_pairs':len(crossing)})
    translation_results.append({'segment':segment,'start_blender_m':list(a),'end_blender_m':list(b),
                                'whole_swept_candidates':[list(p) for p in pairs],'surface_intersections':hits,'pass':not hits})

turn_xy=route['full_rotation']['center_xy_m'];turn=Vector((*turn_xy,start.z))
points=[v for p in moving.values() for v in p['vs']]
actual_radius=max(math.hypot(v.x-start.x,v.y-start.y) for v in points)
published_radius=route['full_rotation']['conservative_diameter_m']/2
radius=max(actual_radius,published_radius)
turn_box=[[turn.x-radius,turn.y-radius,min(v.z for v in points)],
          [turn.x+radius,turn.y+radius,max(v.z for v in points)]]
turn_candidates=[n for n,p in fixed.items() if overlap(turn_box,p['bounds'])]
turn_hits=[]
if turn_candidates:
    for step in range(49):
        angle=2*math.pi*step/48;rotation=Matrix.Rotation(angle,3,'Z')
        for an,p in moving.items():
            vs=[turn+rotation@(v-start) for v in p['vs']]
            box=[[min(v[k] for v in vs) for k in range(3)],[max(v[k] for v in vs) for k in range(3)]]
            tree=None
            for bn in turn_candidates:
                q=fixed[bn]
                if not overlap(box,q['bounds']):continue
                if tree is None:tree=BVHTree.FromPolygons(vs,p['fs'],all_triangles=False,epsilon=0)
                crossing=tree.overlap(q['bvh'])
                if crossing:turn_hits.append({'yaw_degrees':360*step/48,'chair_part':an,'fixed_part':bn,'triangle_surface_pairs':len(crossing)})
actual_bounds=[[min(v[k] for v in points) for k in range(3)],[max(v[k] for v in points) for k in range(3)]]
out={'source_file':str(SOURCE),'source_sha256':hashlib.sha256(SOURCE.read_bytes()).hexdigest(),'canonical_layout_sha256':hashlib.sha256(LAYOUT.read_bytes()).hexdigest(),
     'preflight_file':str(PREFLIGHT),'preflight_sha256':hashlib.sha256(PREFLIGHT.read_bytes()).hexdigest(),
     'chair_layout_id':spec['id'],'one_task_chair':len(chairs)==1,'actual_proxy_world_bounds_blender_m':actual_bounds,
     'actual_proxy_floor_contact_error_m':actual_bounds[0][2]-layout['room_floor_z_m'],
     'method':'Final native evaluated chair mesh. Exact complete swept bounds followed by33 translation samples for remaining candidates along source-authority waypoints, including45cm pullback. Full yaw bound uses the larger of actual vertex radius and published max-arm circumscribed radius;49 yaw samples only for remaining candidates. No scene/model poses saved.',
     'translations':translation_results,
     'full_turn':{'center_blender_m':list(turn),'actual_vertex_support_radius_m':actual_radius,'conservative_support_radius_m':radius,
                  'whole_turn_candidates':turn_candidates,'surface_intersections':turn_hits,'pass':not turn_hits},
     'all_sampled_motion_pass':all(x['pass'] for x in translation_results) and not turn_hits,
     'limits':['Modeled Aeron is a source-guided proxy; actual owned vintage, arm/cylinder/caster options and settings remain unconfirmed.',
               'Expanded-arm rectangle/room-route proof is separate; this actual-mesh proof uses displayed pose and a conservative full-turn bound.',
               'No dynamic caster orientation, human body, textile compression, or real motion/ergonomic certification.',
               'Complete disjoint swept bounds establish proxy clearance; sampled overlapping candidates cannot mathematically establish every intermediate state.']}
(QA/'owned-chair-motion.json').write_text(json.dumps(out,indent=2)+'\n')
print(json.dumps({'one_chair':out['one_task_chair'],'floor_error_m':out['actual_proxy_floor_contact_error_m'],
                  'transfer_pass':all(x['pass'] for x in translation_results),'turn_pass':out['full_turn']['pass'],
                  'hits':[x['surface_intersections'] for x in translation_results if not x['pass']]+turn_hits}))
