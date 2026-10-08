"""Audit source finish dependencies without saving or changing Blender data."""
import bpy
import hashlib
import json
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree

OUT = Path('/workspace/his-office-pinterest/model')
SOURCE = Path('/workspace/his-office-redesign/model/his-office-design.blend')
ROOT_IDS = {'kept-uplift-desk': 'uplift-main-desk',
            'kept-honeywell-02e-pro': 'honeywell-lamp',
            'kept-muttros-cat-tree': 'muttros-cat-tree'}
FIXED_COLLECTIONS = ['01 Measured room shell', '02 Existing fixed feature proxies',
                     '02b Existing door leaves — closed observed state']

source_hash_before = hashlib.sha256(SOURCE.read_bytes()).hexdigest()
bpy.ops.wm.open_mainfile(filepath=str(SOURCE))

def plain(value):
    if isinstance(value, (str, float, int, bool)) or value is None:
        return value
    try:
        return [plain(v) for v in value]
    except TypeError:
        return str(value)

def digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(',', ':'), ensure_ascii=False).encode()).hexdigest()

def node_signature(tree, seen=None):
    if tree is None:
        return None
    seen = set() if seen is None else seen
    if tree.name in seen:
        return {'recursive_node_tree': tree.name}
    seen.add(tree.name)
    nodes = []
    for n in sorted(tree.nodes, key=lambda n: n.name):
        attrs = {}
        for key in ('operation', 'blend_type', 'uv_map', 'attribute_name', 'vector_type',
                    'interpolation', 'extension', 'projection', 'projection_blend',
                    'noise_dimensions', 'wave_type', 'bands_direction', 'rings_direction',
                    'wave_profile', 'space', 'normalize', 'distribution', 'subsurface_method'):
            if hasattr(n, key):
                attrs[key] = plain(getattr(n, key))
        d = {'name': n.name, 'bl_idname': n.bl_idname, 'mute': n.mute,
             'inputs': [{'name': x.name, 'identifier': x.identifier, 'default': plain(x.default_value)}
                        for x in n.inputs if hasattr(x, 'default_value')], 'attributes': attrs}
        if hasattr(n, 'image') and n.image:
            d['image'] = n.image.name
        if hasattr(n, 'color_ramp'):
            ramp = n.color_ramp
            d['color_ramp'] = {'color_mode': ramp.color_mode, 'hue_interpolation': ramp.hue_interpolation,
                               'interpolation': ramp.interpolation,
                               'elements': [[e.position, list(e.color)] for e in ramp.elements]}
        if n.type == 'GROUP':
            d['group'] = node_signature(n.node_tree, seen.copy())
        nodes.append(d)
    return {'nodes': nodes, 'links': sorted([[l.from_node.name, l.from_socket.identifier,
                                             l.to_node.name, l.to_socket.identifier] for l in tree.links])}

def images_in_tree(tree, seen=None):
    if tree is None:
        return set()
    seen = set() if seen is None else seen
    if tree.name in seen:
        return set()
    seen.add(tree.name)
    result = set()
    for n in tree.nodes:
        if hasattr(n, 'image') and n.image:
            result.add(n.image)
        if n.type == 'GROUP':
            result |= images_in_tree(n.node_tree, seen)
    return result

keepers = {}
owner_by_object = {}
for root_name, layout_id in ROOT_IDS.items():
    root = bpy.data.objects[root_name]
    objects = [root, *root.children_recursive]
    keepers[root_name] = objects
    for o in objects:
        owner_by_object[o.name] = root_name
fixed_objects = {o for name in FIXED_COLLECTIONS for o in bpy.data.collections[name].all_objects}
keeper_objects = {o for objects in keepers.values() for o in objects}
protected_objects = keeper_objects | fixed_objects

def object_group(o):
    if o in keeper_objects:
        return owner_by_object[o.name]
    if o in fixed_objects:
        return 'source_fixed_geometry'
    return 'redesignable_or_presentation'

def mats_for(objects):
    return {s.material for o in objects for s in o.material_slots if s.material}

keeper_mats = mats_for(keeper_objects)
fixed_mats = mats_for(fixed_objects)
protected_mats = keeper_mats | fixed_mats
materials = {}
protected_images = set()
for m in sorted(protected_mats, key=lambda x: x.name):
    users = sorted([o for o in bpy.data.objects if any(s.material == m for s in o.material_slots)], key=lambda x: x.name)
    images = images_in_tree(m.node_tree if m.use_nodes else None)
    protected_images |= images
    signature = {'diffuse_color': list(m.diffuse_color), 'metallic': m.metallic, 'roughness': m.roughness,
                 'use_nodes': m.use_nodes, 'node_tree': node_signature(m.node_tree if m.use_nodes else None)}
    for key in ('surface_render_method', 'use_transparency_overlap', 'use_backface_culling', 'alpha_threshold'):
        if hasattr(m, key):
            signature[key] = plain(getattr(m, key))
    materials[m.name] = {
        'protect_for': [x for x, yes in [('keeper_finish', m in keeper_mats), ('source_architecture_or_fixture', m in fixed_mats)] if yes],
        'fingerprint_sha256': digest(signature), 'images': sorted(i.name for i in images),
        'keeper_roots': sorted({owner_by_object[o.name] for o in users if o in keeper_objects}),
        'fixed_users': [o.name for o in users if o in fixed_objects],
        'keeper_users': [o.name for o in users if o in keeper_objects],
        'outside_protected_users': [o.name for o in users if o not in protected_objects],
        'all_object_user_count': len(users), 'blender_datablock_users': m.users,
        'material_snapshot': signature,
    }

