"""Unfurnished fixed-feature check only; final design renders will use chosen layout."""
import bpy
from pathlib import Path
ROOT = Path('/workspace/his-office-redesign/model')
OUT = ROOT / 'shell-checks'
OUT.mkdir(exist_ok=True)
bpy.ops.wm.open_mainfile(filepath=str(ROOT / 'his-office-shell.blend'))
s = bpy.context.scene
s.render.resolution_x = 1000
s.render.resolution_y = 700
s.eevee.taa_render_samples = 16
s.render.image_settings.file_format = 'JPEG'
s.render.image_settings.quality = 92
for name in ('room-a', 'room-b', 'room-c', 'room-d'):
    s.camera = bpy.data.objects['CAM ' + name]
    s.render.filepath = str(OUT / (name + '.jpg'))
    bpy.ops.render.render(write_still=True)
print('SHELL_CHECK_PREVIEWS_READY')
