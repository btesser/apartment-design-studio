import bpy,json
from pathlib import Path
P=Path('/workspace/his-office-redesign/model')
bpy.ops.wm.open_mainfile(filepath=str(P/'his-office-shell.blend'))
before=[{'name':im.name,'size':list(im.size),'has_data':im.has_data} for im in bpy.data.images]
with bpy.data.libraries.load(str(P/'keepers-and-taskchairs.blend'),link=False) as (src,dst):
 dst.collections=['His Office — kept products and two Branch task chairs']
bpy.context.scene.collection.children.link(dst.collections[0])
images=[]
for m in bpy.data.materials:
 if 'Branch selected Black' not in m.name:continue
 for n in m.node_tree.nodes:
  if n.type!='TEX_IMAGE' or not n.image:continue
  im=n.image;rec={'material':m.name,'node':n.name,'name':im.name,'size':list(im.size),'has_data':im.has_data,'packed':bool(im.packed_file),'filepath':im.filepath}
  images.append(rec)
  assert min(im.size)>0 and im.has_data and im.packed_file,rec
bpy.ops.wm.save_as_mainfile(filepath=str(P/'keeper-append-proof.blend'))
(P/'keeper-append-proof.json').write_text(json.dumps({'shell_images_before_append':before,'branch_images_after_append':images,'passed':True},indent=2))
print('APPEND PROOF PASSED',len(images))
