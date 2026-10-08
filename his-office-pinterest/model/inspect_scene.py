"""Read-only inventory; source is opened but never saved."""
import bpy
import json
import sys
from pathlib import Path
ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))
from scene_tools import (read_source, SOURCE, SOURCE_HASH, canonical_id,
                         descendants, bounds, protected_signatures, write_json)

read_source()
roots = []
equipment = []
for obj in bpy.data.objects:
    if obj.type != 'EMPTY':
        continue
    ident = canonical_id(obj)
    if ident:
        members = descendants(obj)
        roots.append({'id': ident, 'name': obj.name, 'position_blender_m': list(obj.location),
                      'rotation_z_deg': __import__('math').degrees(obj.rotation_euler.z),
                      'scale': list(obj.scale), 'children_meshes': sum(o.type == 'MESH' for o in members),
                      'world_bounds_m': bounds(members),
                      'materials': sorted({m.name for o in members if o.type == 'MESH'
                                           for m in o.data.materials if m}),
                      'collections': [c.name for c in obj.users_collection]})
    elif obj.get('assumption'):
        equipment.append({'name': obj.name, 'position_blender_m': list(obj.location),
                          'assumption': obj['assumption'], 'meshes': len(obj.children_recursive)})
mats = []
for m in bpy.data.materials:
    users = [o.name for o in bpy.data.objects if o.type == 'MESH' and m in list(o.data.materials)]
    if not users:
        continue
    p = m.node_tree.nodes.get('Principled BSDF') if m.use_nodes else None
    values = {}
    if p:
        for name in ['Base Color', 'Metallic', 'Roughness', 'Transmission Weight', 'Emission Strength']:
            value = p.inputs[name].default_value
            values[name] = list(value) if hasattr(value, '__len__') else value
    mats.append({'name': m.name, 'users': users, 'principled_defaults': values,
                 'images': [{'node': n.name, 'image': n.image.name, 'size': list(n.image.size),
                             'packed': n.image.packed_file is not None}
                            for n in m.node_tree.nodes if n.type == 'TEX_IMAGE' and n.image]
                 if m.use_nodes else []})
lights = [{'name': o.name, 'position_blender_m': list(o.location), 'type': o.data.type,
           'energy': o.data.energy, 'color': list(o.data.color)}
          for o in bpy.data.objects if o.type == 'LIGHT']
cameras = [{'name': o.name, 'position_blender_m': list(o.location),
            'rotation_euler_rad': list(o.rotation_euler), 'lens_mm': o.data.lens,
            'sensor_width_mm': o.data.sensor_width} for o in bpy.data.objects if o.type == 'CAMERA']
s = bpy.context.scene
report = {'source': str(SOURCE), 'source_sha256': SOURCE_HASH,
          'coordinate_frame': 'Blender Z-up metres; glTF (X,Z,-Y); no recenter/scale/mirror',
          'collections': [{'name': c.name, 'direct_objects': len(c.objects),
                           'all_meshes': sum(o.type == 'MESH' for o in c.all_objects)}
                          for c in bpy.data.collections],
          'product_roots': sorted(roots, key=lambda x: x['id']),
          'standalone_equipment_roots': equipment, 'materials': mats,
          'lights': lights, 'cameras': cameras,
          'render': {'engine': s.render.engine, 'resolution': [s.render.resolution_x, s.render.resolution_y],
                     'samples': s.cycles.samples, 'adaptive_threshold': s.cycles.adaptive_threshold,
                     'denoising': s.cycles.use_denoising, 'exposure': s.view_settings.exposure,
                     'view_transform': s.view_settings.view_transform, 'look': s.view_settings.look}}
write_json('scene-inventory.json', report)
write_json('protected-geometry.json', protected_signatures())
print('READ_ONLY_INVENTORY_READY', len(roots), len(mats), len(lights), len(cameras))
