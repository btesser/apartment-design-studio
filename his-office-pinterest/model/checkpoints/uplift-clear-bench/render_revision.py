"""Render the chosen new revision only; cannot open or save the prior model."""
import argparse
import bpy
import json
import math
import sys
from pathlib import Path
from mathutils import Vector
ROOT = Path(__file__).resolve().parent
parser = argparse.ArgumentParser()
parser.add_argument('--preview', action='store_true')
parser.add_argument('--views', nargs='+', default=['room-a','room-b','room-c','room-d'])
args = parser.parse_args(sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else [])
scene_file = ROOT / 'his-office-pinterest-design.blend'
if not scene_file.exists():
    raise RuntimeError('Chosen revision has not been built; layout/product decisions are pending.')
bpy.ops.wm.open_mainfile(filepath=str(scene_file)); s = bpy.context.scene
directory = ROOT / ('previews' if args.preview else 'renders'); directory.mkdir(exist_ok=True)
if args.preview:
    s.render.resolution_x = 1000; s.render.resolution_y = 694; s.cycles.samples = 24
poses = []
for name in args.views:
    cam = bpy.data.objects['CAM ' + name]; s.camera = cam
    forward = cam.matrix_world.to_quaternion() @ Vector((0,0,-1))
    target = cam.location + forward
    filename = name + '.jpg'; s.render.filepath = str(directory / filename)
    bpy.ops.render.render(write_still=True)
    poses.append({'id': name, 'filename': str(directory.relative_to(ROOT) / filename),
                  'eye_blender_m': list(cam.location), 'look_direction_blender': list(forward),
                  'eye_gltf_m': [cam.location.x,cam.location.z,-cam.location.y],
                  'target_gltf_m': [target.x,target.z,-target.y],
                  'lens_mm': cam.data.lens, 'sensor_width_mm': cam.data.sensor_width,
                  'horizontal_FOV_deg': math.degrees(2*math.atan(cam.data.sensor_width/(2*cam.data.lens))),
                  'pixels': [s.render.resolution_x,s.render.resolution_y],
                  'unit': 'metres; native Blender Z-up; glTF X,Z,-Y'})
    (ROOT / ('preview-camera-poses.json' if args.preview else 'camera-poses.json')).write_text(json.dumps(poses,indent=2))
    print('VIEW_DONE',name,flush=True)
