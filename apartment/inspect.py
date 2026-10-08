import bpy
from mathutils import Vector
bpy.ops.import_scene.gltf(filepath='/workspace/apartment/8_21_2026.glb')
for o in bpy.context.scene.objects:
 if o.type=='MESH':
  v=[o.matrix_world@Vector(x) for x in o.bound_box]
  print('BOUND',o.name,tuple(round(min(x[i] for x in v),2) for i in range(3)),tuple(round(max(x[i] for x in v),2) for i in range(3)))
bpy.ops.wm.save_as_mainfile(filepath='/workspace/apartment/scan.blend')
