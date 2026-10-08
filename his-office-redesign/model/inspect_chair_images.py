import bpy,json
bpy.ops.wm.open_mainfile(filepath='/workspace/his-office-redesign/model/keepers-and-taskchairs.blend')
for m in bpy.data.materials:
 if 'Branch selected Black' not in m.name: continue
 print('MATERIAL',m.name)
 for n in m.node_tree.nodes:
  if n.type=='TEX_IMAGE':
   im=n.image
   print('IMAGE',n.name,im.name if im else None,im.size[: ] if im else None,im.source if im else None,im.filepath if im else None,bool(im.packed_file) if im else None,im.has_data if im else None)
for im in bpy.data.images:
 print('ALLIMAGE',im.name,tuple(im.size),im.filepath,bool(im.packed_file),im.has_data)
