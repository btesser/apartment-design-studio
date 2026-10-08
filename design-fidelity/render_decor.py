import bpy,math
from mathutils import Vector
bpy.ops.wm.open_mainfile(filepath='/workspace/design-fidelity/decor-smoke.blend')
s=bpy.context.scene;s.world=bpy.data.worlds.new('PreviewWorld');s.render.engine='CYCLES';s.cycles.samples=16;s.cycles.use_denoising=False;s.render.resolution_x=1400;s.render.resolution_y=500;s.render.resolution_percentage=100;s.world.color=(.42,.42,.42);s.view_settings.view_transform='AgX'
bpy.ops.object.camera_add(location=(2.22,7,3.2));cam=bpy.context.object;cam.rotation_euler=(Vector((2.22,0,.65))-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.type='ORTHO';cam.data.ortho_scale=5.7;s.camera=cam
bpy.ops.object.light_add(type='AREA',location=(2.2,4.0,5));l=bpy.context.object;l.data.energy=1200;l.data.shape='DISK';l.data.size=5;l.rotation_euler=(Vector((2.2,0,.5))-l.location).to_track_quat('-Z','Y').to_euler()
bpy.ops.mesh.primitive_plane_add(size=200,location=(0,0,-.003));o=bpy.context.object;m=bpy.data.materials.new('Preview ground');m.diffuse_color=(.8,.78,.71,1);o.data.materials.append(m)
s.render.filepath='/workspace/design-fidelity/decor-preview.jpg';s.render.image_settings.file_format='JPEG';bpy.ops.render.render(write_still=True)
