import bpy,json
bpy.ops.wm.open_mainfile(filepath='/workspace/apartment/scan.blend')
for m in bpy.data.materials:
 print('MATERIAL',m.name,m.diffuse_color[:],m.use_nodes)
 if m.use_nodes:
  for n in m.node_tree.nodes:
   if n.type=='TEX_IMAGE':
    im=n.image; print('IMG',im.name,im.size[:],im.filepath)
