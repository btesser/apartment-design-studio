import bpy,math,sys
from mathutils import Vector
bpy.ops.wm.open_mainfile(filepath='/workspace/his-office-redesign/model/keepers-and-taskchairs.blend')
sc=bpy.context.scene;sc.render.engine='CYCLES';sc.cycles.samples=16;sc.cycles.use_denoising=False;sc.render.resolution_x=1100;sc.render.resolution_y=800;sc.render.resolution_percentage=100
sc.world=bpy.data.worlds.new('Product preview world');sc.world.use_nodes=True;sc.world.node_tree.nodes['Background'].inputs[0].default_value=(.82,.84,.87,1);sc.world.node_tree.nodes['Background'].inputs[1].default_value=.55
bpy.ops.mesh.primitive_plane_add(size=200,location=(-6.8,0,1.574));o=bpy.context.object;o.name='Temporary preview floor';m=bpy.data.materials.new('Preview gray floor');m.diffuse_color=(.43,.43,.42,1);o.data.materials.append(m)
for name,loc,energy,size in [('soft key',(-4.2,-3,5.5),900,4),('rear fill',(-7.6,2,4.8),650,3)]:
 d=bpy.data.lights.new(name,'AREA');d.energy=energy;d.shape='DISK';d.size=size;o=bpy.data.objects.new(name,d);sc.collection.objects.link(o);o.location=loc;o.rotation_euler=(Vector((-6.9,-.6,2.1))-o.location).to_track_quat('-Z','Y').to_euler()
for label,pos,target in [('a',(-4.0,-5.0,4.0),(-6.55,-.6,2.5)),('b',(-4.0,2.4,3.6),(-6.55,-.6,2.5))]:
 d=bpy.data.cameras.new('Proxy review camera');o=bpy.data.objects.new('Proxy review camera',d);sc.collection.objects.link(o);o.location=pos;o.rotation_euler=(Vector(target)-o.location).to_track_quat('-Z','Y').to_euler();d.type='ORTHO';d.ortho_scale=4.25;sc.camera=o
 sc.render.filepath='/workspace/his-office-redesign/model/keepers-preview-'+label+'.jpg';sc.render.image_settings.file_format='JPEG';sc.render.image_settings.quality=92;bpy.ops.render.render(write_still=True)