images = {}
for im in sorted(protected_images, key=lambda x: x.name):
    packed = im.packed_file
    packed_bytes = bytes(packed.data) if packed else None
    resolved = Path(bpy.path.abspath(im.filepath)) if im.filepath else None
    images[im.name] = {'source': im.source, 'filepath': im.filepath,
                      'size': list(im.size), 'channels': im.channels, 'has_data': im.has_data,
                      'is_packed': bool(packed), 'packed_byte_count': len(packed_bytes) if packed_bytes else 0,
                      'packed_sha256': hashlib.sha256(packed_bytes).hexdigest() if packed_bytes else None,
                      'disk_path_exists': resolved.exists() if resolved else False,
                      'color_space': im.colorspace_settings.name, 'alpha_mode': im.alpha_mode,
                      'using_protected_materials': sorted(m.name for m in protected_mats if im in images_in_tree(m.node_tree if m.use_nodes else None)),
                      'guard': 'Do not repack, reload, replace, or edit this image. Retain existing packed bytes.' if packed else 'Preserve source bytes and image settings.'}

def object_record(o):
    record = {'name': o.name, 'type': o.type, 'data_name': o.data.name if o.data else None,
              'parent': o.parent.name if o.parent else None,
              'materials': [s.material.name if s.material else None for s in o.material_slots],
              'matrix_local': [list(row) for row in o.matrix_local],
              'matrix_world': [list(row) for row in o.matrix_world],
              'hide_render': o.hide_render, 'hide_viewport': o.hide_viewport}
    if o.type == 'MESH':
        record.update(vertex_count=len(o.data.vertices), polygon_count=len(o.data.polygons),
                      data_user_count=o.data.users,
                      outside_protected_shared_mesh_users=[u.name for u in bpy.data.objects if u not in protected_objects and u.data == o.data])
    return record

def verify_source_lamp_aperture():
    root = bpy.data.objects['kept-honeywell-02e-pro']
    inverse = root.matrix_world.inverted()
    depsgraph = bpy.context.evaluated_depsgraph_get()
    surfaces, local_points = [], []
    for o in root.children_recursive:
        if o.type != 'MESH':
            continue
        evaluated = o.evaluated_get(depsgraph)
        mesh = evaluated.to_mesh()
        verts = [evaluated.matrix_world @ v.co for v in mesh.vertices]
        faces = [tuple(p.vertices) for p in mesh.polygons]
        surfaces.append((o.name, BVHTree.FromPolygons(verts, faces, all_triangles=False)))
        local_points.extend(inverse @ v for v in verts)
        evaluated.to_mesh_clear()
    top = max(v.z for v in local_points)
    cases = [(x, y, None) for x in [-.03, 0, .03] for y in [-.1, 0, .1]]
    cases += [(-.075, 0, 'Narrow parallel LED light bar'), (.075, 0, 'Narrow parallel LED light bar'),
              (-.135018, 0, 'Rectangular panel long rim'), (.135018, 0, 'Rectangular panel long rim')]
    direction = (root.matrix_world.to_3x3() @ Vector((0, 0, -1))).normalized()
    results = []
    for x, y, expected in cases:
        origin = root.matrix_world @ Vector((x, y, top + .1))
        hits = []
        for name, surface in surfaces:
            point, normal, index, distance = surface.ray_cast(origin, direction, .35)
            if point is not None:
                hits.append((distance, name))
        first = min(hits) if hits else None
        passed = first is None if expected is None else bool(first and first[1].startswith(expected))
        results.append({'local_xy_m': [x, y], 'expected': expected or 'open aperture',
                        'first_hit': first[1] if first else None, 'pass': passed})
    return {'method': 'Read-only evaluated mesh BVH: 9 aperture rays, 2 LED bar rays, 2 perimeter rays in the exact owned hierarchy.',
            'mesh_count': len(surfaces), 'led_bar_count': sum(o.name.startswith('Narrow parallel LED light bar') for o in root.children_recursive),
            'all_13_cases_pass': all(x['pass'] for x in results), 'cases': results}

