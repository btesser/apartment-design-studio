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
import json,os
config=json.load(open('/workspace/apartment/multiview-config.json'))
manifest=[]
for room,c in config.items():
 x0,x1,y0,y1=c['bounds'];z=c['z'];floor=c['floor']
 points=[(x0,y0),(x1,y0),(x1,y1),(x0,y1)]
 os.makedirs('/workspace/apartment-design/multiple-angles/'+room,exist_ok=True)
 for i,(x,y) in enumerate(points):
  tx,ty=points[(i+2)%4]
  for o in bpy.data.objects:
   if o.type=='MESH':o.hide_render=(int(o.name.split('_')[1])<11)!=(floor==0)
  cam.location=(x,y,z);target=Vector((tx,ty,z-.2));cam.rotation_euler=(target-cam.location).to_track_quat('-Z','Y').to_euler()
  cam.data.lens=20
  path='/workspace/apartment-design/multiple-angles/'+room+f'/angle-{i+1}.png'
  s.render.filepath=path;bpy.ops.render.render(write_still=True)
  manifest.append(dict(room=room,angle=i+1,floor=floor,camera=list(cam.location),target=list(target),lens_mm=20,path=path))
json.dump(manifest,open('/workspace/apartment-design/multiple-angles/cameras.json','w'),indent=2)
