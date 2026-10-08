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
bpy.ops.object.camera_add();cam=bpy.context.object;s.camera=cam;cam.data.type='ORTHO';cam.data.ortho_scale=18
for floor,z in [(0,0.7),(1,3.8)]:
 for o in list(bpy.data.objects):
  if o.type!='MESH': continue
  idx=int(o.name.split('_')[1]);o.hide_render=(idx<11)!=(floor==0)
  if not o.hide_render:
   import bmesh
   bm=bmesh.new();bm.from_mesh(o.data);faces=[f for f in bm.faces if all((o.matrix_world@v.co).z>z for v in f.verts)];bmesh.ops.delete(bm,geom=faces,context='FACES');bm.to_mesh(o.data);bm.free()
 cam.location=(0,0,15);cam.rotation_euler=(0,0,0);s.render.filepath=f'/workspace/apartment/floor{floor}.png';bpy.ops.render.render(write_still=True)
