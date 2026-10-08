import argparse
import bpy
from pathlib import Path

ROOT = Path('/workspace/his-office-redesign/model')
bpy.ops.wm.open_mainfile(filepath=str(ROOT / 'his-office-design.blend'))
parser = argparse.ArgumentParser()
parser.add_argument('--preview', action='store_true')
parser.add_argument('--views', nargs='+', default=['room-a', 'room-b', 'room-c', 'room-d'])
args = parser.parse_args(__import__('sys').argv[__import__('sys').argv.index('--')+1:] if '--' in __import__('sys').argv else [])
s = bpy.context.scene
out = ROOT / ('previews' if args.preview else 'renders')
out.mkdir(exist_ok=True)
if args.preview:
    s.render.resolution_x = 1000
    s.render.resolution_y = 694
    s.cycles.samples = 24
s.cycles.use_denoising = False
for name in args.views:
    s.camera = bpy.data.objects['CAM ' + name]
    s.render.filepath = str(out / (name + '.jpg'))
    bpy.ops.render.render(write_still=True)
    print('VIEW_DONE', name, flush=True)
print('DESIGN_RENDER_DONE', flush=True)
