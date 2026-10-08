"""Create an unfurnished room-only starting scene in original metric coordinates.

This is an extraction of the old architectural proxy, pending the new raw-scan
fixed-feature audit. It is not the final redesign scene and contains no furniture.
"""
import bpy
import hashlib
import json
import math
import sys
from pathlib import Path
from mathutils import Vector

ROOT = Path('/workspace/his-office-redesign/model')
sys.path.insert(0, str(ROOT))
from primitives import export_glb

selection = json.loads((ROOT / 'source-selection.json').read_text())
source = Path(selection['source'])
source_hash = hashlib.sha256(source.read_bytes()).hexdigest()
bpy.ops.wm.read_factory_settings(use_empty=True)
s = bpy.context.scene
s.unit_settings.system = 'METRIC'
s.unit_settings.scale_length = 1

groups = {}
for key, name in (
    ('shell', '01 Measured room shell'),
    ('fixtures', '02 Existing fixed feature proxies'),
    ('backdrop', '03 Daylight backdrop — presentation only'),
    ('presentation', '04 Lights and camera templates'),
    ('proposal', '05 New proposal — pending selected layout'),
):
    c = bpy.data.collections.new(name)
    s.collection.children.link(c)
    groups[key] = c

with bpy.data.libraries.load(str(source), link=False) as (src, dst):
    missing = set(selection['objects']) - set(src.objects)
    if missing:
        raise RuntimeError(f'Source objects are missing: {missing}')
    dst.objects = selection['objects']

inventory = json.loads((ROOT / 'source-inventory.json').read_text())
reference = {r['name']: r for r in inventory['objects']}
extracted = []
for o in dst.objects:
    if o is None:
        continue
    if o.name.startswith(('his-office wall', 'architecture_')):
        group = groups['shell']
    elif o.name.startswith('Sky outside window'):
        group = groups['backdrop']
    else:
        group = groups['fixtures']
    group.objects.link(o)
    o.hide_render = False
    o.hide_viewport = False
    o['original_source_object'] = o.name
    o['original_source_file'] = str(source)
    o['room'] = 'his-office'
    o['source_geometry_modified'] = False
    bpy.context.view_layer.update()
    old = reference[o.name]
    if any(abs(a - b) > .00001 for a, b in zip(o.location, old['location'])):
        raise RuntimeError(f'Source object moved during extraction: {o.name}')
    extracted.append(o.name)

# Rendering templates carry no layout authority. Final chosen furnishing/cat-tree
# geometry will determine the clear-floor camera positions before design rendering.
floor = 1.575
poses = {
    'room-a': ((-3.46, -2.34, floor + 1.55), (-6.30, -.32, floor + 1.04)),
    'room-b': ((-7.48, -2.27, floor + 1.55), (-4.78, -.23, floor + 1.04)),
    'room-c': ((-7.42, -.07, floor + 1.55), (-4.80, -2.20, floor + 1.04)),
    'room-d': ((-4.14, -.07, floor + 1.55), (-6.55, -2.14, floor + 1.04)),
}
for name, (eye, target) in poses.items():
    data = bpy.data.cameras.new(name)
    o = bpy.data.objects.new('CAM ' + name, data)
    groups['presentation'].objects.link(o)
    o.location = eye
    o.rotation_euler = (Vector(target) - o.location).to_track_quat('-Z', 'Y').to_euler()
    data.lens = 24
    data.sensor_width = 36
    data.clip_start = .025
    data.clip_end = 80

for name, pos, energy, size in (
    ('soft ceiling fill', (-5.63, -1.19, 4.32), 230, 2.8),
    ('window daylight', (-7.75, -.47, 3.46), 260, 1.2),
):
    data = bpy.data.lights.new(name, 'AREA')
    data.energy = energy
    data.shape = 'DISK'
    data.size = size
    o = bpy.data.objects.new('LIGHT ' + name, data)
    groups['presentation'].objects.link(o)
    o.location = pos
    if name == 'window daylight':
        o.rotation_euler = (Vector((-4.20, -1.10, 2.70)) - o.location).to_track_quat('-Z', 'Y').to_euler()

s.world = bpy.data.worlds.new('Neutral daylight world')
s.world.use_nodes = True
s.world.node_tree.nodes.get('Background').inputs['Color'].default_value = (.72, .78, .85, 1)
s.world.node_tree.nodes.get('Background').inputs['Strength'].default_value = .35
s.render.engine = 'BLENDER_EEVEE_NEXT'
s.render.resolution_x = 1440
s.render.resolution_y = 1000
s.render.resolution_percentage = 100
s.eevee.taa_render_samples = 64
s.render.image_settings.file_format = 'PNG'
s.view_settings.view_transform = 'AgX'
s.view_settings.look = 'AgX - Medium High Contrast'
s.camera = bpy.data.objects['CAM room-a']
s['status'] = 'Unfurnished source extraction; radiator and closet/cupboard audit pending. Not a final design.'
s['furniture_count'] = 0
s['coordinate_units'] = 'Meters, native scan coordinate frame; Blender Z-up'

for image in bpy.data.images:
    if image.source == 'FILE':
        try:
            image.pack()
        except Exception:
            pass

export_glb(ROOT / 'unfurnished-source-shell.glb', [groups['shell'], groups['fixtures']])
bpy.ops.wm.save_as_mainfile(filepath=str(ROOT / 'unfurnished-source-shell.blend'))
if hashlib.sha256(source.read_bytes()).hexdigest() != source_hash:
    raise RuntimeError('Original apartment file changed during extraction.')
(ROOT / 'extraction-manifest.json').write_text(json.dumps({
    'source': str(source), 'source_sha256': source_hash,
    'source_unchanged': True, 'native_scale': 1,
    'coordinate_mapping': 'GLTF (X,Y,Z) = Blender (X,Z,-Y)',
    'extracted_objects': extracted, 'original_object_transforms_preserved': True,
    'old_Amy_furniture_count': 0, 'new_proposal_furniture_count': 0,
    'status': 'Starting shell, pending audited radiator and closet/cupboard corrections',
    'template_cameras': {name: {'eye_blender_m': list(eye), 'target_blender_m': list(target),
                               'lens_mm': 24, 'sensor_width_mm': 36,
                               'horizontal_FOV_deg': math.degrees(2 * math.atan(36 / 48)),
                               'is_final': False} for name, (eye, target) in poses.items()},
}, indent=2))
print('UNFURNISHED_SOURCE_SHELL_READY', len(extracted))
