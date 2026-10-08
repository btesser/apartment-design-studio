"""Read and revise the frozen metric room without writing to prior deliveries."""
import bpy
import hashlib
import json
import math
from array import array
from pathlib import Path
from mathutils import Vector

ROOT = Path(__file__).resolve().parent
SOURCE = Path('/workspace/his-office-redesign/model/his-office-design.blend')
SOURCE_HASH = '607e11d67b8fc8813da0872b5f18278733c6a40cd9e1988c3b1cb743971ada0a'
KEEPER_IDS = {'uplift-main-desk', 'honeywell-lamp', 'muttros-cat-tree'}
STRUCTURE_COLLECTIONS = {
    '01 Measured room shell', '02 Existing fixed feature proxies',
    '02b Existing door leaves — closed observed state',
}


def file_hash(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def read_source():
    if file_hash(SOURCE) != SOURCE_HASH:
        raise RuntimeError('Frozen source hash differs from the audited source.')
    bpy.ops.wm.open_mainfile(filepath=str(SOURCE))
    bpy.context.view_layer.update()


def canonical_id(obj):
    return obj.get('canonical_layout_id') or obj.get('id')


def resolve_root(identifier):
    matches = [o for o in bpy.data.objects if o.type == 'EMPTY' and canonical_id(o) == identifier]
    if len(matches) != 1:
        raise ValueError(f'Expected one product root for {identifier!r}; found {len(matches)}')
    return matches[0]


def descendants(root):
    return [root, *list(root.children_recursive)]


def bounds(objects):
    points = [o.matrix_world @ Vector(c) for o in objects if o.type == 'MESH' for c in o.bound_box]
    if not points:
        return None
    return [[min(p[k] for p in points) for k in range(3)],
            [max(p[k] for p in points) for k in range(3)]]


def geometry_digest(obj, matrix):
    """Raw geometry, UVs, local/world transform and geometry modifiers only."""
    h = hashlib.sha256()
    coordinates = array('f', [0]) * (len(obj.data.vertices) * 3)
    obj.data.vertices.foreach_get('co', coordinates)
    h.update(coordinates.tobytes())
    indices = array('i', [0]) * len(obj.data.loops)
    obj.data.loops.foreach_get('vertex_index', indices)
    h.update(indices.tobytes())
    starts = array('i', [0]) * len(obj.data.polygons)
    lengths = array('i', [0]) * len(obj.data.polygons)
    obj.data.polygons.foreach_get('loop_start', starts)
    obj.data.polygons.foreach_get('loop_total', lengths)
    h.update(starts.tobytes()); h.update(lengths.tobytes())
    for uv in obj.data.uv_layers:
        coordinates_uv = array('f', [0]) * (len(uv.data) * 2)
        uv.data.foreach_get('uv', coordinates_uv)
        h.update(uv.name.encode()); h.update(coordinates_uv.tobytes())
    h.update(json.dumps([round(v, 10) for row in matrix for v in row]).encode())
    mods = []
    for mod in obj.modifiers:
        value = {'name': mod.name, 'type': mod.type,
                 'render': mod.show_render, 'viewport': mod.show_viewport}
        if mod.type == 'BEVEL':
            value.update(width=mod.width, segments=mod.segments, affect=mod.affect)
        mods.append(value)
    h.update(json.dumps(mods, sort_keys=True).encode())
    return h.hexdigest()


def material_digest(material):
    payload = {'name': material.name, 'nodes': [], 'links': []}
    if material.use_nodes:
        for node in material.node_tree.nodes:
            row = {'name': node.name, 'type': node.type, 'inputs': {}}
            for socket in node.inputs:
                if not hasattr(socket, 'default_value'):
                    continue
                value = socket.default_value
                if isinstance(value, (str, bool, int, float)):
                    row['inputs'][socket.identifier] = value
                elif hasattr(value, '__len__'):
                    row['inputs'][socket.identifier] = list(value)
            for attr in ['blend_type', 'data_type', 'extension', 'interpolation',
                         'projection', 'noise_dimensions', 'wave_type',
                         'bands_direction', 'wave_profile']:
                if hasattr(node, attr):
                    row[attr] = getattr(node, attr)
            if node.type == 'TEX_IMAGE' and node.image:
                im = node.image
                row['image'] = {'name': im.name, 'size': list(im.size),
                                'colorspace': im.colorspace_settings.name,
                                'packed_sha256': hashlib.sha256(im.packed_file.data).hexdigest()
                                if im.packed_file else None}
            payload['nodes'].append(row)
        payload['links'] = sorted((l.from_node.name, l.from_socket.identifier,
                                   l.to_node.name, l.to_socket.identifier)
                                  for l in material.node_tree.links)
    return hashlib.sha256(json.dumps(payload, sort_keys=True).encode()).hexdigest()


def protected_signatures():
    structure = {}
    for name in STRUCTURE_COLLECTIONS:
        for obj in bpy.data.collections[name].all_objects:
            if obj.type == 'MESH':
                structure[obj.name] = geometry_digest(obj, obj.matrix_world)
    keepers = {}
    for ident in KEEPER_IDS:
        root = resolve_root(ident)
        components = {}
        finishes = {}
        for obj in descendants(root):
            if obj.type != 'MESH':
                continue
            # Child basis transforms remain invariant when the whole keeper is
            # moved or rotated. Product scale and dimensions are never adjusted.
            components[obj.name] = geometry_digest(obj, obj.matrix_basis)
            finishes[obj.name] = [material_digest(m) if m else None for m in obj.data.materials]
        keepers[ident] = {'root_scale': list(root.scale), 'components': components,
                         'material_assignments_and_shaders': finishes}
    return {'structure_world_geometry': structure, 'keeper_product_geometry': keepers}


def assert_protected(before):
    after = protected_signatures()
    if after != before:
        raise RuntimeError('Protected room geometry or owned keeper form was changed.')
    if file_hash(SOURCE) != SOURCE_HASH:
        raise RuntimeError('Prior source file was modified.')


def active_image_checks():
    mats = {m for o in bpy.data.objects if o.type == 'MESH' for m in o.data.materials if m}
    images = {n.image for m in mats if m.use_nodes for n in m.node_tree.nodes
              if n.type == 'TEX_IMAGE' and n.image}
    results = []
    for image in images:
        # Repacking an already packed GLB image with an empty original filepath
        # can destroy its embedded bytes in this Blender build.
        if not image.packed_file and image.filepath:
            image.pack()
        valid = min(image.size) > 0 and image.packed_file is not None
        results.append({'name': image.name, 'pixels': list(image.size),
                        'packed_bytes': len(image.packed_file.data) if image.packed_file else 0,
                        'valid': valid})
        if not valid:
            raise RuntimeError(f'Active image has no loaded/packed pixels: {image.name}')
    return results


def write_json(filename, payload):
    path = ROOT / filename
    path.write_text(json.dumps(payload, indent=2))
    return path


def delete_tree(root):
    for obj in reversed(descendants(root)):
        bpy.data.objects.remove(obj, do_unlink=True)


def export_selected(filepath, objects):
    bpy.ops.object.select_all(action='DESELECT')
    for obj in objects:
        if obj.type in {'MESH', 'EMPTY'}:
            obj.hide_set(False)
            obj.select_set(True)
    bpy.ops.export_scene.gltf(filepath=str(filepath), export_format='GLB',
                             use_selection=True, export_yup=True, export_apply=True,
                             export_extras=True, export_cameras=False, export_lights=False,
                             export_image_format='JPEG', export_jpeg_quality=95)
