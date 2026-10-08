import bpy,json
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
s=bpy.context.scene;s.render.engine='CYCLES';s.cycles.samples=8;s.cycles.use_denoising=False;s.render.resolution_x=1600;s.render.resolution_y=1500;s.view_settings.view_transform='Standard';s.world.color=(.8,.8,.8)
bpy.ops.object.camera_add();cam=bpy.context.object;s.camera=cam;cam.data.type='ORTHO';poses=[]
for id,eye,target,scale in [('rear-door-window',(-6,-1.24,3.05),(-8.5,-1.24,3.05),3.50),('closet-entry',(-6,-1.24,3.05),(-2.7,-1.24,3.05),3.50),('white-wall',(-5.55,-1.8,3.05),(-5.55,.5,3.05),5.40),('brick-wall',(-5.55,-.7,3.05),(-5.55,-3.5,3.05),5.40)]:
 s.render.resolution_y=1500 if scale<4 else 900
 cam.location=eye;cam.rotation_euler=(Vector(target)-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.ortho_scale=scale;s.render.filepath='/workspace/his-office-redesign/geometry/raw-'+id+'.png';bpy.ops.render.render(write_still=True)
 poses.append(dict(id=id,eye=eye,target=target,ortho_width_m=scale,image_width_px=1600,image_height_px=s.render.resolution_y))
json.dump(poses,open('/workspace/his-office-redesign/geometry/raw-camera-poses.json','w'),indent=2)
