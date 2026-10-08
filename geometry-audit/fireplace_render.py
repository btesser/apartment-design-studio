import bpy
from mathutils import Vector
bpy.ops.wm.open_mainfile(filepath='/workspace/apartment/scan.blend')
for o in list(bpy.data.objects):
 if o.type!='MESH' or not o.name.startswith('Mesh_'):bpy.data.objects.remove(o,do_unlink=True)
 else:o.hide_render=int(o.name.split('_')[1])<11
for m in bpy.data.materials:
 if m.use_nodes:
  ns=m.node_tree.nodes;tex=next((n for n in ns if n.type=='TEX_IMAGE'),None);out=next((n for n in ns if n.type=='OUTPUT_MATERIAL'),None)
  if tex and out:
   em=ns.new('ShaderNodeEmission');m.node_tree.links.new(tex.outputs['Color'],em.inputs['Color']);m.node_tree.links.new(em.outputs[0],out.inputs['Surface'])
s=bpy.context.scene;s.render.engine='CYCLES';s.cycles.samples=8;s.cycles.use_denoising=False;s.render.resolution_x=1600;s.render.resolution_y=900;s.view_settings.view_transform='Standard';s.world.color=(.8,.8,.8)
bpy.ops.object.camera_add();cam=bpy.context.object;s.camera=cam;cam.data.type='ORTHO'
for room,x,y,scale in [('his',-5.55,-.7,5.4),('her',5.85,.0,4.9)]:
 cam.location=(x,y,3.05);target=Vector((x,-3.5,3.05));cam.rotation_euler=(target-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.ortho_scale=scale;s.render.filepath='/workspace/geometry-audit/'+room+'-brick-wall-ortho.png';bpy.ops.render.render(write_still=True)
