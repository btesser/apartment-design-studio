import bpy,json,math
from mathutils import Vector
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath='/workspace/his-office-redesign/model/branch-pro-official-shore-reference.glb')
pts=[o.matrix_world@v.co for o in bpy.context.scene.objects if o.type=='MESH' for v in o.data.vertices]
lo=[min(v[i] for v in pts) for i in range(3)];hi=[max(v[i] for v in pts) for i in range(3)]
top=[v for v in pts if v.z>lo[2]+.70]
print('BRANCH INFO',json.dumps({'bounds':[lo,hi],'dimensions':[hi[i]-lo[i] for i in range(3)],'top_mean_xy':[sum(v[i] for v in top)/len(top) for i in range(2)],'meshes':[(o.name,len(o.data.vertices)) for o in bpy.context.scene.objects if o.type=='MESH'],'materials':[(m.name,[(n.name,n.type) for n in m.node_tree.nodes]) for m in bpy.data.materials]}))
