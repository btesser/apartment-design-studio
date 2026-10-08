import bpy,json
from mathutils import Vector
bpy.ops.wm.open_mainfile(filepath='/workspace/his-office-redesign/model/his-office-design.blend')
for name in ['his-office wall4 segment','secondary-workspace::black-brown tabletop','blue-geometric-art::assumed slim black frame']:
 o=bpy.data.objects[name];p=[o.matrix_world@Vector(c) for c in o.bound_box]
 print(name,[[min(c[i]for c in p)for i in range(3)],[max(c[i]for c in p)for i in range(3)]])
