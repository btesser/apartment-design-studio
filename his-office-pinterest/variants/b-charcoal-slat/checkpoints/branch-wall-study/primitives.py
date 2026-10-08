"""Reusable native-meter primitives for dimensioned product proxies.

Functions create geometry only when called by a chosen-layout build script.
Products must carry verified/estimated external dimensions and their source URL.
No prior Amy scene or furnishings are imported here.
"""
import math
import bpy
from mathutils import Vector


def material(name, color, roughness=.55, metallic=0):
    m = bpy.data.materials.get(name) or bpy.data.materials.new(name)
    m.diffuse_color = (*color[:3], 1)
    m.use_nodes = True
    p = m.node_tree.nodes.get('Principled BSDF')
    p.inputs['Base Color'].default_value = (*color[:3], 1)
    p.inputs['Roughness'].default_value = roughness
    p.inputs['Metallic'].default_value = metallic
    return m


def link_object(o, collection, name, mat=None, parent=None):
    o.name = name
    for c in list(o.users_collection):
        c.objects.unlink(o)
    collection.objects.link(o)
    if mat is not None:
        o.data.materials.append(mat)
    if parent is not None:
        o.parent = parent
    return o


def product_root(spec, collection):
    """World placement uses meters; child geometry uses product-local meters."""
    o = bpy.data.objects.new(spec['id'], None)
    collection.objects.link(o)
    o.location = spec['position_blender_m']
    o.rotation_euler.z = math.radians(spec.get('rotation_z_deg', 0))
    for key in ('product_name', 'product_url', 'dimension_confidence', 'dimension_source'):
        if key in spec:
            o[key] = str(spec[key])
    o['external_dimensions_m'] = spec['external_dimensions_m']
    o['proxy_form'] = 'Dimensioned review proxy, not vendor CAD'
    return o


def box(name, location, dimensions, mat, collection, parent=None, bevel=0):
    if any(v <= 0 for v in dimensions):
        raise ValueError(f'{name}: dimensions must all be positive')
    bpy.ops.mesh.primitive_cube_add(size=1, location=location)
    o = link_object(bpy.context.object, collection, name, mat, parent)
    o.dimensions = dimensions
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    if bevel:
        mod = o.modifiers.new('Product edge softness', 'BEVEL')
        mod.width = min(bevel, min(dimensions) * .45)
        mod.segments = 3
    return o


def cylinder(name, location, radius, height, mat, collection, parent=None, vertices=48):
    if radius <= 0 or height <= 0:
        raise ValueError(f'{name}: radius and height must be positive')
    bpy.ops.mesh.primitive_cylinder_add(vertices=vertices, radius=radius, depth=height, location=location)
    return link_object(bpy.context.object, collection, name, mat, parent)


def ellipsoid(name, location, radii, mat, collection, parent=None):
    bpy.ops.mesh.primitive_uv_sphere_add(segments=32, ring_count=16, radius=1, location=location)
    o = link_object(bpy.context.object, collection, name, mat, parent)
    o.scale = radii
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    for p in o.data.polygons:
        p.use_smooth = True
    return o


def rod(name, a, b, radius, mat, collection, parent=None, vertices=32):
    """Can build lamp stems or measured cat-tree branch spans in local coordinates."""
    va, vb = Vector(a), Vector(b)
    delta = vb - va
    if delta.length < .0001:
        raise ValueError(f'{name}: rod endpoints coincide')
    o = cylinder(name, (va + vb) / 2, radius, delta.length, mat, collection, parent, vertices)
    o.rotation_euler = delta.to_track_quat('Z', 'Y').to_euler()
    return o


def bounds_world(objects):
    p = [o.matrix_world @ Vector(c) for o in objects if o.type == 'MESH' for c in o.bound_box]
    if not p:
        return None
    return [[min(q[i] for q in p) for i in range(3)], [max(q[i] for q in p) for i in range(3)]]


def export_glb(filepath, collections):
    """Apply modifiers so GLB and Blender product envelopes agree."""
    bpy.ops.object.select_all(action='DESELECT')
    for c in collections:
        c.hide_viewport = False
        for o in c.all_objects:
            if o.type in ('MESH', 'EMPTY'):
                o.hide_set(False)
                o.select_set(True)
    bpy.ops.export_scene.gltf(filepath=str(filepath), export_format='GLB', use_selection=True,
                              export_yup=True, export_apply=True, export_extras=True,
                              export_image_format='JPEG', export_jpeg_quality=95,
                              export_cameras=False, export_lights=False)
