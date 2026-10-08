import bpy
from mathutils import Vector
bpy.ops.wm.open_mainfile(filepath='/workspace/his-office-redesign/model/keepers-and-taskchairs.blend')
s=bpy.context.scene
for o in s.objects:
 if o.type=='MESH' and o.parent and o.parent.name!='kept-honeywell-02e-pro':o.hide_render=True
s.render.engine='CYCLES';s.cycles.samples=24;s.cycles.use_denoising=False
s.render.resolution_x=750;s.render.resolution_y=550;s.render.resolution_percentage=100
s.world=bpy.data.worlds.new('Lamp head proof world');s.world.use_nodes=True
s.world.node_tree.nodes['Background'].inputs[0].default_value=(.25,.32,.39,1);s.world.node_tree.nodes['Background'].inputs[1].default_value=.55
d=bpy.data.lights.new('Head proof soft fill','AREA');d.energy=75;d.size=1
o=bpy.data.objects.new('Head proof soft fill',d);s.collection.objects.link(o);o.location=(-6.7,-1.0,4.6)
o.rotation_euler=(Vector((-7.67,-.24,3.35))-o.location).to_track_quat('-Z','Y').to_euler()
d=bpy.data.cameras.new('Head proof camera');o=bpy.data.objects.new('Head proof camera',d);s.collection.objects.link(o)
o.location=(-6.9,-1.25,3.06);o.rotation_euler=(Vector((-7.67,-.24,3.40))-o.location).to_track_quat('-Z','Y').to_euler()
d.type='ORTHO';d.ortho_scale=1.10;s.camera=o
s.render.image_settings.file_format='JPEG';s.render.image_settings.quality=95;s.render.filepath='/workspace/his-office-redesign/model/honeywell-open-head-proof.jpg'
bpy.ops.render.render(write_still=True)
