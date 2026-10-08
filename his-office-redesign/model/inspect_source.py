"""Read native scene inventory without changing or saving the source apartment."""
import bpy
import json
from pathlib import Path
from mathutils import Vector

ROOT = Path('/workspace/his-office-redesign/model')
SOURCE = Path('/workspace/apartment-model/integrated.blend')
ROOT.mkdir(parents=True, exist_ok=True)
bpy.ops.wm.open_mainfile(filepath=str(SOURCE))
s = bpy.context.scene
records = []
for o in sorted(bpy.data.objects, key=lambda ob: ob.name):
    bounds = None
    if o.type == 'MESH':
        p = [o.matrix_world @ Vector(c) for c in o.bound_box]
        bounds = [[min(q[i] for q in p) for i in range(3)],
                  [max(q[i] for q in p) for i in range(3)]]
    record = {
        'name': o.name, 'type': o.type,
        'collections': [c.name for c in o.users_collection],
        'parent': o.parent.name if o.parent else None,
        'location': list(o.location), 'rotation_euler': list(o.rotation_euler),
        'world_bbox_m': bounds, 'dimensions_m': list(o.dimensions),
        'vertices': len(o.data.vertices) if o.type == 'MESH' else None,
        'materials': [m.name if m else None for m in o.data.materials] if o.type == 'MESH' else [],
        'hide_render': o.hide_render, 'hide_viewport': o.hide_viewport,
        'custom_properties': {k: str(o[k]) for k in o.keys()},
    }
    records.append(record)
inventory = {
    'source': str(SOURCE), 'unit_system': s.unit_settings.system,
    'scale_length': s.unit_settings.scale_length,
    'coordinate_convention': 'Original metric Blender coordinates, Z-up; GLTF maps (X,Z,-Y). No normalization.',
    'collections': [{'name': c.name, 'direct_objects': len(c.objects), 'all_objects': len(c.all_objects),
                     'hide_render': c.hide_render, 'hide_viewport': c.hide_viewport} for c in bpy.data.collections],
    'objects': records,
}
(ROOT / 'source-inventory.json').write_text(json.dumps(inventory, indent=2))
for r in records:
    p = r['world_bbox_m']
    arch_or_fix = any(c.startswith(('03 ', '05 ', '09 ')) for c in r['collections'])
    if arch_or_fix and (r['name'].startswith(('his-office', 'HIS')) or
                       (p and p[0][0] < -3.00 and p[1][0] > -8.15 and p[0][1] < .45 and p[1][1] > -2.9
                        and p[0][2] > 1.40)):
        print(json.dumps({k: r[k] for k in ('name', 'collections', 'world_bbox_m', 'vertices')}))
print('SOURCE_INSPECTION_COMPLETE', len(records))
