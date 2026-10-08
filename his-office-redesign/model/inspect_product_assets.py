import bpy
import json
from pathlib import Path
from mathutils import Vector
ROOT = Path('/workspace/his-office-redesign/model')
BASE = Path('/workspace/his-office-redesign/products/candidates/official-3d-assets')
out = {}
for name in ('alex-drawers', 'storklinta-low-drawers'):
    bpy.ops.wm.read_factory_settings(use_empty=True)
    bpy.ops.import_scene.gltf(filepath=str(BASE / (name + '.glb')))
    bpy.context.view_layer.update()
    p = [o.matrix_world @ Vector(c) for o in bpy.data.objects if o.type == 'MESH' for c in o.bound_box]
    lo = [min(q[i] for q in p) for i in range(3)]
    hi = [max(q[i] for q in p) for i in range(3)]
    out[name] = {'native_blender_bounds': [lo, hi], 'dimensions_m': [hi[i] - lo[i] for i in range(3)],
                 'objects': [{'name': o.name, 'world_center': list(o.matrix_world.translation),
                              'dimensions': list(o.dimensions), 'materials': [m.name for m in o.data.materials]}
                             for o in bpy.data.objects if o.type == 'MESH']}
(ROOT / 'official-asset-bounds.json').write_text(json.dumps(out, indent=2))
print(json.dumps({k: {x: v[x] for x in ('native_blender_bounds','dimensions_m')} for k,v in out.items()}, indent=2))