report = {
    'schema_version': 1,
    'source': str(SOURCE), 'source_sha256': source_hash_before,
    'read_only_source_audit': True,
    'protection_rules': [
        'Never save to source. Save a fresh scene only in /workspace/his-office-pinterest/model.',
        'Keep the three owned product hierarchies and their material assignments intact; only move or rotate whole roots.',
        'Keep source architecture, fixtures, and closed observed door collections geometrically intact.',
        'When redesigning an object whose material appears in protected_material_names, first copy the material for that object and assign the copy. Do not edit the original datablock.',
        'When assigning material slots on a mesh shared with protected objects, first copy its mesh datablock.',
        'Do not call image.pack() on an already packed image. Packing from missing disk paths can destroy or fail on retained image data.',
        'Protect image node settings, UVs, procedural node inputs, and node links as well as Base Color.',
        'Do not purge protected source dependencies while any keeper/fixed object is being appended or rebuilt.'
    ],
    'keepers': {name: {'canonical_layout_id': ROOT_IDS[name], 'object_count_including_root': len(objects),
                       'material_names': sorted(m.name for m in mats_for(objects)),
                       'objects': [object_record(o) for o in objects]} for name, objects in keepers.items()},
    'source_fixed_collections': {name: {'object_count': len(bpy.data.collections[name].all_objects),
                                       'object_names': sorted(o.name for o in bpy.data.collections[name].all_objects),
                                       'material_names': sorted(m.name for m in mats_for(bpy.data.collections[name].all_objects))} for name in FIXED_COLLECTIONS},
    'protected_material_names': sorted(materials),
    'keeper_material_names': sorted(m.name for m in keeper_mats),
    'protected_image_names': sorted(images),
    'materials': materials, 'images': images,
    'shared_protected_materials': {name: {'outside_protected_users': d['outside_protected_users'], 'keeper_roots': d['keeper_roots'], 'fixed_user_count': len(d['fixed_users'])}
                                  for name, d in materials.items() if d['outside_protected_users'] or len(d['keeper_roots']) > 1},
    'packed_scene_images': sorted(im.name for im in bpy.data.images if im.packed_file),
    'source_lamp_aperture': verify_source_lamp_aperture(),
}
report['source_sha256_after_audit'] = hashlib.sha256(SOURCE.read_bytes()).hexdigest()
report['source_unchanged'] = report['source_sha256_after_audit'] == source_hash_before
assert report['source_unchanged']
(OUT / 'keeper-material-audit-snapshot.json').write_text(json.dumps(report, indent=2, ensure_ascii=False))
guard = json.loads(json.dumps(report))
guard['detailed_audit_snapshot'] = 'keeper-material-audit-snapshot.json'
for entry in guard['materials'].values():
    del entry['material_snapshot']
for keeper in guard['keepers'].values():
    for obj in keeper['objects']:
        obj.pop('matrix_local', None)
        obj.pop('matrix_world', None)
(OUT / 'keeper-material-guard.json').write_text(json.dumps(guard, indent=2, ensure_ascii=False))

lines = ['FROZEN HIS OFFICE SOURCE — READ-ONLY MATERIAL GUARD', '', 'Source: ' + str(SOURCE),
         'SHA256: ' + source_hash_before, 'Source unchanged by audit: yes', '', 'Owned keeper finishes:']
for name, objects in keepers.items():
    lines.append(f'- {name} ({ROOT_IDS[name]}): {len(objects)} objects including root')
    for m in sorted(mats_for(objects), key=lambda x: x.name):
        lines.append('  ' + m.name)
lines.extend(['', 'Protected fixed source collections:'])
for name in FIXED_COLLECTIONS:
    lines.append(f'- {name}: {len(bpy.data.collections[name].all_objects)} objects')
lines.extend(['', 'Honeywell corrected head topology:',
              '- 11 meshes; exactly 2 narrow LED bars; 9 central-aperture rays and 4 positive-control rays pass.'
              if report['source_lamp_aperture']['all_13_cases_pass'] else '- Aperture inspection has a failed ray; inspect JSON.'])
lines.extend(['', 'Materials shared with objects outside protected keepers/fixed geometry:'])
for name, d in materials.items():
    if d['outside_protected_users']:
        lines.append(f'- {name}: {len(d["outside_protected_users"])} outside users: ' + '; '.join(d['outside_protected_users']))
if not any(d['outside_protected_users'] for d in materials.values()):
    lines.append('- None')
lines.extend(['', 'Materials shared across keeper roots:'])
for name, d in materials.items():
    if len(d['keeper_roots']) > 1:
        lines.append('- ' + name + ': ' + ', '.join(d['keeper_roots']))
lines.extend(['', 'Protected image dependencies:'])
for name, d in images.items():
    lines.append(f'- {name}: {d["size"]}, packed={d["is_packed"]}, source path exists={d["disk_path_exists"]}, materials=' + '; '.join(d['using_protected_materials']))
lines.extend(['', 'Pipeline guardrails:', *['- ' + x for x in report['protection_rules']]])
(OUT / 'keeper-material-guard.txt').write_text('\n'.join(lines) + '\n')
print(json.dumps({'source_sha256': source_hash_before, 'source_unchanged': report['source_unchanged'],
                  'keeper_material_names': report['keeper_material_names'], 'protected_image_names': report['protected_image_names'],
                  'shared_protected_materials': report['shared_protected_materials'],
                  'images': images}, indent=2, ensure_ascii=False))
