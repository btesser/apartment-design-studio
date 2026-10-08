import bpy,numpy as np,json
from mathutils import Vector
bpy.ops.wm.open_mainfile(filepath='/workspace/apartment/scan.blend')
out=[]
for material in bpy.data.materials:
 if not material.use_nodes:continue
 n=next((n for n in material.node_tree.nodes if n.type=='TEX_IMAGE'),None)
 if not n:continue
 im=n.image;w,h=im.size[:];pix=np.empty(w*h*4,dtype=np.float32);im.pixels.foreach_get(pix);pix=pix.reshape(h,w,4)
 for o in bpy.data.objects:
  if o.type!='MESH' or not o.name.startswith('Mesh_') or material not in list(o.data.materials): continue
  p=o.data.polygons;uv=o.data.uv_layers.active.data
  loc=[];ids=[]
  for face in p:
   coord=sum((uv[li].uv for li in face.loop_indices),Vector((0,0)))/3
   c=pix[min(h-1,max(0,int(coord.y*h))), min(w-1,max(0,int(coord.x*w)))][:3]
   if np.max(c)<.07:
    loc.append(list(o.matrix_world@face.center));ids.append(face.index)
  if len(loc):
   l=np.array(loc); print(o.name,len(loc), np.round(l.min(axis=0),2),np.round(l.max(axis=0),2));np.savez_compressed('/workspace/apartment-model/dark_'+o.name+'.npz',loc=l,faceids=ids)
