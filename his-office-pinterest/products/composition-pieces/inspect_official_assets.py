import bpy, json, pathlib

p = pathlib.Path('/workspace/his-office-pinterest/products/composition-pieces')
out = {}
for name in ['mosslanda', 'fado', 'persillade']:
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete(use_global=False)
    bpy.ops.import_scene.gltf(filepath=str(p / (name + '-official.glb')))
    meshes = [o for o in bpy.context.scene.objects if o.type == 'MESH']
    pts = [o.matrix_world @ __import__('mathutils').Vector(c) for o in meshes for c in o.bound_box]
    mn = [min(v[i] for v in pts) for i in range(3)]
    mx = [max(v[i] for v in pts) for i in range(3)]
    out[name] = {'importer': 'Blender glTF native Y-up converted to Blender Z-up', 'world_min_m': mn, 'world_max_m': mx, 'dimensions_m': [mx[i]-mn[i] for i in range(3)], 'materials': sorted(set(m.name for o in meshes for m in o.data.materials if m)), 'mesh_count': len(meshes), 'source_transform_preserved': True}
(p / 'official-assets-bounds.json').write_text(json.dumps(out, indent=2))
print(json.dumps(out))
