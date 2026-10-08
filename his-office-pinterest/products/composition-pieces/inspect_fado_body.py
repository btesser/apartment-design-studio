import bpy, bmesh, pathlib, json
from collections import defaultdict

p = pathlib.Path('/workspace/his-office-pinterest/products/composition-pieces')
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)
bpy.ops.import_scene.gltf(filepath=str(p / 'fado-official.glb'))
out = []
for obj in [o for o in bpy.context.scene.objects if o.type == 'MESH']:
    bm = bmesh.new()
    bm.from_mesh(obj.data)
    bmesh.ops.remove_doubles(bm, verts=list(bm.verts), dist=0.00001)
    bm.verts.ensure_lookup_table()
    seen = set()
    for vert in bm.verts:
        if vert in seen:
            continue
        queue = [vert]
        component = []
        seen.add(vert)
        while queue:
            v = queue.pop()
            component.append(v)
            for edge in v.link_edges:
                n = edge.other_vert(v)
                if n not in seen:
                    seen.add(n)
                    queue.append(n)
        coords = [obj.matrix_world @ v.co for v in component]
        low = [min(v[i] for v in coords) for i in range(3)]
        high = [max(v[i] for v in coords) for i in range(3)]
        out.append({'vertices': len(component), 'world_min_m': low, 'world_max_m': high, 'dimensions_m': [high[i]-low[i] for i in range(3)]})
    bm.free()
out.sort(key=lambda v: v['vertices'], reverse=True)
(p / 'fado-source-components.json').write_text(json.dumps({'method': 'Original CAD imported to Blender Z-up, in-memory weld only for connected-component measurement; original bytes unchanged.', 'components': out}, indent=2))
print(json.dumps(out[:20]))
