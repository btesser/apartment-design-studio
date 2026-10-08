import bpy
bpy.ops.wm.open_mainfile(filepath='/workspace/apartment-model/scene-base.blend')
s=bpy.context.scene;s.render.engine='BLENDER_EEVEE_NEXT';s.render.resolution_x=1000;s.render.resolution_y=700
for c in bpy.data.collections:
 if c.name.startswith('01') or c.name.startswith('02'):c.hide_render=True;c.hide_viewport=True
 if c.name.startswith('03') or c.name.startswith('05'):c.hide_render=False;c.hide_viewport=False
s.camera=bpy.data.objects['CAM living-view-a'];s.render.filepath='/workspace/apartment-model/eevee-preview.png';s.render.image_settings.file_format='PNG';bpy.ops.render.render(write_still=True)
