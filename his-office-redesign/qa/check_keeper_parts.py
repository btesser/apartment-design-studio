"""Read-only actual-component QA. Run with Blender; never saves the source model."""
import bpy
import hashlib
import itertools
import json
import sys
from pathlib import Path

from mathutils import Vector
from mathutils.bvhtree import BVHTree

ROOT = Path('/workspace/his-office-redesign')
args = sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else []
source = Path(args[0]) if args else ROOT / 'model/keepers-and-taskchairs.blend'
bpy.ops.wm.open_mainfile(filepath=str(source))
layout = json.loads((ROOT / 'model/layout.json').read_text())
specs = {i['id']: i for i in layout['items']}
expected = {
    'kept-uplift-desk': 'uplift-main-desk',
    'kept-honeywell-02e-pro': 'honeywell-lamp',
    'kept-muttros-cat-tree': 'muttros-cat-tree',
    'branch-pro-task-chair-1': 'branch-primary',
    'branch-pro-task-chair-2': 'branch-secondary'
}
deps = bpy.context.evaluated_depsgraph_get()

def owner(o):
    cur = o
    while cur:
        if cur.name in expected:
            return cur.name
        cur = cur.parent
    return None

parts = {}
for obj in bpy.data.objects:
    group = owner(obj)
    if obj.type != 'MESH' or group is None:
        continue
    ev = obj.evaluated_get(deps)
    mesh = ev.to_mesh()
    pts = [ev.matrix_world @ v.co for v in mesh.vertices]
    faces = [tuple(p.vertices) for p in mesh.polygons]
    lo = [min(v[k] for v in pts) for k in range(3)]
    hi = [max(v[k] for v in pts) for k in range(3)]
    bvh = BVHTree.FromPolygons(pts, faces, all_triangles=False, epsilon=0)
    parts[obj.name] = {'group': group, 'pts': pts, 'bounds': [lo, hi], 'bvh': bvh}
    ev.to_mesh_clear()

def broad_overlap(a, b):
    return all(a['bounds'][0][k] <= b['bounds'][1][k] and b['bounds'][0][k] <= a['bounds'][1][k] for k in range(3))

root_checks = []
for scene_id, layout_id in expected.items():
    o = bpy.data.objects.get(scene_id)
    actual = list(o.matrix_world.translation) if o else None
    target = specs[layout_id]['position_blender_m']
    delta = max(abs(a-b) for a, b in zip(actual, target)) if actual else None
    root_checks.append({'scene_root': scene_id, 'layout_id': layout_id, 'actual_position_blender_m': actual, 'canonical_position_blender_m': target, 'max_position_difference_m': delta, 'matches_canonical_within_1e_minus_5_m': delta is not None and delta < 1e-5})

tested = []
allowed_groups = [
    ('kept-uplift-desk','kept-muttros-cat-tree'),
    ('kept-uplift-desk','kept-honeywell-02e-pro'),
    ('kept-honeywell-02e-pro','kept-muttros-cat-tree'),
    ('kept-uplift-desk','branch-pro-task-chair-1'),
    ('kept-uplift-desk','branch-pro-task-chair-2'),
    ('kept-muttros-cat-tree','branch-pro-task-chair-1')
]
for ga, gb in allowed_groups:
    a = [(name, p) for name, p in parts.items() if p['group'] == ga]
    b = [(name, p) for name, p in parts.items() if p['group'] == gb]
    candidates = []
    intersections = []
    for (an, ap), (bn, bp) in itertools.product(a, b):
        if not broad_overlap(ap, bp):
            continue
        candidates.append([an, bn])
        crosses = ap['bvh'].overlap(bp['bvh'])
        if crosses:
            intersections.append({'a': an, 'b': bn, 'triangle_surface_intersection_pairs': len(crosses)})
    tested.append({'groups': [ga, gb], 'broad_phase_overlaps': candidates, 'triangle_surface_intersections': intersections})

def list_parts(group, text):
    return [{'part': name, 'bounds_blender_m': p['bounds']} for name, p in parts.items() if p['group'] == group and text.lower() in name.lower()]

out = {
    'source_file': str(source),
    'source_sha256': hashlib.sha256(source.read_bytes()).hexdigest(),
    'layout_sha256': hashlib.sha256((ROOT/'model/layout.json').read_bytes()).hexdigest(),
    'method': 'Read-only evaluated native Blender mesh bounds and pairwise world-space triangle BVH surface intersections. No source saved or placement changed.',
    'limits': ['Zero surface intersections does not independently prove absence of fully contained solids.', 'Keeper desk frame, lamp U-base and cat branch geometry are dimensioned photo-based review proxies; actual unmeasured owned components may differ.', 'Caster motion and human circulation are checked separately using conservative nominal envelopes.', 'Scene comparison tolerances refer to export/transform parity, not site measurement accuracy.'],
    'root_position_parity': root_checks,
    'canonical_position_parity_pass': all(r['matches_canonical_within_1e_minus_5_m'] for r in root_checks),
    'tested_group_pairs': tested,
    'keeper_proxy_surface_intersection_count': sum(len(p['triangle_surface_intersections']) for p in tested),
    'cat_basket_parts': list_parts('kept-muttros-cat-tree','wicker basket'),
    'lamp_base_parts': list_parts('kept-honeywell-02e-pro','U-base'),
    'lamp_stem_parts': list_parts('kept-honeywell-02e-pro','upright'),
    'uplift_foot_parts': list_parts('kept-uplift-desk','steel foot'),
    'uplift_top_parts': list_parts('kept-uplift-desk','wood barkline')
}
(ROOT/'qa/keeper-part-checks.json').write_text(json.dumps(out, indent=2)+'\n')
print(json.dumps({'source': str(source), 'root_parity': out['canonical_position_parity_pass'], 'surface_intersection_count': out['keeper_proxy_surface_intersection_count'], 'proof': str(ROOT/'qa/keeper-part-checks.json')}))
