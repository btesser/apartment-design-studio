import bpy, math
from mathutils import Vector
bpy.ops.wm.open_mainfile(filepath='/workspace/apartment/scan.blend')
for o in list(bpy.data.objects):
 if not o.name.startswith('Mesh_'): bpy.data.objects.remove(o,do_unlink=True)
for m in bpy.data.materials:
 if m.use_nodes:
  ns=m.node_tree.nodes; tex=next((n for n in ns if n.type=='TEX_IMAGE'),None)
  out=next((n for n in ns if n.type=='OUTPUT_MATERIAL'),None)
  if tex and out:
   em=ns.new('ShaderNodeEmission');m.node_tree.links.new(tex.outputs['Color'],em.inputs['Color']);m.node_tree.links.new(em.outputs[0],out.inputs['Surface'])
s=bpy.context.scene;s.render.engine='CYCLES';s.cycles.use_denoising=False;s.cycles.samples=8;s.render.resolution_x=1600;s.render.resolution_y=650;s.render.resolution_percentage=100
s.world.color=(.8,.8,.8);s.view_settings.view_transform='Standard'
bpy.ops.object.camera_add();cam=bpy.context.object;s.camera=cam;cam.data.type='PERSP';cam.data.lens=18
s.render.resolution_x=1200;s.render.resolution_y=900
views=[('living-room',(2,-1.9,3.05),(-2,0,2.8),1),('his-office',(-3.4,-1.5,3.05),(-7,0,2.8),1),('her-office',(4,-1.5,3.05),(7,0,2.8),1),('entryway',(1.9,.8,3.05),(3.8,2,2.8),1),('basement-living',(0,-1.8,-.05),(5,0,-.3),0),('bedroom',(-.8,-1.7,-.05),(-3,0,-.3),0),('music-room',(-5,-1.8,-.05),(-7,0,-.3),0)]
for name,pos,target,floor in views:
 for o in bpy.data.objects:
  if o.type=='MESH': o.hide_render=(int(o.name.split('_')[1])<11)!=(floor==0)
 cam.location=pos;cam.rotation_euler=(Vector(target)-cam.location).to_track_quat('-Z','Y').to_euler()
 s.render.filepath='/workspace/apartment/'+name+'.png';bpy.ops.render.render(write_still=True)
